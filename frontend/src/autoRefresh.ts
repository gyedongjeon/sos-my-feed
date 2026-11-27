/** Calls `refresh` every `minutes` (at once too, unless `now` is false); 0 never calls it.
 * Returns a function that stops it. */
export function refreshEvery(minutes: number, refresh: () => void, { now = true } = {}): () => void {
  if (minutes <= 0) return () => {}
  if (now) refresh()
  const timer = setInterval(refresh, minutes * 60_000)
  return () => clearInterval(timer)
}
