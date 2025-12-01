import { MessageType } from '../types/messages';
import type { HelloMessage, ChatSendMessage, ChannelJoinRequestMessage } from '../types/messages';

export class MessageBuilder {
  static hello(username: string): HelloMessage {
    return {
      type: MessageType.HELLO,
      timestamp: new Date().toISOString(),
      correlation_id: crypto.randomUUID(),
      payload: {
        username: username,
      },
    };
  }

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

  static channelJoin(channelId: number, username: string): ChannelJoinRequestMessage {
    return {
      type: MessageType.CHANNEL_JOIN_REQUEST,
      timestamp: new Date().toISOString(),
      correlation_id: crypto.randomUUID(),
      payload: {
        channel_id: channelId,
        username: username,
      },
    };
  }

  // Note: channelLeave is not needed - server automatically handles disconnections
  // Future: Add more builder methods here
}
