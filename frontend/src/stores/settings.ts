import { defineStore } from 'pinia'
import { api } from '../api'
import { t } from '../i18n'
import { browserLanguage as pageLanguageOf } from '../languages'
import type { PageLanguage, ReaderSettings, RefreshMinutes, Settings, Theme } from '../types'

// The language of the pages matching the browser's language, e.g. "ko-KR" -> Korean.
const browserLanguage = (): PageLanguage => pageLanguageOf(navigator.language)

const DEFAULT_READER: ReaderSettings = { theme: 'light', size: 20, lineHeight: 1.8, marginV: 80, marginH: 40, pages: 1, tutorialSeen: false }

const readerOf = (saved: Settings): ReaderSettings => ({
  theme: saved.reader_theme,
  size: saved.reader_size,
  lineHeight: saved.reader_line_height,
  marginV: saved.reader_margin_v,
  marginH: saved.reader_margin_h,
  pages: saved.reader_pages,
  tutorialSeen: saved.reader_tutorial_seen,
})

/** How the pages look and read. The backend keeps the choices. */
export const useSettingsStore = defineStore('settings', {
  state: () => ({
    // Until the saved choice is loaded, the pages are in the browser's language.
    language: browserLanguage(),
    theme: '' as Theme,
    // How an article is laid out for reading, as it is shown now.
    reader: { ...DEFAULT_READER },
    // The layout that is saved; `reader` differs from it while a choice is being tried.
    savedReader: { ...DEFAULT_READER },
    refreshMinutes: 30 as RefreshMinutes,
    error: null as string | null,
  }),
  actions: {
    /** Takes over what the backend has. */
    keep(saved: Settings) {
      if (saved.language) this.language = saved.language
      this.theme = saved.theme
      this.refreshMinutes = saved.refresh_minutes
      this.savedReader = readerOf(saved)
      this.reader = { ...this.savedReader }
    },
    async load() {
      try {
        const saved = await api<Settings>('/settings')
        this.keep(saved)
        // First visit: start from the browser's language; the reader can change it any time.
        if (!saved.language) await this.setLanguage(browserLanguage())
      } catch (e) {
        this.error = (e as Error).message
      }
    },
    /** Saves the choices with some of them changed; a choice that cannot be saved is not made. */
    async save(changed: { language?: PageLanguage; theme?: Theme; reader?: Partial<ReaderSettings>; refreshMinutes?: RefreshMinutes }) {
      this.error = null
      const reader = { ...this.savedReader, ...changed.reader }
      const next: Settings = {
        language: changed.language ?? this.language,
        theme: changed.theme ?? this.theme,
        reader_theme: reader.theme,
        reader_size: reader.size,
        reader_line_height: reader.lineHeight,
        reader_margin_v: reader.marginV,
        reader_margin_h: reader.marginH,
        reader_pages: reader.pages,
        reader_tutorial_seen: reader.tutorialSeen,
        refresh_minutes: changed.refreshMinutes ?? this.refreshMinutes,
      }
      try {
        this.keep(await api<Settings>('/settings', { method: 'PUT', json: next }))
      } catch (e) {
        this.reader = { ...this.savedReader }
        this.error = t('settings.saveFailed', { error: (e as Error).message })
      }
    },
    setLanguage(language: PageLanguage) {
      return this.save({ language })
    },
    setTheme(theme: Theme) {
      return this.save({ theme })
    },
    setRefreshMinutes(refreshMinutes: RefreshMinutes) {
      return this.save({ refreshMinutes })
    },
    /** Shows the article with a layout that is not saved yet, as while a slider is dragged. */
    previewReader(changed: Partial<ReaderSettings>) {
      Object.assign(this.reader, changed)
    },
    setReader(changed: Partial<ReaderSettings>) {
      return this.save({ reader: changed })
    },
  },
})
