from __future__ import annotations

from collections import defaultdict

from models.portfolio_model import Portfolio
from services.stock_service import get_stock_quote


SECTOR_SENSITIVITY = {
    "Technology": 1.30,
    "Communication Services": 1.18,
    "Consumer Cyclical": 1.15,
    "Financial Services": 1.10,
    "Industrials": 1.02,
    "Energy": 0.98,
    "Healthcare": 0.82,
    "Consumer Defensive": 0.78,
    "Utilities": 0.72,
    "Real Estate": 1.05,
}


def _clamp(value: float, min_value: float, max_value: float) -> float:
    return max(min_value, min(max_value, value))


def _severity(loss_pct: float) -> str:
    if loss_pct < 10:
        return "Low Impact"
    if loss_pct < 20:
        return "Moderate Impact"
    if loss_pct < 35:
        return "High Impact"
    return "Critical Impact"


def _severity_color(severity: str) -> str:
    return {
        "Low Impact": "success",
        "Moderate Impact": "warning",
        "High Impact": "orange",
        "Critical Impact": "danger",
    }.get(severity, "secondary")


def validate_crash_percent(value: float) -> tuple[float, list[str]]:
    errors: list[str] = []
    if value <= 0:
        errors.append("Crash percentage must be greater than 0.")
    value = _clamp(value, 1.0, 80.0)
    return value, errors


def run_stress_test(user_id: int, crash_percent: float) -> dict:
    holdings = Portfolio.query.filter_by(user_id=user_id).all()

    sector_before = defaultdict(float)
    sector_loss = defaultdict(float)
    stock_impact: list[dict] = []

    current_value = 0.0
    stressed_value = 0.0

    for holding in holdings:
        quote = get_stock_quote(holding.stock_symbol)
        holding_value = float(holding.quantity) * float(quote["current_price"])
        current_value += holding_value

        sensitivity = SECTOR_SENSITIVITY.get(holding.sector, 1.0)
        effective_decline_pct = _clamp(crash_percent * sensitivity, 0.0, 85.0)
        holding_loss = holding_value * (effective_decline_pct / 100.0)
        holding_after = holding_value - holding_loss
        stressed_value += holding_after

        sector_before[holding.sector] += holding_value
        sector_loss[holding.sector] += holding_loss

        stock_impact.append(
            {
                "symbol": holding.stock_symbol,
                "company_name": holding.company_name,
                "sector": holding.sector,
                "before_value": round(holding_value, 2),
                "after_value": round(holding_after, 2),
                "loss_amount": round(holding_loss, 2),
                "loss_pct": round(effective_decline_pct, 2),
            }
        )

    estimated_loss = current_value - stressed_value
    decline_pct = (estimated_loss / current_value * 100) if current_value > 0 else 0.0
    severity = _severity(decline_pct)

    top_vulnerable = sorted(stock_impact, key=lambda item: item["loss_amount"], reverse=True)[:3]
    sector_impact_rows = []
    for sector, before_value in sorted(sector_before.items(), key=lambda item: item[1], reverse=True):
        loss_amount = sector_loss[sector]
        loss_pct = (loss_amount / before_value * 100) if before_value > 0 else 0.0
        sector_impact_rows.append(
            {
                "sector": sector,
                "before_value": round(before_value, 2),
                "loss_amount": round(loss_amount, 2),
                "loss_pct": round(loss_pct, 2),
            }
        )

    simulated_path = _build_decline_path(current_value, crash_percent)
    insights = _build_insights(severity, sector_impact_rows, top_vulnerable, crash_percent)

    return {
        "inputs": {"crash_percent": round(crash_percent, 2)},
        "summary": {
            "current_value": round(current_value, 2),
            "estimated_loss": round(estimated_loss, 2),
            "remaining_value": round(stressed_value, 2),
            "decline_pct": round(decline_pct, 2),
            "risk_severity": severity,
            "risk_color": _severity_color(severity),
        },
        "sector_impact": sector_impact_rows,
        "top_vulnerable_assets": top_vulnerable,
        "insights": insights,
        "charts": {
            "before_after": {
                "labels": ["Current Value", "Stressed Value"],
                "values": [round(current_value, 2), round(stressed_value, 2)],
            },
            "sector_loss": {
                "labels": [item["sector"] for item in sector_impact_rows],
                "values": [item["loss_amount"] for item in sector_impact_rows],
            },
            "decline_path": simulated_path,
        },
    }


def _build_decline_path(current_value: float, crash_percent: float) -> dict:
    steps = [0, 25, 50, 75, 100]
    labels = []
    values = []
    for step in steps:
        step_crash = crash_percent * (step / 100)
        remaining = current_value * (1 - step_crash / 100)
        labels.append(f"{int(step)}% stress")
        values.append(round(max(0.0, remaining), 2))
    return {"labels": labels, "values": values}


def _build_insights(
    severity: str,
    sector_impact_rows: list[dict],
    top_vulnerable: list[dict],
    crash_percent: float,
) -> list[str]:
    insights: list[str] = []

    if sector_impact_rows:
        top_sector = sector_impact_rows[0]
        insights.append(
            f"{top_sector['sector']} shows the highest stress impact with an estimated loss of ${top_sector['loss_amount']:.2f}."
        )

    if top_vulnerable:
        top_asset = top_vulnerable[0]
        insights.append(
            f"Your most vulnerable asset in this scenario is {top_asset['symbol']} with a projected ${top_asset['loss_amount']:.2f} decline."
        )

    if severity in {"High Impact", "Critical Impact"}:
        insights.append("Stress losses are elevated; consider reducing concentration in high-beta sectors.")
    else:
        insights.append("Portfolio maintains moderate stability under this stress scenario.")

    if crash_percent >= 35:
        insights.append("Diversification quality becomes more important during severe market drawdowns.")

    return insights[:4]
