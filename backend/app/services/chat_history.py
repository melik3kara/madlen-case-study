"""Chat history service for session management."""

import uuid
from datetime import datetime
from typing import Optional
from opentelemetry import trace

from ..schemas import ChatMessage, MessageRole

tracer = trace.get_tracer(__name__)


class ChatHistoryService:
    """Service for managing chat history in memory."""
    
    def __init__(self):
        """Initialize the chat history service."""
        self._sessions: dict[str, list[ChatMessage]] = {}
        self._current_session_id: str = self._create_session()
    
    def _create_session(self) -> str:
        """Create a new session and return its ID."""
        session_id = str(uuid.uuid4())
        self._sessions[session_id] = []
        return session_id
    
    @property
    def current_session_id(self) -> str:
        """Get the current session ID."""
        return self._current_session_id
    
    def add_message(
        self,
        role: MessageRole,
        content: str,
        model: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> ChatMessage:
        """Add a message to the chat history."""
        with tracer.start_as_current_span("chat_history.add_message") as span:
            sid = session_id or self._current_session_id
            span.set_attribute("session_id", sid)
            span.set_attribute("message_role", role.value)
            
            if sid not in self._sessions:
                self._sessions[sid] = []
            
            message = ChatMessage(
                role=role,
                content=content,
                timestamp=datetime.utcnow(),
                model=model
            )
            self._sessions[sid].append(message)
            
            span.set_attribute("message_count", len(self._sessions[sid]))
            return message
    
    def get_history(self, session_id: Optional[str] = None) -> list[ChatMessage]:
        """Get chat history for a session."""
        with tracer.start_as_current_span("chat_history.get_history") as span:
            sid = session_id or self._current_session_id
            span.set_attribute("session_id", sid)
            
            messages = self._sessions.get(sid, [])
            span.set_attribute("message_count", len(messages))
            return messages
    
    def get_messages_for_api(self, session_id: Optional[str] = None) -> list[dict]:
        """Get messages formatted for the OpenRouter API."""
        messages = self.get_history(session_id)
        return [
            {"role": msg.role.value, "content": msg.content}
            for msg in messages
        ]
    
    def clear_history(self, session_id: Optional[str] = None) -> None:
        """Clear chat history for a session."""
        with tracer.start_as_current_span("chat_history.clear_history") as span:
            sid = session_id or self._current_session_id
            span.set_attribute("session_id", sid)
            
            if sid in self._sessions:
                self._sessions[sid] = []
    
    def new_session(self) -> str:
        """Create a new session and set it as current."""
        with tracer.start_as_current_span("chat_history.new_session") as span:
            self._current_session_id = self._create_session()
            span.set_attribute("new_session_id", self._current_session_id)
            return self._current_session_id


# Singleton instance for the application
chat_history_service = ChatHistoryService()
