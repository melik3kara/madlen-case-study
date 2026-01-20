"""Chat router for handling chat-related endpoints with database persistence."""

import time
import uuid
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode

from ..schemas import (
    ChatRequest,
    ChatResponse,
    ChatMessage,
    HistoryResponse,
    MessageRole,
    ErrorResponse,
)
from ..services import openrouter_service
from ..services.chat_history_db import ChatHistoryDBService, get_chat_history_service
from ..database import get_db
from ..telemetry import (
    track_chat_request,
    track_chat_response,
    track_model_usage,
    track_error,
    track_image_upload,
    update_session_count,
)

router = APIRouter(prefix="/chat", tags=["chat"])
tracer = trace.get_tracer(__name__)


def parse_session_id(session_id: Optional[str]) -> Optional[uuid.UUID]:
    """Parse session ID string to UUID."""
    if not session_id:
        return None
    try:
        return uuid.UUID(session_id)
    except ValueError:
        return None


@router.post(
    "",
    response_model=ChatResponse,
    responses={500: {"model": ErrorResponse}},
    summary="Send a chat message",
    description="Send a user message and receive an AI model response"
)
async def send_chat_message(
    request: ChatRequest,
    session_id: Optional[str] = Query(None, description="Session ID to use"),
    db: AsyncSession = Depends(get_db)
) -> ChatResponse:
    """
    Send a chat message to the AI model.
    
    - **message**: The user's message content
    - **model**: The model ID to use (default: meta-llama/llama-3.2-3b-instruct:free)
    - **image**: Optional base64 encoded image for multimodal models
    - **session_id**: Optional session ID (creates new session if not provided)
    """
    start_time = time.perf_counter()
    chat_service = get_chat_history_service(db)
    
    with tracer.start_as_current_span("api.chat.send_message") as span:
        try:
            # Get or create session
            sid = parse_session_id(session_id)
            session = await chat_service.get_or_create_session(sid)
            
            # Rich span attributes
            span.set_attribute("model.id", request.model)
            span.set_attribute("model.provider", request.model.split("/")[0] if "/" in request.model else "unknown")
            span.set_attribute("message.length", len(request.message))
            span.set_attribute("message.word_count", len(request.message.split()))
            span.set_attribute("has_image", request.image is not None)
            span.set_attribute("session.id", str(session.id))
            
            if request.image:
                span.set_attribute("image.media_type", request.image.media_type)
                span.set_attribute("image.size_bytes", len(request.image.base64_data) * 3 // 4)
                track_image_upload(request.image.media_type, "processing")
            
            # Add user message to database
            span.add_event("Adding user message to database")
            await chat_service.add_message(
                role=MessageRole.USER,
                content=request.message,
                session_id=session.id
            )
            
            # Get conversation history for context
            messages = await chat_service.get_messages_for_api(session.id)
            span.set_attribute("context.message_count", len(messages))
            
            # Send to OpenRouter and get response
            span.add_event("Sending message to OpenRouter", {
                "model": request.model,
                "context_messages": len(messages),
            })
            response_content = await openrouter_service.send_message(
                messages=messages,
                model=request.model,
                image=request.image
            )
            
            # Calculate duration
            duration = time.perf_counter() - start_time
            
            # Add assistant response to database
            span.add_event("Adding assistant response to database")
            db_message = await chat_service.add_message(
                role=MessageRole.ASSISTANT,
                content=response_content,
                model=request.model,
                session_id=session.id,
                response_time=duration
            )
            
            # Create response message
            assistant_message = ChatMessage(
                role=MessageRole.ASSISTANT,
                content=response_content,
                timestamp=db_message.created_at,
                model=request.model
            )
            
            span.set_attribute("response.length", len(response_content))
            span.set_attribute("response.word_count", len(response_content.split()))
            span.set_attribute("duration_seconds", duration)
            
            # Track metrics
            model_name = request.model.split("/")[-1].replace(":free", "") if "/" in request.model else request.model
            track_chat_request(request.model, "success", duration, len(request.message))
            track_chat_response(request.model, len(response_content))
            track_model_usage(request.model, model_name)
            
            if request.image:
                track_image_upload(request.image.media_type, "success")
            
            span.set_status(Status(StatusCode.OK))
            
            return ChatResponse(
                message=assistant_message,
                success=True,
                session_id=str(session.id)
            )
            
        except Exception as e:
            duration = time.perf_counter() - start_time
            span.set_status(Status(StatusCode.ERROR, str(e)))
            span.record_exception(e)
            
            # Track error metrics
            error_type = type(e).__name__
            track_chat_request(request.model, "error", duration, len(request.message))
            track_error(error_type, "/api/chat")
            
            if request.image:
                track_image_upload(request.image.media_type, "error")
            
            raise HTTPException(
                status_code=500,
                detail=str(e)
            )


@router.get(
    "/history",
    response_model=HistoryResponse,
    summary="Get chat history",
    description="Retrieve all messages from the current or specified chat session"
)
async def get_chat_history(
    session_id: Optional[str] = Query(None, description="Session ID to get history for"),
    db: AsyncSession = Depends(get_db)
) -> HistoryResponse:
    """Get the chat history for a session."""
    chat_service = get_chat_history_service(db)
    
    with tracer.start_as_current_span("api.chat.get_history") as span:
        sid = parse_session_id(session_id)
        
        if sid:
            session = await chat_service.get_session(sid)
            if not session:
                raise HTTPException(status_code=404, detail="Session not found")
            chat_service.current_session_id = sid
        elif not chat_service.current_session_id:
            # Create new session if none exists
            session = await chat_service.create_session()
            sid = session.id
        else:
            sid = chat_service.current_session_id
        
        db_messages = await chat_service.get_history(sid)
        
        # Convert to schema format
        messages = [
            ChatMessage(
                role=MessageRole(msg.role),
                content=msg.content,
                timestamp=msg.created_at,
                model=msg.model
            )
            for msg in db_messages
        ]
        
        span.set_attribute("session_id", str(sid))
        span.set_attribute("message_count", len(messages))
        
        return HistoryResponse(
            messages=messages,
            count=len(messages),
            session_id=str(sid)
        )


@router.post(
    "/clear",
    summary="Clear chat history",
    description="Clear all messages from the specified or current chat session"
)
async def clear_chat_history(
    session_id: Optional[str] = Query(None, description="Session ID to clear"),
    db: AsyncSession = Depends(get_db)
) -> dict:
    """Clear the chat history for a session."""
    chat_service = get_chat_history_service(db)
    
    with tracer.start_as_current_span("api.chat.clear_history") as span:
        sid = parse_session_id(session_id) or chat_service.current_session_id
        
        if not sid:
            return {"message": "No active session", "success": False}
        
        deleted_count = await chat_service.clear_history(sid)
        span.add_event(f"Chat history cleared: {deleted_count} messages")
        
        return {
            "message": f"Chat history cleared ({deleted_count} messages)",
            "session_id": str(sid),
            "deleted_count": deleted_count,
            "success": True
        }


@router.post(
    "/new-session",
    summary="Start new session",
    description="Start a new chat session"
)
async def new_session(
    title: Optional[str] = Query(None, description="Optional session title"),
    db: AsyncSession = Depends(get_db)
) -> dict:
    """Create a new chat session."""
    chat_service = get_chat_history_service(db)
    
    with tracer.start_as_current_span("api.chat.new_session") as span:
        session = await chat_service.create_session(title=title or "Yeni Sohbet")
        span.set_attribute("new_session_id", str(session.id))
        
        return {
            "message": "New session created",
            "session_id": str(session.id),
            "title": session.title,
            "success": True
        }


@router.get(
    "/sessions",
    summary="Get all sessions",
    description="Get a list of all chat sessions"
)
async def get_sessions(
    limit: int = Query(50, ge=1, le=100, description="Maximum sessions to return"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    db: AsyncSession = Depends(get_db)
) -> dict:
    """Get all chat sessions."""
    chat_service = get_chat_history_service(db)
    
    with tracer.start_as_current_span("api.chat.get_sessions") as span:
        sessions = await chat_service.get_all_sessions(limit=limit, offset=offset)
        span.set_attribute("session_count", len(sessions))
        
        current_id = chat_service.current_session_id
        
        return {
            "sessions": sessions,
            "count": len(sessions),
            "current_session_id": str(current_id) if current_id else None
        }


@router.post(
    "/sessions/{session_id}/switch",
    summary="Switch session",
    description="Switch to an existing chat session"
)
async def switch_session(
    session_id: str,
    db: AsyncSession = Depends(get_db)
) -> dict:
    """Switch to a specific chat session."""
    chat_service = get_chat_history_service(db)
    
    with tracer.start_as_current_span("api.chat.switch_session") as span:
        span.set_attribute("session_id", session_id)
        
        sid = parse_session_id(session_id)
        if not sid:
            raise HTTPException(status_code=400, detail="Invalid session ID")
        
        session = await chat_service.get_session(sid)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        chat_service.current_session_id = sid
        db_messages = await chat_service.get_history(sid)
        
        messages = [
            {
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.created_at.isoformat() if msg.created_at else None,
                "model": msg.model
            }
            for msg in db_messages
        ]
        
        return {
            "message": "Session switched",
            "session_id": session_id,
            "title": session.title,
            "messages": messages,
            "success": True
        }


@router.delete(
    "/sessions/{session_id}",
    summary="Delete session",
    description="Delete a chat session"
)
async def delete_session(
    session_id: str,
    db: AsyncSession = Depends(get_db)
) -> dict:
    """Delete a chat session."""
    chat_service = get_chat_history_service(db)
    
    with tracer.start_as_current_span("api.chat.delete_session") as span:
        span.set_attribute("session_id", session_id)
        
        sid = parse_session_id(session_id)
        if not sid:
            raise HTTPException(status_code=400, detail="Invalid session ID")
        
        success = await chat_service.delete_session(sid)
        if not success:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return {
            "message": "Session deleted",
            "session_id": session_id,
            "success": True
        }


@router.get(
    "/sessions/{session_id}/stats",
    summary="Get session statistics",
    description="Get statistics for a chat session"
)
async def get_session_stats(
    session_id: str,
    db: AsyncSession = Depends(get_db)
) -> dict:
    """Get statistics for a chat session."""
    chat_service = get_chat_history_service(db)
    
    with tracer.start_as_current_span("api.chat.get_session_stats") as span:
        sid = parse_session_id(session_id)
        if not sid:
            raise HTTPException(status_code=400, detail="Invalid session ID")
        
        stats = await chat_service.get_session_stats(sid)
        if not stats:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return stats


@router.patch(
    "/sessions/{session_id}",
    summary="Update session",
    description="Update session title"
)
async def update_session(
    session_id: str,
    title: str = Query(..., description="New session title"),
    db: AsyncSession = Depends(get_db)
) -> dict:
    """Update a chat session's title."""
    chat_service = get_chat_history_service(db)
    
    with tracer.start_as_current_span("api.chat.update_session") as span:
        sid = parse_session_id(session_id)
        if not sid:
            raise HTTPException(status_code=400, detail="Invalid session ID")
        
        success = await chat_service.update_session_title(sid, title)
        if not success:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return {
            "message": "Session updated",
            "session_id": session_id,
            "title": title,
            "success": True
        }
