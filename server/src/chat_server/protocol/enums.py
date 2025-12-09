from enum import StrEnum


class MessageType(StrEnum):
    """
    Types of messages that can be send.
    """

    HELLO = "hello"  # First message expected after connecting to the websocket
    ERROR = "error"

    CHAT_SEND = "chat_send"  # Used when a user send a normal message
    REACT_ADD = "chat_react_add"  # Use when a user reacts to a message
    REACT_REMOVE = "chat_react_remove"  # Use when a user removes a react from a message

    # Channel
    CHANNEL_JOIN = "channel_join"
    CHANNEL_LEAVE = "channel_leave"  # used when a user leaves a channel
    CHANNEL_MEMBERS = "channel_members"  # used to list all the members in a channel
