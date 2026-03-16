# Lumina Knowledge Engine

Lumina is a modern RAG (Retrieval-Augmented Generation) system built with Go, Python, and Next.js.

## 🚀 System Architecture
- **Crawler (Go 1.22)**: High-performance web scraper located in `services/crawler-go`.
- **Brain API (Python 3.11)**: Vector embedding & search service using FastAPI and `sentence-transformers`.
- **Vector DB (Qdrant)**: High-speed vector storage running in Docker.
- **Portal (Next.js 15)**: Modern web interface with dark/light mode support.

## 🛠 Tech Stack
- **Backend**: Go (Colly), Python (FastAPI, Qdrant-Client)
- **AI**: HuggingFace (all-MiniLM-L6-v2)
- **Frontend**: Next.js 15, Tailwind CSS v4, Lucide Icons
- **Infrastructure**: Docker Compose

## 🏗 Project Structure
- `/services/crawler-go`: Data ingestion logic.
- `/services/brain-py`: Embedding and semantic search API.
- `/services/portal-next`: Frontend UI.
- `/deployments`: Docker and database storage.

## 🚦 Getting Started
1. Start Qdrant: `docker-compose -f deployments/docker-compose.yaml up -d`
2. Start Brain API: `cd services/brain-py && python main.py`
3. Run Crawler: `cd services/crawler-go && go run ./cmd/crawler`
4. Start Portal: `cd services/portal-next && npm run dev`

## Module docs

- Crawler details: `services/crawler-go/README.md`