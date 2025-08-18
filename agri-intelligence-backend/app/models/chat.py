"""
💬 CHAT MODELS - THE ULTIMATE CONVERSATIONAL AI SYSTEM
===========================================================

Perfect chat sessions and messages for authenticated agricultural conversations

Features:
- Session-based conversations with unique IDs
- User authentication required
- Message history tracking
- Agricultural context preservation
- Metadata for analytics

Created with ❤️ for seamless farmer conversations
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON, Float
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.models.base import Base, GUID

class ChatSession(Base):
    """
    🗨️ CHAT SESSION MODEL
    
    Represents a conversation session between user and agricultural AI
    """
    __tablename__ = "chat_sessions"
    
    # Primary fields
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID(), ForeignKey("users.id"), nullable=False)
    
    # Session metadata
    title = Column(String(255), nullable=True)  # Auto-generated from first message
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)
    
    # Agricultural context
    primary_topic = Column(String(100), nullable=True)  # crop_management, pest_control, etc.
    location_context = Column(JSON, nullable=True)  # Farmer's location data
    language_preference = Column(String(20), default='english')
    
    # Analytics
    message_count = Column(Integer, default=0)
    total_tokens_used = Column(Integer, default=0)
    satisfaction_rating = Column(Integer, nullable=True)  # 1-5 stars
    
    # Relationships
    user = relationship("User", back_populates="chat_sessions")
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<ChatSession(id={self.id}, user_id={self.user_id}, title='{self.title}')>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'ended_at': self.ended_at.isoformat() if self.ended_at else None,
            'primary_topic': self.primary_topic,
            'location_context': self.location_context,
            'language_preference': self.language_preference,
            'message_count': self.message_count,
            'total_tokens_used': self.total_tokens_used,
            'satisfaction_rating': self.satisfaction_rating
        }

class ChatMessage(Base):
    """
    💬 CHAT MESSAGE MODEL
    
    Individual messages within a chat session
    """
    __tablename__ = "chat_messages"
    
    # Primary fields
    id = Column(Integer, primary_key=True)
    session_id = Column(GUID(), ForeignKey("chat_sessions.id"), nullable=False)
    
    # Message content
    role = Column(String(20), nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    original_language = Column(String(20), nullable=True)
    translated_content = Column(Text, nullable=True)  # English translation if needed
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    tokens_used = Column(Integer, default=0)
    processing_time = Column(Float, default=0.0)
    confidence_score = Column(Float, nullable=True)
    
    # Agricultural context
    detected_topic = Column(String(100), nullable=True)
    expert_consulted = Column(String(100), nullable=True)
    tools_used = Column(JSON, nullable=True)  # List of tools used for this response
    
    # Quality metrics
    fact_check_status = Column(String(20), default='approved')  # approved, corrected, flagged
    accuracy_score = Column(Float, nullable=True)
    user_feedback = Column(String(20), nullable=True)  # thumbs_up, thumbs_down
    
    # Relationships
    session = relationship("ChatSession", back_populates="messages")
    
    def __repr__(self):
        return f"<ChatMessage(id={self.id}, session_id={self.session_id}, role='{self.role}')>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'session_id': self.session_id,
            'role': self.role,
            'content': self.content,
            'original_language': self.original_language,
            'translated_content': self.translated_content,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'tokens_used': self.tokens_used,
            'processing_time': self.processing_time,
            'confidence_score': self.confidence_score,
            'detected_topic': self.detected_topic,
            'expert_consulted': self.expert_consulted,
            'tools_used': self.tools_used,
            'fact_check_status': self.fact_check_status,
            'accuracy_score': self.accuracy_score,
            'user_feedback': self.user_feedback
        }
