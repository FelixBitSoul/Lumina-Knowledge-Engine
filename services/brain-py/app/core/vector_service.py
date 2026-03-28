from typing import List
from .services.embedding import embedding_service
from .services.qdrant import qdrant_service
from .reranker import reranker
from config.settings import settings
import logging

logger = logging.getLogger(__name__)

def search_relevant_documents(query: str, collection: str = "all", top_k: int = 3) -> List[str]:
    """检索相关文档"""
    try:
        # Use specified collection or default from config
        logger.info(f"Searching in collection: {collection}")
        target_collection = collection if collection != "all" else settings.qdrant.collection

        # Generate query vector
        query_vector = embedding_service.encode(query)

        # 粗排：获取更多候选文档
        logger.info(f"Performing initial search with top_k=100")
        initial_results = qdrant_service.search(
            query_vector=query_vector,
            limit=100,  # 粗排默认100
            collection_name=target_collection
        )

        # 精排：使用重排器优化排序
        logger.info(f"Reranking results with top_k={top_k}")
        reranked_results = reranker.rerank(query, initial_results, top_k)

        # 提取相关文档内容
        context = []
        for result in reranked_results:
            content = result.get("content", "")
            if content:
                context.append(content[:500])  # 限制每个文档的长度

        return context
    except Exception as e:
        logger.error(f"Error searching documents: {e}")
        return []
