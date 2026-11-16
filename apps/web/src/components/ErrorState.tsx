import { AlertTriangle } from 'lucide-react'
import type { ReactNode } from 'react'

import { Button } from '@/components/ui/button'

interface ErrorStateProps {
  title?: string
  description?: ReactNode
  onRetry?: () => void
}

/**
 * Shared error surface for query failures. Retrying must be explicit —
 * nothing retries silently, so a broken request never looks like loading.
 */
export function ErrorState({
  title = 'Something went wrong',
  description,
  onRetry,
}: ErrorStateProps) {
  return (
    <div
      role="alert"
      className="flex flex-col items-center gap-3 rounded-xl border border-red-900/50 bg-red-950/30 p-10 text-center"
    >
      <AlertTriangle aria-hidden className="size-5 text-red-400" />
      <p className="text-sm font-medium text-red-200">{title}</p>
      {description ? <p className="max-w-sm text-sm text-red-300/80">{description}</p> : null}
      {onRetry ? (
        <Button variant="outline" size="sm" onClick={onRetry}>
          Try again
        </Button>
      ) : null}
    </div>
  )
}
