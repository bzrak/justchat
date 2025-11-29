import { MessageType } from '../types/messages';
import type { ChatSendMessage, ChannelJoinMessage } from '../types/messages';

export class MessageBuilder {
  static chatSend(roomId: string, content: string, sender: string): ChatSendMessage {
    return {
      type: MessageType.CHAT_SEND,
      timestamp: new Date().toISOString(),
      correlation_id: crypto.randomUUID(),
      payload: {
        room_id: roomId,
        sender: sender,
        content: content,
      },
    };
  }

  static channelJoin(channelId: number, username: string): ChannelJoinMessage {
    return {
      type: MessageType.CHANNEL_JOIN,
      timestamp: new Date().toISOString(),
      correlation_id: crypto.randomUUID(),
      payload: {
        channel_id: channelId,
        username: username,
      },
    };
  }

  // Future: Add more builder methods here
}
