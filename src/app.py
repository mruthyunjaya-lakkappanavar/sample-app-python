"""Simple FastAPI application demonstrating shared CI/CD workflows."""

import os
from fastapi import FastAPI, Query

app = FastAPI(title="sample-app-python", version=os.environ.get("APP_VERSION", "0.1.0"))

VERSION = os.environ.get("APP_VERSION", "0.1.0")


@app.get("/health")
def health():
    """Health check endpoint."""
    return {"status": "ok", "version": VERSION}


@app.get("/api/greet")
def greet(name: str = Query(default="World")):
    """Greeting endpoint."""
    return {"message": f"Hello, {name}!"}


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
