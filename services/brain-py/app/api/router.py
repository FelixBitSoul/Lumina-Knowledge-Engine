from fastapi import APIRouter
from .endpoints import health, ingest, search, chat

api_router = APIRouter()

# Register endpoints
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(ingest.router, prefix="/ingest", tags=["ingest"])
api_router.include_router(search.router, prefix="/search", tags=["search"])
api_router.include_router(chat.router, tags=["chat"])
