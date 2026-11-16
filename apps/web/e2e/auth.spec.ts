import { expect, test } from '@playwright/test'

/**
 * E2E smoke for the shell. Flows marked requireServices() are skipped unless
 * VISTARO_E2E=1 is set AND the full local stack is running (docker compose
 * + uvicorn). The redirect check below is safe to run anywhere: it only
 * needs the Vite server.
 */
function requireServices() {
  test.skip(process.env.VISTARO_E2E !== '1', 'Requires local API stack (VISTARO_E2E=1)')
}

test('signed-out visitor is redirected to the sign-in screen', async ({ page }) => {
  await page.goto('/')
  await expect(page.getByRole('heading', { name: /sign in to vistaro/i })).toBeVisible()
})

test('sign in with wrong credentials shows the API error', async ({ page }) => {
  requireServices()
  await page.goto('/login')
  await page.getByLabel('Email').fill('e2e-wrong@example.com')
  await page.getByLabel('Password').fill('wrong-password-99')
  await page.getByRole('button', { name: /sign in/i }).click()
  await expect(page.getByText('Sign-in failed')).toBeVisible()
})

test('signup, verify, login, create and switch workspace', async ({ page, request }) => {
  requireServices()
  const email = `e2e-${Date.now()}@example.com`
  const password = 'long-enough-password-1'

  // 1. Signup → lands on "check your inbox".
  await page.goto('/signup')
  await page.getByLabel('Email').fill(email)
  await page.getByLabel('Password').fill(password)
  await page.getByRole('button', { name: /create account/i }).click()
  await expect(page.getByRole('heading', { name: /check your inbox/i })).toBeVisible()

  // 2. Read the verification token from Mailpit and verify through the SPA.
  //    The email links to the API's JSON endpoint; the SPA route
  //    /verify-email?token=... performs the same one-time verification from
  //    the browser (documented gap: the email link should redirect into the
  //    SPA — recorded in CLAUDE.md §12 as a follow-up).
  const messages = await request.get('http://localhost:8025/api/v1/messages')
  const inbox = (await messages.json()) as {
    messages: Array<{ ID: string; To: Array<{ Address: string }> }>
  }
  const mail = inbox.messages.find((message) =>
    message.To.some((to) => to.Address === email),
  )
  expect(mail, 'verification email should exist in Mailpit').not.toBeNull()
  const detail = await request.get(`http://localhost:8025/api/v1/message/${mail!.ID}`)
  // Mailpit's v1 detail returns the full Text and HTML bodies. The token
  // charset is deliberately restricted to base64url characters: matching a
  // JSON-stringified body loosely used to swallow escaped `\n` sequences.
  const message = (await detail.json()) as { Text?: string; HTML?: string }
  const link =
    message.HTML?.match(/\/auth\/verify\?token=([A-Za-z0-9_-]+)/)?.[1] ??
    message.Text?.match(/\/auth\/verify\?token=([A-Za-z0-9_-]+)/)?.[1]
  expect(link, 'verification link should be in the email body').not.toBeNull()
  await page.goto(`/verify-email?token=${link!}`)

  await expect(page.getByRole('heading', { name: /email verified/i })).toBeVisible()

  // 3. Sign in.
  await page.getByRole('link', { name: /continue to sign in/i }).click()
  await page.getByLabel('Email').fill(email)
  await page.getByLabel('Password').fill(password)
  await page.getByRole('button', { name: /sign in/i }).click()

  // 4. Create a workspace from the header switcher.
  await expect(page.getByRole('heading', { name: /your workspaces/i })).toBeVisible()
  await page.getByRole('button', { name: /new workspace/i }).click()
  await page.getByLabel('New workspace name').fill('E2E Workspace')
  await page.getByRole('button', { name: /^create$/i }).click()

  // 5. The switcher carries the workspace with the owner role and the
  //    dashboard lists it. The switcher is asserted via toContainText: the
  //    selected <option> of a closed native <select> has no box, so Playwright
  //    treats it as hidden and toBeVisible would never pass.
  await expect(
    page.getByRole('combobox', { name: 'Active workspace' }),
  ).toContainText('E2E Workspace (owner)')
  await expect(
    page.locator('main').getByText('E2E Workspace', { exact: true }),
  ).toBeVisible()
})
