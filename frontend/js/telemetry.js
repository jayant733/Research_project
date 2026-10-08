const PROFILE_LABELS = {
    workstation: "Workstation",
    mobile: "Mobile",
    iot_device: "IoT",
    Desktop: "Workstation",
    Mobile: "Mobile",
    IoT: "IoT"
};

const TIER_LABELS = {
    TIER_1_FHE: "CKKS",
    TIER_2_SECAGG: "SecAgg",
    TIER_3_DP_PLAIN: "Local DP",
    PLAIN: "Plain",
    EXCLUDED: "Excluded",
    DROPPED: "Dropped"
};

function updateTelemetryGrid(clients) {
    const grid = document.getElementById("telemetry-grid");
    const count = document.getElementById("fleet-count");
    const entries = Object.entries(clients || {});
    if (count) {
        count.textContent = `${entries.length} ${entries.length === 1 ? "client" : "clients"}`;
    }
    if (!entries.length) {
        grid.innerHTML = '<p class="empty">Start a run to inspect client assignments and telemetry.</p>';
        return;
    }
    grid.innerHTML = entries.map(([clientId, client]) => renderClient(clientId, client)).join("");
}

function renderClient(clientId, client) {
    const telemetry = client.telemetry || {};
    const profile = PROFILE_LABELS[client.profile] || client.profile || "Client";
    const tier = TIER_LABELS[client.tier] || "Pending";
    const moved = client.previous_tier && client.previous_tier !== client.tier;
    const tierText = moved
        ? `${TIER_LABELS[client.previous_tier] || client.previous_tier} → ${tier}`
        : tier;
    return `
        <div class="client-row tier-${client.tier || "none"}">
            <div class="client-header">
                <span>${clientId} · ${profile}</span>
                <span class="${moved ? "moved" : ""}">${tierText}</span>
            </div>
            <div class="bars">
                ${bar("CPU", telemetry.cpu_usage)}
                ${bar("RAM", telemetry.memory_usage)}
                ${bar("Battery", telemetry.battery_level)}
            </div>
            <div class="client-foot">
                <span>score ${Number(client.score || 0).toFixed(2)}</span>
                <span>trust ${Number(client.trust ?? 1).toFixed(2)}</span>
                <span>${epsilonText(client)}</span>
                <span>${formatBytes(client.payload_bytes)} · ${Number(client.fit_seconds || 0).toFixed(2)}s</span>
                ${client.attack ? `<span class="moved">${client.attack}</span>` : ""}
                ${client.reason ? `<span class="reason">${client.reason}</span>` : ""}
            </div>
        </div>
    `;
}

function bar(label, value) {
    const percent = Math.max(0, Math.min(100, Number(value || 0) * 100));
    return `
        <div>
            <div class="metric-label"><span>${label}</span><span>${percent.toFixed(0)}%</span></div>
            <div class="track"><div class="fill" style="width:${percent}%"></div></div>
        </div>
    `;
}

function epsilonText(client) {
    const spent = Number(client.epsilon || 0).toFixed(2);
    if (client.epsilon_remaining === null || client.epsilon_remaining === undefined) {
        return `ε ${spent}`;
    }
    return `ε ${spent} / left ${Number(client.epsilon_remaining).toFixed(2)}`;
}

function formatBytes(value) {
    const bytes = Number(value || 0);
    if (bytes >= 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${bytes} B`;
}
