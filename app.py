from flask import Flask
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flasgger import Swagger

from config import Config
from utils import db
from models import User, Category, Product, Order, order_items
from controllers import (
    home_bp,
    warmup_bp,
    users_bp,
    auth_bp,
    categories_bp,
    products_bp,
    orders_bp,
    order_items_bp,
)


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    Migrate(app, db)
    JWTManager(app)
    Swagger(app)

    # Register blueprints
    app.register_blueprint(home_bp)
    app.register_blueprint(warmup_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(categories_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(order_items_bp)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=app.config["DEBUG"])
