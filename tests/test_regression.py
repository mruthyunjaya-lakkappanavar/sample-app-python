"""
Regression tests — comprehensive test suite covering all CRUD operations,
edge cases, validation, and data integrity.

These run in PARALLEL with sanity and performance tests,
and use a version MATRIX (Python 3.11, 3.12, 3.13) to verify compatibility.

Marked with pytest marker 'regression' for selective execution:
    pytest -m regression tests/test_regression.py
"""

import pytest

pytestmark = pytest.mark.regression


class TestItemCreate:
    """Full test coverage for item creation."""

    def test_create_item_with_all_fields(self, client):
        """Create item with name, description, and price."""
        response = client.post(
            "/api/items",
            json={"name": "Widget", "description": "A fine widget", "price": 29.99},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Widget"
        assert data["description"] == "A fine widget"
        assert data["price"] == 29.99
        assert "id" in data
        assert "created_at" in data

    def test_create_item_minimal(self, client):
        """Create item with only required field (name)."""
        response = client.post("/api/items", json={"name": "Minimal"})
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Minimal"
        assert data["price"] == 0.0
        assert data["description"] is None

    def test_create_multiple_items(self, client):
        """Create multiple items and verify they all persist."""
        items = [
            {"name": f"Item {i}", "price": float(i * 10)} for i in range(5)
        ]
        for item in items:
            response = client.post("/api/items", json=item)
            assert response.status_code == 201

        # Verify all exist
        response = client.get("/api/items")
        assert len(response.json()) == 5

    def test_create_item_missing_name_returns_422(self, client):
        """Creating item without name should fail validation."""
        response = client.post("/api/items", json={"price": 10.0})
        assert response.status_code == 422

    def test_create_item_with_special_characters(self, client):
        """Item names with special characters should work."""
        response = client.post(
            "/api/items",
            json={"name": "Ñoño's Wïdget™ — #1!", "price": 0.01},
        )
        assert response.status_code == 201
        assert response.json()["name"] == "Ñoño's Wïdget™ — #1!"


class TestItemRead:
    """Full test coverage for reading items."""

    def test_get_item_by_id(self, client):
        """Get specific item by its ID."""
        create_res = client.post("/api/items", json={"name": "Findable", "price": 5.0})
        item_id = create_res.json()["id"]

        response = client.get(f"/api/items/{item_id}")
        assert response.status_code == 200
        assert response.json()["name"] == "Findable"

    def test_list_items_empty(self, client):
        """Empty database should return empty list."""
        response = client.get("/api/items")
        assert response.status_code == 200
        assert response.json() == []

    def test_list_items_pagination_skip(self, client):
        """Skip parameter should offset results."""
        for i in range(10):
            client.post("/api/items", json={"name": f"Item {i}"})

        response = client.get("/api/items?skip=5")
        assert response.status_code == 200
        assert len(response.json()) == 5

    def test_list_items_pagination_limit(self, client):
        """Limit parameter should cap results."""
        for i in range(10):
            client.post("/api/items", json={"name": f"Item {i}"})

        response = client.get("/api/items?limit=3")
        assert response.status_code == 200
        assert len(response.json()) == 3

    def test_list_items_pagination_combined(self, client):
        """Skip + limit should work together."""
        for i in range(10):
            client.post("/api/items", json={"name": f"Item {i}"})

        response = client.get("/api/items?skip=8&limit=5")
        assert response.status_code == 200
        assert len(response.json()) == 2  # Only 2 remaining after skip 8

    def test_get_nonexistent_item(self, client):
        """Getting a nonexistent item should return 404."""
        response = client.get("/api/items/99999")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


class TestItemUpdate:
    """Full test coverage for updating items."""

    def test_update_item_name(self, client):
        """Update only the name field."""
        create_res = client.post("/api/items", json={"name": "Old Name", "price": 10.0})
        item_id = create_res.json()["id"]

        response = client.put(f"/api/items/{item_id}", json={"name": "New Name"})
        assert response.status_code == 200
        assert response.json()["name"] == "New Name"
        assert response.json()["price"] == 10.0  # Unchanged

    def test_update_item_price(self, client):
        """Update only the price field."""
        create_res = client.post("/api/items", json={"name": "Pricey", "price": 10.0})
        item_id = create_res.json()["id"]

        response = client.put(f"/api/items/{item_id}", json={"price": 99.99})
        assert response.status_code == 200
        assert response.json()["price"] == 99.99
        assert response.json()["name"] == "Pricey"  # Unchanged

    def test_update_item_description(self, client):
        """Update the description field."""
        create_res = client.post("/api/items", json={"name": "Described"})
        item_id = create_res.json()["id"]

        response = client.put(
            f"/api/items/{item_id}",
            json={"description": "Now with a description!"},
        )
        assert response.status_code == 200
        assert response.json()["description"] == "Now with a description!"

    def test_update_all_fields(self, client):
        """Update all fields at once."""
        create_res = client.post(
            "/api/items",
            json={"name": "Original", "description": "Old desc", "price": 1.0},
        )
        item_id = create_res.json()["id"]

        response = client.put(
            f"/api/items/{item_id}",
            json={"name": "Updated", "description": "New desc", "price": 99.0},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated"
        assert data["description"] == "New desc"
        assert data["price"] == 99.0

    def test_update_nonexistent_item(self, client):
        """Updating a nonexistent item should return 404."""
        response = client.put("/api/items/99999", json={"name": "Ghost"})
        assert response.status_code == 404


class TestItemDelete:
    """Full test coverage for deleting items."""

    def test_delete_item(self, client):
        """Delete an item and verify it's gone."""
        create_res = client.post("/api/items", json={"name": "Deletable"})
        item_id = create_res.json()["id"]

        delete_res = client.delete(f"/api/items/{item_id}")
        assert delete_res.status_code == 204

        # Verify deleted
        get_res = client.get(f"/api/items/{item_id}")
        assert get_res.status_code == 404

    def test_delete_nonexistent_item(self, client):
        """Deleting a nonexistent item should return 404."""
        response = client.delete("/api/items/99999")
        assert response.status_code == 404

    def test_delete_does_not_affect_others(self, client):
        """Deleting one item should not affect other items."""
        client.post("/api/items", json={"name": "Keep"})
        res2 = client.post("/api/items", json={"name": "Delete"})

        client.delete(f"/api/items/{res2.json()['id']}")

        remaining = client.get("/api/items").json()
        assert len(remaining) == 1
        assert remaining[0]["name"] == "Keep"


class TestDataIntegrity:
    """Tests verifying data consistency and edge cases."""

    def test_item_ids_are_unique(self, client):
        """Each created item should have a unique ID."""
        ids = set()
        for i in range(10):
            res = client.post("/api/items", json={"name": f"Item {i}"})
            ids.add(res.json()["id"])
        assert len(ids) == 10

    def test_item_timestamps_exist(self, client):
        """Created items should have timestamp fields."""
        res = client.post("/api/items", json={"name": "Timestamped"})
        data = res.json()
        assert data["created_at"] is not None
        assert data["updated_at"] is not None

    def test_zero_price_allowed(self, client):
        """Items with zero price should be allowed."""
        res = client.post("/api/items", json={"name": "Free", "price": 0.0})
        assert res.status_code == 201
        assert res.json()["price"] == 0.0

    def test_float_price_precision(self, client):
        """Floating point prices should maintain precision."""
        res = client.post("/api/items", json={"name": "Precise", "price": 19.99})
        assert res.status_code == 201
        assert abs(res.json()["price"] - 19.99) < 0.01


class TestOriginalEndpoints:
    """Ensure original endpoints still work after DB changes (backward compat)."""

    def test_health_endpoint(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"

    def test_greet_endpoint(self, client):
        response = client.get("/api/greet?name=Regression")
        assert response.status_code == 200
        assert response.json()["message"] == "Hello, Regression!"

    def test_greet_default(self, client):
        response = client.get("/api/greet")
        assert response.json()["message"] == "Hello, World!"

    def test_health_json_content_type(self, client):
        response = client.get("/health")
        assert "application/json" in response.headers["content-type"]
