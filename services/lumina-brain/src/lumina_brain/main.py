"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from lumina_brain.api.router import api_router
from lumina_brain.config.settings import settings
from lumina_brain.core.services.websocket_manager import websocket_manager
from lumina_brain.core.services.notification_service import notification_service
from lumina_brain.core.services.database import init_db

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
    # Initialize database
    init_db()
    print("Database initialized")
    
    # Initialize WebSocket manager
    await websocket_manager.start_notification_listener()
    print("WebSocket manager initialized with notification listener")


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources on application shutdown"""
    await notification_service.close()
    print("Notification service resources cleaned up")


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
