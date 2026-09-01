import { NavLink } from 'react-router-dom'

import { useAuth } from '../../context/AuthContext'
import { ThemeToggle } from './ThemeToggle'
import { UserMenu } from './UserMenu'

const NAV_ITEMS = [
  { to: '/roadmap', label: 'Roadmap' },
  { to: '/courses', label: 'Courses' },
  { to: '/roles', label: 'Roles' },
  { to: '/chat', label: 'Chatbot' },
  { to: '/dashboard', label: 'Dashboard' },
  { to: '/settings', label: 'Settings' },
]

function navLinkClass({ isActive }: { isActive: boolean }) {
  return `rounded-md px-3 py-1.5 text-sm font-medium transition ${
    isActive ? 'bg-navy text-white' : 'text-fg-muted hover:text-fg'
  }`
}

export function Logo() {
  return (
    <span className="flex items-center gap-2 text-lg font-semibold">
      <span className="flex h-7 w-7 items-center justify-center rounded-md bg-navy text-white">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
          <path d="M4 4l16 8-16 8V4z" />
        </svg>
      </span>
      PathFinder
    </span>
  )
}

export function NavBar({ onOpenMobileNav }: { onOpenMobileNav: () => void }) {
  const { user } = useAuth()

  return (
    <header className="sticky top-0 z-30 border-b border-border bg-bg/90 backdrop-blur">
      <div className="mx-auto flex h-16 max-w-6xl items-center justify-between px-4 sm:px-6">
        <NavLink to="/" className="shrink-0">
          <Logo />
        </NavLink>

        {user && (
          <nav className="hidden items-center gap-1 md:flex">
            {NAV_ITEMS.map((item) => (
              <NavLink key={item.to} to={item.to} className={navLinkClass}>
                {item.label}
              </NavLink>
            ))}
          </nav>
        )}

        <div className="flex items-center gap-2">
          <ThemeToggle />
          {user ? (
            <>
              <UserMenu />
              <button
                type="button"
                onClick={onOpenMobileNav}
                aria-label="Open navigation menu"
                className="flex h-9 w-9 items-center justify-center rounded-full border border-border md:hidden"
              >
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M4 6h16M4 12h16M4 18h16" />
                </svg>
              </button>
            </>
          ) : (
            <div className="flex items-center gap-2">
              <NavLink
                to="/login"
                className="rounded-full px-3.5 py-1.5 text-sm font-medium text-fg-muted hover:text-fg"
              >
                Log in
              </NavLink>
              <NavLink
                to="/signup"
                className="rounded-full bg-coral px-3.5 py-1.5 text-sm font-semibold text-white hover:bg-coral-dark"
              >
                Sign up
              </NavLink>
            </div>
          )}
        </div>
      </div>
    </header>
  )
}

export { NAV_ITEMS }
