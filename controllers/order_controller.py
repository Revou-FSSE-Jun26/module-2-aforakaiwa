from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required

from schemas import OrderCreateSchema
from services.order_service import OrderService

orders_bp = Blueprint("orders", __name__, url_prefix="/orders")
order_items_bp = Blueprint("order_items", __name__, url_prefix="/orders/<int:order_id>/items")


@orders_bp.route("", methods=["GET"])
@jwt_required()
def get_orders():
    """
    Get all orders for the authenticated user
    ---
    tags:
      - Orders
    security:
      - Bearer: []
    responses:
      200:
        description: List of user orders
    """
    user_id = int(get_jwt_identity())
    orders = OrderService.get_all_by_user(user_id)
    return jsonify([order.to_dict() for order in orders])


@orders_bp.route("/<int:order_id>", methods=["GET"])
@jwt_required()
def get_order(order_id):
    """
    Get a single order by ID with items
    ---
    tags:
      - Orders
    security:
      - Bearer: []
    parameters:
      - name: order_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Order found with items
      403:
        description: Access denied
      404:
        description: Order not found
    """
    order = OrderService.get_by_id(order_id)
    if order is None:
        return jsonify({"error": f"Order {order_id} not found"}), 404
    if order.user_id != int(get_jwt_identity()):
        return jsonify({"error": "You do not have access to this order"}), 403

    result, error = OrderService.get_order_with_items(order_id)
    return jsonify(result)


@orders_bp.route("", methods=["POST"])
@jwt_required()
def create_order():
    """
    Create a new order
    ---
    tags:
      - Orders
    security:
      - Bearer: []
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - shipping_address
          properties:
            shipping_address:
              type: string
            shipping_fee:
              type: number
            items:
              type: array
              items:
                type: object
                properties:
                  product_id:
                    type: integer
                  quantity:
                    type: integer
    responses:
      201:
        description: Order created
      400:
        description: Validation error
      404:
        description: Product not found
      409:
        description: Invalid reference
    """
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    order_create_schema = OrderCreateSchema()
    errors = order_create_schema.validate(data)
    if errors:
        return jsonify({"errors": errors}), 400

    validated = order_create_schema.load(data)
    user_id = int(get_jwt_identity())

    order, error = OrderService.create(user_id, validated)
    if error and "not found" in error:
        return jsonify({"error": error}), 404
    if error:
        return jsonify({"error": error}), 409
    return jsonify({"message": "Order created successfully", "order": order.to_dict()}), 201


@orders_bp.route("/<int:order_id>", methods=["PUT"])
@jwt_required()
def update_order(order_id):
    """
    Update an order
    ---
    tags:
      - Orders
    security:
      - Bearer: []
    parameters:
      - name: order_id
        in: path
        type: integer
        required: true
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            order_status:
              type: string
            shipping_address:
              type: string
            shipping_fee:
              type: number
    responses:
      200:
        description: Order updated
      400:
        description: Cannot change shipping address
      403:
        description: Access denied
      404:
        description: Order not found
    """
    order = OrderService.get_by_id(order_id)
    if order is None:
        return jsonify({"error": f"Order {order_id} not found"}), 404
    if order.user_id != int(get_jwt_identity()):
        return jsonify({"error": "You do not have access to this order"}), 403

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    updated_order, error = OrderService.update(order_id, data)
    if error == "not_found":
        return jsonify({"error": f"Order {order_id} not found"}), 404
    if error:
        return jsonify({"error": error}), 400
    return jsonify({"message": "Order updated", "order": updated_order.to_dict()})


@orders_bp.route("/<int:order_id>", methods=["DELETE"])
@jwt_required()
def delete_order(order_id):
    """
    Delete an order (soft delete)
    ---
    tags:
      - Orders
    security:
      - Bearer: []
    parameters:
      - name: order_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Order deleted
      403:
        description: Access denied
      404:
        description: Order not found
    """
    order = OrderService.get_by_id(order_id)
    if order is None:
        return jsonify({"error": f"Order {order_id} not found"}), 404
    if order.user_id != int(get_jwt_identity()):
        return jsonify({"error": "You do not have access to this order"}), 403

    OrderService.delete(order_id)
    return jsonify({"message": "Order deleted"}), 200


@order_items_bp.route("", methods=["GET"])
@jwt_required()
def get_order_items(order_id):
    """
    Get items for a specific order
    ---
    tags:
      - Order Items
    security:
      - Bearer: []
    parameters:
      - name: order_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: List of order items
      403:
        description: Access denied
      404:
        description: Order not found
    """
    order = OrderService.get_by_id(order_id)
    if order is None:
        return jsonify({"error": f"Order {order_id} not found"}), 404
    if order.user_id != int(get_jwt_identity()):
        return jsonify({"error": "You do not have access to this order"}), 403

    items = OrderService.get_items(order_id)
    return jsonify(items)
