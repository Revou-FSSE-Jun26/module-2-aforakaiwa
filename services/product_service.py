from datetime import datetime

from sqlalchemy.exc import IntegrityError
from utils import db
from models import Product, Order, order_items


ACTIVE_ORDER_STATUSES = ("Pending", "Paid", "Shipped", "Return Process")


class ProductService:

    @staticmethod
    def get_all(page=1, per_page=5):
        """Returns paginated products (excluding soft-deleted)."""
        return Product.query.filter_by(deleted_at=None).paginate(
            page=page, per_page=per_page, error_out=False
        )

    @staticmethod
    def get_by_id(product_id):
        product = db.session.get(Product, product_id)
        if product is None or product.deleted_at is not None:
            return None
        return product

    @staticmethod
    def create(data):
        """Returns (product, None) on success or (None, error_message) on failure."""
        try:
            product = Product(
                category_id=data["category_id"],
                product_name=data["product_name"].strip(),
                sku=data["sku"],
                description=data.get("description"),
                price=data["price"],
                stock_quantity=data.get("stock_quantity", 0),
            )
            db.session.add(product)
            db.session.commit()
            return product, None
        except IntegrityError:
            db.session.rollback()
            return None, "SKU already exists or invalid category"

    @staticmethod
    def update(product_id, data):
        """Returns (product, None) on success or (None, error_message) on failure."""
        product = ProductService.get_by_id(product_id)
        if product is None:
            return None, "not_found"
        try:
            if "product_name" in data:
                product.product_name = data["product_name"].strip()
            if "sku" in data:
                product.sku = data["sku"]
            if "description" in data:
                product.description = data["description"]
            if "price" in data:
                product.price = data["price"]
            if "stock_quantity" in data:
                product.stock_quantity = data["stock_quantity"]
            if "is_active" in data:
                product.is_active = data["is_active"]
            if "category_id" in data:
                product.category_id = data["category_id"]
            db.session.commit()
            return product, None
        except IntegrityError:
            db.session.rollback()
            return None, "SKU already exists or invalid category"

    @staticmethod
    def delete(product_id):
        """Soft delete. Returns (True, None) on success or (False, error_message) on failure."""
        product = ProductService.get_by_id(product_id)
        if product is None:
            return False, "not_found"

        # Check for active orders referencing this product
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
            return False, "Cannot delete product with active orders"

        product.deleted_at = datetime.utcnow()
        db.session.commit()
        return True, None
