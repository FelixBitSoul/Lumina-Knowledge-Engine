# Lumina-Knowledge-Engine 🧠

> **An Industrial-grade RAG (Retrieval-Augmented Generation) engine for real-time technology knowledge synchronization.**

Lumina-Knowledge-Engine is a sophisticated system designed to bridge the gap between static LLMs and fast-evolving web documentation. It leverages a high-performance Go-based crawler for data ingestion and a Python-powered AI pipeline for semantic retrieval.

---

## 🏗️ Architecture Overview

The system is built with a modular microservices philosophy:



* **Ingestion Engine (Go):** A high-concurrency, rate-limited crawler designed for efficient data harvesting.
* **AI Logic Layer (Python):** Handles document chunking, embedding generation, and RAG-based inference.
* **Knowledge Portal (Next.js):** A clean, professional UI for querying the engine with stream-based AI responses.
* **Data Backbone:** Vector database (Milvus/Qdrant) for semantic search, Redis for task orchestration, and PostgreSQL for metadata.

---

## 🛠️ Tech Stack

### Backend & AI
- **Languages:** Go (Concurrency & Scraping), Python 3.10+ (AI Pipeline)
- **AI Frameworks:** FastAPI, LangChain / LlamaIndex
- **Databases:** PostgreSQL (Metadata), Redis (Queue), Milvus/Qdrant (Vector Store)
- **LLM Integration:** DeepSeek / OpenAI API

### Frontend
- **Framework:** Next.js 15 (App Router), TypeScript
- **Styling:** Tailwind CSS, Shadcn UI
- **State & Data:** TanStack Query, Lucide Icons

### Infrastructure (Cloud Native)
- **Containerization:** Docker & Docker Compose
- **Orchestration:** Kubernetes (Ready)
- **CI/CD:** GitHub Actions

---

## 📂 Project Structure

```text
.
├── services/
│   ├── crawler-go/      # High-concurrency data ingestion
│   └── brain-py/        # AI logic & RAG pipeline
├── web/                 # Next.js frontend application
├── deployments/         # Docker & K8s configurations
└── scripts/             # Development & automation tools