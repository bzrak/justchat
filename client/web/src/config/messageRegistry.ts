import { MessageType } from '../types/messages';
import { registerParser } from '../services/messageParser';
import { registerRenderer } from '../components/messages/MessageRenderer';
import { ChatSendMessageComponent } from '../components/messages/ChatSendMessage';
import { ChannelJoinMessage } from '../components/messages/ChannelJoinMessage';
import { ChannelLeaveMessage } from '../components/messages/ChannelLeaveMessage';
import { ErrorMessage } from '../components/messages/ErrorMessage';

// All message type registrations in one place
export function initializeMessageHandlers() {
  // HELLO (connection handshake - no renderer needed, handled by WebSocketContext)
  registerParser(MessageType.HELLO, (data) => data as any);

  // CHAT_SEND (server broadcasts with sender info)
  registerParser(MessageType.CHAT_SEND, (data) => data as any);
  registerRenderer(MessageType.CHAT_SEND, ChatSendMessageComponent);

  // REACT_ADD (server broadcasts when someone adds a reaction)
  registerParser(MessageType.REACT_ADD, (data) => data as any);
  // No renderer needed - reactions are handled by the ChatSendMessage component

  // REACT_REMOVE (server broadcasts when someone removes a reaction)
  registerParser(MessageType.REACT_REMOVE, (data) => data as any);
  // No renderer needed - reactions are handled by the ChatSendMessage component

  // CHANNEL_JOIN (server broadcasts when someone joins)
  registerParser(MessageType.CHANNEL_JOIN, (data) => data as any);
  registerRenderer(MessageType.CHANNEL_JOIN, ChannelJoinMessage);

  // CHANNEL_LEAVE
  registerParser(MessageType.CHANNEL_LEAVE, (data) => data as any);
  registerRenderer(MessageType.CHANNEL_LEAVE, ChannelLeaveMessage);

  // ERROR
  registerParser(MessageType.ERROR, (data) => data as any);
  registerRenderer(MessageType.ERROR, ErrorMessage);

  // CHANNEL_MEMBERS (server sends member list updates)
  registerParser(MessageType.CHANNEL_MEMBERS, (data) => data as any);
  // No renderer needed - handled directly in App state

  // Future types registered here
}
