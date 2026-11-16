import tailwindcss from '@tailwindcss/vite'
import react from '@vitejs/plugin-react'
import path from 'node:path'
import { defineConfig } from 'vitest/config'

const API_ORIGIN = 'http://127.0.0.1:8000'

export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: {
    alias: {
      '@': path.resolve(import.meta.dirname, './src'),
    },
  },
  server: {
    port: 5173,
    // Dev-only same-origin proxy for the API. The session/CSRF cookies belong
    // to the web origin, so the browser must talk to the SPA's own origin;
    // localhost:5173 -> 127.0.0.1:8000 would be a cross-site fetch and
    // SameSite cookies would never ride along. Redirect/cookie behavior is
    // unchanged (the proxy it not visible to the app code, which keeps using
    // relative paths). Staging/proxy decisions for hosted origins (pages.dev
    // -> onrender.com) land with INFRA-001/DEPLOY-001.
    proxy: {
      '/csrf': API_ORIGIN,
      '/auth': API_ORIGIN,
      '/workspaces': API_ORIGIN,
      '/healthz': API_ORIGIN,
    },
  },
  test: {
    environment: 'jsdom',
    setupFiles: ['./src/test/setup.ts'],
  },
})
