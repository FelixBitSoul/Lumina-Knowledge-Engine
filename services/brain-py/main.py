import os
import time
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware # Required for cross-origin requests
from pydantic import BaseModel
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer
import uuid
import uvicorn

app = FastAPI(title="Lumina Brain - Vector Service")

# --- CORS Configuration ---
# Define the list of origins that are allowed to make cross-site HTTP requests
# In development, we allow our Next.js frontend running on localhost:3000
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,           # Allows specific origins
    allow_credentials=True,          # Allows cookies to be included in requests
    allow_methods=["*"],             # Allows all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],             # Allows all headers
)

# 1. Initialize Local Embedding Model
# This will download a small model (~80MB) on first run
MODEL_NAME = os.getenv("MODEL_NAME", "all-MiniLM-L6-v2")
model_cache_dir = os.getenv("MODEL_CACHE_DIR", "/app/models")
model = SentenceTransformer(MODEL_NAME, cache_folder=model_cache_dir)
print(f"Model loaded: {MODEL_NAME}")

# 2. Initialize Qdrant Client
QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))
qdrant_client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
COLLECTION_NAME = os.getenv("QDRANT_COLLECTION", "knowledge_base")

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
        "model": MODEL_NAME,
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
    uvicorn.run(app, host="0.0.0.0", port=8000)