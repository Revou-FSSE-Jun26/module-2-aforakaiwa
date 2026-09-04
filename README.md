# RevoShop API

A RESTful e-commerce backend API built with Flask and PostgreSQL. RevoShop is an online store API that manages users, products, categories, orders, and order items through a RESTful interface backed by PostgreSQL. It provides a complete product catalog, user management, and order processing system with role-based access control, JWT authentication, and data validation.

## Live Deployment

- **API base URL:** https://revoushop-afo.onrender.com
- **Swagger UI:** https://revoushop-afo.onrender.com/apidocs/
- **Hosted on:** Render (web service + managed PostgreSQL)

## Features

- **Full CRUD** for products, categories, orders, and users
- **Many-to-many relationship** between orders and products through the `order_items` association table
- **Role-based access control (RBAC)** — Admin-only endpoints for managing categories and products
- **JWT Authentication** with access token + refresh token
- **Data validation** using Marshmallow schemas (type checking, length limits, range validation)
- **Error handling** with try/except blocks returning consistent JSON error responses
- **Soft delete** — records are marked with `deleted_at` timestamp instead of permanently removed
- **Deletion guard** — blocks removing a product that still has active orders (Pending, Paid, Shipped, Return Process)
- **Pagination** on GET /products (5 items per page by default)
- **Swagger UI** documentation at `/apidocs`
- **MC+S architecture** — Model + Controller + Service pattern for clean separation of concerns

## Technologies Used

| Technology | Purpose |
|-----------|---------|
| Flask | Web framework |
| SQLAlchemy | ORM |
| Flask-Migrate (Alembic) | Database migrations |
| PostgreSQL | Database |
| Flask-JWT-Extended | Authentication (JWT) |
| Marshmallow | Request validation & serialization |
| Flasgger | Swagger/OpenAPI documentation |
| bcrypt | Password hashing |
| pgAdmin / DBeaver | Database management GUI |
| pytest | Testing |
| Locust | Load testing |
| python-dotenv | Environment variable management |
| gunicorn | Production WSGI server |
| Render | Deployment platform (hosted API + PostgreSQL) |

## Project Structure

```
revoushop-db/
├── app.py                  # App factory
├── config.py               # Configuration (DB URI, JWT, Swagger)
├── utils.py                # SQLAlchemy instance + naming convention
├── auth.py                 # Password hashing + roles_required decorator
├── schemas.py              # Marshmallow validation schemas
├── models/
│   ├── user.py             # User model
│   ├── category.py         # Category model
│   ├── product.py          # Product model
│   └── order.py            # Order + order_items model
├── services/
│   ├── user_service.py     # User business logic
│   ├── auth_service.py     # Login/refresh logic
│   ├── category_service.py # Category business logic
│   ├── product_service.py  # Product business logic
│   └── order_service.py    # Order business logic
├── routes/
│   ├── home_controller.py  # / and /warmup routes
│   ├── user_controller.py  # /users routes
│   ├── auth_controller.py  # /auth routes
│   ├── category_controller.py
│   ├── product_controller.py
│   └── order_controller.py # /orders and /orders/<id>/items routes
├── migrations/             # Alembic migration files
├── tests/                  # Test files
├── requirements.txt        # Production dependencies
└── requirements-dev.txt    # Dev/test dependencies (pytest, locust)
```

## How to Run Locally

### Prerequisites

- Python 3.12+
- PostgreSQL running on localhost:5432

### Setup

```bash
# 1. Clone the repository
git clone <repository-url>
cd revoushop-db

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies
# Production only:
pip install -r requirements.txt
# For development + testing (pytest, locust), use:
pip install -r requirements-dev.txt

# 4. Create .env file (copy from example)
cp .env.example .env
# Edit .env with your PostgreSQL credentials

# 5. Create the database
psql -U postgres -c "CREATE DATABASE revoushop_db;"

# 6. Run migrations
flask db upgrade

# 7. (Optional) Seed sample data
psql -U postgres -d revoushop_db -f Seed.sql

# 8. Run the application
flask run --port 5001
```

### Environment Variables (.env)

```
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/revoushop_db
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret
FLASK_DEBUG=True
```

## API Endpoints

### Public (no auth required)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Home / health check |
| GET | `/warmup` | Hardcoded sample data |
| GET | `/warmup/products` | Hardcoded product list |
| GET | `/warmup/products/<id>` | Hardcoded product by ID |
| GET | `/users` | List all users |
| GET | `/users/<id>` | Get user by ID |
| POST | `/users` | Register new user |
| GET | `/categories` | List all categories |
| GET | `/categories/<id>` | Get category with products |
| GET | `/products` | List products (paginated) |
| GET | `/products/<id>` | Get product by ID |

### Auth

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/login` | Login, get access + refresh token |
| POST | `/auth/refresh` | Refresh access token |

### Protected (JWT required)

| Method | Endpoint | Role | Description |
|--------|----------|------|-------------|
| POST | `/categories` | Admin | Create category |
| PUT | `/categories/<id>` | Admin | Update category |
| DELETE | `/categories/<id>` | Admin | Soft delete category |
| POST | `/products` | Admin | Create product |
| PUT | `/products/<id>` | Admin | Update product |
| DELETE | `/products/<id>` | Admin | Soft delete product |
| GET | `/orders` | Any | List user's orders |
| GET | `/orders/<id>` | Any | Get order with items |
| POST | `/orders` | Any | Create order |
| PUT | `/orders/<id>` | Any | Update order |
| DELETE | `/orders/<id>` | Any | Soft delete order |
| GET | `/orders/<id>/items` | Any | Get order items |

### Swagger Documentation

Visit `http://127.0.0.1:5001/apidocs/` when the server is running.

## Testing

The test suite uses an in-memory SQLite database, so PostgreSQL is not required to run the tests.

```bash
# Activate the virtual environment
source venv/bin/activate

# Run the full test suite
pytest -v

# Run a single test file
pytest tests/test_categories.py -v
```

## Screenshots

### Postman Requests

**GET — List / retrieve products**

![GET Product](docs/Postman_GET_product.png)

![GET Product by ID](docs/Postman_GET_product_2.png)

**POST — Register user, login, create category & product**

![POST User](docs/Postman_POST_user.png)

![POST Auth (Login)](docs/Postman_POST_auth.png)

![POST Category](docs/Postman_POST_Category.png)

![POST Products](docs/Postman_POST_Products.png)

**PUT — Update category & product**

![PUT Category](docs/Postman_PUT_categories.png)

![PUT Product](docs/Postman_PUT_product.png)

**DELETE — Soft delete category & product**

![DELETE Category](docs/Postman_DELETE_categories.png)

![DELETE Product](docs/Postman_DELETE_product.png)

### Live Production API Testing (Render)

Full CRUD flow tested against the deployed public URL
`https://revoushop-afo.onrender.com`, confirming the API works end to end in production.

**1. Register user (POST /users):**

![Live POST User](docs/LivePostman_POST_user.png)

**2. Login (POST /auth/login):**

![Live POST Auth](docs/LivePostman_POST_auth.png)

**3. Create category (POST /categories):**

![Live POST Category](docs/LivePostman_POST_Category.png)

**4. Create product (POST /products):**

![Live POST Products](docs/LivePostman_POST_Products.png)

**5. Fetch product (GET /products/&lt;id&gt;):**

![Live GET Product](docs/LivePostman_GET_product_1.png)

**6. Update product (PUT /products/&lt;id&gt;):**

![Live PUT Product](docs/LivePostman_PUT_product.png)

**7. Delete product (DELETE /products/&lt;id&gt;):**

![Live DELETE Product](docs/LivePostman_DELETE_product.png)

### Database Tables (DBeaver)

**Order Items Association Table:**

![Order Items](docs/order_items%20association_table.png)

**Role Added to Users Table:**

![Role Column](docs/role_added_to_users_table.png)

**Flask DB Migration History:**

![Migration History](docs/full_flask_db_history.png)

### Hosted Database (Production)

Screenshot of the live PostgreSQL instance on Render showing all tables in production
(connect DBeaver to the Render External Database URL, or view via Render dashboard):

![Production Database Tables](docs/production_db_tables.png)

### Load Testing (Locust)

**50 users:**

![Locust 50 users](docs/Locust-50%20users.png)

**200 users — Statistics:**

![Locust 200 users statistics](docs/Locust-200%20users%20statistics.png)

**200 users — Charts:**

![Locust 200 users chart](docs/Locust-200%20users%20chart.png)

### Commit History

![Commit History](docs/Commit%20history.png)

### Local Demo

- [Create User Demo (video)](docs/Local%20demo-create%20user.mp4)
- [Get Products Demo (video)](docs/Local%20demo-get%20products.mp4)

## ERD (Entity Relationship Diagram)

![ERD](docs/erd.png)

## Database Schema

- **users** — user_id, username, full_name, role, email, password_hash, is_active, created_at, deleted_at
- **categories** — category_id, category_name, description, created_at, deleted_at
- **products** — product_id, category_id (FK), product_name, sku, description, price, stock_quantity, is_active, created_at, deleted_at
- **orders** — order_id, user_id (FK), order_status, shipping_address, shipping_fee, total_amount, ordered_at, deleted_at
- **order_items** — order_item_id, order_id (FK), product_id (FK), quantity, unit_price, line_total
