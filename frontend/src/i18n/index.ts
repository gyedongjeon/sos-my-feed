import { getActivePinia } from 'pinia'
import { useSettingsStore } from '../stores/settings'
import type { PageLanguage } from '../languages'
import en from './en'
import ko from './ko'
import ja from './ja'
import zhHans from './zh-Hans'
import zhHant from './zh-Hant'
import es from './es'
import fr from './fr'
import de from './de'
import it from './it'
import pt from './pt'
import pl from './pl'
import ru from './ru'
import uk from './uk'
import tr from './tr'
import vi from './vi'
import th from './th'
import id from './id'
import hi from './hi'
import bn from './bn'

/** A text of the pages, by its key in `en.ts`. */
export type MessageKey = keyof typeof en

// The languages the pages are written in, in the order of `LANGUAGES`. To add one, write a file
// like `ko.ts`, list it here, and add it to `LANGUAGES` in `languages.ts`.
const MESSAGES: Record<PageLanguage, Record<MessageKey, string>> = {
  en, ko, ja, 'zh-Hans': zhHans, 'zh-Hant': zhHant, es, fr, de, it, pt, pl, ru, uk, tr, vi, th, id, hi, bn,
}

/** The languages the pages are written in. */
export const PAGE_LANGUAGES = Object.keys(MESSAGES) as PageLanguage[]

// Read while a page is drawn, so the page is drawn again when the language changes.
// English where there is no store to ask (a function used on its own, as in a test).
const language = () => (getActivePinia() ? useSettingsStore().language : 'en')

/** A text of the pages in the chosen language, with `{name}` filled in from `values`. */
export function t(key: MessageKey, values: Record<string, string | number> = {}): string {
  const text = (MESSAGES[language()] ?? en)[key] ?? en[key]
  return text.replace(/\{(\w+)\}/g, (whole, name: string) => (name in values ? String(values[name]) : whole))
}
