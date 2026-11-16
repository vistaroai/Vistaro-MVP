import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Navigate, useLocation } from 'react-router-dom'
import type { ReactNode } from 'react'

import { fetchMe, postLogout } from '@/features/auth/api'
import { FullPageSpinner } from '@/components/Loading'
import { api } from '@/lib/api/client'
import { refreshCsrfToken } from '@/lib/api/csrf'

const SESSION_KEY = ['session'] as const

export function useSession() {
  return useQuery({ queryKey: SESSION_KEY, queryFn: fetchMe, retry: false })
}

export function useLogout() {
  const queryClient = useQueryClient()
  return useMutation({
    // Same CSRF rule as login/signup: re-bind first, then call (csrf.ts).
    mutationFn: async () => {
      await refreshCsrfToken(api)
      return postLogout()
    },
    onSuccess: () => {
      // Drop every cached server state: nothing survives a sign-out.
      queryClient.clear()
    },
  })
}

/**
 * Guard for authenticated routes. Renders nothing of the target UI until /
 * unless the session resolves—avoids flashing protected content, and signed
 * out visitors land on /login (replacing history so "back" stays sane).
 */
export function RequireAuth({ children }: { children: ReactNode }) {
  const { data, isPending } = useSession()
  const location = useLocation()

  if (isPending) return <FullPageSpinner label="Checking your session…" />
  if (data === null || data === undefined) {
    return <Navigate to="/login" replace state={{ from: location.pathname }} />
  }
  return <>{children}</>
}
