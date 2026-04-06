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

**Purpose**: Perform semantic similarity search with Qdrant prefetch for efficient pagination

**Request**:
```http
GET /search?query=how%20to%20install%20docker&page_size=5&page=1 HTTP/1.1
Host: localhost:8000
```

**Query Parameters**:
```typescript
interface SearchParams {
  query: string;       // Search query (URL encoded, 1-500 chars)
  page_size?: number;  // Results per page (1-20, default: 3)
  page?: number;       // Page number, 1-based (default: 1)
  collection?: string;  // Vector collection name (optional)
  // Meta filters
  title?: string;      // Filter by title (full-text search)
  domain?: string;      // Filter by domain (exact match)
  start_time?: string;  // Filter by start time (ISO format)
  end_time?: string;    // Filter by end time (ISO format)
}
```

**Parameter Validation**:
- `query`: Required, 1-500 characters after URL decoding
- `page_size`: Optional, integer between 1-20, default 3
- `page`: Optional, integer >= 1, default 1
- `collection`: Optional, valid collection name
- `title`, `domain`, `start_time`, `end_time`: Optional metadata filters

**Response**:
```json
{
  "query": "how to install docker",
  "page_size": 5,
  "page": 1,
  "offset": 0,
  "collection": "knowledge_base",
  "filters": null,
  "latency_ms": 45,
  "results": [
    {
      "score": 0.92,
      "title": "Docker Installation Guide",
      "url": "https://docs.docker.com/get-started/",
      "domain": "docs.docker.com",
      "content": "Docker is a platform for developing, shipping, and running applications...",
      "updated_at": "2026-03-29T10:30:00Z"
    },
    {
      "score": 0.89,
      "title": "Container Basics",
      "url": "https://docs.docker.com/get-started/overview/",
      "domain": "docs.docker.com",
      "content": "Containers are lightweight, standalone packages that include everything...",
      "updated_at": "2026-03-28T15:45:00Z"
    }
  ]
}
```

**Response Schema**:
```typescript
interface SearchResponse {
  query: string;
  page_size: number;
  page: number;
  offset: number;
  collection: string;
  filters: SearchFilters | null;
  latency_ms: number;
  results: SearchResult[];
}

interface SearchFilters {
  title?: string;
  domain?: string;
  start_time?: string;
  end_time?: string;
}

interface SearchResult {
  score: number;       // Vector similarity score (0.0-1.0)
  title: string;        // Document title
  url: string;          // Source URL
  domain: string;       // Document domain
  content: string;      // Content preview
  updated_at: string;   // Last update time (ISO format)
}
```

**Pagination**:
- Results are paginated with `page_size` and `page` parameters
- `offset = (page - 1) * page_size`
- Response includes current page info for UI display

**Note**: Search uses Qdrant prefetch for efficient pagination without Cross-Encoder reranking. For chat functionality, reranking is applied to improve result quality.

**Status Codes**:
- `200 OK`: Search completed successfully
- `400 Bad Request`: Invalid query parameters
- `500 Internal Server Error`: Search processing error

**Examples**:

**Basic Search**:
```bash
curl -X GET "http://localhost:8000/search?query=react%20hooks"
```

**Paginated Search**:
```bash
curl -X GET "http://localhost:8000/search?query=python%20tutorial&page_size=10&page=2"
```

**Search with Filters**:
```bash
curl -X GET "http://localhost:8000/search?query=docker&page_size=5&domain=docs.docker.com"
```

**Search in Specific Collection**:
```bash
curl -X GET "http://localhost:8000/search?query=docker&page_size=5&collection=tech_docs"
```

---

### 4. Document Upload API

**Endpoint**: `POST /upload`

**Purpose**: Upload and ingest documents (PDF, text files)

**Request**:
```http
POST /upload HTTP/1.1
Host: localhost:8000
Content-Type: multipart/form-data

file=@document.pdf
```

**Request Schema**:
```typescript
interface UploadRequest {
  file: File;  // PDF or text file
}
```

**Validation Rules**:
- `file`: Required, must be PDF or text file
- File size: Maximum 10MB

**Success Response**:
```json
{
  "status": "success",
  "documents": [
    {
      "title": "Document Title",
      "point_id": "550e8400-e29b-41d4-a716-446655440000"
    }
  ]
}
```

**Success Schema**:
```typescript
interface UploadSuccessResponse {
  status: "success";
  documents: Array<{
    title: string;   // Document title
    point_id: string; // UUID of stored vector point
  }>;
}
```

**Error Response**:
```json
{
  "status": "error",
  "message": "Invalid file format"
}
```

**Status Codes**:
- `200 OK`: File successfully uploaded and ingested
- `400 Bad Request`: Invalid file format or size
- `500 Internal Server Error`: Processing error

**Example**:
```bash
curl -X POST http://localhost:8000/upload \
  -F "file=@document.pdf"
```

---

### 5. Collections API

**Endpoint**: `GET /collections`

**Purpose**: Get all available collections from Qdrant

**Request**:
```http
GET /collections HTTP/1.1
Host: localhost:8000
```

**Response**:
```json
{
  "collections": ["knowledge_base", "tech_docs", "web_docs"],
  "count": 3
}
```

**Response Schema**:
```typescript
interface CollectionsResponse {
  collections: string[];  // List of collection names
  count: number;          // Number of collections
}
```

**Status Codes**:
- `200 OK`: Collections retrieved successfully
- `500 Internal Server Error`: Database error

**Example**:
```bash
curl -X GET http://localhost:8000/collections
```

---

### 6. Chat API

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

### 7. Streaming Chat API

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

### 8. File Management API

#### 8.1 List Files

**Endpoint**: `GET /documents`

**Purpose**: List files in a collection with pagination

**Request**:
```http
GET /documents?collection=knowledge_base&limit=20&start_after=raw/collections/knowledge_base/docs/file1.pdf HTTP/1.1
Host: localhost:8000
```

**Query Parameters**:
```typescript
interface ListFilesParams {
  collection: string;       // Collection name (default: knowledge_base)
  limit?: number;           // Maximum number of files to return (default: 20)
  start_after?: string;     // Object name to start after (for pagination)
}
```

**Response**:
```json
{
  "collection": "knowledge_base",
  "files": [
    {
      "file_id": "550e8400-e29b-41d4-a716-446655440000",
      "filename": "Docker Installation Guide.pdf",
      "size": 1024000,
      "uploaded_at": "2026-03-29T10:30:00Z",
      "type": "document",
      "object_name": "raw/collections/knowledge_base/docs/550e8400-e29b-41d4-a716-446655440000.pdf"
    },
    {
      "file_id": "12345678-1234-1234-1234-123456789012",
      "filename": "React Documentation",
      "size": 512000,
      "uploaded_at": "2026-03-28T15:45:00Z",
      "type": "web",
      "url": "https://react.dev/learn",
      "object_name": "raw/collections/knowledge_base/web/12345678-1234-1234-1234-123456789012.json"
    }
  ],
  "count": 2,
  "next_marker": "raw/collections/knowledge_base/web/12345678-1234-1234-1234-123456789012.json"
}
```

**Response Schema**:
```typescript
interface ListFilesResponse {
  collection: string;       // Collection name
  files: File[];           // List of files
  count: number;           // Number of files returned
  next_marker?: string;     // Next marker for pagination
}

interface File {
  file_id: string;          // File ID
  filename: string;         // Original filename
  size: number;             // File size in bytes
  uploaded_at: string;      // Upload timestamp (ISO format)
  type: "document" | "web"; // File type
  url?: string;            // Web URL (for web type)
  object_name: string;      // MinIO object name
}
```

**Status Codes**:
- `200 OK`: Files listed successfully
- `500 Internal Server Error`: Processing error

**Example**:
```bash
curl -X GET "http://localhost:8000/documents?collection=knowledge_base&limit=20"
```

#### 8.2 Delete File

**Endpoint**: `DELETE /documents/{file_id}`

**Purpose**: Delete document from Qdrant and MinIO

**Request**:
```http
DELETE /documents/550e8400-e29b-41d4-a716-446655440000?collection=knowledge_base&filename=Docker%20Installation%20Guide.pdf HTTP/1.1
Host: localhost:8000
```

**Path Parameters**:
- `file_id`: Document ID (based on content hash)

**Query Parameters**:
- `collection`: Qdrant collection name (default: knowledge_base)
- `filename`: Original filename (required for MinIO deletion)

**Response**:
```json
{
  "file_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "deleted",
  "message": "Document deleted successfully"
}
```

**Response Schema**:
```typescript
interface DeleteFileResponse {
  file_id: string;          // Deleted file ID
  status: "deleted";        // Status
  message: string;          // Success message
}
```

**Status Codes**:
- `200 OK`: File deleted successfully
- `500 Internal Server Error`: Processing error

**Example**:
```bash
curl -X DELETE "http://localhost:8000/documents/550e8400-e29b-41d4-a716-446655440000?collection=knowledge_base&filename=Docker%20Installation%20Guide.pdf"
```

---

### 9. Collections Management API

#### 9.1 Create Collection

**Endpoint**: `POST /collections`

**Purpose**: Create a new collection in Qdrant

**Request**:
```http
POST /collections HTTP/1.1
Host: localhost:8000
Content-Type: application/json

{
  "name": "tech_docs",
  "description": "Technical documentation collection"
}
```

**Request Schema**:
```typescript
interface CreateCollectionRequest {
  name: string;            // Collection name
  description: string;      // Collection description
}
```

**Response**:
```json
{
  "collection": "tech_docs",
  "message": "Collection created successfully"
}
```

**Response Schema**:
```typescript
interface CreateCollectionResponse {
  collection: string;       // Created collection name
  message: string;          // Success message
}
```

**Status Codes**:
- `200 OK`: Collection created successfully
- `500 Internal Server Error`: Processing error

**Example**:
```bash
curl -X POST http://localhost:8000/collections \
  -H "Content-Type: application/json" \
  -d '{
    "name": "tech_docs",
    "description": "Technical documentation collection"
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
