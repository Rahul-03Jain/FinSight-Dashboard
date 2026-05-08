function drawDiversificationCharts() {
    const payload = window.finsightDiversification;
    if (!payload || !payload.charts) return;

    const theme = document.documentElement.getAttribute("data-theme") || "light";
    const textColor = theme === "dark" ? "#cbd5e1" : "#334155";
    const legendColor = textColor;

    const palette = [
        "#3b82f6", "#22c55e", "#f59e0b", "#ef4444", "#8b5cf6",
        "#06b6d4", "#10b981", "#f97316", "#64748b", "#ec4899"
    ];

    const sectorLabels = payload.charts.sector_labels || [];
    const sectorValues = payload.charts.sector_values || [];
    const stockLabels = payload.charts.stock_labels || [];
    const stockValues = payload.charts.stock_values || [];

    const makeColors = (count) => {
        const colors = [];
        for (let i = 0; i < count; i++) colors.push(palette[i % palette.length]);
        return colors;
    };

    const commonTooltip = {
        callbacks: {
            label: function (context) {
                const label = context.label || "";
                const value = context.parsed || 0;
                return `${label}: ${value}%`;
            }
        }
    };

    const sectorCanvas = document.getElementById("diversificationSectorPie");
    if (sectorCanvas && sectorLabels.length > 0) {
        new Chart(sectorCanvas, {
            type: "pie",
            data: {
                labels: sectorLabels,
                datasets: [{
                    data: sectorValues,
                    backgroundColor: makeColors(sectorValues.length),
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: "bottom",
                        labels: { color: legendColor }
                    },
                    tooltip: commonTooltip
                }
            }
        });
    }

    const stockCanvas = document.getElementById("diversificationStockDoughnut");
    if (stockCanvas && stockLabels.length > 0) {
        new Chart(stockCanvas, {
            type: "doughnut",
            data: {
                labels: stockLabels,
                datasets: [{
                    data: stockValues,
                    backgroundColor: makeColors(stockValues.length),
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                cutout: "62%",
                plugins: {
                    legend: {
                        position: "bottom",
                        labels: { color: legendColor }
                    },
                    tooltip: commonTooltip
                }
            }
        });
    }
}

document.addEventListener("DOMContentLoaded", () => {
    drawDiversificationCharts();
});

