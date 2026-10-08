document.addEventListener("DOMContentLoaded", () => {
    initCharts();
    const logContainer = document.getElementById("event-log");
    const startButton = document.getElementById("btn-start");

    window.dashboardLog = function (message, type = "info") {
        const entry = document.createElement("div");
        entry.className = `log-entry ${type}`;
        const time = new Date().toTimeString().slice(0, 8);
        const timestamp = document.createElement("span");
        timestamp.className = "time";
        timestamp.textContent = time;
        entry.append(timestamp, document.createTextNode(message));
        logContainer.prepend(entry);
        while (logContainer.children.length > 40) {
            logContainer.lastElementChild.remove();
        }
    };

    function renderRound(metrics, clients) {
        document.getElementById("current-round").textContent = metrics.round;
        document.getElementById("kpi-accuracy").textContent = `${(metrics.accuracy * 100).toFixed(1)}%`;
        document.getElementById("kpi-loss").textContent = Number(metrics.loss).toFixed(3);
        document.getElementById("kpi-clients").textContent = Object.keys(clients).length;
        document.getElementById("kpi-epsilon").textContent = Number(metrics.privacy_budget || 0).toFixed(2);
        document.getElementById("kpi-latency").textContent = `${Number(metrics.latency || 0).toFixed(2)}s`;
        document.getElementById("kpi-bytes").textContent = formatBytes(metrics.payload_bytes);
        updateConvergenceChart(metrics.round, metrics.accuracy, metrics.loss);
        updateTierChart(clients);
        updateTelemetryGrid(clients);
    }

    function applyState(snapshot) {
        if (!snapshot) return;
        document.getElementById("total-rounds").textContent = snapshot.total_rounds;
        document.getElementById("current-round").textContent = snapshot.current_round;
        document.getElementById("mode-pill").textContent = String(snapshot.mode || "ratc").toUpperCase();
        document.getElementById("status-message").textContent = snapshot.message || "";
        document.getElementById("kpi-clients").textContent = snapshot.active_clients;
        startButton.disabled = Boolean(snapshot.running);
        startButton.querySelector(".button-label").textContent = snapshot.running
            ? "Run in progress"
            : "Start live run";
        startButton.setAttribute("aria-busy", String(Boolean(snapshot.running)));
    }

    async function hydrate() {
        const snapshot = await api.status();
        applyState(snapshot);
        resetCharts();
        (snapshot.history || []).forEach((metrics) => renderRound(metrics, metrics.clients || {}));
        if (!(snapshot.history || []).length) updateTelemetryGrid({});
    }

    startButton.addEventListener("click", async () => {
        const rounds = Number(document.getElementById("input-rounds").value);
        const seed = Number(document.getElementById("input-seed").value);
        const mode = document.getElementById("input-mode").value;
        const objective = document.getElementById("input-objective").value;
        const scenario = document.getElementById("input-scenario").value;
        const budgetRaw = document.getElementById("input-budget").value.trim();
        const budget = budgetRaw === "" ? null : Number(budgetRaw);
        if (!Number.isInteger(rounds) || rounds < 1 || rounds > 20) {
            dashboardLog("Rounds must be a whole number from 1 to 20.", "fail");
            document.getElementById("input-rounds").focus();
            return;
        }
        if (!Number.isInteger(seed) || seed < 0 || seed > 10000) {
            dashboardLog("Seed must be a whole number from 0 to 10,000.", "fail");
            document.getElementById("input-seed").focus();
            return;
        }
        if (budget !== null && (!Number.isFinite(budget) || budget < 0 || budget > 100)) {
            dashboardLog("Epsilon cap must be empty or a number from 0 to 100.", "fail");
            document.getElementById("input-budget").focus();
            return;
        }
        startButton.disabled = true;
        startButton.querySelector(".button-label").textContent = "Starting…";
        startButton.setAttribute("aria-busy", "true");
        try {
            await api.startRun(rounds, seed, mode, {
                objective,
                scenario,
                budget_epsilon: budget,
                forbid_iot_fhe: document.getElementById("input-forbid").checked,
                secagg_recovery: document.getElementById("input-recovery").checked || scenario === "dropout"
            });
            dashboardLog(`Started ${mode} · ${objective} · ${scenario} for ${rounds} rounds.`, "warn");
        } catch (error) {
            dashboardLog(error.message, "fail");
            startButton.disabled = false;
            startButton.querySelector(".button-label").textContent = "Start live run";
            startButton.setAttribute("aria-busy", "false");
        }
    });

    new WebSocketManager((event) => {
        applyState(event.state);
        if (event.type === "RUN_STARTED") {
            resetCharts();
            updateTelemetryGrid({});
            dashboardLog("Flower server started and clients are joining.", "success");
        }
        if (event.type === "ROUND_STARTED") {
            dashboardLog(`Round ${event.round} assignments published.`, "info");
        }
        if (event.type === "ROUND_COMPLETED") {
            renderRound(event.metrics, event.clients || {});
            const accuracy = (event.metrics.accuracy * 100).toFixed(1);
            dashboardLog(`Round ${event.metrics.round} complete · accuracy ${accuracy}% · ${formatBytes(event.metrics.payload_bytes)}.`, "success");
            Object.entries(event.clients || {}).forEach(([name, client]) => {
                if (!client.attack) return;
                dashboardLog(`${name} flagged as ${client.attack}. Trust is now ${Number(client.trust).toFixed(2)}.`, "warn");
            });
            if (event.metrics.dropout === "recovered") {
                dashboardLog(`Recovered a SecAgg dropout: ${(event.metrics.dropped_clients || []).join(", ")}.`, "warn");
            }
        }
        if (event.type === "RUN_FINISHED") dashboardLog("Live run finished. JSON and CSV exports are ready.", "success");
        if (event.type === "RUN_FAILED") dashboardLog(event.error || "Live run failed.", "fail");
    });

    hydrate().catch((error) => dashboardLog(error.message, "fail"));
    api.comparison().then(renderComparison).catch(() => {});
});

function renderComparison(payload) {
    const strip = document.getElementById("comparison-strip");
    const values = document.getElementById("comparison-values");
    if (!strip || !values || !payload || !payload.available) return;
    const entries = Object.entries(payload.summary || {});
    if (!entries.length) return;
    values.replaceChildren();
    entries.forEach(([mode, accuracy]) => {
        const item = document.createElement("span");
        item.textContent = `${mode} ${(Number(accuracy) * 100).toFixed(1)}%`;
        values.append(item);
    });
    strip.hidden = false;
}
