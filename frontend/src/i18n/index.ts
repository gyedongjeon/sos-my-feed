import { getActivePinia } from 'pinia'
import { useSettingsStore } from '../stores/settings'
import type { PageLanguage } from '../types'
import en from './en'
import ko from './ko'

/** A text of the pages, by its key in `en.ts`. */
export type MessageKey = keyof typeof en

// The languages the pages are written in. To add one, write a file like `ko.ts`, list it here,
// and add it to `PageLanguage`.
const MESSAGES: Record<PageLanguage, Record<MessageKey, string>> = { en, ko }

/** The languages the pages are written in. */
export const PAGE_LANGUAGES = Object.keys(MESSAGES) as PageLanguage[]

// Read while a page is drawn, so the page is drawn again when the language changes.
// English where there is no store to ask (a function used on its own, as in a test).
const language = () => (getActivePinia() ? useSettingsStore().language : 'en')

/** A text of the pages in the chosen language. */
export function t(key: MessageKey): string {
  return (MESSAGES[language()] ?? en)[key] ?? en[key]
}
