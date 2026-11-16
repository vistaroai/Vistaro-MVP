import { Link, useLocation, useSearchParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'

import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
import { FullPageSpinner } from '@/components/Loading'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { getVerify } from '@/features/auth/api'

/**
 * Email verification outcome screen. The API deliberately answers the same
 * generic envelope for all failures (garbage, expired, reused link), and the
 * UI mirrors that: one neutral invalid state, no hints about what went
 * wrong. Without a token, it renders the plain "check your inbox" card that
 * signup navigates to.
 *
 * The verification call runs through TanStack Query on purpose: React
 * StrictMode double-invokes effects in dev, and a plain useEffect fired the
 * one-time token request twice — the first call consumed it, the second
 * failed and overwrote the screen with "invalid". The query cache
 * deduplicates the double mount into a single request (WARN recorded in
 * CLAUDE.md §12, caught by the E2E run).
 */
export function VerifyEmailRoute() {
  const location = useLocation()
  const [searchParams] = useSearchParams()
  const email =
    (location.state as { email?: string } | null)?.email ?? 'your email address'
  const token = searchParams.get('token')

  const verify = useQuery({
    queryKey: ['verify-email', token],
    queryFn: () => getVerify(token as string),
    enabled: token !== null,
    retry: false,
    staleTime: Infinity,
  })

  const kind =
    token === null
      ? 'inbox'
      : verify.isPending
        ? 'verifying'
        : verify.isError
          ? 'invalid'
          : 'verified'

  return (
    <main className="flex min-h-screen flex-col items-center justify-center px-6 py-16">
      <p className="text-sm font-medium uppercase tracking-[0.3em] text-sky-400">Vistaro</p>
      <div className="mt-6 w-full max-w-md">
        {kind === 'verifying' ? (
          <FullPageSpinner label="Verifying your email…" />
        ) : kind === 'verified' ? (
          <Card>
            <CardHeader>
              <CardTitle>Email verified</CardTitle>
            </CardHeader>
            <CardContent className="flex flex-col gap-4">
              <p className="text-sm text-slate-300">
                Your email address is confirmed. You can sign in and set up your workspace now.
              </p>
              <Button asChild>
                <Link to="/login">Continue to sign in</Link>
              </Button>
            </CardContent>
          </Card>
        ) : kind === 'invalid' ? (
          <Card>
            <CardHeader>
              <CardTitle>This link can’t be used</CardTitle>
            </CardHeader>
            <CardContent className="flex flex-col gap-4">
              <Alert>
                <AlertTitle>Verification failed</AlertTitle>
                <AlertDescription>
                  The verification link is invalid, expired, or was already used. Sign in to
                  request a fresh one.
                </AlertDescription>
              </Alert>
              <Button variant="outline" asChild>
                <Link to="/login">Back to sign in</Link>
              </Button>
            </CardContent>
          </Card>
        ) : (
          <Card>
            <CardHeader>
              <CardTitle>Check your inbox</CardTitle>
            </CardHeader>
            <CardContent className="flex flex-col gap-4">
              <p className="text-sm text-slate-300">
                We sent a verification link to <strong>{email}</strong>. Confirm your address
                to finish setting up your account.
              </p>
              <Button variant="outline" asChild>
                <Link to="/login">Back to sign in</Link>
              </Button>
            </CardContent>
          </Card>
        )}
      </div>
    </main>
  )
}
