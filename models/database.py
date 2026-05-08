from datetime import date

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def init_database() -> None:
    from models.portfolio_model import Goal, Portfolio
    from models.transaction_model import Transaction
    from models.user_model import User

    db.create_all()

    user = User.query.first()
    if user:
        return

    user = User(name="Rahul Investor", email="rahul@example.com")
    db.session.add(user)
    db.session.flush()

    sample_portfolios = [
        Portfolio(user_id=user.id, stock_symbol="AAPL", company_name="Apple Inc.", sector="Technology", quantity=18, average_buy_price=165),
        Portfolio(user_id=user.id, stock_symbol="MSFT", company_name="Microsoft Corp.", sector="Technology", quantity=10, average_buy_price=310),
        Portfolio(user_id=user.id, stock_symbol="JPM", company_name="JPMorgan Chase", sector="Financial Services", quantity=14, average_buy_price=145),
        Portfolio(user_id=user.id, stock_symbol="XOM", company_name="Exxon Mobil", sector="Energy", quantity=22, average_buy_price=101),
        Portfolio(user_id=user.id, stock_symbol="JNJ", company_name="Johnson & Johnson", sector="Healthcare", quantity=8, average_buy_price=155),
    ]
    db.session.add_all(sample_portfolios)

    sample_transactions = [
        Transaction(user_id=user.id, stock_symbol="AAPL", transaction_type="BUY", quantity=10, price=160, total=1600),
        Transaction(user_id=user.id, stock_symbol="AAPL", transaction_type="BUY", quantity=8, price=171, total=1368),
        Transaction(user_id=user.id, stock_symbol="MSFT", transaction_type="BUY", quantity=10, price=310, total=3100),
        Transaction(user_id=user.id, stock_symbol="JPM", transaction_type="BUY", quantity=14, price=145, total=2030),
        Transaction(user_id=user.id, stock_symbol="XOM", transaction_type="BUY", quantity=22, price=101, total=2222),
        Transaction(user_id=user.id, stock_symbol="JNJ", transaction_type="BUY", quantity=8, price=155, total=1240),
    ]
    db.session.add_all(sample_transactions)

    sample_goals = [
        Goal(
            user_id=user.id,
            goal_name="Emergency Investment Fund",
            target_amount=25000,
            current_amount=14500,
            deadline=date(2027, 12, 31),
        ),
        Goal(
            user_id=user.id,
            goal_name="Retirement Portfolio Milestone",
            target_amount=100000,
            current_amount=38500,
            deadline=date(2030, 12, 31),
        ),
    ]
    db.session.add_all(sample_goals)

    db.session.commit()
