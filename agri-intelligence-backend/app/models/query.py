from sqlalchemy import Column, String, Text, JSON, Float
from app.models.base import BaseModel, GUID

class QueryHistory(BaseModel):
    __tablename__ = "query_history"
    
    user_id = Column(GUID(), nullable=True)
    session_id = Column(String(255), nullable=True)
    
    # Query data
    query_text = Column(Text, nullable=False)
    response_text = Column(Text, nullable=True)
    query_type = Column(String(50), nullable=True)
    confidence_score = Column(Float, nullable=True)
    
    # Metadata
    processing_time = Column(Float, nullable=True)
    sources_used = Column(JSON, default=list)
