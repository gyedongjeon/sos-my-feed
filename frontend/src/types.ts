// The shapes of what the backend answers.

/** A language the pages are written in. */
export type PageLanguage = 'en' | 'ko'

/** A theme of the pages by its daisyUI name; empty follows the system. */
export type Theme = '' | 'sos' | 'sos-night'

export interface Article {
  title: string
  url: string
  summary: string
  /** As the feed wrote it; empty when the feed gave none. */
  date: string
}

export interface Feed {
  id: number
  /** The address subscribed to; no two feeds share one. */
  url: string
  title: string
  articles: Article[]
}

/** What a refresh came to: every feed as it is now, and the titles of those that could not be read. */
export interface Refreshed {
  feeds: Feed[]
  failed: string[]
}

export interface Settings {
  /** null until the reader, or the browser's language on the first visit, has chosen one. */
  language: PageLanguage | null
  theme: Theme
  /** The size of an article's text, in pixels. */
  reader_size: number
}
