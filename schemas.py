"""
schemas.py — DTO (Data Transfer Object) layer using Marshmallow.

Handles:
- Request validation (load) — checks incoming JSON has correct types and required fields
- Response serialization (dump) — converts model objects into clean JSON responses

Each resource has separate schemas for input (Create/Update) and output (Response).
"""

from marshmallow import Schema, fields, validate


# ---------- Product Schemas ----------

class ProductCreateSchema(Schema):
    """DTO for creating a product. All required fields must be present."""
    product_name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    sku = fields.Str(required=True, validate=validate.Length(min=1, max=11))
    description = fields.Str(load_default=None)
    price = fields.Float(required=True, validate=validate.Range(min=0))
    stock_quantity = fields.Int(load_default=0, strict=True, validate=validate.Range(min=0))
    is_active = fields.Bool(load_default=True)
    category_id = fields.Int(required=True)


class ProductUpdateSchema(Schema):
    """DTO for updating a product. All fields are optional — only provided fields get updated."""
    product_name = fields.Str(validate=validate.Length(min=1, max=100))
    sku = fields.Str(validate=validate.Length(min=1, max=11))
    description = fields.Str()
    price = fields.Float(validate=validate.Range(min=0))
    stock_quantity = fields.Int(strict=True, validate=validate.Range(min=0))
    is_active = fields.Bool()
    category_id = fields.Int()


class ProductResponseSchema(Schema):
    """DTO for product responses."""
    product_id = fields.Int(dump_only=True)
    category_id = fields.Int()
    product_name = fields.Str()
    sku = fields.Str()
    description = fields.Str()
    price = fields.Float()
    stock_quantity = fields.Int()
    is_active = fields.Bool()
    created_at = fields.DateTime(format="iso")


# ---------- User Schemas ----------

class UserRegisterSchema(Schema):
    """DTO for user registration."""
    username = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    full_name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=8))
    role = fields.Str(
        load_default="Customer",
        validate=validate.OneOf(["Customer", "Admin", "Seller"])
    )


class UserResponseSchema(Schema):
    """DTO for user responses. Never exposes password_hash."""
    user_id = fields.Int(dump_only=True)
    username = fields.Str()
    full_name = fields.Str()
    role = fields.Str()
    email = fields.Email()
    is_active = fields.Bool()
    created_at = fields.DateTime(format="iso")


# ---------- Auth Schemas ----------

class LoginSchema(Schema):
    """DTO for login request."""
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=1))


# ---------- Category Schemas ----------

class CategoryCreateSchema(Schema):
    """DTO for creating a category."""
    category_name = fields.Str(required=True, validate=validate.Length(min=1, max=80))
    description = fields.Str(required=True, validate=validate.Length(min=1, max=1000))


class CategoryUpdateSchema(Schema):
    """DTO for updating a category. All fields optional."""
    category_name = fields.Str(validate=validate.Length(min=1, max=80))
    description = fields.Str(validate=validate.Length(min=1, max=1000))


class CategoryResponseSchema(Schema):
    """DTO for category responses."""
    category_id = fields.Int(dump_only=True)
    category_name = fields.Str()
    description = fields.Str()
    created_at = fields.DateTime(format="iso")


# ---------- Order Schemas ----------

class OrderItemInputSchema(Schema):
    """DTO for order item in create order request."""
    product_id = fields.Int(required=True)
    quantity = fields.Int(required=True, strict=True, validate=validate.Range(min=1))


class OrderCreateSchema(Schema):
    """DTO for creating an order."""
    shipping_address = fields.Str(required=True, validate=validate.Length(min=1, max=1000))
    shipping_fee = fields.Float(load_default=0, validate=validate.Range(min=0))
    items = fields.List(fields.Nested(OrderItemInputSchema), load_default=[])


class OrderResponseSchema(Schema):
    """DTO for order responses."""
    order_id = fields.Int(dump_only=True)
    user_id = fields.Int()
    order_status = fields.Str()
    shipping_address = fields.Str()
    shipping_fee = fields.Float()
    total_amount = fields.Float()
    ordered_at = fields.DateTime(format="iso")
