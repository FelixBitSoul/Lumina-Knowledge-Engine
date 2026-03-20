from fastapi import APIRouter
from ...core.services.qdrant import qdrant_service
from config.settings import settings

router = APIRouter()


@router.get("")
async def health():
    """
    Lightweight health check for the Brain API.
    Used by the portal and Docker to verify readiness.
    """
    try:
        qdrant_service.get_collection(settings.qdrant.collection)
        qdrant_status = "up"
    except Exception:
        qdrant_status = "down"

    return {
        "status": "ok",
        "qdrant": qdrant_status,
        "model": settings.model.name,
        "collection": settings.qdrant.collection,
    }
