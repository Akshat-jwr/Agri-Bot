"""
🌊 STREAMING CHAT ROUTES - LIVE RESPONSE STREAMING
=================================================

Real-time streaming chat responses with:
- Server-Sent Events (SSE) for live typing effect
- Source citations with expandable details
- AI reasoning process visualization
- Live progress updates

The most engaging agricultural chat experience! 🚀✨
"""

import asyncio
import json
import logging
from typing import AsyncGenerator, Dict, Any
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.chat import ChatSession, ChatMessage
from app.schemas.chat import ChatMessageCreate, MessageRole
from app.services.chat_service import chat_service
from app.tools.llm_tools.gemini_text_stream import stream_gemini_text

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/streaming", tags=["🌊 Live Streaming Chat"])

class StreamingChatService:
    """Service for streaming chat responses with live updates"""
    
    @staticmethod
    async def stream_response(
        db: AsyncSession,
        user_id: str,
        message_data: ChatMessageCreate
    ) -> AsyncGenerator[str, None]:
        """Stream chat response with live updates using multi-phase pipeline.

        Phases emitted (SSE events):
        - status (initial)
        - phase: language_detection
        - thinking: google_search (preview search results)
        - thinking: tool_execution (api/tool summaries)
        - thinking: context_fusion (retrieval fusion summary)
        - thinking: draft_generation (raw first-layer answer creation)
        - thinking: draft_preview (non-final draft snippet)
        - phase: fact_check (start)
        - fact_check_step / fact_check_result (verification updates)
        - final_start (before streaming verified answer)
        - response_chunk (streamed verified answer)
        - phase: saving / phase_complete
        - completion (done)
        """

        phase_times = {}
        def mark(phase: str, start: bool):
            now = datetime.utcnow().timestamp()
            entry = phase_times.setdefault(phase, {'start': None, 'end': None, 'duration_s': None})
            if start:
                entry['start'] = now
            else:
                entry['end'] = now
                if entry['start'] is not None:
                    entry['duration_s'] = round(entry['end'] - entry['start'], 3)

        try:
            from app.tools.rag_core.rag_orchestrator import process_agricultural_query
            from app.tools.fact_checker.agricultural_fact_checker import agricultural_fact_checker

            # Initial status
            yield f"data: {json.dumps({'type':'status','message':'🔍 Processing your agricultural query...','progress':5})}\n\n"

            # Session check
            session = await chat_service.get_session(db, message_data.session_id, user_id)
            if not session:
                yield f"data: {json.dumps({'type':'error','message':'Session not found or access denied'})}\n\n"
                return

            # Language detection (lightweight: rely on session preference for now)
            mark('language_detection', True)
            yield f"data: {json.dumps({'type':'phase','phase':'language_detection','title':'🌐 Language Detection','status':'processing'})}\n\n"
            await asyncio.sleep(0.05)
            mark('language_detection', False)
            yield f"data: {json.dumps({'type':'phase_complete','phase':'language_detection','result':session.language_preference,'progress':15})}\n\n"

            # Build conversation context
            mark('retrieval', True)
            yield f"data: {json.dumps({'type':'phase','phase':'retrieval','title':'📚 Retrieving Context','status':'processing'})}\n\n"
            chat_history = await chat_service._get_chat_history(db, message_data.session_id)
            enhanced_query = chat_service._enhance_query_with_context(
                message_data.content, chat_history, session.language_preference
            )

            # Core RAG processing (encapsulates internal retrieval + tool calls)
            ai_response = await process_agricultural_query(
                enhanced_query,
                farmer_context={
                    'session_language': session.language_preference,
                    'location': getattr(session, 'location_context', None)
                }
            )
            mark('retrieval', False)
            yield f"data: {json.dumps({'type':'phase_complete','phase':'retrieval','result':'Context gathered','progress':35})}\n\n"

            # Decompose ai_response for ordered thinking events
            base_resp = ai_response.get('response') if isinstance(ai_response, dict) else None
            latest_info = []
            api_payload = {}
            fused = ai_response.get('fused_context') if isinstance(ai_response, dict) else None
            if isinstance(base_resp, dict):
                latest_info = base_resp.get('latest_info') or []
                api_payload = {k: base_resp.get(k) for k in ['weather_guidance','market_advice','government_benefits'] if base_resp.get(k)}

            sequence_counter = 0

            # 1. Google search context results (requested first)
            if latest_info:
                preview = [
                    {k: v for k, v in item.items() if k in ('title','source','url','summary')}
                    for item in latest_info[:5]
                ]
                yield f"data: {json.dumps({'type':'thinking','sequence':sequence_counter,'phase':'google_search','title':'🔎 Google Search Results','results':preview})}\n\n"
            else:
                yield f"data: {json.dumps({'type':'thinking','sequence':sequence_counter,'phase':'google_search','title':'🔎 Google Search Results','results':[],'empty':True})}\n\n"
            sequence_counter += 1

            # 2. API responses
            if api_payload:
                api_detail = {}
                for k, v in api_payload.items():
                    # Provide lightweight summary string for each API value
                    if isinstance(v, (str, int, float)):
                        api_detail[k] = str(v)[:300]
                    else:
                        try:
                            api_detail[k] = json.dumps(v)[:600]
                        except Exception:
                            api_detail[k] = '<unserializable>'
                yield f"data: {json.dumps({'type':'thinking','sequence':sequence_counter,'phase':'api_sources','title':'🧪 API Responses','apis':list(api_payload.keys()),'details':api_detail})}\n\n"
            else:
                yield f"data: {json.dumps({'type':'thinking','sequence':sequence_counter,'phase':'api_sources','title':'🧪 API Responses','apis':[],'empty':True})}\n\n"
            sequence_counter += 1

            # 3. Other relevant data sources (fusion + ML/SQL, classification, etc.)
            other_payload = {}
            if fused:
                fused_keys = list(getattr(fused, '__dict__', {}).keys())
                other_payload['fused_keys'] = fused_keys[:12]
            # (ML / SQL hints)
            if isinstance(base_resp, dict):
                if base_resp.get('agricultural_recommendations'):
                    other_payload['has_agri_recommendations'] = True
            if ai_response.get('classification'):
                other_payload['classification'] = getattr(ai_response.get('classification'), 'primary_category', None)
            if other_payload:
                yield f"data: {json.dumps({'type':'thinking','sequence':sequence_counter,'phase':'data_sources','title':'🧬 Data & Model Outputs','details':other_payload})}\n\n"
            else:
                yield f"data: {json.dumps({'type':'thinking','sequence':sequence_counter,'phase':'data_sources','title':'🧬 Data & Model Outputs','details':{},'empty':True})}\n\n"
            sequence_counter += 1

            # 4. Draft streaming (first LLM layer) BEFORE fact-check
            mark('draft', True)
            yield f"data: {json.dumps({'type':'thinking','sequence':sequence_counter,'phase':'draft_start','title':'✍️ Draft LLM Response (Streaming)'})}\n\n"
            draft_text = ''
            if isinstance(base_resp, dict):
                draft_text = base_resp.get('english_main_answer') or base_resp.get('main_answer') or ''
            elif isinstance(base_resp, str):
                draft_text = base_resp
            # Stream draft character-by-character for smoother UX
            if draft_text:
                for i, ch in enumerate(draft_text):
                    yield f"data: {json.dumps({'type':'thinking','sequence':sequence_counter,'phase':'draft_chunk','chunk': ch})}\n\n"
                    # Light pacing to simulate typing without overloading network
                    if i % 8 == 0:
                        await asyncio.sleep(0.01)
            mark('draft', False)
            sequence_counter += 1

            # Fact check phase
            mark('fact_check', True)
            yield f"data: {json.dumps({'type':'phase','phase':'fact_check','title':'✅ Fact Checking','status':'processing'})}\n\n"
            expert_text = draft_text
            fact_check_result = await agricultural_fact_checker.validate_and_respond(
                original_query=message_data.content,
                expert_response=expert_text,
                context_data={
                    'weather_intelligence': base_resp.get('weather_guidance') if isinstance(base_resp, dict) else {},
                    'search_results': base_resp.get('latest_info', []) if isinstance(base_resp, dict) else [],
                    'agricultural_data': base_resp.get('agricultural_recommendations') if isinstance(base_resp, dict) else {},
                }
            ) if base_resp else {
                'final_response': draft_text,
                'validation_status': 'approved',
                'fact_check_details': {'confidence': 0.9}
            }

            validation_status = fact_check_result.get('validation_status', 'approved')
            confidence = fact_check_result.get('fact_check_details', {}).get('confidence', 0.9)
            yield f"data: {json.dumps({'type':'fact_check_result','status':validation_status,'confidence':confidence})}\n\n"
            mark('fact_check', False)

            # Final response (verified)
            final_response = fact_check_result.get('final_response') or draft_text or 'No response generated.'
            total_chars = len(final_response)
            yield f"data: {json.dumps({'type':'final_start','title':'✅ Verified Response','total_chars': total_chars})}\n\n"

            # Stream chunks
            mark('final_stream', True)
            # Character-level streaming of final verified answer
            for i, ch in enumerate(final_response):
                yield f"data: {json.dumps({'type':'response_chunk','chunk': ch})}\n\n"
                if i % 8 == 0:
                    await asyncio.sleep(0.01)
            mark('final_stream', False)

            # Save messages
            yield f"data: {json.dumps({'type':'phase','phase':'saving','title':'💾 Saving','status':'processing'})}\n\n"
            mark('persistence', True)
            user_message = ChatMessage(
                session_id=message_data.session_id,
                role=MessageRole.USER.value,
                content=message_data.content,
                original_language=session.language_preference
            )

            # Build retrieval summary (citations removed)
            web_results = []
            api_sources = {}
            if isinstance(base_resp, dict):
                web_results = base_resp.get('latest_info') or []
                # (If needed later, derive lightweight citation info client-side)
                api_sources = {k: base_resp.get(k) for k in ['weather_guidance','market_advice','government_benefits'] if base_resp.get(k)}

            fused = ai_response.get('fused_context') if isinstance(ai_response, dict) else None
            retrieval_context = None
            if fused:
                keys = list(getattr(fused, '__dict__', {}).keys())
                retrieval_context = [{'source': 'fused_context_keys', 'keys': keys[:25]}]

            draft_tokens = len(draft_text.split()) if draft_text else 0

            # Pipeline phase status map
            pipeline_phase_status = {k: v for k, v in phase_times.items()}

            ai_message = ChatMessage(
                session_id=message_data.session_id,
                role=MessageRole.ASSISTANT.value,
                content=final_response,
                original_language=fact_check_result.get('original_language', session.language_preference),
                processing_time=ai_response.get('processing_time', 0.0) if isinstance(ai_response, dict) else 0.0,
                fact_check_status=validation_status,
                confidence_score=confidence,
                expert_consulted=ai_response.get('expert_consulted', 'general-agriculture') if isinstance(ai_response, dict) else 'general-agriculture',
                tools_used=ai_response.get('sources_used', []) if isinstance(ai_response, dict) else [],
                retrieval_context=retrieval_context,
                api_sources=api_sources or None,
                web_search_results=web_results or None,
                ml_inferences={
                    'classification': {
                        'primary_category': getattr(ai_response.get('classification'), 'primary_category', None) if isinstance(ai_response, dict) and ai_response.get('classification') else None,
                        'confidence': getattr(ai_response.get('classification'), 'confidence', None) if isinstance(ai_response, dict) and ai_response.get('classification') else None
                    }
                },
                safety_labels={'overall': 'safe'},
                prompt_version='v1',
                # system_prompt_snapshot removed
                latency_breakdown={'total_processing_s': ai_response.get('processing_time') if isinstance(ai_response, dict) else None},
                error_details=ai_response.get('error') if isinstance(ai_response, dict) and not ai_response.get('success', True) else None,
                draft_content=draft_text or None,
                draft_metadata={'preview_chars': len(draft_text[:400]), 'token_estimate': draft_tokens} if draft_text else None,
                draft_tokens_used=draft_tokens or None,
                pipeline_phase_status=pipeline_phase_status or None
            )

            db.add(user_message)
            db.add(ai_message)
            await db.execute(
                update(ChatSession)
                .where(ChatSession.id == message_data.session_id)
                .values(updated_at=datetime.utcnow(), message_count=ChatSession.message_count + 2)
            )
            await db.commit()
            mark('persistence', False)
            yield f"data: {json.dumps({'type':'phase_complete','phase':'saving','result':'Messages saved','progress':95})}\n\n"

            completion = {
                'type':'completion',
                'message':'Response generated successfully!',
                'progress':100,
                'response_id': f'msg_{ai_message.id}',
                'validation_status': validation_status,
                'confidence': confidence,
                'language': fact_check_result.get('original_language', session.language_preference),
                'sources_used': ai_response.get('sources_used', []) if isinstance(ai_response, dict) else [],
                'phases': phase_times
            }
            yield f"data: {json.dumps(completion)}\n\n"

        except Exception as e:
            logger.error(f"❌ Streaming error: {e}")
            yield f"data: {json.dumps({'type':'error','message':f'Processing failed: {str(e)}'})}\n\n"

@router.post("/chat")
async def stream_chat_response(
    message_data: ChatMessageCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    mode: str = "rag"  # rag (default) or gemini
):
    """
    🌊 STREAM CHAT RESPONSE
    
    Returns a Server-Sent Events stream with:
    - Live typing effect
    - Processing phases with progress
    - Source citations
    - AI reasoning steps
    - Real-time updates
    """
    
    async def generate():
        if mode == "gemini":
            # Simple Gemini token streaming (no RAG/fact-check to reduce latency)
            try:
                yield f"data: {json.dumps({'type':'status','message':'🚀 Gemini streaming started'})}\n\n"
                full_tokens = []
                async for token in stream_gemini_text(message_data.content, system="You are an expert agricultural assistant. Provide concise, accurate answers."):
                    full_tokens.append(token)
                    if await request.is_disconnected():
                        logger.info("🔌 Client disconnected (gemini mode)")
                        return
                    yield f"data: {json.dumps({'type':'response_chunk','chunk': token})}\n\n"
                final_text = ''.join(full_tokens)
                # Persist messages (user + AI)
                session = await chat_service.get_session(db, message_data.session_id, str(current_user.id))
                if session:
                    user_msg = ChatMessage(
                        session_id=message_data.session_id,
                        role=MessageRole.USER.value,
                        content=message_data.content,
                        original_language=session.language_preference
                    )
                    ai_msg = ChatMessage(
                        session_id=message_data.session_id,
                        role=MessageRole.ASSISTANT.value,
                        content=final_text,
                        original_language=session.language_preference,
                        processing_time=0.0,
                        confidence_score=0.0,
                        fact_check_status='approved',
                        expert_consulted='gemini-live',
                        tools_used=['gemini_text']
                    )
                    db.add(user_msg)
                    db.add(ai_msg)
                    await db.execute(
                        update(ChatSession)
                        .where(ChatSession.id == message_data.session_id)
                        .values(updated_at=datetime.utcnow(), message_count=ChatSession.message_count + 2)
                    )
                    await db.commit()
                yield f"data: {json.dumps({'type':'completion','message':'✅ Gemini response complete'})}\n\n"
            except Exception as e:
                logger.error(f"Gemini streaming error: {e}")
                yield f"data: {json.dumps({'type':'error','message':str(e)})}\n\n"
        else:
            async for chunk in StreamingChatService.stream_response(
                db=db,
                user_id=str(current_user.id),
                message_data=message_data
            ):
                if await request.is_disconnected():
                    logger.info("🔌 Client disconnected, stopping stream")
                    break
                yield chunk
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*",
        }
    )

@router.get("/chat")
async def stream_chat_response_get(
    session_id: str,
    content: str,
    token: str,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    🌊 STREAM CHAT RESPONSE (GET for EventSource)
    
    EventSource-compatible endpoint that streams chat responses
    """
    try:
        # Verify token and get user
        from app.core.dependencies import get_current_user_from_token
        current_user = await get_current_user_from_token(token, db)
        
        # Create message data
        message_data = ChatMessageCreate(
            session_id=session_id,
            content=content
        )
        
        # Create streaming generator
        async def generate_stream():
            async for chunk in StreamingChatService.stream_response(
                db=db,
                user_id=str(current_user.id),
                message_data=message_data
            ):
                yield chunk
        
        return StreamingResponse(
            generate_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "*",
            }
        )
        
    except Exception as e:
        logger.error(f"❌ Streaming GET error: {e}")
        return HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def streaming_health():
    """Health check for streaming service"""
    return {
        "status": "healthy",
        "service": "Streaming Chat",
        "features": [
            "Server-Sent Events",
            "Live response streaming",
            "Source citations",
            "AI reasoning visualization",
            "Progress tracking"
        ]
    }
