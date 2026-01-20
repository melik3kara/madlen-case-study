"""
Chat history service with database persistence.

Bu servis chat geçmişini PostgreSQL veritabanında saklar.
SQLAlchemy async ORM kullanır.
"""

import uuid
from datetime import datetime
from typing import Optional, List
from sqlalchemy import select, update, delete, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from opentelemetry import trace

from ..database.models import ChatSession, Message
from ..schemas import ChatMessage, MessageRole

tracer = trace.get_tracer(__name__)


class ChatHistoryDBService:
    """
    Service for managing chat history in PostgreSQL database.
    
    Thread-safe, async, ve persistent storage sağlar.
    """
    
    def __init__(self, db: AsyncSession):
        """
        Initialize the chat history service with a database session.
        
        Args:
            db: SQLAlchemy async session
        """
        self.db = db
        self._current_session_id: Optional[uuid.UUID] = None
    
    # ==================== Session Management ====================
    
    async def create_session(
        self,
        title: str = "Yeni Sohbet",
        user_id: Optional[str] = None
    ) -> ChatSession:
        """
        Create a new chat session.
        
        Args:
            title: Session title
            user_id: Optional user identifier
            
        Returns:
            Created ChatSession object
        """
        with tracer.start_as_current_span("db.chat_history.create_session") as span:
            session = ChatSession(
                title=title,
                user_id=user_id,
                is_active=True,
            )
            self.db.add(session)
            await self.db.flush()
            await self.db.refresh(session)
            
            self._current_session_id = session.id
            span.set_attribute("session_id", str(session.id))
            span.set_attribute("title", title)
            
            return session
    
    async def get_session(self, session_id: uuid.UUID) -> Optional[ChatSession]:
        """
        Get a session by ID with its messages.
        
        Args:
            session_id: Session UUID
            
        Returns:
            ChatSession or None if not found
        """
        with tracer.start_as_current_span("db.chat_history.get_session") as span:
            span.set_attribute("session_id", str(session_id))
            
            result = await self.db.execute(
                select(ChatSession)
                .options(selectinload(ChatSession.messages))
                .where(ChatSession.id == session_id)
            )
            session = result.scalar_one_or_none()
            
            if session:
                span.set_attribute("message_count", len(session.messages))
            
            return session
    
    async def get_or_create_session(
        self,
        session_id: Optional[uuid.UUID] = None,
        user_id: Optional[str] = None
    ) -> ChatSession:
        """
        Get existing session or create a new one.
        
        Args:
            session_id: Optional session UUID
            user_id: Optional user identifier
            
        Returns:
            ChatSession object
        """
        if session_id:
            session = await self.get_session(session_id)
            if session:
                self._current_session_id = session.id
                return session
        
        return await self.create_session(user_id=user_id)
    
    async def get_all_sessions(
        self,
        user_id: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[dict]:
        """
        Get all sessions with metadata.
        
        Args:
            user_id: Optional filter by user
            limit: Maximum sessions to return
            offset: Pagination offset
            
        Returns:
            List of session dictionaries
        """
        with tracer.start_as_current_span("db.chat_history.get_all_sessions") as span:
            query = (
                select(ChatSession)
                .options(selectinload(ChatSession.messages))
                .where(ChatSession.is_active == True)
                .order_by(desc(ChatSession.updated_at))
                .limit(limit)
                .offset(offset)
            )
            
            if user_id:
                query = query.where(ChatSession.user_id == user_id)
            
            result = await self.db.execute(query)
            sessions = result.scalars().all()
            
            session_list = []
            for session in sessions:
                # Get title from first user message if default
                title = session.title
                if title == "Yeni Sohbet" and session.messages:
                    for msg in session.messages:
                        if msg.role == "user":
                            title = msg.content[:50] + ("..." if len(msg.content) > 50 else "")
                            break
                
                session_list.append({
                    "id": str(session.id),
                    "title": title,
                    "message_count": len(session.messages),
                    "last_updated": session.updated_at.isoformat(),
                    "created_at": session.created_at.isoformat(),
                    "is_active": self._current_session_id == session.id,
                })
            
            span.set_attribute("session_count", len(session_list))
            return session_list
    
    async def delete_session(self, session_id: uuid.UUID) -> bool:
        """
        Delete a session and all its messages.
        
        Args:
            session_id: Session UUID to delete
            
        Returns:
            True if deleted, False if not found
        """
        with tracer.start_as_current_span("db.chat_history.delete_session") as span:
            span.set_attribute("session_id", str(session_id))
            
            result = await self.db.execute(
                delete(ChatSession).where(ChatSession.id == session_id)
            )
            
            deleted = result.rowcount > 0
            span.set_attribute("deleted", deleted)
            
            # Create new session if we deleted the current one
            if deleted and self._current_session_id == session_id:
                await self.create_session()
            
            return deleted
    
    async def update_session_title(
        self,
        session_id: uuid.UUID,
        title: str
    ) -> bool:
        """
        Update session title.
        
        Args:
            session_id: Session UUID
            title: New title
            
        Returns:
            True if updated, False if not found
        """
        result = await self.db.execute(
            update(ChatSession)
            .where(ChatSession.id == session_id)
            .values(title=title, updated_at=datetime.utcnow())
        )
        return result.rowcount > 0
    
    # ==================== Message Management ====================
    
    async def add_message(
        self,
        role: MessageRole,
        content: str,
        model: Optional[str] = None,
        session_id: Optional[uuid.UUID] = None,
        response_time: Optional[float] = None,
        prompt_tokens: Optional[int] = None,
        completion_tokens: Optional[int] = None,
    ) -> Message:
        """
        Add a message to a session.
        
        Args:
            role: Message role (user, assistant, system)
            content: Message content
            model: Model used (for assistant messages)
            session_id: Session UUID (uses current if not provided)
            response_time: Response time in seconds
            prompt_tokens: Number of prompt tokens
            completion_tokens: Number of completion tokens
            
        Returns:
            Created Message object
        """
        with tracer.start_as_current_span("db.chat_history.add_message") as span:
            sid = session_id or self._current_session_id
            
            if not sid:
                session = await self.create_session()
                sid = session.id
            
            span.set_attribute("session_id", str(sid))
            span.set_attribute("role", role.value)
            span.set_attribute("content_length", len(content))
            
            message = Message(
                session_id=sid,
                role=role.value,
                content=content,
                model=model,
                response_time=response_time,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
            )
            
            self.db.add(message)
            await self.db.flush()
            await self.db.refresh(message)
            
            # Update session's updated_at timestamp
            await self.db.execute(
                update(ChatSession)
                .where(ChatSession.id == sid)
                .values(updated_at=datetime.utcnow())
            )
            
            # Auto-update title from first user message
            if role == MessageRole.USER:
                session = await self.get_session(sid)
                if session and session.title == "Yeni Sohbet":
                    new_title = content[:50] + ("..." if len(content) > 50 else "")
                    await self.update_session_title(sid, new_title)
            
            span.set_attribute("message_id", str(message.id))
            return message
    
    async def get_history(
        self,
        session_id: Optional[uuid.UUID] = None
    ) -> List[Message]:
        """
        Get all messages for a session.
        
        Args:
            session_id: Session UUID (uses current if not provided)
            
        Returns:
            List of Message objects
        """
        with tracer.start_as_current_span("db.chat_history.get_history") as span:
            sid = session_id or self._current_session_id
            
            if not sid:
                return []
            
            span.set_attribute("session_id", str(sid))
            
            result = await self.db.execute(
                select(Message)
                .where(Message.session_id == sid)
                .order_by(Message.created_at)
            )
            messages = list(result.scalars().all())
            
            span.set_attribute("message_count", len(messages))
            return messages
    
    async def get_messages_for_api(
        self,
        session_id: Optional[uuid.UUID] = None
    ) -> List[dict]:
        """
        Get messages formatted for OpenRouter API.
        
        Args:
            session_id: Session UUID (uses current if not provided)
            
        Returns:
            List of message dictionaries in API format
        """
        messages = await self.get_history(session_id)
        return [msg.to_api_format() for msg in messages]
    
    async def clear_history(
        self,
        session_id: Optional[uuid.UUID] = None
    ) -> int:
        """
        Clear all messages from a session.
        
        Args:
            session_id: Session UUID (uses current if not provided)
            
        Returns:
            Number of deleted messages
        """
        with tracer.start_as_current_span("db.chat_history.clear_history") as span:
            sid = session_id or self._current_session_id
            
            if not sid:
                return 0
            
            span.set_attribute("session_id", str(sid))
            
            result = await self.db.execute(
                delete(Message).where(Message.session_id == sid)
            )
            
            deleted_count = result.rowcount
            span.set_attribute("deleted_count", deleted_count)
            
            return deleted_count
    
    # ==================== Analytics ====================
    
    async def get_session_stats(
        self,
        session_id: Optional[uuid.UUID] = None
    ) -> dict:
        """
        Get statistics for a session.
        
        Args:
            session_id: Session UUID (uses current if not provided)
            
        Returns:
            Statistics dictionary
        """
        sid = session_id or self._current_session_id
        
        if not sid:
            return {}
        
        result = await self.db.execute(
            select(
                func.count(Message.id).label("total_messages"),
                func.count(Message.id).filter(Message.role == "user").label("user_messages"),
                func.count(Message.id).filter(Message.role == "assistant").label("assistant_messages"),
                func.sum(Message.prompt_tokens).label("total_prompt_tokens"),
                func.sum(Message.completion_tokens).label("total_completion_tokens"),
                func.avg(Message.response_time).label("avg_response_time"),
            )
            .where(Message.session_id == sid)
        )
        row = result.one()
        
        return {
            "session_id": str(sid),
            "total_messages": row.total_messages or 0,
            "user_messages": row.user_messages or 0,
            "assistant_messages": row.assistant_messages or 0,
            "total_prompt_tokens": row.total_prompt_tokens or 0,
            "total_completion_tokens": row.total_completion_tokens or 0,
            "avg_response_time": float(row.avg_response_time) if row.avg_response_time else 0,
        }
    
    # ==================== Properties ====================
    
    @property
    def current_session_id(self) -> Optional[uuid.UUID]:
        """Get the current session ID."""
        return self._current_session_id
    
    @current_session_id.setter
    def current_session_id(self, value: uuid.UUID):
        """Set the current session ID."""
        self._current_session_id = value


# Factory function for dependency injection
def get_chat_history_service(db: AsyncSession) -> ChatHistoryDBService:
    """
    Factory function to create ChatHistoryDBService.
    
    Usage with FastAPI:
        @router.post("/chat")
        async def send_message(
            request: ChatRequest,
            db: AsyncSession = Depends(get_db)
        ):
            service = get_chat_history_service(db)
            ...
    """
    return ChatHistoryDBService(db)
