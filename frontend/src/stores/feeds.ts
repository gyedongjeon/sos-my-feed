import { defineStore } from 'pinia'
import { api } from '../api'
import type { MessageKey } from '../i18n'
import { loadLibrary } from '../storage'
import type { Article, Feed } from '../types'

/** An article as the list shows it: with its feed, and when it was published (0 when unknown). */
export interface Post {
  article: Article
  feed: Feed
  time: number
}

async function fetchFeed(url: string): Promise<Feed> {
  return { ...(await api<Omit<Feed, 'url'>>('/feed', { method: 'POST', json: { url } })), url }
}

/** The subscriptions and their articles. */
export const useFeedsStore = defineStore('feeds', {
  state: () => ({
    feeds: loadLibrary().feeds,
    // The address of the feed whose articles are shown; empty shows every feed's.
    filter: '',
    busy: false,
    // What the last subscribing or refreshing came to; null when there is nothing to say.
    message: null as MessageKey | null,
    // The titles of the feeds the last refresh could not read.
    failures: [] as string[],
  }),
  getters: {
    /** The articles shown, newest first. */
    posts: (state): Post[] =>
      state.feeds
        .filter((feed) => !state.filter || feed.url === state.filter)
        .flatMap((feed) => feed.articles.map((article) => ({ article, feed, time: Date.parse(article.date) || 0 })))
        .sort((a, b) => b.time - a.time),
  },
  actions: {
    /** Subscribes to the feed at an address; resolves with whether it was added. */
    async subscribe(address: string): Promise<boolean> {
      if (this.busy) return false
      this.message = null
      this.failures = []
      this.busy = true
      try {
        const parsed = new URL(address.trim())
        parsed.hash = ''
        if (this.feeds.some((feed) => feed.url === parsed.href)) {
          this.message = 'feed.duplicate'
          return false
        }
        const feed = await fetchFeed(parsed.href)
        this.feeds.push(feed)
        this.filter = feed.url
        return true
      } catch {
        this.message = 'feed.failed'
        return false
      } finally {
        this.busy = false
      }
    },
    /** Fetches every feed again. A feed that cannot be read keeps the articles it had. */
    async refresh() {
      this.busy = true
      this.message = null
      this.failures = []
      try {
        for (const feed of this.feeds) {
          try {
            Object.assign(feed, await fetchFeed(feed.url))
          } catch {
            this.failures.push(feed.title)
          }
        }
        this.message = this.failures.length ? 'feed.failed' : 'feed.updated'
      } finally {
        this.busy = false
      }
    },
    remove(url: string) {
      this.feeds = this.feeds.filter((feed) => feed.url !== url)
      if (this.filter === url) this.filter = ''
      this.failures = []
      this.message = null
    },
  },
})
