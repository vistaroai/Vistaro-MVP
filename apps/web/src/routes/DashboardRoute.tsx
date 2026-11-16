import { useQuery } from '@tanstack/react-query'

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { EmptyState } from '@/components/EmptyState'
import { ErrorState } from '@/components/ErrorState'
import { useSession } from '@/lib/auth/session'
import { fetchWorkspaces } from '@/features/workspaces/api'

/**
 * Placeholder workspace home (UI-001 scope). Real content arrives with the
 * feature tasks; this screen exercises the loading / empty / error pattern
 * that every later screen must follow (CLAUDE.md §4, dev guide rule 4).
 */
export function DashboardRoute() {
  const session = useSession()
  const workspaces = useQuery({ queryKey: ['workspaces'], queryFn: fetchWorkspaces })

  if (workspaces.isPending) {
    return <p className="text-sm text-slate-400">Loading workspaces…</p>
  }
  if (workspaces.isError) {
    return (
      <ErrorState
        title="Couldn’t load your workspaces"
        description="You can retry; nothing was changed."
        onRetry={() => void workspaces.refetch()}
      />
    )
  }
  const list = workspaces.data?.workspaces ?? []

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Your workspaces</h1>
        <p className="mt-1 text-sm text-slate-400">
          Signed in as {session.data?.email ?? 'unknown account'}.
        </p>
      </div>
      <Card>
        <CardHeader>
          <CardTitle>Workspaces</CardTitle>
          <CardDescription>
            Every workspace is isolated at the database level; roles and permissions arrive
            with AUTH-003.
          </CardDescription>
        </CardHeader>
        <CardContent>
          {list.length === 0 ? (
            <EmptyState
              title="No workspace yet"
              description="Use “New workspace” in the header to create your first one — you become its owner."
            />
          ) : (
            <ul className="flex flex-col gap-2">
              {list.map((workspace) => (
                <li
                  key={workspace.id}
                  className="flex items-center justify-between rounded-lg border border-slate-800 bg-slate-900/60 px-4 py-3"
                >
                  <span className="text-sm text-slate-100">{workspace.name}</span>
                  <span className="text-xs uppercase tracking-wide text-sky-300">
                    {workspace.role}
                  </span>
                </li>
              ))}
            </ul>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
