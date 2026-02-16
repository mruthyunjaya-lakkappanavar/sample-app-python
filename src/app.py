"""
FastAPI application demonstrating shared CI/CD workflows.

Features:
- Health check and greeting endpoints (original)
- Database-backed CRUD for items (added for integration CI demo)
- Supports SQLite (local) and PostgreSQL (CI service containers)
"""

import os
from typing import Optional, List
from contextlib import asynccontextmanager

from fastapi import FastAPI, Query, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.database import init_db, get_db, Item

VERSION = os.environ.get("APP_VERSION", "0.1.0")


# ── Lifespan event ────────────────────────────────────────────
@asynccontextmanager
async def lifespan(application: FastAPI):
    """Initialize database tables on startup."""
    init_db()
    yield


app = FastAPI(title="sample-app-python", version=VERSION, lifespan=lifespan)


# ── Pydantic schemas ──────────────────────────────────────────
class ItemCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: float = 0.0


class ItemUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None


class ItemResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    name: str
    description: Optional[str]
    price: float
    created_at: Optional[str]
    updated_at: Optional[str]


# ── Original endpoints ────────────────────────────────────────
@app.get("/health")
def health():
    """Health check endpoint."""
    return {"status": "ok", "version": VERSION}


@app.get("/api/greet")
def greet(name: str = Query(default="World")):
    """Greeting endpoint."""
    return {"message": f"Hello, {name}!"}


# ── CRUD endpoints (database-backed) ─────────────────────────
@app.post("/api/items", response_model=ItemResponse, status_code=201)
def create_item(item: ItemCreate, db: Session = Depends(get_db)):
    """Create a new item."""
    db_item = Item(name=item.name, description=item.description, price=item.price)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item.to_dict()


@app.get("/api/items", response_model=List[ItemResponse])
def list_items(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    """List all items with pagination."""
    items = db.query(Item).offset(skip).limit(limit).all()
    return [item.to_dict() for item in items]


@app.get("/api/items/{item_id}", response_model=ItemResponse)
def get_item(item_id: int, db: Session = Depends(get_db)):
    """Get a single item by ID."""
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item.to_dict()


@app.put("/api/items/{item_id}", response_model=ItemResponse)
def update_item(item_id: int, item_update: ItemUpdate, db: Session = Depends(get_db)):
    """Update an existing item."""
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if item_update.name is not None:
        item.name = item_update.name
    if item_update.description is not None:
        item.description = item_update.description
    if item_update.price is not None:
        item.price = item_update.price
    db.commit()
    db.refresh(item)
    return item.to_dict()


@app.delete("/api/items/{item_id}", status_code=204)
def delete_item(item_id: int, db: Session = Depends(get_db)):
    """Delete an item."""
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(item)
    db.commit()
    return None


if __name__ == "__main__":  # pragma: no cover
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="127.0.0.1", port=port)
