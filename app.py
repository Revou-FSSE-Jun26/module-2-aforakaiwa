from flask import Flask
from flask_migrate import Migrate
from utils import db
from models import User, Category, Product, Order, order_items
from routes import home_bp, warmup_bp, users_bp, categories_bp, products_bp, orders_bp, order_items_bp


def create_app():
    app = Flask(__name__)

    # Database configuration — update the URI to match your PostgreSQL setup
    app.config["SQLALCHEMY_DATABASE_URI"] = (
        "postgresql://postgres:admin@localhost:5432/revoushop_db"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    Migrate(app, db)

    # Register blueprints
    app.register_blueprint(home_bp)
    app.register_blueprint(warmup_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(categories_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(order_items_bp)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
