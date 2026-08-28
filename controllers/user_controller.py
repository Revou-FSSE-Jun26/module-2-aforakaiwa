from flask import Blueprint, request, jsonify

from schemas import UserRegisterSchema
from services.user_service import UserService

users_bp = Blueprint("users", __name__, url_prefix="/users")


@users_bp.route("", methods=["GET"])
def get_users():
    """
    Get all users
    ---
    tags:
      - Users
    responses:
      200:
        description: List of all users
    """
    users = UserService.get_all()
    return jsonify([user.to_dict() for user in users])


@users_bp.route("/<int:user_id>", methods=["GET"])
def get_user(user_id):
    """
    Get a user by ID
    ---
    tags:
      - Users
    parameters:
      - name: user_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: User found
      404:
        description: User not found
    """
    user = UserService.get_by_id(user_id)
    if user is None:
        return jsonify({"error": f"User {user_id} not found"}), 404
    return jsonify(user.to_dict())


@users_bp.route("", methods=["POST"])
def create_user():
    """
    Register a new user
    ---
    tags:
      - Users
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - username
            - full_name
            - email
            - password
          properties:
            username:
              type: string
            full_name:
              type: string
            email:
              type: string
            password:
              type: string
            role:
              type: string
    responses:
      201:
        description: User registered successfully
      400:
        description: Validation error
      409:
        description: Username or email already exists
    """
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    user_register_schema = UserRegisterSchema()
    errors = user_register_schema.validate(data)
    if errors:
        return jsonify({"errors": errors}), 400

    validated = user_register_schema.load(data)
    user, error = UserService.create(validated)
    if error:
        return jsonify({"error": error}), 409
    return jsonify({"message": "User registered successfully", "user": user.to_dict()}), 201


@users_bp.route("/<int:user_id>", methods=["PUT"])
def update_user(user_id):
    """
    Update a user
    ---
    tags:
      - Users
    parameters:
      - name: user_id
        in: path
        type: integer
        required: true
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            username:
              type: string
            full_name:
              type: string
            role:
              type: string
            email:
              type: string
            is_active:
              type: boolean
    responses:
      200:
        description: User updated
      404:
        description: User not found
      409:
        description: Email already exists
    """
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    user, error = UserService.update(user_id, data)
    if error == "not_found":
        return jsonify({"error": f"User {user_id} not found"}), 404
    if error:
        return jsonify({"error": error}), 409
    return jsonify({"message": "User updated", "user": user.to_dict()})


@users_bp.route("/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    """
    Delete a user (soft delete)
    ---
    tags:
      - Users
    parameters:
      - name: user_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: User deleted
      404:
        description: User not found
    """
    success, error = UserService.delete(user_id)
    if error == "not_found":
        return jsonify({"error": f"User {user_id} not found"}), 404
    return jsonify({"message": "User deleted"}), 200
