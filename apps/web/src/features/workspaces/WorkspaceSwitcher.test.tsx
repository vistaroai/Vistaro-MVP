import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'

const mockFetchWorkspaces = vi.fn()
const mockCreateWorkspace = vi.fn()
const mockSwitchWorkspace = vi.fn()

vi.mock('@/features/workspaces/api', () => ({
  fetchWorkspaces: () => mockFetchWorkspaces(),
  createWorkspace: (body: { name: string }) => mockCreateWorkspace(body),
  switchWorkspace: (id: string) => mockSwitchWorkspace(id),
}))

import { RequestError } from '@/lib/api/requests'
import { WorkspaceSwitcher } from './WorkspaceSwitcher'

// Partial mock: client.ts still needs the real readCsrfCookie export.
vi.mock('@/lib/api/csrf', async (importOriginal) => ({
  ...(await importOriginal()),
  refreshCsrfToken: () => Promise.resolve(),
}))

const WORKSPACE_A = {
  id: 'ws-a',
  name: 'Alpha',
  role: 'owner',
  created_at: '2026-11-01T10:00:00Z',
} as const
const WORKSPACE_B = {
  id: 'ws-b',
  name: 'Beta',
  role: 'editor',
  created_at: '2026-11-02T10:00:00Z',
} as const

function renderSwitcher() {
  return render(
    <QueryClientProvider
      client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}
    >
      <WorkspaceSwitcher />
    </QueryClientProvider>,
  )
}

describe('WorkspaceSwitcher', () => {
  it('shows a loading state while workspaces are in flight', () => {
    mockFetchWorkspaces.mockReturnValue(new Promise(() => undefined))
    renderSwitcher()
    expect(screen.getByRole('combobox')).toBeDisabled()
    expect(screen.getByText('Loading…')).toBeInTheDocument()
  })

  it('lists workspaces with their roles', async () => {
    mockFetchWorkspaces.mockResolvedValue({ workspaces: [WORKSPACE_A, WORKSPACE_B] })
    renderSwitcher()
    // Wait on the option text, not the select element: the find resolves as
    // soon as data lands, so a plain getByRole would race the query.
    const option = await screen.findByText('Alpha (owner)')
    expect(option).toBeInTheDocument()
    expect(screen.getByRole('combobox')).toBeEnabled()
  })

  it('switches to the selected workspace', async () => {
    mockFetchWorkspaces.mockResolvedValue({ workspaces: [WORKSPACE_A, WORKSPACE_B] })
    mockSwitchWorkspace.mockResolvedValue(WORKSPACE_B)
    renderSwitcher()
    await screen.findByText('Beta (editor)')
    const select = screen.getByRole('combobox')
    fireEvent.change(select, { target: { value: 'ws-b' } })
    await waitFor(() => {
      expect(mockSwitchWorkspace).toHaveBeenCalledWith('ws-b')
    })
    expect(await screen.findByText('Switched to Beta')).toBeInTheDocument()
  })

  it('offers an error state with a retry button', async () => {
    mockFetchWorkspaces.mockRejectedValue(
      new RequestError({ status: 500, code: 'internal', message: 'Boom' }),
    )
    renderSwitcher()
    // The list query retries once with backoff before surfacing the error.
    expect(
      await screen.findByText('Couldn’t load workspaces.', {}, { timeout: 4000 }),
    ).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /try again/i })).toBeInTheDocument()
  })

  it('creates a workspace and switches into it', async () => {
    const created = {
      id: 'ws-c',
      name: 'Gamma',
      role: 'owner',
      created_at: '2026-11-02T11:00:00Z',
    } as const
    mockFetchWorkspaces.mockResolvedValue({ workspaces: [] })
    mockCreateWorkspace.mockResolvedValue(created)
    mockSwitchWorkspace.mockResolvedValue(created)
    renderSwitcher()
    fireEvent.click(await screen.findByRole('button', { name: /new workspace/i }))
    fireEvent.input(screen.getByLabelText('New workspace name'), { target: { value: 'Gamma' } })
    fireEvent.click(screen.getByRole('button', { name: /create$/i }))
    await waitFor(() => {
      expect(mockCreateWorkspace).toHaveBeenCalledWith({ name: 'Gamma' })
    })
    await waitFor(() => {
      expect(mockSwitchWorkspace).toHaveBeenCalledWith('ws-c')
    })
  })
})
