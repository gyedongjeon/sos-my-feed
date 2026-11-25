// How an article is laid out and its pages are turned, after the Re:Leaf reader.
import type { ReaderTheme } from './types'

/** The colours of the paper: its own, the text's, and that of rules and quotation bars. */
export const READER_THEMES: Record<ReaderTheme, { paper: string; ink: string; rule: string; heading?: string }> = {
  light: { paper: '#ffffff', ink: '#222222', rule: '#eaeaea' },
  sepia: { paper: '#fcf6e5', ink: '#4a3c31', rule: '#eaddcf' },
  mint: { paper: '#e8f5e9', ink: '#2e5036', rule: '#c8e6c9' },
  forest: { paper: '#15803d', ink: '#ecfdf5', rule: '#166534' },
  gray: { paper: '#6b7280', ink: '#f3f4f6', rule: '#4b5563' },
  dark: { paper: '#1a1a1a', ink: '#d4d4d4', rule: '#333333', heading: '#ffffff' },
}

/** The space between two pages, in pixels: between the two that are shown side by side, and
 * between one page and the next that is out of sight. */
export const PAGE_GAP = 60

/** Two pages are shown side by side only where each has room for a line of text. */
export const SPREAD_MIN_WIDTH = 720

/** What a tap does by where it lands: the left and right fifths turn the page, the rest
 * shows or hides the menu. */
export function tapZone(x: number, width: number): 'previous' | 'next' | 'menu' {
  if (x < width * 0.2) return 'previous'
  if (x > width * 0.8) return 'next'
  return 'menu'
}

export interface Press {
  x: number
  y: number
  /** In milliseconds. */
  time: number
}

/** Whether a press and its release are a tap, not a drag (which selects text) or a long press. */
export function isTap(down: Press, up: Press): boolean {
  return Math.abs(up.x - down.x) < 10 && Math.abs(up.y - down.y) < 10 && up.time - down.time < 300
}

/**
 * The number of pages of a text laid out in columns, from the width the browser reports for
 * all of them and the width that is shown at once. A few pixels are allowed for, since a
 * browser may round the width up.
 */
export function pageCount(contentWidth: number, shownWidth: number): number {
  return Math.max(1, Math.ceil((contentWidth + PAGE_GAP - 10) / (shownWidth + PAGE_GAP)))
}
