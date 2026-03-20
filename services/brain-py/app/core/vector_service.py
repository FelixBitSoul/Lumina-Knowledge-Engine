from typing import List
from .services.embedding import embedding_service
from .services.qdrant import qdrant_service
from config.settings import settings

def search_relevant_documents(query: str, collection: str = "all", top_k: int = 3) -> List[str]:
    """检索相关文档"""
    try:
        # Use specified collection or default from config
        target_collection = collection if collection != "all" else settings.qdrant.collection

        # Generate query vector
        query_vector = embedding_service.encode(query)

        # Search in Qdrant
        results = qdrant_service.search(
            query_vector=query_vector,
            limit=top_k,
            collection_name=target_collection
        )

        # 提取相关文档内容
        context = []
        for result in results:
            content = result.get("content", "")
            if content:
                context.append(content[:500])  # 限制每个文档的长度

        return context
    except Exception as e:
        print(f"Error searching documents: {e}")
        return []
