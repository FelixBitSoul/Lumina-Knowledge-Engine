# Local Development Setup

This guide provides step-by-step instructions for setting up the Lumina Knowledge Engine in a local development environment using Docker Compose.

## 📋 Prerequisites

### System Requirements
- **Operating System**: Windows 10+, macOS 10.15+, or Linux (Ubuntu 18.04+)
- **RAM**: Minimum 4GB, Recommended 8GB+
- **Storage**: At least 10GB free space
- **Network**: Internet connection for downloading dependencies

### Required Software

#### 1. Docker & Docker Compose
Download and install Docker Desktop:
- [Windows](https://www.docker.com/products/docker-desktop/)
- [macOS](https://www.docker.com/products/docker-desktop/)
- [Linux](https://docs.docker.com/engine/install/)

Verify installation:
```bash
docker --version
docker-compose --version
```

#### 2. Git
Download and install Git:
- [Git-scm.com](https://git-scm.com/)

Verify installation:
```bash
git --version
```

## 🚀 Quick Start

### Step 1: Clone Repository
```bash
git clone https://github.com/FelixBitSoul/lumina-knowledge-engine.git
cd lumina-knowledge-engine
```

### Step 2: Configure Environment

Create a `.env` file in the `deployments` directory:

```bash
# Qdrant Configuration
QDRANT_VERSION=v1.10.0
HOST_QDRANT_REST_PORT=6333
HOST_QDRANT_GRPC_PORT=6334
QDRANT_COLLECTION=knowledge_base

# Brain API Configuration
HOST_BRAIN_API_PORT=8000
MODEL_NAME=all-MiniLM-L6-v2
MODEL_CACHE_DIR=/app/models

# Portal Configuration
HOST_PORTAL_PORT=3000

# Crawler Configuration
BRAIN_INGEST_URL=http://brain-api:8000/api/ingest

# Logging
LOG_LEVEL=info
```

### Step 3: Start All Services

```bash
cd deployments
docker-compose up -d
```

This will start all services including:
- Qdrant Vector Database
- Brain API
- Portal Frontend
- Redis
- MinIO
- Celery Worker

### Step 4: Verify Setup

Open your browser and navigate to:
- **Portal**: http://localhost:3000
- **Brain API Docs**: http://localhost:8000/docs
- **Qdrant Health**: http://localhost:6333/health
- **MinIO Console**: http://localhost:9001 (login with minioadmin:minioadmin)

### Step 5: Start Crawler (Optional)

```bash
cd deployments
docker-compose --profile crawler up -d
```

## 📁 Project Structure

```
lumina-knowledge-engine/
├── services/
│   ├── lumina-brain/       # Python FastAPI service
│   │   ├── src/            # Source code
│   │   ├── pyproject.toml  # Project configuration
│   │   └── .venv/          # Virtual environment
│   ├── crawler-go/         # Go crawler service
│   │   ├── cmd/            # Command line interface
│   │   ├── internal/       # Internal packages
│   │   ├── crawler-config.yaml     # Crawler configuration
│   │   └── go.mod          # Go dependencies
│   └── portal-next/        # Next.js frontend
│       ├── src/            # Source code
│       ├── package.json    # Node dependencies
│       └── next.config.ts  # Next.js config
├── deployments/
│   └── docker-compose.yaml # Docker services
└── docs/                   # Documentation
```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
# .env
# Vector Database
QDRANT_HOST=localhost
QDRANT_PORT=6333
QDRANT_COLLECTION=knowledge_base

# Brain API
BRAIN_API_HOST=localhost
BRAIN_API_PORT=8000

# Portal
NEXT_PUBLIC_API_URL=http://localhost:8000

# Crawler
CRAWLER_CONFIG=services/crawler-go/crawler-config.yaml
BRAIN_INGEST_URL=http://localhost:8000/ingest

# Logging
LOG_LEVEL=info
```

### Crawler Configuration

Edit `services/crawler-go/crawler-config.yaml`:

```yaml
tasks:
  - name: "local-test"
    seeds:
      - "https://docs.docker.com/get-started/"
    max_depth: 1
    allowed_domains:
      - "docs.docker.com"
    concurrency: 4
    rate_limit:
      requests_per_minute: 30
    request_timeout_seconds: 15
    user_agent: "LuminaCrawler/0.1 (Local Dev)"
    retry:
      max_attempts: 3
      backoff_seconds: 2
      retry_on_status: [429, 500, 502, 503, 504]
```

## 🔄 Development Workflow

### Daily Development Routine

1. **Start Services**:
   ```bash
   # Start all services
   cd deployments
   docker-compose up -d

   # Start services with crawler
   cd deployments
   docker-compose --profile crawler up -d
   ```

2. **Make Changes**:
   - Edit source code in the respective service directories
   - Changes will be reflected when services are restarted

3. **Restart Services** (after code changes):
   ```bash
   # Restart specific service
   cd deployments
   docker-compose restart brain-api  # Restart Brain API
   docker-compose restart portal     # Restart Portal
   docker-compose restart crawler    # Restart Crawler
   ```

4. **Test Changes**:
   - Access http://localhost:3000
   - Test search functionality
   - Check API documentation at http://localhost:8000/docs

### Code Quality

#### Linting and Formatting
```bash
# Go
cd deployments
docker-compose run --rm crawler go fmt ./...
docker-compose run --rm crawler go vet ./...

# Python
cd deployments
docker-compose run --rm brain-api flake8 src/
docker-compose run --rm brain-api black src/

# JavaScript/TypeScript
cd deployments
docker-compose run --rm portal npm run lint
docker-compose run --rm portal npm run format
```

#### Testing
```bash
# Go
cd deployments
docker-compose run --rm crawler go test ./...

# Python
cd deployments
docker-compose run --rm brain-api pytest

# JavaScript/TypeScript
cd deployments
docker-compose run --rm portal npm test
```

## 🐛 Troubleshooting

### Common Issues

#### Port Conflicts
```bash
# Check what's using ports
netstat -tulpn | grep :3000  # Portal
netstat -tulpn | grep :8000  # Brain API
netstat -tulpn | grep :6333  # Qdrant
netstat -tulpn | grep :6379  # Redis
netstat -tulpn | grep :9000  # MinIO

# Kill processes using ports
sudo kill -9 <PID>

# Alternatively, update port mappings in .env file
```

#### Docker Issues
```bash
# Reset Docker
docker system prune -a
docker-compose down -v
docker-compose up -d

# Check Docker logs
cd deployments
docker-compose logs -f
```

### Service-Specific Issues

#### Brain API Won't Start
```bash
# Check Brain API logs
cd deployments
docker-compose logs -f brain-api

# Check if dependencies are installed correctly
cd deployments
docker-compose build brain-api

# Check Brain API health
curl http://localhost:8000/health
```

#### Crawler Fails
```bash
# Check Crawler logs
cd deployments
docker-compose logs -f crawler

# Check Crawler configuration
cd deployments
docker-compose run --rm crawler cat /app/config/crawler-config.yaml

# Check Brain API connectivity
curl http://localhost:8000/health
```

#### Portal Shows Errors
```bash
# Check Portal logs
cd deployments
docker-compose logs -f portal

# Check API connectivity
curl http://localhost:8000/health

# Check browser console for errors
```

#### Qdrant Issues
```bash
# Check Qdrant logs
cd deployments
docker-compose logs -f qdrant

# Check Qdrant health
curl http://localhost:6333/health
```

## 📊 Performance Tips

### Local Development Optimization

1. **Reduce Crawler Load**:
   ```yaml
   concurrency: 2
   rate_limit:
     requests_per_minute: 10
   ```

2. **Limit Vector Collection Size**:
   ```python
   # In lumina-brain/src/lumina_brain/main.py, add cleanup
   if collection_size > 1000:
       qdrant_client.delete_collection(collection_name)
       qdrant_client.create_collection(...)
   ```

3. **Use Lightweight Models**:
   ```python
   # For testing, use smaller models
   MODEL_NAME = "all-MiniLM-L6-v2"  # Already lightweight
   ```

### Resource Monitoring

```bash
# Monitor system resources
htop          # CPU and memory
iotop         # Disk I/O
nethogs       # Network usage

# Monitor Docker resources
docker stats
docker-compose top
```

## 🧪 Testing Setup

### Unit Tests
```bash
# Run all tests using Docker Compose
cd deployments
docker-compose run --rm brain-api pytest
docker-compose run --rm crawler go test ./...
docker-compose run --rm portal npm test
```

### Integration Tests
```bash
# Test API integration
curl -X POST http://localhost:8000/api/ingest \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com", "title": "Test", "content": "Test content"}'

curl -X GET "http://localhost:8000/api/search?query=test"
```

### End-to-End Tests
```bash
# Start all services
cd deployments
docker-compose --profile crawler up -d

# Test complete workflow
# 1. Wait for services to start
# 2. Access http://localhost:3000 in browser
# 3. Test search functionality
```

## 📚 Development Resources

### Documentation
- [API Documentation](../api/)
- [Architecture Guide](../architecture/)
- [Configuration Reference](../api/crawler-config.md)

### Useful Commands
```bash
# Quick restart all services
docker-compose restart
pkill -f "python main.py"
cd services/portal-next && npm run dev

# Clean rebuild
docker-compose down -v
docker-compose up -d --build
```

### IDE Configuration

#### VS Code Extensions
- Go (golang.go)
- Python (ms-python.python)
- Docker (ms-azuretools.vscode-docker)
- ESLint (dbaeumer.vscode-eslint)

#### Configuration Files
```json
// .vscode/settings.json
{
  "go.formatTool": "goimports",
  "python.defaultInterpreterPath": "./services/lumina-brain/.venv/bin/python",
  "typescript.preferences.importModuleSpecifier": "relative"
}
```

---

*For production deployment, see the [Docker Deployment](./docker-deployment.md) and [Cloud Deployment](./cloud-deployment.md) guides.*
