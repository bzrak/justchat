import { useState, useEffect, useRef, type FormEvent } from 'react'
import './App.css'
import { initializeMessageHandlers } from './config/messageRegistry'
import type { Message } from './types/messages'
import { parseMessage } from './services/messageParser'
import { MessageRenderer } from './components/messages/MessageRenderer'
import { MessageBuilder } from './services/messageBuilder'
import { Sidebar } from './components/Sidebar'
import { useUser } from './contexts/UserContext'

function App() {
  const { username } = useUser()
  // TODO: Replace with actual room ID management
  const TEMP_ROOM_ID = useRef(crypto.randomUUID()).current
  const [message, setMessage] = useState('')
  const [messages, setMessages] = useState<Message[]>([])
  const [isConnected, setIsConnected] = useState(false)
  const [channels, setChannels] = useState([
    { id: '1', name: 'general' },
    { id: '2', name: 'random' }
  ])
  const [currentChannelId, setCurrentChannelId] = useState('1')
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

      // Send Hello message first to establish connection
      const helloMessage = MessageBuilder.hello(username)
      ws.send(JSON.stringify(helloMessage))
      console.log('Sent Hello:', helloMessage)

      // Then send Channel Join message
      const channelJoinMessage = MessageBuilder.channelJoin(parseInt(currentChannelId), username)
      ws.send(JSON.stringify(channelJoinMessage))
      console.log('Sent Channel Join:', channelJoinMessage)
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
      const chatMessage = MessageBuilder.chatSend(TEMP_ROOM_ID, message, username)
      wsRef.current.send(JSON.stringify(chatMessage))
      console.log('Sent:', chatMessage)
      setMessage('')
    }
  }

  return (
    <div className="flex h-screen bg-gray-100">
      {/* Sidebar */}
      <Sidebar
        channels={channels}
        currentChannelId={currentChannelId}
        onChannelSelect={setCurrentChannelId}
      />

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className="bg-white border-b border-gray-200 p-4">
          <div className="flex items-center justify-between">
            <h1 className="text-2xl font-bold text-gray-800">
              # {channels.find(c => c.id === currentChannelId)?.name || 'chat'}
            </h1>
            <span className={`inline-block px-3 py-1 rounded-full text-sm font-medium ${isConnected
              ? 'bg-green-100 text-green-800'
              : 'bg-red-100 text-red-800'
              }`}>
              {isConnected ? '● Connected' : '● Disconnected'}
            </span>
          </div>
        </div>

        {/* Messages Display */}
        <div className="flex-1 overflow-y-auto p-6 bg-gray-50">
          {messages.length === 0 ? (
            <p className="text-gray-400 text-center mt-8">No messages yet...</p>
          ) : (
            <div className="space-y-3 max-w-4xl mx-auto">
              {messages.map((msg, index) => (
                <MessageRenderer
                  key={msg.correlation_id || `${msg.timestamp}-${index}`}
                  message={msg}
                  currentUsername={username}
                />
              ))}
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        {/* Message Form */}
        <div className="bg-white border-t border-gray-200 p-4">
          <form onSubmit={sendMessage} className="flex gap-2 max-w-4xl mx-auto">
            <input
              type="text"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              placeholder={`Message #${channels.find(c => c.id === currentChannelId)?.name || 'chat'}`}
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
    </div>
  )
}

export default App
