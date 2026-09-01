import { useQuery, useQueryClient } from '@tanstack/react-query'
import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react'
import type { ReactNode } from 'react'

import { getMe, login as apiLogin, signup as apiSignup } from '../api/authApi'
import { clearToken, getToken, setToken } from '../api/authToken'
import type { User } from '../api/types'

const USER_CACHE_KEY = 'pf_auth_user'

function readCachedUser(): User | null {
  try {
    const raw = localStorage.getItem(USER_CACHE_KEY)
    return raw ? (JSON.parse(raw) as User) : null
  } catch {
    return null
  }
}

function writeCachedUser(user: User | null): void {
  try {
    if (user) localStorage.setItem(USER_CACHE_KEY, JSON.stringify(user))
    else localStorage.removeItem(USER_CACHE_KEY)
  } catch {
    // ignore
  }
}

interface AuthValue {
  user: User | null
  // Convenience alias — user.id IS the owning learner_id everywhere in
  // this system (see stores/account-store's docstring). Kept as its own
  // field so the ~9 existing call sites of the old useLearnerSession()
  // hook needed minimal changes when this replaced it.
  learnerId: string | null
  isLoading: boolean
  login: (email: string, password: string) => Promise<void>
  signup: (email: string, password: string, displayName?: string) => Promise<void>
  logout: () => void
}

const AuthContext = createContext<AuthValue | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const queryClient = useQueryClient()
  const [hasToken, setHasToken] = useState(() => !!getToken())
  // Hydrate optimistically from the last-known cached user so the UI
  // doesn't flash a logged-out state on every reload while /api/auth/me
  // is still in flight.
  const [user, setUser] = useState<User | null>(() => (getToken() ? readCachedUser() : null))

  const meQuery = useQuery({
    queryKey: ['me'],
    queryFn: getMe,
    enabled: hasToken,
    retry: false,
  })

  useEffect(() => {
    if (meQuery.data) {
      setUser(meQuery.data)
      writeCachedUser(meQuery.data)
    }
  }, [meQuery.data])

  useEffect(() => {
    if (meQuery.isError) {
      setUser(null)
      writeCachedUser(null)
      clearToken()
      setHasToken(false)
    }
  }, [meQuery.isError])

  const applyAuthResult = useCallback(
    (token: string, authedUser: User) => {
      setToken(token)
      writeCachedUser(authedUser)
      setUser(authedUser)
      setHasToken(true)
      queryClient.setQueryData(['me'], authedUser)
    },
    [queryClient],
  )

  const login = useCallback(
    async (email: string, password: string) => {
      const result = await apiLogin(email, password)
      applyAuthResult(result.access_token, result.user)
    },
    [applyAuthResult],
  )

  const signup = useCallback(
    async (email: string, password: string, displayName?: string) => {
      const result = await apiSignup(email, password, displayName)
      applyAuthResult(result.access_token, result.user)
    },
    [applyAuthResult],
  )

  const logout = useCallback(() => {
    clearToken()
    writeCachedUser(null)
    setUser(null)
    setHasToken(false)
    queryClient.clear()
  }, [queryClient])

  // Only "loading" while we have a token but haven't resolved a user yet
  // (first paint after a reload) — never loading for a logged-out visitor.
  const isLoading = hasToken && meQuery.isPending && !user

  const value = useMemo<AuthValue>(
    () => ({
      user,
      learnerId: user?.id ?? null,
      isLoading,
      login,
      signup,
      logout,
    }),
    [user, isLoading, login, signup, logout],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return ctx
}
