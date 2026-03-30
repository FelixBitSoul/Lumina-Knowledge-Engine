from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, FieldCondition, Filter, MatchValue, MatchText, Range, DatetimeRange
from lumina_brain.config.settings import settings
import uuid
import hashlib
from datetime import datetime, timezone
from urllib.parse import urlparse


class QdrantService:
    """Service for handling Qdrant vector database operations"""

    def __init__(self):
        self.client = QdrantClient(
            host=settings.qdrant.host,
            port=settings.qdrant.port
        )
        # Create default collection if it doesn't exist
        self._ensure_collection(settings.qdrant.collection)

    def generate_id_from_url(self, url: str) -> str:
        """Generate a deterministic UUID based on the URL"""
        hash_object = hashlib.md5(url.encode())
        return str(uuid.UUID(hash_object.hexdigest()))

    def extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        parsed_url = urlparse(url)
        return parsed_url.netloc

    def _ensure_collection(self, collection_name: str):
        """Create collection if it doesn't exist"""
        try:
            self.client.get_collection(collection_name=collection_name)
        except Exception:
            # Vector size 384 is specific to 'all-MiniLM-L6-v2'
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=384, distance=Distance.COSINE)
            )

            # Create payload indexes for metadata fields
            # Title - full-text search index
            self.client.create_payload_index(
                collection_name=collection_name,
                field_name="title",
                field_schema="text"
            )

            # URL - keyword index for exact match
            self.client.create_payload_index(
                collection_name=collection_name,
                field_name="url",
                field_schema="keyword"
            )

            # Domain - keyword index for exact match
            self.client.create_payload_index(
                collection_name=collection_name,
                field_name="domain",
                field_schema="keyword"
            )

            # Updated_at - datetime index for time range filtering
            self.client.create_payload_index(
                collection_name=collection_name,
                field_name="updated_at",
                field_schema="datetime"
            )

    def get_collection(self, collection_name: str):
        """Get collection information"""
        return self.client.get_collection(collection_name=collection_name)

    def upsert_document(self, url: str, title: str, content: str, vector: list, collection_name: str = None) -> str:
        """Upsert document to Qdrant"""
        target_collection = collection_name or settings.qdrant.collection
        self._ensure_collection(target_collection)

        # Generate integer ID by hashing the URL
        point_id = int(hashlib.sha256(url.encode()).hexdigest(), 16) % 10**18

        # Get current UTC time
        updated_at = datetime.now(timezone.utc).isoformat()

        # Extract domain from URL
        domain = self.extract_domain(url)

        self.client.upsert(
            collection_name=target_collection,
            points=[
                PointStruct(
                    id=point_id,
                    vector=vector,
                    payload={
                        "url": url,
                        "domain": domain,
                        "title": title,
                        "content": content,
                        "updated_at": updated_at,
                    },
                )
            ],
        )

        return str(point_id)

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
                    "content": payload.get("content") or "",
                    "updated_at": payload.get("updated_at"),
                }
            )

        return results

    def search_multiple_collections(self, query_vector: list, limit: int, collection_names: list = None) -> list:
        """Search across multiple collections"""
        if not collection_names:
            # If no collections specified, use default collection
            return self.search(query_vector, limit)

        all_results = []
        for collection_name in collection_names:
            try:
                # Ensure collection exists
                self._ensure_collection(collection_name)

                search_result = self.client.query_points(
                    collection_name=collection_name,
                    query=query_vector,
                    limit=limit,
                    with_payload=True,
                    with_vectors=False,
                )

                for hit in search_result.points:
                    payload = hit.payload or {}
                    all_results.append(
                        {
                            "score": hit.score,
                            "title": payload.get("title"),
                            "url": payload.get("url"),
                            "content": payload.get("content") or "",
                            "updated_at": payload.get("updated_at"),
                            "collection": collection_name,  # Add collection information
                        }
                    )
            except Exception as e:
                print(f"Error searching collection {collection_name}: {e}")

        # Sort results by score and limit
        all_results.sort(key=lambda x: x["score"], reverse=True)
        return all_results[:limit]

    def search_with_filters(
        self,
        query_vector: list,
        limit: int,
        collection_name: str = None,
        filters: dict = None
    ) -> list:
        """Search for similar documents with metadata filters"""
        target_collection = collection_name or settings.qdrant.collection
        self._ensure_collection(target_collection)

        qdrant_filter = self._build_filter(filters)

        search_result = self.client.query_points(
            collection_name=target_collection,
            query=query_vector,
            limit=limit,
            with_payload=True,
            with_vectors=False,
            query_filter=qdrant_filter
        )

        return self._parse_search_result(search_result)

    def search_prefetch(
        self,
        query_vector: list,
        limit: int,
        offset: int,
        collection_name: str = None,
        filters: dict = None,
        prefetch_limit: int = 9
    ) -> list:
        """Search with prefetch for efficient pagination using Qdrant's prefetch capability"""
        target_collection = collection_name or settings.qdrant.collection
        self._ensure_collection(target_collection)

        qdrant_filter = self._build_filter(filters)

        search_result = self.client.query_points(
            collection_name=target_collection,
            query=query_vector,
            limit=limit,
            offset=offset,
            with_payload=True,
            with_vectors=False,
            query_filter=qdrant_filter,
            prefetch=[
                {
                    "limit": prefetch_limit,
                    "offset": offset,
                    "query": query_vector,
                    "filter": qdrant_filter
                }
            ] if offset > 0 else None
        )

        return self._parse_search_result(search_result)

    def _build_filter(self, filters: dict = None) -> Filter:
        """Build Qdrant filter from filters dict"""
        if not filters:
            return None

        must_conditions = []

        if filters.get("title"):
            must_conditions.append(
                FieldCondition(
                    key="title",
                    match=MatchText(text=filters["title"])
                )
            )

        if filters.get("url"):
            must_conditions.append(
                FieldCondition(
                    key="url",
                    match=MatchValue(value=filters["url"])
                )
            )

        if filters.get("domain"):
            must_conditions.append(
                FieldCondition(
                    key="domain",
                    match=MatchValue(value=filters["domain"])
                )
            )

        if filters.get("time_range"):
            time_filter = filters["time_range"]
            datetime_range_conditions = {}
            if time_filter.get("start"):
                datetime_range_conditions["gte"] = time_filter["start"]
            if time_filter.get("end"):
                datetime_range_conditions["lte"] = time_filter["end"]
            if datetime_range_conditions:
                must_conditions.append(
                    FieldCondition(
                        key="updated_at",
                        range=DatetimeRange(**datetime_range_conditions)
                    )
                )

        if must_conditions:
            return Filter(must=must_conditions)
        return None

    def _parse_search_result(self, search_result) -> list:
        """Parse Qdrant search result into list of dicts"""
        results = []
        for hit in search_result.points:
            payload = hit.payload or {}
            results.append({
                "score": hit.score,
                "title": payload.get("title"),
                "url": payload.get("url"),
                "domain": payload.get("domain"),
                "content": payload.get("content") or "",
                "updated_at": payload.get("updated_at"),
            })
        return results


# Create global Qdrant service instance
qdrant_service = QdrantService()
