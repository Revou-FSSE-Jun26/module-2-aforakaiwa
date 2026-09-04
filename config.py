import os
from datetime import timedelta

from dotenv import load_dotenv

load_dotenv()


class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Flask's own secret, used for sessions/cookies.
    # No default fallback: the app must fail fast if this is not configured.
    SECRET_KEY = os.environ["SECRET_KEY"]
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'

    # flask-jwt-extended configuration.
    # No default fallback: forging JWTs must not be possible via a known default.
    JWT_SECRET_KEY = os.environ["JWT_SECRET_KEY"]
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)

    # Flasgger / Swagger UI configuration.
    SWAGGER = {
        'title': 'Simple Shops API',
        'uiversion': 3,
        'version': '1.0.0',
        'description': 'A simple shop API with products, users, and orders',
        'securityDefinitions': {
            'Bearer': {
                'type': 'apiKey',
                'name': 'Authorization',
                'in': 'header',
                'description': 'JWT Authorization header. Example: "Bearer {token}"'
            }
        },
    }
