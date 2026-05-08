function getStressTickColor() {
    const theme = document.documentElement.getAttribute("data-theme") || "light";
    return theme === "dark" ? "#cbd5e1" : "#334155";
}

function bindStressControls() {
    const form = document.getElementById("stressForm");
    const slider = document.getElementById("crashPercent");
    const label = document.getElementById("crashPercentLabel");
    const scenarioButtons = document.querySelectorAll(".scenario-btn");

    if (slider && label) {
        const updateLabel = () => {
            label.textContent = `${slider.value}%`;
        };
        slider.addEventListener("input", updateLabel);
        updateLabel();
    }

    scenarioButtons.forEach((button) => {
        button.addEventListener("click", () => {
            if (!slider || !form) return;
            slider.value = button.dataset.value || "20";
            if (label) label.textContent = `${slider.value}%`;
            form.requestSubmit();
        });
    });
}

function renderStressCharts() {
    const payload = window.finsightStressTest;
    if (!payload || !payload.charts) return;

    const tickColor = getStressTickColor();
    const beforeAfter = payload.charts.before_after || { labels: [], values: [] };
    const sectorLoss = payload.charts.sector_loss || { labels: [], values: [] };
    const declinePath = payload.charts.decline_path || { labels: [], values: [] };

    const beforeAfterCtx = document.getElementById("stressBeforeAfterChart");
    if (beforeAfterCtx) {
        new Chart(beforeAfterCtx, {
            type: "bar",
            data: {
                labels: beforeAfter.labels,
                datasets: [
                    {
                        label: "Portfolio Value (USD)",
                        data: beforeAfter.values,
                        backgroundColor: ["#0ea5e9", "#ef4444"],
                        borderRadius: 8
                    }
                ]
            },
            options: {
                responsive: true,
                plugins: { legend: { display: false } },
                scales: {
                    x: { ticks: { color: tickColor } },
                    y: { ticks: { color: tickColor } }
                }
            }
        });
    }

    const sectorLossCtx = document.getElementById("stressSectorLossChart");
    if (sectorLossCtx) {
        new Chart(sectorLossCtx, {
            type: "doughnut",
            data: {
                labels: sectorLoss.labels,
                datasets: [
                    {
                        label: "Sector Loss (USD)",
                        data: sectorLoss.values,
                        backgroundColor: ["#ef4444", "#f97316", "#f59e0b", "#8b5cf6", "#3b82f6", "#06b6d4", "#22c55e"]
                    }
                ]
            },
            options: {
                responsive: true,
                cutout: "60%",
                plugins: {
                    legend: {
                        position: "bottom",
                        labels: { color: tickColor }
                    }
                }
            }
        });
    }

    const declinePathCtx = document.getElementById("stressDeclinePathChart");
    if (declinePathCtx) {
        new Chart(declinePathCtx, {
            type: "line",
            data: {
                labels: declinePath.labels,
                datasets: [
                    {
                        label: "Portfolio Value Under Stress",
                        data: declinePath.values,
                        borderColor: "#ef4444",
                        backgroundColor: "rgba(239,68,68,0.15)",
                        fill: true,
                        pointRadius: 3,
                        tension: 0.3
                    }
                ]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        labels: { color: tickColor }
                    }
                },
                scales: {
                    x: { ticks: { color: tickColor } },
                    y: { ticks: { color: tickColor } }
                }
            }
        });
    }
}

document.addEventListener("DOMContentLoaded", () => {
    bindStressControls();
    renderStressCharts();
});
