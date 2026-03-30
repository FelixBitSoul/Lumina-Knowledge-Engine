# Docker Deployment Guide

This guide provides comprehensive instructions for deploying the Lumina Knowledge Engine using Docker containers, suitable for development, testing, and production environments.

## 🐳 Overview

Docker deployment offers:
- **Consistency**: Same environment across development and production
- **Isolation**: Services isolated in separate containers
- **Portability**: Easy deployment across different platforms
- **Scalability**: Simple horizontal scaling with container orchestration

## 📋 Prerequisites

### System Requirements
- **Docker**: 20.10+ with Docker Compose 2.0+
- **RAM**: Minimum 4GB, Recommended 8GB+
- **Storage**: Minimum 20GB, Recommended 50GB+
- **OS**: Linux, macOS, or Windows with WSL2

### Docker Installation
```bash
# Verify Docker installation
docker --version
docker-compose --version

# Test Docker functionality
docker run hello-world
```

## 🚀 Quick Start

### Option 1: Using Docker Compose (Recommended)
```bash
# Clone repository
git clone https://github.com/FelixBitSoul/lumina-knowledge-engine.git
cd lumina-knowledge-engine

# Navigate to deployments directory
cd deployments

# Start all core services (Qdrant, Brain API, Portal)
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f

# Optional: Start Crawler service for content ingestion
docker-compose --profile crawler up -d
```

### Option 2: Individual Containers
```bash
# Start Qdrant
docker run -d --name qdrant \
  -p 6333:6333 -p 6334:6334 \
  -v qdrant_data:/qdrant/storage \
  qdrant/qdrant:v1.7.4

# Start Brain API (build from source)
cd services/lumina-brain
docker build -t lumina/brain-api:latest .
docker run -d --name brain-api \
  -p 8000:8000 \
  --link qdrant:qdrant \
  -e QDRANT_HOST=qdrant \
  -e QDRANT_PORT=6333 \
  lumina/brain-api:latest

# Start Portal (build from source)
cd services/portal-next
docker build -t lumina/portal:latest .
docker run -d --name portal \
  -p 3000:3000 \
  --link brain-api:brain-api \
  -e NEXT_PUBLIC_API_URL=http://localhost:8000 \
  lumina/portal:latest
```

## 📁 Docker Compose Configuration

### Complete docker-compose.yaml
```yaml
version: '3.8'

services:
  # Vector Database
  qdrant:
    image: qdrant/qdrant:v1.7.4
    container_name: lumina-qdrant
    restart: unless-stopped
    ports:
      - "6333:6333"  # REST API
      - "6334:6334"  # gRPC API
    volumes:
      - qdrant_data:/qdrant/storage
      - ./deployments/qdrant/config.yaml:/qdrant/config/production.yaml:ro
    environment:
      - QDRANT__SERVICE__HTTP_PORT=6333
      - QDRANT__SERVICE__GRPC_PORT=6334
    networks:
      - lumina-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:6333/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Brain API Service
  brain-api:
    build:
      context: ./services/lumina-brain
      dockerfile: Dockerfile
    container_name: lumina-brain-api
    restart: unless-stopped
    ports:
      - "8000:8000"
    environment:
      - QDRANT_HOST=qdrant
      - QDRANT_PORT=6333
      - QDRANT_COLLECTION=knowledge_base
      - MODEL_NAME=all-MiniLM-L6-v2
      - LOG_LEVEL=info
    volumes:
      - ./services/lumina-brain/models:/app/models:ro
      - brain_models:/app/models_cache  # Persistent model cache
    networks:
      - lumina-network
    depends_on:
      qdrant:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Portal Frontend
  portal:
    build:
      context: ./services/portal-next
      dockerfile: Dockerfile
      args:
        - NEXT_PUBLIC_API_URL=http://localhost:8000
        - NODE_ENV=production
    container_name: lumina-portal
    restart: unless-stopped
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000
      - NODE_ENV=production
    networks:
      - lumina-network
    depends_on:
      brain-api:
        condition: service_healthy

  # Crawler Service (Optional)
  crawler:
    build:
      context: ./services/crawler-go
      dockerfile: Dockerfile
    container_name: lumina-crawler
    restart: "no"  # Manual start only
    environment:
      - BRAIN_INGEST_URL=http://brain-api:8000/ingest
      - CRAWLER_CONFIG=/app/config/crawler-config.yaml
      - LOG_LEVEL=info
    volumes:
      - ./services/crawler-go/crawler-config.yaml:/app/config/crawler-config.yaml:ro
      - ./logs:/app/logs
    networks:
      - lumina-network
    depends_on:
      brain-api:
        condition: service_healthy
    profiles:
      - crawler  # Use: docker-compose --profile crawler up -d

  # Redis Cache (Optional)
  redis:
    image: redis:7-alpine
    container_name: lumina-redis
    restart: unless-stopped
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    networks:
      - lumina-network
    command: redis-server --appendonly yes

volumes:
  qdrant_data:
    driver: local
  brain_models:  # Model cache for Brain API
    driver: local
  redis_data:
    driver: local

networks:
  lumina-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16
```

## 🔧 Dockerfiles

### Brain API Dockerfile
```dockerfile
# services/lumina-brain/Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create non-root user
RUN useradd --create-home --shell /bin/bash app
USER app

# Copy application code
COPY . .

# Create models directory
RUN mkdir -p models

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose port
EXPOSE 8000

# Start application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Portal Dockerfile
```dockerfile
# services/portal-next/Dockerfile
FROM node:18-alpine AS base

# Install dependencies only when needed
FROM base AS deps
WORKDIR /app

# Copy package files
COPY package*.json ./
RUN npm ci --omit=dev

# Rebuild the source code only when needed
FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .

# Build arguments
ARG NEXT_PUBLIC_API_URL
ARG NODE_ENV=production

ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL
ENV NODE_ENV=$NODE_ENV

# Build application
RUN npm run build

# Production image, copy all the files and run next
FROM base AS runner
WORKDIR /app

ENV NODE_ENV=production

# Create non-root user
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

# Copy built application
COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:3000 || exit 1

EXPOSE 3000

ENV PORT 3000

CMD ["node", "server.js"]
```

### Crawler Dockerfile
```dockerfile
# services/crawler-go/Dockerfile
FROM golang:1.22-alpine AS builder

# Install git (required for some Go modules)
RUN apk add --no-cache git

WORKDIR /app

# Copy go mod files
COPY go.mod go.sum ./
RUN go mod download

# Copy source code
COPY . .

# Build application
RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o crawler ./cmd/crawler

# Final stage
FROM alpine:latest

# Install curl for health checks
RUN apk --no-cache add ca-certificates curl

WORKDIR /root/

# Copy binary from builder
COPY --from=builder /app/crawler .

# Copy configuration
COPY crawler-config.yaml ./
COPY .env.example ./.env.example

# Create logs directory
RUN mkdir -p logs

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD test -f ./logs/crawler.log && grep "Task.*Done" ./logs/crawler.log || exit 1

# Run crawler
CMD ["./crawler"]
```

## ⚙️ Configuration Management

### Environment Variables

Create `.env` file for each service:

**For Crawler Service:**
```bash
# services/crawler-go/.env
# Crawler Configuration
CRAWLER_CONFIG=crawler-config.yaml

# Brain API Configuration
BRAIN_INGEST_URL=http://localhost:8000/ingest

# Logging
LOG_LEVEL=info

# Environment
GO_ENV=development
```

**For Brain API Service:**
```bash
# services/lumina-brain/.env
# Vector Database
QDRANT_HOST=localhost
QDRANT_PORT=6333
QDRANT_COLLECTION=knowledge_base

# Model Configuration
MODEL_NAME=all-MiniLM-L6-v2
MODEL_CACHE_DIR=./models

# OpenAI API (for query rewriting)
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_API_BASE=https://api.deepseek.com/v1
LLM_MODEL_NAME=deepseek-chat
```

**For Portal Service:**
```bash
# services/portal-next/.env
NEXT_PUBLIC_API_URL=http://localhost:8000
NODE_ENV=development
```

### Production Configuration

#### Resource Limits
```yaml
# docker-compose.prod.yaml
version: '3.8'

services:
  brain-api:
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 2G
        reservations:
          cpus: '0.5'
          memory: 1G

  qdrant:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
        reservations:
          cpus: '1.0'
          memory: 2G
```

#### Logging Configuration
```yaml
services:
  brain-api:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  qdrant:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

## 🚀 Deployment Commands

### Development Deployment
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f brain-api

# Stop services
docker-compose down

# Rebuild and restart
docker-compose up -d --build
```

### Production Deployment
```bash
# Use production configuration
docker-compose -f docker-compose.yaml -f docker-compose.prod.yaml up -d

# Scale services
docker-compose up -d --scale brain-api=3 --scale portal=2

# Rolling update
docker-compose up -d --no-deps brain-api
```

### Maintenance Commands
```bash
# Backup data
docker run --rm -v lumina_qdrant_data:/data -v $(pwd):/backup \
  alpine tar czf /backup/qdrant-backup-$(date +%Y%m%d).tar.gz -C /data .

# Restore data
docker run --rm -v lumina_qdrant_data:/data -v $(pwd):/backup \
  alpine tar xzf /backup/qdrant-backup-20240317.tar.gz -C /data

# Clean up
docker system prune -f
docker volume prune -f
```

## 🔒 Security Configuration

### Security Best Practices

#### 1. Network Security
```yaml
# Use internal networks
networks:
  lumina-internal:
    internal: true
  lumina-external:
    driver: bridge

services:
  brain-api:
    networks:
      - lumina-internal
      - lumina-external

  qdrant:
    networks:
      - lumina-internal
    ports: []  # No external ports
```

#### 2. User Permissions
```dockerfile
# Run as non-root user
RUN adduser --disabled-password --gecos '' appuser
USER appuser
```

#### 3. Secrets Management
```bash
# Use Docker secrets
echo "your-secret-key" | docker secret create db_password -

# In docker-compose.yaml
services:
  brain-api:
    secrets:
      - db_password
secrets:
  db_password:
    external: true
```

### SSL/TLS Configuration

#### Using Traefik
```yaml
version: '3.8'

services:
  traefik:
    image: traefik:v2.10
    command:
      - "--api.insecure=true"
      - "--providers.docker=true"
      - "--entrypoints.web.address=:80"
      - "--entrypoints.websecure.address=:443"
      - "--certificatesresolvers.myresolver.acme.tlschallenge=true"
      - "--certificatesresolvers.myresolver.acme.email=admin@example.com"
      - "--certificatesresolvers.myresolver.acme.storage=/letsencrypt/acme.json"
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - "/var/run/docker.sock:/var/run/docker.sock:ro"
      - "./letsencrypt:/letsencrypt"
    networks:
      - lumina-network

  portal:
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.portal.rule=Host(`lumina.example.com`)"
      - "traefik.http.routers.portal.entrypoints=websecure"
      - "traefik.http.routers.portal.tls.certresolver=myresolver"
```

## 📊 Monitoring and Logging

### Health Checks
```yaml
services:
  brain-api:
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s
```

### Logging Configuration
```yaml
services:
  brain-api:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
        labels: "service=brain-api,environment=production"
```

### Monitoring Stack
```yaml
# docker-compose.monitoring.yaml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - "./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml"
      - prometheus_data:/prometheus

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3001:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana

volumes:
  prometheus_data:
  grafana_data:
```

## 🐛 Troubleshooting

### Common Issues

#### Container Won't Start
```bash
# Check logs
docker-compose logs <service>

# Check container status
docker-compose ps

# Inspect container
docker inspect <container_name>
```

#### Port Conflicts
```bash
# Check port usage
netstat -tulpn | grep :<port>

# Change ports in docker-compose.yaml
ports:
  - "8001:8000"  # Use different host port
```

#### Resource Issues
```bash
# Check resource usage
docker stats

# Increase memory limits
services:
  brain-api:
    deploy:
      resources:
        limits:
          memory: 4G
```

#### Network Issues
```bash
# Check network configuration
docker network ls
docker network inspect <network_name>

# Reset networks
docker-compose down
docker network prune
docker-compose up -d
```

### Debugging Commands
```bash
# Enter container
docker-compose exec brain-api sh

# View real-time logs
docker-compose logs -f --tail=100 brain-api

# Test service connectivity
docker-compose exec brain-api curl http://qdrant:6333/health

# Check environment variables
docker-compose exec brain-api env | grep QDRANT
```

## 📈 Performance Optimization

### Production Optimizations

#### 1. Multi-stage Builds
```dockerfile
# Use multi-stage builds to reduce image size
FROM golang:1.22-alpine AS builder
# ... build steps
FROM alpine:latest
COPY --from=builder /app/crawler .
```

#### 2. Resource Limits
```yaml
services:
  brain-api:
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 2G
```

#### 3. Caching
```yaml
services:
  portal:
    build:
      context: ./services/portal-next
      cache_from:
        - lumina/portal:latest
```

### Scaling Strategies
```bash
# Horizontal scaling
docker-compose up -d --scale brain-api=3

# Load balancing with nginx
upstream brain_api {
    server brain-api-1:8000;
    server brain-api-2:8000;
    server brain-api-3:8000;
}
```

---

*For cloud deployment options, see the [Cloud Deployment Guide](./cloud-deployment.md).*
