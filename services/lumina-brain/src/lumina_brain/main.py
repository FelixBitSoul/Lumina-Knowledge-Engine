"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from lumina_brain.api.router import api_router
from lumina_brain.config.settings import settings
from lumina_brain.core.services.websocket_manager import websocket_manager

app = FastAPI(
    title="Lumina Brain API",
    description="Vector embedding and semantic search service",
    version="1.0.0",
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors.origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router)


@app.on_event("startup")
async def startup_event():
    """Initialize WebSocket manager on application startup"""
    await websocket_manager.init_redis_pubsub()
    print("WebSocket manager initialized with Redis Pub/Sub")


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources on application shutdown"""
    if websocket_manager.redis_client:
        await websocket_manager.redis_client.close()
    print("WebSocket manager resources cleaned up")


def main():
    """Run the application."""
    import uvicorn
    uvicorn.run(
        "lumina_brain.main:app",
        host=settings.api.host,
        port=settings.api.port,
        reload=True,
    )


if __name__ == "__main__":
    main()
