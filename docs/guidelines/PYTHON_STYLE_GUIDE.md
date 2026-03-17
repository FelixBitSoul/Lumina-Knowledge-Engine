# Python Style Guide

This style guide defines coding standards and best practices for Python code in the Lumina Knowledge Engine project, specifically for the Brain API service (`services/brain-py`).

---

## 📋 Table of Contents

- [Code Formatting](#code-formatting)
- [Type Annotations](#type-annotations)
- [Naming Conventions](#naming-conventions)
- [Project Structure](#project-structure)
- [Error Handling](#error-handling)
- [Async Programming](#async-programming)
- [Documentation](#documentation)
- [Testing](#testing)
- [FastAPI Patterns](#fastapi-patterns)
- [Anti-patterns to Avoid](#anti-patterns-to-avoid)

---

## 🎨 Code Formatting

### Mandatory Formatting

All Python code **must** be formatted with **Black**:

```bash
# Install black
pip install black

# Format single file
black main.py

# Format all files in directory
black .

# Check formatting without writing
black --check .

# Show diff
black --diff .
```

### Import Organization

Use **isort** to organize imports:

```bash
# Install isort
pip install isort

# Organize imports
isort .

# Check only
isort --check-only .
```

### Import Order

```python
# Standard library imports
import os
import sys
from datetime import datetime
from typing import List, Optional

# Third-party imports
import numpy as np
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

# Local application imports
from .config import Settings
from .models import Document
from .utils import normalize_text
```

### isort Configuration (pyproject.toml)

```toml
[tool.isort]
profile = "black"
src_paths = ["services/brain-py"]
known_first_party = ["brain"]
sections = ["FUTURE", "STDLIB", "THIRDPARTY", "FIRSTPARTY", "LOCALFOLDER"]
```

### Line Length

- Black default: 88 characters
- Project maximum: 100 characters (override if needed)

```toml
# pyproject.toml
[tool.black]
line-length = 88
target-version = ['py311']
```

---

## 🏷 Type Annotations

### Mandatory Typing

All function parameters and return types **must** be annotated:

```python
# Good - fully annotated
from typing import List, Optional

def search_documents(
    query: str,
    collection: str,
    limit: int = 10,
) -> List[SearchResult]:
    """Search documents by query string."""
    results: List[SearchResult] = []
    # ... implementation
    return results

# Bad - no type annotations
def search_documents_bad(query, collection, limit=10):
    results = []
    # ... implementation
    return results
```

### Common Type Hints

```python
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Tuple,
    Union,
)

# Basic types
def process(text: str) -> str: ...
def count() -> int: ...
def is_valid() -> bool: ...

# Optional (may be None)
def find_by_id(doc_id: str) -> Optional[Document]: ...

# Lists
def get_all() -> List[Document]: ...
def process_batch(items: List[str]) -> List[Result]: ...

# Dictionaries
def get_config() -> Dict[str, Any]: ...

# Unions (multiple possible types)
def parse_value(value: Union[str, int]) -> float: ...

# Callable (functions)
def with_retry(func: Callable[[], T], max_attempts: int = 3) -> T: ...
```

### Pydantic Models

Use Pydantic for data validation and serialization:

```python
from pydantic import BaseModel, Field, HttpUrl, validator

class Document(BaseModel):
    """Represents a crawled document."""
    
    url: HttpUrl
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)
    
    @validator('content')
    def content_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError('Content cannot be empty or whitespace')
        return v.strip()

class SearchRequest(BaseModel):
    """Search request payload."""
    
    query: str = Field(..., min_length=1, description="Search query string")
    limit: int = Field(default=10, ge=1, le=100, description="Max results to return")
    collection: str = Field(default="knowledge_base", description="Collection name")

class SearchResult(BaseModel):
    """Search result item."""
    
    score: float = Field(..., ge=0.0, le=1.0, description="Similarity score")
    title: str
    url: HttpUrl
    content: str
```

---

## 🏷 Naming Conventions

### General Rules

Follow **PEP 8** naming conventions:

| Type | Convention | Example |
|------|------------|---------|
| **Variables** | snake_case | `document_title`, `max_results` |
| **Functions** | snake_case | `fetch_document()`, `normalize_text()` |
| **Classes** | PascalCase | `DocumentProcessor`, `SearchService` |
| **Constants** | UPPER_SNAKE_CASE | `DEFAULT_TIMEOUT`, `MAX_RETRIES` |
| **Modules** | snake_case | `document_processor.py` |
| **Packages** | snake_case | `services`, `utils` |
| **Private** | _leading_underscore | `_internal_helper()` |
| **Strongly Private** | __double_underscore | `__very_private` |

### Variable Names

```python
# Good - descriptive
base_url = "https://example.com"
request_timeout = 30.0
document_count = 100
is_processing = True

# Acceptable - short scope
for i, url in enumerate(urls):
    # i and url clear in small scope

# Bad - unclear
u = "https://example.com"  # What is 'u'?
rt = 30.0                  # What's 'rt'?
data = get_data()          # What kind of data?
```

### Function Names

```python
# Good - action verbs
def fetch_document(url: str) -> Document: ...
def normalize_text(text: str) -> str: ...
def calculate_similarity(a: str, b: str) -> float: ...

# Bad - unclear names
def process(data): ...     # Too vague
def do_it(): ...            # Meaningless
def handle(x, y): ...       # Unclear parameters
```

### Class Names

```python
# Good - nouns, descriptive
class Document:
    """Represents a crawled document."""

class SearchService:
    """Service for semantic search operations."""

class EmbeddingModel:
    """Wrapper for sentence transformer model."""

# Bad - unclear
class Handler: ...
class Manager: ...
class Data: ...
```

### Constants

```python
# Module-level constants
DEFAULT_TIMEOUT = 30.0  # seconds
MAX_RETRIES = 3
EMBEDDING_DIMENSION = 384
BATCH_SIZE = 32

# Class constants
class Config:
    DEFAULT_COLLECTION = "knowledge_base"
    SUPPORTED_MODELS = ["all-MiniLM-L6-v2", "all-mpnet-base-v2"]
```

---

## 📁 Project Structure

### Standard Layout

```
services/brain-py/
├── 📁 app/                     # Application package
│   ├── 📄 __init__.py
│   ├── 📄 main.py              # FastAPI application entry
│   ├── 📄 config.py            # Configuration management
│   ├── 📁 api/                 # API routes
│   │   ├── 📄 __init__.py
│   │   ├── 📄 health.py        # Health check endpoints
│   │   ├── 📄 ingest.py        # Document ingestion
│   │   └── 📄 search.py        # Search endpoints
│   ├── 📁 core/                # Core business logic
│   │   ├── 📄 __init__.py
│   │   ├── 📄 embeddings.py    # Embedding generation
│   │   └── 📄 search.py        # Search operations
│   ├── 📁 models/              # Pydantic models
│   │   ├── 📄 __init__.py
│   │   ├── 📄 document.py
│   │   └── 📄 search.py
│   └── 📁 utils/               # Utility functions
│       ├── 📄 __init__.py
│       └── 📄 text.py
├── 📁 tests/                   # Test directory
│   ├── 📄 __init__.py
│   ├── 📄 conftest.py          # pytest fixtures
│   ├── 📄 test_health.py
│   ├── 📄 test_ingest.py
│   └── 📄 test_search.py
├── 📄 requirements.txt         # Dependencies
├── 📄 requirements-dev.txt     # Dev dependencies
├── 📄 pyproject.toml           # Project configuration
├── 📄 Dockerfile               # Container config
└── 📄 README.md                # Service documentation
```

### Module Organization

```python
# app/__init__.py
"""Brain API application package."""

__version__ = "0.1.0"
__all__ = ["create_app"]

from app.main import create_app


# app/main.py
"""FastAPI application factory."""

from fastapi import FastAPI

from app.api import health, ingest, search
from app.config import get_settings


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    settings = get_settings()
    
    app = FastAPI(
        title="Lumina Brain API",
        version=__version__,
        description="Semantic search and document ingestion API",
    )
    
    # Include routers
    app.include_router(health.router, prefix="/health", tags=["health"])
    app.include_router(ingest.router, prefix="/ingest", tags=["ingest"])
    app.include_router(search.router, prefix="/search", tags=["search"])
    
    return app
```

---

## ⚠️ Error Handling

### Exception Hierarchy

```python
# app/exceptions.py

class BrainAPIError(Exception):
    """Base exception for Brain API."""
    pass


class DocumentNotFoundError(BrainAPIError):
    """Raised when a document is not found."""
    pass


class EmbeddingError(BrainAPIError):
    """Raised when embedding generation fails."""
    pass


class SearchError(BrainAPIError):
    """Raised when search operation fails."""
    pass
```

### FastAPI Exception Handlers

```python
# app/main.py
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.exceptions import BrainAPIError, DocumentNotFoundError

app = FastAPI()

@app.exception_handler(BrainAPIError)
async def brain_api_exception_handler(
    request: Request,
    exc: BrainAPIError
) -> JSONResponse:
    """Handle Brain API exceptions."""
    return JSONResponse(
        status_code=500,
        content={
            "error": "internal_error",
            "message": str(exc),
            "type": exc.__class__.__name__,
        },
    )

@app.exception_handler(DocumentNotFoundError)
async def not_found_handler(
    request: Request,
    exc: DocumentNotFoundError
) -> JSONResponse:
    """Handle document not found."""
    return JSONResponse(
        status_code=404,
        content={
            "error": "not_found",
            "message": str(exc),
        },
    )
```

### Error Handling Pattern

```python
# Good - explicit error handling
async def search_documents(
    query: str,
    collection: str,
    limit: int = 10,
) -> List[SearchResult]:
    """Search documents with error handling."""
    try:
        # Validate inputs
        if not query.strip():
            raise ValueError("Query cannot be empty")
        
        if limit < 1 or limit > 100:
            raise ValueError("Limit must be between 1 and 100")
        
        # Perform search
        results = await perform_search(query, collection, limit)
        return results
        
    except ValueError as e:
        # Re-raise validation errors
        raise
    except Exception as e:
        # Wrap unexpected errors
        logger.error(f"Search failed: {e}")
        raise SearchError(f"Search operation failed: {e}") from e


# Good - FastAPI endpoint with HTTPException
from fastapi import HTTPException

@app.get("/search")
async def search(
    query: str,
    limit: int = 10,
) -> SearchResponse:
    """Search endpoint."""
    if not query.strip():
        raise HTTPException(
            status_code=400,
            detail="Query parameter is required and cannot be empty"
        )
    
    try:
        results = await search_documents(query, limit=limit)
        return SearchResponse(results=results)
    except SearchError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Search failed: {str(e)}"
        )
```

---

## 🔄 Async Programming

### Async Function Guidelines

```python
# Always use async for I/O operations
async def fetch_document(url: str) -> Document:
    """Fetch document asynchronously."""
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            content = await response.text()
            return Document(content=content)

# Use sync for CPU-bound operations (but consider ProcessPoolExecutor)
def embed_text(text: str) -> np.ndarray:
    """Generate embedding (CPU-bound, use sync)."""
    return model.encode(text)

# Async wrapper for CPU-bound operations
async def embed_text_async(text: str) -> np.ndarray:
    """Generate embedding in thread pool."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, embed_text, text)
```

### Concurrent Operations

```python
import asyncio
from typing import List

async def process_batch(documents: List[Document]) -> List[Embedding]:
    """Process documents concurrently."""
    # Create tasks
    tasks = [
        embed_document_async(doc)
        for doc in documents
    ]
    
    # Execute concurrently
    embeddings = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Handle results
    results = []
    for doc, emb in zip(documents, embeddings):
        if isinstance(emb, Exception):
            logger.error(f"Failed to embed {doc.url}: {emb}")
            continue
        results.append(emb)
    
    return results


async def embed_document_async(doc: Document) -> Embedding:
    """Embed single document with timeout."""
    try:
        return await asyncio.wait_for(
            embed_text_async(doc.content),
            timeout=30.0
        )
    except asyncio.TimeoutError:
        raise EmbeddingError(f"Timeout embedding {doc.url}")
```

---

## 📝 Documentation

### Google Style Docstrings

```python
def search_documents(
    query: str,
    collection: str = "knowledge_base",
    limit: int = 10,
) -> List[SearchResult]:
    """Search documents using semantic similarity.
    
    Performs vector similarity search using the query embedding
    and returns the most similar documents from the collection.
    
    Args:
        query: Search query string. Must be non-empty.
        collection: Name of the vector collection to search.
            Defaults to "knowledge_base".
        limit: Maximum number of results to return.
            Must be between 1 and 100. Defaults to 10.
    
    Returns:
        List of search results ordered by relevance score
        (highest first). Empty list if no matches found.
    
    Raises:
        ValueError: If query is empty or limit is out of range.
        SearchError: If the search operation fails.
        CollectionNotFoundError: If the collection doesn't exist.
    
    Example:
        >>> results = await search_documents(
        ...     query="python tutorial",
        ...     collection="programming",
        ...     limit=5
        ... )
        >>> print(results[0].title)
        'Python Basics'
    """
    # Implementation...
```

### Type Documentation

```python
from typing import TypeVar, Generic

T = TypeVar("T")

class PaginatedResponse(Generic[T]):
    """Generic paginated response wrapper.
    
    Attributes:
        items: List of items in current page.
        total: Total number of items across all pages.
        page: Current page number (1-indexed).
        page_size: Number of items per page.
        has_next: Whether more pages exist.
        has_previous: Whether previous pages exist.
    """
    
    items: List[T]
    total: int
    page: int
    page_size: int
    has_next: bool
    has_previous: bool
```

---

## 🧪 Testing

### pytest Standards

```python
# tests/test_search.py
import pytest
from httpx import AsyncClient

from app.main import create_app


@pytest.fixture
async def client():
    """Create test client."""
    app = create_app()
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


class TestSearchEndpoint:
    """Test suite for search endpoint."""
    
    async def test_search_success(self, client: AsyncClient):
        """Test successful search."""
        response = await client.get("/search?query=python&limit=5")
        
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert len(data["results"]) <= 5
    
    async def test_search_empty_query(self, client: AsyncClient):
        """Test validation of empty query."""
        response = await client.get("/search?query=")
        
        assert response.status_code == 400
        assert "error" in response.json()
    
    async def test_search_invalid_limit(self, client: AsyncClient):
        """Test validation of invalid limit."""
        response = await client.get("/search?query=test&limit=999")
        
        assert response.status_code == 422  # Validation error
    
    @pytest.mark.parametrize("query", [
        "python",
        "machine learning",
        "docker compose",
    ])
    async def test_search_various_queries(self, client: AsyncClient, query: str):
        """Test search with various queries."""
        response = await client.get(f"/search?query={query}&limit=3")
        assert response.status_code == 200
```

### Fixtures

```python
# tests/conftest.py
import pytest
from unittest.mock import Mock

from app.core.embeddings import EmbeddingService


@pytest.fixture
def mock_qdrant():
    """Mock Qdrant client."""
    client = Mock()
    client.search.return_value = []
    return client


@pytest.fixture
def embedding_service(mock_qdrant):
    """Create embedding service with mock client."""
    service = EmbeddingService(qdrant_client=mock_qdrant)
    return service


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    import asyncio
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
```

### Mocking

```python
from unittest.mock import AsyncMock, patch, MagicMock

async def test_search_with_mocked_embeddings():
    """Test search with mocked embedding service."""
    # Mock the embedding model
    mock_model = MagicMock()
    mock_model.encode.return_value = np.random.rand(384)
    
    with patch("app.core.embeddings.model", mock_model):
        results = await search_documents("test query")
        
        # Verify model was called
        mock_model.encode.assert_called_once_with("test query")
        assert len(results) >= 0
```

---

## 🎯 FastAPI Patterns

### Dependency Injection

```python
from fastapi import Depends, FastAPI
from functools import lru_cache

# app/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    model_name: str = "all-MiniLM-L6-v2"
    
    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# app/dependencies.py
from app.core.embeddings import EmbeddingService

async def get_embedding_service(
    settings: Settings = Depends(get_settings)
) -> EmbeddingService:
    """Dependency for embedding service."""
    return EmbeddingService(
        model_name=settings.model_name,
    )


# app/api/search.py
from fastapi import APIRouter, Depends

router = APIRouter()

@router.get("/")
async def search(
    query: str,
    service: EmbeddingService = Depends(get_embedding_service),
) -> SearchResponse:
    """Search endpoint with dependency injection."""
    results = await service.search(query)
    return SearchResponse(results=results)
```

### Request/Response Models

```python
from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI()

# Request model
class IngestRequest(BaseModel):
    """Document ingestion request."""
    url: HttpUrl
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=10)
    metadata: Optional[Dict[str, Any]] = None

# Response model
class IngestResponse(BaseModel):
    """Document ingestion response."""
    status: str = Field(..., pattern="^(success|error)$")
    document_id: Optional[str] = None
    message: Optional[str] = None
    processing_time_ms: float

@app.post("/ingest", response_model=IngestResponse)
async def ingest_document(request: IngestRequest) -> IngestResponse:
    """Ingest a document into the knowledge base."""
    start_time = time.time()
    
    try:
        doc_id = await process_document(request)
        
        return IngestResponse(
            status="success",
            document_id=doc_id,
            processing_time_ms=(time.time() - start_time) * 1000,
        )
    except Exception as e:
        return IngestResponse(
            status="error",
            message=str(e),
            processing_time_ms=(time.time() - start_time) * 1000,
        )
```

---

## 🚫 Anti-patterns to Avoid

### 1. Missing Type Annotations

```python
# Bad
def process(data):
    return data * 2

# Good
from typing import Union

def process(data: Union[int, float]) -> Union[int, float]:
    return data * 2
```

### 2. Mutable Default Arguments

```python
# Bad - mutable default
def add_item(item, items=[]):
    items.append(item)
    return items

# Good - None default
def add_item(item: str, items: Optional[List[str]] = None) -> List[str]:
    if items is None:
        items = []
    items.append(item)
    return items
```

### 3. Bare Except Clauses

```python
# Bad
try:
    process()
except:  # Catches everything including KeyboardInterrupt!
    pass

# Good
try:
    process()
except ValueError as e:
    logger.error(f"Invalid value: {e}")
except Exception as e:
    logger.exception("Unexpected error")
    raise
```

### 4. Using print() for Logging

```python
# Bad
print(f"Processing {document.url}")

# Good
import logging

logger = logging.getLogger(__name__)
logger.info(f"Processing {document.url}")
```

### 5. Unnecessary List/Dict Comprehensions

```python
# Bad - side effects in comprehension
[process(doc) for doc in documents]

# Good - explicit loop
for doc in documents:
    process(doc)

# Good - comprehension for transformation
urls = [doc.url for doc in documents if doc.is_valid()]
```

---

## 📚 Additional Resources

- [PEP 8 -- Style Guide for Python Code](https://pep8.org/)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [pytest Documentation](https://docs.pytest.org/)

---

## 🛠 Tools Configuration

### pyproject.toml

```toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "brain-py"
version = "0.1.0"
requires-python = ">=3.11"

[tool.black]
line-length = 88
target-version = ['py311']
include = '\.pyi?$'
extend-exclude = '''
/(
    \.git
  | \.venv
  | build
  | dist
)/
'''

[tool.isort]
profile = "black"
src_paths = ["services/brain-py"]

[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
strict = true

[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"
```

---

<p align="center">
  Write clean, typed, Pythonic code. 🐍
</p>
