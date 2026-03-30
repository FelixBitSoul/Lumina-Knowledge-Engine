from fastapi import APIRouter, Query
from lumina_brain.core.services.embedding import embedding_service
from lumina_brain.core.services.qdrant import qdrant_service
from lumina_brain.core.reranker import reranker
from lumina_brain.config.settings import settings
import time
from typing import Optional

router = APIRouter()


@router.get("")
async def search(
    query: str,
    limit: int = Query(3, ge=1, le=10),
    collection: str = Query(None, description="Collection name (default: config collection)"),
    # Meta filters
    title: Optional[str] = Query(None, description="Filter by title (full-text search)"),
    url: Optional[str] = Query(None, description="Filter by URL (exact match)"),
    domain: Optional[str] = Query(None, description="Filter by domain (exact match)"),
    start_time: Optional[str] = Query(None, description="Filter by start time (ISO format)"),
    end_time: Optional[str] = Query(None, description="Filter by end time (ISO format)")
):
    """
    Perform semantic search against the vector database with optional metadata filters.
    Returns a structured response suitable for the Next.js portal.
    
    Meta filters:
    - title: Full-text search in document titles
    - url: Exact match for document URL
    - domain: Exact match for document domain
    - start_time/end_time: Time range filter for updated_at
    """
    start_time_perf = time.time()
    
    # Use specified collection or default from config
    target_collection = collection or settings.qdrant.collection
    
    # Generate query vector
    query_vector = embedding_service.encode(query)

    # Build filters
    filters = {}
    if title:
        filters["title"] = title
    if url:
        filters["url"] = url
    if domain:
        filters["domain"] = domain
    if start_time or end_time:
        filters["time_range"] = {}
        if start_time:
            filters["time_range"]["start"] = start_time
        if end_time:
            filters["time_range"]["end"] = end_time

    # 粗排：获取更多候选文档
    if filters:
        # Use filtered search if filters are provided
        initial_results = qdrant_service.search_with_filters(
            query_vector=query_vector,
            limit=100,  # 粗排默认100
            collection_name=target_collection,
            filters=filters
        )
    else:
        # Use regular search if no filters
        initial_results = qdrant_service.search(
            query_vector=query_vector,
            limit=100,  # 粗排默认100
            collection_name=target_collection
        )

    # 精排：使用重排器优化排序
    results = reranker.rerank(query, initial_results, limit)

    latency_ms = int((time.time() - start_time_perf) * 1000)

    return {
        "query": query,
        "limit": limit,
        "collection": target_collection,
        "filters": filters if filters else None,
        "latency_ms": latency_ms,
        "results": results,
    }