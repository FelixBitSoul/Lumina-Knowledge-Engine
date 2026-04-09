from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel
from lumina_brain.core.services.qdrant import qdrant_service

router = APIRouter()

class CollectionCreate(BaseModel):
    name: str
    description: str

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

@router.post("")
async def create_collection(collection: CollectionCreate = Body(...)):
    """
    Create a new collection in Qdrant.

    Args:
        collection: CollectionCreate object with name and description

    Returns:
        dict: Success message with collection name
    """
    try:
        # Create collection in Qdrant
        qdrant_service._ensure_collection(collection.name)

        return {
            "collection": collection.name,
            "message": "Collection created successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def _get_minio_file_count(collection_name: str, minio_service) -> int:
    """Get file count from MinIO for a collection"""
    try:
        # Build MinIO path prefix
        prefix = f"raw/collections/{collection_name}/"

        # List all objects with the specified prefix
        objects = minio_service.client.list_objects(
            bucket_name=minio_service.bucket,
            prefix=prefix,
            recursive=True
        )

        # Count files
        file_count = 0
        for _ in objects:
            file_count += 1

        return file_count
    except Exception as e:
        print(f"Error counting files in MinIO: {e}")
        return 0


def _get_qdrant_vector_count(collection_name: str, qdrant_service) -> int:
    """Get vector count from Qdrant for a collection"""
    try:
        # Get collection information
        collection_info = qdrant_service.client.get_collection(collection_name=collection_name)

        # Get total vectors (points) in the collection
        total_vectors = collection_info.points_count

        return total_vectors
    except Exception as e:
        print(f"Error getting collection info from Qdrant: {e}")
        return 0


def _initialize_collection_stats(collection_name: str) -> dict:
    """Initialize collection statistics with default values"""
    return {
        "collection": collection_name,
        "files_count": 0,
        "total_vectors": 0,
        "total_chunks": 0,  # Each vector represents a chunk
        "vector_size": 384,  # Fixed for all-MiniLM-L6-v2 model
        "distance_function": "cosine"
    }


@router.get("/{collection_name}")
async def get_collection_details(collection_name: str):
    """
    Get detailed information about a specific collection.
    Returns collection metadata including file count, vector count, and chunk count.
    """
    try:
        from lumina_brain.core.services.cache import cache_service
        from lumina_brain.core.services.minio import minio_service

        # Generate cache key
        cache_key = f"lumina:stats:{collection_name}"

        # Try to get stats from cache
        cached_stats = cache_service.get(cache_key)
        if cached_stats:
            return cached_stats

        # Initialize stats
        stats = _initialize_collection_stats(collection_name)

        # Get file count from MinIO
        stats["files_count"] = _get_minio_file_count(collection_name, minio_service)

        # Get vector count from Qdrant
        total_vectors = _get_qdrant_vector_count(collection_name, qdrant_service)
        stats["total_vectors"] = total_vectors
        stats["total_chunks"] = total_vectors  # Each vector represents a chunk

        # Cache stats with 60-second expiration
        cache_service.set(cache_key, stats, ttl=60)

        return stats
    except Exception as e:
        # If collection doesn't exist, return default values
        return _initialize_collection_stats(collection_name)
