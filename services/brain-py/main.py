import os
from fastapi import FastAPI
from pydantic import BaseModel
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer
import uuid
import uvicorn

app = FastAPI(title="Lumina Brain - Vector Service")

# 1. Initialize Local Embedding Model
# This will download a small model (~80MB) on first run
model = SentenceTransformer('all-MiniLM-L6-v2')

# 2. Initialize Qdrant Client
qdrant_client = QdrantClient(host="localhost", port=6333)
COLLECTION_NAME = "knowledge_base"

# Create collection if it doesn't exist
try:
    qdrant_client.get_collection(collection_name=COLLECTION_NAME)
except Exception:
    # Vector size 384 is specific to 'all-MiniLM-L6-v2'
    qdrant_client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=384, distance=Distance.COSINE),
    )

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
                        "content": doc.content
                    }
                )
            ]
        )
        
        print(f"Successfully indexed: {doc.title}")
        return {"status": "success", "point_id": point_id}
    except Exception as e:
        print(f"Error during ingestion: {e}")
        return {"status": "error", "message": str(e)}

# Add a simple Search endpoint for testing
@app.get("/search")
async def search(query: str, limit: int = 3):
    """
    Perform semantic search against the vector database
    """
    query_vector = model.encode(query).tolist()
    
    hits = qdrant_client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        limit=limit
    ).points
    
    results = []
    for hit in hits:
        results.append({
            "score": 0.0,
            "title": hit.payload.get("title"),
            "url": hit.payload.get("url"),
            "content": hit.payload.get("content")[:200]
        })
    
    return {"results": results}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)