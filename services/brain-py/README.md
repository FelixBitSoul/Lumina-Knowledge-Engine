# 🧠 Lumina Brain API

The **Brain API** is the core AI service of the Lumina Knowledge Engine, providing vector embedding generation and semantic search capabilities via a RESTful FastAPI interface.

Built with Python 3.11, FastAPI, and Sentence Transformers.

---

## ✨ Features

- **🔢 Vector Embeddings**: 384-dimensional embeddings using all-MiniLM-L6-v2
- **🔍 Semantic Search**: Cosine similarity search across vector collections
- **⚡ High Performance**: FastAPI async endpoints for optimal throughput
- **📊 RESTful API**: OpenAPI-documented endpoints with automatic validation
- **🐳 Docker Ready**: Production-ready containerization
- **💾 Qdrant Integration**: High-performance vector database storage
- **🔄 Model Caching**: Automatic model download and caching
- **📈 Health Monitoring**: Built-in health check endpoints

---

## 🏗 Architecture

```
┌─────────────────────────────────────┐
│         🧠 Brain API                │
│      (Python 3.11 + FastAPI)        │
├─────────────────────────────────────┤
│  📄 main.py                         │
│    ├── GET  /health                │
│    ├── POST /ingest                │
│    └── GET  /search                │
├─────────────────────────────────────┤
│  🔢 all-MiniLM-L6-v2 (384 dims)    │
├─────────────────────────────────────┤
│  🔌 Connects to: Qdrant (6333)     │
└─────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- pip or conda
- Qdrant running (see [deployments/docker-compose.yaml](../../deployments/docker-compose.yaml))

### Installation

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (macOS/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Configuration

Set environment variables:

```bash
# Windows PowerShell
$env:QDRANT_HOST="localhost"
$env:QDRANT_PORT="6333"

# macOS/Linux
export QDRANT_HOST=localhost
export QDRANT_PORT=6333
```

Or create `.env` file:

```bash
QDRANT_HOST=localhost
QDRANT_PORT=6333
QDRANT_COLLECTION=knowledge_base
MODEL_NAME=all-MiniLM-L6-v2
LOG_LEVEL=info
```

### Run the Service

```bash
# Development mode with auto-reload
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Production mode
python main.py

# Or with uvicorn directly
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

Access the service:
- **🚀 API Base**: http://localhost:8000
- **📖 API Docs**: http://localhost:8000/docs (Swagger UI)
- **📚 ReDoc**: http://localhost:8000/redoc
- **💓 Health**: http://localhost:8000/health

---

## 📡 API Endpoints

### 🔍 `GET /health`

Service health check with dependency status.

**Response:**
```json
{
  "status": "ok",
  "qdrant": "up",
  "model": "all-MiniLM-L6-v2",
  "collection": "knowledge_base"
}
```

---

### 📥 `POST /ingest`

Ingest a document and generate vector embedding.

**Request:**
```bash
curl -X POST http://localhost:8000/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://docs.docker.com/get-started/",
    "title": "Docker Getting Started",
    "content": "Docker is a platform for developing..."
  }'
```

**Response:**
```json
{
  "status": "success",
  "point_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

---

### 🔎 `GET /search`

Perform semantic similarity search.

**Request:**
```bash
curl -X GET "http://localhost:8000/search?query=how%20to%20install%20docker&limit=5"
```

**Response:**
```json
{
  "query": "how to install docker",
  "limit": 5,
  "collection": "knowledge_base",
  "latency_ms": 45,
  "results": [
    {
      "score": 0.95,
      "title": "Docker Installation Guide",
      "url": "https://docs.docker.com/get-started/",
      "content": "Docker is a platform for developing..."
    }
  ]
}
```

---

## 📁 Project Structure

```
brain-py/
├── 📄 main.py                 # FastAPI application
├── 📄 requirements.txt        # Python dependencies
├── 📄 Dockerfile              # Container configuration
├── 📁 models/                 # Model cache directory
│   └── all-MiniLM-L6-v2/      # Downloaded transformer model
└── 📄 README.md               # This file
```

### Key Files

- **`main.py`**: FastAPI application with endpoints
- **`requirements.txt`**: Python dependencies
- **`Dockerfile`**: Multi-stage container build

---

## ⚙️ Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `QDRANT_HOST` | ✅ | `localhost` | Qdrant database host |
| `QDRANT_PORT` | ✅ | `6333` | Qdrant database port |
| `QDRANT_COLLECTION` | ❌ | `knowledge_base` | Vector collection name |
| `MODEL_NAME` | ❌ | `all-MiniLM-L6-v2` | Embedding model name |
| `MODEL_CACHE_DIR` | ❌ | `./models` | Model cache directory |
| `API_HOST` | ❌ | `0.0.0.0` | API bind host |
| `API_PORT` | ❌ | `8000` | API bind port |
| `LOG_LEVEL` | ❌ | `info` | Logging level |

### Model Configuration

**Default Model**: `all-MiniLM-L6-v2`

- **Dimensions**: 384
- **Size**: ~80MB
- **Languages**: English (multilingual models available)
- **Performance**: ~100ms per document

Alternative models:
- `all-mpnet-base-v2`: Higher quality, slower (768 dims)
- `paraphrase-multilingual-MiniLM-L12-v2`: Multilingual support

---

## 📦 Dependencies

### Core
- **fastapi**: ^0.104.0 - Modern web framework
- **uvicorn**: ^0.24.0 - ASGI server
- **sentence-transformers**: ^2.2.0 - Embedding models
- **qdrant-client**: ^1.6.0 - Vector database client

### Utilities
- **pydantic**: ^2.5.0 - Data validation
- **python-dotenv**: ^1.0.0 - Environment variables
- **numpy**: ^1.24.0 - Numerical operations

### Development
- **pytest**: ^7.4.0 - Testing framework
- **httpx**: ^0.25.0 - HTTP client for testing
- **black**: ^23.0.0 - Code formatting
- **flake8**: ^6.1.0 - Code linting

See `requirements.txt` for complete list.

---

## 🧪 Testing

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run tests
pytest

# Run with coverage
pytest --cov=.

# Run specific test
pytest tests/test_api.py

# Format code
black .

# Lint code
flake8 .
```

---

## 🐳 Docker Support

### Build Image

```bash
# Build locally
docker build -t lumina/brain-api:latest .

# Build with no cache
docker build --no-cache -t lumina/brain-api:latest .
```

### Run Container

```bash
# Basic run
docker run -d \
  -p 8000:8000 \
  -e QDRANT_HOST=host.docker.internal \
  -e QDRANT_PORT=6333 \
  lumina/brain-api:latest

# With volume for model cache
docker run -d \
  -p 8000:8000 \
  -e QDRANT_HOST=host.docker.internal \
  -e QDRANT_PORT=6333 \
  -v brain_models:/app/models \
  lumina/brain-api:latest
```

### Docker Compose

See [deployments/docker-compose.yaml](../../deployments/docker-compose.yaml) for complete multi-service setup.

---

## 🔌 Integration Examples

### Python Client

```python
import requests

# Search
response = requests.get(
    "http://localhost:8000/search",
    params={"query": "docker tutorial", "limit": 5}
)
results = response.json()

for result in results["results"]:
    print(f"{result['score']:.2f}: {result['title']}")
```

### JavaScript/TypeScript Client

```typescript
// Search
const response = await fetch(
  'http://localhost:8000/search?query=docker+tutorial&limit=5'
);
const data = await response.json();

console.log(data.results.map(r => `${r.score}: ${r.title}`));
```

### cURL

```bash
# Health check
curl http://localhost:8000/health

# Search
curl -X GET "http://localhost:8000/search?query=test&limit=3"

# Ingest
curl -X POST http://localhost:8000/ingest \
  -H "Content-Type: application/json" \
  -d '{"url": "...", "title": "...", "content": "..."}'
```

---

## 📊 Performance

### Benchmarks

| Operation | Average | P95 | Notes |
|-----------|---------|-----|-------|
| Health Check | 5ms | 10ms | Simple status check |
| Document Ingest | 150ms | 300ms | Includes embedding generation |
| Semantic Search | 45ms | 80ms | Vector similarity search |

### Resource Usage

| Resource | Minimum | Recommended |
|----------|---------|-------------|
| CPU | 1 core | 2+ cores |
| RAM | 1GB | 2GB+ |
| Disk | 500MB | 1GB+ (for model cache) |

---

## 🔗 Related Documentation

- **API Reference**: [docs/api/brain-api.md](../../docs/api/brain-api.md)
- **OpenAPI Spec**: [docs/api/openapi/brain-api.yaml](../../docs/api/openapi/brain-api.yaml)
- **Deployment Guide**: [docs/deployment/docker-deployment.md](../../docs/deployment/docker-deployment.md)
- **Architecture**: [docs/architecture/component-details.md](../../docs/architecture/component-details.md)

---

## 🤝 Contributing

1. Follow the [AI Collaboration Guide](../../AI_COLLABORATION_GUIDE.md)
2. Write tests for new features
3. Ensure code passes linting: `black . && flake8 .`
4. Update API documentation for endpoint changes
5. Follow PEP 8 style guidelines

---

## 📄 License

This project is part of the Lumina Knowledge Engine and is licensed under the MIT License.

---

<p align="center">
  Part of <a href="../../README.md">Lumina Knowledge Engine</a> 🔍
</p>
