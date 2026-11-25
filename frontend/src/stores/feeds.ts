import { defineStore } from 'pinia'
import { api } from '../api'
import { type MessageKey, t } from '../i18n'
import type { Article, Feed, Refreshed } from '../types'

/** An article as the list shows it: with its feed, and when it was published (0 when unknown). */
export interface Post {
  article: Article
  feed: Feed
  time: number
}

/** The subscriptions and their articles. The backend keeps them. */
export const useFeedsStore = defineStore('feeds', {
  state: () => ({
    feeds: [] as Feed[],
    // The feed whose articles are shown; null shows every feed's.
    filter: null as number | null,
    busy: false,
    // What the last subscribing or refreshing came to; null when there is nothing to say.
    message: null as MessageKey | null,
    // The titles of the feeds the last refresh could not read.
    failures: [] as string[],
    // Why the subscriptions could not be loaded or changed.
    error: '',
  }),
  getters: {
    /** The articles shown, newest first. */
    posts: (state): Post[] =>
      state.feeds
        .filter((feed) => state.filter === null || feed.id === state.filter)
        .flatMap((feed) => feed.articles.map((article) => ({ article, feed, time: Date.parse(article.date) || 0 })))
        .sort((a, b) => b.time - a.time),
  },
  actions: {
    async load() {
      this.error = ''
      try {
        this.feeds = await api<Feed[]>('/feeds')
      } catch (e) {
        this.error = t('feed.loadFailed', { error: (e as Error).message })
      }
    },
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
        const feed = await api<Feed>('/feeds', { method: 'POST', json: { url: parsed.href } })
        this.feeds.push(feed)
        this.filter = feed.id
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
        const { feeds, failed } = await api<Refreshed>('/feeds/refresh', { method: 'POST' })
        this.feeds = feeds
        this.failures = failed
        this.message = failed.length ? 'feed.failed' : 'feed.updated'
      } catch {
        this.message = 'feed.failed'
      } finally {
        this.busy = false
      }
    },
    /** Unsubscribes from a feed; resolves with whether it was removed. */
    async remove(id: number): Promise<boolean> {
      this.error = ''
      try {
        await api(`/feeds/${id}`, { method: 'DELETE' })
      } catch (e) {
        this.error = t('settings.removeFailed', { error: (e as Error).message })
        return false
      }
      this.feeds = this.feeds.filter((feed) => feed.id !== id)
      if (this.filter === id) this.filter = null
      this.failures = []
      this.message = null
      return true
    },
  },
})
