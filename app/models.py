# app/models.py

from pydantic import BaseModel
from typing import Optional, Dict, Any


class AgentRequest(BaseModel):
    query: str
    user_id: Optional[str] = None
    output_format: Optional[str] = "markdown"


class AgentResponse(BaseModel):
    success: bool
    report: str
    metadata: Dict[str, Any]
