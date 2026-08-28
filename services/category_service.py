from datetime import datetime

from sqlalchemy.exc import IntegrityError
from utils import db
from models import Category


class CategoryService:

    @staticmethod
    def get_all():
        return Category.query.filter_by(deleted_at=None).all()

    @staticmethod
    def get_by_id(category_id):
        category = db.session.get(Category, category_id)
        if category is None or category.deleted_at is not None:
            return None
        return category

    @staticmethod
    def create(data):
        """Returns (category, None) on success or (None, error_message) on failure."""
        try:
            category = Category(
                category_name=data["category_name"],
                description=data["description"],
            )
            db.session.add(category)
            db.session.commit()
            return category, None
        except IntegrityError:
            db.session.rollback()
            return None, "Category name already exists"

    @staticmethod
    def update(category_id, data):
        """Returns (category, None) on success or (None, error_message) on failure."""
        category = CategoryService.get_by_id(category_id)
        if category is None:
            return None, "not_found"
        try:
            if "category_name" in data:
                category.category_name = data["category_name"]
            if "description" in data:
                category.description = data["description"]
            db.session.commit()
            return category, None
        except IntegrityError:
            db.session.rollback()
            return None, "Category name already exists"

    @staticmethod
    def delete(category_id):
        """Soft delete. Returns (True, None) on success or (False, error_message) on failure."""
        category = CategoryService.get_by_id(category_id)
        if category is None:
            return False, "not_found"
        category.deleted_at = datetime.utcnow()
        db.session.commit()
        return True, None
