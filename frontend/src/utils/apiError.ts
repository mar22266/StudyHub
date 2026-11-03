export class ApiError extends Error {
  constructor(public readonly status: number, public readonly data: unknown) {
    super(`HTTP ${status}`)
    this.name = 'ApiError'
  }
}

export function errorMessage(error: unknown): string {
  if (!(error instanceof ApiError)) return 'No fue posible completar la operación'

  const detail = (error.data as { detail?: unknown } | null)?.detail
  if (Array.isArray(detail)) {
    const message = detail.find(item => typeof item?.msg === 'string')?.msg
    if (message) return message.replace(/^Value error,\s*/i, '')
  }
  if (typeof detail === 'string') return detail
  return 'No fue posible completar la operación'
}
