// The shapes of what the backend answers and what the browser keeps.

/** A language the pages are written in. */
export type PageLanguage = 'en' | 'ko'

export interface Article {
  title: string
  url: string
  summary: string
  /** As the feed wrote it; empty when the feed gave none. */
  date: string
}

export interface Feed {
  title: string
  /** The address subscribed to; no two feeds share one. */
  url: string
  articles: Article[]
}

/** Everything the browser keeps: the subscriptions with their articles, and the preferences. */
export interface Library {
  feeds: Feed[]
  language: PageLanguage
  /** A daisyUI theme name; empty follows the system. */
  theme: string
  readerSize?: number
}
