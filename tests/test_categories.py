"""
Test cases for Category CRUD endpoints.
Covers happy path and error cases for GET all, GET by ID, POST, PUT, DELETE.
"""
import pytest


# ---------- Helper ----------

def get_admin_token(client):
    """Create an admin user and return a valid JWT token."""
    client.post("/users", json={
        "username": "test_admin",
        "full_name": "Test Admin",
        "email": "admin@test.com",
        "password": "password123",
        "role": "Admin",
    })
    resp = client.post("/auth/login", json={
        "email": "admin@test.com",
        "password": "password123",
    })
    return resp.get_json()["access_token"]


def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


# ---------- GET /categories (list) ----------

class TestGetCategories:

    def test_get_categories_empty(self, client):
        """Happy path: returns empty list when no categories exist."""
        resp = client.get("/categories")
        assert resp.status_code == 200
        assert isinstance(resp.get_json(), list)

    def test_get_categories_with_data(self, client):
        """Happy path: returns list of categories after creating one."""
        token = get_admin_token(client)
        client.post("/categories", json={
            "category_name": "Electronics",
            "description": "Gadgets and devices",
        }, headers=auth_headers(token))

        resp = client.get("/categories")
        data = resp.get_json()
        assert resp.status_code == 200
        assert len(data) == 1
        assert data[0]["category_name"] == "Electronics"

    def test_get_categories_excludes_deleted(self, client):
        """Soft-deleted categories should not appear in list."""
        token = get_admin_token(client)
        client.post("/categories", json={
            "category_name": "ToDelete",
            "description": "Will be deleted",
        }, headers=auth_headers(token))
        client.delete("/categories/1", headers=auth_headers(token))

        resp = client.get("/categories")
        assert resp.status_code == 200
        assert len(resp.get_json()) == 0


# ---------- GET /categories/<id> ----------

class TestGetCategoryById:

    def test_get_category_found(self, client):
        """Happy path: returns category with products list."""
        token = get_admin_token(client)
        client.post("/categories", json={
            "category_name": "Books",
            "description": "Reading materials",
        }, headers=auth_headers(token))

        resp = client.get("/categories/1")
        data = resp.get_json()
        assert resp.status_code == 200
        assert data["category_name"] == "Books"
        assert "products" in data

    def test_get_category_not_found(self, client):
        """Error case: returns 404 for non-existent category."""
        resp = client.get("/categories/999")
        assert resp.status_code == 404
        assert "not found" in resp.get_json()["error"].lower()

    def test_get_category_deleted_returns_404(self, client):
        """Error case: soft-deleted category returns 404."""
        token = get_admin_token(client)
        client.post("/categories", json={
            "category_name": "Deleted",
            "description": "Gone",
        }, headers=auth_headers(token))
        client.delete("/categories/1", headers=auth_headers(token))

        resp = client.get("/categories/1")
        assert resp.status_code == 404


# ---------- POST /categories ----------

class TestCreateCategory:

    def test_create_category_success(self, client):
        """Happy path: creates category and returns 201."""
        token = get_admin_token(client)
        resp = client.post("/categories", json={
            "category_name": "Fashion",
            "description": "Clothing and accessories",
        }, headers=auth_headers(token))

        data = resp.get_json()
        assert resp.status_code == 201
        assert data["category_name"] == "Fashion"
        assert data["description"] == "Clothing and accessories"
        assert "category_id" in data

    def test_create_category_missing_name(self, client):
        """Error case: missing category_name returns 400."""
        token = get_admin_token(client)
        resp = client.post("/categories", json={
            "description": "No name provided",
        }, headers=auth_headers(token))

        assert resp.status_code == 400
        assert "errors" in resp.get_json()

    def test_create_category_missing_description(self, client):
        """Error case: missing description returns 400."""
        token = get_admin_token(client)
        resp = client.post("/categories", json={
            "category_name": "Sports",
        }, headers=auth_headers(token))

        assert resp.status_code == 400
        assert "errors" in resp.get_json()

    def test_create_category_empty_name(self, client):
        """Error case: empty category_name returns 400."""
        token = get_admin_token(client)
        resp = client.post("/categories", json={
            "category_name": "",
            "description": "Valid description",
        }, headers=auth_headers(token))

        assert resp.status_code == 400

    def test_create_category_no_body(self, client):
        """Error case: no request body returns 400."""
        token = get_admin_token(client)
        resp = client.post("/categories",
                          headers=auth_headers(token),
                          content_type="application/json")

        assert resp.status_code == 400
        assert "error" in resp.get_json()

    def test_create_category_duplicate_name(self, client):
        """Error case: duplicate category_name returns 409."""
        token = get_admin_token(client)
        client.post("/categories", json={
            "category_name": "Unique",
            "description": "First",
        }, headers=auth_headers(token))

        resp = client.post("/categories", json={
            "category_name": "Unique",
            "description": "Duplicate",
        }, headers=auth_headers(token))

        assert resp.status_code == 409
        assert "error" in resp.get_json()

    def test_create_category_requires_admin(self, client):
        """Error case: non-admin user gets 403."""
        # Create a customer user
        client.post("/users", json={
            "username": "customer",
            "full_name": "Customer User",
            "email": "cust@test.com",
            "password": "password123",
            "role": "Customer",
        })
        resp = client.post("/auth/login", json={
            "email": "cust@test.com",
            "password": "password123",
        })
        cust_token = resp.get_json()["access_token"]

        resp = client.post("/categories", json={
            "category_name": "Blocked",
            "description": "Should fail",
        }, headers=auth_headers(cust_token))

        assert resp.status_code == 403


# ---------- PUT /categories/<id> ----------

class TestUpdateCategory:

    def test_update_category_success(self, client):
        """Happy path: updates category and returns 200."""
        token = get_admin_token(client)
        client.post("/categories", json={
            "category_name": "Old Name",
            "description": "Old description",
        }, headers=auth_headers(token))

        resp = client.put("/categories/1", json={
            "category_name": "New Name",
        }, headers=auth_headers(token))

        data = resp.get_json()
        assert resp.status_code == 200
        assert data["category"]["category_name"] == "New Name"

    def test_update_category_partial(self, client):
        """Happy path: partial update only changes provided fields."""
        token = get_admin_token(client)
        client.post("/categories", json={
            "category_name": "Original",
            "description": "Keep this",
        }, headers=auth_headers(token))

        resp = client.put("/categories/1", json={
            "description": "Updated description",
        }, headers=auth_headers(token))

        data = resp.get_json()
        assert resp.status_code == 200
        assert data["category"]["category_name"] == "Original"
        assert data["category"]["description"] == "Updated description"

    def test_update_category_not_found(self, client):
        """Error case: returns 404 for non-existent category."""
        token = get_admin_token(client)
        resp = client.put("/categories/999", json={
            "category_name": "Ghost",
        }, headers=auth_headers(token))

        assert resp.status_code == 404

    def test_update_category_empty_name(self, client):
        """Error case: empty name returns 400."""
        token = get_admin_token(client)
        client.post("/categories", json={
            "category_name": "Valid",
            "description": "Valid",
        }, headers=auth_headers(token))

        resp = client.put("/categories/1", json={
            "category_name": "",
        }, headers=auth_headers(token))

        assert resp.status_code == 400

    def test_update_category_no_body(self, client):
        """Error case: no request body returns 400."""
        token = get_admin_token(client)
        client.post("/categories", json={
            "category_name": "Test",
            "description": "Test",
        }, headers=auth_headers(token))

        resp = client.put("/categories/1",
                         headers=auth_headers(token),
                         content_type="application/json")

        assert resp.status_code == 400


# ---------- DELETE /categories/<id> ----------

class TestDeleteCategory:

    def test_delete_category_success(self, client):
        """Happy path: soft deletes category and returns 200."""
        token = get_admin_token(client)
        client.post("/categories", json={
            "category_name": "Removable",
            "description": "Can be deleted",
        }, headers=auth_headers(token))

        resp = client.delete("/categories/1", headers=auth_headers(token))
        assert resp.status_code == 200
        assert resp.get_json()["message"] == "Category deleted"

        # Verify it's gone from GET
        resp = client.get("/categories/1")
        assert resp.status_code == 404

    def test_delete_category_not_found(self, client):
        """Error case: returns 404 for non-existent category."""
        token = get_admin_token(client)
        resp = client.delete("/categories/999", headers=auth_headers(token))
        assert resp.status_code == 404

    def test_delete_category_requires_admin(self, client):
        """Error case: non-admin user gets 403."""
        # Create admin and category first
        token = get_admin_token(client)
        client.post("/categories", json={
            "category_name": "Protected",
            "description": "Admin only",
        }, headers=auth_headers(token))

        # Create customer
        client.post("/users", json={
            "username": "cust2",
            "full_name": "Customer",
            "email": "cust2@test.com",
            "password": "password123",
            "role": "Customer",
        })
        resp = client.post("/auth/login", json={
            "email": "cust2@test.com",
            "password": "password123",
        })
        cust_token = resp.get_json()["access_token"]

        resp = client.delete("/categories/1", headers=auth_headers(cust_token))
        assert resp.status_code == 403
