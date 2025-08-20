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
from app.tools.rag_core.rag_orchestrator import process_agricultural_query

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
            # Use full RAG orchestrator (multilingual + tool orchestration)
            ai_response = await process_agricultural_query(
                enhanced_query,
                farmer_context={
                    'session_language': session.language_preference,
                    'location': session.location_context
                }
            )
            
            # Process AI response with metadata
            ai_content, ai_metadata = self._process_ai_response(ai_response, session.language_preference)

            # Derive extended metadata for new ChatMessage fields
            fused_context = ai_response.get('fused_context')
            # Defensive attribute access helper
            def _ctx(obj, attr, default=None):
                try:
                    return getattr(obj, attr)
                except Exception:
                    return default

            weather_ctx = _ctx(fused_context, 'weather_intelligence', {}) if fused_context else {}
            market_ctx = _ctx(fused_context, 'market_intelligence', {}) if fused_context else {}
            agri_ctx = _ctx(fused_context, 'agricultural_data', {}) if fused_context else {}
            govt_ctx = _ctx(fused_context, 'government_info', {}) if fused_context else {}
            web_ctx = _ctx(fused_context, 'web_intelligence', {}) if fused_context else {}
            # Prefer structured latest_info over legacy latest_info alias
            search_results = []
            if isinstance(ai_response.get('response'), dict):
                resp_obj = ai_response.get('response')
                search_results = resp_obj.get('latest_info') or resp_obj.get('search_results') or []
            classification = ai_response.get('classification')

            # Build retrieval context (compact snippets for audit)
            retrieval_context = []
            def _add_ctx(name, data):
                if data:
                    retrieval_context.append({
                        'source': name,
                        'keys': list(data.keys())[:10]
                    })
            _add_ctx('weather', weather_ctx)
            _add_ctx('market', market_ctx)
            _add_ctx('agricultural', agri_ctx)
            _add_ctx('government', govt_ctx)
            _add_ctx('web_intelligence', web_ctx)

            # Citations removed: frontend can derive from web_search_results

            api_sources = {
                'weather_intelligence': weather_ctx if weather_ctx else None,
                'market_intelligence': market_ctx if market_ctx else None,
                'government_info': govt_ctx if govt_ctx else None
            }
            # Remove empty entries
            api_sources = {k: v for k, v in api_sources.items() if v}

            # sql_results removed from model
            ml_inferences = {}
            if classification:
                try:
                    ml_inferences['classification'] = {
                        'primary_category': getattr(classification, 'primary_category', None),
                        'confidence': getattr(classification, 'confidence', None)
                    }
                except Exception:
                    pass
            if isinstance(agri_ctx, dict) and 'yield_forecast' in agri_ctx:
                ml_inferences['yield_prediction'] = agri_ctx.get('yield_forecast')

            safety_labels = {'overall': 'safe'}  # Placeholder until moderation integrated

            latency_breakdown = {
                'total_processing_s': ai_response.get('processing_time'),
            }
            prompt_version = 'v1'  # Tag for reproducibility
            system_prompt_snapshot = ai_metadata.get('system_prompt', '') if isinstance(ai_metadata, dict) else ''
            
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
                tools_used=ai_metadata.get('sources_used', []),
                retrieval_context=retrieval_context or None,
                api_sources=api_sources or None,
                web_search_results=search_results if search_results else None,
                ml_inferences=ml_inferences or None,
                safety_labels=safety_labels,
                prompt_version=prompt_version,
                # system_prompt_snapshot removed
                latency_breakdown=latency_breakdown or None,
                error_details=ai_response.get('error') if not ai_response.get('success', True) else None
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
        """Process AI response and extract metadata, normalizing new orchestrator shape"""
        raw = ai_response.get('response')
        content: str
        if isinstance(raw, dict):
            # New orchestrator returns structured dict with main_answer
            content = raw.get('main_answer') or raw.get('english_main_answer') or str(raw)
        else:
            content = raw or ai_response.get('answer', 'No response available')

        metadata = {
            'model_used': ai_response.get('metadata', {}).get('model', 'agricultural-expert'),
            'processing_time': ai_response.get('processing_time', 0.0),
            'confidence_score': ai_response.get('confidence_score', 0.0),
            'fact_check_status': FactCheckStatus.APPROVED.value,
            'sources_used': ai_response.get('tools_used', []),
            'expert_consulted': (
                getattr(ai_response.get('classification'), 'primary_category', None)
                if ai_response.get('classification') is not None else 'general-agriculture'
            ) or 'general-agriculture'
        }
        return content, metadata

# Global instance
chat_service = ChatService()
