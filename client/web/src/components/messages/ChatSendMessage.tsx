import { useState } from 'react'
import type { ChatSendMessageServerToClient } from '../../types/messages'
import { useReactions } from '../../contexts/ReactionsContext'
import { useWebSocket } from '../../contexts/WebSocketContext'
import { MessageBuilder } from '../../services/messageBuilder'
import { ReactionPicker } from '../ReactionPicker'

interface ChatSendMessageProps {
  message: ChatSendMessageServerToClient;
  currentUsername?: string;
}

export function ChatSendMessageComponent({ message, currentUsername }: ChatSendMessageProps) {
  const { payload, timestamp, id } = message;
  const sender = payload.sender?.username || "Unknown";
  const isOwnMessage = currentUsername && sender === currentUsername;
  const { getMessageReactions } = useReactions()
  const { sendMessage } = useWebSocket()
  const [showPicker, setShowPicker] = useState(false)

  const messageReactions = id ? getMessageReactions(id) : new Map()

  const handleAddReaction = (emote: string) => {
    if (!id) return
    const reactMsg = MessageBuilder.reactAdd(payload.channel_id, id, emote)
    sendMessage(reactMsg)
  }

  const handleRemoveReaction = (emote: string) => {
    if (!id) return
    const reactMsg = MessageBuilder.reactRemove(payload.channel_id, id, emote)
    sendMessage(reactMsg)
  }

  if (isOwnMessage) {
    return (
      <div className="flex justify-end">
        <div className="max-w-md">
          <div className="relative p-4 bg-gradient-to-r from-green-50 to-emerald-50 rounded-lg shadow-md border-r-4 border-green-500 group">
            <div className="text-gray-800 leading-relaxed mb-2">
              {payload.content}
            </div>

            {messageReactions.size > 0 && (
              <div className="flex flex-wrap gap-1 mb-2">
                {Array.from(messageReactions.entries()).map(([emote, count]) => (
                  <button
                    key={emote}
                    onClick={() => handleRemoveReaction(emote)}
                    className="inline-flex items-center gap-1 px-2 py-1 bg-white rounded-full text-sm hover:bg-gray-100 border border-gray-200"
                  >
                    <span>{emote}</span>
                    <span className="text-xs text-gray-600">{count}</span>
                  </button>
                ))}
              </div>
            )}

            <div className="flex items-center justify-between text-xs text-gray-500">
              <div className="relative">
                {showPicker && (
                  <ReactionPicker
                    onSelect={handleAddReaction}
                    onClose={() => setShowPicker(false)}
                  />
                )}
                <button
                  onClick={() => setShowPicker(!showPicker)}
                  className="opacity-0 group-hover:opacity-100 transition-opacity text-lg hover:scale-125"
                  title="Add reaction"
                >
                  😊
                </button>
              </div>
              <span>{new Date(timestamp).toLocaleTimeString()}</span>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex justify-start">
      <div className="max-w-md">
        <div className="relative p-4 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg shadow-md border-l-4 border-blue-500 group">
          <div className="flex items-center gap-2 mb-2">
            <div className="flex items-center justify-center w-8 h-8 bg-blue-500 text-white rounded-full font-semibold text-sm">
              {sender[0].toUpperCase()}
            </div>
            <div className="flex flex-col">
              <span className="font-semibold text-gray-900">
                {sender}
              </span>
              <span className="text-xs text-gray-500">
                {new Date(timestamp).toLocaleTimeString()}
              </span>
            </div>
          </div>

          <div className="pl-10 text-gray-800 leading-relaxed mb-2">
            {payload.content}
          </div>

          {messageReactions.size > 0 && (
            <div className="flex flex-wrap gap-1 pl-10 mb-2">
              {Array.from(messageReactions.entries()).map(([emote, count]) => (
                <button
                  key={emote}
                  onClick={() => handleRemoveReaction(emote)}
                  className="inline-flex items-center gap-1 px-2 py-1 bg-white rounded-full text-sm hover:bg-gray-100 border border-gray-200"
                >
                  <span>{emote}</span>
                  <span className="text-xs text-gray-600">{count}</span>
                </button>
              ))}
            </div>
          )}

          <div className="pl-10 relative">
            {showPicker && (
              <ReactionPicker
                onSelect={handleAddReaction}
                onClose={() => setShowPicker(false)}
              />
            )}
            <button
              onClick={() => setShowPicker(!showPicker)}
              className="opacity-0 group-hover:opacity-100 transition-opacity text-lg hover:scale-125"
              title="Add reaction"
            >
              😊
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
