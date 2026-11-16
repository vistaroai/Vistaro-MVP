import type { ReactNode } from 'react'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

/**
 * Shared frame for every unsigned-in screen: brand line, one card, and a
 * footer slot for the cross-link ("No account? Sign up"). Keeps the three
 * auth routes visually and semantically identical.
 */
export function AuthCard({
  title,
  children,
  footer,
}: {
  title: string
  children: ReactNode
  footer?: ReactNode
}) {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center px-6 py-16">
      <p className="text-sm font-medium uppercase tracking-[0.3em] text-sky-400">Vistaro</p>
      <Card className="mt-6 w-full max-w-sm">
        <CardHeader>
          <CardTitle>{title}</CardTitle>
        </CardHeader>
        <CardContent className="flex flex-col gap-4">{children}</CardContent>
      </Card>
      {footer ? <div className="mt-4 text-sm text-slate-400">{footer}</div> : null}
    </main>
  )
}
