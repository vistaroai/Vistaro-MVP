/**
 * Normalized request failure. Every thrown error across the app carries the
 * API envelope's code (e.g. `SESSION_EXPIRED`) so screens can branch on it,
 * plus a status for redirects. Never expose raw network details to users.
 */
export class RequestError extends Error {
  status: number
  code: string

  constructor(init: { status: number; code: string; message: string }) {
    super(init.message)
    this.name = 'RequestError'
    this.status = init.status
    this.code = init.code
  }
}

function parseEnvelope(status: number, body: unknown): RequestError {
  if (body !== null && typeof body === 'object' && 'error' in body) {
    const detail = (body as { error: Record<string, unknown> }).error
    return new RequestError({
      status,
      code: typeof detail.code === 'string' ? detail.code : 'UNKNOWN',
      message:
        typeof detail.message === 'string' ? detail.message : 'The request failed.',
    })
  }
  return new RequestError({ status, code: 'UNKNOWN', message: 'The request failed.' })
}

/**
 * openapi-fetch returns `{ data, error }` instead of throwing; this turns
 * that into react-query's throw convention (mutations set `isError` with the
 * RequestError as `error`). Assumption documented: when `data` is present it
 * is the success body; otherwise the declared error body is an envelope.
 */
export async function assertOk<T>(result: {
  data?: T
  error?: unknown
  response: Response
}): Promise<T> {
  if (result.data !== undefined) return result.data
  throw parseEnvelope(result.response.status, result.error)
}

/** User-facing text for any thrown value in screens and switchers. */
export function describeError(error: unknown): string {
  if (error instanceof RequestError) return error.message
  return 'Something went wrong. Please try again.'
}
