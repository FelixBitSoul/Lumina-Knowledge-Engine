import time
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware # Required for cross-origin requests
from pydantic import BaseModel
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer
import uuid
import uvicorn

from config.settings import settings

app = FastAPI(title="Lumina Brain - Vector Service")

# --- CORS Configuration ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors.origins,           # Allows specific origins
    allow_credentials=True,                        # Allows cookies to be included in requests
    allow_methods=["*"],                           # Allows all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],                           # Allows all headers
)

# 1. Initialize Local Embedding Model
# This will download a small model (~80MB) on first run
model = SentenceTransformer(settings.model.name, cache_folder=settings.model.cache_dir)
print(f"Model loaded: {settings.model.name}")

# 2. Initialize Qdrant Client
qdrant_client = QdrantClient(host=settings.qdrant.host, port=settings.qdrant.port)
COLLECTION_NAME = settings.qdrant.collection

# Create collection if it doesn't exist
try:
    qdrant_client.get_collection(collection_name=COLLECTION_NAME)
except Exception:
    # Vector size 384 is specific to 'all-MiniLM-L6-v2'
    qdrant_client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=384, distance=Distance.COSINE),
    )


@app.get("/health")
async def health():
    """
    Lightweight health check for the Brain API.
    Used by the portal and Docker to verify readiness.
    """
    try:
        qdrant_client.get_collection(collection_name=COLLECTION_NAME)
        qdrant_status = "up"
    except Exception:
        qdrant_status = "down"

    return {
        "status": "ok",
        "qdrant": qdrant_status,
        "model": settings.model.name,
        "collection": COLLECTION_NAME,
    }

class Document(BaseModel):
    url: str
    title: str
    content: str

@app.post("/ingest")
async def ingest_document(doc: Document):
    """
    Process document: Generate embedding and store in Qdrant
    """
    try:
        # Generate vector embedding from content
        vector = model.encode(doc.content).tolist()

        # Create a unique point for Qdrant
        point_id = str(uuid.uuid4())

        # Upsert into Qdrant
        qdrant_client.upsert(
            collection_name=COLLECTION_NAME,
            points=[
                PointStruct(
                    id=point_id,
                    vector=vector,
                    payload={
                        "url": doc.url,
                        "title": doc.title,
                        "content": doc.content,
                    },
                )
            ],
        )

        print(f"Successfully indexed: {doc.title}")
        return {"status": "success", "point_id": point_id}
    except Exception as e:
        print(f"Error during ingestion: {e}")
        return {"status": "error", "message": str(e)}

# Add a semantic search endpoint
@app.get("/search")
async def search(query: str, limit: int = 3):
    """
    Perform semantic search against the vector database.
    Returns a structured response suitable for the Next.js portal.
    """
    start_time = time.time()
    query_vector = model.encode(query).tolist()

    search_result = qdrant_client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        limit=limit,
        with_payload=True,
        with_vectors=False,
    )

    hits = search_result.points

    results = []
    for hit in hits:
        payload = hit.payload or {}
        results.append(
            {
                "score": hit.score,
                "title": payload.get("title"),
                "url": payload.get("url"),
                "content": (payload.get("content") or "")[:200],
            }
        )

    latency_ms = int((time.time() - start_time) * 1000)

    return {
        "query": query,
        "limit": limit,
        "collection": COLLECTION_NAME,
        "latency_ms": latency_ms,
        "results": results,
    }

if __name__ == "__main__":
    uvicorn.run(app, host=settings.api.host, port=settings.api.port)