// The languages the pages are written in: those of the SOS series.

/** Each by its code, its own name, and the browser language tags it stands for. */
export const LANGUAGES = [
  { code: 'en', label: 'English', tags: ['en'] },
  { code: 'ko', label: '한국어', tags: ['ko'] },
  { code: 'ja', label: '日本語', tags: ['ja'] },
  { code: 'zh-Hans', label: '简体中文', tags: ['zh'] },
  { code: 'zh-Hant', label: '繁體中文', tags: ['zh-tw', 'zh-hk', 'zh-mo', 'zh-hant'] },
  { code: 'es', label: 'Español', tags: ['es'] },
  { code: 'fr', label: 'Français', tags: ['fr'] },
  { code: 'de', label: 'Deutsch', tags: ['de'] },
  { code: 'it', label: 'Italiano', tags: ['it'] },
  { code: 'pt', label: 'Português', tags: ['pt'] },
  { code: 'pl', label: 'Polski', tags: ['pl'] },
  { code: 'ru', label: 'Русский', tags: ['ru'] },
  { code: 'uk', label: 'Українська', tags: ['uk'] },
  { code: 'tr', label: 'Türkçe', tags: ['tr'] },
  { code: 'vi', label: 'Tiếng Việt', tags: ['vi'] },
  { code: 'th', label: 'ไทย', tags: ['th'] },
  { code: 'id', label: 'Bahasa Indonesia', tags: ['id'] },
  { code: 'hi', label: 'हिन्दी', tags: ['hi'] },
  { code: 'bn', label: 'বাংলা', tags: ['bn'] },
] as const

/** A language the pages are written in. */
export type PageLanguage = (typeof LANGUAGES)[number]['code']

/** The language of the pages for a browser's language tag ("zh-TW" is Traditional Chinese);
 * English when the pages are not written in it. */
export function browserLanguage(tag: string): PageLanguage {
  const lower = tag.toLowerCase()
  const has = (test: (t: string) => boolean) => LANGUAGES.find((l) => (l.tags as readonly string[]).some(test))
  // Region- or script-specific tags first, then the base language.
  const match = has((t) => t.includes('-') && lower.startsWith(t)) ?? has((t) => t === lower.split('-')[0])
  return match?.code ?? 'en'
}
