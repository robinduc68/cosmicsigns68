import { ApiError, type ApiEnvelope } from '@cosmic/shared'

/**
 * The single door to the backend.
 *
 * Every call goes through here so error shape, base URL and request ids are
 * handled once — components never touch `$fetch` directly.
 */
export function useApi() {
  const config = useRuntimeConfig()

  const baseURL = import.meta.server
    ? config.apiBaseInternal || config.public.apiBase
    : config.public.apiBase

  async function request<T>(
    path: string,
    options: {
      method?: 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE'
      body?: unknown
      headers?: Record<string, string>
    } = {},
  ): Promise<T> {
    try {
      const envelope = await $fetch<ApiEnvelope<T>>(path, {
        baseURL,
        method: options.method ?? 'GET',
        body: options.body as Record<string, unknown> | undefined,
        headers: options.headers,
      })

      if (envelope.error) {
        throw new ApiError(envelope.error, 200)
      }
      return envelope.data as T
    } catch (caught: unknown) {
      if (caught instanceof ApiError) throw caught

      const failure = caught as {
        status?: number
        data?: ApiEnvelope<unknown>
        response?: { headers?: Headers }
      }
      const body = failure.data?.error
      const requestId = failure.response?.headers?.get?.('x-request-id') ?? undefined

      if (body) {
        throw new ApiError(body, failure.status ?? 500, requestId)
      }

      // Network failure, CORS, backend down — never surface the raw cause.
      throw new ApiError(
        {
          code: 'NETWORK_ERROR',
          message: 'Không kết nối được tới máy chủ. Bạn kiểm tra mạng và thử lại nhé.',
          details: {},
        },
        0,
        requestId,
      )
    }
  }

  return { request, baseURL }
}
