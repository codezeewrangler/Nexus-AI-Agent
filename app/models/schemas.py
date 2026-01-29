# app/models/schemas.py

from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from datetime import datetime


class DocumentUploadResponse(BaseModel):
    document_id: str
    filename: str
    size_bytes: int
    chunk_count: int
    upload_time: datetime


class QueryRequest(BaseModel):
    query: str = Field(..., min_length=3, max_length=500)
    document_id: Optional[str] = None
    top_k: int = Field(default=5, ge=1, le=10)
    
    @field_validator('query')
    @classmethod
    def query_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError('Query cannot be empty')
        return v.strip()


class SourceChunk(BaseModel):
    content: str
    similarity: float
    chunk_id: str
    page_number: Optional[int] = None


class QueryResponse(BaseModel):
    answer: str
    sources: List[SourceChunk]
    query_time_ms: float
    model_used: str
    tokens_used: int


class HealthResponse(BaseModel):
    status: str
    documents_stored: int
