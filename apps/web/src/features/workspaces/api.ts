import type { components } from '@/lib/api/schema.d.ts'
import { api } from '@/lib/api/client'
import { assertOk } from '@/lib/api/requests'

export type WorkspaceOut = components['schemas']['WorkspaceOut']
export type WorkspaceList = components['schemas']['WorkspaceList']

export async function fetchWorkspaces(): Promise<WorkspaceList> {
  return assertOk(await api.GET('/workspaces'))
}

export async function createWorkspace(body: { name: string }): Promise<WorkspaceOut> {
  return assertOk(await api.POST('/workspaces', { body }))
}

export async function switchWorkspace(workspaceId: string): Promise<WorkspaceOut> {
  return assertOk(
    await api.POST('/workspaces/{workspace_id}/switch', {
      params: { path: { workspace_id: workspaceId } },
    }),
  )
}
