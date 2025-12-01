export const MessageType = {
  HELLO: "hello",
  CHAT_SEND: "chat_send",
  CHAT_BROADCAST: "chat_broadcast",
  CHANNEL_JOIN_REQUEST: "channel_join_request",
  CHANNEL_LEAVE: "channel_leave",
  ERROR: "error",
  // Future types go here
} as const;

export type MessageTypeValue = typeof MessageType[keyof typeof MessageType];

export interface BaseMessage {
  type: MessageTypeValue;
  timestamp: string;
  correlation_id?: string;
  payload: any;
}

// Hello (client sends this on connection)
export interface HelloPayload {
  username: string;
}

export interface HelloMessage extends BaseMessage {
  type: typeof MessageType.HELLO;
  payload: HelloPayload;
}

// Client sends this
export interface ChatSendPayload {
  room_id: string;
  sender: string;
  content: string;
}

export interface ChatSendMessage extends BaseMessage {
  type: typeof MessageType.CHAT_SEND;
  payload: ChatSendPayload;
}

// Server sends this (broadcast to room)
export interface ChatBroadcastPayload {
  content: string;
  user_id?: string;
  username?: string;
  room_id?: string;
}

export interface ChatBroadcastMessage extends BaseMessage {
  type: typeof MessageType.CHAT_BROADCAST;
  payload: ChatBroadcastPayload;
}

// Channel Join Request (client sends this)
export interface ChannelJoinRequestPayload {
  username: string;
  channel_id: number;
}

export interface ChannelJoinRequestMessage extends BaseMessage {
  type: typeof MessageType.CHANNEL_JOIN_REQUEST;
  payload: ChannelJoinRequestPayload;
}

// Channel Leave (server sends this when user disconnects)
export interface ChannelLeavePayload {
  username: string;
  channel_id: number;
}

export interface ChannelLeaveMessage extends BaseMessage {
  type: typeof MessageType.CHANNEL_LEAVE;
  payload: ChannelLeavePayload;
}

// Error (server sends this)
export interface ErrorPayload {
  detail: string;
}

export interface ErrorMessage extends BaseMessage {
  type: typeof MessageType.ERROR;
  payload: ErrorPayload;
}

// Union type - add more here as you implement them
export type Message = ChatBroadcastMessage | ChannelJoinRequestMessage | ChatSendMessage | ChannelLeaveMessage | ErrorMessage;
