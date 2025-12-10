from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import select

from chat_server.api.models import UserCreate
from chat_server.db.models import MessageTable, UserTable
from chat_server.protocol.messages import ChatSend
from chat_server.security.utils import get_password_hash

import logging


async def create_user(session: AsyncSession, user_in: UserCreate) -> UserTable:
    """
    Create an User in the database. Returns the User created.
    """
    user_db = UserTable(
        username=user_in.username, hashed_password=get_password_hash(user_in.password)
    )

    try:
        session.add(user_db)
        await session.commit()
        await session.refresh(user_db)
        logging.debug(f"Created user successfully: {user_db}")
        return user_db
    except Exception as e:
        await session.rollback()
        logging.warning(f"Failed to add a user: {e}")
        raise e


async def get_user_by_username(
    session: AsyncSession, username: str
) -> UserTable | None:
    """
    Retrieve an User from the database using a username. Returns None if not found.
    """
    res = await session.execute(select(UserTable).where(UserTable.username == username))
    return res.scalar_one_or_none()


async def get_user_by_id(session: AsyncSession, id: int) -> UserTable | None:
    """
    Retrieve an User from the database using an ID. Returns None if not found.
    """
    return await session.get(UserTable, id)


async def create_message(
    session: AsyncSession, message: ChatSend
) -> MessageTable | None:
    """
    Store a message in the database.
    """
    sender_id = None
    user_db = await get_user_by_username(session, message.payload.sender.username)
    if user_db:
        # Authenticated User
        sender_id = user_db.id
    sender_username = message.payload.sender.username
    channel_id = message.payload.channel_id
    timestamp = message.timestamp

    message_db = MessageTable(
        channel_id=channel_id,
        sender_id=sender_id,
        sender_username=sender_username,
        timestamp=timestamp,
    )

    try:
        session.add(message_db)
        await session.commit()
        await session.refresh(message_db)
        logging.debug(f"Created message in database successfully: {repr(message_db)}")
    except Exception as e:
        await session.rollback()
        logging.error(f"Failed to create message in database: {e}")
        raise e
