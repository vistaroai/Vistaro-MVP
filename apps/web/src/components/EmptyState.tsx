import type { ReactNode } from 'react'

interface EmptyStateProps {
  title: string
  description?: string
  action?: ReactNode
  icon?: ReactNode
}

/** Shared empty state so every screen answers "why is this blank?" (CLAUDE.md 4). */
export function EmptyState({ title, description, action, icon }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center gap-3 rounded-xl border border-dashed border-slate-800 bg-slate-900/40 p-10 text-center">
      {icon}
      <p className="text-sm font-medium text-slate-200">{title}</p>
      {description ? <p className="max-w-sm text-sm text-slate-400">{description}</p> : null}
      {action}
    </div>
  )
}
