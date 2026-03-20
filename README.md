# Lumina Knowledge Engine 🔍

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Go Version](https://img.shields.io/badge/Go-1.22+-00ADD8?style=flat&logo=go&logoColor=white)](https://golang.org/)
[![Python Version](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python&logoColor=white)](https://python.org/)
[![Next.js](https://img.shields.io/badge/Next.js-15-000000?style=flat&logo=next.js&logoColor=white)](https://nextjs.org/)

A modern **RAG (Retrieval-Augmented Generation)** system for semantic document search and knowledge management. Built with Go, Python, and Next.js for high performance and scalability.

[🚀 Quick Start](#quick-start) • [📖 Documentation](#documentation) • [🏗 Architecture](#system-architecture) • [🐳 Docker](#docker-deployment)

---

## ✨ Features

- **🔍 Semantic Search**: AI-powered vector similarity search using sentence transformers
- **🕷️ Web Crawler**: High-performance Go-based crawler with configurable depth and rate limiting
- **🧠 Vector Embeddings**: All-MiniLM-L6-v2 model for 384-dimensional semantic embeddings
- **⚡ High Performance**: Async processing, concurrent crawling, and optimized vector storage
- **🎨 Modern UI**: Next.js 15 frontend with Tailwind CSS and dark/light theme support
- **🐳 Easy Deployment**: One-command Docker Compose deployment
- **📊 RESTful API**: OpenAPI-documented endpoints for easy integration
- **🔧 Configurable**: YAML-based configuration for crawling tasks and system settings

---

## 📸 Project Screenshots

1. **Search Interface**
   ![Search Interface](https://github.com/user-attachments/assets/601017ad-95d3-449b-9869-ad02c40b17d7)
   ![Sidebar Interface](https://github.com/user-attachments/assets/d5dd3be5-95d7-4012-ad33-92eb65816f1b)

2. **Chat Interface**
   ![Chat Interface](https://github.com/user-attachments/assets/2c150b17-a56e-41da-ade4-8b9155b3bedc)

---

## 🏗 System Architecture

```
┌─────────────────┐      ┌──────────────────┐      ┌─────────────────┐
│   🕷️ Crawler    │──────▶│   🧠 Brain API   │──────▶│  💾 Qdrant DB   │
│   (Go + Colly)  │      │ (Python/FastAPI) │      │  (Vector Store) │
└─────────────────┘      └──────────────────┘      └─────────────────┘
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

---

## 🛠 Tech Stack

- **🐭 Backend**: Go (Colly crawler), Python (FastAPI, Qdrant-Client, sentence-transformers)
- **🤖 AI/ML**: HuggingFace Transformers, all-MiniLM-L6-v2 embeddings
- **⚛️ Frontend**: Next.js 15, React 19, Tailwind CSS v4, Lucide Icons
- **💾 Database**: Qdrant Vector Database (384-dimensional vectors)
- **🐳 Infrastructure**: Docker, Docker Compose
- **📊 Monitoring**: Health checks, structured logging

---

## 🚀 Quick Start

### Option 1: Docker Compose (Recommended)

```bash
# Clone repository
git clone https://github.com/FelixBitSoul/lumina-knowledge-engine.git
cd lumina-knowledge-engine/deployments

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

### Option 2: Local Development

```bash
# 1. Start Qdrant
docker-compose -f deployments/docker-compose.yaml up -d qdrant

# 2. Start Brain API (Python 3.11+)
cd services/brain-py
pip install -r requirements.txt
python main.py

# 3. Start Portal (Node.js 18+)
cd services/portal-next
npm install
npm run dev

# 4. Optional: Run Crawler (Go 1.22+)
cd services/crawler-go
go run ./cmd/crawler
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
│   ├── 🧠 brain-py/           # Python FastAPI service
│   │   ├── main.py            # API endpoints
│   │   ├── requirements.txt   # Python dependencies
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
- **Brain API Details**: [services/brain-py/README.md](services/brain-py/README.md)
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

- Go 1.22+
- Python 3.11+
- Node.js 18+
- Docker 20.10+

### Local Development Setup

```bash
# Install dependencies
make install

# Run tests
make test

# Start development servers
make dev
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
