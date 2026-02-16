"""
Sanity (smoke) tests — quick checks that the app is alive and core endpoints work.

These run FIRST in the CI pipeline, providing fast feedback.
If sanity fails, regression and performance tests don't need to run.

Marked with pytest marker 'sanity' for selective execution:
    pytest -m sanity tests/test_sanity.py
"""

import pytest

pytestmark = pytest.mark.sanity


class TestSanityHealth:
    """Verify the application starts and responds to health checks."""

    def test_health_endpoint_returns_200(self, client):
        """App should respond with 200 OK on /health."""
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_returns_ok_status(self, client):
        """Health response should contain status: ok."""
        data = client.get("/health").json()
        assert data["status"] == "ok"

    def test_health_includes_version(self, client):
        """Health response should include a version string."""
        data = client.get("/health").json()
        assert "version" in data
        assert isinstance(data["version"], str)


class TestSanityGreet:
    """Verify the greeting endpoint works."""

    def test_greet_default(self, client):
        """Greet without name should return 'Hello, World!'."""
        response = client.get("/api/greet")
        assert response.status_code == 200
        assert response.json()["message"] == "Hello, World!"

    def test_greet_with_name(self, client):
        """Greet with name should personalize the message."""
        response = client.get("/api/greet?name=Sanity")
        assert response.status_code == 200
        assert response.json()["message"] == "Hello, Sanity!"


class TestSanityItems:
    """Verify CRUD endpoints are reachable (basic smoke test)."""

    def test_items_list_returns_200(self, client):
        """GET /api/items should return 200 with empty list initially."""
        response = client.get("/api/items")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_create_item_returns_201(self, client):
        """POST /api/items should create an item and return 201."""
        response = client.post(
            "/api/items",
            json={"name": "Smoke Test Item", "price": 9.99},
        )
        assert response.status_code == 201
        assert response.json()["name"] == "Smoke Test Item"

    def test_get_nonexistent_item_returns_404(self, client):
        """GET /api/items/999 should return 404 for missing items."""
        response = client.get("/api/items/999")
        assert response.status_code == 404
