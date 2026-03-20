from pydantic import BaseModel


class DocumentCreate(BaseModel):
    """Schema for document creation"""
    url: str
    title: str
    content: str
