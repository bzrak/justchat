from contextlib import asynccontextmanager
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
import pytest_asyncio
from sqlalchemy import StaticPool
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from chat_server.api.models import UserCreate
from chat_server.connection.channel import Channel
from chat_server.connection.context import ConnectionContext
from chat_server.connection.manager import ConnectionManager
from chat_server.connection.user import User
from chat_server.db.models import Base
from chat_server.protocol.messages import ChatSend, ChatSendPayload, UserFrom
from chat_server.services.channel_service import ChannelService
from chat_server.services.membership_service import MembershipService
from chat_server.services.message_broker import MessageBroker
from chat_server.services.moderation_service import ModerationService

DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture(scope="function")
async def test_engine():
    """
    Create a fresh database for each test function.
    """
    engine = create_async_engine(DATABASE_URL, poolclass=StaticPool)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def test_session(test_engine):
    """
    Create a database Session for testing.
    """

    async_session = async_sessionmaker(test_engine, expire_on_commit=False)

    async with async_session() as session:
        yield session
        await session.rollback()


@pytest.fixture
def sample_user():
    """
    Valid sample data for a User.
    """
    return {"username": "testuser", "password": "testuserpassword"}


@pytest.fixture
def user_create_obj(sample_user):
    """
    Provides a Pydantic UserCreate object for testing.
    """
    return UserCreate(**sample_user)


@pytest.fixture
def sample_chat_send() -> ChatSend:
    sender = UserFrom(username="testuser", is_guest=False)
    payload = ChatSendPayload(
        channel_id=1, sender=sender, content="This is a test message"
    )
    return ChatSend(timestamp=datetime.now(), id=uuid4(), payload=payload)


# Handler test fixtures


@pytest.fixture
def mock_websocket():
    """Mock WebSocket for testing handlers."""
    ws = AsyncMock()
    ws.send_json = AsyncMock()
    ws.close = AsyncMock()
    return ws


@pytest.fixture
def test_user():
    """Domain User object for testing."""
    return User(username="testuser", id=1, is_guest=False)


@pytest.fixture
def test_channel():
    """Domain Channel object for testing."""
    return Channel(id=1, name="general")


@pytest.fixture
def mock_manager():
    """Mock ConnectionManager with all services for handler tests."""
    manager = MagicMock(spec=ConnectionManager)

    # channel_srvc has mix of sync and async methods
    manager.channel_srvc = MagicMock(spec=ChannelService)
    # Async methods need explicit AsyncMock
    manager.channel_srvc.join_channel = AsyncMock()
    manager.channel_srvc.leave_channel = AsyncMock()
    manager.channel_srvc.send_to_channel = AsyncMock()
    manager.channel_srvc.leave_all_channels = AsyncMock()
    # Sync methods (is_member, get_channel_by_id, create_channel) work with MagicMock

    manager.broker = AsyncMock(spec=MessageBroker)
    manager.moderation = AsyncMock(spec=ModerationService)
    manager.send_error = AsyncMock()
    return manager


@pytest_asyncio.fixture
async def patched_session(test_engine):
    """
    Patches async_session to use the test database.
    Use this fixture in handler tests that need real DB operations.
    """
    async_session_maker = async_sessionmaker(test_engine, expire_on_commit=False)

    with patch("chat_server.db.db.async_session", async_session_maker):
        yield
