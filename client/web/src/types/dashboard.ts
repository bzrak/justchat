export interface UserPublic {
  id: number
  username: string
  is_guest: boolean
  created_at: string
}

export interface UsersPublic {
  total_users: number
  page: number
  page_size: number
  total_pages: number
  users: UserPublic[]
}

export interface MessagePublic {
  channel_id: number
  sender_username: string
  timestamp: string
  content: string
}

export interface MessagesPublic {
  count: number
  messages: MessagePublic[]
}

export interface UserUpdate {
  username?: string
  password?: string
}
