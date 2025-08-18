"""
💬 CHAT SCHEMAS - PERFECT API VALIDATION
==========================================

Pydantic schemas for chat sessions and messages with comprehensive validation

Features:
- Session creation and management
- Message validation and formatting
- Response models with metadata
- Error handling schemas

Built for bulletproof API validation! 🛡️
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

# Enums for validation
class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"

class FeedbackType(str, Enum):
    THUMBS_UP = "thumbs_up"
    THUMBS_DOWN = "thumbs_down"

class FactCheckStatus(str, Enum):
    APPROVED = "approved"
    CORRECTED = "corrected"
    FLAGGED = "flagged"

# 🚀 SESSION SCHEMAS
class ChatSessionCreate(BaseModel):
    """Schema for creating a new chat session"""
    title: Optional[str] = Field(None, max_length=255, description="Optional session title")
    location_context: Optional[Dict[str, Any]] = Field(None, description="Farmer's location data")
    language_preference: str = Field(default="english", description="Preferred language for responses")
    
    @validator('language_preference')
    def validate_language(cls, v):
        allowed_languages = [
            'english', 'hindi', 'punjabi', 'bengali', 'tamil', 'telugu', 
            'kannada', 'malayalam', 'gujarati', 'marathi', 'odia', 'bhojpuri',
            'hinglish', 'punglish', 'bengalish'
        ]
        if v.lower() not in allowed_languages:
            raise ValueError(f'Language must be one of: {", ".join(allowed_languages)}')
        return v.lower()

class ChatSessionResponse(BaseModel):
    """Schema for chat session response"""
    id: str
    user_id: str  # Fixed: UUID fields should be strings
    title: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    ended_at: Optional[datetime]
    primary_topic: Optional[str]
    location_context: Optional[Dict[str, Any]]
    language_preference: str
    message_count: int
    total_tokens_used: int
    satisfaction_rating: Optional[int]

    @validator('id', 'user_id', pre=True)
    def convert_uuid_to_str(cls, v):
        """Convert UUID objects to strings"""
        return str(v) if v is not None else v

    class Config:
        from_attributes = True

class ChatSessionUpdate(BaseModel):
    """Schema for updating a chat session"""
    title: Optional[str] = Field(None, max_length=255)
    is_active: Optional[bool] = None
    satisfaction_rating: Optional[int] = Field(None, ge=1, le=5)
    location_context: Optional[Dict[str, Any]] = None

# 💬 MESSAGE SCHEMAS
class ChatMessageCreate(BaseModel):
    """Schema for creating a new chat message"""
    session_id: str = Field(..., description="Chat session ID")
    content: str = Field(..., min_length=1, max_length=5000, description="Message content")
    
    @validator('content')
    def validate_content(cls, v):
        if not v.strip():
            raise ValueError('Message content cannot be empty')
        return v.strip()

class ChatMessageResponse(BaseModel):
    """Schema for chat message response"""
    id: int
    session_id: str
    role: MessageRole
    content: str
    original_language: Optional[str]
    translated_content: Optional[str]
    created_at: datetime
    tokens_used: int
    processing_time: float
    confidence_score: Optional[float]
    detected_topic: Optional[str]
    expert_consulted: Optional[str]
    tools_used: Optional[List[str]]
    fact_check_status: FactCheckStatus
    accuracy_score: Optional[float]
    user_feedback: Optional[FeedbackType]

    @validator('session_id', pre=True)
    def convert_session_uuid_to_str(cls, v):
        """Convert UUID objects to strings"""
        return str(v) if v is not None else v

    class Config:
        from_attributes = True

class ChatMessageFeedback(BaseModel):
    """Schema for message feedback"""
    feedback: FeedbackType = Field(..., description="User feedback on the message")

# 🗨️ CONVERSATION SCHEMAS
class ChatConversationResponse(BaseModel):
    """Schema for full conversation response"""
    session: ChatSessionResponse
    messages: List[ChatMessageResponse]
    
    class Config:
        from_attributes = True

class ChatHistoryRequest(BaseModel):
    """Schema for chat history context"""
    session_id: str = Field(..., description="Session ID for context")
    limit: int = Field(default=10, ge=1, le=50, description="Number of recent messages to include")

# 🎯 CHAT ANALYTICS SCHEMAS
class ChatAnalytics(BaseModel):
    """Schema for chat analytics"""
    total_sessions: int
    active_sessions: int
    total_messages: int
    average_session_length: float
    most_common_topics: List[Dict[str, Any]]
    language_distribution: Dict[str, int]
    satisfaction_scores: Dict[str, int]

# 🚨 ERROR SCHEMAS
class ChatError(BaseModel):
    """Schema for chat-related errors"""
    error_type: str
    message: str
    session_id: Optional[str] = None
    details: Optional[Dict[str, Any]] = None

# 📊 RESPONSE WRAPPERS
class ChatSessionListResponse(BaseModel):
    """Schema for listing chat sessions"""
    sessions: List[ChatSessionResponse]
    total_count: int
    page: int
    page_size: int
    has_next: bool

class ChatSuccessResponse(BaseModel):
    """Generic success response for chat operations"""
    success: bool = True
    message: str
    data: Optional[Dict[str, Any]] = None
