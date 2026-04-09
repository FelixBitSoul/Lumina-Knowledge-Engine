from fastapi import APIRouter, Query
from lumina_brain.core.services.embedding import embedding_service
from lumina_brain.core.services.qdrant import qdrant_service
from lumina_brain.core.services.cache import cache_service
from lumina_brain.config.settings import settings
import time
from typing import Optional, Dict, Any

router = APIRouter()


def _build_search_filters(
    title: Optional[str],
    url: Optional[str],
    domain: Optional[str],
    category: Optional[str],
    file_name: Optional[str],
    start_time: Optional[str],
    end_time: Optional[str]
) -> Dict[str, Any]:
    """Build search filters from query parameters"""
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
    return filters


def _build_search_response(
    query: str,
    page_size: int,
    page: int,
    offset: int,
    target_collection: str,
    filters: Dict[str, Any],
    results: Any,
    latency_ms: int,
    cached: bool
) -> Dict[str, Any]:
    """Build search response"""
    return {
        "query": query,
        "page_size": page_size,
        "page": page,
        "offset": offset,
        "collection": target_collection,
        "filters": filters if filters else None,
        "latency_ms": latency_ms,
        "results": results,
        "cached": cached
    }


def _perform_search(
    query_vector: Any,
    page_size: int,
    offset: int,
    target_collection: str,
    filters: Dict[str, Any]
) -> Any:
    """Perform search with or without filters"""
    prefetch_limit = page_size * 3
    
    if filters:
        return qdrant_service.search_prefetch(
            query_vector=query_vector,
            limit=page_size,
            offset=offset,
            collection_name=target_collection,
            filters=filters,
            prefetch_limit=prefetch_limit
        )
    else:
        return qdrant_service.search_prefetch(
            query_vector=query_vector,
            limit=page_size,
            offset=offset,
            collection_name=target_collection,
            prefetch_limit=prefetch_limit
        )


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
    offset = (page - 1) * page_size

    # Build filters
    filters = _build_search_filters(
        title, url, domain, category, file_name, start_time, end_time
    )

    # Generate cache key
    cache_key = cache_service.generate_cache_key(query, target_collection, filters)

    # Check if result is in cache
    cached_result = cache_service.get(cache_key)
    if cached_result:
        latency_ms = int((time.time() - start_time_perf) * 1000)
        return _build_search_response(
            query, page_size, page, offset, target_collection, filters, 
            cached_result, latency_ms, True
        )

    # If not in cache, perform search
    query_vector = embedding_service.encode(query)
    results = _perform_search(
        query_vector, page_size, offset, target_collection, filters
    )

    # Cache the results
    cache_service.set(cache_key, results)

    latency_ms = int((time.time() - start_time_perf) * 1000)

    return _build_search_response(
        query, page_size, page, offset, target_collection, filters, 
        results, latency_ms, False
    )
