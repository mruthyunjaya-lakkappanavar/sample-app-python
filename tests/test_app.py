"""Tests for the FastAPI application."""

import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)


def test_health_endpoint(client):
    """Test the health check endpoint returns OK."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data


def test_greet_with_name(client):
    """Test the greet endpoint with a name parameter."""
    response = client.get("/api/greet?name=Alice")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Hello, Alice!"


def test_greet_without_name(client):
    """Test the greet endpoint without a name defaults to World."""
    response = client.get("/api/greet")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Hello, World!"


def test_health_returns_json(client):
    """Test that health endpoint returns valid JSON content type."""
    response = client.get("/health")
    assert "application/json" in response.headers["content-type"]
