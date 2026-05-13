from pydantic import BaseModel
from typing import Optional, List, Any


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = "default"


class ChatResponse(BaseModel):
    response: str
    tools_used: List[str] = []
    execution_time_ms: float = 0
    filtered: bool = False
    metadata: Optional[dict] = None


class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
