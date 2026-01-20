"""SQLAlchemy ORM models for the chat application."""

import uuid
from datetime import datetime
from typing import List, Optional
from sqlalchemy import (
    String,
    Text,
    DateTime,
    Boolean,
    ForeignKey,
    Index,
    Enum as SQLEnum,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from .connection import Base


class ChatSession(Base):
    """
    Chat session model.
    
    Bir kullanıcının bir sohbet oturumunu temsil eder.
    Her oturum birden fazla mesaj içerebilir.
    """
    __tablename__ = "chat_sessions"
    
    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    
    # Session metadata
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        default="Yeni Sohbet",
    )
    
    # User tracking (for future multi-user support)
    user_id: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        index=True,
    )
    
    # Status
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )
    
    # Relationships
    messages: Mapped[List["Message"]] = relationship(
        "Message",
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="Message.created_at",
        lazy="selectin",
    )
    
    # Indexes
    __table_args__ = (
        Index("idx_session_user_updated", "user_id", "updated_at"),
        Index("idx_session_active", "is_active"),
    )
    
    def __repr__(self) -> str:
        return f"<ChatSession(id={self.id}, title='{self.title[:20]}...')>"
    
    @property
    def message_count(self) -> int:
        """Get the number of messages in this session."""
        return len(self.messages) if self.messages else 0


class Message(Base):
    """
    Chat message model.
    
    Bir sohbet oturumundaki tek bir mesajı temsil eder.
    """
    __tablename__ = "messages"
    
    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    
    # Foreign key to session
    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("chat_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    
    # Message content
    role: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )  # 'user', 'assistant', 'system'
    
    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    
    # Model used for assistant messages
    model: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )
    
    # Token counts (for analytics)
    prompt_tokens: Mapped[Optional[int]] = mapped_column(
        nullable=True,
    )
    completion_tokens: Mapped[Optional[int]] = mapped_column(
        nullable=True,
    )
    
    # Response time in seconds
    response_time: Mapped[Optional[float]] = mapped_column(
        nullable=True,
    )
    
    # Timestamp
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
    )
    
    # Relationships
    session: Mapped["ChatSession"] = relationship(
        "ChatSession",
        back_populates="messages",
    )
    
    # Indexes
    __table_args__ = (
        Index("idx_message_session_created", "session_id", "created_at"),
        Index("idx_message_role", "role"),
    )
    
    def __repr__(self) -> str:
        content_preview = self.content[:30] + "..." if len(self.content) > 30 else self.content
        return f"<Message(id={self.id}, role='{self.role}', content='{content_preview}')>"
    
    def to_dict(self) -> dict:
        """Convert message to dictionary for API responses."""
        return {
            "id": str(self.id),
            "role": self.role,
            "content": self.content,
            "model": self.model,
            "timestamp": self.created_at.isoformat() if self.created_at else None,
        }
    
    def to_api_format(self) -> dict:
        """Convert message to OpenRouter API format."""
        return {
            "role": self.role,
            "content": self.content,
        }
