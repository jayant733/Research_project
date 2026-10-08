Chart.defaults.color = "#aeb6a7";
Chart.defaults.font.family = "IBM Plex Sans";
Chart.defaults.font.size = 11;
Chart.defaults.borderColor = "#30392d";

let convergenceChart;
let tierChart;

function initCharts() {
    const convergence = document.getElementById("convergenceChart").getContext("2d");
    convergenceChart = new Chart(convergence, {
        type: "line",
        data: {
            labels: [],
            datasets: [
                {
                    label: "Accuracy %",
                    data: [],
                    borderColor: "#8fbf73",
                    backgroundColor: "rgba(150, 198, 125, 0.10)",
                    borderWidth: 2,
                    pointRadius: 2,
                    pointHoverRadius: 4,
                    tension: 0.25,
                    fill: true
                },
                {
                    label: "Loss",
                    data: [],
                    borderColor: "#e79750",
                    borderWidth: 2,
                    pointRadius: 2,
                    pointHoverRadius: 4,
                    tension: 0.25,
                    yAxisID: "y1"
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: { mode: "index", intersect: false },
            plugins: {
                legend: {
                    align: "end",
                    labels: { usePointStyle: true, pointStyle: "circle", boxWidth: 8 }
                }
            },
            scales: {
                x: { grid: { display: false } },
                y: {
                    min: 0,
                    max: 100,
                    ticks: { callback: (value) => `${value}%` },
                    title: { display: true, text: "Accuracy" }
                },
                y1: {
                    position: "right",
                    min: 0,
                    suggestedMax: 1,
                    grid: { drawOnChartArea: false },
                    title: { display: true, text: "Loss" }
                }
            }
        }
    });

    const tiers = document.getElementById("tierChart").getContext("2d");
    tierChart = new Chart(tiers, {
        type: "doughnut",
        data: {
            labels: ["CKKS", "SecAgg", "Local DP", "Plain", "Excluded"],
            datasets: [{
                data: [0, 0, 0, 0, 0],
                backgroundColor: ["#e79750", "#51b8a8", "#d9b765", "#929bab", "#e07861"],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: "72%",
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: (context) => `${context.label}: ${context.raw} clients`
                    }
                }
            }
        }
    });
}

function resetCharts() {
    convergenceChart.data.labels = [];
    convergenceChart.data.datasets.forEach((dataset) => { dataset.data = []; });
    convergenceChart.update();
    tierChart.data.datasets[0].data = [0, 0, 0, 0, 0];
    tierChart.update();
}

function updateConvergenceChart(round, accuracy, loss) {
    const label = `R${round}`;
    const labels = convergenceChart.data.labels;
    if (labels[labels.length - 1] === label) return;
    labels.push(label);
    convergenceChart.data.datasets[0].data.push(Number(accuracy) * 100);
    convergenceChart.data.datasets[1].data.push(Number(loss));
    convergenceChart.update();
}

function updateTierChart(clients) {
    const counts = { TIER_1_FHE: 0, TIER_2_SECAGG: 0, TIER_3_DP_PLAIN: 0, PLAIN: 0, EXCLUDED: 0 };
    Object.values(clients || {}).forEach((client) => {
        if (Object.prototype.hasOwnProperty.call(counts, client.tier)) counts[client.tier] += 1;
    });
    tierChart.data.datasets[0].data = [
        counts.TIER_1_FHE, counts.TIER_2_SECAGG, counts.TIER_3_DP_PLAIN, counts.PLAIN, counts.EXCLUDED
    ];
    tierChart.update();
}
