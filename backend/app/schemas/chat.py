"""Chat-related Pydantic schemas."""

from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class MessageRole(str, Enum):
    """Enum for message roles."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ChatMessage(BaseModel):
    """Schema for a single chat message."""
    role: MessageRole
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    model: Optional[str] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ImageData(BaseModel):
    """Schema for image data in multimodal requests."""
    base64_data: str
    media_type: str = "image/png"


class ChatRequest(BaseModel):
    """Schema for chat request."""
    message: str = Field(..., min_length=1, description="User message content")
    model: str = Field(
        default="meta-llama/llama-3.2-3b-instruct:free",
        description="Model ID to use for the response"
    )
    image: Optional[ImageData] = Field(
        default=None,
        description="Optional image data for multimodal models"
    )


class ChatResponse(BaseModel):
    """Schema for chat response."""
    message: ChatMessage
    success: bool = True
    error: Optional[str] = None
    session_id: Optional[str] = None


class ModelInfo(BaseModel):
    """Schema for model information."""
    id: str
    name: str
    description: Optional[str] = None
    context_length: Optional[int] = None
    supports_images: bool = False
    pricing: Optional[dict] = None


class ModelsResponse(BaseModel):
    """Schema for models list response."""
    models: list[ModelInfo]
    count: int


class HistoryResponse(BaseModel):
    """Schema for chat history response."""
    messages: list[ChatMessage]
    count: int
    session_id: str


class ErrorResponse(BaseModel):
    """Schema for error response."""
    error: str
    detail: Optional[str] = None
    status_code: int = 500
