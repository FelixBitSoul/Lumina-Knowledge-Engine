# Brain API Documentation

The Brain API is a Python FastAPI service that provides vector embedding generation and semantic search capabilities for the Lumina Knowledge Engine.

## 📋 Service Overview

- **Service Name**: Brain API
- **Technology**: Python 3.11 + FastAPI
- **Base URL**: `http://localhost:8000`
- **Version**: 1.0.0
- **Documentation**: `http://localhost:8000/docs` (Swagger UI)

## 🚀 Quick Start

### Start the Service
```bash
cd services/lumina-brain
uv run start
```

### Verify Health
```bash
curl -X GET http://localhost:8000/health
```

## 📡 Endpoints

### 1. Health Check

**Endpoint**: `GET /health`

**Purpose**: Verify service health and dependency status

**Request**:
```http
GET /health HTTP/1.1
Host: localhost:8000
```

**Response**:
```json
{
  "status": "ok",
  "qdrant": "up",
  "model": "all-MiniLM-L6-v2",
  "collection": "knowledge_base"
}
```

**Response Schema**:
```typescript
interface HealthResponse {
  status: "ok" | "error";
  qdrant: "up" | "down";
  model: string;
  collection: string;
}
```

**Status Codes**:
- `200 OK`: Service healthy
- `503 Service Unavailable`: Service or dependencies unhealthy

**Example**:
```bash
curl -X GET http://localhost:8000/health
# Response: {"status":"ok","qdrant":"up","model":"all-MiniLM-L6-v2","collection":"knowledge_base"}
```

---

### 2. Document Ingestion

**Endpoint**: `POST /ingest`

**Purpose**: Process document and store vector embedding

**Request**:
```http
POST /ingest HTTP/1.1
Host: localhost:8000
Content-Type: application/json

{
  "url": "https://docs.docker.com/get-started/",
  "title": "Docker Getting Started",
  "content": "Docker is a platform for developing, shipping, and running applications in containers..."
}
```

**Request Schema**:
```typescript
interface Document {
  url: string;        // Valid URL (max 2048 chars)
  title: string;      // Document title (1-200 chars)
  content: string;    // Cleaned text content (10-1,000,000 chars)
}
```

**Validation Rules**:
- `url`: Must be a valid HTTP/HTTPS URL
- `title`: Required, 1-200 characters
- `content`: Required, 10-1,000,000 characters
- `content`: Automatically sanitized for HTML/JS

**Success Response**:
```json
{
  "status": "success",
  "point_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Success Schema**:
```typescript
interface IngestSuccessResponse {
  status: "success";
  point_id: string;   // UUID of stored vector point
}
```

**Error Response**:
```json
{
  "status": "error",
  "message": "Invalid URL format"
}
```

**Error Schema**:
```typescript
interface ErrorResponse {
  status: "error";
  message: string;
}
```

**Status Codes**:
- `200 OK`: Document successfully ingested
- `400 Bad Request`: Invalid input data
- `500 Internal Server Error`: Processing error

**Examples**:

**Valid Request**:
```bash
curl -X POST http://localhost:8000/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://react.dev/learn",
    "title": "React Documentation",
    "content": "React is a JavaScript library for building user interfaces..."
  }'
```

**Invalid Request (Missing Fields)**:
```bash
curl -X POST http://localhost:8000/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com"
  }'
# Response: 400 Bad Request - Missing required fields
```

---

### 3. Semantic Search

**Endpoint**: `GET /search`

**Purpose**: Perform semantic similarity search with relevance reranking

**Request**:
```http
GET /search?query=how%20to%20install%20docker&limit=5 HTTP/1.1
Host: localhost:8000
```

**Query Parameters**:
```typescript
interface SearchParams {
  query: string;    // Search query (URL encoded, 1-500 chars)
  limit?: number;   // Maximum results (1-20, default: 3)
  collection?: string; // Vector collection name (optional)
}
```

**Parameter Validation**:
- `query`: Required, 1-500 characters after URL decoding
- `limit`: Optional, integer between 1-20
- `collection`: Optional, valid collection name

**Response**:
```json
{
  "query": "how to install docker",
  "limit": 5,
  "collection": "knowledge_base",
  "latency_ms": 100,
  "results": [
    {
      "score": 0.98,
      "vector_score": 0.92,
      "rerank_score": 0.98,
      "title": "Docker Installation Guide",
      "url": "https://docs.docker.com/get-started/",
      "content": "Docker is a platform for developing, shipping, and running applications..."
    },
    {
      "score": 0.95,
      "vector_score": 0.87,
      "rerank_score": 0.95,
      "title": "Container Basics",
      "url": "https://docs.docker.com/get-started/overview/",
      "content": "Containers are lightweight, standalone packages that include everything..."
    }
  ]
}
```

**Response Schema**:
```typescript
interface SearchResponse {
  query: string;
  limit: number;
  collection: string;
  latency_ms: number;
  results: SearchResult[];
}

interface SearchResult {
  score: number;         // Final relevance score (0.0-1.0)
  vector_score: number;  // Original vector similarity score
  rerank_score: number;  // Cross-Encoder reranking score
  title: string;         // Document title
  url: string;           // Source URL
  content: string;       // Content preview
  collection?: string;   // Collection name (if multi-collection search)
}
```

**Status Codes**:
- `200 OK`: Search completed successfully
- `400 Bad Request`: Invalid query parameters
- `500 Internal Server Error`: Search processing error

**Examples**:

**Basic Search**:
```bash
curl -X GET "http://localhost:8000/search?query=react%20hooks"
```

**Search with Limit**:
```bash
curl -X GET "http://localhost:8000/search?query=python%20tutorial&limit=10"
```

**Search in Specific Collection**:
```bash
curl -X GET "http://localhost:8000/search?query=docker&limit=5&collection=tech_docs"
```

**Invalid Query (Empty)**:
```bash
curl -X GET "http://localhost:8000/search?query="
# Response: 400 Bad Request - Query cannot be empty
```

**Invalid Limit (Too High)**:
```bash
curl -X GET "http://localhost:8000/search?query=test&limit=50"
# Response: 400 Bad Request - Limit must be between 1-20
```

---

### 4. Chat API

**Endpoint**: `POST /chat`

**Purpose**: Conversational interface with context awareness

**Request**:
```http
POST /chat HTTP/1.1
Host: localhost:8000
Content-Type: application/json

{
  "message": "How do I use Docker?",
  "conversation_id": "12345",
  "collection": "knowledge_base"
}
```

**Request Schema**:
```typescript
interface ChatRequest {
  message: string;           // User message (1-1000 chars)
  conversation_id?: string;  // Optional conversation ID
  collection?: string;       // Optional vector collection name
}
```

**Parameter Validation**:
- `message`: Required, 1-1000 characters
- `conversation_id`: Optional, valid UUID format
- `collection`: Optional, valid collection name

**Response**:
```json
{
  "id": "67890",
  "content": "To use Docker, you first need to install it on your system. You can download the installer from the official Docker website...",
  "conversation_id": "12345",
  "timestamp": 1678901234
}
```

**Response Schema**:
```typescript
interface ChatResponse {
  id: string;              // Response ID
  content: string;         // Assistant response
  conversation_id: string; // Conversation ID
  timestamp: number;       // Unix timestamp
}
```

**Status Codes**:
- `200 OK`: Chat response generated
- `400 Bad Request`: Invalid input data
- `500 Internal Server Error`: Processing error

**Example**:
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Tell me about React hooks",
    "collection": "tech_docs"
  }'
```

---

### 5. Streaming Chat API

**Endpoint**: `POST /chat/stream`

**Purpose**: Streaming conversational interface for real-time responses

**Request**:
```http
POST /chat/stream HTTP/1.1
Host: localhost:8000
Content-Type: application/json

{
  "message": "Explain machine learning",
  "collection": "ai_docs"
}
```

**Request Schema**:
```typescript
interface ChatRequest {
  message: string;           // User message (1-1000 chars)
  conversation_id?: string;  // Optional conversation ID
  collection?: string;       // Optional vector collection name
}
```

**Response**:
SSE (Server-Sent Events) stream with incremental response chunks:

```
data: {"id": "123", "content": "Machine learning is a subset of artificial intelligence that", "conversation_id": "54321", "is_finished": false}

data: {"id": "124", "content": " allows systems to learn from data without being explicitly", "conversation_id": "54321", "is_finished": false}

data: {"id": "125", "content": " programmed.", "conversation_id": "54321", "is_finished": true}
```

**Status Codes**:
- `200 OK`: Streaming response started
- `400 Bad Request`: Invalid input data
- `500 Internal Server Error`: Processing error

**Example**:
```bash
curl -N -X POST http://localhost:8000/chat/stream \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is Docker?",
    "collection": "tech_docs"
  }'
```

---

## 🔧 Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `QDRANT_HOST` | `localhost` | Qdrant database host |
| `QDRANT_PORT` | `6333` | Qdrant database port |
| `QDRANT_COLLECTION` | `knowledge_base` | Vector collection name |
| `MODEL_NAME` | `all-MiniLM-L6-v2` | Embedding model name |
| `MODEL_CACHE_DIR` | `./models` | Model cache directory |
| `OPENAI_API_KEY` | - | OpenAI API key for query rewriting |
| `OPENAI_API_BASE` | `https://api.openai.com/v1` | Custom OpenAI API endpoint |
| `LLM_MODEL_NAME` | `gpt-3.5-turbo` | LLM model for query rewriting |

### Model Configuration

**Default Model**: `all-MiniLM-L6-v2`
- **Dimensions**: 384
- **Size**: ~80MB
- **Language**: English (multilingual support)
- **Performance**: ~100ms per document

**Supported Models**:
- `all-MiniLM-L6-v2` (default)
- `all-mpnet-base-v2` (higher quality, slower)
- `paraphrase-multilingual-MiniLM-L12-v2` (multilingual)

## 📊 Performance Metrics

### Response Times

| Endpoint | Average | 95th Percentile | Target |
|----------|---------|-----------------|--------|
| `/health` | 5ms | 10ms | < 20ms |
| `/ingest` | 150ms | 300ms | < 500ms |
| `/search` | 45ms | 80ms | < 200ms |

### Throughput

| Operation | Current Rate | Maximum Rate |
|-----------|--------------|-------------|
| Embedding Generation | ~10 docs/sec | ~20 docs/sec |
| Search Queries | ~20 qps | ~50 qps |
| Concurrent Users | 50 | 200 |

## 🛡️ Error Handling

### Error Response Format

All errors return a consistent JSON format:

```json
{
  "status": "error",
  "message": "Human-readable error description",
  "error_code": "ERROR_CODE",
  "timestamp": "2026-03-17T12:00:00Z"
}
```

### Common Error Codes

| Error Code | HTTP Status | Description |
|------------|-------------|-------------|
| `INVALID_URL` | 400 | URL format is invalid |
| `MISSING_FIELD` | 400 | Required field is missing |
| `INVALID_CONTENT` | 400 | Content length or format invalid |
| `MODEL_ERROR` | 500 | Embedding model failure |
| `DATABASE_ERROR` | 500 | Qdrant database error |
| `EMPTY_QUERY` | 400 | Search query cannot be empty |
| `INVALID_LIMIT` | 400 | Search limit out of range |

### Error Examples

**Validation Error**:
```json
{
  "status": "error",
  "message": "Invalid URL format: not-a-url",
  "error_code": "INVALID_URL",
  "timestamp": "2026-03-17T12:00:00Z"
}
```

**Database Error**:
```json
{
  "status": "error",
  "message": "Failed to connect to Qdrant database",
  "error_code": "DATABASE_ERROR",
  "timestamp": "2026-03-17T12:00:00Z"
}
```

## 🔒 Security

### Input Sanitization

- **URL Validation**: Strict URL format checking
- **Content Sanitization**: HTML/JavaScript removal
- **Length Limits**: Prevent resource exhaustion
- **Encoding**: Proper UTF-8 handling

### CORS Configuration

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Rate Limiting (Planned)

Future implementation will include rate limiting:
- **IP-based limiting**: 100 requests/minute
- **User-based limiting**: 1000 requests/hour
- **Endpoint-specific limits**: Different limits per endpoint

## 📝 Examples

### Complete Workflow

1. **Ingest Documents**:
```bash
# Document 1
curl -X POST http://localhost:8000/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://docs.docker.com/get-started/",
    "title": "Docker Getting Started",
    "content": "Docker is a platform for developing, shipping, and running applications in containers. Docker enables you to separate your applications from your infrastructure..."
  }'

# Document 2
curl -X POST http://localhost:8000/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://react.dev/learn",
    "title": "React Documentation",
    "content": "React is a JavaScript library for building user interfaces. It lets you compose complex UIs from small and isolated pieces of code called components..."
  }'
```

2. **Search Documents**:
```bash
curl -X GET "http://localhost:8000/search?query=container%20development"
```

3. **Expected Response**:
```json
{
  "query": "container development",
  "limit": 3,
  "collection": "knowledge_base",
  "latency_ms": 52,
  "results": [
    {
      "score": 0.92,
      "title": "Docker Getting Started",
      "url": "https://docs.docker.com/get-started/",
      "content": "Docker is a platform for developing, shipping, and running applications in containers..."
    }
  ]
}
```

### Batch Processing (Python)

```python
import requests
import json

# Documents to ingest
documents = [
    {
        "url": "https://docs.python.org/3/tutorial/",
        "title": "Python Tutorial",
        "content": "Python is an interpreted, high-level, general-purpose programming language..."
    },
    {
        "url": "https://fastapi.tiangolo.com/tutorial/",
        "title": "FastAPI Tutorial", 
        "content": "FastAPI is a modern, fast web framework for building APIs with Python..."
    }
]

# Ingest documents
for doc in documents:
    response = requests.post(
        "http://localhost:8000/ingest",
        json=doc,
        headers={"Content-Type": "application/json"}
    )
    print(f"Ingested {doc['title']}: {response.json()}")

# Search
search_response = requests.get(
    "http://localhost:8000/search",
    params={"query": "python web framework", "limit": 5}
)
print("Search Results:", json.dumps(search_response.json(), indent=2))
```

## 🔄 Integration Examples

### JavaScript/TypeScript Client

```typescript
class BrainAPIClient {
  private baseUrl: string;

  constructor(baseUrl = 'http://localhost:8000') {
    this.baseUrl = baseUrl;
  }

  async health(): Promise<HealthResponse> {
    const response = await fetch(`${this.baseUrl}/health`);
    return response.json();
  }

  async ingest(doc: Document): Promise<IngestResponse> {
    const response = await fetch(`${this.baseUrl}/ingest`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(doc)
    });
    return response.json();
  }

  async search(query: string, limit = 3): Promise<SearchResponse> {
    const params = new URLSearchParams({ query, limit: limit.toString() });
    const response = await fetch(`${this.baseUrl}/search?${params}`);
    return response.json();
  }
}

// Usage
const client = new BrainAPIClient();

// Search example
const results = await client.search('react hooks tutorial');
console.log('Search results:', results.results);
```

### Python Client

```python
import requests
from typing import List, Dict, Any

class BrainAPIClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url

    def health(self) -> Dict[str, Any]:
        response = requests.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()

    def ingest(self, url: str, title: str, content: str) -> Dict[str, Any]:
        doc = {"url": url, "title": title, "content": content}
        response = requests.post(
            f"{self.base_url}/ingest",
            json=doc,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        return response.json()

    def search(self, query: str, limit: int = 3) -> Dict[str, Any]:
        params = {"query": query, "limit": limit}
        response = requests.get(f"{self.base_url}/search", params=params)
        response.raise_for_status()
        return response.json()

# Usage
client = BrainAPIClient()

# Ingest document
result = client.ingest(
    url="https://example.com/docs",
    title="Example Doc",
    content="This is example content..."
)
print(f"Ingested with ID: {result['point_id']}")

# Search
search_results = client.search("example query")
for result in search_results["results"]:
    print(f"Score: {result['score']:.2f} - {result['title']}")
```

---

*For OpenAPI specifications, see the [OpenAPI directory](./openapi/).*
