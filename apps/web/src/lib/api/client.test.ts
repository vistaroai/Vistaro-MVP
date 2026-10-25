import { describe, expect, it } from 'vitest'
import { attachCsrfHeader, createApiClient } from './client'

describe('createApiClient', () => {
  it('initializes an openapi-fetch client with default options', () => {
    const client = createApiClient()
    expect(client).toBeDefined()
    expect(typeof client.GET).toBe('function')
  })

  it('accepts custom baseUrl options', () => {
    const client = createApiClient({ baseUrl: 'https://api.example.com' })
    expect(client).toBeDefined()
    expect(typeof client.GET).toBe('function')
  })

  it('attaches the CSRF token to unsafe requests', () => {
    const request = new Request('https://api.example.com/api/v1/items', { method: 'POST' })
    const result = attachCsrfHeader(request, () => 'csrf-value', 'https://api.example.com')
    expect(result.headers.get('X-CSRF-Token')).toBe('csrf-value')
  })

  it('does not add a CSRF token to safe requests', () => {
    const request = new Request('https://api.example.com/healthz', { method: 'GET' })
    const result = attachCsrfHeader(request, () => 'csrf-value', 'https://api.example.com')
    expect(result.headers.has('X-CSRF-Token')).toBe(false)
  })

  it('does not send CSRF tokens to a different origin', () => {
    const request = new Request('https://other.example/path', { method: 'POST' })
    const result = attachCsrfHeader(request, () => 'csrf-value', 'https://api.example.com')
    expect(result.headers.has('X-CSRF-Token')).toBe(false)
  })
})
