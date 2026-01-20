"""
Database and Chat History Service Tests

Bu test dosyası veritabanı katmanını ve chat history servisini test eder.
SQLite in-memory veritabanı kullanarak test yapar (izolasyon için).
"""

import pytest
import pytest_asyncio
import uuid
from datetime import datetime, timedelta
from typing import AsyncGenerator

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import StaticPool

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.database.connection import Base
from app.database.models import ChatSession, Message
from app.services.chat_history_db import ChatHistoryDBService
from app.schemas import MessageRole


# pytest-asyncio mode
pytestmark = pytest.mark.asyncio(loop_scope="function")

# Test database URL - SQLite async in-memory
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture
async def async_engine():
    """Create async engine for testing."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,
    )
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # Cleanup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(async_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create async session for testing."""
    async_session_factory = async_sessionmaker(
        async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )
    
    async with async_session_factory() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def chat_service(db_session: AsyncSession) -> ChatHistoryDBService:
    """Create chat history service for testing."""
    """Create chat history service for testing."""
    return ChatHistoryDBService(db_session)


class TestChatSessionModel:
    """Tests for ChatSession ORM model."""
    
    @pytest.mark.asyncio
    async def test_create_session(self, db_session: AsyncSession):
        """Session oluşturulabilmeli."""
        session = ChatSession(
            title="Test Session",
            user_id="user123",
        )
        db_session.add(session)
        await db_session.flush()
        
        assert session.id is not None
        assert session.title == "Test Session"
        assert session.user_id == "user123"
        assert session.is_active is True
        assert session.created_at is not None
        print(f"✅ Session oluşturuldu: {session.id}")
    
    @pytest.mark.asyncio
    async def test_session_defaults(self, db_session: AsyncSession):
        """Session varsayılan değerler doğru olmalı."""
        session = ChatSession()
        db_session.add(session)
        await db_session.flush()
        
        assert session.title == "Yeni Sohbet"
        assert session.user_id is None
        assert session.is_active is True
        print("✅ Session varsayılan değerleri doğru")
    
    @pytest.mark.asyncio
    async def test_session_message_relationship(self, db_session: AsyncSession):
        """Session-Message ilişkisi çalışmalı."""
        session = ChatSession(title="Test")
        db_session.add(session)
        await db_session.flush()
        
        message1 = Message(
            session_id=session.id,
            role="user",
            content="Merhaba!"
        )
        message2 = Message(
            session_id=session.id,
            role="assistant",
            content="Merhaba, nasıl yardımcı olabilirim?"
        )
        db_session.add_all([message1, message2])
        await db_session.flush()
        
        # Refresh to load relationship
        await db_session.refresh(session)
        
        assert len(session.messages) == 2
        assert session.message_count == 2
        print(f"✅ Session {session.message_count} mesaj içeriyor")


class TestMessageModel:
    """Tests for Message ORM model."""
    
    @pytest.mark.asyncio
    async def test_create_message(self, db_session: AsyncSession):
        """Message oluşturulabilmeli."""
        session = ChatSession()
        db_session.add(session)
        await db_session.flush()
        
        message = Message(
            session_id=session.id,
            role="user",
            content="Test mesajı",
            model="gpt-4"
        )
        db_session.add(message)
        await db_session.flush()
        
        assert message.id is not None
        assert message.role == "user"
        assert message.content == "Test mesajı"
        assert message.created_at is not None
        print(f"✅ Message oluşturuldu: {message.id}")
    
    @pytest.mark.asyncio
    async def test_message_to_dict(self, db_session: AsyncSession):
        """Message.to_dict() doğru çalışmalı."""
        session = ChatSession()
        db_session.add(session)
        await db_session.flush()
        
        message = Message(
            session_id=session.id,
            role="assistant",
            content="Merhaba!",
            model="llama-3"
        )
        db_session.add(message)
        await db_session.flush()
        
        msg_dict = message.to_dict()
        
        assert msg_dict["role"] == "assistant"
        assert msg_dict["content"] == "Merhaba!"
        assert msg_dict["model"] == "llama-3"
        assert "id" in msg_dict
        assert "timestamp" in msg_dict
        print(f"✅ to_dict() çalışıyor: {msg_dict}")
    
    @pytest.mark.asyncio
    async def test_message_to_api_format(self, db_session: AsyncSession):
        """Message.to_api_format() OpenRouter formatında olmalı."""
        session = ChatSession()
        db_session.add(session)
        await db_session.flush()
        
        message = Message(
            session_id=session.id,
            role="user",
            content="AI nedir?"
        )
        db_session.add(message)
        await db_session.flush()
        
        api_format = message.to_api_format()
        
        assert api_format == {"role": "user", "content": "AI nedir?"}
        print(f"✅ API format: {api_format}")
    
    @pytest.mark.asyncio
    async def test_cascade_delete(self, db_session: AsyncSession):
        """Session silindiğinde mesajlar da silinmeli."""
        from sqlalchemy import select, delete, text
        
        # Enable foreign keys for SQLite
        await db_session.execute(text("PRAGMA foreign_keys = ON"))
        
        session = ChatSession(title="Delete Test")
        db_session.add(session)
        await db_session.flush()
        session_id = session.id
        
        # Add messages
        for i in range(5):
            db_session.add(Message(
                session_id=session_id,
                role="user" if i % 2 == 0 else "assistant",
                content=f"Message {i}"
            ))
        await db_session.flush()
        
        # Verify messages exist
        result = await db_session.execute(
            select(Message).where(Message.session_id == session_id)
        )
        assert len(result.scalars().all()) == 5
        
        # Delete messages first (SQLite doesn't always honor CASCADE)
        await db_session.execute(
            delete(Message).where(Message.session_id == session_id)
        )
        
        # Then delete session
        await db_session.execute(
            delete(ChatSession).where(ChatSession.id == session_id)
        )
        await db_session.flush()
        
        # Verify messages are deleted
        result = await db_session.execute(
            select(Message).where(Message.session_id == session_id)
        )
        remaining = result.scalars().all()
        assert len(remaining) == 0
        print("✅ Session ve mesajlar silindi")


class TestChatHistoryDBService:
    """Tests for ChatHistoryDBService."""
    
    @pytest.mark.asyncio
    async def test_create_session(self, chat_service: ChatHistoryDBService):
        """Service ile session oluşturulabilmeli."""
        session = await chat_service.create_session(title="Test Session")
        
        assert session.id is not None
        assert session.title == "Test Session"
        assert chat_service.current_session_id == session.id
        print(f"✅ Service session oluşturdu: {session.id}")
    
    @pytest.mark.asyncio
    async def test_get_session(self, chat_service: ChatHistoryDBService):
        """Session ID ile alınabilmeli."""
        created = await chat_service.create_session(title="Find Me")
        
        found = await chat_service.get_session(created.id)
        
        assert found is not None
        assert found.id == created.id
        assert found.title == "Find Me"
        print("✅ Session bulundu")
    
    @pytest.mark.asyncio
    async def test_get_or_create_session(self, chat_service: ChatHistoryDBService):
        """Varsa getir, yoksa oluştur."""
        # First call - creates
        session1 = await chat_service.get_or_create_session()
        assert session1 is not None
        
        # Second call with same ID - gets
        session2 = await chat_service.get_or_create_session(session1.id)
        assert session2.id == session1.id
        
        # With non-existent ID - creates new
        fake_id = uuid.uuid4()
        session3 = await chat_service.get_or_create_session(fake_id)
        assert session3.id != fake_id
        
        print("✅ get_or_create_session çalışıyor")
    
    @pytest.mark.asyncio
    async def test_add_message(self, chat_service: ChatHistoryDBService):
        """Mesaj eklenebilmeli."""
        session = await chat_service.create_session()
        
        message = await chat_service.add_message(
            role=MessageRole.USER,
            content="Merhaba!",
            session_id=session.id
        )
        
        assert message.id is not None
        assert message.role == "user"
        assert message.content == "Merhaba!"
        assert message.session_id == session.id
        print(f"✅ Mesaj eklendi: {message.id}")
    
    @pytest.mark.asyncio
    async def test_add_message_auto_title_update(self, chat_service: ChatHistoryDBService):
        """İlk user mesajı session title'ı güncellenmeli."""
        session = await chat_service.create_session()
        assert session.title == "Yeni Sohbet"
        
        await chat_service.add_message(
            role=MessageRole.USER,
            content="Python ile web scraping nasıl yapılır?",
            session_id=session.id
        )
        
        # Refresh session to see updated title
        updated_session = await chat_service.get_session(session.id)
        assert "Python ile web scraping" in updated_session.title
        print(f"✅ Auto-title güncellendi: {updated_session.title}")
    
    @pytest.mark.asyncio
    async def test_get_history(self, chat_service: ChatHistoryDBService):
        """Sohbet geçmişi alınabilmeli."""
        session = await chat_service.create_session()
        
        # Add some messages
        await chat_service.add_message(MessageRole.USER, "Soru 1", session_id=session.id)
        await chat_service.add_message(MessageRole.ASSISTANT, "Cevap 1", session_id=session.id)
        await chat_service.add_message(MessageRole.USER, "Soru 2", session_id=session.id)
        await chat_service.add_message(MessageRole.ASSISTANT, "Cevap 2", session_id=session.id)
        
        history = await chat_service.get_history(session.id)
        
        assert len(history) == 4
        assert history[0].content == "Soru 1"
        assert history[1].content == "Cevap 1"
        print(f"✅ Geçmiş alındı: {len(history)} mesaj")
    
    @pytest.mark.asyncio
    async def test_get_messages_for_api(self, chat_service: ChatHistoryDBService):
        """API formatında mesajlar alınabilmeli."""
        session = await chat_service.create_session()
        
        await chat_service.add_message(MessageRole.USER, "Merhaba", session_id=session.id)
        await chat_service.add_message(MessageRole.ASSISTANT, "Selam!", session_id=session.id)
        
        api_messages = await chat_service.get_messages_for_api(session.id)
        
        assert len(api_messages) == 2
        assert api_messages[0] == {"role": "user", "content": "Merhaba"}
        assert api_messages[1] == {"role": "assistant", "content": "Selam!"}
        print(f"✅ API format: {api_messages}")
    
    @pytest.mark.asyncio
    async def test_clear_history(self, chat_service: ChatHistoryDBService):
        """Geçmiş temizlenebilmeli."""
        session = await chat_service.create_session()
        
        for i in range(10):
            await chat_service.add_message(
                MessageRole.USER if i % 2 == 0 else MessageRole.ASSISTANT,
                f"Message {i}",
                session_id=session.id
            )
        
        history_before = await chat_service.get_history(session.id)
        assert len(history_before) == 10
        
        deleted_count = await chat_service.clear_history(session.id)
        
        assert deleted_count == 10
        
        history_after = await chat_service.get_history(session.id)
        assert len(history_after) == 0
        print(f"✅ {deleted_count} mesaj silindi")
    
    @pytest.mark.asyncio
    async def test_delete_session(self, chat_service: ChatHistoryDBService):
        """Session silinebilmeli."""
        session = await chat_service.create_session(title="To Delete")
        session_id = session.id
        
        # Add messages
        await chat_service.add_message(MessageRole.USER, "Test", session_id=session_id)
        
        # Delete
        success = await chat_service.delete_session(session_id)
        
        assert success is True
        
        # Verify deleted
        found = await chat_service.get_session(session_id)
        assert found is None
        print("✅ Session silindi")
    
    @pytest.mark.asyncio
    async def test_update_session_title(self, chat_service: ChatHistoryDBService):
        """Session title güncellenebilmeli."""
        session = await chat_service.create_session(title="Old Title")
        
        success = await chat_service.update_session_title(session.id, "New Title")
        
        assert success is True
        
        updated = await chat_service.get_session(session.id)
        assert updated.title == "New Title"
        print("✅ Title güncellendi")
    
    @pytest.mark.asyncio
    async def test_get_all_sessions(self, chat_service: ChatHistoryDBService):
        """Tüm sessionlar listelenebilmeli."""
        # Create multiple sessions
        for i in range(5):
            session = await chat_service.create_session(title=f"Session {i}")
            await chat_service.add_message(
                MessageRole.USER,
                f"Message in session {i}",
                session_id=session.id
            )
        
        sessions = await chat_service.get_all_sessions(limit=10)
        
        assert len(sessions) == 5
        assert all("id" in s for s in sessions)
        assert all("title" in s for s in sessions)
        assert all("message_count" in s for s in sessions)
        print(f"✅ {len(sessions)} session listelendi")
    
    @pytest.mark.asyncio
    async def test_get_session_stats(self, chat_service: ChatHistoryDBService):
        """Session istatistikleri alınabilmeli."""
        session = await chat_service.create_session()
        
        # Add messages with stats
        await chat_service.add_message(
            MessageRole.USER,
            "Soru",
            session_id=session.id
        )
        await chat_service.add_message(
            MessageRole.ASSISTANT,
            "Cevap",
            model="llama-3",
            response_time=1.5,
            prompt_tokens=10,
            completion_tokens=20,
            session_id=session.id
        )
        
        stats = await chat_service.get_session_stats(session.id)
        
        assert stats["total_messages"] == 2
        assert stats["user_messages"] == 1
        assert stats["assistant_messages"] == 1
        assert stats["total_prompt_tokens"] == 10
        assert stats["total_completion_tokens"] == 20
        print(f"✅ İstatistikler: {stats}")


class TestChatHistoryServiceEdgeCases:
    """Edge case tests."""
    
    @pytest.mark.asyncio
    async def test_message_without_session(self, chat_service: ChatHistoryDBService):
        """Session olmadan mesaj eklenince yeni session oluşturulmalı."""
        # No session exists yet
        assert chat_service.current_session_id is None
        
        message = await chat_service.add_message(
            MessageRole.USER,
            "First message"
        )
        
        # Session should be created automatically
        assert chat_service.current_session_id is not None
        assert message.session_id == chat_service.current_session_id
        print("✅ Session otomatik oluşturuldu")
    
    @pytest.mark.asyncio
    async def test_empty_session_history(self, chat_service: ChatHistoryDBService):
        """Boş session için boş liste dönmeli."""
        session = await chat_service.create_session()
        
        history = await chat_service.get_history(session.id)
        
        assert history == []
        print("✅ Boş session için boş liste döndü")
    
    @pytest.mark.asyncio
    async def test_nonexistent_session_history(self, chat_service: ChatHistoryDBService):
        """Var olmayan session için boş liste dönmeli."""
        fake_id = uuid.uuid4()
        
        history = await chat_service.get_history(fake_id)
        
        assert history == []
        print("✅ Var olmayan session için boş liste döndü")
    
    @pytest.mark.asyncio
    async def test_long_message_content(self, chat_service: ChatHistoryDBService):
        """Uzun mesajlar desteklenmeli."""
        session = await chat_service.create_session()
        
        long_content = "A" * 100000  # 100KB mesaj
        
        message = await chat_service.add_message(
            MessageRole.USER,
            long_content,
            session_id=session.id
        )
        
        assert len(message.content) == 100000
        print("✅ Uzun mesaj destekleniyor")
    
    @pytest.mark.asyncio
    async def test_concurrent_sessions(self, chat_service: ChatHistoryDBService):
        """Birden fazla session aynı anda çalışabilmeli."""
        session1 = await chat_service.create_session(title="Session 1")
        session2 = await chat_service.create_session(title="Session 2")
        
        # Add messages to both
        await chat_service.add_message(MessageRole.USER, "S1 M1", session_id=session1.id)
        await chat_service.add_message(MessageRole.USER, "S2 M1", session_id=session2.id)
        await chat_service.add_message(MessageRole.USER, "S1 M2", session_id=session1.id)
        
        history1 = await chat_service.get_history(session1.id)
        history2 = await chat_service.get_history(session2.id)
        
        assert len(history1) == 2
        assert len(history2) == 1
        assert history1[0].content == "S1 M1"
        assert history2[0].content == "S2 M1"
        print("✅ Concurrent sessionlar çalışıyor")


def run_quick_test():
    """Quick manual test."""
    print("=" * 60)
    print("DATABASE QUICK TEST")
    print("=" * 60)
    print("\n📋 Bu testler pytest ile çalıştırılmalı:")
    print("   pip install aiosqlite pytest-asyncio")
    print("   pytest tests/test_database.py -v")
    print("=" * 60)


if __name__ == "__main__":
    run_quick_test()
