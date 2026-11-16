import { defineConfig, devices } from '@playwright/test'

/**
 * E2E config (UI-001). Scripts and expectations:
 * - `pnpm test:e2e` runs the suite. `webServer` starts the Vite dev server
 *   automatically, and an already-running instance is reused.
 * - Specs that need the real API start with `requireServices` (see
 *   e2e/auth.spec.ts). For those, Postgres/Redis/Mailpit must be up
 *   (`docker compose -f infra/docker-compose.yml up -d`) and the API must be
 *   running (e.g. `uv run uvicorn vistaro.main:app --port 8000` from
 *   apps/api). Specs that don't need the API run everywhere.
 * - Browser binaries: run `pnpm exec playwright install chromium` once.
 */
export default defineConfig({
  testDir: './e2e',
  fullyParallel: false,
  retries: 0,
  use: {
    baseURL: 'http://localhost:5173',
    trace: 'on-first-retry',
  },
  projects: [{ name: 'chromium', use: { ...devices['Desktop Chrome'] } }],
  webServer: {
    command: 'pnpm dev',
    url: 'http://localhost:5173',
    reuseExistingServer: true,
    timeout: 30_000,
  },
})
