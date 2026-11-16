import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { MemoryRouter } from 'react-router-dom'
import { render } from '@testing-library/react'
import { describe, it, vi } from 'vitest'

// Accessible-by-construction auth screens (playbook verification: automated
// accessibility check). axe runs on the rendered DOM; layout-only rules that
// need real browsers (contrast) are covered by later Playwright runs.
vi.mock('@/features/auth/api', async (importOriginal) => ({
  ...(await importOriginal<typeof import('@/features/auth/api')>()),
  fetchMe: () => Promise.resolve(null),
}))

import { expectNoAxeViolations } from '@/test/setup'
import { LoginRoute } from './LoginRoute'
import { SignupRoute } from './SignupRoute'
import { VerifyEmailRoute } from './VerifyEmailRoute'
import { AuthCard } from './AuthCard'

function mounted(ui: React.ReactNode) {
  return render(
    <QueryClientProvider
      client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}
    >
      <MemoryRouter>{ui}</MemoryRouter>
    </QueryClientProvider>,
  )
}

describe('accessibility (axe)', () => {
  it('login screen has no violations', async () => {
    const { container } = mounted(<LoginRoute />)
    await expectNoAxeViolations(container)
  })

  it('signup screen has no violations', async () => {
    const { container } = mounted(<SignupRoute />)
    await expectNoAxeViolations(container)
  })

  it('verify-email screen has no violations', async () => {
    const { container } = mounted(<VerifyEmailRoute />)
    await expectNoAxeViolations(container)
  })

  it('the shared auth card has no violations bare', async () => {
    const { container } = mounted(<AuthCard title="Empty card">Nothing to see</AuthCard>)
    await expectNoAxeViolations(container)
  })
})
