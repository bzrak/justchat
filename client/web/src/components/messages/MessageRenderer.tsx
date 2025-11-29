import type { ComponentType } from 'react';
import type { Message, MessageTypeValue } from '../../types/messages';

// Registry of components per message type
const renderers: Partial<Record<MessageTypeValue, ComponentType<any>>> = {};

// Register a renderer component
export function registerRenderer(
  type: MessageTypeValue,
  component: ComponentType<any>
) {
  renderers[type] = component;
}

// Main message renderer
export function MessageRenderer({ message, currentUsername }: { message: Message; currentUsername?: string }) {
  const Renderer = renderers[message.type];

  if (!Renderer) {
    console.warn("No renderer for message type:", message.type);
    return null;
  }

  return <Renderer message={message} currentUsername={currentUsername} />;
}
