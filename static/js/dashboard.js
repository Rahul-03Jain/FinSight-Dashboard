function applySavedTheme() {
    const savedTheme = localStorage.getItem("finsight-theme") || "light";
    document.documentElement.setAttribute("data-theme", savedTheme);
}

function setupThemeToggle() {
    const toggle = document.getElementById("themeToggle");
    if (!toggle) return;
    toggle.addEventListener("click", () => {
        const current = document.documentElement.getAttribute("data-theme") || "light";
        const next = current === "light" ? "dark" : "light";
        document.documentElement.setAttribute("data-theme", next);
        localStorage.setItem("finsight-theme", next);
    });
}

function drawDashboardCharts() {
    const config = window.finsightCharts;
    if (!config) return;

    const growthCtx = document.getElementById("growthChart");
    if (growthCtx) {
        new Chart(growthCtx, {
            type: "line",
            data: {
                labels: config.growth.labels,
                datasets: [{
                    label: "Portfolio Value",
                    data: config.growth.values,
                    fill: true,
                    borderColor: "#3b82f6",
                    backgroundColor: "rgba(59,130,246,0.12)",
                    tension: 0.3
                }]
            }
        });
    }

    const sectorCtx = document.getElementById("sectorChart");
    if (sectorCtx) {
        new Chart(sectorCtx, {
            type: "doughnut",
            data: {
                labels: config.sector.labels,
                datasets: [{ data: config.sector.values }]
            }
        });
    }

    const stockAllocCtx = document.getElementById("stockAllocationChart");
    if (stockAllocCtx) {
        new Chart(stockAllocCtx, {
            type: "pie",
            data: {
                labels: config.stockAllocation.labels,
                datasets: [{ data: config.stockAllocation.values }]
            }
        });
    }

    const pnlCtx = document.getElementById("pnlContributionChart");
    if (pnlCtx) {
        new Chart(pnlCtx, {
            type: "bar",
            data: {
                labels: config.pnlContribution.labels,
                datasets: [{
                    label: "P/L Contribution",
                    data: config.pnlContribution.values,
                    backgroundColor: config.pnlContribution.values.map((v) => (v >= 0 ? "#22c55e" : "#ef4444"))
                }]
            },
            options: { plugins: { legend: { display: false } } }
        });
    }
}

function drawTrendCharts() {
    const trends = window.finsightTrends;
    if (!trends) return;

    trends.forEach((item) => {
        const canvas = document.getElementById(`trend-${item.symbol}`);
        if (!canvas) return;
        new Chart(canvas, {
            type: "line",
            data: {
                labels: item.history_labels,
                datasets: [{
                    data: item.history_prices,
                    borderColor: "#0ea5e9",
                    pointRadius: 0,
                    tension: 0.2
                }]
            },
            options: {
                scales: {
                    x: { display: false },
                    y: { display: true }
                },
                plugins: {
                    legend: { display: false }
                }
            }
        });
    });
}

document.addEventListener("DOMContentLoaded", () => {
    applySavedTheme();
    setupThemeToggle();
    drawDashboardCharts();
    drawTrendCharts();
});
