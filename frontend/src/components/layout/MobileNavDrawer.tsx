import { NavLink } from 'react-router-dom'

import { NAV_ITEMS } from './NavBar'

export function MobileNavDrawer({ open, onClose }: { open: boolean; onClose: () => void }) {
  if (!open) return null

  return (
    <div className="fixed inset-0 z-40 md:hidden">
      <button
        aria-label="Close navigation menu"
        className="absolute inset-0 bg-black/40"
        onClick={onClose}
      />
      <nav className="absolute inset-y-0 right-0 flex w-72 max-w-[85vw] flex-col gap-1 bg-bg-raised p-4 shadow-xl">
        <div className="mb-2 flex items-center justify-between">
          <span className="text-sm font-semibold text-fg-muted">Menu</span>
          <button
            type="button"
            onClick={onClose}
            aria-label="Close"
            className="flex h-8 w-8 items-center justify-center rounded-full border border-border"
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M6 6l12 12M18 6L6 18" />
            </svg>
          </button>
        </div>
        {NAV_ITEMS.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            onClick={onClose}
            className={({ isActive }) =>
              `rounded-md px-3 py-2.5 text-sm font-medium ${
                isActive ? 'bg-navy text-white' : 'text-fg-muted hover:bg-border/50 hover:text-fg'
              }`
            }
          >
            {item.label}
          </NavLink>
        ))}
      </nav>
    </div>
  )
}
