import { MessageType } from '../types/messages';
import type { ChatSendMessage } from '../types/messages';

export class MessageBuilder {
  static chatSend(roomId: string, content: string): ChatSendMessage {
    return {
      type: MessageType.CHAT_SEND,
      timestamp: new Date().toISOString(),
      correlation_id: crypto.randomUUID(),
      payload: {
        room_id: roomId,
        content: content,
      },
    };
  }

  // Future: Add more builder methods here
}
