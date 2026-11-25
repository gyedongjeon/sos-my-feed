import { createPinia, setActivePinia } from 'pinia'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import type { Settings } from '../types'
import { useSettingsStore } from './settings'

const NOTHING_CHOSEN: Settings = {
  language: null,
  theme: '',
  reader_theme: 'light',
  reader_size: 20,
  reader_line_height: 1.8,
  reader_margin_v: 80,
  reader_margin_h: 40,
  reader_pages: 1,
  reader_tutorial_seen: false,
}
const CHOSEN: Settings = {
  language: 'ko',
  theme: 'sos',
  reader_theme: 'sepia',
  reader_size: 22,
  reader_line_height: 1.5,
  reader_margin_v: 60,
  reader_margin_h: 30,
  reader_pages: 2,
  reader_tutorial_seen: true,
}

// A tiny backend: remembers the settings like the real `/api/settings`.
function fakeBackend(saved: Settings, browserLanguage: string, failSaving = false) {
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
    const backend = fakeBackend({ ...CHOSEN, language: 'en', theme: 'sos-night' }, 'ko-KR')
    const store = useSettingsStore()
    await store.load()
    expect(store.language).toBe('en')
    expect(store.theme).toBe('sos-night')
    expect(store.reader).toEqual({ theme: 'sepia', size: 22, lineHeight: 1.5, marginV: 60, marginH: 30, pages: 2, tutorialSeen: true })
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
    expect(backend.saved).toEqual({ ...NOTHING_CHOSEN, language: expected })
  })

  it('save one choice together with the others', async () => {
    const backend = fakeBackend(CHOSEN, 'ko-KR')
    const store = useSettingsStore()
    await store.load()
    await store.setReader({ size: 26, pages: 1 })
    expect(store.reader.size).toBe(26)
    expect(backend.saved).toEqual({ ...CHOSEN, reader_size: 26, reader_pages: 1 })
    await store.setTheme('')
    expect(backend.saved).toEqual({ ...CHOSEN, reader_size: 26, reader_pages: 1, theme: '' })
  })

  it('keep the previous choice and report an error when saving fails', async () => {
    fakeBackend({ ...CHOSEN, theme: '' }, 'ko-KR', true)
    const store = useSettingsStore()
    await store.load()
    await store.setLanguage('en')
    expect(store.language).toBe('ko')
    // Said in the reader's language, which is Korean here.
    expect(store.error).toBe('설정을 저장하지 못했습니다: disk full')
  })
})

describe('the layout of the reader', () => {
  it('can be tried before it is saved', async () => {
    const backend = fakeBackend(CHOSEN, 'ko-KR')
    const store = useSettingsStore()
    await store.load()
    // A slider being dragged: the page follows, and nothing is saved until it is let go.
    store.previewReader({ size: 30 })
    expect(store.reader.size).toBe(30)
    expect(backend.puts).toBe(0)
    await store.setReader({ size: 30 })
    expect(backend.saved.reader_size).toBe(30)
  })

  it('goes back to what was saved when it cannot be saved', async () => {
    fakeBackend(CHOSEN, 'ko-KR', true)
    const store = useSettingsStore()
    await store.load()
    store.previewReader({ marginH: 80 })
    await store.setReader({ marginH: 80 })
    expect(store.reader.marginH).toBe(30)
    expect(store.error).toBe('설정을 저장하지 못했습니다: disk full')
  })
})
