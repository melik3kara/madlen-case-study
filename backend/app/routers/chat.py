"""Chat router for handling chat-related endpoints."""

import time
from fastapi import APIRouter, HTTPException
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
from ..services import openrouter_service, chat_history_service
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


@router.post(
    "",
    response_model=ChatResponse,
    responses={500: {"model": ErrorResponse}},
    summary="Send a chat message",
    description="Send a user message and receive an AI model response"
)
async def send_chat_message(request: ChatRequest) -> ChatResponse:
    """
    Send a chat message to the AI model.
    
    - **message**: The user's message content
    - **model**: The model ID to use (default: meta-llama/llama-3.2-3b-instruct:free)
    - **image**: Optional base64 encoded image for multimodal models
    """
    start_time = time.perf_counter()
    
    with tracer.start_as_current_span("api.chat.send_message") as span:
        # Rich span attributes
        span.set_attribute("model.id", request.model)
        span.set_attribute("model.provider", request.model.split("/")[0] if "/" in request.model else "unknown")
        span.set_attribute("message.length", len(request.message))
        span.set_attribute("message.word_count", len(request.message.split()))
        span.set_attribute("has_image", request.image is not None)
        span.set_attribute("session.id", chat_history_service.current_session_id)
        
        if request.image:
            span.set_attribute("image.media_type", request.image.media_type)
            span.set_attribute("image.size_bytes", len(request.image.base64_data) * 3 // 4)
            track_image_upload(request.image.media_type, "processing")
        
        try:
            # Add user message to history
            span.add_event("Adding user message to history")
            chat_history_service.add_message(
                role=MessageRole.USER,
                content=request.message
            )
            
            # Get conversation history for context
            messages = chat_history_service.get_messages_for_api()
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
            
            # Add assistant response to history
            span.add_event("Adding assistant response to history")
            assistant_message = chat_history_service.add_message(
                role=MessageRole.ASSISTANT,
                content=response_content,
                model=request.model
            )
            
            # Calculate metrics
            duration = time.perf_counter() - start_time
            span.set_attribute("response.length", len(response_content))
            span.set_attribute("response.word_count", len(response_content.split()))
            span.set_attribute("duration_seconds", duration)
            
            # Track metrics
            model_name = request.model.split("/")[-1].replace(":free", "") if "/" in request.model else request.model
            track_chat_request(request.model, "success", duration, len(request.message))
            track_chat_response(request.model, len(response_content))
            track_model_usage(request.model, model_name)
            update_session_count(len(chat_history_service._sessions))
            
            if request.image:
                track_image_upload(request.image.media_type, "success")
            
            span.set_status(Status(StatusCode.OK))
            
            return ChatResponse(
                message=assistant_message,
                success=True
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
    description="Retrieve all messages from the current chat session"
)
async def get_chat_history() -> HistoryResponse:
    """Get the chat history for the current session."""
    with tracer.start_as_current_span("api.chat.get_history") as span:
        messages = chat_history_service.get_history()
        session_id = chat_history_service.current_session_id
        
        span.set_attribute("session_id", session_id)
        span.set_attribute("message_count", len(messages))
        
        return HistoryResponse(
            messages=messages,
            count=len(messages),
            session_id=session_id
        )


@router.post(
    "/clear",
    summary="Clear chat history",
    description="Clear all messages from the current chat session"
)
async def clear_chat_history() -> dict:
    """Clear the chat history for the current session."""
    with tracer.start_as_current_span("api.chat.clear_history") as span:
        chat_history_service.clear_history()
        span.add_event("Chat history cleared")
        
        return {"message": "Chat history cleared", "success": True}


@router.post(
    "/new-session",
    summary="Start new session",
    description="Start a new chat session"
)
async def new_session() -> dict:
    """Create a new chat session."""
    with tracer.start_as_current_span("api.chat.new_session") as span:
        new_session_id = chat_history_service.new_session()
        span.set_attribute("new_session_id", new_session_id)
        
        return {
            "message": "New session created",
            "session_id": new_session_id,
            "success": True
        }


@router.get(
    "/sessions",
    summary="Get all sessions",
    description="Get a list of all chat sessions"
)
async def get_sessions() -> dict:
    """Get all chat sessions."""
    with tracer.start_as_current_span("api.chat.get_sessions") as span:
        sessions = chat_history_service.get_all_sessions()
        span.set_attribute("session_count", len(sessions))
        
        return {
            "sessions": sessions,
            "count": len(sessions),
            "current_session_id": chat_history_service.current_session_id
        }


@router.post(
    "/sessions/{session_id}/switch",
    summary="Switch session",
    description="Switch to an existing chat session"
)
async def switch_session(session_id: str) -> dict:
    """Switch to a specific chat session."""
    with tracer.start_as_current_span("api.chat.switch_session") as span:
        span.set_attribute("session_id", session_id)
        
        success = chat_history_service.switch_session(session_id)
        if not success:
            raise HTTPException(status_code=404, detail="Session not found")
        
        messages = chat_history_service.get_history()
        
        return {
            "message": "Session switched",
            "session_id": session_id,
            "messages": [
                {
                    "role": msg.role.value,
                    "content": msg.content,
                    "timestamp": msg.timestamp.isoformat() if msg.timestamp else None,
                    "model": msg.model
                }
                for msg in messages
            ],
            "success": True
        }


@router.delete(
    "/sessions/{session_id}",
    summary="Delete session",
    description="Delete a chat session"
)
async def delete_session(session_id: str) -> dict:
    """Delete a chat session."""
    with tracer.start_as_current_span("api.chat.delete_session") as span:
        span.set_attribute("session_id", session_id)
        
        success = chat_history_service.delete_session(session_id)
        if not success:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return {
            "message": "Session deleted",
            "session_id": session_id,
            "success": True
        }
