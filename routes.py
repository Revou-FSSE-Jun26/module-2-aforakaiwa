from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, jwt_required
from sqlalchemy.exc import IntegrityError
from utils import db
from models import User, Category, Product, Order, order_items
from auth import roles_required
from schemas import (
    CategoryCreateSchema, CategoryUpdateSchema,
    ProductCreateSchema, ProductUpdateSchema,
    UserRegisterSchema, LoginSchema,
    OrderCreateSchema,
)

ACTIVE_ORDER_STATUSES = ("Pending", "Paid", "Shipped", "Return Process")


# ---------- Home ----------
home_bp = Blueprint("home", __name__)


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


# ---------- Warm-up (hardcoded seed data) ----------
warmup_bp = Blueprint("warmup", __name__, url_prefix="/warmup")


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
            {"user_id": 4, "username": "rina_wijaya", "full_name": "Rina Wijaya", "role": "Customer", "email": "rina.wijaya@gmail.com", "is_active": True, "created_at": "2026-01-22T13:05:00"},
            {"user_id": 5, "username": "kevin_tan", "full_name": "Kevin Tanuwijaya", "role": "Customer", "email": "kevin.tan@revoshop.dev", "is_active": True, "created_at": "2026-02-11T20:31:00"},
            {"user_id": 6, "username": "dewi_lestari", "full_name": "Dewi Lestari", "role": "Customer", "email": "dewi.lestari@gmail.com", "is_active": True, "created_at": "2026-03-02T11:17:00"},
            {"user_id": 7, "username": "fajar_ramadhan", "full_name": "Fajar Ramadhan", "role": "Customer", "email": "fajar.ramadhan@proton.me", "is_active": True, "created_at": "2026-04-19T16:48:00"},
            {"user_id": 8, "username": "maria_s", "full_name": "Maria Simanjuntak", "role": "Customer", "email": "maria.simanjuntak@gmail.com", "is_active": False, "created_at": "2026-05-27T08:03:00"},
        ],
        "categories": [
            {"category_id": 1, "category_name": "Electronics", "description": "Gadgets, computer peripherals and audio gear."},
            {"category_id": 2, "category_name": "Fashion", "description": "Clothing, footwear and everyday bags."},
            {"category_id": 3, "category_name": "Home & Living", "description": "Furniture, kitchenware and home lighting."},
            {"category_id": 4, "category_name": "Books & Stationery", "description": "Printed books, notebooks and writing tools."},
            {"category_id": 5, "category_name": "Sports & Outdoors", "description": "Fitness equipment and outdoor accessories."},
            {"category_id": 6, "category_name": "Health & Beauty", "description": "Skincare, personal care and daily essentials."},
        ],
        "products": [
            {"product_id": 1, "category_id": 1, "product_name": "Logitech MX Master 3S Wireless Mouse", "sku": "ELC-MOU-001", "price": 1450000.00, "stock_quantity": 42, "is_active": True},
            {"product_id": 2, "category_id": 1, "product_name": "Anker PowerCore 20000mAh Power Bank", "sku": "ELC-PWB-002", "price": 549000.00, "stock_quantity": 130, "is_active": True},
            {"product_id": 3, "category_id": 1, "product_name": "Samsung 27\" 4K UHD Monitor UR55", "sku": "ELC-MON-003", "price": 3899000.00, "stock_quantity": 15, "is_active": True},
            {"product_id": 4, "category_id": 1, "product_name": "Keychron K2 Mechanical Keyboard", "sku": "ELC-KEY-004", "price": 1299000.00, "stock_quantity": 25, "is_active": True},
            {"product_id": 5, "category_id": 1, "product_name": "Sony WH-1000XM5 Headphones", "sku": "ELC-HDP-005", "price": 4999000.00, "stock_quantity": 8, "is_active": True},
            {"product_id": 6, "category_id": 2, "product_name": "Uniqlo AIRism Cotton T-Shirt", "sku": "FSH-TSH-006", "price": 199000.00, "stock_quantity": 200, "is_active": True},
            {"product_id": 7, "category_id": 2, "product_name": "Levi's 511 Slim Fit Jeans", "sku": "FSH-JNS-007", "price": 899000.00, "stock_quantity": 60, "is_active": True},
            {"product_id": 8, "category_id": 2, "product_name": "Eiger Canvas Daypack 25L", "sku": "FSH-BAG-008", "price": 675000.00, "stock_quantity": 35, "is_active": True},
            {"product_id": 9, "category_id": 2, "product_name": "Adidas Runfalcon 3.0 Sneakers", "sku": "FSH-SHO-009", "price": 799000.00, "stock_quantity": 48, "is_active": True},
            {"product_id": 10, "category_id": 3, "product_name": "IKEA MARKUS Office Chair", "sku": "HML-CHR-010", "price": 2799000.00, "stock_quantity": 12, "is_active": True},
            {"product_id": 11, "category_id": 3, "product_name": "Ceramic Coffee Mug Set (4 pcs)", "sku": "HML-MUG-011", "price": 165000.00, "stock_quantity": 90, "is_active": True},
            {"product_id": 12, "category_id": 3, "product_name": "Philips LED Desk Lamp", "sku": "HML-LMP-012", "price": 349000.00, "stock_quantity": 55, "is_active": True},
            {"product_id": 13, "category_id": 3, "product_name": "Non-stick Frying Pan 24cm", "sku": "HML-PAN-013", "price": 259000.00, "stock_quantity": 70, "is_active": True},
            {"product_id": 14, "category_id": 4, "product_name": "Clean Code - Robert C. Martin", "sku": "BKS-BOK-014", "price": 585000.00, "stock_quantity": 20, "is_active": True},
            {"product_id": 15, "category_id": 4, "product_name": "Designing Data-Intensive Applications", "sku": "BKS-BOK-015", "price": 725000.00, "stock_quantity": 14, "is_active": True},
            {"product_id": 16, "category_id": 4, "product_name": "Pilot G2 Gel Pen (Box of 12)", "sku": "BKS-PEN-016", "price": 132000.00, "stock_quantity": 150, "is_active": True},
            {"product_id": 17, "category_id": 4, "product_name": "A5 Hardcover Dotted Notebook", "sku": "BKS-NTB-017", "price": 89000.00, "stock_quantity": 110, "is_active": True},
            {"product_id": 18, "category_id": 5, "product_name": "Yoga Mat TPE 6mm", "sku": "SPT-YGM-018", "price": 245000.00, "stock_quantity": 65, "is_active": True},
            {"product_id": 19, "category_id": 5, "product_name": "Adjustable Dumbbell 10kg", "sku": "SPT-DMB-019", "price": 615000.00, "stock_quantity": 22, "is_active": True},
            {"product_id": 20, "category_id": 5, "product_name": "Stainless Steel Water Bottle 1L", "sku": "SPT-BTL-020", "price": 175000.00, "stock_quantity": 95, "is_active": True},
            {"product_id": 21, "category_id": 6, "product_name": "Wardah UV Shield Sunscreen SPF 35", "sku": "HBT-SUN-021", "price": 45000.00, "stock_quantity": 180, "is_active": True},
            {"product_id": 22, "category_id": 6, "product_name": "Sensodyne Repair & Protect 100g", "sku": "HBT-TPT-022", "price": 32000.00, "stock_quantity": 0, "is_active": True},
            {"product_id": 23, "category_id": 6, "product_name": "Somethinc Niacinamide 10% Serum", "sku": "HBT-SRM-023", "price": 149000.00, "stock_quantity": 40, "is_active": False},
        ],
        "orders": [
            {"order_id": 1, "user_id": 1, "order_status": "Delivered", "shipping_address": "Jl. Margonda Raya No. 45, Beji, Depok, Jawa Barat 16424", "shipping_fee": 22000.00, "total_amount": 3369000.00, "ordered_at": "2026-02-04T10:22:00"},
            {"order_id": 2, "user_id": 2, "order_status": "Delivered", "shipping_address": "Jl. Dipatiukur No. 112, Coblong, Bandung, Jawa Barat 40132", "shipping_fee": 28000.00, "total_amount": 1599000.00, "ordered_at": "2026-02-17T15:47:00"},
            {"order_id": 3, "user_id": 3, "order_status": "Shipped", "shipping_address": "Jl. Senopati No. 8, Kebayoran Baru, Jakarta Selatan 12190", "shipping_fee": 18000.00, "total_amount": 1506000.00, "ordered_at": "2026-03-09T09:05:00"},
            {"order_id": 4, "user_id": 1, "order_status": "Delivered", "shipping_address": "Jl. Margonda Raya No. 45, Beji, Depok, Jawa Barat 16424", "shipping_fee": 22000.00, "total_amount": 581000.00, "ordered_at": "2026-03-21T19:33:00"},
            {"order_id": 5, "user_id": 4, "order_status": "Cancelled", "shipping_address": "Jl. Raya Darmo No. 77, Wonokromo, Surabaya, Jawa Timur 60241", "shipping_fee": 35000.00, "total_amount": 8933000.00, "ordered_at": "2026-04-02T08:14:00"},
            {"order_id": 6, "user_id": 5, "order_status": "Paid", "shipping_address": "Jl. Boulevard Gading Serpong Blok M2/9, Tangerang, Banten 15810", "shipping_fee": 20000.00, "total_amount": 1845000.00, "ordered_at": "2026-04-15T21:08:00"},
            {"order_id": 7, "user_id": 6, "order_status": "Delivered", "shipping_address": "Jl. Kaliurang KM 5 No. 21, Sleman, Yogyakarta 55281", "shipping_fee": 30000.00, "total_amount": 3228000.00, "ordered_at": "2026-05-06T12:41:00"},
            {"order_id": 8, "user_id": 3, "order_status": "Delivered", "shipping_address": "Jl. Senopati No. 8, Kebayoran Baru, Jakarta Selatan 12190", "shipping_fee": 18000.00, "total_amount": 5316000.00, "ordered_at": "2026-05-19T17:26:00"},
            {"order_id": 9, "user_id": 7, "order_status": "Pending", "shipping_address": "Jl. Akses UI No. 130, Tugu, Depok, Jawa Barat 16451", "shipping_fee": 22000.00, "total_amount": 1095000.00, "ordered_at": "2026-06-11T11:59:00"},
            {"order_id": 10, "user_id": 2, "order_status": "Shipped", "shipping_address": "Jl. Dipatiukur No. 112, Coblong, Bandung, Jawa Barat 40132", "shipping_fee": 28000.00, "total_amount": 507000.00, "ordered_at": "2026-06-28T14:10:00"},
            {"order_id": 11, "user_id": 5, "order_status": "Delivered", "shipping_address": "Jl. Boulevard Gading Serpong Blok M2/9, Tangerang, Banten 15810", "shipping_fee": 20000.00, "total_amount": 4219000.00, "ordered_at": "2026-07-09T09:47:00"},
            {"order_id": 12, "user_id": 6, "order_status": "Paid", "shipping_address": "Jl. Kaliurang KM 5 No. 21, Sleman, Yogyakarta 55281", "shipping_fee": 30000.00, "total_amount": 274000.00, "ordered_at": "2026-07-24T20:02:00"},
        ],
        "order_items": [
            {"order_item_id": 1, "order_id": 1, "product_id": 1, "quantity": 1, "unit_price": 1450000.00, "line_total": 1450000.00},
            {"order_item_id": 2, "order_id": 1, "product_id": 4, "quantity": 1, "unit_price": 1199000.00, "line_total": 1199000.00},
            {"order_item_id": 3, "order_id": 1, "product_id": 12, "quantity": 2, "unit_price": 349000.00, "line_total": 698000.00},
            {"order_item_id": 4, "order_id": 2, "product_id": 6, "quantity": 3, "unit_price": 199000.00, "line_total": 597000.00},
            {"order_item_id": 5, "order_id": 2, "product_id": 9, "quantity": 1, "unit_price": 799000.00, "line_total": 799000.00},
            {"order_item_id": 6, "order_id": 2, "product_id": 20, "quantity": 1, "unit_price": 175000.00, "line_total": 175000.00},
            {"order_item_id": 7, "order_id": 3, "product_id": 14, "quantity": 1, "unit_price": 585000.00, "line_total": 585000.00},
            {"order_item_id": 8, "order_id": 3, "product_id": 15, "quantity": 1, "unit_price": 725000.00, "line_total": 725000.00},
            {"order_item_id": 9, "order_id": 3, "product_id": 17, "quantity": 2, "unit_price": 89000.00, "line_total": 178000.00},
            {"order_item_id": 10, "order_id": 4, "product_id": 11, "quantity": 1, "unit_price": 165000.00, "line_total": 165000.00},
            {"order_item_id": 11, "order_id": 4, "product_id": 13, "quantity": 1, "unit_price": 259000.00, "line_total": 259000.00},
            {"order_item_id": 12, "order_id": 4, "product_id": 21, "quantity": 3, "unit_price": 45000.00, "line_total": 135000.00},
            {"order_item_id": 13, "order_id": 5, "product_id": 5, "quantity": 1, "unit_price": 4999000.00, "line_total": 4999000.00},
            {"order_item_id": 14, "order_id": 5, "product_id": 3, "quantity": 1, "unit_price": 3899000.00, "line_total": 3899000.00},
            {"order_item_id": 15, "order_id": 6, "product_id": 18, "quantity": 1, "unit_price": 245000.00, "line_total": 245000.00},
            {"order_item_id": 16, "order_id": 6, "product_id": 19, "quantity": 2, "unit_price": 615000.00, "line_total": 1230000.00},
            {"order_item_id": 17, "order_id": 6, "product_id": 20, "quantity": 2, "unit_price": 175000.00, "line_total": 350000.00},
            {"order_item_id": 18, "order_id": 7, "product_id": 10, "quantity": 1, "unit_price": 2799000.00, "line_total": 2799000.00},
            {"order_item_id": 19, "order_id": 7, "product_id": 16, "quantity": 1, "unit_price": 132000.00, "line_total": 132000.00},
            {"order_item_id": 20, "order_id": 7, "product_id": 17, "quantity": 3, "unit_price": 89000.00, "line_total": 267000.00},
            {"order_item_id": 21, "order_id": 8, "product_id": 5, "quantity": 1, "unit_price": 4749000.00, "line_total": 4749000.00},
            {"order_item_id": 22, "order_id": 8, "product_id": 2, "quantity": 1, "unit_price": 549000.00, "line_total": 549000.00},
            {"order_item_id": 23, "order_id": 9, "product_id": 6, "quantity": 2, "unit_price": 199000.00, "line_total": 398000.00},
            {"order_item_id": 24, "order_id": 9, "product_id": 8, "quantity": 1, "unit_price": 675000.00, "line_total": 675000.00},
            {"order_item_id": 25, "order_id": 10, "product_id": 11, "quantity": 2, "unit_price": 165000.00, "line_total": 330000.00},
            {"order_item_id": 26, "order_id": 10, "product_id": 23, "quantity": 1, "unit_price": 149000.00, "line_total": 149000.00},
            {"order_item_id": 27, "order_id": 11, "product_id": 1, "quantity": 2, "unit_price": 1450000.00, "line_total": 2900000.00},
            {"order_item_id": 28, "order_id": 11, "product_id": 4, "quantity": 1, "unit_price": 1299000.00, "line_total": 1299000.00},
            {"order_item_id": 29, "order_id": 12, "product_id": 21, "quantity": 4, "unit_price": 45000.00, "line_total": 180000.00},
            {"order_item_id": 30, "order_id": 12, "product_id": 22, "quantity": 2, "unit_price": 32000.00, "line_total": 64000.00},
        ],
    }
    return jsonify(data)


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
    products = [
        {"product_id": 1, "category_id": 1, "product_name": "Logitech MX Master 3S Wireless Mouse", "sku": "ELC-MOU-001", "price": 1450000.00, "stock_quantity": 42, "is_active": True},
        {"product_id": 2, "category_id": 1, "product_name": "Anker PowerCore 20000mAh Power Bank", "sku": "ELC-PWB-002", "price": 549000.00, "stock_quantity": 130, "is_active": True},
        {"product_id": 3, "category_id": 1, "product_name": "Samsung 27\" 4K UHD Monitor UR55", "sku": "ELC-MON-003", "price": 3899000.00, "stock_quantity": 15, "is_active": True},
        {"product_id": 4, "category_id": 1, "product_name": "Keychron K2 Mechanical Keyboard", "sku": "ELC-KEY-004", "price": 1299000.00, "stock_quantity": 25, "is_active": True},
        {"product_id": 5, "category_id": 1, "product_name": "Sony WH-1000XM5 Headphones", "sku": "ELC-HDP-005", "price": 4999000.00, "stock_quantity": 8, "is_active": True},
        {"product_id": 6, "category_id": 2, "product_name": "Uniqlo AIRism Cotton T-Shirt", "sku": "FSH-TSH-006", "price": 199000.00, "stock_quantity": 200, "is_active": True},
        {"product_id": 7, "category_id": 2, "product_name": "Levi's 511 Slim Fit Jeans", "sku": "FSH-JNS-007", "price": 899000.00, "stock_quantity": 60, "is_active": True},
        {"product_id": 8, "category_id": 2, "product_name": "Eiger Canvas Daypack 25L", "sku": "FSH-BAG-008", "price": 675000.00, "stock_quantity": 35, "is_active": True},
        {"product_id": 9, "category_id": 2, "product_name": "Adidas Runfalcon 3.0 Sneakers", "sku": "FSH-SHO-009", "price": 799000.00, "stock_quantity": 48, "is_active": True},
        {"product_id": 10, "category_id": 3, "product_name": "IKEA MARKUS Office Chair", "sku": "HML-CHR-010", "price": 2799000.00, "stock_quantity": 12, "is_active": True},
        {"product_id": 11, "category_id": 3, "product_name": "Ceramic Coffee Mug Set (4 pcs)", "sku": "HML-MUG-011", "price": 165000.00, "stock_quantity": 90, "is_active": True},
        {"product_id": 12, "category_id": 3, "product_name": "Philips LED Desk Lamp", "sku": "HML-LMP-012", "price": 349000.00, "stock_quantity": 55, "is_active": True},
        {"product_id": 13, "category_id": 3, "product_name": "Non-stick Frying Pan 24cm", "sku": "HML-PAN-013", "price": 259000.00, "stock_quantity": 70, "is_active": True},
        {"product_id": 14, "category_id": 4, "product_name": "Clean Code - Robert C. Martin", "sku": "BKS-BOK-014", "price": 585000.00, "stock_quantity": 20, "is_active": True},
        {"product_id": 15, "category_id": 4, "product_name": "Designing Data-Intensive Applications", "sku": "BKS-BOK-015", "price": 725000.00, "stock_quantity": 14, "is_active": True},
        {"product_id": 16, "category_id": 4, "product_name": "Pilot G2 Gel Pen (Box of 12)", "sku": "BKS-PEN-016", "price": 132000.00, "stock_quantity": 150, "is_active": True},
        {"product_id": 17, "category_id": 4, "product_name": "A5 Hardcover Dotted Notebook", "sku": "BKS-NTB-017", "price": 89000.00, "stock_quantity": 110, "is_active": True},
        {"product_id": 18, "category_id": 5, "product_name": "Yoga Mat TPE 6mm", "sku": "SPT-YGM-018", "price": 245000.00, "stock_quantity": 65, "is_active": True},
        {"product_id": 19, "category_id": 5, "product_name": "Adjustable Dumbbell 10kg", "sku": "SPT-DMB-019", "price": 615000.00, "stock_quantity": 22, "is_active": True},
        {"product_id": 20, "category_id": 5, "product_name": "Stainless Steel Water Bottle 1L", "sku": "SPT-BTL-020", "price": 175000.00, "stock_quantity": 95, "is_active": True},
        {"product_id": 21, "category_id": 6, "product_name": "Wardah UV Shield Sunscreen SPF 35", "sku": "HBT-SUN-021", "price": 45000.00, "stock_quantity": 180, "is_active": True},
        {"product_id": 22, "category_id": 6, "product_name": "Sensodyne Repair & Protect 100g", "sku": "HBT-TPT-022", "price": 32000.00, "stock_quantity": 0, "is_active": True},
        {"product_id": 23, "category_id": 6, "product_name": "Somethinc Niacinamide 10% Serum", "sku": "HBT-SRM-023", "price": 149000.00, "stock_quantity": 40, "is_active": False},
    ]
    return jsonify(products)


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
        description: Product ID
    responses:
      200:
        description: Product found
      404:
        description: Product not found
    """
    products = [
        {"product_id": 1, "category_id": 1, "product_name": "Logitech MX Master 3S Wireless Mouse", "sku": "ELC-MOU-001", "price": 1450000.00, "stock_quantity": 42, "is_active": True},
        {"product_id": 2, "category_id": 1, "product_name": "Anker PowerCore 20000mAh Power Bank", "sku": "ELC-PWB-002", "price": 549000.00, "stock_quantity": 130, "is_active": True},
        {"product_id": 3, "category_id": 1, "product_name": "Samsung 27\" 4K UHD Monitor UR55", "sku": "ELC-MON-003", "price": 3899000.00, "stock_quantity": 15, "is_active": True},
        {"product_id": 4, "category_id": 1, "product_name": "Keychron K2 Mechanical Keyboard", "sku": "ELC-KEY-004", "price": 1299000.00, "stock_quantity": 25, "is_active": True},
        {"product_id": 5, "category_id": 1, "product_name": "Sony WH-1000XM5 Headphones", "sku": "ELC-HDP-005", "price": 4999000.00, "stock_quantity": 8, "is_active": True},
        {"product_id": 6, "category_id": 2, "product_name": "Uniqlo AIRism Cotton T-Shirt", "sku": "FSH-TSH-006", "price": 199000.00, "stock_quantity": 200, "is_active": True},
        {"product_id": 7, "category_id": 2, "product_name": "Levi's 511 Slim Fit Jeans", "sku": "FSH-JNS-007", "price": 899000.00, "stock_quantity": 60, "is_active": True},
        {"product_id": 8, "category_id": 2, "product_name": "Eiger Canvas Daypack 25L", "sku": "FSH-BAG-008", "price": 675000.00, "stock_quantity": 35, "is_active": True},
        {"product_id": 9, "category_id": 2, "product_name": "Adidas Runfalcon 3.0 Sneakers", "sku": "FSH-SHO-009", "price": 799000.00, "stock_quantity": 48, "is_active": True},
        {"product_id": 10, "category_id": 3, "product_name": "IKEA MARKUS Office Chair", "sku": "HML-CHR-010", "price": 2799000.00, "stock_quantity": 12, "is_active": True},
        {"product_id": 11, "category_id": 3, "product_name": "Ceramic Coffee Mug Set (4 pcs)", "sku": "HML-MUG-011", "price": 165000.00, "stock_quantity": 90, "is_active": True},
        {"product_id": 12, "category_id": 3, "product_name": "Philips LED Desk Lamp", "sku": "HML-LMP-012", "price": 349000.00, "stock_quantity": 55, "is_active": True},
        {"product_id": 13, "category_id": 3, "product_name": "Non-stick Frying Pan 24cm", "sku": "HML-PAN-013", "price": 259000.00, "stock_quantity": 70, "is_active": True},
        {"product_id": 14, "category_id": 4, "product_name": "Clean Code - Robert C. Martin", "sku": "BKS-BOK-014", "price": 585000.00, "stock_quantity": 20, "is_active": True},
        {"product_id": 15, "category_id": 4, "product_name": "Designing Data-Intensive Applications", "sku": "BKS-BOK-015", "price": 725000.00, "stock_quantity": 14, "is_active": True},
        {"product_id": 16, "category_id": 4, "product_name": "Pilot G2 Gel Pen (Box of 12)", "sku": "BKS-PEN-016", "price": 132000.00, "stock_quantity": 150, "is_active": True},
        {"product_id": 17, "category_id": 4, "product_name": "A5 Hardcover Dotted Notebook", "sku": "BKS-NTB-017", "price": 89000.00, "stock_quantity": 110, "is_active": True},
        {"product_id": 18, "category_id": 5, "product_name": "Yoga Mat TPE 6mm", "sku": "SPT-YGM-018", "price": 245000.00, "stock_quantity": 65, "is_active": True},
        {"product_id": 19, "category_id": 5, "product_name": "Adjustable Dumbbell 10kg", "sku": "SPT-DMB-019", "price": 615000.00, "stock_quantity": 22, "is_active": True},
        {"product_id": 20, "category_id": 5, "product_name": "Stainless Steel Water Bottle 1L", "sku": "SPT-BTL-020", "price": 175000.00, "stock_quantity": 95, "is_active": True},
        {"product_id": 21, "category_id": 6, "product_name": "Wardah UV Shield Sunscreen SPF 35", "sku": "HBT-SUN-021", "price": 45000.00, "stock_quantity": 180, "is_active": True},
        {"product_id": 22, "category_id": 6, "product_name": "Sensodyne Repair & Protect 100g", "sku": "HBT-TPT-022", "price": 32000.00, "stock_quantity": 0, "is_active": True},
        {"product_id": 23, "category_id": 6, "product_name": "Somethinc Niacinamide 10% Serum", "sku": "HBT-SRM-023", "price": 149000.00, "stock_quantity": 40, "is_active": False},
    ]
    product = None
    for product in products:
        if product["product_id"] == product_id:
            break
    else:
        product = None
    if product is None:
        return jsonify({"error": "Product not found"}), 404
    return jsonify(product)


# ---------- Users ----------
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
      500:
        description: Internal server error
    """
    try:
        users = User.query.all()
        return jsonify([user.to_dict() for user in users])
    except Exception as e:
        return jsonify({"error": str(e)}), 500


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
        description: User ID
    responses:
      200:
        description: User found
      404:
        description: User not found
      500:
        description: Internal server error
    """
    try:
        user = db.get_or_404(User, user_id)
        return jsonify(user.to_dict())
    except Exception as e:
        return jsonify({"error": str(e)}), 500


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
              example: john_doe
            full_name:
              type: string
              example: John Doe
            email:
              type: string
              example: john@example.com
            password:
              type: string
              example: securepass123
            role:
              type: string
              example: Customer
    responses:
      201:
        description: User registered successfully
      400:
        description: Missing required field or invalid password
      409:
        description: Username or email already exists
      500:
        description: Internal server error
    """
    try:
        data = request.get_json(silent=True)
        if not data:
            return jsonify({"error": "Request body must be JSON"}), 400

        user_register_schema = UserRegisterSchema()
        errors = user_register_schema.validate(data)
        if errors:
            return jsonify({"errors": errors}), 400

        validated = user_register_schema.load(data)
        user = User(
            username=validated["username"],
            full_name=validated["full_name"],
            email=validated["email"],
            role=validated["role"],
        )
        user.set_password(validated["password"])

        db.session.add(user)
        db.session.commit()
        return jsonify({"message": "User registered successfully",
                        "user": user.to_dict()}), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Username or email already exists"}), 409
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


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
        description: User ID
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
      409:
        description: Email already exists
      500:
        description: Internal server error
    """
    try:
        user = db.get_or_404(User, user_id)
        data = request.get_json()
        user.username = data.get("username", user.username)
        user.full_name = data.get("full_name", user.full_name)
        user.role = data.get("role", user.role)
        user.email = data.get("email", user.email)
        user.is_active = data.get("is_active", user.is_active)
        db.session.commit()
        return jsonify({"message": "User updated",
                        "user": user.to_dict()})
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Email already exists"}), 409
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@users_bp.route("/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    """
    Delete a user
    ---
    tags:
      - Users
    parameters:
      - name: user_id
        in: path
        type: integer
        required: true
        description: User ID
    responses:
      200:
        description: User deleted
      409:
        description: Cannot delete user with existing orders
      500:
        description: Internal server error
    """
    try:
        user = db.get_or_404(User, user_id)
        db.session.delete(user)
        db.session.commit()
        return jsonify({"message": "User deleted"}), 200
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Cannot delete user with existing orders"}), 409
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


# ---------- Auth ----------
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
              example: john@example.com
            password:
              type: string
              example: securepass123
    responses:
      200:
        description: Login successful, returns access token
      400:
        description: Missing required field
      401:
        description: Invalid email or password
      403:
        description: Account deactivated
      500:
        description: Internal server error
    """
    try:
        data = request.get_json(silent=True)
        if not data:
            return jsonify({"error": "Request body must be JSON"}), 400

        login_schema = LoginSchema()
        errors = login_schema.validate(data)
        if errors:
            return jsonify({"errors": errors}), 400

        validated = login_schema.load(data)
        user = User.query.filter_by(email=validated["email"]).first()
        if not user or not user.check_password(validated["password"]):
            return jsonify({"error": "Invalid email or password"}), 401

        if not user.is_active:
            return jsonify({"error": "This account has been deactivated"}), 403

        access_token = create_access_token(
            identity=str(user.user_id),
            additional_claims={"role": user.role}
        )
        refresh_token = create_refresh_token(
            identity=str(user.user_id),
            additional_claims={"role": user.role}
        )
        return jsonify({
            "message": "Login successful",
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": user.to_dict(),
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


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
    user = db.session.get(User, int(current_user_id))
    if user is None:
        return jsonify({"error": "User not found"}), 401

    new_access_token = create_access_token(
        identity=current_user_id,
        additional_claims={"role": user.role},
        fresh=False
    )
    return jsonify({"access_token": new_access_token}), 200


# ---------- Categories ----------
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
      500:
        description: Internal server error
    """
    try:
        categories = Category.query.all()
        return jsonify([category.to_dict() for category in categories])
    except Exception as e:
        return jsonify({"error": str(e)}), 500


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
        description: Category ID
    responses:
      200:
        description: Category found with products
      404:
        description: Category not found
      500:
        description: Internal server error
    """
    try:
        category = db.get_or_404(Category, category_id)
        result = category.to_dict()
        result["products"] = [product.to_dict() for product in category.products]
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@categories_bp.route("", methods=["POST"])
@roles_required("Admin")
def create_category():
    """
    Create a new category (requires JWT)
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
              example: Electronics
            description:
              type: string
              example: Gadgets and peripherals
    responses:
      201:
        description: Category created
      400:
        description: Missing required field
      409:
        description: Category name already exists
      500:
        description: Internal server error
    """
    try:
        data = request.get_json(silent=True)
        if not data:
            return jsonify({"error": "Request body must be JSON"}), 400

        category_create_schema = CategoryCreateSchema()
        errors = category_create_schema.validate(data)
        if errors:
            return jsonify({"errors": errors}), 400

        validated = category_create_schema.load(data)
        category = Category(
            category_name=validated["category_name"],
            description=validated["description"],
        )
        db.session.add(category)
        db.session.commit()
        return jsonify(category.to_dict()), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Category name already exists"}), 409
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@categories_bp.route("/<int:category_id>", methods=["PUT"])
@roles_required("Admin")
def update_category(category_id):
    """
    Update a category (requires JWT)
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
        description: Category ID
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
      409:
        description: Category name already exists
      500:
        description: Internal server error
    """
    try:
        category = db.get_or_404(Category, category_id)
        data = request.get_json(silent=True)
        if not data:
            return jsonify({"error": "Request body must be JSON"}), 400

        category_update_schema = CategoryUpdateSchema()
        errors = category_update_schema.validate(data)
        if errors:
            return jsonify({"errors": errors}), 400

        validated = category_update_schema.load(data)
        if "category_name" in validated:
            category.category_name = validated["category_name"]
        if "description" in validated:
            category.description = validated["description"]
        db.session.commit()
        return jsonify({"message": "category update successfully",
                        "category": category.to_dict()})
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Category name already exists"}), 409
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@categories_bp.route("/<int:category_id>", methods=["DELETE"])
@roles_required("Admin")
def delete_category(category_id):
    """
    Delete a category (requires JWT)
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
        description: Category ID
    responses:
      200:
        description: Category deleted
      409:
        description: Cannot delete category with existing products
      500:
        description: Internal server error
    """
    try:
        category = db.get_or_404(Category, category_id)
        db.session.delete(category)
        db.session.commit()
        return jsonify({"message": "Category deleted"}), 200
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Cannot delete category with existing products"}), 409
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


# ---------- Products ----------
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
        description: Page number
      - name: per_page
        in: query
        type: integer
        default: 5
        description: Items per page
    responses:
      200:
        description: Paginated list of products
      500:
        description: Internal server error
    """
    try:
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 5, type=int)

        pagination = Product.query.paginate(page=page, per_page=per_page, error_out=False)

        return jsonify({
            "products": [product.to_dict() for product in pagination.items],
            "page": pagination.page,
            "per_page": pagination.per_page,
            "total_pages": pagination.pages,
            "total_items": pagination.total,
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


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
        description: Product ID
    responses:
      200:
        description: Product found
      404:
        description: Product not found
      500:
        description: Internal server error
    """
    try:
        product = db.session.get(Product, product_id)
        if product is None:
            return jsonify({"error": f"Product {product_id} not found"}), 404
        return jsonify(product.to_dict())
    except Exception as e:
        return jsonify({"error": str(e)}), 500




@products_bp.route("", methods=["POST"])
@roles_required("Admin")
def create_product():
    """
    Create a new product (requires JWT)
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
              example: 1
            product_name:
              type: string
              example: Wireless Mouse
            sku:
              type: string
              example: ELC-MOU-01
            description:
              type: string
              example: A wireless mouse
            price:
              type: number
              example: 350000
            stock_quantity:
              type: integer
              example: 50
    responses:
      201:
        description: Product created
      400:
        description: Missing required field or validation error
      409:
        description: SKU already exists
      500:
        description: Internal server error
    """
    try:
        data = request.get_json(silent=True)
        if not data:
            return jsonify({"error": "Request body must be JSON"}), 400

        product_create_schema = ProductCreateSchema()
        errors = product_create_schema.validate(data)
        if errors:
            return jsonify({"errors": errors}), 400

        validated = product_create_schema.load(data)
        product = Product(
            category_id=validated["category_id"],
            product_name=validated["product_name"].strip(),
            sku=validated["sku"],
            description=validated.get("description"),
            price=validated["price"],
            stock_quantity=validated.get("stock_quantity", 0),
        )
        db.session.add(product)
        db.session.commit()
        return jsonify({"message": "Product added",
                        "product": product.to_dict()}), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "SKU already exists or invalid category"}), 409
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@products_bp.route("/<int:product_id>", methods=["PUT"])
@roles_required("Admin")
def update_product(product_id):
    """
    Update a product (requires JWT)
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
        description: Product ID
      - name: body
        in: body
        required: true
        schema:
          type: object
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
            is_active:
              type: boolean
    responses:
      200:
        description: Product updated
      400:
        description: Validation error
      409:
        description: SKU already exists
      500:
        description: Internal server error
    """
    try:
        product = db.session.get(Product, product_id)
        if product is None:
            return jsonify({"error": f"Product {product_id} not found"}), 404
        data = request.get_json(silent=True)
        if not data:
            return jsonify({"error": "Request body must be JSON"}), 400

        product_update_schema = ProductUpdateSchema()
        errors = product_update_schema.validate(data)
        if errors:
            return jsonify({"errors": errors}), 400

        validated = product_update_schema.load(data)
        if "product_name" in validated:
            product.product_name = validated["product_name"].strip()
        if "sku" in validated:
            product.sku = validated["sku"]
        if "description" in validated:
            product.description = validated["description"]
        if "price" in validated:
            product.price = validated["price"]
        if "stock_quantity" in validated:
            product.stock_quantity = validated["stock_quantity"]
        if "is_active" in validated:
            product.is_active = validated["is_active"]
        if "category_id" in validated:
            product.category_id = validated["category_id"]
        db.session.commit()
        return jsonify({"message": "Product updated",
                        "product": product.to_dict()}), 200
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "SKU already exists or invalid category"}), 409
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@products_bp.route("/<int:product_id>", methods=["DELETE"])
@roles_required("Admin")
def delete_product(product_id):
    """
    Delete a product (requires JWT)
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
        description: Product ID
    responses:
      200:
        description: Product deleted
      409:
        description: Cannot delete product with active orders
      500:
        description: Internal server error
    """
    try:
        product = db.get_or_404(Product, product_id)

        active_order_exists = (
            db.session.query(order_items)
            .join(Order, Order.order_id == order_items.c.order_id)
            .filter(
                order_items.c.product_id == product_id,
                Order.order_status.in_(ACTIVE_ORDER_STATUSES),
            )
            .first()
        )
        if active_order_exists:
            return jsonify({"error": "Cannot delete product with active orders"}), 409

        db.session.delete(product)
        db.session.commit()
        return jsonify({"message": "Product deleted"}), 200
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Cannot delete product with existing order items"}), 409
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


# ---------- Orders ----------
orders_bp = Blueprint("orders", __name__, url_prefix="/orders")


@orders_bp.route("", methods=["GET"])
@jwt_required()
def get_orders():
    """
    Get all orders for the authenticated user (requires JWT)
    ---
    tags:
      - Orders
    security:
      - Bearer: []
    responses:
      200:
        description: List of user orders
      500:
        description: Internal server error
    """
    try:
        user_id = int(get_jwt_identity())
        orders = (
            Order.query.filter_by(user_id=user_id)
            .order_by(Order.ordered_at.desc())
            .all()
        )
        return jsonify([order.to_dict() for order in orders])
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@orders_bp.route("/<int:order_id>", methods=["GET"])
@jwt_required()
def get_order(order_id):
    """
    Get a single order by ID with items (requires JWT)
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
        description: Order ID
    responses:
      200:
        description: Order found with items
      403:
        description: Access denied
      404:
        description: Order not found
      500:
        description: Internal server error
    """
    try:
        order = db.get_or_404(Order, order_id)
        if order.user_id != int(get_jwt_identity()):
            return jsonify({"error": "You do not have access to this order"}), 403

        result = order.to_dict()
        items = db.session.execute(
            order_items.select().where(order_items.c.order_id == order_id)
        ).fetchall()
        item_list = []
        for row in items:
            product = db.session.get(Product, row.product_id)
            item_list.append({
                "order_item_id": row.order_item_id,
                "product_id": row.product_id,
                "quantity": row.quantity,
                "unit_price": float(row.unit_price),
                "line_total": float(row.line_total) if row.line_total else None,
                "product": product.to_dict() if product else None,
            })
        result["items"] = item_list
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@orders_bp.route("", methods=["POST"])
@jwt_required()
def create_order():
    """
    Create a new order (requires JWT)
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
              example: Jl. Test No. 1, Jakarta
            shipping_fee:
              type: number
              example: 15000
            items:
              type: array
              items:
                type: object
                properties:
                  product_id:
                    type: integer
                    example: 1
                  quantity:
                    type: integer
                    example: 2
    responses:
      201:
        description: Order created successfully
      400:
        description: Missing required field or invalid items
      409:
        description: Invalid user or product reference
      500:
        description: Internal server error
    """
    try:
        data = request.get_json(silent=True)
        if not data:
            return jsonify({"error": "Request body must be JSON"}), 400

        order_create_schema = OrderCreateSchema()
        errors = order_create_schema.validate(data)
        if errors:
            return jsonify({"errors": errors}), 400

        validated = order_create_schema.load(data)
        user_id = int(get_jwt_identity())

        order = Order(
            user_id=user_id,
            shipping_address=validated["shipping_address"],
            shipping_fee=validated["shipping_fee"],
        )
        db.session.add(order)
        db.session.flush()

        total = float(validated["shipping_fee"])
        for item_data in validated["items"]:
            product = db.session.get(Product, item_data["product_id"])
            if product is None:
                db.session.rollback()
                return jsonify({"error": f"Product {item_data['product_id']} not found"}), 404

            unit_price = float(product.price)
            quantity = item_data["quantity"]
            line_total = unit_price * quantity
            total += line_total

            db.session.execute(order_items.insert().values(
                order_id=order.order_id,
                product_id=product.product_id,
                quantity=quantity,
                unit_price=unit_price,
                line_total=line_total,
            ))

        order.total_amount = total
        db.session.commit()
        return jsonify({"message": "Order created successfully",
                       "order": order.to_dict()}), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Invalid user or product reference"}), 409
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@orders_bp.route("/<int:order_id>", methods=["PUT"])
@jwt_required()
def update_order(order_id):
    """
    Update an order (requires JWT)
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
        description: Order ID
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            order_status:
              type: string
              example: Paid
            shipping_address:
              type: string
            shipping_fee:
              type: number
    responses:
      200:
        description: Order updated
      400:
        description: Cannot change shipping address for shipped/delivered/cancelled orders
      403:
        description: Access denied
      409:
        description: Invalid order status
      500:
        description: Internal server error
    """
    try:
        order = db.get_or_404(Order, order_id)
        if order.user_id != int(get_jwt_identity()):
            return jsonify({"error": "You do not have access to this order"}), 403

        data = request.get_json()

        # Block shipping address changes if order is already shipped/delivered/cancelled
        if data.get("shipping_address") and order.order_status in ("Delivered", "Cancelled", "Shipped"):
            return jsonify({"error": "Shipping address cannot be changed for orders that are Shipped, Delivered, or Cancelled"}), 400

        order.order_status = data.get("order_status", order.order_status)
        order.shipping_address = data.get("shipping_address", order.shipping_address)

        # Recalculate total_amount if shipping_fee is updated
        if "shipping_fee" in data:
            old_shipping = float(order.shipping_fee)
            new_shipping = float(data["shipping_fee"])
            order.shipping_fee = new_shipping
            order.total_amount = float(order.total_amount) - old_shipping + new_shipping

        db.session.commit()
        return jsonify({"message": "Order updated", "order": order.to_dict()})
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Invalid order status"}), 409
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@orders_bp.route("/<int:order_id>", methods=["DELETE"])
@jwt_required()
def delete_order(order_id):
    """
    Delete an order (requires JWT)
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
        description: Order ID
    responses:
      200:
        description: Order deleted
      403:
        description: Access denied
      409:
        description: Cannot delete this order
      500:
        description: Internal server error
    """
    try:
        order = db.get_or_404(Order, order_id)
        if order.user_id != int(get_jwt_identity()):
            return jsonify({"error": "You do not have access to this order"}), 403

        db.session.delete(order)
        db.session.commit()
        return jsonify({"message": "Order deleted"}), 200
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Cannot delete this order"}), 409
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


# ---------- Order Items ----------
order_items_bp = Blueprint("order_items", __name__, url_prefix="/orders/<int:order_id>/items")


@order_items_bp.route("", methods=["GET"])
@jwt_required()
def get_order_items(order_id):
    """
    Get items for a specific order (requires JWT)
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
        description: Order ID
    responses:
      200:
        description: List of order items
      403:
        description: Access denied
      404:
        description: Order not found
      500:
        description: Internal server error
    """
    try:
        order = db.get_or_404(Order, order_id)
        if order.user_id != int(get_jwt_identity()):
            return jsonify({"error": "You do not have access to this order"}), 403

        items = db.session.execute(
            order_items.select().where(order_items.c.order_id == order_id)
        ).fetchall()
        return jsonify([
            {
                "order_item_id": row.order_item_id,
                "order_id": row.order_id,
                "product_id": row.product_id,
                "quantity": row.quantity,
                "unit_price": float(row.unit_price),
                "line_total": float(row.line_total) if row.line_total else None,
            }
            for row in items
        ])
    except Exception as e:
        return jsonify({"error": str(e)}), 500
