"""
Locust load test for RevoShop API.

Simulates a realistic sequential user journey:
  1. Register + login (on_start)
  2. GET all products
  3. GET a single product by ID
  4. POST a new order
  5. GET the created order

Run:
  1. Start the API:   flask run --debug --port 5001
  2. Start Locust:    locust
  3. Open:            http://localhost:8089
     Host:            http://127.0.0.1:5001
"""

import random

from locust import HttpUser, SequentialTaskSet, task, between


class UserJourney(SequentialTaskSet):
    """A single shopper's end-to-end flow, executed in order."""

    def on_start(self):
        """Register a unique user and log in to obtain a JWT token."""
        self.headers = {}
        self.order_id = None
        self.product_ids = [1]  # fallback until we fetch the real list

        unique_id = random.randint(100000, 999999)
        email = f"locust_{unique_id}@test.com"

        # Register (ignore duplicate errors — we only care about being able to log in)
        self.client.post("/users", json={
            "username": f"locust_user_{unique_id}",
            "full_name": f"Locust User {unique_id}",
            "email": email,
            "password": "password123",
            "role": "Customer",
        }, name="0. POST register")

        # Login
        resp = self.client.post("/auth/login", json={
            "email": email,
            "password": "password123",
        }, name="0. POST login")

        if resp.status_code == 200:
            token = resp.json().get("access_token")
            self.headers = {"Authorization": f"Bearer {token}"}

    @task
    def list_products(self):
        """Step 1: browse all products (paginated) and cache their IDs."""
        resp = self.client.get("/products", name="1. GET all products")
        if resp.status_code == 200:
            ids = [p["product_id"] for p in resp.json().get("products", [])]
            if ids:
                self.product_ids = ids

    @task
    def view_product(self):
        """Step 2: view a random product by ID."""
        product_id = random.choice(self.product_ids)
        self.client.get(f"/products/{product_id}", name="2. GET product by id")

    @task
    def create_order(self):
        """Step 3: create a new order with random product(s) and quantity."""
        if not self.headers:
            return

        # Pick 1-3 distinct random products, each with a random quantity (1-5)
        chosen = random.sample(
            self.product_ids,
            k=min(len(self.product_ids), random.randint(1, 3)),
        )
        items = [
            {"product_id": pid, "quantity": random.randint(1, 5)}
            for pid in chosen
        ]

        resp = self.client.post("/orders", headers=self.headers, json={
            "shipping_address": "Jl. Load Test No. 1, Jakarta",
            "shipping_fee": 15000,
            "items": items,
        }, name="3. POST order")

        if resp.status_code == 201:
            self.order_id = resp.json().get("order", {}).get("order_id")

    @task
    def get_created_order(self):
        """Step 4: view the created order, then restart the journey."""
        if self.headers and self.order_id:
            self.client.get(
                f"/orders/{self.order_id}",
                headers=self.headers,
                name="4. GET created order",
            )
        self.interrupt()


class WebUser(HttpUser):
    """Simulated shop user."""
    tasks = [UserJourney]
    wait_time = between(1, 3)
    host = "http://127.0.0.1:5001"
