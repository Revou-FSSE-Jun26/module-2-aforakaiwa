from datetime import datetime

from sqlalchemy.exc import IntegrityError
from utils import db
from models import User


class UserService:

    @staticmethod
    def get_all():
        return User.query.filter_by(deleted_at=None).all()

    @staticmethod
    def get_by_id(user_id):
        user = db.session.get(User, user_id)
        if user is None or user.deleted_at is not None:
            return None
        return user

    @staticmethod
    def create(data):
        """Create a new user. Returns (user, None) on success or (None, error_message) on failure."""
        try:
            user = User(
                username=data["username"],
                full_name=data["full_name"],
                email=data["email"],
                role=data.get("role", "Customer"),
            )
            user.set_password(data["password"])
            db.session.add(user)
            db.session.commit()
            return user, None
        except IntegrityError:
            db.session.rollback()
            return None, "Username or email already exists"

    @staticmethod
    def update(user_id, data):
        """Update a user. Returns (user, None) on success or (None, error_message) on failure."""
        user = UserService.get_by_id(user_id)
        if user is None:
            return None, "not_found"
        try:
            if "username" in data:
                user.username = data["username"]
            if "full_name" in data:
                user.full_name = data["full_name"]
            if "role" in data:
                user.role = data["role"]
            if "email" in data:
                user.email = data["email"]
            if "is_active" in data:
                user.is_active = data["is_active"]
            db.session.commit()
            return user, None
        except IntegrityError:
            db.session.rollback()
            return None, "Email already exists"

    @staticmethod
    def delete(user_id):
        """Soft delete a user. Returns (True, None) on success or (False, error_message) on failure."""
        user = UserService.get_by_id(user_id)
        if user is None:
            return False, "not_found"
        user.deleted_at = datetime.utcnow()
        db.session.commit()
        return True, None

    @staticmethod
    def get_by_email(email):
        return User.query.filter_by(email=email, deleted_at=None).first()
