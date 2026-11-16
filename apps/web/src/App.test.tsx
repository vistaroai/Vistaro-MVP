import { MemoryRouter } from 'react-router-dom'
import { render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'

// Session probe returns "signed out": the guarded home route must land on
// the sign-in screen. Only fetchMe is stubbed; flows that submit forms are
// tested in their feature files.
vi.mock('./features/auth/api', () => ({
  fetchMe: () => Promise.resolve(null),
}))

import App from './App'

describe('App', () => {
  it('renders the sign-in screen for a signed-out visitor', async () => {
    render(
      <MemoryRouter initialEntries={['/']}>
        <App />
      </MemoryRouter>,
    )

    expect(
      await screen.findByRole('heading', { name: /sign in to vistaro/i }),
    ).toBeInTheDocument()
  })
})
