from datetime import timedelta
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import select

from chat_server.api.models import UserCreate
from chat_server.db.models import MessageTable, MuteTable, UserTable
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
        id=message.id,
        channel_id=channel_id,
        sender_id=sender_id,
        sender_username=sender_username,
        timestamp=timestamp,
        content=message.payload.content,
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


async def get_channel_messages(
    session: AsyncSession, channel_id: int
) -> list[MessageTable] | None:
    """
    Retrive all messages stored from a channel.
    """
    # TODO: Paginate this
    stmt = select(MessageTable).where(MessageTable.channel_id == channel_id)
    res = await session.execute(stmt)
    return list(res.scalars().all())


async def mute_user(
    session: AsyncSession,
    target_id: int,
    by_id: int,
    channel_id: int,
    duration: int | None = None,
    reason: str = "",
):
    """
    Store mute in database
    """
    try:
        if not await get_user_by_id(session, target_id):
            raise ValueError("Target user does not exist.")
        if not await get_user_by_id(session, by_id):
            raise ValueError("Issuer user does not exist.")

        mute_db = MuteTable(
            target_id=target_id,
            by_id=by_id,
            channel_id=channel_id,
            expires_at=func.now() + timedelta(seconds=duration) if duration else None,
        )

        session.add(mute_db)
        await session.commit()
        await session.refresh(mute_db)
        logging.info(f"Mute logged: {mute_db}")
    except Exception as e:
        await session.rollback()
        logging.error(f"Failed to mute user: {e}")
        raise e


async def get_mute(
    session: AsyncSession, target_id: int, channel_id: int
) -> MuteTable | None:
    """
    Check if `target_id` is muted in `channel_id`.
    """
    try:
        if not await get_user_by_id(session, target_id):
            raise ValueError("Target user does not exist.")

        stmt = select(MuteTable).where(
            MuteTable.target_id == target_id,
            MuteTable.channel_id == channel_id,
            (MuteTable.expires_at.is_(None)) | (MuteTable.expires_at > func.now()),
        )
        res = await session.execute(stmt)
        return res.scalar_one_or_none()

    except Exception as e:
        logging.error(f"Failed to check mute: {e}")
        raise e
