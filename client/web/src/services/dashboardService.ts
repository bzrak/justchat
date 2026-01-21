import { tokenStorage } from './tokenStorage'
import type { UserPublic, UsersPublic, MessagesPublic, UserUpdate } from '../types/dashboard'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export class DashboardError extends Error {
  statusCode?: number
  detail?: string

  constructor(message: string, statusCode?: number, detail?: string) {
    super(message)
    this.name = 'DashboardError'
    this.statusCode = statusCode
    this.detail = detail
  }
}

function getAuthHeaders(): HeadersInit {
  const token = tokenStorage.getToken()
  return {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json',
  }
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const error = await response.json().catch(() => ({}))
    throw new DashboardError(
      error.detail || 'Request failed',
      response.status,
      error.detail
    )
  }
  return await response.json()
}

export const dashboardService = {
  async getUsers(page: number = 1, pageSize: number = 10, registeredOnly: boolean = false): Promise<UsersPublic> {
    const params = new URLSearchParams({
      page: page.toString(),
      page_size: pageSize.toString(),
    })
    if (registeredOnly) {
      params.append('registered_only', 'true')
    }
    const response = await fetch(
      `${API_BASE_URL}/api/v1/dashboard/users/?${params.toString()}`,
      {
        method: 'GET',
        headers: getAuthHeaders(),
      }
    )
    return handleResponse<UsersPublic>(response)
  },

  async getUser(id: number): Promise<UserPublic> {
    const response = await fetch(
      `${API_BASE_URL}/api/v1/dashboard/users/${id}`,
      {
        method: 'GET',
        headers: getAuthHeaders(),
      }
    )
    return handleResponse<UserPublic>(response)
  },

  async getUserMessages(id: number, offset: number = 0, limit: number = 10): Promise<MessagesPublic> {
    const response = await fetch(
      `${API_BASE_URL}/api/v1/dashboard/users/${id}/messages?offset=${offset}&limit=${limit}`,
      {
        method: 'GET',
        headers: getAuthHeaders(),
      }
    )
    return handleResponse<MessagesPublic>(response)
  },

  async updateUser(id: number, data: UserUpdate): Promise<UserPublic> {
    const response = await fetch(
      `${API_BASE_URL}/api/v1/dashboard/users/${id}`,
      {
        method: 'PATCH',
        headers: getAuthHeaders(),
        body: JSON.stringify(data),
      }
    )
    return handleResponse<UserPublic>(response)
  },

  async deleteUser(id: number): Promise<void> {
    const response = await fetch(
      `${API_BASE_URL}/api/v1/dashboard/users/${id}`,
      {
        method: 'DELETE',
        headers: getAuthHeaders(),
      }
    )
    if (!response.ok) {
      const error = await response.json().catch(() => ({}))
      throw new DashboardError(
        error.detail || 'Delete failed',
        response.status,
        error.detail
      )
    }
  },
}
