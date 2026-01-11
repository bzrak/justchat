from datetime import datetime
from uuid import uuid4
import pytest
import pytest_asyncio
from sqlalchemy import StaticPool
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import sessionmaker

from chat_server.api.models import UserCreate
from chat_server.db.models import Base
from chat_server.protocol.messages import ChatSend, ChatSendPayload, UserFrom

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
