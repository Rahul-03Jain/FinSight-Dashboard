from flask import Blueprint, redirect, render_template, request, url_for

from models.database import db
from models.portfolio_model import Portfolio
from models.transaction_model import Transaction
from services.analytics_service import build_portfolio_snapshot
from services.auth_service import get_current_user, login_required
from utils.helpers import safe_float

transaction_bp = Blueprint("transactions", __name__)


@transaction_bp.route("/transactions", methods=["GET", "POST"])
@login_required
def transactions():
    user = get_current_user()
    error_message = ""

    if request.method == "POST":
        symbol = request.form.get("stock_symbol", "").upper().strip()
        transaction_type = request.form.get("transaction_type", "").upper().strip()
        quantity = safe_float(request.form.get("quantity"))
        price = safe_float(request.form.get("price"))
        sector = request.form.get("sector", "Other").strip() or "Other"
        company_name = request.form.get("company_name", symbol).strip() or symbol

        if not symbol or quantity <= 0 or price <= 0 or transaction_type not in {"BUY", "SELL"}:
            error_message = "Please provide valid transaction details."
        else:
            holding = Portfolio.query.filter_by(user_id=user.id, stock_symbol=symbol).first()

            if transaction_type == "SELL":
                if not holding or holding.quantity < quantity:
                    error_message = "Cannot sell more shares than you currently hold."
                else:
                    holding.quantity -= quantity
                    if holding.quantity == 0:
                        db.session.delete(holding)
            else:
                if holding:
                    total_cost = (holding.average_buy_price * holding.quantity) + (price * quantity)
                    holding.quantity += quantity
                    holding.average_buy_price = total_cost / holding.quantity
                    holding.sector = sector
                    holding.company_name = company_name
                else:
                    holding = Portfolio(
                        user_id=user.id,
                        stock_symbol=symbol,
                        company_name=company_name,
                        sector=sector,
                        quantity=quantity,
                        average_buy_price=price,
                    )
                    db.session.add(holding)

            if not error_message:
                transaction = Transaction(
                    user_id=user.id,
                    stock_symbol=symbol,
                    transaction_type=transaction_type,
                    quantity=quantity,
                    price=price,
                    total=quantity * price,
                )
                db.session.add(transaction)
                db.session.commit()
                return redirect(url_for("transactions.transactions"))

    symbol_filter = request.args.get("symbol", "").upper().strip()
    tx_type_filter = request.args.get("tx_type", "").upper().strip()

    tx_query = Transaction.query.filter_by(user_id=user.id)
    if symbol_filter:
        tx_query = tx_query.filter(Transaction.stock_symbol == symbol_filter)
    if tx_type_filter in {"BUY", "SELL"}:
        tx_query = tx_query.filter(Transaction.transaction_type == tx_type_filter)

    transaction_history = tx_query.order_by(Transaction.timestamp.desc()).all()
    snapshot = build_portfolio_snapshot(user.id)

    return render_template(
        "transactions.html",
        user=user,
        snapshot=snapshot,
        transactions=transaction_history,
        error_message=error_message,
        symbol_filter=symbol_filter,
        tx_type_filter=tx_type_filter,
    )
