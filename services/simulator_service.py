from __future__ import annotations

from dataclasses import dataclass

from utils.helpers import percentage


@dataclass
class SimulationInput:
    initial_investment: float
    monthly_investment: float
    annual_return_rate: float
    duration_years: int


def validate_simulation_input(payload: SimulationInput) -> list[str]:
    errors: list[str] = []

    if payload.initial_investment < 0:
        errors.append("Initial investment cannot be negative.")
    if payload.monthly_investment < 0:
        errors.append("Monthly investment cannot be negative.")
    if payload.annual_return_rate < 0 or payload.annual_return_rate > 50:
        errors.append("Expected annual return should be between 0% and 50%.")
    if payload.duration_years < 1 or payload.duration_years > 50:
        errors.append("Investment duration must be between 1 and 50 years.")

    return errors


def _monthly_growth_rate(annual_rate_pct: float) -> float:
    annual_rate_decimal = annual_rate_pct / 100
    return (1 + annual_rate_decimal) ** (1 / 12) - 1


def run_investment_simulation(payload: SimulationInput) -> dict:
    monthly_rate = _monthly_growth_rate(payload.annual_return_rate)
    total_months = payload.duration_years * 12

    current_value = payload.initial_investment
    total_invested = payload.initial_investment

    labels: list[str] = ["Start"]
    growth_values: list[float] = [round(current_value, 2)]
    invested_values: list[float] = [round(total_invested, 2)]
    profit_values: list[float] = [0.0]

    for month in range(1, total_months + 1):
        current_value = current_value * (1 + monthly_rate)
        current_value += payload.monthly_investment
        total_invested += payload.monthly_investment

        labels.append(f"Month {month}")
        growth_values.append(round(current_value, 2))
        invested_values.append(round(total_invested, 2))
        profit_values.append(round(current_value - total_invested, 2))

    profit = current_value - total_invested
    roi_pct = percentage(profit, total_invested) if total_invested > 0 else 0.0

    return {
        "summary": {
            "future_value": round(current_value, 2),
            "total_invested": round(total_invested, 2),
            "profit": round(profit, 2),
            "roi_pct": round(roi_pct, 2),
        },
        "timeseries": {
            "labels": labels,
            "growth_values": growth_values,
            "invested_values": invested_values,
            "profit_values": profit_values,
        },
    }


def generate_simulation_insights(payload: SimulationInput, simulation_result: dict) -> list[str]:
    insights: list[str] = []
    summary = simulation_result["summary"]

    future_value = float(summary["future_value"])
    invested = float(summary["total_invested"])
    profit = float(summary["profit"])
    roi_pct = float(summary["roi_pct"])

    if payload.annual_return_rate > 0:
        doubling_years = round(72 / payload.annual_return_rate, 1)
        insights.append(f"At {payload.annual_return_rate}% annual return, investments could double in roughly {doubling_years} years.")

    monthly_total = payload.monthly_investment * payload.duration_years * 12
    if payload.monthly_investment > 0 and monthly_total > payload.initial_investment:
        insights.append("Monthly investing significantly improves long-term portfolio growth through compounding.")

    if roi_pct >= 100:
        insights.append("Projected ROI is above 100%, indicating substantial long-term growth potential.")
    elif roi_pct >= 40:
        insights.append("Projected ROI is healthy and shows meaningful wealth creation over time.")
    else:
        insights.append("Projected growth is moderate; increasing monthly contributions may improve outcomes.")

    if payload.duration_years >= 10 and profit > invested * 0.5:
        insights.append("Longer duration is amplifying compounding gains. Staying invested boosts final value.")

    if future_value <= invested:
        insights.append("Current assumptions produce limited gains. Consider revising return rate or contribution plan.")

    return insights[:4]
