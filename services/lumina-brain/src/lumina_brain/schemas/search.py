from pydantic import BaseModel
from typing import List


class SearchResult(BaseModel):
    """Schema for search result"""
    score: float
    vector_score: float
    rerank_score: float
    title: str
    url: str
    content: str
    collection: str = None


class SearchResponse(BaseModel):
    """Schema for search response"""
    query: str
    limit: int
    collection: str
    latency_ms: int
    results: List[SearchResult]