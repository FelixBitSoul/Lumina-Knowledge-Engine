# 🧠 Lumina Brain API

The **Lumina Brain API** is the core AI service of the Lumina Knowledge Engine, providing vector embedding generation, semantic search, and conversational AI capabilities via a RESTful FastAPI interface.

Built with Python 3.11, FastAPI, and Sentence Transformers.

---

## ✨ Features

- **🔢 Vector Embeddings**: 384-dimensional embeddings using all-MiniLM-L6-v2 with automatic model caching
- **🔍 Semantic Search**: Cosine similarity search with Qdrant prefetch pagination and metadata filtering
- **🎯 Query Rewriting**: Context-aware query rewriting for multi-turn conversations
- **📊 Reranking**: Cross-Encoder based relevance optimization (for chat only)
- **🔄 Multi-Collection Search**: Search across multiple vector collections with unified results
- **💬 Conversational AI**: Context-aware chat interface with reranking
- **⚡ High Performance**: FastAPI async endpoints for optimal throughput
- **📊 RESTful API**: OpenAPI-documented endpoints with automatic validation
- **🐳 Docker Ready**: Production-ready containerization
- **💾 Qdrant Integration**: High-performance vector database storage with automatic collection creation
- **🔄 Model Caching**: Automatic model download and caching
- **📈 Health Monitoring**: Built-in health check endpoints
- **📄 Collections API**: Dynamic collection listing from Qdrant
- **📥 Document Upload**: Support for PDF and text file uploads with async processing
- **🔧 Metadata Filtering**: Filter by title, domain, URL, and time range
- **⚡ Async Processing**: Celery-based background task processing
- **📦 MinIO Integration**: Object storage for original documents
- **🌐 WebSocket Notifications**: Real-time document processing updates
- **🔄 Task Management**: Task status tracking and monitoring

---

## 🏗 Architecture

```
┌─────────────────────────────────────┐
│         🧠 Lumina Brain API        │
│      (Python 3.11 + FastAPI)        │
├─────────────────────────────────────┤
│  📄 main.py                         │
│    ├── GET  /health                │
│    ├── POST /ingest                │
│    ├── GET  /collections           │
│    ├── GET  /search                │
│    └── POST /chat                  │
├─────────────────────────────────────┤
│  🔢 Embedding: all-MiniLM-L6-v2    │
│  📊 Reranking: cross-encoder       │
│  🎯 Query Rewriter: LLM-based      │
├─────────────────────────────────────┤
│  🔌 Connects to:                    │
│    - Qdrant (6333)                 │
│    - Redis (6379)                  │
│    - MinIO (9000)                  │
│    - OpenAI API (for rewriting)    │
└─────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- uv package manager
- Qdrant running (see [deployments/docker-compose.yaml](../../deployments/docker-compose.yaml))
- Redis running (for Celery task queue)
- MinIO running (for document storage)

### Installation

```bash
# Create virtual environment and install dependencies
uv sync

# Run the service
uv run python -m lumina_brain.main
```

### Configuration

Set environment variables or create `.env` file:

```bash
QDRANT_HOST=localhost
QDRANT_PORT=6333
QDRANT_COLLECTION=knowledge_base
MODEL_NAME=all-MiniLM-L6-v2
MODEL_CACHE_DIR=./models
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_API_BASE=https://api.deepseek.com/v1
LLM_MODEL_NAME=deepseek-chat
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
MINIO_ENDPOINT=minio:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET=lumina-documents
```

### Run the Service

```bash
# Start the API service
uv run python -m lumina_brain.main

# Or with uvicorn directly
uv run uvicorn lumina_brain.main:app --host 0.0.0.0 --port 8000 --reload

# Start Celery worker for async processing
uv run celery -A lumina_brain.celery_app worker --loglevel=info --concurrency=4
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

### 📤 `POST /upload`

Upload and ingest documents (PDF, text files) with async processing.

**Request:**
```bash
curl -X POST http://localhost:8000/upload \
  -F "file=@document.pdf" \
  -F "category=technical" \
  -F "collection=documents"
```

**Response:**
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "file_id": "b2e1bfd0-921d-7586-9436-589beae56676",
  "file_name": "document.pdf",
  "category": "technical",
  "collection": "documents",
  "status": "pending",
  "websocket_url": "ws://localhost:8000/ws/b2e1bfd0-921d-7586-9436-589beae56676",
  "message": "Document uploaded successfully. Processing in background."
}
```

---

### 🔎 `GET /search`

Perform semantic similarity search with metadata filtering and Qdrant prefetch pagination.

**Request:**
```bash
curl -X GET "http://localhost:8000/search?query=how%20to%20install%20docker&limit=5&page=1&domain=docs.docker.com"
```

**Response:**
```json
{
  "query": "how to install docker",
  "page_size": 5,
  "page": 1,
  "offset": 0,
  "collection": "knowledge_base",
  "filters": {"domain": "docs.docker.com"},
  "latency_ms": 100,
  "results": [
    {
      "score": 0.98,
      "title": "Docker Installation Guide",
      "url": "https://docs.docker.com/get-started/",
      "domain": "docs.docker.com",
      "content": "Docker is a platform for developing...",
      "updated_at": "2026-03-30T12:00:00Z"
    }
  ]
}
```

---

### 📚 `GET /collections`

List all available vector collections.

**Response:**
```json
{
  "collections": ["knowledge_base", "technical_docs"]
}
```

---

### 💬 `POST /chat`

Conversational interface with context awareness.

**Request:**
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "How do I use Docker?",
    "conversation_id": "12345",
    "collection": "knowledge_base"
  }'
```

**Response:**
```json
{
  "id": "67890",
  "content": "To use Docker, you first need to install it...",
  "conversation_id": "12345",
  "timestamp": 1678901234
}
```

---

### 📋 `GET /upload/tasks/{task_id}`

Get status of an upload task.

**Response:**
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "progress": 100,
  "total": 100,
  "current_step": "Completed",
  "result": {
    "file_id": "b2e1bfd0-921d-7586-9436-589beae56676",
    "filename": "document.pdf",
    "chunks_created": 25,
    "status": "success"
  }
}
```

---

### 🔗 `GET /documents/{file_id}/preview-url`

Generate temporary preview URL for a document.

**Response:**
```json
{
  "preview_url": "https://minio.local:9000/lumina-documents/b2e1bfd0-921d-7586-9436-589beae56676/raw/document.pdf?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=minioadmin%2F20260404%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20260404T100000Z&X-Amz-Expires=600&X-Amz-SignedHeaders=host&X-Amz-Signature=...",
  "expires_in": 600
}
```

---

### 🗑️ `DELETE /documents/{file_id}`

Delete a document and its embeddings.

**Request:**
```bash
curl -X DELETE "http://localhost:8000/documents/b2e1bfd0-921d-7586-9436-589beae56676?collection=documents&filename=document.pdf"
```

**Response:**
```json
{
  "status": "success",
  "message": "Document deleted successfully"
}
```

---

### 🌐 `WebSocket /ws/{file_id}`

Real-time document processing notifications.

**Messages:**
- `connected`: Connection established
- `processing`: Processing in progress with progress updates
- `completed`: Processing completed successfully
- `failed`: Processing failed with error

---

### 💬 `POST /chat/stream`

Streaming conversational interface for real-time responses.

**Request:**
```bash
curl -N -X POST http://localhost:8000/chat/stream \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Tell me about Docker",
    "collection": "knowledge_base"
  }'
```

**Response:**
SSE (Server-Sent Events) stream with incremental response chunks.

---

## 📁 Project Structure

```
lumina-brain/
├── src/
│   └── lumina_brain/
│       ├── __init__.py            # Version information
│       ├── main.py                # FastAPI application
│       ├── celery_app.py          # Celery application configuration
│       ├── api/                   # API endpoints
│       │   ├── router.py          # API router
│       │   └── endpoints/         # Endpoint handlers
│       │       ├── upload.py      # File upload endpoint
│       │       ├── websocket.py   # WebSocket endpoint
│       │       ├── documents.py   # Document management endpoints
│       ├── core/                  # Core services
│       │   ├── services/          # Service implementations
│       │   │   ├── minio.py       # MinIO object storage service
│       │   │   ├── websocket_manager.py  # WebSocket connection manager
│       │   ├── vector_service.py  # Vector search service
│       │   ├── query_rewriter.py  # Query rewriting service
│       │   ├── reranker.py        # Relevance reranking service
│       │   └── llm_service.py     # LLM service
│       ├── tasks/                 # Celery tasks
│       │   └── document_tasks.py  # Document processing tasks
│       ├── schemas/               # Data models
│       └── config/                # Configuration
├── tests/                         # Test directory
├── pyproject.toml                 # Project configuration
├── uv.lock                        # uv lock file
├── .env.example                   # Environment variables example
├── Dockerfile                     # Container configuration
└── README.md                      # This file
```

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
| `OPENAI_API_KEY` | ✅ | - | OpenAI API key for query rewriting |
| `OPENAI_API_BASE` | ❌ | `https://api.openai.com/v1` | Custom OpenAI API endpoint |
| `LLM_MODEL_NAME` | ❌ | `gpt-3.5-turbo` | LLM model for query rewriting |
| `REDIS_HOST` | ✅ | `localhost` | Redis host for Celery |
| `REDIS_PORT` | ✅ | `6379` | Redis port for Celery |
| `REDIS_DB` | ❌ | `0` | Redis database for Celery |
| `MINIO_ENDPOINT` | ✅ | `minio:9000` | MinIO endpoint |
| `MINIO_ACCESS_KEY` | ✅ | - | MinIO access key |
| `MINIO_SECRET_KEY` | ✅ | - | MinIO secret key |
| `MINIO_BUCKET` | ❌ | `lumina-documents` | MinIO bucket name |

### Model Configuration

#### Embedding Model
**Default**: `all-MiniLM-L6-v2`
- **Dimensions**: 384
- **Size**: ~80MB
- **Languages**: English (multilingual models available)

#### Reranking Model
**Default**: `cross-encoder/ms-marco-MiniLM-L-12-v2`
- **Type**: Cross-Encoder
- **Size**: ~200MB
- **Purpose**: Relevance reranking

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
  -e OPENAI_API_KEY=your_api_key \
  lumina/brain-api:latest

# With volume for model cache
docker run -d \
  -p 8000:8000 \
  -e QDRANT_HOST=host.docker.internal \
  -e QDRANT_PORT=6333 \
  -e OPENAI_API_KEY=your_api_key \
  -v lumina_models:/app/models \
  lumina/brain-api:latest
```

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

---

## 📊 Performance

### Benchmarks

| Operation | Average | P95 | Notes |
|-----------|---------|-----|-------|
| Health Check | 5ms | 10ms | Simple status check |
| Document Ingest | 150ms | 300ms | Includes embedding generation |
| Search with Reranking | 100ms | 150ms | Includes 100 candidates + reranking |
| Query Rewriting | 300ms | 500ms | LLM-based context processing |
| Chat Response | 500ms | 1000ms | Includes rewriting + search + LLM response |

---

## 🔗 Related Documentation

- **API Reference**: [docs/api/brain-api.md](../../docs/api/brain-api.md)
- **OpenAPI Spec**: [docs/api/openapi/brain-api.yaml](../../docs/api/openapi/brain-api.yaml)
- **Deployment Guide**: [docs/deployment/docker-deployment.md](../../docs/deployment/docker-deployment.md)

---

## 🤝 Contributing

1. Follow the [AI Collaboration Guide](../../AI_COLLABORATION_GUIDE.md)
2. Write tests for new features
3. Ensure code passes linting
4. Update API documentation for endpoint changes
5. Follow PEP 8 style guidelines

---

## 📄 License

This project is part of the Lumina Knowledge Engine and is licensed under the MIT License.

---

<p align="center">
  Part of <a href="../../README.md">Lumina Knowledge Engine</a> 🔍
</p>