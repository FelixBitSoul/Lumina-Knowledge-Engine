# Brain API Dockerfile
# Python FastAPI service for vector embedding and semantic search

FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
# RUN curl -LsSf https://astral.sh/uv/install.sh | sh
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

COPY pyproject.toml uv.lock ./

# Install dependencies with uv using pyproject.toml (including Python version)
RUN uv sync --frozen --no-install-project

# Production stage
FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy venv from builder
COPY --from=builder /app/.venv /app/.venv

# Make sure scripts in venv are usable
ENV PATH=/app/.venv/bin:$PATH
# Set HF_ENDPOINT environment variable
ENV HF_ENDPOINT="https://hf-mirror.com"

# Create directories
RUN mkdir -p /app/models /app/logs

# Copy application code
COPY app ./app
COPY config ./config
COPY .env .

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
# CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
CMD ["python", "-m", "app.main"]
