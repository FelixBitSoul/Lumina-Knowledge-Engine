from pydantic import BaseModel
from typing import Optional


class ChatRequest(BaseModel):
    """Schema for chat request"""
    message: str
    conversation_id: Optional[str] = None
    collection: Optional[str] = None


class ChatResponse(BaseModel):
    """Schema for chat response"""
    id: str
    content: str
    conversation_id: str
    timestamp: int