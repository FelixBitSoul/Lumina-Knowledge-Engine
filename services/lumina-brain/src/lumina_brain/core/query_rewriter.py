import os
from openai import OpenAI
import logging

logger = logging.getLogger(__name__)

class QueryRewriter:
    """查询重写服务"""
    
    def __init__(self):
        self.client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_API_BASE")
        )
        self.model_name = os.getenv("LLM_MODEL_NAME", "gpt-3.5-turbo")
        self.prompt_template = """你是一个对话分析助手。给定一段对话历史和用户最新的提问，你的任务是将最新提问重写为一个 完全独立、无须上下文即可理解 的查询语句。 
处理逻辑： 
指代消除 ：将"它"、"那个"、"这种方法"等代词替换为对话中实际指向的主体。 
背景补全 ：如果最新提问是补充性的（如"为什么？"），请结合上文补全完整问题。 
禁止回答 ：不要回答用户的问题，只需重写问题。 
如果当前问题已经是独立的，请原样返回。 
对话历史：  {chat_history} 
用户最新提问：  {user_query} 
重写后的独立查询： 
"""
    
    def rewrite(self, user_query: str, chat_history: list) -> str:
        """重写查询"""
        # 构建对话历史文本
        history_text = "\n".join([
            f"{'用户' if msg['role'] == 'user' else '助手'}: {msg['content'][:200]}"
            for msg in chat_history[-6:]  # 最近3轮对话
        ])
        
        # 构建完整提示词
        prompt = self.prompt_template.format(
            chat_history=history_text,
            user_query=user_query
        )
        
        try:
            # 调用OpenAI API
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "system", "content": prompt}],
                max_tokens=100,
                temperature=0.1
            )
            
            rewritten_query = response.choices[0].message.content.strip()
            return rewritten_query or user_query
        except Exception as e:
            logger.error(f"Query rewriting failed: {str(e)}")
            # 失败时回退到原始查询
            return user_query


# 创建全局查询重写器实例
query_rewriter = QueryRewriter()