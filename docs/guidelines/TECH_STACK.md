# Lumina Knowledge Engine - Technical Stack

A comprehensive overview of the technology choices, architecture, and development standards for the Lumina Knowledge Engine project.

---

## 📋 Table of Contents

- [System Architecture Overview](#system-architecture-overview)
- [Service Technology Stack](#service-technology-stack)
- [Infrastructure & DevOps](#infrastructure--devops)
- [Development Tooling](#development-tooling)
- [Version Compatibility](#version-compatibility)
- [Technology Rationale](#technology-rationale)
- [Architecture Decisions](#architecture-decisions)
- [Future Roadmap](#future-roadmap)

---

## 🏗 System Architecture Overview

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Lumina Knowledge Engine                   │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌─────────────┐      ┌──────────────┐      ┌─────────────┐  │
│  │  🕷️ Crawler │──────▶│  🧠 Brain API│──────▶│ 💾 Vector DB│  │
│  │    (Go)     │      │  (Python)    │      │  (Qdrant)   │  │
│  └─────────────┘      └──────────────┘      └─────────────┘  │
│                               │                               │
│                               ▼                               │
│                        ┌──────────────┐                      │
│                        │  🌐 Portal   │                      │
│                        │  (Next.js)   │                      │
│                        └──────────────┘                      │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

```
1. Crawler discovers and fetches web content
2. Content is cleaned and sent to Brain API
3. Brain API generates vector embeddings
4. Vectors are stored in Qdrant
5. Portal queries Brain API for semantic search
6. Results are displayed to users
```

---

## 🛠 Service Technology Stack

### 1. Crawler Service (`services/crawler-go`)

| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| **Language** | Go | 1.22+ | High-performance concurrent crawling |
| **Framework** | Colly | v2.1.0+ | Web scraping framework |
| **Extraction** | go-readability | latest | Article content extraction |
| **HTML Parsing** | goquery (PuerkitoBio) | v1.8.0+ | DOM manipulation |
| **Configuration** | yaml.v3 | v3.0.1+ | YAML configuration parsing |
| **CLI** | Standard `flag` package | - | Command-line interface |

**Key Libraries:**
- `github.com/gocolly/colly/v2` - Async web crawling
- `github.com/go-shiori/go-readability` - Content extraction
- `github.com/PuerkitoBio/goquery` - jQuery-like syntax for Go
- `gopkg.in/yaml.v3` - YAML parsing

### 2. Brain API Service (`services/brain-py`)

| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| **Language** | Python | 3.11+ | AI/ML service implementation |
| **Framework** | FastAPI | 0.104.0+ | High-performance API framework |
| **Server** | Uvicorn | 0.24.0+ | ASGI server |
| **ML/AI** | sentence-transformers | 2.2.0+ | Text embedding models |
| **Vector DB Client** | qdrant-client | 1.6.0+ | Qdrant integration |
| **Data Validation** | Pydantic | 2.5.0+ | Request/response validation |
| **Environment** | python-dotenv | 1.0.0+ | Configuration management |

**Key Libraries:**
- `fastapi` - Modern, fast web framework
- `uvicorn[standard]` - ASGI server with optimizations
- `sentence-transformers` - HuggingFace embedding models
- `qdrant-client` - Vector database client
- `pydantic` - Data validation and settings
- `numpy` - Numerical operations

**Embedding Model:**
- **Primary**: `all-MiniLM-L6-v2` (384 dimensions)
- **Alternatives**: `all-mpnet-base-v2`, `paraphrase-multilingual-MiniLM-L12-v2`

### 3. Portal Frontend (`services/portal-next`)

| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| **Framework** | Next.js | 15.0.0+ | React framework with App Router |
| **Language** | TypeScript | 5.0.0+ | Type-safe JavaScript |
| **UI Library** | React | 19.0.0+ | Component-based UI |
| **Styling** | Tailwind CSS | 4.0.0+ | Utility-first CSS |
| **Icons** | Lucide React | latest | Icon library |
| **Font** | Geist (Vercel) | via next/font | Optimized font loading |

**Key Dependencies:**
- `next` - React framework
- `react` & `react-dom` - UI library
- `tailwindcss` - CSS framework
- `lucide-react` - Icons
- `typescript` - Type checking
- `eslint` - Code linting

### 4. Vector Database

| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| **Database** | Qdrant | 1.7.4+ | Vector similarity search |
| **Storage** | Persistent Volume | - | Data persistence |
| **Protocols** | HTTP REST, gRPC | - | API access |

**Features:**
- HNSW indexing for approximate nearest neighbors
- Metadata filtering
- Collection management
- Horizontal scalability (future)

---

## 🏭 Infrastructure & DevOps

### Container Orchestration

| Tool | Version | Purpose |
|------|---------|---------|
| **Docker** | 20.10+ | Container runtime |
| **Docker Compose** | 2.0+ | Multi-container orchestration |
| **BuildKit** | Built-in | Advanced image building |

### Cloud Platforms (Optional)

| Platform | Services | Purpose |
|------------|----------|---------|
| **AWS** | EKS, ECS, RDS, ElastiCache | Production deployment |
| **Google Cloud** | GKE, Cloud Run, Cloud SQL | Alternative cloud option |
| **Azure** | AKS, Container Instances | Enterprise deployment |

### CI/CD

| Tool | Purpose |
|------|---------|
| **GitHub Actions** | Automated testing and deployment |
| **Terraform** | Infrastructure as Code (cloud deployments) |

---

## 🔧 Development Tooling

### Code Quality Tools

#### Go
| Tool | Purpose | Command |
|------|---------|---------|
| `gofmt` | Code formatting | `gofmt -w .` |
| `goimports` | Import management | `goimports -w .` |
| `golangci-lint` | Comprehensive linting | `golangci-lint run` |
| `go vet` | Static analysis | `go vet ./...` |
| `go test` | Testing | `go test ./...` |

#### Python
| Tool | Purpose | Command |
|------|---------|---------|
| `black` | Code formatting | `black .` |
| `isort` | Import sorting | `isort .` |
| `flake8` | Style linting | `flake8 .` |
| `mypy` | Type checking | `mypy .` |
| `pytest` | Testing | `pytest` |

#### TypeScript/JavaScript
| Tool | Purpose | Command |
|------|---------|---------|
| `prettier` | Code formatting | `prettier --write .` |
| `eslint` | Linting | `eslint . --fix` |
| `tsc` | Type checking | `tsc --noEmit` |
| `jest` | Testing | `jest` |

### Development Environment

#### Recommended IDEs
- **Go**: GoLand, VS Code with Go extension
- **Python**: PyCharm, VS Code with Python extension
- **TypeScript**: VS Code, WebStorm

#### VS Code Extensions
- Go: `golang.go`
- Python: `ms-python.python`, `ms-python.black-formatter`
- TypeScript: `esbenp.prettier-vscode`, `dbaeumer.vscode-eslint`
- Docker: `ms-vscode.vscode-docker`
- YAML: `redhat.vscode-yaml`

### Version Control

| Tool | Purpose |
|------|---------|
| **Git** | Source control |
| **GitHub** | Repository hosting |
| **Conventional Commits** | Commit message standard |

---

## 📊 Version Compatibility

### Minimum Versions

| Component | Minimum Version | Recommended |
|-----------|----------------|-------------|
| **Go** | 1.22 | 1.22+ |
| **Python** | 3.11 | 3.11+ |
| **Node.js** | 18 LTS | 20 LTS |
| **Docker** | 20.10 | Latest |
| **Docker Compose** | 2.0 | Latest |

### Version Constraints

```yaml
# Go (go.mod)
go 1.22

# Python (requirements.txt)
python_requires = >=3.11

# Node.js (package.json)
engines: {
  "node": ">=18.0.0",
  "npm": ">=9.0.0"
}
```

---

## 🤔 Technology Rationale

### Why Go for the Crawler?

**Advantages:**
- ⚡ **Performance**: Compiled, fast execution for high-throughput crawling
- 🏃 **Concurrency**: Goroutines for efficient parallel processing
- 📦 **Single Binary**: Easy deployment with minimal dependencies
- 🕸️ **Colly Framework**: Mature, feature-rich web scraping framework

**Use Cases:**
- High-concurrency HTTP fetching
- Link extraction and URL normalization
- Rate-limited, polite crawling

### Why Python for the Brain API?

**Advantages:**
- 🤖 **AI/ML Ecosystem**: Rich libraries for embeddings and ML
- 🚀 **FastAPI**: High-performance async framework
- 📝 **Developer Experience**: Clear, readable code for complex logic
- 🔬 **Research Friendly**: Easy experimentation with models

**Use Cases:**
- Vector embedding generation
- Semantic search logic
- Text preprocessing and normalization
- API endpoint implementation

### Why Next.js for the Portal?

**Advantages:**
- ⚡ **Performance**: Server-side rendering, static generation
- 🎯 **SEO**: Built-in SEO optimizations
- 🛠 **Developer Experience**: TypeScript, hot reload, rich ecosystem
- 📱 **Responsive**: Tailwind CSS for modern UI

**Use Cases:**
- Modern web interface
- Server-side API integration
- Static and dynamic content

### Why Qdrant?

**Advantages:**
- 🎯 **Purpose Built**: Vector database optimized for similarity search
- ⚡ **Performance**: HNSW indexing for fast approximate search
- 🐳 **Easy Deployment**: Docker-first approach
- 📈 **Scalable**: Horizontal scaling support

**Use Cases:**
- Vector storage (384 dimensions)
- Cosine similarity search
- Metadata filtering

---

## 🏛 Architecture Decisions

### ADR 1: Microservices Architecture

**Decision**: Separate services for crawling, processing, and presentation.

**Rationale:**
- Independent scaling of components
- Technology diversity for optimal solutions
- Fault isolation
- Team autonomy

### ADR 2: Language Separation

**Decision**: Go for crawler, Python for AI, TypeScript for frontend.

**Rationale:**
- Go: Performance-critical network operations
- Python: Rich AI/ML ecosystem
- TypeScript: Type-safe frontend development

### ADR 3: RESTful API + gRPC (Future)

**Decision**: REST for external, gRPC for internal (planned).

**Rationale:**
- REST: Human-readable, easy debugging
- gRPC: High-performance internal communication (future optimization)

### ADR 4: Docker-First Deployment

**Decision**: Docker as primary deployment method.

**Rationale:**
- Environment consistency
- Easy local development
- Cloud portability
- Simple scaling

---

## 🚀 Future Roadmap

### Planned Technologies

| Technology | Purpose | Timeline |
|------------|---------|----------|
| **Redis** | Caching layer | Q2 2024 |
| **PostgreSQL** | Metadata storage | Q2 2024 |
| **gRPC** | Internal service communication | Q3 2024 |
| **Kafka/RabbitMQ** | Event streaming | Q3 2024 |
| **Prometheus** | Metrics collection | Q3 2024 |
| **Grafana** | Monitoring dashboards | Q3 2024 |
| **Elasticsearch** | Full-text search (hybrid) | Q4 2024 |
| **Kubernetes** | Production orchestration | Q4 2024 |

### Version Upgrades

| Component | Current | Target | Timeline |
|-----------|---------|--------|----------|
| **Go** | 1.22 | 1.23 | Q3 2024 |
| **Python** | 3.11 | 3.12 | Q3 2024 |
| **Next.js** | 15 | Latest | Ongoing |
| **Qdrant** | 1.7.4 | Latest | Ongoing |

---

## 📚 Related Documentation

- **Contributing Guide**: [CONTRIBUTING.md](CONTRIBUTING.md)
- **Go Style Guide**: [GO_STYLE_GUIDE.md](GO_STYLE_GUIDE.md)
- **Python Style Guide**: [PYTHON_STYLE_GUIDE.md](PYTHON_STYLE_GUIDE.md)
- **TypeScript Style Guide**: [TYPESCRIPT_STYLE_GUIDE.md](TYPESCRIPT_STYLE_GUIDE.md)
- **Architecture**: [docs/architecture/system-overview.md](docs/architecture/system-overview.md)
- **Deployment**: [docs/deployment/](docs/deployment/)

---

## 🔄 Keeping This Document Updated

When making technology changes:

1. Update version numbers in this document
2. Add new technologies to the appropriate sections
3. Document rationale for technology choices
4. Update the future roadmap if applicable

See [AI_COLLABORATION_GUIDE.md](AI_COLLABORATION_GUIDE.md) for documentation requirements.

---

<p align="center">
  Technology choices made with purpose. 🎯
</p>
