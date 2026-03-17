# Lumina Knowledge Engine Documentation

Welcome to the Lumina Knowledge Engine documentation. This section contains comprehensive guides for understanding, deploying, and extending the system.

## 📚 Documentation Structure

### 📖 [Architecture](./architecture/)
System design, component interactions, and technical decisions.

- [System Overview](./architecture/system-overview.md) - High-level architecture and component relationships
- [Component Details](./architecture/component-details.md) - Deep dive into each service
- [Data Flow](./architecture/data-flow.md) - End-to-end data journey and interactions
- [API Contracts](./architecture/api-contracts.md) - Service-to-service communication protocols
- [Technical Decisions](./architecture/technical-decisions.md) - Design rationale and trade-offs
- [Performance Characteristics](./architecture/performance-characteristics.md) - Performance analysis and bottlenecks

### � [API Documentation](./api/)
Complete API specifications and integration guides.

- [Brain API](./api/brain-api.md) - Python FastAPI endpoints and examples
- [Crawler Configuration](./api/crawler-config.md) - YAML configuration reference
- [Portal Integration](./api/portal-integration.md) - Frontend integration guide
- [OpenAPI Specs](./api/openapi/) - Machine-readable API specifications

### �🚀 [Deployment](./deployment/)
Guides for deploying Lumina in different environments.

- [Local Setup](./deployment/local-setup.md) - Development environment setup
- [Docker Deployment](./deployment/docker-deployment.md) - Production deployment with Docker
- [Cloud Deployment](./deployment/cloud-deployment.md) - Cloud deployment options

### 👨‍💻 [Development](./development/)
Resources for developers contributing to Lumina.

- [Getting Started](./development/getting-started.md) - New developer onboarding
- [Contributing](./development/contributing.md) - Contribution guidelines
- [Code Style](./development/code-style.md) - Coding standards and conventions
- [Testing](./development/testing.md) - Testing strategies and practices

### 📖 [User Guide](./user-guide/)
Documentation for end users of the Lumina system.

- [Quick Start](./user-guide/quick-start.md) - Basic usage guide
- [Configuration](./user-guide/configuration.md) - System configuration options
- [Troubleshooting](./user-guide/troubleshooting.md) - Common issues and solutions
- [Best Practices](./user-guide/best-practices.md) - Usage recommendations

### 🔧 [Operations](./operations/)
Operational documentation for system administrators.

- [Monitoring](./operations/monitoring.md) - System monitoring and alerting
- [Maintenance](./operations/maintenance.md) - Regular maintenance procedures
- [Backup & Restore](./operations/backup-restore.md) - Data backup and recovery

## 🏗 Quick Navigation

### For New Users
1. Read the [System Overview](./architecture/system-overview.md) to understand the architecture
2. Follow the [Quick Start](./user-guide/quick-start.md) guide to get running
3. Check [Configuration](./user-guide/configuration.md) for customization options

### For Developers
1. Start with [Getting Started](./development/getting-started.md) for development setup
2. Review [Architecture](./architecture/) documentation for system understanding
3. Follow [Contributing](./development/contributing.md) guidelines for contributions

### For Operators
1. Review [Deployment](./deployment/) guides for your target environment
2. Check [Operations](./operations/) documentation for maintenance procedures
3. Monitor system health using [Monitoring](./operations/monitoring.md) guidelines

## 🎯 System Overview

Lumina Knowledge Engine is a modern RAG (Retrieval-Augmented Generation) system built with:

- **Crawler (Go 1.22)**: High-performance web scraper
- **Brain API (Python 3.11)**: Vector embedding & search service
- **Vector DB (Qdrant)**: High-speed vector storage
- **Portal (Next.js 15)**: Modern web interface

The system follows a microservices architecture with clear separation of concerns, enabling independent scaling and maintenance of each component.

## 📞 Getting Help

- Check the [Troubleshooting](./user-guide/troubleshooting.md) guide for common issues
- Review [FAQ](./user-guide/faq.md) for frequently asked questions
- Join our community discussions for technical support

---

*Last updated: 2026-03-17*
