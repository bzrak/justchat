export const MessageType = {
  HELLO: "hello",
  CHAT_SEND: "chat_send",
  CHAT_BROADCAST: "chat_broadcast",
  CHANNEL_JOIN: "channel_join",
  CHANNEL_LEAVE: "channel_leave",
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

// Channel Join (client sends this)
export interface ChannelJoinPayload {
  username: string;
  channel_id: number;
}

export interface ChannelJoinMessage extends BaseMessage {
  type: typeof MessageType.CHANNEL_JOIN;
  payload: ChannelJoinPayload;
}

// Channel Leave (client sends this)
export interface ChannelLeavePayload {
  username: string;
  channel_id: number;
}

export interface ChannelLeaveMessage extends BaseMessage {
  type: typeof MessageType.CHANNEL_LEAVE;
  payload: ChannelLeavePayload;
}

// Union type - add more here as you implement them
export type Message = ChatBroadcastMessage | ChannelJoinMessage | ChatSendMessage | ChannelLeaveMessage;
