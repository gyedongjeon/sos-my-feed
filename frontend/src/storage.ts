// The library as the browser keeps it, in local storage.
import type { Library } from './types'

const KEY = 'sos-my-feed.v1'

/** The saved library; on the first visit an empty one in the browser's language. */
export function loadLibrary(): Library {
  const initial: Library = { feeds: [], language: navigator.language.startsWith('ko') ? 'ko' : 'en', theme: '' }
  try {
    return JSON.parse(localStorage.getItem(KEY) || 'null') ?? initial
  } catch {
    return initial
  }
}

/** Resolves with whether the browser could keep it. */
export function saveLibrary(library: Library): boolean {
  try {
    localStorage.setItem(KEY, JSON.stringify(library))
    return true
  } catch {
    return false
  }
}
