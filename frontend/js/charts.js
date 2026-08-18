Chart.defaults.color = '#94a3b8';
Chart.defaults.font.family = 'Inter';

let convergenceChart, tierChart;

function initCharts() {
    const ctxConv = document.getElementById('convergenceChart').getContext('2d');
    convergenceChart = new Chart(ctxConv, {
        type: 'line',
        data: {
            labels: [],
            datasets: [
                {
                    label: 'Accuracy',
                    data: [],
                    borderColor: '#00ff88',
                    backgroundColor: 'rgba(0, 255, 136, 0.1)',
                    yAxisID: 'y',
                    tension: 0.3,
                    fill: true
                },
                {
                    label: 'Loss',
                    data: [],
                    borderColor: '#ef4444',
                    yAxisID: 'y1',
                    tension: 0.3
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: { type: 'linear', display: true, position: 'left', title: {display: true, text: 'Accuracy'} },
                y1: { type: 'linear', display: true, position: 'right', title: {display: true, text: 'Loss'}, grid: {drawOnChartArea: false} }
            }
        }
    });

    const ctxTier = document.getElementById('tierChart').getContext('2d');
    tierChart = new Chart(ctxTier, {
        type: 'doughnut',
        data: {
            labels: ['Tier 1 (FHE)', 'Tier 2 (SecAgg)', 'Tier 3 (DP)'],
            datasets: [{
                data: [0, 0, 0],
                backgroundColor: ['#6c63ff', '#00d4ff', '#ff6b6b'],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'bottom' }
            },
            cutout: '70%'
        }
    });
}

function updateConvergenceChart(round, accuracy, loss) {
    convergenceChart.data.labels.push(`R${round}`);
    convergenceChart.data.datasets[0].data.push(accuracy * 100);
    convergenceChart.data.datasets[1].data.push(loss);
    convergenceChart.update();
}

function updateTierChart(clients) {
    let t1 = 0, t2 = 0, t3 = 0;
    Object.values(clients).forEach(c => {
        if (c.tier === 'TIER_1_FHE') t1++;
        else if (c.tier === 'TIER_2_SECAGG') t2++;
        else if (c.tier === 'TIER_3_DP_PLAIN') t3++;
    });
    tierChart.data.datasets[0].data = [t1, t2, t3];
    tierChart.update();
}
