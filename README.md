# Lumina Knowledge Engine 🔍

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Go Version](https://img.shields.io/badge/Go-1.24+-00ADD8?style=flat&logo=go&logoColor=white)](https://golang.org/)
[![Python Version](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python&logoColor=white)](https://python.org/)
[![Next.js](https://img.shields.io/badge/Next.js-15.0.2-000000?style=flat&logo=next.js&logoColor=white)](https://nextjs.org/)

A modern **RAG (Retrieval-Augmented Generation)** system for semantic document search and knowledge management. Built with Go, Python, and Next.js for high performance and scalability.

[🚀 Quick Start](#quick-start) • [📖 Documentation](#documentation) • [🏗 Architecture](#system-architecture) • [🐳 Docker](#docker-deployment)

---

## ✨ Features

- **🔍 Semantic Search**: AI-powered vector similarity search with relevance reranking
- **💬 Conversational AI**: Context-aware chat interface with query rewriting
- **🕷️ Web Crawler**: High-performance Go-based crawler with configurable depth and rate limiting
- **🧠 Vector Embeddings**: All-MiniLM-L6-v2 model for 384-dimensional semantic embeddings
- **🎯 Query Rewriting**: LLM-based context processing for multi-turn conversations
- **📊 Reranking**: Cross-Encoder based relevance optimization
- **🔄 Multi-Collection Search**: Search across multiple vector collections
- **⚡ High Performance**: Async processing, concurrent crawling, and optimized vector storage
- **🎨 Modern UI**: Next.js 15 frontend with Tailwind CSS and dark/light theme support
- **🐳 Easy Deployment**: One-command Docker Compose deployment
- **📊 RESTful API**: OpenAPI-documented endpoints for easy integration
- **🔧 Configurable**: YAML-based configuration for crawling tasks and system settings
- **⚡ Async Document Processing**: Celery-based background task processing for large files
- **🌐 WebSocket Notifications**: Real-time document processing updates
- **📦 MinIO Integration**: Object storage for original documents with preview support
- **🔄 Task Management**: Task status tracking and monitoring
- **🗑️ Document Management**: Support for document deletion and cleanup

---

## 📸 Project Screenshots

1. **Search Interface**
   ![Search Interface](https://github.com/user-attachments/assets/869c41b2-e003-418d-b912-ae6344df0000)
   ![Sidebar Interface](https://github.com/user-attachments/assets/d5dd3be5-95d7-4012-ad33-92eb65816f1b)

2. **Chat Interface**
   ![Chat Interface](https://github.com/user-attachments/assets/15a33bd8-4cff-42cb-bebe-39c09708a33c)

3. **Upload Interface**
   ![Upload Interface](https://github.com/user-attachments/assets/f9536444-0351-4f8b-8b3f-5969d6aa800f)
   ![Upload success Interface](https://github.com/user-attachments/assets/e77756f3-004b-453f-a86c-0b360b0fb7c7)
---

## 🏗 System Architecture

```
┌─────────────────┐      ┌──────────────────┐      ┌─────────────────┐
│   🕷️ Crawler    │──────▶│   🧠 Brain API   │──────▶│  💾 Qdrant DB   │
│   (Go + Colly)  │      │ (Python/FastAPI) │      │  (Vector Store) │
└─────────────────┘      └──────────────────┘      └─────────────────┘
                               │       ▲
                               ▼       │
                        ┌──────────────────┐
                        │  📦 MinIO       │
                        │  (Object Store) │
                        └──────────────────┘
                               │       ▲
                               ▼       │
                        ┌──────────────────┐
                        │  📡 Redis        │
                        │  (Task Queue)   │
                        └──────────────────┘
                               │       ▲
                               ▼       │
                        ┌──────────────────┐
                        │  🚀 Celery       │
                        │  (Workers)      │
                        └──────────────────┘
                               │
                               ▼
                        ┌──────────────────┐
                        │  🌐 Portal       │
                        │  (Next.js 15)    │
                        └──────────────────┘
```

### Core Services

| Service | Technology | Purpose | Port |
|---------|------------|---------|------|
| **Crawler** | Go 1.22 + Colly | Web scraping & content extraction | - |
| **Brain API** | Python 3.11 + FastAPI | Vector embedding & semantic search | 8000 |
| **Vector DB** | Qdrant | High-performance vector storage | 6333/6334 |
| **Portal** | Next.js 15 + Tailwind | User interface & search frontend | 3000 |
| **Redis** | Redis 7+ | Task queue & Pub/Sub | 6379 |
| **MinIO** | MinIO | Object storage for documents | 9000 |
| **Celery** | Celery 5+ | Background task processing | - |

---

## 🛠 Tech Stack

### Core Technologies
- **🐭 Backend**: Go 1.24 (Colly 2.2.0 crawler), Python 3.11+ (FastAPI 0.104+)
- **🤖 AI/ML**: sentence-transformers 2.2+, Qdrant-Client 1.6+, OpenAI 1.0+
- **⚛️ Frontend**: Next.js 15.0.2, React 19.0.0, Tailwind CSS v4, Lucide Icons 0.577.0
- **💾 Database**: Qdrant Vector Database (384-dimensional vectors)
- **🐳 Infrastructure**: Docker, Docker Compose
- **📊 Monitoring**: Health checks, structured logging
- **🔧 AI Services**: Query rewriting, relevance reranking, conversational AI

### Detailed Dependencies
- **Crawler (Go)**: Colly v2.2.0, go-readability, goquery, godotenv
- **Brain API (Python)**: FastAPI, uvicorn, sentence-transformers, qdrant-client, pydantic, openai, PyMuPDF, celery, redis, minio
- **Portal (Next.js)**: React 19, @tanstack/react-query, zustand, shadcn, tailwind-merge, class-variance-authority, clsx, next-themes, radix-ui, tw-animate-css, lucide-react
- **Infrastructure**: Redis 7+, MinIO, Celery 5+

---

## 🚀 Quick Start

### Docker Compose (Recommended)

```bash
# Clone repository
git clone https://github.com/FelixBitSoul/lumina-knowledge-engine.git
cd lumina-knowledge-engine/deployments

# Create .env file (based on .env.example)
cp .env.example .env

# Start all services
docker-compose up -d

# Verify services
curl http://localhost:8000/health  # Brain API
curl http://localhost:3000         # Portal
curl http://localhost:6333/health  # Qdrant
```

Access the services:
- **🌐 Portal**: http://localhost:3000
- **📖 API Docs**: http://localhost:8000/docs
- **🔍 Search**: Use the portal or API directly
- **💽 MinIO Console**: http://localhost:9001 (login with minioadmin:minioadmin)

### Start with Crawler

```bash
# Start all services including crawler
cd deployments
docker-compose --profile crawler up -d
```

---

## 📂 Project Structure

```
lumina-knowledge-engine/
├── 📁 services/
│   ├── 🕷️ crawler-go/          # Go-based web crawler
│   │   ├── cmd/crawler/       # CLI entry point
│   │   ├── internal/          # Core packages
│   │   ├── crawler-config.yaml        # Crawler configuration
│   │   └── README.md          # Crawler documentation
│   │
│   ├── 🧠 lumina-brain/       # Python FastAPI service
│   │   ├── src/               # Source code
│   │   ├── pyproject.toml     # Project configuration
│   │   └── README.md          # API documentation
│   │
│   └── 🌐 portal-next/        # Next.js frontend
│       ├── src/app/           # Next.js 15 app router
│       ├── package.json       # Node dependencies
│       └── README.md          # Frontend documentation
│
├── 📁 deployments/
│   ├── docker-compose.yaml    # Docker orchestration
│   └── qdrant_data/           # Vector database storage
│
├── 📁 docs/                   # Comprehensive documentation
│   ├── architecture/          # System design docs
│   ├── api/                   # API specifications
│   ├── deployment/            # Deployment guides
│   └── README.md              # Documentation overview
│
├── 📄 README.md               # This file
├── 📄 AI_COLLABORATION_GUIDE.md  # AI assistant guidelines
└── 📄 LICENSE                 # MIT License
```

---

## � Documentation

### 📚 Core Documentation

| Document | Description |
|----------|-------------|
| [System Architecture](docs/architecture/system-overview.md) | High-level design & component interactions |
| [API Documentation](docs/api/brain-api.md) | Brain API endpoints & OpenAPI specs |
| [Crawler Config](docs/api/crawler-config.md) | YAML configuration reference |
| [Deployment Guides](docs/deployment/) | Docker, local, and cloud deployment |
| [Portal Integration](docs/api/portal-integration.md) | Frontend integration guide |
| [Technical Guidelines](docs/guidelines/) | Style guides, tech stack, and coding standards |
| [Product Requirements](docs/PRD.md) | Features, user stories, and roadmap |

### 🔗 Quick Links

- **Crawler Details**: [services/crawler-go/README.md](services/crawler-go/README.md)
- **Brain API Details**: [services/lumina-brain/README.md](services/lumina-brain/README.md)
- **Portal Details**: [services/portal-next/README.md](services/portal-next/README.md)

---

## 🐳 Docker Deployment

### Production-Ready Compose

The `deployments/docker-compose.yaml` includes:

- ✅ **Qdrant**: Vector database with persistent storage
- ✅ **Brain API**: Python FastAPI with health checks
- ✅ **Portal**: Next.js frontend with API integration
- ✅ **Crawler** (optional): Go crawler with profiles support
- ✅ **Custom Network**: Isolated bridge network
- ✅ **Named Volumes**: Persistent data storage

### Usage

```bash
# Start core services
docker-compose up -d

# Start with crawler
docker-compose --profile crawler up -d

# View logs
docker-compose logs -f [service-name]

# Stop all
docker-compose down
```

See [Docker Deployment Guide](docs/deployment/docker-deployment.md) for detailed instructions.

---

## 🎯 Usage Examples

### 1. Crawl Documents

```bash
# Configure crawler (edit services/crawler-go/crawler-config.yaml)
tasks:
  - name: "tech-docs"
    seeds: ["https://docs.docker.com/get-started/"]
    max_depth: 2
    allowed_domains: ["docs.docker.com"]
    rate_limit:
      requests_per_minute: 60

# Run crawler
cd services/crawler-go
go run ./cmd/crawler
```

### 2. Search via API

```bash
# Semantic search
curl -X GET "http://localhost:8000/search?query=how%20to%20install%20docker&limit=5"

# Response
{
  "query": "how to install docker",
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

### 3. Ingest Documents

```bash
curl -X POST http://localhost:8000/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com/docs",
    "title": "Example Documentation",
    "content": "This is the content to index..."
  }'
```

---

## ⚙️ Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `QDRANT_HOST` | localhost | Vector database host |
| `QDRANT_PORT` | 6333 | Vector database port |
| `MODEL_NAME` | all-MiniLM-L6-v2 | Embedding model |
| `NEXT_PUBLIC_API_URL` | http://localhost:8000 | Brain API URL |
| `BRAIN_INGEST_URL` | http://localhost:8000/ingest | Ingestion endpoint |
| `LOG_LEVEL` | info | Logging level |

### Crawler Configuration

See [Crawler Config Reference](docs/api/crawler-config.md) for detailed YAML configuration options.

---

## 🧪 Development

### Prerequisites

- Docker 20.10+
- Docker Compose 1.29+
- Git

### Development Workflow

```bash
# Start all services in development mode (uses docker-compose.override.yml)
cd deployments
docker-compose up -d

# Make code changes
# Edit files in services/ directory - changes will be automatically reflected due to volume mounting

# Run tests using Docker Compose
cd deployments
# Run Brain API tests
docker-compose run --rm brain-api pytest
# Run Crawler tests
docker-compose run --rm crawler go test ./...
# Run Portal tests
docker-compose run --rm portal npm test

# View logs
cd deployments
docker-compose logs -f brain-api

# Stop services
cd deployments
docker-compose down
```

### Running Unit Tests (UT)

All unit tests should be run using Docker Compose to ensure consistent environment:

```bash
# Run all tests
cd deployments
docker-compose run --rm brain-api pytest
docker-compose run --rm crawler go test ./...
docker-compose run --rm portal npm test

# Run specific test files
cd deployments
docker-compose run --rm brain-api pytest tests/test_search.py
docker-compose run --rm crawler go test ./internal/crawler
```

See [Local Setup Guide](docs/deployment/local-setup.md) for detailed instructions.

---

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### AI Collaboration

This project follows the [AI Collaboration Guide](AI_COLLABORATION_GUIDE.md) for AI-assisted development.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Qdrant**: High-performance vector database
- **Sentence Transformers**: Efficient text embeddings
- **Colly**: Elegant Go web scraping framework
- **FastAPI**: Modern, fast Python web framework
- **Next.js**: React framework for production

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/FelixBitSoul/lumina-knowledge-engine/issues)
- **Documentation**: [Full Documentation](docs/)
- **Discussions**: [GitHub Discussions](https://github.com/FelixBitSoul/lumina-knowledge-engine/discussions)

---

<p align="center">
  Built with ❤️ using Go, Python, and Next.js
</p>
