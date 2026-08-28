import sys
import os
import pytest

# Ensure the project root is on the import path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app
from utils import db as _db


@pytest.fixture
def app():
    """Create a Flask application configured for testing with in-memory SQLite."""
    app = create_app()
    app.config.update(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "SQLALCHEMY_TRACK_MODIFICATIONS": False,
        }
    )

    with app.app_context():
        _db.create_all()
        yield app
        _db.session.remove()
        _db.drop_all()


@pytest.fixture
def client(app):
    """Provide a Flask test client."""
    return app.test_client()


@pytest.fixture
def db_session(app):
    """Provide a database session for direct model testing."""
    with app.app_context():
        yield _db.session
