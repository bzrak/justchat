import type { ChatSendMessage } from '../../types/messages';

interface ChatSendMessageProps {
  message: ChatSendMessage;
  currentUsername?: string;
}

export function ChatSendMessageComponent({ message, currentUsername }: ChatSendMessageProps) {
  const { payload, timestamp } = message;
  const isOwnMessage = currentUsername && payload.sender === currentUsername;

  if (isOwnMessage) {
    // Own message - aligned right with green styling
    return (
      <div className="flex justify-end">
        <div className="max-w-md">
          <div className="relative p-4 bg-gradient-to-r from-green-50 to-emerald-50 rounded-lg shadow-md border-r-4 border-green-500">
            {/* Message content */}
            <div className="text-gray-800 leading-relaxed mb-2">
              {payload.content}
            </div>
            {/* Timestamp */}
            <div className="text-xs text-gray-500 text-right">
              {new Date(timestamp).toLocaleTimeString()}
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Other user's message - aligned left with blue styling
  return (
    <div className="flex justify-start">
      <div className="max-w-md">
        <div className="relative p-4 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg shadow-md border-l-4 border-blue-500">
          {/* Message header */}
          <div className="flex items-center gap-2 mb-2">
            <div className="flex items-center justify-center w-8 h-8 bg-blue-500 text-white rounded-full font-semibold text-sm">
              {(payload.sender || "A")[0].toUpperCase()}
            </div>
            <div className="flex flex-col">
              <span className="font-semibold text-gray-900">
                {payload.sender || "Anonymous"}
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
      </div>
    </div>
  );
}
