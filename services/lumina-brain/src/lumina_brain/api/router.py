from fastapi import APIRouter
from .endpoints import health, ingest, search, chat, collections, upload, websocket, documents

api_router = APIRouter()

api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(ingest.router, prefix="/ingest", tags=["ingest"])
api_router.include_router(upload.router, prefix="/upload", tags=["upload"])
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_router.include_router(collections.router, prefix="/collections", tags=["collections"])
api_router.include_router(search.router, prefix="/search", tags=["search"])
api_router.include_router(chat.router, tags=["chat"])
api_router.include_router(websocket.router, tags=["websocket"])
