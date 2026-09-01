import { apiClient } from './client'
import type { AuthResponse, User } from './types'

export function signup(email: string, password: string, displayName?: string) {
  return apiClient.post<AuthResponse>('/api/auth/signup', {
    email,
    password,
    display_name: displayName || null,
  })
}

export function login(email: string, password: string) {
  return apiClient.post<AuthResponse>('/api/auth/login', { email, password })
}

export function getMe() {
  return apiClient.get<User>('/api/auth/me')
}
