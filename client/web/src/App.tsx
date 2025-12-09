import { useState, useEffect, useRef, type FormEvent } from 'react'
import './App.css'
import { initializeMessageHandlers } from './config/messageRegistry'
import { MessageRenderer } from './components/messages/MessageRenderer'
import { MessageBuilder } from './services/messageBuilder'
import { Sidebar } from './components/Sidebar'
import { MembersList } from './components/MembersList'
import { LoginModal } from './components/LoginModal'
import { useUser } from './contexts/UserContext'
import { useWebSocket } from './contexts/WebSocketContext'
import type { Message } from './types/messages'

interface Channel {
  id: number
  name: string
}

interface Member {
  username: string
  isOnline: boolean // For now, all members from server are considered online
}

function App() {
  const { username, displayName, isAuthenticated, login, logout } = useUser()
  const { isConnected, isReady, messages, sendMessage: wsSendMessage, reconnect } = useWebSocket()
  const [message, setMessage] = useState('')
  const [isLoginModalOpen, setIsLoginModalOpen] = useState(false)
  const [channels, setChannels] = useState<Channel[]>([])
  const [currentChannelId, setCurrentChannelId] = useState<number | null>(null)
  const [isJoinModalOpen, setIsJoinModalOpen] = useState(false)
  const [joinChannelId, setJoinChannelId] = useState('')
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const joinedChannelsRef = useRef<Set<number>>(new Set())

  // Store members per channel (channelId -> Member[])
  const [channelMembers, setChannelMembers] = useState<Map<number, Member[]>>(new Map())

  // Track processed message IDs to avoid duplicate processing
  const processedMessageIds = useRef<Set<string>>(new Set())

  // Initialize message handlers on mount
  useEffect(() => {
    initializeMessageHandlers()
  }, [])

  // Reset joined channels when connection is lost
  useEffect(() => {
    if (!isReady) {
      joinedChannelsRef.current.clear()
    }
  }, [isReady])

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  // Listen for CHANNEL_MEMBERS messages to update member list
  useEffect(() => {
    console.log('[App] Processing messages, total count:', messages.length)

    // Process ALL unprocessed CHANNEL_MEMBERS messages, not just the latest
    messages.forEach((message, index) => {
      // Skip if already processed
      const messageKey = message.id || `${message.timestamp}-${message.type}-${index}`

      console.log(`[App] Checking message ${index}:`, {
        type: message.type,
        messageKey,
        alreadyProcessed: processedMessageIds.current.has(messageKey)
      })

      if (processedMessageIds.current.has(messageKey)) {
        return
      }

      if (message.type === 'channel_members') {
        const payload = message.payload as { channel_id: number; members: { username: string }[] }
        const members: Member[] = payload.members.map(m => ({
          username: m.username,
          isOnline: true // All members in the list are currently online
        }))

        console.log(`[App] UPDATING members for channel ${payload.channel_id}:`, {
          memberCount: members.length,
          members: members.map(m => m.username)
        })

        setChannelMembers(prev => {
          const updated = new Map(prev)
          updated.set(payload.channel_id, members)
          console.log('[App] New channelMembers state:', {
            channelId: payload.channel_id,
            memberCount: members.length,
            allChannels: Array.from(updated.keys())
          })
          return updated
        })

        // Mark as processed
        processedMessageIds.current.add(messageKey)
      }
    })
  }, [messages])

  // Filter messages for current channel
  const filteredMessages = currentChannelId !== null
    ? messages.filter((msg: Message) => {
        // Filter CHAT_SEND messages by channel_id
        if (msg.type === 'chat_send' && 'channel_id' in msg.payload) {
          return msg.payload.channel_id === currentChannelId
        }
        // Show channel join/leave messages for current channel
        if ((msg.type === 'channel_join' || msg.type === 'channel_leave') && 'channel_id' in msg.payload) {
          return msg.payload.channel_id === currentChannelId
        }
        // Show errors in current channel
        if (msg.type === 'error') {
          return true
        }
        return false
      })
    : []

  function handleJoinChannel(e: FormEvent<HTMLFormElement>) {
    e.preventDefault()

    const channelId = parseInt(joinChannelId)
    if (isNaN(channelId) || channelId < 0) {
      alert('Please enter a valid channel ID (positive number)')
      return
    }

    // Check if already joined
    if (joinedChannelsRef.current.has(channelId)) {
      alert('You have already joined this channel')
      setIsJoinModalOpen(false)
      setJoinChannelId('')
      return
    }

    // Send join request (username no longer needed - server knows it)
    const channelJoinMessage = MessageBuilder.channelJoin(channelId)
    wsSendMessage(channelJoinMessage)

    // Add to joined channels
    joinedChannelsRef.current.add(channelId)

    // Add to channels list if not already there
    if (!channels.find(c => c.id === channelId)) {
      setChannels(prev => [...prev, { id: channelId, name: `Channel ${channelId}` }])
    }

    // Set as current channel
    setCurrentChannelId(channelId)

    // Close modal
    setIsJoinModalOpen(false)
    setJoinChannelId('')
  }

  function handleChannelSelect(channelId: number) {
    setCurrentChannelId(channelId)
  }

  function sendMessage(e: FormEvent<HTMLFormElement>) {
    e.preventDefault()

    if (!currentChannelId) {
      alert('Please join a channel first')
      return
    }

    if (message.trim() && isConnected) {
      const chatMessage = MessageBuilder.chatSend(currentChannelId, message)
      wsSendMessage(chatMessage)
      setMessage('')
    }
  }

  function handleLoginSuccess(loggedInUsername: string) {
    login(loggedInUsername)
    // Reconnect WebSocket with new token
    reconnect()
  }

  function handleLogout() {
    logout()
    // Reconnect as guest
    reconnect()
  }

  return (
    <div className="flex h-screen bg-gray-100">
      <LoginModal
        isOpen={isLoginModalOpen}
        onClose={() => setIsLoginModalOpen(false)}
        onLoginSuccess={handleLoginSuccess}
      />

      {/* Join Channel Modal */}
      {isJoinModalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-96 shadow-xl">
            <h2 className="text-xl font-bold mb-4">Join Channel</h2>
            <form onSubmit={handleJoinChannel}>
              <div className="mb-4">
                <label htmlFor="channelId" className="block text-sm font-medium text-gray-700 mb-2">
                  Channel ID
                </label>
                <input
                  id="channelId"
                  type="number"
                  value={joinChannelId}
                  onChange={(e) => setJoinChannelId(e.target.value)}
                  placeholder="Enter channel ID (e.g., 1)"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  autoFocus
                  min="0"
                />
              </div>
              <div className="flex justify-end gap-2">
                <button
                  type="button"
                  onClick={() => {
                    setIsJoinModalOpen(false)
                    setJoinChannelId('')
                  }}
                  className="px-4 py-2 text-gray-700 bg-gray-200 rounded hover:bg-gray-300"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 text-white bg-blue-500 rounded hover:bg-blue-600"
                >
                  Join
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Sidebar */}
      <Sidebar
        channels={channels}
        currentChannelId={currentChannelId}
        onChannelSelect={handleChannelSelect}
        onAddChannel={() => setIsJoinModalOpen(true)}
      />

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className="bg-white border-b border-gray-200 p-4">
          <div className="flex items-center justify-between">
            <h1 className="text-2xl font-bold text-gray-800">
              {currentChannelId !== null
                ? `# ${channels.find(c => c.id === currentChannelId)?.name || `Channel ${currentChannelId}`}`
                : '# Select a channel'}
            </h1>
            <div className="flex items-center gap-3">
              <span className="text-sm text-gray-600">
                {isAuthenticated ? (
                  <>
                    <span className="font-medium text-gray-800">{displayName}</span>
                    {' '}
                    <span className="text-green-600">(authenticated)</span>
                  </>
                ) : (
                  <span className="text-gray-500">Guest mode</span>
                )}
              </span>
              {isAuthenticated ? (
                <button
                  onClick={handleLogout}
                  className="px-3 py-1 text-sm bg-gray-200 text-gray-700 rounded hover:bg-gray-300 transition-colors"
                >
                  Logout
                </button>
              ) : (
                <button
                  onClick={() => setIsLoginModalOpen(true)}
                  className="px-3 py-1 text-sm bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors"
                >
                  Login
                </button>
              )}
              <span className={`inline-block px-3 py-1 rounded-full text-sm font-medium ${isConnected
                ? 'bg-green-100 text-green-800'
                : 'bg-red-100 text-red-800'
                }`}>
                {isConnected ? '● Connected' : '● Disconnected'}
              </span>
            </div>
          </div>
        </div>

        {/* Messages Display */}
        <div className="flex-1 overflow-y-auto p-6 bg-gray-50">
          {currentChannelId === null ? (
            <div className="flex flex-col items-center justify-center h-full text-gray-400">
              <p className="text-lg mb-4">No channel selected</p>
              <button
                onClick={() => setIsJoinModalOpen(true)}
                className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
              >
                Join a Channel
              </button>
            </div>
          ) : filteredMessages.length === 0 ? (
            <p className="text-gray-400 text-center mt-8">No messages in this channel yet...</p>
          ) : (
            <div className="space-y-3 max-w-4xl mx-auto">
              {filteredMessages.map((msg, index) => (
                <MessageRenderer
                  key={msg.id || `${msg.timestamp}-${index}`}
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
              placeholder={
                currentChannelId !== null
                  ? `Message #${channels.find(c => c.id === currentChannelId)?.name || `Channel ${currentChannelId}`}`
                  : 'Join a channel to send messages'
              }
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              disabled={!isConnected || currentChannelId === null}
            />
            <button
              type="submit"
              disabled={!isConnected || !message.trim() || currentChannelId === null}
              className="px-6 py-2 bg-blue-500 text-white rounded-lg font-medium hover:bg-blue-600 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
            >
              Send
            </button>
          </form>
        </div>
      </div>

      {/* Right Sidebar - Members List */}
      <MembersList
        members={(() => {
          const members = currentChannelId !== null ? (channelMembers.get(currentChannelId) || []) : []
          console.log('[App] Passing members to MembersList:', {
            currentChannelId,
            memberCount: members.length,
            members: members.map(m => m.username),
            allChannelsInMap: Array.from(channelMembers.keys()),
            mapSize: channelMembers.size
          })
          return members
        })()}
        currentChannelId={currentChannelId}
      />
    </div>
  )
}

export default App
