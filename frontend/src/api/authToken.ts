// Plain (non-React) localStorage accessors for the login JWT. Kept
// separate from context/AuthContext.tsx so api/client.ts can read the
// token without importing a React context module.

const TOKEN_KEY = 'pf_auth_token'

export function getToken(): string | null {
  try {
    return localStorage.getItem(TOKEN_KEY)
  } catch {
    return null
  }
}

export function setToken(token: string): void {
  try {
    localStorage.setItem(TOKEN_KEY, token)
  } catch {
    // localStorage unavailable (private mode, etc.) — session still works
    // for this page view, just won't persist across reloads.
  }
}

export function clearToken(): void {
  try {
    localStorage.removeItem(TOKEN_KEY)
  } catch {
    // ignore
  }
}
