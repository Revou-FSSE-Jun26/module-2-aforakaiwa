from flask import Blueprint, request, jsonify
from sqlalchemy.exc import IntegrityError
from utils import db
from models import User, Category, Product, Order, order_items


# ---------- Home ----------
home_bp = Blueprint("home", __name__)


@home_bp.route("/")
def home():
    return jsonify({"message": "Welcome to the Revou Shop", "status": "ok"})


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
        data = request.get_json()
        if not data or not data.get('full_name') or not data.get('email') or not data.get('password_hash'):
            return jsonify({"error": "Missing required field"}), 400

        user = User(
            full_name=data["full_name"],
            email=data["email"],
            password_hash=data["password_hash"],
        )

        db.session.add(user)
        db.session.commit()
        return jsonify({"message": "User registered succesfully",
                        "user": user.to_dict()}), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Email already exists"}), 409
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@users_bp.route("/<int:user_id>", methods=["PUT"])
def update_user(user_id):
    try:
        user = db.get_or_404(User, user_id)
        data = request.get_json()
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
        return jsonify(category.to_dict())
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@categories_bp.route("", methods=["POST"])
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


@products_bp.route("", methods=["POST"])
def create_product():
    try:
        data = request.get_json()
        if not data or not data.get('category_id') or not data.get('product_name') or not data.get('sku') or not data.get('sku') or not data.get('price'):
            return jsonify({"error": "Missing required field"}), 400

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
def update_product(product_id):
    try:
        product = db.get_or_404(Product, product_id)
        data = request.get_json()
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
def delete_product(product_id):
    try:
        product = db.get_or_404(Product, product_id)
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
def get_orders():
    try:
        orders = Order.query.order_by(Order.ordered_at.desc()).all()
        return jsonify([o.to_dict() for o in orders])
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@orders_bp.route("/<int:order_id>", methods=["GET"])
def get_order(order_id):
    try:
        order = db.get_or_404(Order, order_id)
        result = order.to_dict()
        items = db.session.execute(
            order_items.select().where(order_items.c.order_id == order_id)
        ).fetchall()
        result["items"] = [
            {
                "order_item_id": row.order_item_id,
                "product_id": row.product_id,
                "quantity": row.quantity,
                "unit_price": float(row.unit_price),
                "line_total": float(row.line_total) if row.line_total else None,
            }
            for row in items
        ]
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@orders_bp.route("", methods=["POST"])
def create_order():
    try:
        data = request.get_json()
        if not data or not data.get("user_id") or not data.get("shipping_address"):
            return jsonify({"error": "Missing required field"}), 400

        order = Order(
            user_id=data["user_id"],
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
def update_order(order_id):
    try:
        order = db.get_or_404(Order, order_id)
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



# ---------- Order Items ----------
order_items_bp = Blueprint("order_items", __name__, url_prefix="/orders/<int:order_id>/items")


@order_items_bp.route("", methods=["GET"])
def get_order_items(order_id):
    try:
        db.get_or_404(Order, order_id)
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

