import numpy as np


def calculate_roi(current_value: float, invested_amount: float) -> float:
    if invested_amount <= 0:
        return 0.0
    return ((current_value - invested_amount) / invested_amount) * 100


def calculate_daily_gain_loss(current_value: float, previous_value: float) -> float:
    return current_value - previous_value


def calculate_portfolio_return_percentage(total_profit_loss: float, total_invested: float) -> float:
    if total_invested <= 0:
        return 0.0
    return (total_profit_loss / total_invested) * 100


def calculate_volatility(closing_prices: list[float]) -> float:
    if len(closing_prices) < 2:
        return 0.0
    returns = np.diff(closing_prices) / np.array(closing_prices[:-1])
    if len(returns) == 0:
        return 0.0
    return float(np.std(returns) * np.sqrt(252) * 100)


def calculate_diversification_score(sector_weights: list[float]) -> float:
    if not sector_weights:
        return 0.0
    hhi = sum(weight * weight for weight in sector_weights)
    normalized = max(0.0, min(1.0, 1 - hhi))
    return normalized * 100
