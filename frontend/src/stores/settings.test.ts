import { createPinia, setActivePinia } from 'pinia'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { useSettingsStore } from './settings'

// A browser with the given language and saved library.
function browser(language: string, saved?: unknown) {
  vi.stubGlobal('navigator', { language })
  vi.stubGlobal('localStorage', { getItem: () => (saved === undefined ? null : JSON.stringify(saved)) })
}

beforeEach(() => setActivePinia(createPinia()))
afterEach(() => vi.unstubAllGlobals())

describe('settings', () => {
  it.each([
    ['ko-KR', 'ko'],
    ['en-US', 'en'],
    ['sv-SE', 'en'],
  ])('start from the browser language on the first visit: %s -> %s', (tag, expected) => {
    browser(tag)
    expect(useSettingsStore().language).toBe(expected)
  })

  it('use what was saved', () => {
    browser('ko-KR', { feeds: [], language: 'en', theme: 'sos-night', readerSize: 24 })
    const store = useSettingsStore()
    expect(store.language).toBe('en')
    expect(store.theme).toBe('sos-night')
    expect(store.readerSize).toBe(24)
  })

  it('read articles at 20px until another size is chosen', () => {
    browser('en-US', { feeds: [], language: 'en', theme: '' })
    expect(useSettingsStore().readerSize).toBe(20)
  })
})
