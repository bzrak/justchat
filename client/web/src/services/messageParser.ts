import type { BaseMessage, Message, MessageTypeValue } from '../types/messages';

type MessageParser = (data: BaseMessage) => Message | null;

const parsers: Partial<Record<MessageTypeValue, MessageParser>> = {};

export function registerParser(type: MessageTypeValue, parser: MessageParser) {
  parsers[type] = parser;
}

export function parseMessage(rawData: string): Message | null {
  try {
    const data = JSON.parse(rawData) as any;

    if (data.detail && !data.type) {
      const errorMessage: BaseMessage = {
        type: "error",
        timestamp: new Date().toISOString(),
        payload: {
          detail: data.detail
        }
      };
      data.type = errorMessage.type;
      data.timestamp = errorMessage.timestamp;
      data.payload = errorMessage.payload;
    }

    if (!data.type) {
      console.error("[MessageParser] Invalid message structure - missing type:", data);
      return null;
    }

    const parser = parsers[data.type as MessageTypeValue];

    if (!parser) {
      console.warn("[MessageParser] No parser for message type:", data.type);
      return null;
    }

    return parser(data);

  } catch (e) {
    console.error("Failed to parse message:", e);
    return null;
  }
}
