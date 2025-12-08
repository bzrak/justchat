from enum import StrEnum


class MessageType(StrEnum):
    """
    Types of messages that can be send.
    """

    HELLO = "hello"  # First message expected after connecting to the websocket
    ERROR = "error"

    CHAT_SEND = "chat_send"  # Used when a user send a normal message

    # Channel
    CHANNEL_JOIN = "channel_join"
    CHANNEL_LEAVE = "channel_leave"  # used when a user leaves a channel

    # User
    USER_ONLINE = "user_online"  # State user is online
    USER_AFK = "user_afk"  # User is AFK
    USER_OFFLINE = "user_offline"  # State user is offlline
    USER_TYPING_START = "typing_start"  # User started typing
    USER_TYPING_STOP = "typing_stop"  # User stopped typing
