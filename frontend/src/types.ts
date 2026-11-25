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

/** A piece of an article's text, in reading order. */
export interface Block {
  kind: 'paragraph' | 'heading' | 'quote'
  text: string
}

/** A colour of the paper an article is read on. */
export type ReaderTheme = 'light' | 'sepia' | 'mint' | 'forest' | 'gray' | 'dark'

/** How an article is laid out for reading. */
export interface ReaderSettings {
  theme: ReaderTheme
  /** The size of the text, in pixels. */
  size: number
  /** The height of a line, in text sizes. */
  lineHeight: number
  /** The margins above and below the text, and beside it, in pixels. */
  marginV: number
  marginH: number
  /** One page, or two side by side. */
  pages: number
  /** Whether the reader has been shown how pages are turned. */
  tutorialSeen: boolean
}

/** The settings as the backend keeps them. */
export interface Settings {
  /** null until the reader, or the browser's language on the first visit, has chosen one. */
  language: PageLanguage | null
  theme: Theme
  reader_theme: ReaderTheme
  reader_size: number
  reader_line_height: number
  reader_margin_v: number
  reader_margin_h: number
  reader_pages: number
  reader_tutorial_seen: boolean
}
