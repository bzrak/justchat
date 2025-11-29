"""Message Protocol"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel
from pydantic.types import UUID4

from .enums import MessageType


class BaseMessage(BaseModel):
    """
    Base Message Class containg absolute necessary information.
    """

    type: MessageType
    # NOTE: Maybe add a subtype ? E.g. type: SYSTEM, subtype: BROADCAST
    timestamp: datetime
    correlation_id: UUID4 | None = None
    payload: Any

    @classmethod
    def from_json(cls, json_str: str) -> "BaseMessage | None":
        """
        Deserialize a JSON String to a Message.

        Raise ValidationError in case of invalid format
        """
        import json

        data = json.loads(json_str)

        match data["type"]:
            case MessageType.CHAT_SEND:
                return ChatSend.model_validate_json(json_str)
            case MessageType.CHANNEL_JOIN:
                return ChannelJoin.model_validate_json(json_str)
            case _:
                return None

    @classmethod
    def to_json(cls, **kwargs) -> str:
        # FIX: Not working, just use model_dump_json directly for now.
        """
        Serialize Message to JSON string.
        """
        return cls.model_dump_json(**kwargs)


class MessagePublic(BaseModel):
    payload: Any


###################
# Type: CHAT_SEND #
###################
class ChatSendPayload(BaseModel):
    room_id: UUID4
    sender: str
    content: str


class ChatSend(BaseMessage):
    type: MessageType = MessageType.CHAT_SEND
    payload: ChatSendPayload


########################
# Type: CHAT_BROADCAST #
########################
class ChatBroadcastPayload(BaseModel):
    content: str


class ChatBroadcast(BaseMessage):
    type: MessageType = MessageType.CHAT_BROADCAST
    payload: ChatBroadcastPayload


########################
# Type: CHANNEL_JOIN   #
########################
class ChannelJoinPayload(BaseModel):
    username: str
    channel_id: int


class ChannelJoin(BaseMessage):
    type: MessageType = MessageType.CHANNEL_JOIN
    payload: ChannelJoinPayload
