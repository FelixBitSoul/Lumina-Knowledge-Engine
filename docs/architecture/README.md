# Architecture Documentation

This section contains detailed documentation about the Lumina Knowledge Engine's architecture, design decisions, and system behavior.

## 📋 Architecture Documents

### 📊 [System Overview](./system-overview.md)
High-level system architecture, component relationships, and technology stack overview.

### 🔧 [Component Details](./component-details.md)
In-depth technical documentation for each service component:
- Crawler Service (Go)
- Brain API (Python)  
- Portal Frontend (Next.js)
- Vector Database (Qdrant)

### 🌊 [Data Flow](./data-flow.md)
End-to-end data flow diagrams, request/response patterns, and system interactions.

### 📡 [API Contracts](./api-contracts.md)
Service-to-service communication protocols, data models, and interface specifications.

### 🎯 [Technical Decisions](./technical-decisions.md)
Design rationale, technology choices, trade-offs, and architectural decisions.

### ⚡ [Performance Characteristics](./performance-characteristics.md)
Performance analysis, bottlenecks, scalability limits, and optimization opportunities.

## 🏗 Architecture Principles

Lumina follows these core architectural principles:

### 1. **Microservices Architecture**
- Clear service boundaries
- Independent deployment and scaling
- Technology diversity (Go, Python, JavaScript)

### 2. **Separation of Concerns**
- Data ingestion (Crawler)
- Vector processing (Brain API)
- User interface (Portal)
- Storage (Qdrant)

### 3. **Configuration-Driven**
- YAML-based crawler configuration
- Environment-based service configuration
- Flexible deployment options

### 4. **Fault Tolerance**
- Retry mechanisms and error handling
- Health checks and monitoring
- Graceful degradation

## 🔄 Data Flow Overview

```mermaid
graph LR
    A[Web Sources] --> B[Crawler Service]
    B --> C[Content Processing]
    C --> D[Brain API]
    D --> E[Vector Embedding]
    E --> F[Qdrant DB]
    F --> G[Semantic Search]
    G --> H[Portal Frontend]
    H --> I[User Interface]
    
    style A fill:#e1f5fe
    style B fill:#f3e5f5
    style C fill:#fff3e0
    style D fill:#e8f5e8
    style E fill:#fce4ec
    style F fill:#f1f8e9
    style G fill:#e0f2f1
    style H fill:#f9fbe7
    style I fill:#e3f2fd
```

## 🛠 Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Crawler** | Go 1.22 + Colly | High-performance web scraping |
| **Brain API** | Python 3.11 + FastAPI | Vector embeddings and search |
| **Portal** | Next.js 15 + React | Modern web interface |
| **Vector DB** | Qdrant | High-speed vector storage |
| **Embedding** | SentenceTransformers | Text vectorization |
| **Container** | Docker | Service deployment |

## 📏 Non-Functional Requirements

### Performance
- Search response time: < 500ms
- Crawler throughput: 60 requests/minute per task
- Concurrent users: 100+

### Reliability
- Service availability: 99.9%
- Automatic retry on failures
- Health check endpoints

### Scalability
- Horizontal scaling of crawler instances
- Vector database clustering support
- Stateless service design

### Maintainability
- Clear service boundaries
- Comprehensive logging
- Configuration-driven behavior

---

*For detailed technical information, please refer to the specific documentation pages linked above.*
