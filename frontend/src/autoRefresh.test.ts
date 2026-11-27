import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { refreshEvery } from './autoRefresh'

beforeEach(() => vi.useFakeTimers())
afterEach(() => vi.useRealTimers())

const MINUTE = 60_000

describe('refreshing on a schedule', () => {
  it('refreshes at once, then once each interval', () => {
    const refresh = vi.fn()
    refreshEvery(30, refresh)
    expect(refresh).toHaveBeenCalledTimes(1)
    vi.advanceTimersByTime(29 * MINUTE)
    expect(refresh).toHaveBeenCalledTimes(1)
    vi.advanceTimersByTime(MINUTE)
    expect(refresh).toHaveBeenCalledTimes(2)
    vi.advanceTimersByTime(30 * MINUTE)
    expect(refresh).toHaveBeenCalledTimes(3)
  })

  it('can wait a whole interval before the first refresh', () => {
    const refresh = vi.fn()
    refreshEvery(15, refresh, { now: false })
    expect(refresh).not.toHaveBeenCalled()
    vi.advanceTimersByTime(15 * MINUTE)
    expect(refresh).toHaveBeenCalledTimes(1)
  })

  it('never refreshes when the interval is 0', () => {
    const refresh = vi.fn()
    refreshEvery(0, refresh)
    vi.advanceTimersByTime(24 * 60 * MINUTE)
    expect(refresh).not.toHaveBeenCalled()
  })

  it('stops when asked to', () => {
    const refresh = vi.fn()
    const stop = refreshEvery(15, refresh, { now: false })
    stop()
    vi.advanceTimersByTime(60 * MINUTE)
    expect(refresh).not.toHaveBeenCalled()
  })
})
