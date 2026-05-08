function buildTickColor() {
    const theme = document.documentElement.getAttribute("data-theme") || "light";
    return theme === "dark" ? "#cbd5e1" : "#334155";
}

function downsampleSeries(labels, values, maxPoints = 60) {
    if (!labels || !values || labels.length <= maxPoints) {
        return { labels, values };
    }

    const step = Math.ceil(labels.length / maxPoints);
    const sampleLabels = [];
    const sampleValues = [];
    for (let i = 0; i < labels.length; i += step) {
        sampleLabels.push(labels[i]);
        sampleValues.push(values[i]);
    }
    if (sampleLabels[sampleLabels.length - 1] !== labels[labels.length - 1]) {
        sampleLabels.push(labels[labels.length - 1]);
        sampleValues.push(values[values.length - 1]);
    }
    return { labels: sampleLabels, values: sampleValues };
}

function renderSimulationCharts() {
    const payload = window.finsightSimulation;
    if (!payload || !payload.summary || !payload.timeseries) return;

    const tickColor = buildTickColor();
    const ts = payload.timeseries;
    const downsampledGrowth = downsampleSeries(ts.labels, ts.growth_values, 72);

    const growthCanvas = document.getElementById("simGrowthChart");
    if (growthCanvas) {
        new Chart(growthCanvas, {
            type: "line",
            data: {
                labels: downsampledGrowth.labels,
                datasets: [
                    {
                        label: "Portfolio Value",
                        data: downsampledGrowth.values,
                        borderColor: "#3b82f6",
                        backgroundColor: "rgba(59,130,246,0.14)",
                        fill: true,
                        tension: 0.25,
                        pointRadius: 0
                    }
                ]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        labels: {
                            color: tickColor
                        }
                    }
                },
                scales: {
                    x: {
                        ticks: {
                            color: tickColor,
                            maxTicksLimit: 10
                        }
                    },
                    y: {
                        ticks: {
                            color: tickColor
                        }
                    }
                }
            }
        });
    }

    const comparisonCanvas = document.getElementById("simComparisonChart");
    if (comparisonCanvas) {
        new Chart(comparisonCanvas, {
            type: "bar",
            data: {
                labels: ["Total Invested", "Estimated Profit"],
                datasets: [
                    {
                        label: "Amount (USD)",
                        data: [payload.summary.total_invested, payload.summary.profit],
                        backgroundColor: ["#0ea5e9", payload.summary.profit >= 0 ? "#22c55e" : "#ef4444"],
                        borderRadius: 8
                    }
                ]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    x: {
                        ticks: { color: tickColor }
                    },
                    y: {
                        ticks: { color: tickColor }
                    }
                }
            }
        });
    }
}

document.addEventListener("DOMContentLoaded", () => {
    renderSimulationCharts();
});
