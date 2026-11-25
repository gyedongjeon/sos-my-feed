import { defineStore } from 'pinia'
import { api } from '../api'
import { t } from '../i18n'
import type { PageLanguage, Settings, Theme } from '../types'

// The language of the pages matching the browser's language, e.g. "ko-KR" -> Korean.
const browserLanguage = (): PageLanguage => (navigator.language.toLowerCase().startsWith('ko') ? 'ko' : 'en')

/** How the pages look and read. The backend keeps the choices. */
export const useSettingsStore = defineStore('settings', {
  state: () => ({
    // Until the saved choice is loaded, the pages are in the browser's language.
    language: browserLanguage(),
    theme: '' as Theme,
    // The size of an article's text, in pixels.
    readerSize: 20,
    error: null as string | null,
  }),
  actions: {
    async load() {
      try {
        const saved = await api<Settings>('/settings')
        this.theme = saved.theme
        this.readerSize = saved.reader_size
        if (saved.language) this.language = saved.language
        // First visit: start from the browser's language; the reader can change it any time.
        else await this.setLanguage(browserLanguage())
      } catch (e) {
        this.error = (e as Error).message
      }
    },
    /** Saves the choices with some of them changed; a choice that cannot be saved is not made. */
    async save(changed: Partial<Settings>) {
      this.error = null
      const next: Settings = { language: this.language, theme: this.theme, reader_size: this.readerSize, ...changed }
      try {
        const saved = await api<Settings>('/settings', { method: 'PUT', json: next })
        if (saved.language) this.language = saved.language
        this.theme = saved.theme
        this.readerSize = saved.reader_size
      } catch (e) {
        this.error = t('settings.saveFailed', { error: (e as Error).message })
      }
    },
    setLanguage(language: PageLanguage) {
      return this.save({ language })
    },
    setTheme(theme: Theme) {
      return this.save({ theme })
    },
    setReaderSize(size: number) {
      return this.save({ reader_size: size })
    },
  },
})
