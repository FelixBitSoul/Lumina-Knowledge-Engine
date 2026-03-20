from fastapi import APIRouter, Query
from ...core.services.embedding import embedding_service
from ...core.services.qdrant import qdrant_service
from config.settings import settings
import time

router = APIRouter()


@router.get("")
async def search(
    query: str,
    limit: int = Query(3, ge=1, le=10),
    collection: str = Query(None, description="Collection name (default: config collection)")
):
    """
    Perform semantic search against the vector database.
    Returns a structured response suitable for the Next.js portal.
    """
    start_time = time.time()
    
    # Use specified collection or default from config
    target_collection = collection or settings.qdrant.collection
    
    # Generate query vector
    query_vector = embedding_service.encode(query)

    # Search in Qdrant
    results = qdrant_service.search(
        query_vector=query_vector,
        limit=limit,
        collection_name=target_collection
    )

    latency_ms = int((time.time() - start_time) * 1000)

    return {
        "query": query,
        "limit": limit,
        "collection": target_collection,
        "latency_ms": latency_ms,
        "results": results,
    }
