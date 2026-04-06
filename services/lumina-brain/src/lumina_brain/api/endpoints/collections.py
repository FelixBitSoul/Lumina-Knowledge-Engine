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

@router.get("/{collection_name}")
async def get_collection_details(collection_name: str):
    """
    Get detailed information about a specific collection.
    Returns collection metadata including file count, vector count, and chunk count.
    """
    try:
        from lumina_brain.core.services.cache import cache_service
        from lumina_brain.core.services.minio import minio_service

        # 生成缓存键
        cache_key = f"lumina:stats:{collection_name}"

        # 尝试从缓存获取统计信息
        cached_stats = cache_service.get(cache_key)
        if cached_stats:
            return cached_stats

        # 初始化统计信息
        stats = {
            "collection": collection_name,
            "files_count": 0,
            "total_vectors": 0,
            "total_chunks": 0,  # Each vector represents a chunk
            "vector_size": 384,  # Fixed for all-MiniLM-L6-v2 model
            "distance_function": "cosine"
        }

        # 统计 MinIO 中的文件数量
        try:
            # 构建 MinIO 路径前缀
            prefix = f"raw/collections/{collection_name}/"

            # 列出 MinIO 中指定前缀的所有对象
            objects = minio_service.client.list_objects(
                bucket_name=minio_service.bucket,
                prefix=prefix,
                recursive=True
            )

            # 计算文件数量
            file_count = 0
            for _ in objects:
                file_count += 1

            stats["files_count"] = file_count
        except Exception as e:
            print(f"Error counting files in MinIO: {e}")
            # 继续执行，不影响其他统计

        # 获取 Qdrant 中的向量数量
        try:
            # Get collection information
            collection_info = qdrant_service.client.get_collection(collection_name=collection_name)

            # Get total vectors (points) in the collection
            # 使用正确的属性名称 points_count 而不是 vectors_count
            total_vectors = collection_info.points_count

            stats["total_vectors"] = total_vectors
            stats["total_chunks"] = total_vectors  # Each vector represents a chunk
        except Exception as e:
            print(f"Error getting collection info from Qdrant: {e}")
            # 继续执行，返回默认值

        # 缓存统计结果，过期时间 60 秒
        cache_service.set(cache_key, stats, ttl=60)

        return stats
    except Exception as e:
        # 若 Collection 尚不存在，返回 files_count: 0, vectors_count: 0
        return {
            "collection": collection_name,
            "files_count": 0,
            "total_vectors": 0,
            "total_chunks": 0,
            "vector_size": 384,
            "distance_function": "cosine"
        }
