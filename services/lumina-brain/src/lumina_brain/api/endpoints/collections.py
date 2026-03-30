from fastapi import APIRouter, HTTPException
from lumina_brain.core.services.qdrant import qdrant_service

router = APIRouter()

@router.get("")
async def get_collections():
    """
    Get all available collections from Qdrant.
    Returns a list of collection names with optional metadata.
    """
    try:
        collections_response = qdrant_service.client.get_collections()
        collection_names = [col.name for col in collections_response.collections]

        return {
            "collections": collection_names,
            "count": len(collection_names)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))