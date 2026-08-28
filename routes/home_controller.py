from flask import Blueprint, jsonify

home_bp = Blueprint("home", __name__)
warmup_bp = Blueprint("warmup", __name__, url_prefix="/warmup")


@home_bp.route("/")
def home():
    """
    Home endpoint
    ---
    tags:
      - Home
    responses:
      200:
        description: Welcome message
    """
    return jsonify({"message": "Welcome to the Revou Shop", "status": "ok"})


@warmup_bp.route("", methods=["GET"])
def warmup():
    """
    Get all hardcoded sample data
    ---
    tags:
      - Warmup
    responses:
      200:
        description: Hardcoded sample data (users, categories, products, orders, order_items)
    """
    data = {
        "users": [
            {"user_id": 1, "username": "andi_pratama", "full_name": "Andi Pratama", "role": "Customer", "email": "andi.pratama@gmail.com", "is_active": True, "created_at": "2025-11-03T09:12:00"},
            {"user_id": 2, "username": "siti_nurhaliza", "full_name": "Siti Nurhaliza", "role": "Customer", "email": "siti.nurhaliza@yahoo.com", "is_active": True, "created_at": "2025-12-14T18:40:00"},
            {"user_id": 3, "username": "budi_santoso", "full_name": "Budi Santoso", "role": "Customer", "email": "budi.santoso@outlook.com", "is_active": True, "created_at": "2026-01-08T07:55:00"},
        ],
        "categories": [
            {"category_id": 1, "category_name": "Electronics", "description": "Gadgets, computer peripherals and audio gear."},
            {"category_id": 2, "category_name": "Fashion", "description": "Clothing, footwear and everyday bags."},
        ],
        "products": [
            {"product_id": 1, "category_id": 1, "product_name": "Logitech MX Master 3S Wireless Mouse", "sku": "ELC-MOU-001", "price": 1450000.00, "stock_quantity": 42, "is_active": True},
            {"product_id": 2, "category_id": 1, "product_name": "Anker PowerCore 20000mAh Power Bank", "sku": "ELC-PWB-002", "price": 549000.00, "stock_quantity": 130, "is_active": True},
        ],
        "orders": [
            {"order_id": 1, "user_id": 1, "order_status": "Delivered", "shipping_address": "Jl. Margonda Raya No. 45", "shipping_fee": 22000.00, "total_amount": 3369000.00, "ordered_at": "2026-02-04T10:22:00"},
        ],
        "order_items": [
            {"order_item_id": 1, "order_id": 1, "product_id": 1, "quantity": 1, "unit_price": 1450000.00, "line_total": 1450000.00},
        ],
    }
    return jsonify(data)


HARDCODED_PRODUCTS = [
    {"product_id": 1, "category_id": 1, "product_name": "Logitech MX Master 3S Wireless Mouse", "sku": "ELC-MOU-001", "price": 1450000.00, "stock_quantity": 42, "is_active": True},
    {"product_id": 2, "category_id": 1, "product_name": "Anker PowerCore 20000mAh Power Bank", "sku": "ELC-PWB-002", "price": 549000.00, "stock_quantity": 130, "is_active": True},
    {"product_id": 3, "category_id": 1, "product_name": "Samsung 27\" 4K UHD Monitor UR55", "sku": "ELC-MON-003", "price": 3899000.00, "stock_quantity": 15, "is_active": True},
    {"product_id": 4, "category_id": 1, "product_name": "Keychron K2 Mechanical Keyboard", "sku": "ELC-KEY-004", "price": 1299000.00, "stock_quantity": 25, "is_active": True},
    {"product_id": 5, "category_id": 1, "product_name": "Sony WH-1000XM5 Headphones", "sku": "ELC-HDP-005", "price": 4999000.00, "stock_quantity": 8, "is_active": True},
]


@warmup_bp.route("/products", methods=["GET"])
def warmup_products():
    """
    Get all hardcoded products
    ---
    tags:
      - Warmup
    responses:
      200:
        description: Full list of hardcoded products
    """
    return jsonify(HARDCODED_PRODUCTS)


@warmup_bp.route("/products/<int:product_id>", methods=["GET"])
def warmup_product(product_id):
    """
    Get a single hardcoded product by ID
    ---
    tags:
      - Warmup
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
    product = None
    for product in HARDCODED_PRODUCTS:
        if product["product_id"] == product_id:
            break
    else:
        product = None
    if product is None:
        return jsonify({"error": "Product not found"}), 404
    return jsonify(product)
