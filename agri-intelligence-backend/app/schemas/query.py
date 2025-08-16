from pydantic import BaseModel, Field
from typing import List, Optional

class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000, description="Your agricultural question")
    session_id: Optional[str] = None

class QueryResponse(BaseModel):
    answer: str
    confidence: float
    sources: List[str] = []
    processing_time: float
    user_location: Optional[str] = None
