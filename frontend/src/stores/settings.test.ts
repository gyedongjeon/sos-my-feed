import { createPinia, setActivePinia } from 'pinia'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { useSettingsStore } from './settings'

const NOTHING_CHOSEN = { language: null, theme: '', reader_size: 20 }

// A tiny backend: remembers the settings like the real `/api/settings`.
function fakeBackend(saved: Record<string, unknown>, browserLanguage: string, failSaving = false) {
  const state = { saved, puts: 0 }
  vi.stubGlobal('navigator', { language: browserLanguage })
  vi.stubGlobal('fetch', async (_url: string, init?: RequestInit) => {
    if (init?.method === 'PUT') {
      state.puts++
      if (failSaving) return new Response(JSON.stringify({ detail: 'disk full' }), { status: 500 })
      state.saved = JSON.parse(init.body as string)
    }
    return new Response(JSON.stringify(state.saved), { status: 200 })
  })
  return state
}

beforeEach(() => setActivePinia(createPinia()))
afterEach(() => vi.unstubAllGlobals())

describe('settings', () => {
  it('use what was saved and leave it alone', async () => {
    const backend = fakeBackend({ language: 'en', theme: 'sos-night', reader_size: 24 }, 'ko-KR')
    const store = useSettingsStore()
    await store.load()
    expect(store.language).toBe('en')
    expect(store.theme).toBe('sos-night')
    expect(store.readerSize).toBe(24)
    expect(backend.puts).toBe(0)
  })

  it.each([
    ['ko-KR', 'ko'],
    ['en-US', 'en'],
    ['sv-SE', 'en'],
  ])('start from the browser language on the first visit: %s -> %s', async (browser, expected) => {
    const backend = fakeBackend(NOTHING_CHOSEN, browser)
    const store = useSettingsStore()
    expect(store.language).toBe(expected)
    await store.load()
    expect(store.language).toBe(expected)
    expect(backend.saved).toEqual({ language: expected, theme: '', reader_size: 20 })
  })

  it('save one choice together with the others', async () => {
    const backend = fakeBackend({ language: 'ko', theme: 'sos', reader_size: 22 }, 'ko-KR')
    const store = useSettingsStore()
    await store.load()
    await store.setReaderSize(26)
    expect(store.readerSize).toBe(26)
    expect(backend.saved).toEqual({ language: 'ko', theme: 'sos', reader_size: 26 })
    await store.setTheme('')
    expect(backend.saved).toEqual({ language: 'ko', theme: '', reader_size: 26 })
  })

  it('keep the previous choice and report an error when saving fails', async () => {
    fakeBackend({ language: 'ko', theme: '', reader_size: 20 }, 'ko-KR', true)
    const store = useSettingsStore()
    await store.load()
    await store.setLanguage('en')
    expect(store.language).toBe('ko')
    // Said in the reader's language, which is Korean here.
    expect(store.error).toBe('설정을 저장하지 못했습니다: disk full')
  })
})
