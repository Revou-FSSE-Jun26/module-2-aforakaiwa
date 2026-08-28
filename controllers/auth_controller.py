from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required

from schemas import LoginSchema
from services.auth_service import AuthService

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/login", methods=["POST"])
def login():
    """
    Login and get JWT token
    ---
    tags:
      - Auth
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - email
            - password
          properties:
            email:
              type: string
            password:
              type: string
    responses:
      200:
        description: Login successful
      400:
        description: Validation error
      401:
        description: Invalid credentials
      403:
        description: Account deactivated
    """
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    login_schema = LoginSchema()
    errors = login_schema.validate(data)
    if errors:
        return jsonify({"errors": errors}), 400

    validated = login_schema.load(data)
    result, error = AuthService.login(validated["email"], validated["password"])
    if error:
        message, status_code = error
        return jsonify({"error": message}), status_code

    return jsonify({
        "message": "Login successful",
        "access_token": result["access_token"],
        "refresh_token": result["refresh_token"],
        "user": result["user"].to_dict(),
    }), 200


@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    """
    Refresh access token using a refresh token
    ---
    tags:
      - Auth
    security:
      - Bearer: []
    responses:
      200:
        description: New access token generated
      401:
        description: Invalid or expired refresh token
    """
    current_user_id = get_jwt_identity()
    new_token, error = AuthService.refresh(current_user_id)
    if error:
        return jsonify({"error": error}), 401
    return jsonify({"access_token": new_token}), 200
