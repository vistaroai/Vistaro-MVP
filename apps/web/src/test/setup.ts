import '@testing-library/jest-dom/vitest'
import { expect } from 'vitest'
import { afterEach } from 'vitest'
import { cleanup } from '@testing-library/react'
import { axe } from 'jest-axe'

// Vitestinjects no global hooks (globals not enabled), so Testing Library's
// automatic cleanup never runs: without this, every rendered component from
// earlier tests stays mounted (duplicate button/labels everywhere).
afterEach(function cascadeCleanup() {
  cleanup()
})

// Accessibility helper for component tests: run axe on the rendered element
// and fail with a readable list of violation IDs. We avoid augmenting
// vitest's `Assertion` interface (it fights the generated typings, TS2428);
// an explicit helper keeps the typing honest and the diff small.
export async function expectNoAxeViolations(
  container: HTMLElement,
): Promise<void> {
  const results = await axe(container)
  const ids = results.violations.map((violation) => violation.id)
  expect(ids, `axe found violations: ${JSON.stringify(results.violations.map((v) => ({ id: v.id, impact: v.impact, nodes: v.nodes.length })))}`).toEqual(
    [],
  )
}
