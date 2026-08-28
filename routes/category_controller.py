from flask import Blueprint, request, jsonify

from auth import roles_required
from schemas import CategoryCreateSchema, CategoryUpdateSchema
from services.category_service import CategoryService

categories_bp = Blueprint("categories", __name__, url_prefix="/categories")


@categories_bp.route("", methods=["GET"])
def get_categories():
    """
    Get all categories
    ---
    tags:
      - Categories
    responses:
      200:
        description: List of all categories
    """
    categories = CategoryService.get_all()
    return jsonify([category.to_dict() for category in categories])


@categories_bp.route("/<int:category_id>", methods=["GET"])
def get_category(category_id):
    """
    Get a category by ID with its products
    ---
    tags:
      - Categories
    parameters:
      - name: category_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Category found
      404:
        description: Category not found
    """
    category = CategoryService.get_by_id(category_id)
    if category is None:
        return jsonify({"error": f"Category {category_id} not found"}), 404
    result = category.to_dict()
    result["products"] = [
        product.to_dict() for product in category.products
        if product.deleted_at is None
    ]
    return jsonify(result)


@categories_bp.route("", methods=["POST"])
@roles_required("Admin")
def create_category():
    """
    Create a new category (requires Admin)
    ---
    tags:
      - Categories
    security:
      - Bearer: []
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - category_name
            - description
          properties:
            category_name:
              type: string
            description:
              type: string
    responses:
      201:
        description: Category created
      400:
        description: Validation error
      409:
        description: Category name already exists
    """
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    category_create_schema = CategoryCreateSchema()
    errors = category_create_schema.validate(data)
    if errors:
        return jsonify({"errors": errors}), 400

    validated = category_create_schema.load(data)
    category, error = CategoryService.create(validated)
    if error:
        return jsonify({"error": error}), 409
    return jsonify(category.to_dict()), 201


@categories_bp.route("/<int:category_id>", methods=["PUT"])
@roles_required("Admin")
def update_category(category_id):
    """
    Update a category (requires Admin)
    ---
    tags:
      - Categories
    security:
      - Bearer: []
    parameters:
      - name: category_id
        in: path
        type: integer
        required: true
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            category_name:
              type: string
            description:
              type: string
    responses:
      200:
        description: Category updated
      404:
        description: Category not found
      409:
        description: Category name already exists
    """
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    category_update_schema = CategoryUpdateSchema()
    errors = category_update_schema.validate(data)
    if errors:
        return jsonify({"errors": errors}), 400

    validated = category_update_schema.load(data)
    category, error = CategoryService.update(category_id, validated)
    if error == "not_found":
        return jsonify({"error": f"Category {category_id} not found"}), 404
    if error:
        return jsonify({"error": error}), 409
    return jsonify({"message": "Category updated", "category": category.to_dict()})


@categories_bp.route("/<int:category_id>", methods=["DELETE"])
@roles_required("Admin")
def delete_category(category_id):
    """
    Delete a category (soft delete, requires Admin)
    ---
    tags:
      - Categories
    security:
      - Bearer: []
    parameters:
      - name: category_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Category deleted
      404:
        description: Category not found
    """
    success, error = CategoryService.delete(category_id)
    if error == "not_found":
        return jsonify({"error": f"Category {category_id} not found"}), 404
    return jsonify({"message": "Category deleted"}), 200
