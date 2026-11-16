import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'

const mockFetchMe = vi.fn()

vi.mock('@/features/auth/api', async (importOriginal) => ({
  ...(await importOriginal<typeof import('@/features/auth/api')>()),
  fetchMe: () => mockFetchMe(),
}))

import { RequireAuth } from './session'

function renderGuarded(ui: React.ReactNode, initialPath: string) {
  return render(
    <QueryClientProvider
      client={
        new QueryClient({ defaultOptions: { queries: { retry: false } } })
      }
    >
      <MemoryRouter initialEntries={[initialPath]}>
        <Routes>
          <Route path="/login" element={<div>login-screen</div>} />
          <Route path="/secure" element={<RequireAuth>{ui}</RequireAuth>} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>,
  )
}

const AUTHED_USER = { id: 'u-1', email: 'user@example.com', email_verified: true } as const

describe('RequireAuth', () => {
  it('renders children when a session exists', async () => {
    mockFetchMe.mockResolvedValue(AUTHED_USER)
    renderGuarded(<div>secure-content</div>, '/secure')
    expect(await screen.findByText('secure-content')).toBeInTheDocument()
  })

  it('redirects to /login when the session is missing', async () => {
    mockFetchMe.mockResolvedValue(null)
    renderGuarded(<div>secure-content</div>, '/secure')
    expect(await screen.findByText('login-screen')).toBeInTheDocument()
    expect(screen.queryByText('secure-content')).not.toBeInTheDocument()
  })

  it('shows the loading state while the session probe is in flight', () => {
    mockFetchMe.mockReturnValue(new Promise(() => undefined))
    renderGuarded(<div>secure-content</div>, '/secure')
    expect(screen.getByRole('status')).toBeInTheDocument()
    expect(screen.queryByText('secure-content')).not.toBeInTheDocument()
    expect(screen.queryByText('login-screen')).not.toBeInTheDocument()
  })
})
