import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'

import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { InlineSpinner } from '@/components/Loading'
import { api } from '@/lib/api/client'
import { describeError } from '@/lib/api/requests'
import { refreshCsrfToken } from '@/lib/api/csrf'
import {
  createWorkspace,
  fetchWorkspaces,
  switchWorkspace,
} from '@/features/workspaces/api'

/**
 * Workspace picker for the app header. Native <select> (best
 * a11y-per-effort), plus an inline "new workspace" form. Creation also
 * switches into the new workspace immediately, mirroring the backend's
 * creator-is-owner rule.
 *
 * Note on "active": the server keeps the active workspace on the session row
 * but /auth/me does not expose it yet, so this control cannot show which
 * workspace is active after a reload; it switches on selection and the
 * invalidation refreshes every tenant-scoped screen. Exposing
 * active_workspace_id on /auth/me is a small follow-up API nicety, recorded
 * in CLAUDE.md §12.
 */
export function WorkspaceSwitcher() {
  const queryClient = useQueryClient()
  const [creating, setCreating] = useState(false)
  const [name, setName] = useState('')

  const list = useQuery({
    queryKey: ['workspaces'],
    queryFn: fetchWorkspaces,
    retry: 1,
  })

  const invalidateWorkspaceState = () => {
    void queryClient.invalidateQueries({ queryKey: ['workspaces'] })
    void queryClient.invalidateQueries({ queryKey: ['session'] })
  }

  const switchMutation = useMutation({
    mutationFn: async (workspaceId: string) => {
      await refreshCsrfToken(api)
      return switchWorkspace(workspaceId)
    },
    onSuccess: invalidateWorkspaceState,
  })

  const createMutation = useMutation({
    mutationFn: async (workspaceName: string) => {
      await refreshCsrfToken(api)
      const created = await createWorkspace({ name: workspaceName })
      await switchWorkspace(created.id)
      return created
    },
    onSuccess: () => {
      setCreating(false)
      setName('')
      invalidateWorkspaceState()
    },
  })

  if (list.isError) {
    return (
      <div className="flex items-center gap-2 text-sm text-red-300">
        <span>Couldn’t load workspaces.</span>
        <Button size="sm" variant="outline" onClick={() => void list.refetch()}>
          Try again
        </Button>
      </div>
    )
  }

  const workspaces = list.data?.workspaces ?? []
  const busy = switchMutation.isPending || createMutation.isPending

  return (
    <div className="flex items-center gap-2">
      {/* The select is uncontrolled on purpose: the server does not expose
          the session's active workspace yet, so the control only reflects
          what the user picked. See the docstring. */}
      {!list.isPending ? (
        <label className="sr-only" htmlFor="workspace-switcher">
          Active workspace
        </label>
      ) : null}
      <select
        id="workspace-switcher"
        aria-live="polite"
        className="h-9 rounded-md border border-slate-700 bg-slate-900 px-2 text-sm text-slate-100"
        disabled={list.isPending || busy || workspaces.length === 0}
        onChange={(event) => switchMutation.mutate(event.target.value)}
      >
        {list.isPending ? <option value="">Loading…</option> : null}
        {!list.isPending && workspaces.length === 0 ? (
          <option value="">No workspace yet</option>
        ) : null}
        {workspaces.map((workspace) => (
          <option key={workspace.id} value={workspace.id}>
            {workspace.name} ({workspace.role})
          </option>
        ))}
      </select>

      {busy ? <InlineSpinner /> : null}

      {creating ? (
        <form
          className="flex items-center gap-2"
          onSubmit={(event) => {
            event.preventDefault()
            if (name.trim().length > 0) void createMutation.mutateAsync(name.trim())
          }}
        >
          <Input
            aria-label="New workspace name"
            value={name}
            maxLength={120}
            onChange={(event) => setName(event.target.value)}
            className="h-9 w-40"
            placeholder="Workspace name"
            autoFocus
          />
          <Button size="sm" type="submit" disabled={name.trim().length === 0}>
            Create
          </Button>
          <Button
            size="sm"
            type="button"
            variant="ghost"
            onClick={() => setCreating(false)}
          >
            Cancel
          </Button>
        </form>
      ) : (
        <Button size="sm" variant="ghost" onClick={() => setCreating(true)}>
          New workspace
        </Button>
      )}

      {createMutation.isError ? (
        <span className="text-sm text-red-300">{describeError(createMutation.error)}</span>
      ) : null}
      {switchMutation.isSuccess ? (
        <span className="text-sm text-emerald-300" role="status">
          Switched to {switchMutation.data?.name}
        </span>
      ) : null}
    </div>
  )
}
