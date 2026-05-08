from utils.calculations import calculate_diversification_score


def calculate_risk_score(sector_values: dict[str, float], volatility: float) -> dict:
    total_value = sum(sector_values.values())
    if total_value <= 0:
        return {
            "risk_score": 1,
            "risk_category": "Low Risk",
            "risk_color": "success",
            "diversification_score": 0.0,
            "max_sector_weight": 0.0,
        }

    weights = [value / total_value for value in sector_values.values()]
    max_sector_weight = max(weights)
    diversification_score = calculate_diversification_score(weights)

    concentration_penalty = max(0.0, (max_sector_weight - 0.35) * 12)
    diversification_penalty = max(0.0, (60 - diversification_score) / 10)
    volatility_penalty = min(4.0, volatility / 12)

    raw_score = 2 + concentration_penalty + diversification_penalty + volatility_penalty
    risk_score = max(1, min(10, int(round(raw_score))))

    if risk_score <= 3:
        category = "Low Risk"
        color = "success"
    elif risk_score <= 6:
        category = "Medium Risk"
        color = "warning"
    else:
        category = "High Risk"
        color = "danger"

    return {
        "risk_score": risk_score,
        "risk_category": category,
        "risk_color": color,
        "diversification_score": round(diversification_score, 2),
        "max_sector_weight": round(max_sector_weight * 100, 2),
    }
