import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'

const mockPostLogin = vi.fn()

vi.mock('@/features/auth/api', () => ({
  postLogin: (body: { email: string; password: string }) => mockPostLogin(body),
}))

// Partial mock: client.ts still needs the real readCsrfCookie export.
vi.mock('@/lib/api/csrf', async (importOriginal) => ({
  ...(await importOriginal()),
  refreshCsrfToken: () => Promise.resolve(),
}))

import { RequestError } from '@/lib/api/requests'

import { LoginRoute } from './LoginRoute'

function renderLogin(initialEntries: string[] = ['/login']) {
  return render(
    <QueryClientProvider
      client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}
    >
      <MemoryRouter initialEntries={initialEntries}>
        <Routes>
          <Route path="/login" element={<LoginRoute />} />
          <Route path="/" element={<div>home-screen</div>} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>,
  )
}

function fillLoginForm(email: string, password: string) {
  fireEvent.input(screen.getByLabelText('Email'), { target: { value: email } })
  fireEvent.input(screen.getByLabelText('Password'), { target: { value: password } })
}

describe('LoginRoute', () => {
  it('blocks submission and shows validation messages when empty', async () => {
    renderLogin()
    fireEvent.click(screen.getByRole('button', { name: /sign in/i }))
    expect(await screen.findByText('Enter a valid email address')).toBeInTheDocument()
    expect(mockPostLogin).not.toHaveBeenCalled()
  })

  it('submits valid credentials and lands on home', async () => {
    mockPostLogin.mockResolvedValue({
      user: { id: 'u-1', email: 'user@example.com', email_verified: true },
      csrf_token: 'pair',
    })
    renderLogin()
    fillLoginForm('user@example.com', 'long-enough-password-1')
    fireEvent.click(screen.getByRole('button', { name: /sign in/i }))
    expect(await screen.findByText('home-screen')).toBeInTheDocument()
    expect(mockPostLogin).toHaveBeenCalledWith({
      email: 'user@example.com',
      password: 'long-enough-password-1',
    })
  })

  it('surfaces the API error for failed logins', async () => {
    mockPostLogin.mockRejectedValue(
      new RequestError({ status: 401, code: 'auth_invalid_credentials', message: 'Wrong email or password.' }),
    )
    renderLogin()
    fillLoginForm('user@example.com', 'short-password')
    fireEvent.click(screen.getByRole('button', { name: /sign in/i }))
    await waitFor(() => {
      expect(screen.getByText('Sign-in failed')).toBeInTheDocument()
    })
    expect(screen.getByText('Wrong email or password.')).toBeInTheDocument()
  })
})
