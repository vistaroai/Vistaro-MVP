import type { components } from '@/lib/api/schema.d.ts'
import { api } from '@/lib/api/client'
import { assertOk } from '@/lib/api/requests'

export type MeUser = components['schemas']['UserOut']
export type AuthResponse = components['schemas']['AuthResponse']

/**
 * Session probe. A 401 is an ordinary signed-out state, not an error, so it
 * resolves to `null` instead of throwing — screens can branch on it without
 * error UI flicker.
 */
export async function fetchMe(): Promise<MeUser | null> {
  const result = await api.GET('/auth/me')
  if (result.response.status === 401) return null
  return assertOk(result)
}

export async function postSignup(body: { email: string; password: string }) {
  return assertOk(await api.POST('/auth/signup', { body }))
}

export async function postLogin(body: { email: string; password: string }) {
  return assertOk(await api.POST('/auth/login', { body }))
}

export async function postLogout(): Promise<void> {
  await assertOk(await api.POST('/auth/logout'))
}

/** Visit-page verification: the API answers one generic envelope on any failure. */
export async function getVerify(token: string) {
  return assertOk(await api.GET('/auth/verify', { params: { query: { token } } }))
}
