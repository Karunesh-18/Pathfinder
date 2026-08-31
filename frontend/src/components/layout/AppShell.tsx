import { useState } from 'react'
import type { ReactNode } from 'react'

import { AssistantDrawer } from '../assistant/AssistantDrawer'
import { MobileNavDrawer } from './MobileNavDrawer'
import { NavBar } from './NavBar'

export function AppShell({ children }: { children: ReactNode }) {
  const [mobileNavOpen, setMobileNavOpen] = useState(false)

  return (
    <div className="min-h-svh bg-bg text-fg">
      <NavBar onOpenMobileNav={() => setMobileNavOpen(true)} />
      <MobileNavDrawer open={mobileNavOpen} onClose={() => setMobileNavOpen(false)} />
      <main className="mx-auto max-w-6xl px-4 py-6 sm:px-6 sm:py-8">{children}</main>
      <AssistantDrawer />
    </div>
  )
}
