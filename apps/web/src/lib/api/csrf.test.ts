import { describe, expect, it } from 'vitest'

import { CSRF_COOKIE_NAME, readCsrfCookie } from './csrf'

describe('readCsrfCookie', () => {
  it('returns the current csrf cookie value', () => {
    document.cookie = `${CSRF_COOKIE_NAME}=token-1`
    expect(readCsrfCookie()).toBe('token-1')
  })

  it('returns null when the cookie is absent', () => {
    document.cookie = `${CSRF_COOKIE_NAME}=;max-age=0`
    expect(readCsrfCookie()).toBeNull()
  })

  it('does not pick up unrelated cookies', () => {
    document.cookie = 'vistaro_session=session-token'
    document.cookie = `${CSRF_COOKIE_NAME}=pair-token`
    expect(readCsrfCookie()).toBe('pair-token')
  })
})
