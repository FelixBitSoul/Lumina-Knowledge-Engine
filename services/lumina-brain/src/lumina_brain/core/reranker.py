from sentence_transformers import CrossEncoder
from lumina_brain.config.settings import settings
import logging

logger = logging.getLogger(__name__)

class Reranker:
    """文档重排服务"""
    
    def __init__(self):
        try:
            # 使用中型交叉编码器模型
            self.model = CrossEncoder(
                'cross-encoder/ms-marco-MiniLM-L-12-v2',
                cache_folder=settings.model.cache_dir
            )
            logger.info("Reranker model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load reranker model: {str(e)}")
            self.model = None
    
    def rerank(self, query: str, documents: list, top_k: int = 3) -> list:
        """重排文档列表
        
        Args:
            query: 查询字符串
            documents: 原始文档列表
            top_k: 重排后返回的文档数量
            
        Returns:
            重排后的文档列表
        """
        if not self.model:
            logger.warning("Reranker model not available, returning original results")
            return documents[:top_k]
        
        if not documents:
            return []
        
        try:
            # 准备模型输入
            pairs = [[query, doc.get('content', '')] for doc in documents]
            
            # 获取相关性分数
            scores = self.model.predict(pairs)
            
            # 为文档添加分数
            for i, doc in enumerate(documents):
                doc['rerank_score'] = float(scores[i])
                # 保留原始向量搜索分数
                doc['vector_score'] = doc.get('score', 0.0)
                # 设置最终分数为重新排序的分数
                doc['score'] = doc['rerank_score']
            
            # 按重排分数排序
            documents.sort(key=lambda x: x['rerank_score'], reverse=True)
            
            return documents[:top_k]
        except Exception as e:
            logger.error(f"Reranking failed: {str(e)}")
            # 失败时返回原始排序
            return documents[:top_k]


# 创建全局重排器实例
reranker = Reranker()