"""
Shared test fixtures for all test categories.

Provides a clean database session and test client for each test.
Uses SQLite in-memory for local tests, PostgreSQL when DATABASE_URL is set.
"""

import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.database import Base, get_db
from src.app import app


# Use in-memory SQLite for tests unless DATABASE_URL is explicitly set
TEST_DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./test.db")

if TEST_DATABASE_URL.startswith("postgres://"):
    TEST_DATABASE_URL = TEST_DATABASE_URL.replace("postgres://", "postgresql://", 1)

test_engine = create_engine(TEST_DATABASE_URL, pool_pre_ping=True)
TestSession = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(autouse=True)
def setup_database():
    """Create tables before each test, drop after."""
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def db_session():
    """Provide a clean database session for each test."""
    session = TestSession()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(db_session):
    """Create a test client with overridden DB dependency."""

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()
