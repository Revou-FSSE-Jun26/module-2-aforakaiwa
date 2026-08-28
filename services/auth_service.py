from flask_jwt_extended import create_access_token, create_refresh_token

from services.user_service import UserService


class AuthService:

    @staticmethod
    def login(email, password):
        """Authenticate user. Returns (tokens_dict, None) on success or (None, error_tuple) on failure."""
        user = UserService.get_by_email(email)
        if not user or not user.check_password(password):
            return None, ("Invalid email or password", 401)

        if not user.is_active:
            return None, ("This account has been deactivated", 403)

        access_token = create_access_token(
            identity=str(user.user_id),
            additional_claims={"role": user.role}
        )
        refresh_token = create_refresh_token(
            identity=str(user.user_id),
            additional_claims={"role": user.role}
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": user,
        }, None

    @staticmethod
    def refresh(current_user_id):
        """Generate a new access token from refresh token. Returns (token, None) or (None, error_msg)."""
        from models import User
        from utils import db

        user = db.session.get(User, int(current_user_id))
        if user is None:
            return None, "User not found"

        new_access_token = create_access_token(
            identity=current_user_id,
            additional_claims={"role": user.role},
            fresh=False
        )
        return new_access_token, None
