from flask import Blueprint, render_template, request

from models.portfolio_model import Goal
from models.user_model import User
from services.analytics_service import build_portfolio_snapshot

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
@dashboard_bp.route("/dashboard")
def dashboard():
    user = User.query.first()
    snapshot = build_portfolio_snapshot(user.id)
    return render_template("dashboard.html", user=user, snapshot=snapshot)


@dashboard_bp.route("/portfolio")
def portfolio():
    user = User.query.first()
    snapshot = build_portfolio_snapshot(user.id)
    return render_template("portfolio.html", user=user, snapshot=snapshot)


@dashboard_bp.route("/goals", methods=["GET", "POST"])
def goals():
    user = User.query.first()
    if request.method == "POST":
        from datetime import datetime

        from models.database import db
        from utils.helpers import safe_float

        goal_name = request.form.get("goal_name", "").strip()
        target_amount = safe_float(request.form.get("target_amount"))
        current_amount = safe_float(request.form.get("current_amount"))
        deadline_raw = request.form.get("deadline", "").strip()

        if goal_name and target_amount > 0 and current_amount >= 0:
            deadline = datetime.strptime(deadline_raw, "%Y-%m-%d").date() if deadline_raw else None
            goal = Goal(
                user_id=user.id,
                goal_name=goal_name,
                target_amount=target_amount,
                current_amount=current_amount,
                deadline=deadline,
            )
            db.session.add(goal)
            db.session.commit()

    snapshot = build_portfolio_snapshot(user.id)
    user_goals = Goal.query.filter_by(user_id=user.id).order_by(Goal.created_at.desc()).all()
    return render_template("goals.html", user=user, snapshot=snapshot, goals=user_goals)
