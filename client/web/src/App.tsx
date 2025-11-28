import { useState, useEffect, useRef, type FormEvent } from 'react'
import './App.css'
import { initializeMessageHandlers } from './config/messageRegistry'
import type { Message } from './types/messages'
import { parseMessage } from './services/messageParser'
import { MessageRenderer } from './components/messages/MessageRenderer'
import { MessageBuilder } from './services/messageBuilder'

// TODO: Replace with actual room ID management
const TEMP_ROOM_ID = crypto.randomUUID()

function App() {
  const [message, setMessage] = useState('')
  const [messages, setMessages] = useState<Message[]>([])
  const [isConnected, setIsConnected] = useState(false)
  const wsRef = useRef<WebSocket | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // Initialize message handlers on mount
  useEffect(() => {
    initializeMessageHandlers()
  }, [])

  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8000/ws')

    ws.onopen = () => {
      console.log('Connected to WebSocket')
      setIsConnected(true)
    }

    ws.onmessage = (event) => {
      console.log('Message received:', event.data)
      const parsedMessage = parseMessage(event.data)

      if (parsedMessage) {
        setMessages(prev => [...prev, parsedMessage])
      }
    }

    ws.onerror = (error) => {
      console.error('WebSocket error:', error)
    }

    ws.onclose = () => {
      console.log('Disconnected from WebSocket')
      setIsConnected(false)
    }

    wsRef.current = ws

    // Cleanup on unmount
    return () => {
      ws.close()
    }
  }, [])

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  function sendMessage(e: FormEvent<HTMLFormElement>) {
    e.preventDefault()

    if (message.trim() && wsRef.current && isConnected) {
      const chatMessage = MessageBuilder.chatSend(TEMP_ROOM_ID, message)
      wsRef.current.send(JSON.stringify(chatMessage))
      console.log('Sent:', chatMessage)
      setMessage('')
    }
  }

  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <div className="max-w-2xl mx-auto">
        <h1 className="text-3xl font-bold mb-6 text-gray-800">
          WebSocket Chat
        </h1>

        {/* Connection Status */}
        <div className="mb-4">
          <span className={`inline-block px-3 py-1 rounded-full text-sm font-medium ${isConnected
            ? 'bg-green-100 text-green-800'
            : 'bg-red-100 text-red-800'
            }`}>
            {isConnected ? '● Connected' : '● Disconnected'}
          </span>
        </div>

        {/* Messages Display */}
        <div className="bg-gray-50 rounded-lg p-4 mb-4 h-96 overflow-y-auto">
          {messages.length === 0 ? (
            <p className="text-gray-400 text-center">No messages yet...</p>
          ) : (
            <div className="space-y-3">
              {messages.map((msg, index) => (
                <MessageRenderer
                  key={msg.correlation_id || `${msg.timestamp}-${index}`}
                  message={msg}
                />
              ))}
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        {/* Message Form */}
        <form onSubmit={sendMessage} className="flex gap-2">
          <input
            type="text"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder="Type a message..."
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            disabled={!isConnected}
          />
          <button
            type="submit"
            disabled={!isConnected || !message.trim()}
            className="px-6 py-2 bg-blue-500 text-white rounded-lg font-medium hover:bg-blue-600 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
          >
            Send
          </button>
        </form>
      </div>
    </div>
  )
}

export default App
