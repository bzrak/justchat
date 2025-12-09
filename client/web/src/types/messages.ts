export const MessageType = {
  HELLO: "hello",
  ERROR: "error",
  CHAT_SEND: "chat_send",
  REACT_ADD: "chat_react_add",
  REACT_REMOVE: "chat_react_remove",
  CHANNEL_JOIN: "channel_join",
  CHANNEL_LEAVE: "channel_leave",
  CHANNEL_MEMBERS: "channel_members",
  // Future types go here
} as const;

export type MessageTypeValue = typeof MessageType[keyof typeof MessageType];

export interface BaseMessage {
  type: MessageTypeValue;
  timestamp: string;
  id?: string; // Changed from correlation_id to id to match backend
  payload: any;
}

// User information object (matches backend UserFrom)
export interface UserFrom {
  username: string;
}

// Hello (Client → Server: send token only, no username)
export interface HelloPayloadClientToServer {
  token?: string; // Optional JWT token for authentication
}

export interface HelloMessageClientToServer extends BaseMessage {
  type: typeof MessageType.HELLO;
  payload: HelloPayloadClientToServer;
}

// Hello (Server → Client: returns user info, especially for guests)
export interface HelloPayloadServerToClient {
  token?: string;
  user?: UserFrom; // Server returns the assigned username
}

export interface HelloMessageServerToClient extends BaseMessage {
  type: typeof MessageType.HELLO;
  payload: HelloPayloadServerToClient;
}

// Chat Send (Client → Server)
export interface ChatSendPayloadClientToServer {
  channel_id: number;
  content: string;
}

export interface ChatSendMessageClientToServer extends BaseMessage {
  type: typeof MessageType.CHAT_SEND;
  payload: ChatSendPayloadClientToServer;
}

// Chat Send (Server → Client: broadcasts to channel with sender info)
export interface ChatSendPayloadServerToClient {
  channel_id: number;
  sender?: UserFrom; // User who sent the message
  content: string;
}

export interface ChatSendMessageServerToClient extends BaseMessage {
  type: typeof MessageType.CHAT_SEND;
  payload: ChatSendPayloadServerToClient;
}

// Channel Join (Client → Server)
export interface ChannelJoinPayloadClientToServer {
  channel_id: number;
  user?: UserFrom; // Optional user info
}

export interface ChannelJoinMessageClientToServer extends BaseMessage {
  type: typeof MessageType.CHANNEL_JOIN;
  payload: ChannelJoinPayloadClientToServer;
}

// Channel Join (Server → Client: broadcasts when user joins)
export interface ChannelJoinPayloadServerToClient {
  channel_id: number;
  user?: UserFrom; // User who joined
}

export interface ChannelJoinMessageServerToClient extends BaseMessage {
  type: typeof MessageType.CHANNEL_JOIN;
  payload: ChannelJoinPayloadServerToClient;
}

// Channel Leave (Server → Client only)
export interface ChannelLeavePayload {
  channel_id: number;
  user?: UserFrom; // User who left
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

// Reactions (Client → Server)
export interface ReactPayloadClientToServer {
  emote: string; // Emoji string
  message_id: string; // UUID of the message being reacted to
  channel_id: number;
}

export interface ReactAddMessageClientToServer extends BaseMessage {
  type: typeof MessageType.REACT_ADD;
  payload: ReactPayloadClientToServer;
}

export interface ReactRemoveMessageClientToServer extends BaseMessage {
  type: typeof MessageType.REACT_REMOVE;
  payload: ReactPayloadClientToServer;
}

// Reactions (Server → Client: broadcasts to channel)
export interface ReactPayloadServerToClient {
  emote: string;
  message_id: string;
  channel_id: number;
}

export interface ReactAddMessageServerToClient extends BaseMessage {
  type: typeof MessageType.REACT_ADD;
  payload: ReactPayloadServerToClient;
}

export interface ReactRemoveMessageServerToClient extends BaseMessage {
  type: typeof MessageType.REACT_REMOVE;
  payload: ReactPayloadServerToClient;
}

// Channel Members (Server → Client: sent when member list changes)
export interface ChannelMembersPayload {
  channel_id: number;
  members: UserFrom[];
}

export interface ChannelMembersMessage extends BaseMessage {
  type: typeof MessageType.CHANNEL_MEMBERS;
  payload: ChannelMembersPayload;
}

// Union type for messages received from server
export type Message =
  | HelloMessageServerToClient
  | ChatSendMessageServerToClient
  | ChannelJoinMessageServerToClient
  | ChannelLeaveMessage
  | ErrorMessage
  | ReactAddMessageServerToClient
  | ReactRemoveMessageServerToClient
  | ChannelMembersMessage;
