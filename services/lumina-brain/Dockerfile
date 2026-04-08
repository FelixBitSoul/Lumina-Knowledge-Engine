# syntax=docker/dockerfile:1.4
# Lumina Brain API Dockerfile
# Python FastAPI service for vector embedding and semantic search

FROM python:3.11-slim as builder

WORKDIR /app

# 替换为 Debian 12 (bookworm) 的国内镜像源（以阿里源为例）
RUN sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list.d/debian.sources && \
    sed -i 's/security.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list.d/debian.sources

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 设置 pip 全局镜像源
ENV PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple

# 之后所有的 pip install 都会默认使用清华源
RUN pip install uv

# Set UV cache directory
ENV UV_CACHE_DIR=/app/.uv-cache

# Copy dependency files first to leverage layer cache
COPY pyproject.toml uv.lock ./

# Install dependencies with cache mount
RUN --mount=type=cache,id=uv-cache,target=/app/.uv-cache \
    uv sync --frozen

# Production stage
FROM python:3.11-slim

WORKDIR /app

# 替换为 Debian 12 (bookworm) 的国内镜像源（以阿里源为例）
RUN sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list.d/debian.sources && \
    sed -i 's/security.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list.d/debian.sources

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy venv from builder
COPY --from=builder /app/.venv /app/.venv

# Make sure scripts in venv are usable
ENV PATH=/app/.venv/bin:$PATH
# Set Python path to include the project directory
ENV PYTHONPATH=/app/src
# Set HF_ENDPOINT environment variable
ENV HF_ENDPOINT="https://hf-mirror.com"

# Create directories
RUN mkdir -p /app/models /app/logs

# Copy application code
COPY src ./src
COPY .env .

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["python", "-m", "lumina_brain.main"]
