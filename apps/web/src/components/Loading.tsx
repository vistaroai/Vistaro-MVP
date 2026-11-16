import { Loader2 } from 'lucide-react'

import { cn } from '@/lib/utils'

/** Accessible loading indicator: screen readers get the status text. */
export function FullPageSpinner({ label = 'Loading…' }: { label?: string }) {
  return (
    <div
      role="status"
      className="flex min-h-[50vh] flex-col items-center justify-center gap-3 text-slate-400"
    >
      <Loader2 aria-hidden className="size-6 animate-spin" />
      <span className="text-sm">{label}</span>
    </div>
  )
}

/** Inline, quieter variant for panels. */
export function InlineSpinner({ className }: { className?: string }) {
  return (
    <span role="status" className={cn('inline-flex', className)}>
      <Loader2 aria-hidden className="size-4 animate-spin" />
      <span className="sr-only">Loading…</span>
    </span>
  )
}
