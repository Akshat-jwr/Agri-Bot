"""
💬 CHAT SERVICE - THE ULTIMATE CONVERSATION ENGINE
==================================================

Complete business logic for chat sessions and messages with:
- Session management and authentication
- Message processing with AI integration  
- Chat history context for conversations
- Analytics and performance tracking

The most advanced agricultural chat system ever built! 🌾🤖
"""

import logging
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import desc, func, select

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
    🧠 ULTIMATE CHAT SERVICE
    
    Handles all chat operations with perfect authentication and context management
    """
    
    def __init__(self):
        self.max_session_history = 20  # Maximum messages to keep in context
        self.session_timeout_hours = 24  # Auto-close sessions after 24 hours
    
    # 🚀 SESSION MANAGEMENT
    async def create_session(self, db: AsyncSession, user_id: int, session_data: ChatSessionCreate) -> ChatSession:
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
            logger.error(f"❌ Failed to create chat session: {e}")
            db.rollback()
            raise
    
    def get_user_sessions(self, db: AsyncSession, user_id: int, 
                         limit: int = 20, offset: int = 0) -> Tuple[List[ChatSession], int]:
        """
        Get all chat sessions for a user with pagination
        """
        try:
            # Get sessions
            sessions = db.query(ChatSession).filter(
                ChatSession.user_id == user_id
            ).order_by(desc(ChatSession.updated_at)).offset(offset).limit(limit).all()
            
            # Get total count
            total_count = db.query(ChatSession).filter(
                ChatSession.user_id == user_id
            ).count()
            
            return sessions, total_count
            
        except Exception as e:
            logger.error(f"❌ Failed to get user sessions: {e}")
            return [], 0
    
    def get_session(self, db: AsyncSession, session_id: str, user_id: int) -> Optional[ChatSession]:
        """
        Get a specific session (with user ownership verification)
        """
        try:
            session = db.query(ChatSession).filter(
                ChatSession.id == session_id,
                ChatSession.user_id == user_id
            ).first()
            
            return session
            
        except Exception as e:
            logger.error(f"❌ Failed to get session: {e}")
            return None
    
    def update_session(self, db: AsyncSession, session_id: str, user_id: int, 
                      update_data: ChatSessionUpdate) -> Optional[ChatSession]:
        """
        Update session details
        """
        try:
            session = self.get_session(db, session_id, user_id)
            if not session:
                return None
            
            # Update fields
            if update_data.title is not None:
                session.title = update_data.title
            if update_data.is_active is not None:
                session.is_active = update_data.is_active
                if not update_data.is_active:
                    session.ended_at = datetime.utcnow()
            if update_data.satisfaction_rating is not None:
                session.satisfaction_rating = update_data.satisfaction_rating
            if update_data.location_context is not None:
                session.location_context = update_data.location_context
            
            session.updated_at = datetime.utcnow()
            
            db.commit()
            db.refresh(session)
            
            logger.info(f"✅ Updated session {session_id}")
            return session
            
        except Exception as e:
            logger.error(f"❌ Failed to update session: {e}")
            db.rollback()
            return None
    
    def delete_session(self, db: AsyncSession, session_id: str, user_id: int) -> bool:
        """
        Delete a chat session and all its messages
        """
        try:
            session = self.get_session(db, session_id, user_id)
            if not session:
                return False
            
            db.delete(session)
            db.commit()
            
            logger.info(f"✅ Deleted session {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to delete session: {e}")
            db.rollback()
            return False
    
    # 💬 MESSAGE MANAGEMENT
    async def send_message(self, db: AsyncSession, user_id: int, 
                          message_data: ChatMessageCreate) -> Tuple[ChatMessage, ChatMessage]:
        """
        🎯 SEND MESSAGE AND GET AI RESPONSE
        
        This is the main function that:
        1. Validates session ownership
        2. Saves user message
        3. Gets chat history for context
        4. Calls AI with conversation history
        5. Saves AI response
        6. Updates session metadata
        
        Returns: (user_message, ai_response)
        """
        try:
            start_time = datetime.utcnow()
            
            # 1. Verify session ownership
            session = self.get_session(db, message_data.session_id, user_id)
            if not session:
                raise ValueError("Session not found or access denied")
            
            if not session.is_active:
                raise ValueError("Session is not active")
            
            # 2. Save user message
            user_message = ChatMessage(
                session_id=session.id,
                role=MessageRole.USER,
                content=message_data.content,
                created_at=datetime.utcnow()
            )
            
            db.add(user_message)
            db.flush()  # Get the ID without committing
            
            # 3. Get conversation history for context
            chat_history = self._get_chat_history(db, session.id)
            
            # 4. Call AI with conversation context
            ai_response_data = await self._process_ai_response(
                query=message_data.content,
                chat_history=chat_history,
                session_context={
                    'user_id': user_id,
                    'session_id': session.id,
                    'language_preference': session.language_preference,
                    'location_context': session.location_context,
                    'primary_topic': session.primary_topic
                }
            )
            
            # 5. Save AI response
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            ai_message = ChatMessage(
                session_id=session.id,
                role=MessageRole.ASSISTANT,
                content=ai_response_data['response'],
                original_language=ai_response_data.get('original_language'),
                translated_content=ai_response_data.get('english_response'),
                created_at=datetime.utcnow(),
                tokens_used=ai_response_data.get('tokens_used', 0),
                processing_time=processing_time,
                confidence_score=ai_response_data.get('confidence_score'),
                detected_topic=ai_response_data.get('detected_topic'),
                expert_consulted=ai_response_data.get('expert_consulted'),
                tools_used=ai_response_data.get('tools_used', []),
                fact_check_status=ai_response_data.get('fact_check_status', 'approved'),
                accuracy_score=ai_response_data.get('accuracy_score')
            )
            
            db.add(ai_message)
            
            # 6. Update session metadata
            session.message_count += 2  # User + AI message
            session.total_tokens_used += ai_response_data.get('tokens_used', 0)
            session.updated_at = datetime.utcnow()
            
            # Update primary topic if detected
            if ai_response_data.get('detected_topic') and not session.primary_topic:
                session.primary_topic = ai_response_data['detected_topic']
            
            # Auto-generate title from first user message
            if not session.title or "Agricultural Chat" in session.title:
                session.title = self._generate_session_title(message_data.content)
            
            db.commit()
            db.refresh(user_message)
            db.refresh(ai_message)
            
            logger.info(f"✅ Processed message in session {session.id} - {processing_time:.2f}s")
            return user_message, ai_message
            
        except Exception as e:
            logger.error(f"❌ Failed to send message: {e}")
            db.rollback()
            raise
    
    def get_session_messages(self, db: AsyncSession, session_id: str, user_id: int,
                           limit: int = 50, offset: int = 0) -> List[ChatMessage]:
        """
        Get messages for a session with pagination
        """
        try:
            # Verify session ownership
            session = self.get_session(db, session_id, user_id)
            if not session:
                return []
            
            messages = db.query(ChatMessage).filter(
                ChatMessage.session_id == session_id
            ).order_by(ChatMessage.created_at).offset(offset).limit(limit).all()
            
            return messages
            
        except Exception as e:
            logger.error(f"❌ Failed to get session messages: {e}")
            return []
    
    def add_message_feedback(self, db: AsyncSession, message_id: int, user_id: int, 
                           feedback: str) -> bool:
        """
        Add user feedback to a message
        """
        try:
            # Get message and verify session ownership
            message = db.query(ChatMessage).join(ChatSession).filter(
                ChatMessage.id == message_id,
                ChatSession.user_id == user_id,
                ChatMessage.role == MessageRole.ASSISTANT  # Only allow feedback on AI responses
            ).first()
            
            if not message:
                return False
            
            message.user_feedback = feedback
            db.commit()
            
            logger.info(f"✅ Added feedback '{feedback}' to message {message_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to add message feedback: {e}")
            db.rollback()
            return False
    
    # 🧠 PRIVATE HELPER METHODS
    def _get_chat_history(self, db: AsyncSession, session_id: str) -> List[Dict[str, Any]]:
        """
        Get recent chat history for conversation context
        """
        try:
            messages = db.query(ChatMessage).filter(
                ChatMessage.session_id == session_id
            ).order_by(desc(ChatMessage.created_at)).limit(self.max_session_history).all()
            
            # Reverse to get chronological order
            messages.reverse()
            
            history = []
            for msg in messages:
                history.append({
                    'role': msg.role,
                    'content': msg.content,
                    'timestamp': msg.created_at.isoformat(),
                    'detected_topic': msg.detected_topic
                })
            
            return history
            
        except Exception as e:
            logger.error(f"❌ Failed to get chat history: {e}")
            return []
    
    async def _process_ai_response(self, query: str, chat_history: List[Dict[str, Any]], 
                                 session_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process AI response with conversation context
        """
        try:
            # Enhance the query with conversation context
            context_enhanced_query = self._enhance_query_with_context(query, chat_history)
            
            # Call the RAG orchestrator
            result = await process_agricultural_query(context_enhanced_query)
            
            if result and result.get('success'):
                return {
                    'response': result['response'],
                    'english_response': result.get('english_response'),
                    'original_language': result.get('metadata', {}).get('original_language'),
                    'tokens_used': 100,  # Estimate for now
                    'confidence_score': result.get('metadata', {}).get('confidence', 0.8),
                    'detected_topic': result.get('metadata', {}).get('query_category'),
                    'expert_consulted': result.get('metadata', {}).get('expert_consulted'),
                    'tools_used': result.get('metadata', {}).get('tools_used', []),
                    'fact_check_status': result.get('metadata', {}).get('fact_check_status', 'approved'),
                    'accuracy_score': result.get('metadata', {}).get('accuracy_score')
                }
            else:
                # Fallback response
                return {
                    'response': "I apologize, but I'm unable to process your agricultural query at the moment. Please try again or contact support.",
                    'tokens_used': 50,
                    'confidence_score': 0.0,
                    'fact_check_status': 'approved'
                }
                
        except Exception as e:
            logger.error(f"❌ AI processing failed: {e}")
            return {
                'response': "I'm experiencing technical difficulties. Please try again later.",
                'tokens_used': 30,
                'confidence_score': 0.0,
                'fact_check_status': 'approved'
            }
    
    def _enhance_query_with_context(self, query: str, chat_history: List[Dict[str, Any]]) -> str:
        """
        Enhance user query with conversation context for better AI responses
        """
        if not chat_history:
            return query
        
        # Build context from recent messages
        context_parts = []
        
        # Get last few exchanges for context
        recent_history = chat_history[-6:]  # Last 3 user + 3 AI messages
        
        if recent_history:
            context_parts.append("Previous conversation context:")
            for msg in recent_history:
                role_prefix = "Farmer" if msg['role'] == 'user' else "AI"
                context_parts.append(f"{role_prefix}: {msg['content'][:100]}...")
        
        context_parts.append(f"\\nCurrent question: {query}")
        
        return "\\n".join(context_parts)
    
    def _generate_session_title(self, first_message: str) -> str:
        """
        Generate a meaningful session title from the first message
        """
        # Extract key agricultural terms
        keywords = ['crop', 'pest', 'disease', 'fertilizer', 'irrigation', 'harvest', 
                   'seed', 'soil', 'weather', 'market', 'price', 'yield']
        
        words = first_message.lower().split()
        found_keywords = [word for word in words if any(kw in word for kw in keywords)]
        
        if found_keywords:
            title = f"Agricultural Help: {' '.join(found_keywords[:3]).title()}"
        else:
            title = f"Agricultural Chat - {datetime.now().strftime('%Y-%m-%d')}"
        
        return title[:50]  # Limit title length
    
    # 📊 ANALYTICS METHODS
    def get_user_chat_analytics(self, db: AsyncSession, user_id: int) -> Dict[str, Any]:
        """
        Get chat analytics for a specific user
        """
        try:
            # Basic session stats
            total_sessions = db.query(ChatSession).filter(ChatSession.user_id == user_id).count()
            active_sessions = db.query(ChatSession).filter(
                ChatSession.user_id == user_id,
                ChatSession.is_active == True
            ).count()
            
            # Message stats
            total_messages = db.query(ChatMessage).join(ChatSession).filter(
                ChatSession.user_id == user_id
            ).count()
            
            # Recent activity (last 30 days)
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            recent_sessions = db.query(ChatSession).filter(
                ChatSession.user_id == user_id,
                ChatSession.created_at >= thirty_days_ago
            ).count()
            
            return {
                'total_sessions': total_sessions,
                'active_sessions': active_sessions,
                'total_messages': total_messages,
                'recent_sessions_30d': recent_sessions,
                'average_messages_per_session': total_messages / max(total_sessions, 1)
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get chat analytics: {e}")
            return {}

# Global instance
chat_service = ChatService()
