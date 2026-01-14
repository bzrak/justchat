/**
 * Authentication service for API calls
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export interface LoginCredentials {
  username: string
  password: string
}

export interface LoginResponse {
  access_token: string
  token_type: string
  expires_in: number
}

export interface SignupCredentials {
  username: string
  password: string
}

export interface UserPublic {
  id: number
  username: string
}

export class AuthError extends Error {
  statusCode?: number
  detail?: string

  constructor(message: string, statusCode?: number, detail?: string) {
    super(message)
    this.name = 'AuthError'
    this.statusCode = statusCode
    this.detail = detail
  }
}

export const authService = {
  /**
   * Login user and get access token
   */
  async login(credentials: LoginCredentials): Promise<LoginResponse> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(credentials),
      })

      if (!response.ok) {
        const error = await response.json().catch(() => ({}))
        throw new AuthError(
          error.detail || 'Login failed',
          response.status,
          error.detail
        )
      }

      return await response.json()
    } catch (error) {
      if (error instanceof AuthError) {
        throw error
      }
      throw new AuthError('Network error. Please check your connection.')
    }
  },

  /**
   * Sign up a new user (placeholder for future implementation)
   */
  async signup(credentials: SignupCredentials): Promise<UserPublic> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/auth/signup`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(credentials),
      })

      if (!response.ok) {
        const error = await response.json().catch(() => ({}))
        throw new AuthError(
          error.detail || 'Signup failed',
          response.status,
          error.detail
        )
      }

      return await response.json()
    } catch (error) {
      if (error instanceof AuthError) {
        throw error
      }
      throw new AuthError('Network error. Please check your connection.')
    }
  },

  /**
   * Get current user info using token
   */
  async getCurrentUser(token: string): Promise<UserPublic> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/auth/me`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })

      if (!response.ok) {
        throw new AuthError('Failed to get user info', response.status)
      }

      return await response.json()
    } catch (error) {
      if (error instanceof AuthError) {
        throw error
      }
      throw new AuthError('Network error. Please check your connection.')
    }
  },
}
