import createFetchClient, { type Client } from 'openapi-fetch'
import type { paths } from './schema.d.ts'

export type ApiClient = Client<paths>

export interface CreateApiClientOptions {
  baseUrl?: string
  getCsrfToken?: () => string | null
}

export function attachCsrfHeader(
  request: Request,
  getToken: () => string | null,
  trustedOrigin?: string,
): Request {
  if (['GET', 'HEAD', 'OPTIONS'].includes(request.method.toUpperCase())) return request
  if (!trustedOrigin || new URL(request.url).origin !== trustedOrigin) return request
  const token = getToken()
  if (token) request.headers.set('X-CSRF-Token', token)
  return request
}

function resolveTrustedOrigin(baseUrl: string, browserOrigin?: string): string | undefined {
  try {
    return new URL(baseUrl || browserOrigin || '', browserOrigin).origin
  } catch {
    return undefined
  }
}

/**
 * Create a typed API client backed by openapi-fetch.
 * Includes credentials by default and forwards CSRF / request tracing headers.
 */
export function createApiClient(options: CreateApiClientOptions = {}): ApiClient {
  const baseUrl = options.baseUrl ?? ''
  const browserOrigin = typeof window === 'undefined' ? undefined : window.location.origin
  const trustedOrigin = resolveTrustedOrigin(baseUrl, browserOrigin)

  const client = createFetchClient<paths>({
    baseUrl,
    credentials: 'include',
  })

  client.use({
    onRequest: ({ request }) =>
      attachCsrfHeader(request, options.getCsrfToken ?? (() => null), trustedOrigin),
  })

  return client
}

export const api = createApiClient()
