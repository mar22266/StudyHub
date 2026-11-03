import { ApiError } from '../utils/apiError'

type ApiResult<T> = { data: T }

async function request<T>(method: string, path: string, body?: unknown): Promise<ApiResult<T>> {
  const headers = new Headers()
  const token = localStorage.getItem('studyhub_token')
  if (token) headers.set('Authorization', `Bearer ${token}`)
  if (body !== undefined) headers.set('Content-Type', 'application/json')

  const response = await fetch(`/api${path}`, {
    method,
    headers,
    body: body === undefined ? undefined : JSON.stringify(body),
    redirect: 'error',
  })
  const text = response.status === 204 ? '' : await response.text()
  let data: unknown = undefined
  if (text) {
    try { data = JSON.parse(text) } catch { data = text }
  }
  if (!response.ok) throw new ApiError(response.status, data)
  return { data: data as T }
}

const api = {
  get: <T = unknown>(path: string) => request<T>('GET', path),
  post: <T = unknown>(path: string, body?: unknown) => request<T>('POST', path, body),
  put: <T = unknown>(path: string, body?: unknown) => request<T>('PUT', path, body),
  delete: <T = unknown>(path: string) => request<T>('DELETE', path),
}

export default api
export {errorMessage} from '../utils/apiError'
