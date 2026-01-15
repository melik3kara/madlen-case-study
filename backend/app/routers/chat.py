"""Chat router for handling chat-related endpoints."""

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
    with tracer.start_as_current_span("api.chat.send_message") as span:
        span.set_attribute("model", request.model)
        span.set_attribute("message_length", len(request.message))
        span.set_attribute("has_image", request.image is not None)
        
        try:
            # Add user message to history
            span.add_event("Adding user message to history")
            chat_history_service.add_message(
                role=MessageRole.USER,
                content=request.message
            )
            
            # Get conversation history for context
            messages = chat_history_service.get_messages_for_api()
            
            # Send to OpenRouter and get response
            span.add_event("Sending message to OpenRouter")
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
            
            span.set_status(Status(StatusCode.OK))
            
            return ChatResponse(
                message=assistant_message,
                success=True
            )
            
        except Exception as e:
            span.set_status(Status(StatusCode.ERROR, str(e)))
            span.record_exception(e)
            
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
