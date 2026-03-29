"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from lumina_brain.api.router import api_router
from lumina_brain.config.settings import settings

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