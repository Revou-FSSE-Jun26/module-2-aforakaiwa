import os
from datetime import timedelta

from dotenv import load_dotenv

load_dotenv()


class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///default.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Flask's own secret, used for sessions/cookies.
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-me')
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'

    # flask-jwt-extended configuration.
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'super-secret-key-change-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)

    # Reserved for future API documentation (flasgger) - not wired up yet.
    SWAGGER = {
        'title': 'Simple Shops API',
        'uiversion': 3,
        'version': '1.0.0',
        'description': 'A simple shop API with products, users, and orders',
    }
