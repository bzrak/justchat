# Frontend Message System

## Overview
This is an extensible, type-safe message protocol system for the WebSocket chat application.

## Architecture

### File Structure
```
src/
├── types/
│   └── messages.ts              # Message type definitions
├── services/
│   ├── messageParser.ts         # Parser with registry pattern
│   └── messageBuilder.ts        # Message factory methods
├── components/
│   └── messages/
│       ├── ChatMessage.tsx      # Chat message component
│       └── MessageRenderer.tsx  # Renderer with registry pattern
├── config/
│   └── messageRegistry.ts       # Central registration point
└── App.tsx                      # Main app with WebSocket integration
```

## Current Implementation

### Message Types (Currently Supported)
- **CHAT_BROADCAST**: Chat messages from server (displayed)

### How It Works

1. **Message arrives** via WebSocket
2. **Parser** deserializes JSON → typed `Message` object
3. **App.tsx** adds to messages array
4. **MessageRenderer** routes to appropriate component
5. **ChatMessage** renders the UI

## Adding a New Message Type

### Example: Adding ERROR message type

#### Step 1: Define types (types/messages.ts)
```typescript
export enum MessageType {
  CHAT_SEND = "CHAT_SEND",
  CHAT_BROADCAST = "CHAT_BROADCAST",
  ERROR = "ERROR",  // ← Add this
}

export interface ErrorPayload {
  code: string;
  message: string;
}

export interface ErrorMessage extends BaseMessage {
  type: MessageType.ERROR;
  payload: ErrorPayload;
}

// Update union
export type Message = ChatBroadcastMessage | ErrorMessage;
```

#### Step 2: Create component (components/messages/ErrorMessage.tsx)
```typescript
import { ErrorMessage } from '../../types/messages';

export function ErrorMessageComponent({ message }: { message: ErrorMessage }) {
  return (
    <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
      <strong className="text-red-800">[{message.payload.code}]</strong>
      <p className="text-red-700">{message.payload.message}</p>
    </div>
  );
}
```

#### Step 3: Register (config/messageRegistry.ts)
```typescript
import { ErrorMessageComponent } from '../components/messages/ErrorMessage';

export function initializeMessageHandlers() {
  // CHAT_BROADCAST
  registerParser(MessageType.CHAT_BROADCAST, (data) => data as any);
  registerRenderer(MessageType.CHAT_BROADCAST, ChatMessage);

  // ERROR - Add these lines
  registerParser(MessageType.ERROR, (data) => data as any);
  registerRenderer(MessageType.ERROR, ErrorMessageComponent);
}
```

**That's it!** No changes needed to:
- App.tsx
- MessageRenderer logic
- Parser logic
- Any existing components

## Key Design Benefits

1. **Registry Pattern**: Easy to add new types without modifying existing code
2. **Type-Safe**: TypeScript enforces correct message structures
3. **Modular**: Each message type is self-contained
4. **Extensible**: Just 3 steps to add a new type
5. **Maintainable**: Clear separation of concerns

## Message Flow

```
WebSocket.onmessage
    ↓
parseMessage(rawData)
    ↓
Typed Message object
    ↓
Added to messages array
    ↓
MessageRenderer
    ↓
Specific Component (ChatMessage, ErrorMessage, etc.)
    ↓
Rendered UI
```

## Sending Messages

Use `MessageBuilder` to create properly formatted messages:

```typescript
import { MessageBuilder } from './services/messageBuilder';

const message = MessageBuilder.chatSend(roomId, content);
websocket.send(JSON.stringify(message));
```

## Future Enhancements

- Add USER_STATUS messages (online/offline)
- Add TYPING_INDICATOR messages
- Add ERROR messages from server
- Add MESSAGE_ACK for delivery confirmation
- Add ROOM_JOIN/LEAVE messages
