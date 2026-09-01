import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

import { useAuth } from '../../context/AuthContext'

export function UserMenu() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const [open, setOpen] = useState(false)

  if (!user) return null

  const label = user.display_name || user.email

  function handleLogout() {
    setOpen(false)
    logout()
    navigate('/')
  }

  return (
    <div className="relative">
      <button
        type="button"
        onClick={() => setOpen((o) => !o)}
        className="flex h-9 items-center gap-2 rounded-full border border-border px-3 text-sm font-medium hover:bg-bg-raised"
      >
        <span className="flex h-6 w-6 items-center justify-center rounded-full bg-navy text-xs font-semibold text-white">
          {label.charAt(0).toUpperCase()}
        </span>
        <span className="hidden max-w-[8rem] truncate sm:inline">{label}</span>
      </button>

      {open && (
        <>
          <button
            aria-label="Close menu"
            className="fixed inset-0 z-30 cursor-default"
            onClick={() => setOpen(false)}
          />
          <div className="absolute right-0 z-40 mt-2 w-48 overflow-hidden rounded-xl border border-border bg-bg-raised shadow-lg">
            <div className="border-b border-border px-3.5 py-2.5 text-xs text-fg-muted">{user.email}</div>
            <button
              type="button"
              onClick={handleLogout}
              className="block w-full px-3.5 py-2.5 text-left text-sm font-medium text-danger hover:bg-danger/10"
            >
              Log out
            </button>
          </div>
        </>
      )}
    </div>
  )
}
