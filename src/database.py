"""
Database module — SQLAlchemy models and connection management.

Uses SQLite for local development and PostgreSQL in CI (via service containers).
The DATABASE_URL environment variable controls which database is used.
"""

import os
from datetime import datetime, timezone
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./app.db")

# Handle PostgreSQL URL scheme (SQLAlchemy requires postgresql://)
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    echo=os.environ.get("SQL_ECHO", "").lower() == "true",
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class Item(Base):
    """A simple item model for CRUD operations."""

    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(String(1024), nullable=True)
    price = Column(Float, nullable=False, default=0.0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "price": self.price,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


def init_db():
    """Create all tables. Safe to call multiple times."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Dependency for FastAPI — yields a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
