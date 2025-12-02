import { createContext, useContext, useEffect, useRef, useState, useCallback, type ReactNode } from 'react'
import { MessageBuilder } from '../services/messageBuilder'
import { parseMessage } from '../services/messageParser'
import type { Message } from '../types/messages'
import { tokenStorage } from '../services/tokenStorage'

interface WebSocketContextType {
  isConnected: boolean
  messages: Message[]
  sendMessage: (message: any) => void
  reconnect: () => void
  disconnect: () => void
  clearMessages: () => void
  isReady: boolean // True after HELLO is sent and connection is established
}

const WebSocketContext = createContext<WebSocketContextType | undefined>(undefined)

const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws'

interface WebSocketProviderProps {
  children: ReactNode
  username: string
  enabled?: boolean // Allow disabling WebSocket until user is ready
}

export function WebSocketProvider({ children, username, enabled = true }: WebSocketProviderProps) {
  const [isConnected, setIsConnected] = useState(false)
  const [isReady, setIsReady] = useState(false)
  const [messages, setMessages] = useState<Message[]>([])
  const wsRef = useRef<WebSocket | null>(null)
  const reconnectTimeoutRef = useRef<NodeJS.Timeout>()
  const isIntentionalDisconnect = useRef(false)

  const connect = useCallback(() => {
    if (!enabled || !username) {
      console.log('WebSocket connection disabled or no username')
      return
    }

    // Don't reconnect if already connected
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      console.log('WebSocket already connected')
      return
    }

    console.log('Connecting to WebSocket...')
    const ws = new WebSocket(WS_URL)

    ws.onopen = () => {
      console.log('Connected to WebSocket')
      setIsConnected(true)

      // Get token if available
      const token = tokenStorage.getToken()

      // Send Hello message with optional token
      const helloMessage = MessageBuilder.hello(username, token || undefined)
      ws.send(JSON.stringify(helloMessage))
      console.log('Sent Hello:', helloMessage)

      // Mark as ready for application to send additional messages
      setIsReady(true)
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

    ws.onclose = (event) => {
      console.log('Disconnected from WebSocket', event.code, event.reason)
      setIsConnected(false)
      setIsReady(false)
      wsRef.current = null

      // Auto-reconnect unless intentional disconnect
      if (!isIntentionalDisconnect.current && enabled) {
        console.log('Attempting to reconnect in 3 seconds...')
        reconnectTimeoutRef.current = setTimeout(() => {
          connect()
        }, 3000)
      }
    }

    wsRef.current = ws
  }, [username, enabled])

  const disconnect = useCallback(() => {
    isIntentionalDisconnect.current = true
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current)
    }
    if (wsRef.current) {
      // Remove event listeners before closing
      wsRef.current.onopen = null
      wsRef.current.onmessage = null
      wsRef.current.onerror = null
      wsRef.current.onclose = null
      wsRef.current.close()
      wsRef.current = null
    }
    setIsConnected(false)
    setIsReady(false)
  }, [])

  const reconnect = useCallback(() => {
    console.log('Manual reconnect triggered')
    isIntentionalDisconnect.current = false
    disconnect()
    setTimeout(() => {
      connect()
    }, 500)
  }, [connect, disconnect])

  const sendMessage = useCallback((message: any) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message))
      console.log('Sent message:', message)
    } else {
      console.error('WebSocket not connected')
    }
  }, [])

  const clearMessages = useCallback(() => {
    setMessages([])
  }, [])

  // Connect on mount only - do NOT reconnect on username change
  useEffect(() => {
    isIntentionalDisconnect.current = false
    connect()

    return () => {
      disconnect()
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []) // Empty deps - only connect on mount

  const value: WebSocketContextType = {
    isConnected,
    isReady,
    messages,
    sendMessage,
    reconnect,
    disconnect,
    clearMessages,
  }

  return (
    <WebSocketContext.Provider value={value}>
      {children}
    </WebSocketContext.Provider>
  )
}

export function useWebSocket() {
  const context = useContext(WebSocketContext)
  if (context === undefined) {
    throw new Error('useWebSocket must be used within a WebSocketProvider')
  }
  return context
}
