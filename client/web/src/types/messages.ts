export const MessageType = {
  CHAT_SEND: "chat_send",
  CHAT_BROADCAST: "chat_broadcast",
  // Future types go here
} as const;

export type MessageTypeValue = typeof MessageType[keyof typeof MessageType];

export interface BaseMessage {
  type: MessageTypeValue;
  timestamp: string;
  correlation_id?: string;
  payload: any;
}

// Client sends this
export interface ChatSendPayload {
  room_id: string;
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

// Union type - add more here as you implement them
export type Message = ChatBroadcastMessage;
