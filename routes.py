from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from sqlalchemy.exc import IntegrityError
from utils import db
from models import User, Category, Product, Order, order_items

ACTIVE_ORDER_STATUSES = ("Pending", "Paid", "Shipped", "Return Process")


# ---------- Home ----------
home_bp = Blueprint("home", __name__)


@home_bp.route("/")
def home():
    return jsonify({"message": "Welcome to the Revou Shop", "status": "ok"})


# ---------- Warm-up (hardcoded seed data) ----------
warmup_bp = Blueprint("warmup", __name__, url_prefix="/warmup")


@warmup_bp.route("", methods=["GET"])
def warmup():
    """Returns hardcoded sample data based on Seed.sql for testing without DB."""
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


# ---------- Users ----------
users_bp = Blueprint("users", __name__, url_prefix="/users")


@users_bp.route("", methods=["GET"])
def get_users():
    try:
        users = User.query.all()
        return jsonify([u.to_dict() for u in users])
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@users_bp.route("/<int:user_id>", methods=["GET"])
def get_user(user_id):
    try:
        user = db.get_or_404(User, user_id)
        return jsonify(user.to_dict())
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@users_bp.route("", methods=["POST"])
def create_user():
    try:
        data = request.get_json(silent=True)
        if not data or not data.get('username') or not data.get('full_name') or not data.get('email') or not data.get('password'):
            return jsonify({"error": "Missing required field: username, full_name, email, password"}), 400

        if len(data["password"]) < 8:
            return jsonify({"error": "Password must be at least 8 characters long"}), 400

        user = User(
            username=data["username"],
            full_name=data["full_name"],
            email=data["email"],
            role=data.get("role", "Customer"),
        )
        user.set_password(data["password"])

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
    try:
        data = request.get_json(silent=True)
        if not data or not data.get("email") or not data.get("password"):
            return jsonify({"error": "Missing required field: email, password"}), 400

        user = User.query.filter_by(email=data["email"]).first()
        if not user or not user.check_password(data["password"]):
            return jsonify({"error": "Invalid email or password"}), 401

        if not user.is_active:
            return jsonify({"error": "This account has been deactivated"}), 403

        access_token = create_access_token(identity=str(user.user_id))
        return jsonify({
            "message": "Login successful",
            "access_token": access_token,
            "user": user.to_dict(),
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ---------- Categories ----------
categories_bp = Blueprint("categories", __name__, url_prefix="/categories")


@categories_bp.route("", methods=["GET"])
def get_categories():
    try:
        categories = Category.query.all()
        return jsonify([c.to_dict() for c in categories])
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@categories_bp.route("/<int:category_id>", methods=["GET"])
def get_category(category_id):
    try:
        category = db.get_or_404(Category, category_id)
        result = category.to_dict()
        result["products"] = [p.to_dict() for p in category.products]
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@categories_bp.route("", methods=["POST"])
@jwt_required()
def create_category():
    try:
        data = request.get_json()
        if not data or not data.get('category_name') or not data.get('description'):
            return jsonify({"error": "Missing required field"}), 400
        
        category = Category(
            category_name=data["category_name"],
            description=data.get("description"),
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
@jwt_required()
def update_category(category_id):
    try:
        category = db.get_or_404(Category, category_id)
        data = request.get_json()
        category.category_name = data.get("category_name", category.category_name)
        category.description = data.get("description", category.description)
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
@jwt_required()
def delete_category(category_id):
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
    try:
        products = Product.query.all()
        return jsonify([p.to_dict() for p in products])
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@products_bp.route("/<int:product_id>", methods=["GET"])
def get_product(product_id):
    try:
        product = db.get_or_404(Product, product_id)
        return jsonify(product.to_dict())
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def validate_product_payload(data, partial=False):
    """Returns an error message string, or None if the payload is valid.
    When partial=True (PUT), only fields present in the payload are checked."""
    required_fields = ["category_id", "product_name", "sku", "price"]
    if not partial:
        for field in required_fields:
            if data.get(field) in (None, ""):
                return f"Missing required field: {field}"

    if "category_id" in data and data["category_id"] is not None:
        if not Category.query.get(data["category_id"]):
            return "category_id does not reference an existing category"

    if "sku" in data and data["sku"] is not None:
        if not isinstance(data["sku"], str) or not (1 <= len(data["sku"]) <= 11):
            return "sku must be a string of at most 11 characters"

    if "price" in data and data["price"] is not None:
        try:
            price = float(data["price"])
        except (TypeError, ValueError):
            return "price must be a number"
        if price < 0:
            return "price must be greater than or equal to 0"

    if "stock_quantity" in data and data["stock_quantity"] is not None:
        stock = data["stock_quantity"]
        if not isinstance(stock, int) or isinstance(stock, bool) or stock < 0:
            return "stock_quantity must be a non-negative integer"

    return None


@products_bp.route("", methods=["POST"])
@jwt_required()
def create_product():
    try:
        data = request.get_json(silent=True)
        if not data:
            return jsonify({"error": "Missing request body"}), 400

        error = validate_product_payload(data, partial=False)
        if error:
            return jsonify({"error": error}), 400

        product = Product(
            category_id=data["category_id"],
            product_name=data["product_name"],
            sku=data["sku"],
            description=data.get("description"),
            price=data["price"],
            stock_quantity=data.get("stock_quantity", 0),
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
@jwt_required()
def update_product(product_id):
    try:
        product = db.get_or_404(Product, product_id)
        data = request.get_json(silent=True)
        if not data:
            return jsonify({"error": "Missing request body"}), 400

        error = validate_product_payload(data, partial=True)
        if error:
            return jsonify({"error": error}), 400

        product.product_name = data.get("product_name", product.product_name)
        product.sku = data.get("sku", product.sku)
        product.description = data.get("description", product.description)
        product.price = data.get("price", product.price)
        product.stock_quantity = data.get("stock_quantity", product.stock_quantity)
        product.is_active = data.get("is_active", product.is_active)
        product.category_id = data.get("category_id", product.category_id)
        db.session.commit()
        return jsonify({"message": "Product updated",
                        "product": product.to_dict()})
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "SKU already exists or invalid category"}), 409
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@products_bp.route("/<int:product_id>", methods=["DELETE"])
@jwt_required()
def delete_product(product_id):
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
    try:
        user_id = int(get_jwt_identity())
        orders = (
            Order.query.filter_by(user_id=user_id)
            .order_by(Order.ordered_at.desc())
            .all()
        )
        return jsonify([o.to_dict() for o in orders])
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@orders_bp.route("/<int:order_id>", methods=["GET"])
@jwt_required()
def get_order(order_id):
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
    try:
        data = request.get_json(silent=True)
        if not data or not data.get("shipping_address"):
            return jsonify({"error": "Missing required field: shipping_address"}), 400

        user_id = int(get_jwt_identity())

        order = Order(
            user_id=user_id,
            shipping_address=data["shipping_address"],
            shipping_fee=data.get("shipping_fee", 0),
        )
        db.session.add(order)
        db.session.flush()

        total = float(data.get("shipping_fee", 0))
        for item_data in data.get("items", []):
            if not item_data.get("product_id") or not item_data.get("quantity"):
                db.session.rollback()
                return jsonify({"error": "Each item requires product_id and quantity"}), 400

            product = db.get_or_404(Product, item_data["product_id"])
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

