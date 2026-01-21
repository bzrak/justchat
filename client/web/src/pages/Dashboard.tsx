import { useState, useEffect, useCallback, type FormEvent } from 'react'
import { Link } from 'react-router-dom'
import { dashboardService, DashboardError } from '../services/dashboardService'
import type { UserPublic, MessagePublic, UserUpdate } from '../types/dashboard'

const PAGE_SIZE_OPTIONS = [10, 25, 50]
const MESSAGES_PER_PAGE = 5

// Icon components
function UsersIcon({ className = "w-6 h-6" }: { className?: string }) {
  return (
    <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
    </svg>
  )
}

function UserCheckIcon({ className = "w-6 h-6" }: { className?: string }) {
  return (
    <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4" />
    </svg>
  )
}

function UserGuestIcon({ className = "w-6 h-6" }: { className?: string }) {
  return (
    <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
    </svg>
  )
}

function ChatIcon({ className = "w-6 h-6" }: { className?: string }) {
  return (
    <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
    </svg>
  )
}

function HomeIcon({ className = "w-6 h-6" }: { className?: string }) {
  return (
    <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
    </svg>
  )
}

function DashboardIcon({ className = "w-6 h-6" }: { className?: string }) {
  return (
    <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
    </svg>
  )
}

function PencilIcon({ className = "w-5 h-5" }: { className?: string }) {
  return (
    <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
    </svg>
  )
}

function TrashIcon({ className = "w-5 h-5" }: { className?: string }) {
  return (
    <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
    </svg>
  )
}

function ChevronDownIcon({ className = "w-5 h-5" }: { className?: string }) {
  return (
    <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
    </svg>
  )
}

function ChevronUpIcon({ className = "w-5 h-5" }: { className?: string }) {
  return (
    <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 15l7-7 7 7" />
    </svg>
  )
}

function SearchIcon({ className = "w-5 h-5" }: { className?: string }) {
  return (
    <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
    </svg>
  )
}

function generateAvatarColor(username: string): string {
  const colors = [
    'bg-red-500', 'bg-orange-500', 'bg-amber-500', 'bg-yellow-500',
    'bg-lime-500', 'bg-green-500', 'bg-emerald-500', 'bg-teal-500',
    'bg-cyan-500', 'bg-sky-500', 'bg-blue-500', 'bg-indigo-500',
    'bg-violet-500', 'bg-purple-500', 'bg-fuchsia-500', 'bg-pink-500',
  ]
  let hash = 0
  for (let i = 0; i < username.length; i++) {
    hash = username.charCodeAt(i) + ((hash << 5) - hash)
  }
  return colors[Math.abs(hash) % colors.length]
}

export function Dashboard() {
  const [users, setUsers] = useState<UserPublic[]>([])
  const [totalUsers, setTotalUsers] = useState(0)
  const [currentPage, setCurrentPage] = useState(1)
  const [pageSize, setPageSize] = useState(10)
  const [totalPages, setTotalPages] = useState(1)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [registeredOnly, setRegisteredOnly] = useState(false)
  const [searchInput, setSearchInput] = useState('')
  const [searchQuery, setSearchQuery] = useState('')

  // Stats
  const [registeredCount, setRegisteredCount] = useState(0)
  const [guestCount, setGuestCount] = useState(0)

  // Expanded user state
  const [expandedUserId, setExpandedUserId] = useState<number | null>(null)
  const [userMessages, setUserMessages] = useState<MessagePublic[]>([])
  const [totalMessages, setTotalMessages] = useState(0)
  const [messagesPage, setMessagesPage] = useState(0)
  const [isLoadingMessages, setIsLoadingMessages] = useState(false)

  // Edit modal state
  const [editingUser, setEditingUser] = useState<UserPublic | null>(null)
  const [editUsername, setEditUsername] = useState('')
  const [editPassword, setEditPassword] = useState('')
  const [isEditing, setIsEditing] = useState(false)
  const [editError, setEditError] = useState<string | null>(null)

  // Delete modal state
  const [deletingUser, setDeletingUser] = useState<UserPublic | null>(null)
  const [isDeleting, setIsDeleting] = useState(false)

  // Debounce search input
  useEffect(() => {
    const timer = setTimeout(() => {
      setSearchQuery(searchInput)
      setCurrentPage(1)
    }, 300)
    return () => clearTimeout(timer)
  }, [searchInput])

  const loadUsers = useCallback(async () => {
    setIsLoading(true)
    setError(null)
    try {
      const response = await dashboardService.getUsers(currentPage, pageSize, registeredOnly, searchQuery || undefined)
      setUsers(response.users)
      setTotalUsers(response.total_users)
      setTotalPages(response.total_pages)

      // Calculate stats from current page (ideally this would come from a stats endpoint)
      const registered = response.users.filter(u => !u.is_guest).length
      const guests = response.users.filter(u => u.is_guest).length
      setRegisteredCount(registered)
      setGuestCount(guests)
    } catch (err) {
      if (err instanceof DashboardError) {
        setError(err.detail || err.message)
      } else {
        setError('Failed to load users')
      }
    } finally {
      setIsLoading(false)
    }
  }, [currentPage, pageSize, registeredOnly, searchQuery])

  useEffect(() => {
    loadUsers()
  }, [loadUsers])

  async function loadUserMessages(userId: number, page: number = 0) {
    setIsLoadingMessages(true)
    try {
      const response = await dashboardService.getUserMessages(userId, page * MESSAGES_PER_PAGE, MESSAGES_PER_PAGE)
      setUserMessages(response.messages)
      setTotalMessages(response.count)
      setMessagesPage(page)
    } catch (err) {
      console.error('Failed to load messages:', err)
      setUserMessages([])
      setTotalMessages(0)
    } finally {
      setIsLoadingMessages(false)
    }
  }

  function handleRowClick(user: UserPublic) {
    if (expandedUserId === user.id) {
      setExpandedUserId(null)
      setUserMessages([])
      setTotalMessages(0)
      setMessagesPage(0)
    } else {
      setExpandedUserId(user.id)
      loadUserMessages(user.id, 0)
    }
  }

  function openEditModal(user: UserPublic, e: React.MouseEvent) {
    e.stopPropagation()
    setEditingUser(user)
    setEditUsername(user.username)
    setEditPassword('')
    setEditError(null)
  }

  function closeEditModal() {
    setEditingUser(null)
    setEditUsername('')
    setEditPassword('')
    setEditError(null)
  }

  async function handleEditSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault()
    if (!editingUser) return

    setIsEditing(true)
    setEditError(null)

    const updateData: UserUpdate = {}
    if (editUsername !== editingUser.username) {
      updateData.username = editUsername
    }
    if (editPassword) {
      updateData.password = editPassword
    }

    if (Object.keys(updateData).length === 0) {
      closeEditModal()
      return
    }

    try {
      const updatedUser = await dashboardService.updateUser(editingUser.id, updateData)
      setUsers(users.map(u => u.id === updatedUser.id ? updatedUser : u))
      closeEditModal()
    } catch (err) {
      if (err instanceof DashboardError) {
        setEditError(err.detail || err.message)
      } else {
        setEditError('Failed to update user')
      }
    } finally {
      setIsEditing(false)
    }
  }

  function openDeleteModal(user: UserPublic, e: React.MouseEvent) {
    e.stopPropagation()
    setDeletingUser(user)
  }

  function closeDeleteModal() {
    setDeletingUser(null)
  }

  async function handleDeleteConfirm() {
    if (!deletingUser) return

    setIsDeleting(true)
    try {
      await dashboardService.deleteUser(deletingUser.id)
      if (expandedUserId === deletingUser.id) {
        setExpandedUserId(null)
        setUserMessages([])
      }
      closeDeleteModal()
      loadUsers()
    } catch (err) {
      console.error('Failed to delete user:', err)
    } finally {
      setIsDeleting(false)
    }
  }

  const totalMessagesPages = Math.ceil(totalMessages / MESSAGES_PER_PAGE)

  return (
    <div className="min-h-screen bg-slate-900 flex">
      {/* Sidebar */}
      <aside className="w-64 bg-slate-800 border-r border-slate-700 flex flex-col">
        <div className="p-6 border-b border-slate-700">
          <h1 className="text-xl font-bold text-white flex items-center gap-2">
            <DashboardIcon className="w-6 h-6 text-blue-400" />
            Admin Panel
          </h1>
        </div>

        <nav className="flex-1 p-4">
          <ul className="space-y-2">
            <li>
              <Link
                to="/"
                className="flex items-center gap-3 px-4 py-3 text-slate-300 hover:bg-slate-700 rounded-lg transition-colors"
              >
                <HomeIcon className="w-5 h-5" />
                Back to Chat
              </Link>
            </li>
            <li>
              <Link
                to="/dashboard"
                className="flex items-center gap-3 px-4 py-3 text-white bg-blue-600 rounded-lg"
              >
                <UsersIcon className="w-5 h-5" />
                Users
              </Link>
            </li>
          </ul>
        </nav>

        <div className="p-4 border-t border-slate-700">
          <p className="text-xs text-slate-500 text-center">JustChat Admin v1.0</p>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-auto">
        {/* Header */}
        <header className="bg-slate-800 border-b border-slate-700 px-8 py-6">
          <h2 className="text-2xl font-bold text-white">User Management</h2>
          <p className="text-slate-400 mt-1">Manage and monitor all registered users</p>
        </header>

        <div className="p-8">
          {/* Stats Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <div className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-2xl p-6 shadow-lg shadow-blue-500/20">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-blue-100 text-sm font-medium">Total Users</p>
                  <p className="text-3xl font-bold text-white mt-1">{totalUsers}</p>
                </div>
                <div className="bg-white/20 rounded-xl p-3">
                  <UsersIcon className="w-8 h-8 text-white" />
                </div>
              </div>
            </div>

            <div className="bg-gradient-to-br from-emerald-500 to-emerald-600 rounded-2xl p-6 shadow-lg shadow-emerald-500/20">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-emerald-100 text-sm font-medium">Registered</p>
                  <p className="text-3xl font-bold text-white mt-1">{registeredCount}</p>
                </div>
                <div className="bg-white/20 rounded-xl p-3">
                  <UserCheckIcon className="w-8 h-8 text-white" />
                </div>
              </div>
            </div>

            <div className="bg-gradient-to-br from-amber-500 to-amber-600 rounded-2xl p-6 shadow-lg shadow-amber-500/20">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-amber-100 text-sm font-medium">Guests</p>
                  <p className="text-3xl font-bold text-white mt-1">{guestCount}</p>
                </div>
                <div className="bg-white/20 rounded-xl p-3">
                  <UserGuestIcon className="w-8 h-8 text-white" />
                </div>
              </div>
            </div>

            <div className="bg-gradient-to-br from-purple-500 to-purple-600 rounded-2xl p-6 shadow-lg shadow-purple-500/20">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-purple-100 text-sm font-medium">Messages</p>
                  <p className="text-3xl font-bold text-white mt-1">{totalMessages || '-'}</p>
                </div>
                <div className="bg-white/20 rounded-xl p-3">
                  <ChatIcon className="w-8 h-8 text-white" />
                </div>
              </div>
            </div>
          </div>

          {/* Error State */}
          {error && (
            <div className="mb-6 bg-red-500/10 border border-red-500/20 text-red-400 px-6 py-4 rounded-xl">
              {error}
            </div>
          )}

          {/* Users Table Card */}
          <div className="bg-slate-800 rounded-2xl shadow-xl border border-slate-700 overflow-hidden">
            <div className="px-6 py-5 border-b border-slate-700 flex justify-between items-center">
              <div className="flex items-center gap-4">
                <h3 className="text-lg font-semibold text-white">All Users</h3>
                <div className="relative">
                  <SearchIcon className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                  <input
                    type="text"
                    value={searchInput}
                    onChange={(e) => setSearchInput(e.target.value)}
                    placeholder="Search username..."
                    className="pl-9 pr-4 py-2 bg-slate-700 text-slate-200 text-sm rounded-lg border border-slate-600 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent placeholder-slate-400 w-64"
                  />
                </div>
              </div>
              <div className="flex items-center gap-4">
                <label className="flex items-center gap-2 cursor-pointer">
                  <span className="text-sm text-slate-400">Registered only</span>
                  <button
                    onClick={() => {
                      setCurrentPage(1)
                      setRegisteredOnly(!registeredOnly)
                    }}
                    className={`relative w-11 h-6 rounded-full transition-colors ${
                      registeredOnly ? 'bg-blue-600' : 'bg-slate-600'
                    }`}
                  >
                    <span
                      className={`absolute top-1 left-1 w-4 h-4 bg-white rounded-full transition-transform ${
                        registeredOnly ? 'translate-x-5' : 'translate-x-0'
                      }`}
                    />
                  </button>
                </label>
                <div className="flex items-center gap-2">
                  <span className="text-sm text-slate-400">Show</span>
                  <select
                    value={pageSize}
                    onChange={(e) => {
                      setCurrentPage(1)
                      setPageSize(Number(e.target.value))
                    }}
                    className="bg-slate-700 text-slate-300 text-sm rounded-lg px-3 py-1.5 border border-slate-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    {PAGE_SIZE_OPTIONS.map(size => (
                      <option key={size} value={size}>{size}</option>
                    ))}
                  </select>
                </div>
                <span className="text-sm text-slate-400">{totalUsers} total</span>
              </div>
            </div>

            {/* Loading State */}
            {isLoading && (
              <div className="px-6 py-12 text-center">
                <div className="inline-block w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
                <p className="text-slate-400 mt-4">Loading users...</p>
              </div>
            )}

            {/* Users Table */}
            {!isLoading && !error && (
              <>
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="bg-slate-700/50">
                        <th className="px-6 py-4 text-left text-xs font-semibold text-slate-300 uppercase tracking-wider">
                          User
                        </th>
                        <th className="px-6 py-4 text-left text-xs font-semibold text-slate-300 uppercase tracking-wider">
                          Status
                        </th>
                        <th className="px-6 py-4 text-left text-xs font-semibold text-slate-300 uppercase tracking-wider">
                          Joined
                        </th>
                        <th className="px-6 py-4 text-left text-xs font-semibold text-slate-300 uppercase tracking-wider">
                          ID
                        </th>
                        <th className="px-6 py-4 text-right text-xs font-semibold text-slate-300 uppercase tracking-wider">
                          Actions
                        </th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-700">
                      {users.map(user => (
                        <>
                          <tr
                            key={user.id}
                            onClick={() => handleRowClick(user)}
                            className="hover:bg-slate-700/50 cursor-pointer transition-colors group"
                          >
                            <td className="px-6 py-4">
                              <div className="flex items-center gap-4">
                                <div className={`w-10 h-10 rounded-full ${generateAvatarColor(user.username)} flex items-center justify-center text-white font-semibold text-sm`}>
                                  {user.username.charAt(0).toUpperCase()}
                                </div>
                                <div className="flex items-center gap-2">
                                  <span className="text-white font-medium">{user.username}</span>
                                  {expandedUserId === user.id ? (
                                    <ChevronUpIcon className="w-4 h-4 text-slate-400" />
                                  ) : (
                                    <ChevronDownIcon className="w-4 h-4 text-slate-400 opacity-0 group-hover:opacity-100 transition-opacity" />
                                  )}
                                </div>
                              </div>
                            </td>
                            <td className="px-6 py-4">
                              {user.is_guest ? (
                                <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium bg-amber-500/10 text-amber-400 border border-amber-500/20">
                                  <span className="w-1.5 h-1.5 rounded-full bg-amber-400"></span>
                                  Guest
                                </span>
                              ) : (
                                <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
                                  Registered
                                </span>
                              )}
                            </td>
                            <td className="px-6 py-4">
                              <span className="text-slate-400 text-sm">
                                {new Date(user.created_at).toLocaleDateString()}
                              </span>
                            </td>
                            <td className="px-6 py-4">
                              <span className="text-slate-400 font-mono text-sm">#{user.id}</span>
                            </td>
                            <td className="px-6 py-4">
                              <div className="flex items-center justify-end gap-2">
                                <button
                                  onClick={(e) => openEditModal(user, e)}
                                  className="p-2 text-slate-400 hover:text-blue-400 hover:bg-blue-500/10 rounded-lg transition-colors"
                                  title="Edit user"
                                >
                                  <PencilIcon />
                                </button>
                                <button
                                  onClick={(e) => openDeleteModal(user, e)}
                                  className="p-2 text-slate-400 hover:text-red-400 hover:bg-red-500/10 rounded-lg transition-colors"
                                  title="Delete user"
                                >
                                  <TrashIcon />
                                </button>
                              </div>
                            </td>
                          </tr>
                          {/* Expanded Messages Row */}
                          {expandedUserId === user.id && (
                            <tr key={`${user.id}-messages`}>
                              <td colSpan={5} className="px-6 py-4 bg-slate-900/50">
                                <div className="bg-slate-800 rounded-xl border border-slate-700 p-5">
                                  <h4 className="font-semibold text-white mb-4 flex items-center gap-2">
                                    <ChatIcon className="w-5 h-5 text-purple-400" />
                                    Message History
                                    <span className="text-sm font-normal text-slate-400">({totalMessages} total)</span>
                                  </h4>
                                  {isLoadingMessages ? (
                                    <div className="flex items-center justify-center py-8">
                                      <div className="w-6 h-6 border-3 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
                                    </div>
                                  ) : userMessages.length === 0 ? (
                                    <p className="text-slate-500 text-sm py-4 text-center">No messages found</p>
                                  ) : (
                                    <>
                                      <div className="space-y-3 mb-4">
                                        {userMessages.map((msg, idx) => (
                                          <div key={idx} className="bg-slate-900/50 rounded-lg p-4 border border-slate-700">
                                            <div className="flex justify-between text-xs text-slate-500 mb-2">
                                              <span className="bg-slate-700 px-2 py-0.5 rounded">Channel #{msg.channel_id}</span>
                                              <span>{new Date(msg.timestamp).toLocaleString()}</span>
                                            </div>
                                            <p className="text-slate-300">{msg.content}</p>
                                          </div>
                                        ))}
                                      </div>
                                      {/* Messages Pagination */}
                                      {totalMessagesPages > 1 && (
                                        <div className="flex justify-center items-center gap-3 pt-2">
                                          <button
                                            onClick={(e) => {
                                              e.stopPropagation()
                                              loadUserMessages(user.id, messagesPage - 1)
                                            }}
                                            disabled={messagesPage === 0}
                                            className="px-4 py-2 text-sm bg-slate-700 text-slate-300 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-slate-600 transition-colors"
                                          >
                                            Previous
                                          </button>
                                          <span className="text-sm text-slate-400">
                                            Page {messagesPage + 1} of {totalMessagesPages}
                                          </span>
                                          <button
                                            onClick={(e) => {
                                              e.stopPropagation()
                                              loadUserMessages(user.id, messagesPage + 1)
                                            }}
                                            disabled={messagesPage >= totalMessagesPages - 1}
                                            className="px-4 py-2 text-sm bg-slate-700 text-slate-300 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-slate-600 transition-colors"
                                          >
                                            Next
                                          </button>
                                        </div>
                                      )}
                                    </>
                                  )}
                                </div>
                              </td>
                            </tr>
                          )}
                        </>
                      ))}
                    </tbody>
                  </table>
                </div>

                {/* Empty State */}
                {users.length === 0 && (
                  <div className="px-6 py-12 text-center">
                    <UsersIcon className="w-12 h-12 text-slate-600 mx-auto mb-4" />
                    <p className="text-slate-400">No users found</p>
                  </div>
                )}

                {/* Pagination */}
                {totalPages > 1 && (
                  <div className="px-6 py-4 border-t border-slate-700 flex justify-between items-center">
                    <button
                      onClick={() => setCurrentPage(p => p - 1)}
                      disabled={currentPage === 1}
                      className="px-5 py-2.5 bg-slate-700 text-slate-300 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-slate-600 transition-colors font-medium"
                    >
                      Previous
                    </button>
                    <div className="flex items-center gap-2">
                      {Array.from({ length: Math.min(totalPages, 5) }, (_, i) => {
                        let pageNum = i + 1
                        if (totalPages > 5) {
                          if (currentPage <= 3) {
                            pageNum = i + 1
                          } else if (currentPage > totalPages - 3) {
                            pageNum = totalPages - 4 + i
                          } else {
                            pageNum = currentPage - 2 + i
                          }
                        }
                        return (
                          <button
                            key={pageNum}
                            onClick={() => setCurrentPage(pageNum)}
                            className={`w-10 h-10 rounded-lg font-medium transition-colors ${
                              currentPage === pageNum
                                ? 'bg-blue-600 text-white'
                                : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
                            }`}
                          >
                            {pageNum}
                          </button>
                        )
                      })}
                    </div>
                    <button
                      onClick={() => setCurrentPage(p => p + 1)}
                      disabled={currentPage >= totalPages}
                      className="px-5 py-2.5 bg-slate-700 text-slate-300 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-slate-600 transition-colors font-medium"
                    >
                      Next
                    </button>
                  </div>
                )}
              </>
            )}
          </div>
        </div>
      </main>

      {/* Edit Modal */}
      {editingUser && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50">
          <div className="bg-slate-800 rounded-2xl shadow-2xl p-8 w-full max-w-md border border-slate-700">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-xl font-bold text-white">Edit User</h2>
              <button
                onClick={closeEditModal}
                className="text-slate-400 hover:text-white transition-colors p-1"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            <form onSubmit={handleEditSubmit} className="space-y-5">
              {editError && (
                <div className="bg-red-500/10 border border-red-500/20 text-red-400 px-4 py-3 rounded-xl text-sm">
                  {editError}
                </div>
              )}

              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">
                  Username
                </label>
                <input
                  type="text"
                  value={editUsername}
                  onChange={(e) => setEditUsername(e.target.value)}
                  className="w-full px-4 py-3 bg-slate-900 border border-slate-700 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                  required
                  disabled={isEditing}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">
                  New Password
                  <span className="text-slate-500 font-normal ml-1">(leave empty to keep current)</span>
                </label>
                <input
                  type="password"
                  value={editPassword}
                  onChange={(e) => setEditPassword(e.target.value)}
                  className="w-full px-4 py-3 bg-slate-900 border border-slate-700 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                  placeholder="Enter new password"
                  disabled={isEditing}
                />
              </div>

              <div className="flex gap-3 pt-4">
                <button
                  type="submit"
                  disabled={isEditing}
                  className="flex-1 bg-blue-600 text-white py-3 px-4 rounded-xl font-semibold hover:bg-blue-500 disabled:bg-slate-700 disabled:cursor-not-allowed transition-colors"
                >
                  {isEditing ? 'Saving...' : 'Save Changes'}
                </button>
                <button
                  type="button"
                  onClick={closeEditModal}
                  disabled={isEditing}
                  className="flex-1 bg-slate-700 text-slate-300 py-3 px-4 rounded-xl font-semibold hover:bg-slate-600 disabled:bg-slate-800 disabled:cursor-not-allowed transition-colors"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Delete Confirmation Modal */}
      {deletingUser && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50">
          <div className="bg-slate-800 rounded-2xl shadow-2xl p-8 w-full max-w-md border border-slate-700">
            <div className="text-center mb-6">
              <div className="w-16 h-16 bg-red-500/10 rounded-full flex items-center justify-center mx-auto mb-4">
                <TrashIcon className="w-8 h-8 text-red-500" />
              </div>
              <h2 className="text-xl font-bold text-white mb-2">Delete User</h2>
              <p className="text-slate-400">
                Are you sure you want to delete <strong className="text-white">{deletingUser.username}</strong>?
                <br />
                <span className="text-red-400 text-sm">This action cannot be undone.</span>
              </p>
            </div>
            <div className="flex gap-3">
              <button
                onClick={handleDeleteConfirm}
                disabled={isDeleting}
                className="flex-1 bg-red-600 text-white py-3 px-4 rounded-xl font-semibold hover:bg-red-500 disabled:bg-slate-700 disabled:cursor-not-allowed transition-colors"
              >
                {isDeleting ? 'Deleting...' : 'Delete User'}
              </button>
              <button
                onClick={closeDeleteModal}
                disabled={isDeleting}
                className="flex-1 bg-slate-700 text-slate-300 py-3 px-4 rounded-xl font-semibold hover:bg-slate-600 disabled:bg-slate-800 disabled:cursor-not-allowed transition-colors"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
