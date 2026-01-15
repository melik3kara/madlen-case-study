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
    
    def switch_session(self, session_id: str) -> bool:
        """Switch to an existing session."""
        with tracer.start_as_current_span("chat_history.switch_session") as span:
            span.set_attribute("target_session_id", session_id)
            
            if session_id in self._sessions:
                self._current_session_id = session_id
                span.set_status(trace.Status(trace.StatusCode.OK))
                return True
            
            span.set_status(trace.Status(trace.StatusCode.ERROR, "Session not found"))
            return False
    
    def get_all_sessions(self) -> list[dict]:
        """Get all sessions with their metadata."""
        with tracer.start_as_current_span("chat_history.get_all_sessions") as span:
            sessions = []
            for session_id, messages in self._sessions.items():
                if not messages:
                    continue  # Skip empty sessions
                
                # Get title from first user message
                title = "Yeni Sohbet"
                for msg in messages:
                    if msg.role == MessageRole.USER:
                        title = msg.content[:50] + ("..." if len(msg.content) > 50 else "")
                        break
                
                # Get last updated time
                last_updated = messages[-1].timestamp if messages else datetime.utcnow()
                
                sessions.append({
                    "id": session_id,
                    "title": title,
                    "message_count": len(messages),
                    "last_updated": last_updated.isoformat(),
                    "is_active": session_id == self._current_session_id
                })
            
            # Sort by last_updated descending
            sessions.sort(key=lambda x: x["last_updated"], reverse=True)
            span.set_attribute("session_count", len(sessions))
            return sessions
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a session."""
        with tracer.start_as_current_span("chat_history.delete_session") as span:
            span.set_attribute("session_id", session_id)
            
            if session_id in self._sessions:
                del self._sessions[session_id]
                
                # If we deleted the current session, create a new one
                if session_id == self._current_session_id:
                    self._current_session_id = self._create_session()
                
                return True
            return False


# Singleton instance for the application
chat_history_service = ChatHistoryService()
