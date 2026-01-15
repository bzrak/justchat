import { createContext, useContext, useState, useEffect, type ReactNode } from 'react'
import { tokenStorage } from '../services/tokenStorage'

interface UserContextType {
  username: string
  displayName: string
  setUsername: (username: string, isGuest?: boolean) => void
  avatarColor: string
  isAuthenticated: boolean
  isGuest: boolean
  login: (username: string) => void
  logout: () => void
}

const UserContext = createContext<UserContextType | undefined>(undefined)

function generateAvatarColor(): string {
  const colors = [
    'bg-blue-500',
    'bg-purple-500',
    'bg-pink-500',
    'bg-green-500',
    'bg-yellow-500',
    'bg-red-500',
    'bg-indigo-500',
    'bg-teal-500',
  ]
  return colors[Math.floor(Math.random() * colors.length)]
}

export function UserProvider({ children }: { children: ReactNode }) {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(() => {
    return tokenStorage.hasValidToken()
  })

  const [isGuest, setIsGuest] = useState<boolean>(() => {
    const stored = localStorage.getItem('chat-is-guest')
    return stored === 'true'
  })

  const [displayName, setDisplayName] = useState<string>(() => {
    const stored = localStorage.getItem('chat-display-name')
    return stored || 'Guest'
  })

  const [avatarColor] = useState<string>(() => {
    const stored = localStorage.getItem('chat-avatar-color')
    return stored || generateAvatarColor()
  })

  const username = displayName

  useEffect(() => {
    localStorage.setItem('chat-display-name', displayName)
  }, [displayName])

  useEffect(() => {
    localStorage.setItem('chat-avatar-color', avatarColor)
  }, [avatarColor])

  useEffect(() => {
    localStorage.setItem('chat-is-guest', isGuest.toString())
  }, [isGuest])

  const setUsername = (newDisplayName: string, newIsGuest: boolean = true) => {
    setDisplayName(newDisplayName)
    setIsGuest(newIsGuest)
  }

  const login = (loggedInUsername: string) => {
    setDisplayName(loggedInUsername)
    setIsAuthenticated(true)
    setIsGuest(false)
  }

  const logout = () => {
    tokenStorage.clearToken()
    setIsAuthenticated(false)
    setIsGuest(true)
    setDisplayName('Guest')
  }

  return (
    <UserContext.Provider
      value={{
        username,
        displayName,
        setUsername,
        avatarColor,
        isAuthenticated,
        isGuest,
        login,
        logout
      }}
    >
      {children}
    </UserContext.Provider>
  )
}

export function useUser() {
  const context = useContext(UserContext)
  if (context === undefined) {
    throw new Error('useUser must be used within a UserProvider')
  }
  return context
}
