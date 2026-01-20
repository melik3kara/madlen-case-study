"""
API Integration Tests for Chat Application.

Tests all API endpoints including:
- Chat endpoints (send message, history, clear, sessions)
- Models endpoint
- Health check
- Error handling
"""

import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
import uuid

from app.database import Base, get_db
from app.schemas import MessageRole


# Test database configuration - use file-based SQLite for persistence between requests
import tempfile
import os

# Configure async tests
pytestmark = pytest.mark.asyncio(loop_scope="function")


def create_test_app():
    """Create a fresh app instance for testing without rate limiting."""
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    from app.routers import chat_router, models_router
    from app.config import get_settings
    
    settings = get_settings()
    
    test_app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
    )
    
    # CORS middleware only, no rate limiting
    test_app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include routers
    test_app.include_router(chat_router, prefix="/api")
    test_app.include_router(models_router, prefix="/api")
    
    @test_app.get("/health")
    async def health():
        return {"status": "healthy", "version": settings.app_version, "service": settings.app_name}
    
    return test_app


@pytest_asyncio.fixture
async def test_engine():
    """Create test database engine with file-based SQLite - fresh for each test."""
    import time
    # Use unique file for each test to ensure isolation
    test_db_file = os.path.join(tempfile.gettempdir(), f"test_chat_api_{time.time_ns()}.db")
    
    engine = create_async_engine(
        f"sqlite+aiosqlite:///{test_db_file}",
        echo=False,
        connect_args={"check_same_thread": False}
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    await engine.dispose()
    
    # Clean up test database file
    if os.path.exists(test_db_file):
        try:
            os.remove(test_db_file)
        except:
            pass


@pytest_asyncio.fixture
async def test_session(test_engine):
    """Create test database session."""
    session_factory = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    async with session_factory() as session:
        yield session


@pytest_asyncio.fixture
async def client(test_engine):
    """Create test client with test database and no rate limiting."""
    test_app = create_test_app()
    
    session_factory = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )
    
    async def override_get_db():
        async with session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()
    
    test_app.dependency_overrides[get_db] = override_get_db
    
    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
    
    test_app.dependency_overrides.clear()


# ==================== Health Check Tests ====================

class TestHealthCheck:
    """Tests for health check endpoint."""
    
    async def test_health_check_returns_200(self, client):
        """Health check should return 200 OK."""
        response = await client.get("/health")
        assert response.status_code == 200
    
    async def test_health_check_response_format(self, client):
        """Health check should return proper JSON format."""
        response = await client.get("/health")
        data = response.json()
        
        assert "status" in data
        assert data["status"] == "healthy"
        assert "version" in data
        assert "service" in data


# ==================== Models API Tests ====================

class TestModelsAPI:
    """Tests for models endpoint."""
    
    async def test_get_models_success(self, client):
        """Should return list of available models."""
        # Mock OpenRouter service
        mock_models = [
            {
                "id": "meta-llama/llama-3.2-3b-instruct:free",
                "name": "Llama 3.2 3B Instruct",
                "description": "A test model",
                "context_length": 8192,
                "supports_images": False
            },
            {
                "id": "google/gemma-3-27b-it:free",
                "name": "Gemma 3 27B",
                "description": "Another test model",
                "context_length": 8192,
                "supports_images": True
            }
        ]
        
        with patch('app.routers.models.openrouter_service.get_available_models', 
                   new_callable=AsyncMock, return_value=mock_models):
            response = await client.get("/api/models")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "models" in data
        assert "count" in data
        assert data["count"] == 2
        assert len(data["models"]) == 2
    
    async def test_get_models_empty_list(self, client):
        """Should handle empty models list."""
        with patch('app.routers.models.openrouter_service.get_available_models',
                   new_callable=AsyncMock, return_value=[]):
            response = await client.get("/api/models")
        
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 0
        assert data["models"] == []


# ==================== Session Management Tests ====================

class TestSessionAPI:
    """Tests for session management endpoints."""
    
    async def test_create_new_session(self, client):
        """Should create a new chat session."""
        response = await client.post("/api/chat/new-session")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert "session_id" in data
        assert "title" in data
        # Verify session_id is a valid UUID
        uuid.UUID(data["session_id"])
    
    async def test_create_session_with_title(self, client):
        """Should create session with custom title."""
        response = await client.post("/api/chat/new-session?title=Test%20Session")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert data["title"] == "Test Session"
    
    async def test_get_sessions_empty(self, client):
        """Should return empty list when no sessions exist."""
        response = await client.get("/api/chat/sessions")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "sessions" in data
        assert "count" in data
        assert data["count"] == 0
    
    async def test_get_sessions_after_creation(self, client):
        """Should list sessions after creating them."""
        # Create two sessions
        await client.post("/api/chat/new-session?title=Session%201")
        await client.post("/api/chat/new-session?title=Session%202")
        
        response = await client.get("/api/chat/sessions")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["count"] == 2
        assert len(data["sessions"]) == 2
    
    async def test_get_sessions_pagination(self, client):
        """Should support pagination."""
        # Create multiple sessions
        for i in range(5):
            await client.post(f"/api/chat/new-session?title=Session%20{i}")
        
        # Get with limit
        response = await client.get("/api/chat/sessions?limit=2&offset=0")
        
        assert response.status_code == 200
        data = response.json()
        
        # Should return at most 2 sessions
        assert len(data["sessions"]) <= 2
    
    async def test_switch_session_success(self, client):
        """Should switch to existing session."""
        # Create a session
        create_response = await client.post("/api/chat/new-session")
        session_id = create_response.json()["session_id"]
        
        # Switch to it
        response = await client.post(f"/api/chat/sessions/{session_id}/switch")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert data["session_id"] == session_id
        assert "messages" in data
    
    async def test_switch_session_not_found(self, client):
        """Should return 404 for non-existent session."""
        fake_id = str(uuid.uuid4())
        response = await client.post(f"/api/chat/sessions/{fake_id}/switch")
        
        assert response.status_code == 404
    
    async def test_switch_session_invalid_id(self, client):
        """Should return 400 for invalid session ID format."""
        response = await client.post("/api/chat/sessions/not-a-uuid/switch")
        
        assert response.status_code == 400
    
    async def test_delete_session_success(self, client):
        """Should delete existing session."""
        # Create a session
        create_response = await client.post("/api/chat/new-session")
        session_id = create_response.json()["session_id"]
        
        # Delete it
        response = await client.delete(f"/api/chat/sessions/{session_id}")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        
        # Verify it's deleted
        switch_response = await client.post(f"/api/chat/sessions/{session_id}/switch")
        assert switch_response.status_code == 404
    
    async def test_delete_session_not_found(self, client):
        """Should return 404 for non-existent session."""
        fake_id = str(uuid.uuid4())
        response = await client.delete(f"/api/chat/sessions/{fake_id}")
        
        assert response.status_code == 404
    
    async def test_update_session_title(self, client):
        """Should update session title."""
        # Create a session
        create_response = await client.post("/api/chat/new-session")
        session_id = create_response.json()["session_id"]
        
        # Update title
        response = await client.patch(
            f"/api/chat/sessions/{session_id}?title=Updated%20Title"
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert data["title"] == "Updated Title"
    
    async def test_get_session_stats(self, client):
        """Should return session statistics."""
        # Create a session
        create_response = await client.post("/api/chat/new-session")
        session_id = create_response.json()["session_id"]
        
        response = await client.get(f"/api/chat/sessions/{session_id}/stats")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "session_id" in data
        assert "total_messages" in data
        assert "user_messages" in data
        assert "assistant_messages" in data


# ==================== Chat History Tests ====================

class TestChatHistoryAPI:
    """Tests for chat history endpoints."""
    
    async def test_get_history_creates_session(self, client):
        """Should create session if none exists when getting history."""
        response = await client.get("/api/chat/history")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "messages" in data
        assert "count" in data
        assert "session_id" in data
        assert data["count"] == 0
    
    async def test_get_history_for_session(self, client):
        """Should get history for specific session."""
        # Create a session
        create_response = await client.post("/api/chat/new-session")
        session_id = create_response.json()["session_id"]
        
        response = await client.get(f"/api/chat/history?session_id={session_id}")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["session_id"] == session_id
        assert data["count"] == 0
    
    async def test_get_history_session_not_found(self, client):
        """Should return 404 for non-existent session."""
        fake_id = str(uuid.uuid4())
        response = await client.get(f"/api/chat/history?session_id={fake_id}")
        
        assert response.status_code == 404
    
    async def test_clear_history_success(self, client):
        """Should clear chat history."""
        # Create a session
        create_response = await client.post("/api/chat/new-session")
        session_id = create_response.json()["session_id"]
        
        response = await client.post(f"/api/chat/clear?session_id={session_id}")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert "deleted_count" in data
    
    async def test_clear_history_no_session(self, client):
        """Should handle clearing when no active session."""
        response = await client.post("/api/chat/clear")
        
        assert response.status_code == 200
        data = response.json()
        
        # Should return success false since no active session
        assert data["success"] is False


# ==================== Chat Message Tests ====================

class TestChatMessageAPI:
    """Tests for chat message endpoint."""
    
    async def test_send_message_success(self, client):
        """Should send message and receive response."""
        # Mock OpenRouter response
        mock_response = "This is a test response from the AI model."
        
        with patch('app.routers.chat_db.openrouter_service.send_message',
                   new_callable=AsyncMock, return_value=mock_response):
            response = await client.post(
                "/api/chat",
                json={
                    "message": "Hello, how are you?",
                    "model": "meta-llama/llama-3.2-3b-instruct:free"
                }
            )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert "message" in data
        assert data["message"]["role"] == "assistant"
        assert data["message"]["content"] == mock_response
    
    async def test_send_message_creates_session(self, client):
        """Should create session if none provided."""
        mock_response = "Hello!"
        
        with patch('app.routers.chat_db.openrouter_service.send_message',
                   new_callable=AsyncMock, return_value=mock_response):
            response = await client.post(
                "/api/chat",
                json={
                    "message": "Hi",
                    "model": "test-model"
                }
            )
        
        assert response.status_code == 200
        
        # Verify session was created
        sessions_response = await client.get("/api/chat/sessions")
        data = sessions_response.json()
        assert data["count"] >= 1
    
    async def test_send_message_with_session_id(self, client):
        """Should use provided session ID."""
        # Create a session first
        create_response = await client.post("/api/chat/new-session")
        session_id = create_response.json()["session_id"]
        
        mock_response = "Response for specific session"
        
        with patch('app.routers.chat_db.openrouter_service.send_message',
                   new_callable=AsyncMock, return_value=mock_response):
            response = await client.post(
                f"/api/chat?session_id={session_id}",
                json={
                    "message": "Test message",
                    "model": "test-model"
                }
            )
        
        assert response.status_code == 200
        
        # Verify message was added to the session
        history_response = await client.get(f"/api/chat/history?session_id={session_id}")
        history = history_response.json()
        
        # Should have user message and assistant response
        assert history["count"] == 2
    
    async def test_send_message_empty_content(self, client):
        """Should reject empty message."""
        response = await client.post(
            "/api/chat",
            json={
                "message": "",
                "model": "test-model"
            }
        )
        
        # Empty message should be rejected by validation
        assert response.status_code == 422
    
    async def test_send_message_missing_model(self, client):
        """Should use default model if not provided."""
        mock_response = "Default model response"
        
        with patch('app.routers.chat_db.openrouter_service.send_message',
                   new_callable=AsyncMock, return_value=mock_response):
            response = await client.post(
                "/api/chat",
                json={
                    "message": "Hello"
                }
            )
        
        assert response.status_code == 200
    
    async def test_send_message_with_image(self, client):
        """Should handle image data."""
        mock_response = "I can see the image."
        
        with patch('app.routers.chat_db.openrouter_service.send_message',
                   new_callable=AsyncMock, return_value=mock_response):
            response = await client.post(
                "/api/chat",
                json={
                    "message": "What's in this image?",
                    "model": "google/gemma-3-27b-it:free",
                    "image": {
                        "base64_data": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
                        "media_type": "image/png"
                    }
                }
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    async def test_send_message_api_error(self, client):
        """Should handle API errors gracefully."""
        with patch('app.routers.chat_db.openrouter_service.send_message',
                   new_callable=AsyncMock, 
                   side_effect=Exception("OpenRouter API error")):
            response = await client.post(
                "/api/chat",
                json={
                    "message": "Hello",
                    "model": "test-model"
                }
            )
        
        assert response.status_code == 500
        data = response.json()
        assert "detail" in data


# ==================== Error Handling Tests ====================

class TestErrorHandling:
    """Tests for error handling."""
    
    async def test_invalid_json_body(self, client):
        """Should return 422 for invalid JSON."""
        response = await client.post(
            "/api/chat",
            content="not valid json",
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 422
    
    async def test_missing_required_field(self, client):
        """Should return 422 for missing required fields."""
        response = await client.post(
            "/api/chat",
            json={}  # Missing 'message' field
        )
        
        assert response.status_code == 422
    
    async def test_not_found_endpoint(self, client):
        """Should return 404 for non-existent endpoint."""
        response = await client.get("/api/nonexistent")
        
        assert response.status_code == 404
    
    async def test_method_not_allowed(self, client):
        """Should return 405 for wrong HTTP method."""
        response = await client.put("/api/chat/history")
        
        assert response.status_code == 405


# ==================== Integration Tests ====================

class TestChatWorkflow:
    """Integration tests for complete chat workflows."""
    
    async def test_complete_chat_workflow(self, client):
        """Test complete workflow: create session, send messages, get history."""
        mock_response = "Test response"
        
        # 1. Create new session
        create_response = await client.post("/api/chat/new-session?title=Integration%20Test")
        assert create_response.status_code == 200
        session_id = create_response.json()["session_id"]
        
        # 2. Send first message
        with patch('app.routers.chat_db.openrouter_service.send_message',
                   new_callable=AsyncMock, return_value=mock_response):
            msg1_response = await client.post(
                f"/api/chat?session_id={session_id}",
                json={"message": "First message", "model": "test-model"}
            )
        assert msg1_response.status_code == 200
        
        # 3. Send second message
        with patch('app.routers.chat_db.openrouter_service.send_message',
                   new_callable=AsyncMock, return_value="Second response"):
            msg2_response = await client.post(
                f"/api/chat?session_id={session_id}",
                json={"message": "Second message", "model": "test-model"}
            )
        assert msg2_response.status_code == 200
        
        # 4. Get history
        history_response = await client.get(f"/api/chat/history?session_id={session_id}")
        assert history_response.status_code == 200
        history = history_response.json()
        
        assert history["count"] == 4  # 2 user + 2 assistant messages
        
        # 5. Clear history
        clear_response = await client.post(f"/api/chat/clear?session_id={session_id}")
        assert clear_response.status_code == 200
        
        # 6. Verify history is cleared
        history_after_clear = await client.get(f"/api/chat/history?session_id={session_id}")
        assert history_after_clear.json()["count"] == 0
        
        # 7. Delete session
        delete_response = await client.delete(f"/api/chat/sessions/{session_id}")
        assert delete_response.status_code == 200
    
    async def test_multiple_sessions_workflow(self, client):
        """Test working with multiple sessions."""
        mock_response = "Response"
        
        # Create two sessions
        session1 = (await client.post("/api/chat/new-session?title=Session%201")).json()["session_id"]
        session2 = (await client.post("/api/chat/new-session?title=Session%202")).json()["session_id"]
        
        # Add message to session 1
        with patch('app.routers.chat_db.openrouter_service.send_message',
                   new_callable=AsyncMock, return_value=mock_response):
            await client.post(
                f"/api/chat?session_id={session1}",
                json={"message": "Message to session 1", "model": "test"}
            )
        
        # Add message to session 2
        with patch('app.routers.chat_db.openrouter_service.send_message',
                   new_callable=AsyncMock, return_value=mock_response):
            await client.post(
                f"/api/chat?session_id={session2}",
                json={"message": "Message to session 2", "model": "test"}
            )
        
        # Verify each session has its own messages
        history1 = (await client.get(f"/api/chat/history?session_id={session1}")).json()
        history2 = (await client.get(f"/api/chat/history?session_id={session2}")).json()
        
        assert history1["count"] == 2
        assert history2["count"] == 2
        
        # Verify messages are different
        assert history1["messages"][0]["content"] == "Message to session 1"
        assert history2["messages"][0]["content"] == "Message to session 2"


# ==================== Rate Limit Header Tests ====================
# Note: Rate limit headers are tested in test_rate_limit.py with the main app
# These tests use a test app without rate limiting for isolation
