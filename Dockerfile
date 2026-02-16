# ── Stage 1: Build ──────────────────────────────────────────────
FROM python:3.12-slim AS builder

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

COPY . .

# ── Stage 2: Runtime ───────────────────────────────────────────
FROM python:3.12-slim

LABEL org.opencontainers.image.source="https://github.com/mruthyunjaya-lakkappanavar/sample-app-python"
LABEL org.opencontainers.image.description="Sample Python FastAPI app with shared CI/CD workflows"

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy application code
COPY src/ ./src/

# Create non-root user
RUN useradd --create-home --shell /bin/bash appuser
USER appuser

EXPOSE 8000

ENV PORT=8000
ENV APP_VERSION="0.1.0"

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

CMD ["python", "-m", "uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8000"]
