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
    console.log('[MessageParser] Parsing raw data:', rawData);
    const data = JSON.parse(rawData) as any;
    console.log('[MessageParser] JSON parsed:', data);

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

    if (!data.type) {
      console.error("[MessageParser] Invalid message structure - missing type:", data);
      return null;
    }

    console.log('[MessageParser] Message type:', data.type);
    console.log('[MessageParser] Available parsers:', Object.keys(parsers));

    const parser = parsers[data.type];

    if (!parser) {
      console.warn("[MessageParser] No parser for message type:", data.type);
      console.warn("[MessageParser] Available parsers are:", Object.keys(parsers));
      return null;
    }

    console.log('[MessageParser] Found parser for type:', data.type);
    const parsed = parser(data);
    console.log('[MessageParser] Parser returned:', parsed);
    return parsed;

  } catch (e) {
    console.error("Failed to parse message:", e);
    return null;
  }
}
