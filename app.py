from flask import Flask

from models.database import init_database, db
from routes.analytics_routes import analytics_bp
from routes.auth_routes import auth_bp
from routes.dashboard_routes import dashboard_bp
from routes.transaction_routes import transaction_bp


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = "finsight-dev-secret-key"

    db.init_app(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(transaction_bp)

    with app.app_context():
        init_database()

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
