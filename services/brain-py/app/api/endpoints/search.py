from fastapi import APIRouter, Query
from ...core.services.embedding import embedding_service
from ...core.services.qdrant import qdrant_service
from ...core.reranker import reranker
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

    # 粗排：获取更多候选文档
    initial_results = qdrant_service.search(
        query_vector=query_vector,
        limit=100,  # 粗排默认100
        collection_name=target_collection
    )

    # 精排：使用重排器优化排序
    results = reranker.rerank(query, initial_results, limit)

    latency_ms = int((time.time() - start_time) * 1000)

    return {
        "query": query,
        "limit": limit,
        "collection": target_collection,
        "latency_ms": latency_ms,
        "results": results,
    }
