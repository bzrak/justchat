import type { ChatBroadcastMessage } from '../../types/messages';

interface ChatMessageProps {
  message: ChatBroadcastMessage;
}

export function ChatMessage({ message }: ChatMessageProps) {
  const { payload, timestamp } = message;

  return (
    <div className="relative p-4 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg shadow-md border-l-4 border-blue-500">
      {/* Broadcast indicator badge */}
      <div className="absolute top-2 right-2">
        <span className="inline-flex items-center gap-1 px-2 py-1 text-xs font-medium text-blue-700 bg-blue-100 rounded-full">
          <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
            <path d="M2 6a2 2 0 012-2h6a2 2 0 012 2v8a2 2 0 01-2 2H4a2 2 0 01-2-2V6zM14.553 7.106A1 1 0 0014 8v4a1 1 0 00.553.894l2 1A1 1 0 0018 13V7a1 1 0 00-1.447-.894l-2 1z" />
          </svg>
          BROADCAST
        </span>
      </div>

      {/* Message header */}
      <div className="flex items-center gap-2 mb-2 pr-24">
        <div className="flex items-center justify-center w-8 h-8 bg-blue-500 text-white rounded-full font-semibold text-sm">
          {(payload.username || "A")[0].toUpperCase()}
        </div>
        <div className="flex flex-col">
          <span className="font-semibold text-gray-900">
            {payload.username || "Anonymous"}
          </span>
          <span className="text-xs text-gray-500">
            {new Date(timestamp).toLocaleTimeString()}
          </span>
        </div>
      </div>

      {/* Message content */}
      <div className="pl-10 text-gray-800 leading-relaxed">
        {payload.content}
      </div>
    </div>
  );
}
