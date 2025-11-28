import type { ChatBroadcastMessage } from '../../types/messages';

interface ChatMessageProps {
  message: ChatBroadcastMessage;
}

export function ChatMessage({ message }: ChatMessageProps) {
  const { payload, timestamp } = message;

  return (
    <div className="p-3 bg-white rounded-lg shadow-sm">
      <div className="flex justify-between items-center mb-1">
        <span className="font-semibold text-gray-800">
          {payload.username || "Anonymous"}
        </span>
        <span className="text-xs text-gray-500">
          {new Date(timestamp).toLocaleTimeString()}
        </span>
      </div>
      <div className="text-gray-700">
        {payload.content}
      </div>
    </div>
  );
}
