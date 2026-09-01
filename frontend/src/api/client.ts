import { clearToken, getToken } from './authToken'

const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'

export class ApiError extends Error {
  status: number
  code: string

  constructor(status: number, code: string, message: string) {
    super(message)
    this.status = status
    this.code = code
  }
}

interface ErrorEnvelope {
  error?: { code: string; message: string }
  detail?: { code: string; message: string } | string
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const token = getToken()
  const res = await fetch(`${BASE_URL}${path}`, {
    ...init,
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(init?.headers ?? {}),
    },
  })

  if (res.status === 401) {
    // Stale/expired/missing token — clear it and force back to login.
    // A hard redirect (rather than react-router's navigate()) guarantees
    // every bit of in-memory state tied to the old identity (query cache
    // keyed by learnerId, etc.) gets reset cleanly, which isn't reliably
    // true when called from a plain fetch wrapper outside of React.
    clearToken()
    if (typeof window !== 'undefined' && window.location.pathname !== '/login') {
      window.location.assign('/login')
    }
  }

  if (!res.ok) {
    let code = 'unknown_error'
    let message = `Request failed with status ${res.status}`
    try {
      const body: ErrorEnvelope = await res.json()
      if (body.error) {
        code = body.error.code
        message = body.error.message
      } else if (body.detail) {
        if (typeof body.detail === 'string') {
          message = body.detail
        } else {
          code = body.detail.code
          message = body.detail.message
        }
      }
    } catch {
      // response body wasn't JSON — keep the generic message
    }
    throw new ApiError(res.status, code, message)
  }

  if (res.status === 204) {
    return undefined as T
  }
  return (await res.json()) as T
}

export const apiClient = {
  get: <T>(path: string) => request<T>(path, { method: 'GET' }),
  post: <T>(path: string, body?: unknown) =>
    request<T>(path, { method: 'POST', body: body === undefined ? undefined : JSON.stringify(body) }),
  patch: <T>(path: string, body?: unknown) =>
    request<T>(path, { method: 'PATCH', body: body === undefined ? undefined : JSON.stringify(body) }),
}
