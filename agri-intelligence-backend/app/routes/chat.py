"""
💬 CHAT API ROUTES - THE ULTIMATE CONVERSATION ENDPOINTS
========================================================

Perfect RESTfu        session = await chat_service.get_session(
            db=db,
            session_id=session_id,
            user_id=str(current_user.id)
        ) for chat sessions and messages with:
- Full authentication required for all endpoints
- Session management with user ownership verification
- Real-time message processing with AI integration
- Chat history and analytics endpoints

The most secure and feature-complete chat API ever! 🔐🚀
"""

import logging
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.chat import (
    ChatSessionCreate, ChatSessionResponse, ChatSessionUpdate, ChatSessionListResponse,
    ChatMessageCreate, ChatMessageResponse, ChatConversationResponse,
    ChatMessageFeedback, ChatSuccessResponse, ChatAnalytics
)
from app.services.chat_service import chat_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/chat", tags=["💬 Agricultural Chat"])

# 🚀 CHAT SESSION ENDPOINTS

@router.post("/sessions", response_model=ChatSessionResponse)
async def create_chat_session(
    session_data: ChatSessionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    🆕 CREATE NEW CHAT SESSION
    
    Creates a new chat session for the authenticated user.
    Only verified users can create chat sessions.
    """
    try:
        logger.info(f"🆕 Creating chat session for user {current_user.id}")
        
        session = await chat_service.create_session(
            db=db,
            user_id=str(current_user.id),  # Convert UUID to string
            session_data=session_data
        )
        
        logger.info(f"✅ Created session {session.id} for user {current_user.id}")
        return session
        
    except ValueError as e:
        logger.error(f"❌ Session creation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"❌ Unexpected error creating session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create chat session"
        )

@router.get("/sessions", response_model=ChatSessionListResponse)
async def get_user_chat_sessions(
    page: int = 1,
    page_size: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    📋 GET USER CHAT SESSIONS
    
    Retrieves all chat sessions for the authenticated user with pagination.
    """
    try:
        if page < 1 or page_size < 1 or page_size > 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid pagination parameters"
            )
        
        offset = (page - 1) * page_size
        
        sessions, total = await chat_service.get_user_sessions(
            db=db,
            user_id=str(current_user.id),
            skip=offset,
            limit=page_size
        )
        
        has_next = offset + page_size < total
        
        return ChatSessionListResponse(
            sessions=sessions,
            total_count=total,
            page=page,
            page_size=page_size,
            has_next=has_next
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to get user sessions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve chat sessions"
        )

@router.get("/sessions/{session_id}", response_model=ChatSessionResponse)
async def get_chat_session(
    session_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    📖 GET SPECIFIC CHAT SESSION
    
    Retrieves a specific chat session. User must own the session.
    """
    try:
        session = chat_service.get_session(
            db=db,
            session_id=session_id,
            user_id=current_user.id
        )
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat session not found"
            )
        
        return session
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to get session {session_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve chat session"
        )

@router.put("/sessions/{session_id}", response_model=ChatSessionResponse)
async def update_chat_session(
    session_id: str,
    update_data: ChatSessionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    ✏️ UPDATE CHAT SESSION
    
    Updates session details like title, status, or satisfaction rating.
    """
    try:
        session = chat_service.update_session(
            db=db,
            session_id=session_id,
            user_id=current_user.id,
            update_data=update_data
        )
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat session not found"
            )
        
        return session
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to update session {session_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update chat session"
        )

@router.delete("/sessions/{session_id}", response_model=ChatSuccessResponse)
async def delete_chat_session(
    session_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    🗑️ DELETE CHAT SESSION
    
    Deletes a chat session and all its messages. Cannot be undone.
    """
    try:
        success = chat_service.delete_session(
            db=db,
            session_id=session_id,
            user_id=current_user.id
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat session not found"
            )
        
        return ChatSuccessResponse(
            success=True,
            message=f"Chat session {session_id} deleted successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to delete session {session_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete chat session"
        )

# 💬 MESSAGE ENDPOINTS

@router.post("/messages", response_model=List[ChatMessageResponse])
async def send_chat_message(
    message_data: ChatMessageCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    💬 SEND CHAT MESSAGE
    
    🎯 THE MAIN CHAT ENDPOINT
    
    Sends a message and gets AI response with full conversation context.
    This is where the magic happens:
    1. Validates session ownership
    2. Saves user message
    3. Gets conversation history for context
    4. Calls AI with chat history
    5. Returns both user and AI messages
    """
    try:
        logger.info(f"💬 Processing message in session {message_data.session_id} for user {current_user.id}")
        logger.info(f"📝 Message: {message_data.content[:100]}...")
        
        # Send message and get AI response with conversation context
        user_message, ai_message = await chat_service.send_message(
            db=db,
            user_id=current_user.id,
            message_data=message_data
        )
        
        # Background task for analytics
        background_tasks.add_task(
            log_chat_analytics,
            session_id=message_data.session_id,
            user_id=current_user.id,
            message_content=message_data.content
        )
        
        logger.info(f"✅ Message processed successfully in session {message_data.session_id}")
        return [user_message, ai_message]
        
    except ValueError as e:
        logger.error(f"❌ Message validation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"❌ Failed to process message: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process message"
        )

@router.get("/sessions/{session_id}/messages", response_model=List[ChatMessageResponse])
async def get_session_messages(
    session_id: str,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    📜 GET SESSION MESSAGES
    
    Retrieves all messages for a chat session with pagination.
    """
    try:
        if limit < 1 or limit > 100 or offset < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid pagination parameters"
            )
        
        messages = chat_service.get_session_messages(
            db=db,
            session_id=session_id,
            user_id=current_user.id,
            limit=limit,
            offset=offset
        )
        
        return messages
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to get messages for session {session_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve messages"
        )

@router.get("/sessions/{session_id}/conversation", response_model=ChatConversationResponse)
async def get_full_conversation(
    session_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    🗨️ GET FULL CONVERSATION
    
    Gets complete conversation with session details and all messages.
    """
    try:
        # Get session
        session = chat_service.get_session(
            db=db,
            session_id=session_id,
            user_id=current_user.id
        )
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat session not found"
            )
        
        # Get all messages
        messages = chat_service.get_session_messages(
            db=db,
            session_id=session_id,
            user_id=current_user.id,
            limit=1000  # Get all messages
        )
        
        return ChatConversationResponse(
            session=session,
            messages=messages
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to get conversation for session {session_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve conversation"
        )

@router.post("/messages/{message_id}/feedback", response_model=ChatSuccessResponse)
async def add_message_feedback(
    message_id: int,
    feedback_data: ChatMessageFeedback,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    👍 ADD MESSAGE FEEDBACK
    
    Allows users to provide thumbs up/down feedback on AI responses.
    """
    try:
        success = chat_service.add_message_feedback(
            db=db,
            message_id=message_id,
            user_id=current_user.id,
            feedback=feedback_data.feedback
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Message not found or access denied"
            )
        
        return ChatSuccessResponse(
            success=True,
            message=f"Feedback '{feedback_data.feedback}' added successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to add feedback to message {message_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add feedback"
        )

# 📊 ANALYTICS ENDPOINTS

@router.get("/analytics", response_model=Dict[str, Any])
async def get_user_chat_analytics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    📊 GET CHAT ANALYTICS
    
    Provides analytics about user's chat usage and patterns.
    """
    try:
        analytics = chat_service.get_user_chat_analytics(
            db=db,
            user_id=current_user.id
        )
        
        return {
            "user_id": current_user.id,
            "analytics": analytics,
            "generated_at": "2025-01-18T00:00:00Z"
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to get analytics for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve analytics"
        )

# 🔧 BACKGROUND TASKS

async def log_chat_analytics(session_id: str, user_id: int, message_content: str):
    """Background task for logging chat analytics"""
    try:
        logger.info(f"📊 Chat Analytics: User {user_id} sent message in session {session_id}")
        logger.info(f"📝 Content length: {len(message_content)} characters")
        # Additional analytics logic can be added here
    except Exception as e:
        logger.error(f"❌ Analytics logging failed: {e}")

# 🏥 HEALTH CHECK

@router.get("/health")
async def chat_health_check():
    """Health check for chat system"""
    return {
        "status": "healthy",
        "service": "Agricultural Chat System",
        "features": [
            "Session management",
            "Real-time messaging",
            "AI integration",
            "Conversation context",
            "User authentication",
            "Message feedback",
            "Analytics"
        ],
        "version": "1.0.0",
        "timestamp": "2025-01-18T00:00:00Z"
    }
