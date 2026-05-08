from __future__ import annotations

from collections import defaultdict

from models.portfolio_model import Portfolio
from services.stock_service import get_stock_quote


def _compute_current_values(holdings: list[Portfolio]) -> tuple[dict[str, float], dict[str, float]]:
    """
    Computes current stock values and current sector values using live quotes.
    Returns:
      - stock_values: {SYMBOL: current_value}
      - sector_values: {SECTOR: aggregated_current_value}
    """
    stock_values: dict[str, float] = {}
    sector_values: dict[str, float] = defaultdict(float)

    for holding in holdings:
        quote = get_stock_quote(holding.stock_symbol)
        current_value = float(holding.quantity) * float(quote["current_price"])
        stock_values[holding.stock_symbol] = current_value
        sector_values[holding.sector] += current_value

    return stock_values, dict(sector_values)


def _clamp(value: float, min_value: float, max_value: float) -> float:
    return max(min_value, min(max_value, value))


def assign_diversification_category(score: int) -> str:
    if score >= 80:
        return "Excellent Diversification"
    if score >= 60:
        return "Good Diversification"
    if score >= 40:
        return "Moderate Diversification"
    return "Poor Diversification"


def _score_reduction(
    *,
    max_stock_weight: float,
    max_sector_weight: float,
    stock_count: int,
    sector_count: int,
) -> int:
    score = 100

    # Too few stocks / sectors are a clear diversification weakness.
    if sector_count < 3:
        score -= 20

    if stock_count < 3:
        score -= 20
    elif stock_count < 5:
        score -= 10

    # Concentration penalties.
    if max_stock_weight > 0.40:
        excess_ratio = (max_stock_weight - 0.40) / 0.60  # 0..1
        score -= int(round(_clamp(excess_ratio, 0.0, 1.0) * 40))

    if max_sector_weight > 0.60:
        excess_ratio = (max_sector_weight - 0.60) / 0.40  # 0..1
        score -= int(round(_clamp(excess_ratio, 0.0, 1.0) * 30))

    return int(round(_clamp(score, 0.0, 100.0)))


def calculate_diversification_score(
    *,
    stock_values: dict[str, float],
    sector_values: dict[str, float],
) -> dict:
    stock_count = len(stock_values)
    sector_count = len(sector_values)

    total_value = float(sum(stock_values.values()))
    if total_value <= 0:
        score = 0
        category = assign_diversification_category(score)
        return {
            "score": score,
            "category": category,
            "largest_stock_allocation_pct": 0.0,
            "largest_sector_concentration_pct": 0.0,
            "max_stock_symbol": None,
            "max_sector": None,
            "stock_count": stock_count,
            "sector_count": sector_count,
        }

    stock_weights = {sym: val / total_value for sym, val in stock_values.items() if total_value > 0}
    sector_total = float(sum(sector_values.values())) or total_value
    sector_weights = {sec: val / sector_total for sec, val in sector_values.items()}

    max_stock_symbol = max(stock_weights, key=stock_weights.get) if stock_weights else None
    max_sector = max(sector_weights, key=sector_weights.get) if sector_weights else None
    max_stock_weight = float(stock_weights.get(max_stock_symbol, 0.0)) if max_stock_symbol else 0.0
    max_sector_weight = float(sector_weights.get(max_sector, 0.0)) if max_sector else 0.0

    score = _score_reduction(
        max_stock_weight=max_stock_weight,
        max_sector_weight=max_sector_weight,
        stock_count=stock_count,
        sector_count=sector_count,
    )
    category = assign_diversification_category(score)

    return {
        "score": score,
        "category": category,
        "largest_stock_allocation_pct": round(max_stock_weight * 100, 2),
        "largest_sector_concentration_pct": round(max_sector_weight * 100, 2),
        "max_stock_symbol": max_stock_symbol,
        "max_sector": max_sector,
        "stock_count": stock_count,
        "sector_count": sector_count,
    }


def diversification_color(score: int) -> str:
    category = assign_diversification_category(score)
    if category.startswith("Excellent"):
        return "success"
    if category.startswith("Good"):
        return "primary"
    if category.startswith("Moderate"):
        return "warning"
    return "danger"


def generate_diversification_insights(
    *,
    score_info: dict,
) -> list[str]:
    insights: list[str] = []
    score = int(score_info["score"])
    category = str(score_info["category"])

    max_stock_pct = float(score_info["largest_stock_allocation_pct"])
    max_sector_pct = float(score_info["largest_sector_concentration_pct"])
    max_stock_symbol = score_info["max_stock_symbol"]
    max_sector = score_info["max_sector"]
    stock_count = int(score_info["stock_count"])
    sector_count = int(score_info["sector_count"])

    if max_sector_pct > 60 and max_sector:
        insights.append(
            f"Your portfolio is heavily concentrated in {max_sector} stocks ({max_sector_pct}%)."
        )

    if max_stock_pct > 40 and max_stock_symbol:
        insights.append(
            f"High concentration detected in one asset: {max_stock_symbol} at {max_stock_pct}% of your portfolio."
        )

    if sector_count < 3:
        insights.append(
            "Portfolio diversification is limited because you hold fewer than 3 sectors. "
            "Consider adding positions in additional industries."
        )

    if stock_count < 5:
        insights.append(
            "You hold a relatively small number of stocks. Increasing the number of positions can reduce concentration risk."
        )

    if not insights:
        if category == "Excellent Diversification":
            insights.append("Portfolio diversification is healthy across multiple sectors.")
        elif category == "Good Diversification":
            insights.append("Your portfolio is reasonably diversified, with manageable concentration levels.")
        elif category == "Moderate Diversification":
            insights.append("Diversification is moderate; some allocation concentration is present.")
        else:
            insights.append("Your portfolio shows weak diversification; consider spreading investments more broadly.")

    # Ensure at least 2 insights for a better UI experience.
    if len(insights) == 1:
        insights.append(
            "Tip: keep individual holdings and sectors from dominating your total portfolio value."
        )

    return insights[:4]


def build_diversification_snapshot(user_id: int) -> dict:
    holdings = Portfolio.query.filter_by(user_id=user_id).all()
    if not holdings:
        # Keep UI stable when the portfolio is empty.
        stock_values = {}
        sector_values = {}
    else:
        stock_values, sector_values = _compute_current_values(holdings)

    score_info = calculate_diversification_score(stock_values=stock_values, sector_values=sector_values)

    total_value = float(sum(stock_values.values())) or 0.0
    stock_allocation_pct = []
    stock_labels = []
    for sym, value in sorted(stock_values.items(), key=lambda kv: kv[1], reverse=True):
        stock_labels.append(sym)
        stock_allocation_pct.append(round((value / total_value) * 100, 2) if total_value > 0 else 0.0)

    sector_total = float(sum(sector_values.values())) or total_value or 1.0
    sector_allocation_pct = []
    sector_labels = []
    for sec, value in sorted(sector_values.items(), key=lambda kv: kv[1], reverse=True):
        sector_labels.append(sec)
        sector_allocation_pct.append(round((value / sector_total) * 100, 2) if sector_total > 0 else 0.0)

    return {
        "score": int(score_info["score"]),
        "category": str(score_info["category"]),
        "color": diversification_color(int(score_info["score"])),
        "stock_count": int(score_info["stock_count"]),
        "sector_count": int(score_info["sector_count"]),
        "largest_stock_allocation_pct": float(score_info["largest_stock_allocation_pct"]),
        "largest_sector_concentration_pct": float(score_info["largest_sector_concentration_pct"]),
        "max_stock_symbol": score_info["max_stock_symbol"],
        "max_sector": score_info["max_sector"],
        "insights": generate_diversification_insights(score_info=score_info),
        "charts": {
            "sector_labels": sector_labels,
            "sector_values": sector_allocation_pct,
            "stock_labels": stock_labels,
            "stock_values": stock_allocation_pct,
        },
    }

