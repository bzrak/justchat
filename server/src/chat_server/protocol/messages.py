from typing import Literal

from pydantic import UUID4, BaseModel, ConfigDict

from chat_server.protocol.basemessage import BaseMessage
from chat_server.protocol.enums import MessageType
from chat_server.protocol.registry import register_message


class UserFrom(BaseModel):
    """
    User information to be transported.
    """

    username: str
    model_config = ConfigDict(from_attributes=True)


# Error
class ErrorMessagePayload(BaseModel):
    detail: str


@register_message(MessageType.ERROR)
class ErrorMessage(BaseMessage):
    type: Literal[MessageType.ERROR] = MessageType.ERROR
    payload: ErrorMessagePayload


# Hello
class HelloPayload(BaseModel):
    model_config = {"extra": "forbid"}
    token: str | None = None
    user: UserFrom | None = None


@register_message(MessageType.HELLO)
class Hello(BaseMessage):
    type: Literal[MessageType.HELLO] = MessageType.HELLO
    payload: HelloPayload


# Channel Join
class ChannelJoinPayload(BaseModel):
    model_config = {"extra": "forbid"}
    channel_id: int
    user: UserFrom | None = None


@register_message(MessageType.CHANNEL_JOIN)
class ChannelJoin(BaseMessage):
    type: Literal[MessageType.CHANNEL_JOIN] = MessageType.CHANNEL_JOIN
    payload: ChannelJoinPayload


# Channel Leave
class ChannelLeavePayload(BaseModel):
    model_config = {"extra": "forbid"}
    channel_id: int
    user: UserFrom | None = None


@register_message(MessageType.CHANNEL_LEAVE)
class ChannelLeave(BaseMessage):
    type: Literal[MessageType.CHANNEL_LEAVE] = MessageType.CHANNEL_LEAVE
    payload: ChannelLeavePayload


# Chat Send
class ChatSendPayload(BaseModel):
    model_config = {"extra": "forbid"}
    channel_id: int
    sender: UserFrom | None = None
    content: str


@register_message(MessageType.CHAT_SEND)
class ChatSend(BaseMessage):
    type: Literal[MessageType.CHAT_SEND] = MessageType.CHAT_SEND
    payload: ChatSendPayload


# Reacts
class ReactPayload(BaseModel):
    model_config = {"extra": "forbid"}
    # TODO: Limit the possible values for an emote
    emote: str
    message_id: UUID4
    channel_id: int


@register_message(MessageType.REACT_ADD)
class ReactAdd(BaseMessage):
    type: Literal[MessageType.REACT_ADD] = MessageType.REACT_ADD
    payload: ReactPayload


@register_message(MessageType.REACT_REMOVE)
class ReactRemove(BaseMessage):
    type: Literal[MessageType.REACT_REMOVE] = MessageType.REACT_REMOVE
    payload: ReactPayload


# Channel Members
class ChannelMembersPayload(BaseModel):
    model_config = {"extra": "forbid"}
    channel_id: int
    members: list[UserFrom]


@register_message(MessageType.CHANNEL_MEMBERS)
class ChannelMembers(BaseMessage):
    type: Literal[MessageType.CHANNEL_MEMBERS] = MessageType.CHANNEL_MEMBERS
    payload: ChannelMembersPayload
