/** The API accepts sessions only when they end after they start on the same day. */
export function hasValidTimeRange(start: string, end: string): boolean {
  return /^([01]\d|2[0-3]):[0-5]\d$/.test(start)
    && /^([01]\d|2[0-3]):[0-5]\d$/.test(end)
    && end > start
}
