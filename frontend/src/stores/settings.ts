import { defineStore } from 'pinia'
import { loadLibrary } from '../storage'
import type { PageLanguage } from '../types'

/** How the pages look and read. */
export const useSettingsStore = defineStore('settings', {
  state: () => {
    const { language, theme, readerSize } = loadLibrary()
    return {
      language: language as PageLanguage,
      // A daisyUI theme name; empty follows the system.
      theme,
      // The size of an article's text, in pixels.
      readerSize: readerSize ?? 20,
    }
  },
})
