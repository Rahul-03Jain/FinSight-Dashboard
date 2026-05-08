from flask import Blueprint, render_template

from models.user_model import User
from services.analytics_service import build_portfolio_snapshot

analytics_bp = Blueprint("analytics", __name__)


@analytics_bp.route("/analytics")
def analytics():
    user = User.query.first()
    snapshot = build_portfolio_snapshot(user.id)
    return render_template("analytics.html", user=user, snapshot=snapshot)
