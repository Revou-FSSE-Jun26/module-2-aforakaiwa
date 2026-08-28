from datetime import datetime

from utils import db


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
    deleted_at = db.Column(db.DateTime, nullable=True, default=None)

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
            "deleted_at": self.deleted_at.isoformat() if self.deleted_at else None,
        }
