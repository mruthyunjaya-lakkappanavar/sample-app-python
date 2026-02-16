"""
Performance tests — verify response times and throughput under load.

These run in PARALLEL with sanity and regression tests.
They test that the application can handle concurrent requests
and responds within acceptable time bounds.

Marked with pytest marker 'performance' for selective execution:
    pytest -m performance tests/test_performance.py
"""

import time
import concurrent.futures
import pytest

pytestmark = pytest.mark.performance

# Performance thresholds (in seconds)
HEALTH_RESPONSE_TIME_LIMIT = 0.5
CRUD_RESPONSE_TIME_LIMIT = 1.0
CONCURRENT_RPS_MINIMUM = 10  # At least 10 requests/second


class TestResponseTimes:
    """Verify individual endpoint response times are acceptable."""

    def test_health_response_time(self, client):
        """Health endpoint should respond within 500ms."""
        start = time.monotonic()
        response = client.get("/health")
        elapsed = time.monotonic() - start

        assert response.status_code == 200
        assert elapsed < HEALTH_RESPONSE_TIME_LIMIT, \
            f"Health responded in {elapsed:.3f}s (limit: {HEALTH_RESPONSE_TIME_LIMIT}s)"

    def test_greet_response_time(self, client):
        """Greet endpoint should respond within 500ms."""
        start = time.monotonic()
        response = client.get("/api/greet?name=Perf")
        elapsed = time.monotonic() - start

        assert response.status_code == 200
        assert elapsed < HEALTH_RESPONSE_TIME_LIMIT

    def test_create_item_response_time(self, client):
        """Creating an item should complete within 1s."""
        start = time.monotonic()
        response = client.post("/api/items", json={"name": "Perf Item", "price": 1.0})
        elapsed = time.monotonic() - start

        assert response.status_code == 201
        assert elapsed < CRUD_RESPONSE_TIME_LIMIT, \
            f"Create responded in {elapsed:.3f}s (limit: {CRUD_RESPONSE_TIME_LIMIT}s)"

    def test_list_items_response_time(self, client):
        """Listing items should complete within 1s even with data."""
        # Create some items first
        for i in range(20):
            client.post("/api/items", json={"name": f"Item {i}", "price": float(i)})

        start = time.monotonic()
        response = client.get("/api/items")
        elapsed = time.monotonic() - start

        assert response.status_code == 200
        assert len(response.json()) == 20
        assert elapsed < CRUD_RESPONSE_TIME_LIMIT


class TestThroughput:
    """Verify the application handles concurrent load."""

    def test_sequential_health_throughput(self, client):
        """Sequential health checks should maintain acceptable throughput."""
        num_requests = 50
        start = time.monotonic()

        for _ in range(num_requests):
            response = client.get("/health")
            assert response.status_code == 200

        elapsed = time.monotonic() - start
        rps = num_requests / elapsed

        assert rps >= CONCURRENT_RPS_MINIMUM, \
            f"Throughput {rps:.1f} req/s below minimum {CONCURRENT_RPS_MINIMUM} req/s"

    def test_sequential_crud_throughput(self, client):
        """CRUD operations should maintain acceptable throughput."""
        num_operations = 20
        start = time.monotonic()

        for i in range(num_operations):
            # Create
            res = client.post("/api/items", json={"name": f"Throughput {i}", "price": float(i)})
            assert res.status_code == 201
            item_id = res.json()["id"]

            # Read
            res = client.get(f"/api/items/{item_id}")
            assert res.status_code == 200

        elapsed = time.monotonic() - start
        total_ops = num_operations * 2  # create + read
        ops_per_sec = total_ops / elapsed

        assert ops_per_sec >= CONCURRENT_RPS_MINIMUM, \
            f"CRUD throughput {ops_per_sec:.1f} ops/s below minimum"


class TestStress:
    """Basic stress tests to check for resource leaks or crashes."""

    def test_rapid_create_delete_cycle(self, client):
        """Rapidly creating and deleting items should not cause errors."""
        for i in range(30):
            res = client.post("/api/items", json={"name": f"Stress {i}"})
            assert res.status_code == 201
            item_id = res.json()["id"]

            res = client.delete(f"/api/items/{item_id}")
            assert res.status_code == 204

        # Database should be clean
        items = client.get("/api/items").json()
        assert len(items) == 0

    def test_large_payload(self, client):
        """Large description should be handled without error."""
        long_desc = "A" * 1000
        res = client.post(
            "/api/items",
            json={"name": "Large", "description": long_desc, "price": 1.0},
        )
        assert res.status_code == 201
        assert len(res.json()["description"]) == 1000

    def test_pagination_under_load(self, client):
        """Pagination should work correctly with many items."""
        # Create 50 items
        for i in range(50):
            client.post("/api/items", json={"name": f"Page {i}", "price": float(i)})

        # Page through all items
        all_items = []
        skip = 0
        limit = 10
        while True:
            res = client.get(f"/api/items?skip={skip}&limit={limit}")
            assert res.status_code == 200
            batch = res.json()
            if not batch:
                break
            all_items.extend(batch)
            skip += limit

        assert len(all_items) == 50
