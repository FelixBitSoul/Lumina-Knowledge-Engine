from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from config.settings import settings
import uuid


class QdrantService:
    """Service for handling Qdrant vector database operations"""
    
    def __init__(self):
        self.client = QdrantClient(
            host=settings.qdrant.host,
            port=settings.qdrant.port
        )
        # Create default collection if it doesn't exist
        self._ensure_collection(settings.qdrant.collection)
    
    def _ensure_collection(self, collection_name: str):
        """Create collection if it doesn't exist"""
        try:
            self.client.get_collection(collection_name=collection_name)
        except Exception:
            # Vector size 384 is specific to 'all-MiniLM-L6-v2'
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=384, distance=Distance.COSINE),
            )
    
    def get_collection(self, collection_name: str):
        """Get collection information"""
        return self.client.get_collection(collection_name=collection_name)
    
    def upsert_document(self, url: str, title: str, content: str, vector: list, collection_name: str = None) -> str:
        """Upsert document to Qdrant"""
        target_collection = collection_name or settings.qdrant.collection
        self._ensure_collection(target_collection)
        
        point_id = str(uuid.uuid4())
        
        self.client.upsert(
            collection_name=target_collection,
            points=[
                PointStruct(
                    id=point_id,
                    vector=vector,
                    payload={
                        "url": url,
                        "title": title,
                        "content": content,
                    },
                )
            ],
        )
        
        return point_id
    
    def search(self, query_vector: list, limit: int, collection_name: str = None) -> list:
        """Search for similar documents"""
        target_collection = collection_name or settings.qdrant.collection
        self._ensure_collection(target_collection)
        
        search_result = self.client.query_points(
            collection_name=target_collection,
            query=query_vector,
            limit=limit,
            with_payload=True,
            with_vectors=False,
        )
        
        results = []
        for hit in search_result.points:
            payload = hit.payload or {}
            results.append(
                {
                    "score": hit.score,
                    "title": payload.get("title"),
                    "url": payload.get("url"),
                    "content": (payload.get("content") or "")[:200],
                }
            )
        
        return results


# Create global Qdrant service instance
qdrant_service = QdrantService()
