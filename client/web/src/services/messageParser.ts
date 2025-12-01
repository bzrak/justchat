import type { BaseMessage, Message, MessageTypeValue } from '../types/messages';

type MessageParser = (data: BaseMessage) => Message | null;

// Registry of parsers per type
const parsers: Partial<Record<MessageTypeValue, MessageParser>> = {};

// Register a parser for a message type
export function registerParser(type: MessageTypeValue, parser: MessageParser) {
  parsers[type] = parser;
}

// Parse incoming message
export function parseMessage(rawData: string): Message | null {
  try {
    const data = JSON.parse(rawData) as any;

    // Handle error responses that might only have a "detail" field
    if (data.detail && !data.type) {
      console.log("Detected error response, converting to error message");
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

    if (!data.type || !data.timestamp) {
      console.error("Invalid message structure:", data);
      return null;
    }

    const parser = parsers[data.type];

    if (!parser) {
      console.warn("No parser for message type:", data.type);
      return null;
    }

    return parser(data);

  } catch (e) {
    console.error("Failed to parse message:", e);
    return null;
  }
}
