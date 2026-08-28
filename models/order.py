from datetime import datetime

from utils import db


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
    deleted_at = db.Column(db.DateTime, nullable=True, default=None)

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
            "deleted_at": self.deleted_at.isoformat() if self.deleted_at else None,
        }
