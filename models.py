from datetime import datetime
from utils import db


class User(db.Model):
    __tablename__ = "users"

    user_id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False, server_default="Customer")
    email = db.Column(db.String(255), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    orders = db.relationship("Order", backref="user", lazy=True)

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "full_name": self.full_name,
            "role": self.role,
            "email": self.email,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Category(db.Model):
    __tablename__ = "categories"

    category_id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(80), nullable=False, unique=True)
    description = db.Column(db.String(1000))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    products = db.relationship("Product", backref="category", lazy=True)

    def to_dict(self):
        return {
            "category_id": self.category_id,
            "category_name": self.category_name,
            "description": self.description,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Product(db.Model):
    __tablename__ = "products"

    product_id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(
        db.Integer,
        db.ForeignKey("categories.category_id", ondelete="RESTRICT"),
        nullable=False,
    )
    product_name = db.Column(db.String(255), nullable=False)
    sku = db.Column(db.String(11), nullable=False, unique=True)
    description = db.Column(db.String(1000))
    price = db.Column(db.Numeric(12, 2), nullable=False)
    stock_quantity = db.Column(db.Integer, nullable=False, default=0)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (
        db.CheckConstraint("price >= 0", name="chk_product_price"),
        db.CheckConstraint("stock_quantity >= 0", name="chk_product_stock"),
    )

    def to_dict(self):
        return {
            "product_id": self.product_id,
            "category_id": self.category_id,
            "product_name": self.product_name,
            "sku": self.sku,
            "description": self.description,
            "price": float(self.price),
            "stock_quantity": self.stock_quantity,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

# ---------- Association Table (Many-to-Many: Orders <-> Products) ----------
order_items = db.Table(
    "order_items",
    db.Column("order_item_id", db.Integer, primary_key=True),
    db.Column("order_id", db.Integer, db.ForeignKey("orders.order_id", ondelete="CASCADE"), nullable=False),
    db.Column("product_id", db.Integer, db.ForeignKey("products.product_id", ondelete="RESTRICT"), nullable=False),
    db.Column("quantity", db.Integer, nullable=False),
    db.Column("unit_price", db.Numeric(12, 2), nullable=False),
    db.Column("line_total", db.Numeric(12, 2)),
    db.CheckConstraint("quantity > 0", name="chk_order_items_quantity"),
    db.CheckConstraint("unit_price >= 0", name="chk_order_items_unit_price"),
)


class Order(db.Model):
    __tablename__ = "orders"

    order_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.user_id", ondelete="RESTRICT"),
        nullable=False,
    )
    order_status = db.Column(db.String(20), nullable=False, default="Pending")
    shipping_address = db.Column(db.String(1000), nullable=False)
    shipping_fee = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    total_amount = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    ordered_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # Many-to-many relationship with Product through order_items
    products = db.relationship(
        "Product",
        secondary=order_items,
        backref=db.backref("orders", lazy=True),
        lazy=True,
    )

    __table_args__ = (
        db.CheckConstraint(
            "order_status IN ('Pending','Paid','Shipped','Delivered','Cancelled','Return Process')",
            name="chk_orders_status",
        ),
        db.CheckConstraint(
            "shipping_fee >= 0 AND total_amount >= 0", name="chk_orders_totals"
        ),
    )

    def to_dict(self):
        return {
            "order_id": self.order_id,
            "user_id": self.user_id,
            "order_status": self.order_status,
            "shipping_address": self.shipping_address,
            "shipping_fee": float(self.shipping_fee),
            "total_amount": float(self.total_amount),
            "ordered_at": self.ordered_at.isoformat() if self.ordered_at else None,
        }
