from flask import Blueprint, render_template, request

from models.user_model import User
from services.analytics_service import build_portfolio_snapshot
from services.diversification_service import build_diversification_snapshot
from services.simulator_service import (
    SimulationInput,
    generate_simulation_insights,
    run_investment_simulation,
    validate_simulation_input,
)
from services.stress_test_service import run_stress_test, validate_crash_percent
from utils.helpers import safe_float, safe_int

analytics_bp = Blueprint("analytics", __name__)


@analytics_bp.route("/analytics")
def analytics():
    user = User.query.first()
    snapshot = build_portfolio_snapshot(user.id)
    return render_template("analytics.html", user=user, snapshot=snapshot)


@analytics_bp.route("/diversification")
def diversification():
    user = User.query.first()
    snapshot = build_diversification_snapshot(user.id)
    return render_template("diversification.html", user=user, snapshot=snapshot)


@analytics_bp.route("/simulator", methods=["GET", "POST"])
def simulator():
    user = User.query.first()

    form_data = {
        "initial_investment": 100000.0,
        "monthly_investment": 10000.0,
        "annual_return_rate": 12.0,
        "duration_years": 10,
    }
    errors: list[str] = []
    result = None
    insights: list[str] = []

    if request.method == "POST":
        form_data = {
            "initial_investment": safe_float(request.form.get("initial_investment"), 0.0),
            "monthly_investment": safe_float(request.form.get("monthly_investment"), 0.0),
            "annual_return_rate": safe_float(request.form.get("annual_return_rate"), 0.0),
            "duration_years": safe_int(request.form.get("duration_years"), 0),
        }

    payload = SimulationInput(
        initial_investment=form_data["initial_investment"],
        monthly_investment=form_data["monthly_investment"],
        annual_return_rate=form_data["annual_return_rate"],
        duration_years=form_data["duration_years"],
    )

    errors = validate_simulation_input(payload)
    if not errors:
        result = run_investment_simulation(payload)
        insights = generate_simulation_insights(payload, result)

    return render_template(
        "simulator.html",
        user=user,
        form_data=form_data,
        errors=errors,
        simulation_result=result,
        insights=insights,
    )


@analytics_bp.route("/stress-test", methods=["GET", "POST"])
def stress_test():
    user = User.query.first()
    crash_percent = 20.0
    errors: list[str] = []

    if request.method == "POST":
        crash_percent = safe_float(request.form.get("crash_percent"), 20.0)

    crash_percent, validation_errors = validate_crash_percent(crash_percent)
    errors.extend(validation_errors)

    snapshot = run_stress_test(user.id, crash_percent)

    scenarios = [
        {"label": "Mild Correction", "value": 10},
        {"label": "Bear Market", "value": 20},
        {"label": "Severe Crash", "value": 35},
        {"label": "Extreme Crash", "value": 50},
    ]

    return render_template(
        "stress_test.html",
        user=user,
        crash_percent=crash_percent,
        scenarios=scenarios,
        errors=errors,
        snapshot=snapshot,
    )
