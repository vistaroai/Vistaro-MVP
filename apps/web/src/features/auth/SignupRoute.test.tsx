import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { fireEvent, render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'

// Partial mock: client.ts still needs the real readCsrfCookie export.
vi.mock('@/lib/api/csrf', async (importOriginal) => ({
  ...(await importOriginal()),
  refreshCsrfToken: () => Promise.resolve(),
}))

const mockPostSignup = vi.fn()

vi.mock('@/features/auth/api', () => ({
  postSignup: (body: { email: string; password: string }) => mockPostSignup(body),
}))

import { SignupRoute } from './SignupRoute'
import { RequestError } from '@/lib/api/requests'

function renderSignup() {
  return render(
    <QueryClientProvider
      client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}
    >
      <MemoryRouter initialEntries={['/signup']}>
        <Routes>
          <Route path="/signup" element={<SignupRoute />} />
          <Route path="/verify-email" element={<div>verify-screen</div>} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>,
  )
}

function fillSignupForm(email: string, password: string) {
  fireEvent.input(screen.getByLabelText('Email'), { target: { value: email } })
  fireEvent.input(screen.getByLabelText('Password'), { target: { value: password } })
}

describe('SignupRoute', () => {
  it('enforces the API password rules before submitting', async () => {
    renderSignup()
    fillSignupForm('new-user@example.com', 'short')
    fireEvent.click(screen.getByRole('button', { name: /create account/i }))
    expect(await screen.findByText('Use at least 10 characters')).toBeInTheDocument()
    expect(mockPostSignup).not.toHaveBeenCalled()
  })

  it('creates the account and moves to the verify screen', async () => {
    mockPostSignup.mockResolvedValue({
      user: { id: 'u-2', email: 'new-user@example.com', email_verified: false },
      csrf_token: 'pair',
    })
    renderSignup()
    fillSignupForm('new-user@example.com', 'long-enough-password-1')
    fireEvent.click(screen.getByRole('button', { name: /create account/i }))
    expect(await screen.findByText('verify-screen')).toBeInTheDocument()
    expect(mockPostSignup).toHaveBeenCalledWith({
      email: 'new-user@example.com',
      password: 'long-enough-password-1',
    })
  })

  it('surfaces the API error for duplicate signups', async () => {
    mockPostSignup.mockRejectedValue(
      new RequestError({
        status: 409,
        code: 'AUTH_EMAIL_EXISTS',
        message: 'An account with that email already exists.',
      }),
    )
    renderSignup()
    fillSignupForm('user@example.com', 'long-enough-password-1')
    fireEvent.click(screen.getByRole('button', { name: /create account/i }))
    expect(await screen.findByText('Sign-up failed')).toBeInTheDocument()
    expect(
      screen.getByText('An account with that email already exists.'),
    ).toBeInTheDocument()
  })
})
