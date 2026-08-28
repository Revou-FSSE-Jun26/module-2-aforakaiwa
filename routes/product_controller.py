from flask import Blueprint, request, jsonify

from auth import roles_required
from schemas import ProductCreateSchema, ProductUpdateSchema
from services.product_service import ProductService

products_bp = Blueprint("products", __name__, url_prefix="/products")


@products_bp.route("", methods=["GET"])
def get_products():
    """
    Get all products with pagination
    ---
    tags:
      - Products
    parameters:
      - name: page
        in: query
        type: integer
        default: 1
      - name: per_page
        in: query
        type: integer
        default: 5
    responses:
      200:
        description: Paginated list of products
    """
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 5, type=int)

    pagination = ProductService.get_all(page=page, per_page=per_page)

    return jsonify({
        "products": [product.to_dict() for product in pagination.items],
        "page": pagination.page,
        "per_page": pagination.per_page,
        "total_pages": pagination.pages,
        "total_items": pagination.total,
    })


@products_bp.route("/<int:product_id>", methods=["GET"])
def get_product(product_id):
    """
    Get a product by ID
    ---
    tags:
      - Products
    parameters:
      - name: product_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Product found
      404:
        description: Product not found
    """
    product = ProductService.get_by_id(product_id)
    if product is None:
        return jsonify({"error": f"Product {product_id} not found"}), 404
    return jsonify(product.to_dict())


@products_bp.route("", methods=["POST"])
@roles_required("Admin")
def create_product():
    """
    Create a new product (requires Admin)
    ---
    tags:
      - Products
    security:
      - Bearer: []
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - category_id
            - product_name
            - sku
            - price
          properties:
            category_id:
              type: integer
            product_name:
              type: string
            sku:
              type: string
            description:
              type: string
            price:
              type: number
            stock_quantity:
              type: integer
    responses:
      201:
        description: Product created
      400:
        description: Validation error
      409:
        description: SKU already exists
    """
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    product_create_schema = ProductCreateSchema()
    errors = product_create_schema.validate(data)
    if errors:
        return jsonify({"errors": errors}), 400

    validated = product_create_schema.load(data)
    product, error = ProductService.create(validated)
    if error:
        return jsonify({"error": error}), 409
    return jsonify({"message": "Product added", "product": product.to_dict()}), 201


@products_bp.route("/<int:product_id>", methods=["PUT"])
@roles_required("Admin")
def update_product(product_id):
    """
    Update a product (requires Admin)
    ---
    tags:
      - Products
    security:
      - Bearer: []
    parameters:
      - name: product_id
        in: path
        type: integer
        required: true
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            product_name:
              type: string
            sku:
              type: string
            description:
              type: string
            price:
              type: number
            stock_quantity:
              type: integer
            is_active:
              type: boolean
            category_id:
              type: integer
    responses:
      200:
        description: Product updated
      400:
        description: Validation error
      404:
        description: Product not found
      409:
        description: SKU already exists
    """
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    product_update_schema = ProductUpdateSchema()
    errors = product_update_schema.validate(data)
    if errors:
        return jsonify({"errors": errors}), 400

    validated = product_update_schema.load(data)
    product, error = ProductService.update(product_id, validated)
    if error == "not_found":
        return jsonify({"error": f"Product {product_id} not found"}), 404
    if error:
        return jsonify({"error": error}), 409
    return jsonify({"message": "Product updated", "product": product.to_dict()}), 200


@products_bp.route("/<int:product_id>", methods=["DELETE"])
@roles_required("Admin")
def delete_product(product_id):
    """
    Delete a product (soft delete, requires Admin)
    ---
    tags:
      - Products
    security:
      - Bearer: []
    parameters:
      - name: product_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Product deleted
      404:
        description: Product not found
      409:
        description: Cannot delete product with active orders
    """
    success, error = ProductService.delete(product_id)
    if error == "not_found":
        return jsonify({"error": f"Product {product_id} not found"}), 404
    if error:
        return jsonify({"error": error}), 409
    return jsonify({"message": "Product deleted"}), 200
