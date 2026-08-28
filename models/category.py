from datetime import datetime

from utils import db


class Category(db.Model):
    __tablename__ = "categories"

    category_id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(80), nullable=False, unique=True)
    description = db.Column(db.String(1000))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    deleted_at = db.Column(db.DateTime, nullable=True, default=None)

    products = db.relationship("Product", backref="category", lazy=True)

    def to_dict(self):
        return {
            "category_id": self.category_id,
            "category_name": self.category_name,
            "description": self.description,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "deleted_at": self.deleted_at.isoformat() if self.deleted_at else None,
        }
