document.addEventListener('DOMContentLoaded', () => {
    initCharts();
    
    const logContainer = document.getElementById('event-log');
    
    window.dashboardLog = function(msg, type='info') {
        const d = new Date();
        const timeStr = d.toTimeString().split(' ')[0];
        const div = document.createElement('div');
        div.className = `log-entry ${type}`;
        div.innerHTML = `<span class="time">[${timeStr}]</span> ${msg}`;
        logContainer.prepend(div);
    };

    // Initial Registration of mock clients
    const profiles = ['Desktop', 'Desktop', 'Mobile', 'Mobile', 'Mobile', 'IoT', 'IoT', 'IoT', 'IoT', 'IoT'];
    profiles.forEach(p => api.registerClient(p));
    
    // Wire up buttons
    document.getElementById('btn-simulate').addEventListener('click', async () => {
        dashboardLog('Triggering federated round simulation...', 'system');
        await api.startRound();
    });
    
    document.getElementById('btn-register').addEventListener('click', async () => {
        const p = profiles[Math.floor(Math.random() * profiles.length)];
        const res = await api.registerClient(p);
        dashboardLog(`Registered new client ${res.client.profile}`, 'system');
    });

    // Handle incoming WS messages
    new WebSocketManager((data) => {
        if (data.type === 'ROUND_COMPLETED') {
            const m = data.metrics;
            const c = data.clients;
            
            // Update KPIs
            document.getElementById('current-round').innerText = m.round;
            document.getElementById('kpi-accuracy').innerText = (m.accuracy * 100).toFixed(2) + '%';
            document.getElementById('kpi-clients').innerText = Object.keys(c).length;
            document.getElementById('kpi-epsilon').innerText = m.privacy_budget.toFixed(2);
            document.getElementById('kpi-latency').innerText = m.latency.toFixed(2) + 's';
            
            // Update Charts
            updateConvergenceChart(m.round, m.accuracy, m.loss);
            updateTierChart(c);
            
            // Update Telemetry Grid
            updateTelemetryGrid(c);
            
            dashboardLog(`Round ${m.round} complete | Acc: ${(m.accuracy*100).toFixed(1)}% | Latency: ${m.latency.toFixed(2)}s`, 'success');
        }
    });
});
