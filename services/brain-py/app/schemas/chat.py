from pydantic import BaseModel
from typing import Optional

class ChatRequest(BaseModel):
    """对话请求模型"""
    message: str
    conversation_id: Optional[str] = None
    collection: str = "all"

class ChatResponse(BaseModel):
    """对话响应模型"""
    id: str
    content: str
    conversation_id: str
    timestamp: int
