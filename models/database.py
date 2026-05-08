from datetime import date

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

db = SQLAlchemy()


def init_database() -> None:
    from models.portfolio_model import Goal, Portfolio
    from models.transaction_model import Transaction
    from models.user_model import User

    db.create_all()
    _ensure_users_schema_columns()
    _seed_demo_users(User)
    _seed_demo_portfolios(User, Portfolio, Transaction, Goal)
    db.session.commit()


def _ensure_users_schema_columns() -> None:
    existing_columns = db.session.execute(text("PRAGMA table_info(users)")).fetchall()
    column_names = {row[1] for row in existing_columns}

    if "password" not in column_names:
        db.session.execute(text("ALTER TABLE users ADD COLUMN password VARCHAR(120) DEFAULT 'demo123'"))
    if "investor_type" not in column_names:
        db.session.execute(text("ALTER TABLE users ADD COLUMN investor_type VARCHAR(60) DEFAULT 'Balanced Investor'"))
    db.session.commit()


def _seed_demo_users(User) -> None:
    demo_users = [
        {"name": "Conservative Investor", "email": "conservative@finsight.com", "password": "demo123", "investor_type": "Conservative Investor"},
        {"name": "Balanced Investor", "email": "balanced@finsight.com", "password": "demo123", "investor_type": "Balanced Investor"},
        {"name": "Aggressive Investor", "email": "aggressive@finsight.com", "password": "demo123", "investor_type": "Aggressive Investor"},
    ]

    existing_users = {user.email: user for user in User.query.all()}

    for demo in demo_users:
        user = existing_users.get(demo["email"])
        if not user:
            user = User(**demo)
            db.session.add(user)
        else:
            user.name = demo["name"]
            user.password = demo["password"]
            user.investor_type = demo["investor_type"]

    db.session.flush()


def _seed_demo_portfolios(User, Portfolio, Transaction, Goal) -> None:
    demo_seed_data = {
        "conservative@finsight.com": {
            "portfolio": [
                {"stock_symbol": "JNJ", "company_name": "Johnson & Johnson", "sector": "Healthcare", "quantity": 24, "average_buy_price": 150},
                {"stock_symbol": "PG", "company_name": "Procter & Gamble", "sector": "Consumer Defensive", "quantity": 30, "average_buy_price": 142},
                {"stock_symbol": "KO", "company_name": "Coca-Cola Co.", "sector": "Consumer Defensive", "quantity": 35, "average_buy_price": 58},
                {"stock_symbol": "DUK", "company_name": "Duke Energy", "sector": "Utilities", "quantity": 26, "average_buy_price": 92},
                {"stock_symbol": "PFE", "company_name": "Pfizer Inc.", "sector": "Healthcare", "quantity": 40, "average_buy_price": 35},
            ],
            "goals": [
                {"goal_name": "Capital Preservation Goal", "target_amount": 60000, "current_amount": 32500, "deadline": date(2029, 6, 30)},
            ],
        },
        "balanced@finsight.com": {
            "portfolio": [
                {"stock_symbol": "AAPL", "company_name": "Apple Inc.", "sector": "Technology", "quantity": 14, "average_buy_price": 165},
                {"stock_symbol": "MSFT", "company_name": "Microsoft Corp.", "sector": "Technology", "quantity": 9, "average_buy_price": 305},
                {"stock_symbol": "JPM", "company_name": "JPMorgan Chase", "sector": "Financial Services", "quantity": 16, "average_buy_price": 146},
                {"stock_symbol": "XOM", "company_name": "Exxon Mobil", "sector": "Energy", "quantity": 20, "average_buy_price": 102},
                {"stock_symbol": "UNH", "company_name": "UnitedHealth Group", "sector": "Healthcare", "quantity": 6, "average_buy_price": 470},
            ],
            "goals": [
                {"goal_name": "Balanced Wealth Growth", "target_amount": 80000, "current_amount": 37800, "deadline": date(2028, 12, 31)},
            ],
        },
        "aggressive@finsight.com": {
            "portfolio": [
                {"stock_symbol": "NVDA", "company_name": "NVIDIA Corp.", "sector": "Technology", "quantity": 16, "average_buy_price": 760},
                {"stock_symbol": "TSLA", "company_name": "Tesla Inc.", "sector": "Consumer Cyclical", "quantity": 18, "average_buy_price": 230},
                {"stock_symbol": "AMD", "company_name": "Advanced Micro Devices", "sector": "Technology", "quantity": 26, "average_buy_price": 150},
                {"stock_symbol": "META", "company_name": "Meta Platforms", "sector": "Communication Services", "quantity": 10, "average_buy_price": 410},
                {"stock_symbol": "AMZN", "company_name": "Amazon.com Inc.", "sector": "Consumer Cyclical", "quantity": 12, "average_buy_price": 145},
            ],
            "goals": [
                {"goal_name": "High Growth Milestone", "target_amount": 150000, "current_amount": 49800, "deadline": date(2030, 12, 31)},
            ],
        },
    }

    for email, config in demo_seed_data.items():
        user = User.query.filter_by(email=email).first()
        if not user:
            continue

        has_portfolio = Portfolio.query.filter_by(user_id=user.id).count() > 0
        has_transactions = Transaction.query.filter_by(user_id=user.id).count() > 0
        has_goals = Goal.query.filter_by(user_id=user.id).count() > 0

        if not has_portfolio:
            portfolio_records = [Portfolio(user_id=user.id, **item) for item in config["portfolio"]]
            db.session.add_all(portfolio_records)

        if not has_transactions:
            transaction_records = [
                Transaction(
                    user_id=user.id,
                    stock_symbol=item["stock_symbol"],
                    transaction_type="BUY",
                    quantity=item["quantity"],
                    price=item["average_buy_price"],
                    total=item["quantity"] * item["average_buy_price"],
                )
                for item in config["portfolio"]
            ]
            db.session.add_all(transaction_records)

        if not has_goals:
            goal_records = [Goal(user_id=user.id, **goal) for goal in config["goals"]]
            db.session.add_all(goal_records)
