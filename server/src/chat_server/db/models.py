from datetime import datetime
from sqlalchemy import ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.types import DateTime, Integer, String

USERNAME_MAX_LENGTH = 30


class Base(DeclarativeBase):
    pass


class UserTable(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(USERNAME_MAX_LENGTH), unique=True)
    hashed_password: Mapped[str] = mapped_column(String(255))


class ChannelTable(Base):
    __tablename__ = "channels"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(60))


class MessageTable(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(primary_key=True)
    channel_id: Mapped[int] = mapped_column(Integer)
    sender_id: Mapped[int | None] = mapped_column(ForeignKey("user.id"))
    sender_username: Mapped[str] = mapped_column(
        String(USERNAME_MAX_LENGTH), nullable=False
    )
    timestamp: Mapped[datetime] = mapped_column(DateTime)
