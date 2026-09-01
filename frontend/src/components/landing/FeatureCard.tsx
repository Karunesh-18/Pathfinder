import type { ReactNode } from 'react'

export function FeatureCard({ icon, title, description }: { icon: ReactNode; title: string; description: string }) {
  return (
    <div className="rounded-2xl border border-border bg-bg-raised p-5 sm:p-6">
      <div className="mb-3 flex h-10 w-10 items-center justify-center rounded-full bg-navy/10 text-navy dark:text-navy-light">
        {icon}
      </div>
      <h3 className="mb-1 text-sm font-semibold">{title}</h3>
      <p className="text-sm text-fg-muted">{description}</p>
    </div>
  )
}
