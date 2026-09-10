/** The single response envelope every Cosmic Signs endpoint returns. */
export interface ApiEnvelope<T> {
  data: T | null
  meta: Record<string, unknown>
  error: ApiErrorBody | null
}

export interface ApiErrorBody {
  code: string
  message: string
  details: Record<string, unknown>
}

/** Error thrown by the API client so callers can branch on `code`. */
export class ApiError extends Error {
  readonly code: string
  readonly status: number
  readonly details: Record<string, unknown>
  readonly requestId?: string

  constructor(body: ApiErrorBody, status: number, requestId?: string) {
    super(body.message)
    this.name = 'ApiError'
    this.code = body.code
    this.status = status
    this.details = body.details ?? {}
    this.requestId = requestId
  }

  /** Field-level messages produced by request validation, if any. */
  get fieldErrors(): Record<string, string> {
    const fields = this.details.fields
    return typeof fields === 'object' && fields !== null ? (fields as Record<string, string>) : {}
  }
}
