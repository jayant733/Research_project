function createBar(label, value) {
    const percent = Math.min(100, Math.max(0, value * 100));
    return `
        <div class="metric-bar-container">
            <div style="display:flex; justify-content:space-between">
                <span>${label}</span>
                <span>${percent.toFixed(0)}%</span>
            </div>
            <div class="bar-bg">
                <div class="bar-fill" style="width: ${percent}%"></div>
            </div>
        </div>
    `;
}

function updateTelemetryGrid(clients) {
    const grid = document.getElementById('telemetry-grid');
    grid.innerHTML = '';
    
    Object.entries(clients).forEach(([cid, data]) => {
        const t = data.telemetry || { cpu_usage: 0, memory_usage: 0, battery_level: 1 };
        
        const row = document.createElement('div');
        row.className = `client-row tier-${data.tier || 'none'}`;
        
        let tierLabel = 'Pending';
        if (data.tier === 'TIER_1_FHE') tierLabel = 'FHE';
        if (data.tier === 'TIER_2_SECAGG') tierLabel = 'SecAgg';
        if (data.tier === 'TIER_3_DP_PLAIN') tierLabel = 'DP';
        
        row.innerHTML = `
            <div class="client-header">
                <span>${cid} (${data.profile})</span>
                <span>${tierLabel}</span>
            </div>
            <div class="client-metrics">
                ${createBar('CPU', t.cpu_usage)}
                ${createBar('RAM', t.memory_usage)}
                ${createBar('BAT', t.battery_level)}
            </div>
        `;
        
        grid.appendChild(row);
    });
}
