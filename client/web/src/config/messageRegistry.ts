import { MessageType } from '../types/messages';
import { registerParser } from '../services/messageParser';
import { registerRenderer } from '../components/messages/MessageRenderer';
import { ChatMessage } from '../components/messages/ChatMessage';
import { ChatSendMessageComponent } from '../components/messages/ChatSendMessage';
import { ChannelJoinMessage } from '../components/messages/ChannelJoinMessage';
import { ChannelLeaveMessage } from '../components/messages/ChannelLeaveMessage';

// All message type registrations in one place
export function initializeMessageHandlers() {
  // CHAT_BROADCAST
  registerParser(MessageType.CHAT_BROADCAST, (data) => data as any);
  registerRenderer(MessageType.CHAT_BROADCAST, ChatMessage);

  // CHAT_SEND
  registerParser(MessageType.CHAT_SEND, (data) => data as any);
  registerRenderer(MessageType.CHAT_SEND, ChatSendMessageComponent);

  // CHANNEL_JOIN
  registerParser(MessageType.CHANNEL_JOIN, (data) => data as any);
  registerRenderer(MessageType.CHANNEL_JOIN, ChannelJoinMessage);

  // CHANNEL_LEAVE
  registerParser(MessageType.CHANNEL_LEAVE, (data) => data as any);
  registerRenderer(MessageType.CHANNEL_LEAVE, ChannelLeaveMessage);

  // Future types registered here
  // Example:
  // registerParser(MessageType.ERROR, errorParser);
  // registerRenderer(MessageType.ERROR, ErrorMessage);
}
