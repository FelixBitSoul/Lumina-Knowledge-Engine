# Local Development Setup

This guide provides step-by-step instructions for setting up the Lumina Knowledge Engine in a local development environment.

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

#### 2. Go 1.22+
Download and install Go:
- [Official Downloads](https://golang.org/dl/)

Verify installation:
```bash
go version
# Should show: go version go1.22.x linux/amd64
```

#### 3. Python 3.11+
Download and install Python:
- [Python.org](https://www.python.org/downloads/)

Verify installation:
```bash
python --version
# Should show: Python 3.11.x
```

#### 4. Node.js 18+
Download and install Node.js:
- [Node.js.org](https://nodejs.org/)

Verify installation:
```bash
node --version
npm --version
```

#### 5. Git
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

### Step 2: Start Vector Database
```bash
# Start Qdrant vector database
docker-compose -f deployments/docker-compose.yaml up -d qdrant

# Verify Qdrant is running
curl http://localhost:6333/health
```

### Step 3: Setup Brain API
```bash
cd services/lumina-brain

# Install dependencies
uv sync

# Start the Brain API service
uv run start
```

### Step 4: Setup Crawler Service
```bash
# Open new terminal
cd services/crawler-go

# Install Go dependencies
go mod download

# Run the crawler (optional - for testing)
go run ./cmd/crawler
```

### Step 5: Setup Portal Frontend
```bash
# Open new terminal
cd services/portal-next

# Install dependencies
npm install

# Start the development server
npm run dev
```

### Step 6: Verify Setup
Open your browser and navigate to:
- **Portal**: http://localhost:3000
- **Brain API Docs**: http://localhost:8000/docs
- **Qdrant Health**: http://localhost:6333/health

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
   # Start Qdrant (if not running)
   docker-compose -f deployments/docker-compose.yaml up -d qdrant

   # Start Brain API
   cd services/lumina-brain && uv run start

   # Start Portal (in another terminal)
   cd services/portal-next && npm run dev
   ```

2. **Make Changes**:
   - Edit source code
   - Frontend changes auto-reload
   - Backend changes require restart

3. **Test Changes**:
   - Access http://localhost:3000
   - Test search functionality
   - Check API documentation at http://localhost:8000/docs

4. **Run Crawler** (optional):
   ```bash
   cd services/crawler-go
   go run ./cmd/crawler
   ```

### Code Quality

#### Linting and Formatting
```bash
# Go
cd services/crawler-go
go fmt ./...
go vet ./...

# Python
cd services/lumina-brain
flake8 src/
black src/

# JavaScript/TypeScript
cd services/portal-next
npm run lint
npm run format
```

#### Testing
```bash
# Go
cd services/crawler-go
go test ./...

# Python
cd services/lumina-brain
pytest

# JavaScript/TypeScript
cd services/portal-next
npm test
```

## 🐛 Troubleshooting

### Common Issues

#### Port Conflicts
```bash
# Check what's using ports
netstat -tulpn | grep :3000  # Portal
netstat -tulpn | grep :8000  # Brain API
netstat -tulpn | grep :6333  # Qdrant

# Kill processes using ports
sudo kill -9 <PID>
```

#### Docker Issues
```bash
# Reset Docker
docker system prune -a
docker-compose down -v
docker-compose up -d
```

#### Python Virtual Environment Issues
```bash
# Recreate virtual environment
cd services/lumina-brain
rm -rf .venv
uv venv
uv sync
```

#### Node.js Issues
```bash
# Clear npm cache
npm cache clean --force

# Delete node_modules and reinstall
cd services/portal-next
rm -rf node_modules package-lock.json
npm install
```

#### Go Module Issues
```bash
# Refresh Go modules
cd services/crawler-go
go clean -modcache
go mod download
go mod tidy
```

### Service-Specific Issues

#### Brain API Won't Start
```bash
# Check Python version
python --version

# Check dependencies
pip list | grep fastapi
pip list | grep qdrant

# Check logs
python main.py --verbose
```

#### Crawler Fails
```bash
# Check Go version
go version

# Check configuration
cd services/crawler-go
go run ./cmd/crawler --config=config-test.yaml

# Check Brain API connectivity
curl http://localhost:8000/health
```

#### Portal Shows Errors
```bash
# Check Node.js version
node --version

# Check API connectivity
curl http://localhost:8000/health

# Check browser console for errors
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
# Run all tests
make test

# Service-specific tests
cd services/lumina-brain && pytest
cd services/crawler-go && go test ./...
cd services/portal-next && npm test
```

### Integration Tests
```bash
# Test API integration
curl -X POST http://localhost:8000/ingest \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com", "title": "Test", "content": "Test content"}'

curl -X GET "http://localhost:8000/search?query=test"
```

### End-to-End Tests
```bash
# Test complete workflow
cd services/crawler-go
go run ./cmd/crawler

# Then test search in portal at http://localhost:3000
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
