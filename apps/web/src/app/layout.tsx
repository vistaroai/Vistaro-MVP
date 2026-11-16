import { Outlet, useNavigate } from 'react-router-dom'

import { Button } from '@/components/ui/button'
import { ErrorBoundary } from '@/components/ErrorBoundary'
import { useLogout, useSession } from '@/lib/auth/session'
import { WorkspaceSwitcher } from '@/features/workspaces/WorkspaceSwitcher'

/**
 * Authenticated app shell: brand, workspace switcher, account, sign-out.
 * The session query is the single source of the signed-in identity here;
 * RequireAuth has already guaranteed it is loaded.
 */
export function AppLayout() {
  const { data: user } = useSession()
  const logout = useLogout()
  const navigate = useNavigate()

  return (
    <div className="flex min-h-screen flex-col bg-slate-950 text-slate-100">
      <header className="border-b border-slate-800 bg-slate-900/70">
        <div className="mx-auto flex w-full max-w-5xl flex-wrap items-center justify-between gap-3 px-6 py-3">
          <p className="text-sm font-semibold uppercase tracking-[0.3em] text-sky-400">
            Vistaro
          </p>
          <div className="flex flex-wrap items-center gap-3">
            <WorkspaceSwitcher />
            {user ? (
              <span className="text-sm text-slate-300">{user.email}</span>
            ) : (
              <span className="text-sm text-slate-500">Signed-out session</span>
            )}
            <Button
              size="sm"
              variant="outline"
              disabled={logout.isPending}
              onClick={() => {
                void logout.mutateAsync().then(() => navigate('/login', { replace: true }))
              }}
            >
              {logout.isPending ? 'Signing out…' : 'Sign out'}
            </Button>
          </div>
        </div>
      </header>
      <main className="mx-auto w-full max-w-5xl flex-1 px-6 py-10">
        <ErrorBoundary>
          <Outlet />
        </ErrorBoundary>
      </main>
      <footer className="border-t border-slate-800 px-6 py-4 text-center text-xs text-slate-500">
        Vistaro MVP — modules arrive in later tasks.
      </footer>
    </div>
  )
}
