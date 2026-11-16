import type { ApiClient } from './client'

/** Same value as the API's `CSRF_COOKIE_NAME` (core/security.py). */
export const CSRF_COOKIE_NAME = 'csrf_token'

/**
 * Read the double-submit CSRF cookie at call time instead of caching it:
 * every auth state change (signup, login, logout, re-binding GET /csrf)
 * rewrites the cookie, so the freshest value is always the correct pair
 * partner for the next unsafe request's X-CSRF-Token header.
 */
export function readCsrfCookie(): string | null {
  const match = document.cookie.match(/(?:^|; )csrf_token=([^;]*)/)
  if (!match || match[1] === undefined) return null
  return decodeURIComponent(match[1])
}

/**
 * The API re-binds CSRF tokens on each GET /csrf: when the client's cookie
 * could be stale relative to the session (long-idle tab, a re-login in
 * another tab), fetching /csrf first re-sets the pairing cookie, so the
 * subsequent unsafe request passes both the double-submit and the
 * session-bound check. Call this immediately before unsafe calls that
 * accept a possibly-stale pairing (login, signup).
 */
export async function refreshCsrfToken(client: ApiClient): Promise<void> {
  await client.GET('/csrf')
}
