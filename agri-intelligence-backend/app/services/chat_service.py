"""
💬 FIXED CHAT SERVICE - ASYNC DATABASE OPERATIONS
=================================================

Complete business logic for chat sessions and messages with:
- PROPER async/await database operations
- Session management and authentication
- Message processing with AI integration  
- Chat history context for conversations

Now with PERFECT async SQLAlchemy patterns! 🚀
"""

import logging
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import desc, func, select, delete, update

from app.models.chat import ChatSession, ChatMessage
from app.models.user import User
from app.schemas.chat import (
    ChatSessionCreate, ChatSessionUpdate, ChatMessageCreate, 
    MessageRole, FactCheckStatus
)
from app.tools.rag_core.simple_rag_orchestrator import process_agricultural_query

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChatService:
    """
    🧠 FIXED CHAT SERVICE WITH PROPER ASYNC OPERATIONS
    
    Handles all chat operations with perfect async database patterns
    """
    
    def __init__(self):
        self.max_session_history = 20  # Maximum messages to keep in context
        self.session_timeout_hours = 24  # Auto-close sessions after 24 hours
    
    # 🚀 SESSION MANAGEMENT
    async def create_session(self, db: AsyncSession, user_id: str, session_data: ChatSessionCreate) -> ChatSession:
        """
        Create a new chat session for authenticated user
        """
        try:
            # Verify user exists and is active
            result = await db.execute(
                select(User).filter(
                    User.id == user_id, 
                    User.is_active == True,
                    User.is_verified == True
                )
            )
            user = result.scalar_one_or_none()
            
            if not user:
                raise ValueError("User not found or not verified")
            
            # Create new session
            session = ChatSession(
                user_id=user_id,
                title=session_data.title or f"Agricultural Chat - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                location_context=session_data.location_context,
                language_preference=session_data.language_preference,
                is_active=True
            )
            
            db.add(session)
            await db.commit()
            await db.refresh(session)
            
            logger.info(f"✅ Created chat session {session.id} for user {user_id}")
            return session
            
        except Exception as e:
            logger.error(f"❌ Failed to create session: {e}")
            await db.rollback()
            raise e
    
    async def get_user_sessions(self, db: AsyncSession, user_id: str, 
                               skip: int = 0, limit: int = 20) -> Tuple[List[ChatSession], int]:
        """Get all sessions for a user with pagination"""
        try:
            # Get sessions with async execution
            result = await db.execute(
                select(ChatSession)
                .filter(ChatSession.user_id == user_id)
                .order_by(desc(ChatSession.updated_at))
                .offset(skip)
                .limit(limit)
            )
            sessions = result.scalars().all()
            
            # Get total count
            count_result = await db.execute(
                select(func.count(ChatSession.id))
                .filter(ChatSession.user_id == user_id)
            )
            total_count = count_result.scalar()
            
            return list(sessions), total_count
            
        except Exception as e:
            logger.error(f"❌ Failed to get user sessions: {e}")
            raise e
    
    async def get_session(self, db: AsyncSession, session_id: str, user_id: str) -> Optional[ChatSession]:
        """Get a specific session by ID for the user"""
        try:
            result = await db.execute(
                select(ChatSession)
                .filter(
                    ChatSession.id == session_id,
                    ChatSession.user_id == user_id
                )
            )
            return result.scalar_one_or_none()
            
        except Exception as e:
            logger.error(f"❌ Failed to get session: {e}")
            raise e
    
    async def get_session_messages(self, db: AsyncSession, session_id: str, user_id: str, 
                                 limit: int = 50, offset: int = 0) -> List[ChatMessage]:
        """Get messages for a specific session with pagination"""
        try:
            # First verify the session belongs to the user
            session = await self.get_session(db, session_id, user_id)
            if not session:
                raise ValueError("Session not found or access denied")
            
            # Get messages with pagination
            result = await db.execute(
                select(ChatMessage)
                .filter(ChatMessage.session_id == session_id)
                .order_by(ChatMessage.created_at.asc())  # Oldest first for conversation flow
                .offset(offset)
                .limit(limit)
            )
            messages = result.scalars().all()
            
            logger.info(f"📜 Retrieved {len(messages)} messages for session {session_id}")
            return list(messages)
            
        except Exception as e:
            logger.error(f"❌ Failed to get session messages: {e}")
            raise e
    
    async def update_session(self, db: AsyncSession, session_id: str, user_id: str, 
                           update_data: ChatSessionUpdate) -> Optional[ChatSession]:
        """
        Update a chat session (title, status, satisfaction rating, etc.)
        """
        try:
            # First verify the session belongs to the user
            session = await self.get_session(db, session_id, user_id)
            if not session:
                return None
            
            # Update fields from update_data
            update_dict = {}
            if update_data.title is not None:
                update_dict['title'] = update_data.title
            if update_data.is_active is not None:
                update_dict['is_active'] = update_data.is_active
            if update_data.satisfaction_rating is not None:
                update_dict['satisfaction_rating'] = update_data.satisfaction_rating
            if update_data.language_preference is not None:
                update_dict['language_preference'] = update_data.language_preference
            
            # Always update the timestamp
            update_dict['updated_at'] = datetime.utcnow()
            
            # If ending the session
            if update_data.is_active is False:
                update_dict['ended_at'] = datetime.utcnow()
            
            # Perform the update
            await db.execute(
                update(ChatSession)
                .where(ChatSession.id == session_id)
                .values(**update_dict)
            )
            await db.commit()
            
            # Fetch and return updated session
            updated_session = await self.get_session(db, session_id, user_id)
            logger.info(f"✅ Updated session {session_id}")
            return updated_session
            
        except Exception as e:
            logger.error(f"❌ Failed to update session: {e}")
            await db.rollback()
            raise e
    
    async def delete_session(self, db: AsyncSession, session_id: str, user_id: str) -> bool:
        """
        Delete a chat session and all its messages (CASCADE delete)
        """
        try:
            # First verify the session belongs to the user
            session = await self.get_session(db, session_id, user_id)
            if not session:
                return False
            
            # Delete messages first (explicit cleanup)
            await db.execute(
                delete(ChatMessage)
                .where(ChatMessage.session_id == session_id)
            )
            
            # Delete the session
            await db.execute(
                delete(ChatSession)
                .where(ChatSession.id == session_id)
            )
            
            await db.commit()
            logger.info(f"✅ Deleted session {session_id} and all its messages")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to delete session: {e}")
            await db.rollback()
            return False
    
    async def send_message(self, db: AsyncSession, user_id: str, 
                          message_data: ChatMessageCreate) -> Tuple[ChatMessage, ChatMessage]:
        """
        Send a message and get AI response with conversation context
        """
        try:
            # Verify session exists and belongs to user
            session = await self.get_session(db, message_data.session_id, user_id)
            if not session:
                raise ValueError("Session not found or access denied")
            
            # Create user message
            user_message = ChatMessage(
                session_id=message_data.session_id,
                role=MessageRole.USER.value,  # Convert enum to string
                content=message_data.content,
                original_language=session.language_preference  # Get from session
            )
            
            # Get conversation history for context
            chat_history = await self._get_chat_history(db, message_data.session_id)
            
            # Enhance query with conversation context
            enhanced_query = self._enhance_query_with_context(
                message_data.content, 
                chat_history, 
                session.language_preference  # Get from session
            )
            
            # Process with RAG system
            ai_response = await process_agricultural_query(enhanced_query)
            
            # Process AI response with metadata
            ai_content, ai_metadata = self._process_ai_response(ai_response, session.language_preference)
            
            # Create AI message
            ai_message = ChatMessage(
                session_id=message_data.session_id,
                role=MessageRole.ASSISTANT.value,  # Convert enum to string
                content=ai_content,
                original_language=session.language_preference,  # Get from session
                processing_time=ai_metadata.get('processing_time', 0.0),
                fact_check_status=ai_metadata.get('fact_check_status', 'approved'),
                confidence_score=ai_metadata.get('confidence_score', 0.9),
                expert_consulted=ai_metadata.get('expert_consulted', 'general-agriculture'),
                tools_used=ai_metadata.get('sources_used', [])
            )
            
            # Save both messages
            db.add(user_message)
            db.add(ai_message)
            
            # Update session
            await db.execute(
                update(ChatSession)
                .where(ChatSession.id == message_data.session_id)
                .values(
                    updated_at=datetime.utcnow(),
                    message_count=ChatSession.message_count + 2
                )
            )
            
            await db.commit()
            await db.refresh(user_message)
            await db.refresh(ai_message)
            
            logger.info(f"✅ Processed message in session {message_data.session_id}")
            return user_message, ai_message
            
        except Exception as e:
            logger.error(f"❌ Failed to send message: {e}")
            await db.rollback()
            raise e
    
    async def _get_chat_history(self, db: AsyncSession, session_id: str) -> List[Dict[str, Any]]:
        """Get recent chat history for context"""
        try:
            result = await db.execute(
                select(ChatMessage)
                .filter(ChatMessage.session_id == session_id)
                .order_by(desc(ChatMessage.created_at))
                .limit(self.max_session_history)
            )
            messages = result.scalars().all()
            
            return [
                {
                    "role": msg.role,  # Already a string in database
                    "content": msg.content,
                    "timestamp": msg.created_at.isoformat()
                }
                for msg in reversed(messages)  # Chronological order
            ]
            
        except Exception as e:
            logger.error(f"❌ Failed to get chat history: {e}")
            return []
    
    def _enhance_query_with_context(self, query: str, chat_history: List[Dict], 
                                   language: str = None) -> str:
        """Enhance query with conversation context"""
        if not chat_history:
            return query
        
        # Build context from recent messages
        context_parts = []
        for msg in chat_history[-5:]:  # Last 5 messages for context
            role = "User" if msg["role"] == "user" else "Assistant"
            context_parts.append(f"{role}: {msg['content'][:100]}...")
        
        context_str = "\n".join(context_parts)
        
        enhanced_query = f"""
Previous conversation context:
{context_str}

Current query: {query}

Please provide a response that takes into account the conversation history above.
"""
        return enhanced_query
    
    def _process_ai_response(self, ai_response: Dict[str, Any], 
                           language: str = None) -> Tuple[str, Dict[str, Any]]:
        """Process AI response and extract metadata"""
        
        # Extract content
        content = ai_response.get('response', ai_response.get('answer', 'No response available'))
        
        # Extract metadata
        metadata = {
            'model_used': ai_response.get('model_used', 'agricultural-expert'),
            'processing_time': ai_response.get('processing_time', 0.0),
            'confidence_score': ai_response.get('confidence_score', 0.9),
            'fact_check_status': FactCheckStatus.APPROVED,
            'sources_used': ai_response.get('sources', []),
            'expert_consulted': ai_response.get('expert_type', 'general-agriculture')
        }
        
        return content, metadata

# Global instance
chat_service = ChatService()
