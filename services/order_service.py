from datetime import datetime

from sqlalchemy.exc import IntegrityError
from utils import db
from models import Product, Order, order_items


class OrderService:

    @staticmethod
    def get_all_by_user(user_id):
        return (
            Order.query.filter_by(user_id=user_id, deleted_at=None)
            .order_by(Order.ordered_at.desc())
            .all()
        )

    @staticmethod
    def get_by_id(order_id):
        order = db.session.get(Order, order_id)
        if order is None or order.deleted_at is not None:
            return None
        return order

    @staticmethod
    def get_order_with_items(order_id):
        """Returns (order_dict_with_items, None) or (None, error_message)."""
        order = OrderService.get_by_id(order_id)
        if order is None:
            return None, "not_found"

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
        return result, None

    @staticmethod
    def create(user_id, data):
        """Returns (order, None) on success or (None, error_message) on failure."""
        try:
            order = Order(
                user_id=user_id,
                shipping_address=data["shipping_address"],
                shipping_fee=data.get("shipping_fee", 0),
            )
            db.session.add(order)
            db.session.flush()

            total = float(data.get("shipping_fee", 0))
            for item_data in data.get("items", []):
                product = db.session.get(Product, item_data["product_id"])
                if product is None:
                    db.session.rollback()
                    return None, f"Product {item_data['product_id']} not found"

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
            return order, None
        except IntegrityError:
            db.session.rollback()
            return None, "Invalid user or product reference"

    @staticmethod
    def update(order_id, data):
        """Returns (order, None) on success or (None, error_message) on failure."""
        order = OrderService.get_by_id(order_id)
        if order is None:
            return None, "not_found"

        # Block shipping address changes for shipped/delivered/cancelled orders
        if data.get("shipping_address") and order.order_status in ("Delivered", "Cancelled", "Shipped"):
            return None, "Shipping address cannot be changed for orders that are Shipped, Delivered, or Cancelled"

        try:
            if "order_status" in data:
                order.order_status = data["order_status"]
            if "shipping_address" in data:
                order.shipping_address = data["shipping_address"]
            if "shipping_fee" in data:
                old_shipping = float(order.shipping_fee)
                new_shipping = float(data["shipping_fee"])
                order.shipping_fee = new_shipping
                order.total_amount = float(order.total_amount) - old_shipping + new_shipping

            db.session.commit()
            return order, None
        except IntegrityError:
            db.session.rollback()
            return None, "Invalid order status"

    @staticmethod
    def delete(order_id):
        """Soft delete. Returns (True, None) on success or (False, error_message) on failure."""
        order = OrderService.get_by_id(order_id)
        if order is None:
            return False, "not_found"
        order.deleted_at = datetime.utcnow()
        db.session.commit()
        return True, None

    @staticmethod
    def get_items(order_id):
        """Returns list of order items."""
        items = db.session.execute(
            order_items.select().where(order_items.c.order_id == order_id)
        ).fetchall()
        return [
            {
                "order_item_id": row.order_item_id,
                "order_id": row.order_id,
                "product_id": row.product_id,
                "quantity": row.quantity,
                "unit_price": float(row.unit_price),
                "line_total": float(row.line_total) if row.line_total else None,
            }
            for row in items
        ]
