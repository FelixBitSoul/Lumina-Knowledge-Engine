from fastapi import APIRouter, Query
from lumina_brain.core.services.embedding import embedding_service
from lumina_brain.core.services.qdrant import qdrant_service
from lumina_brain.core.services.cache import cache_service
from lumina_brain.config.settings import settings
import time
from typing import Optional

router = APIRouter()


@router.get("")
async def search(
    query: str,
    page_size: int = Query(3, ge=1, le=20, description="Number of results per page"),
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    collection: str = Query(None, description="Collection name (default: config collection)"),
    # Meta filters
    title: Optional[str] = Query(None, description="Filter by title (full-text search)"),
    url: Optional[str] = Query(None, description="Filter by URL (exact match)"),
    domain: Optional[str] = Query(None, description="Filter by domain (exact match)"),
    category: Optional[str] = Query(None, description="Filter by category (exact match)"),
    file_name: Optional[str] = Query(None, description="Filter by file name (exact match)"),
    start_time: Optional[str] = Query(None, description="Filter by start time (ISO format)"),
    end_time: Optional[str] = Query(None, description="Filter by end time (ISO format)")
):
    """
    Perform semantic search against the vector database with optional metadata filters.
    Uses Qdrant prefetch for efficient pagination without reranking.

    Meta filters:
    - title: Full-text search in document titles
    - url: Exact match for document URL
    - domain: Exact match for document domain
    - category: Exact match for document category
    - file_name: Exact match for file name
    - start_time/end_time: Time range filter for updated_at
    """
    start_time_perf = time.time()

    target_collection = collection or settings.qdrant.collection

    # Generate cache key
    cache_key = cache_service.generate_cache_key(query, target_collection, filters)

    # Check if result is in cache
    cached_result = cache_service.get(cache_key)
    if cached_result:
        latency_ms = int((time.time() - start_time_perf) * 1000)
        return {
            "query": query,
            "page_size": page_size,
            "page": page,
            "offset": offset,
            "collection": target_collection,
            "filters": filters if filters else None,
            "latency_ms": latency_ms,
            "results": cached_result,
            "cached": True
        }

    # If not in cache, perform search
    query_vector = embedding_service.encode(query)

    filters = {}
    if title:
        filters["title"] = title
    if url:
        filters["url"] = url
    if domain:
        filters["domain"] = domain
    if category:
        filters["category"] = category
    if file_name:
        filters["file_name"] = file_name
    if start_time or end_time:
        filters["time_range"] = {}
        if start_time:
            filters["time_range"]["start"] = start_time
        if end_time:
            filters["time_range"]["end"] = end_time

    offset = (page - 1) * page_size
    prefetch_limit = page_size * 3

    if filters:
        results = qdrant_service.search_prefetch(
            query_vector=query_vector,
            limit=page_size,
            offset=offset,
            collection_name=target_collection,
            filters=filters,
            prefetch_limit=prefetch_limit
        )
    else:
        results = qdrant_service.search_prefetch(
            query_vector=query_vector,
            limit=page_size,
            offset=offset,
            collection_name=target_collection,
            prefetch_limit=prefetch_limit
        )

    # Cache the results
    cache_service.set(cache_key, results)

    latency_ms = int((time.time() - start_time_perf) * 1000)

    return {
        "query": query,
        "page_size": page_size,
        "page": page,
        "offset": offset,
        "collection": target_collection,
        "filters": filters if filters else None,
        "latency_ms": latency_ms,
        "results": results,
        "cached": False
    }
