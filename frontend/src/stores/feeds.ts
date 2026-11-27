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
    // Whether only the articles not read yet are shown.
    unreadOnly: false,
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
        .flatMap((feed) =>
          feed.articles
            .filter((article) => !state.unreadOnly || !article.read)
            .map((article) => ({ article, feed, time: Date.parse(article.date) || 0 })),
        )
        .sort((a, b) => b.time - a.time),
    /** How many articles are not read yet, of one feed or (null) of every feed. */
    unread:
      (state) =>
      (id: number | null): number =>
        state.feeds
          .filter((feed) => id === null || feed.id === id)
          .reduce((count, feed) => count + feed.articles.filter((article) => !article.read).length, 0),
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
    /** Subscribes to several feeds at once, such as those chosen from the catalog, and shows
     * every feed; resolves with how many were added. Those that cannot be read are named. */
    async subscribeAll(chosen: { title: string; url: string }[]): Promise<number> {
      if (this.busy) return 0
      this.message = null
      this.failures = []
      this.busy = true
      try {
        const asked = chosen.filter((choice) => !this.feeds.some((feed) => feed.url === choice.url))
        // Asked for together, so a slow site does not hold up the others.
        const answers = await Promise.allSettled(asked.map((choice) => api<Feed>('/feeds', { method: 'POST', json: { url: choice.url } })))
        const added = answers.flatMap((answer) => (answer.status === 'fulfilled' ? [answer.value] : []))
        this.feeds.push(...added)
        this.failures = asked.filter((_, i) => answers[i].status === 'rejected').map((choice) => choice.title)
        this.filter = null
        this.message = this.failures.length ? 'feed.failed' : 'catalog.added'
        return added.length
      } finally {
        this.busy = false
      }
    },
    /** Fetches every feed again. A feed that cannot be read keeps the articles it had. A quiet
     * refresh, done on a schedule, says nothing of how it went and waits for its next turn
     * when something else is under way. */
    async refresh({ quiet = false } = {}) {
      if (quiet && this.busy) return
      this.busy = true
      if (!quiet) {
        this.message = null
        this.failures = []
      }
      try {
        const { feeds, failed } = await api<Refreshed>('/feeds/refresh', { method: 'POST' })
        this.feeds = feeds
        if (quiet) return
        this.failures = failed
        this.message = failed.length ? 'feed.failed' : 'feed.updated'
      } catch {
        if (!quiet) this.message = 'feed.failed'
      } finally {
        this.busy = false
      }
    },
    /** Marks articles read, or unread again. The mark is shown at once and taken back if the
     * backend cannot keep it. */
    async mark(posts: Post[], read: boolean) {
      const changed = posts.filter((post) => post.article.read !== read)
      if (!changed.length) return
      this.error = ''
      for (const post of changed) post.article.read = read
      const byFeed = new Map<number, string[]>()
      for (const post of changed) byFeed.set(post.feed.id, [...(byFeed.get(post.feed.id) ?? []), post.article.url])
      const answers = await Promise.allSettled(
        [...byFeed].map(([id, urls]) => api(`/feeds/${id}/read`, { method: 'PUT', json: { urls, read } })),
      )
      const refused = answers.find((answer): answer is PromiseRejectedResult => answer.status === 'rejected')
      if (!refused) return
      const failed = new Set([...byFeed.keys()].filter((_, i) => answers[i].status === 'rejected'))
      for (const post of changed) if (failed.has(post.feed.id)) post.article.read = !read
      this.error = t('feed.markFailed', { error: (refused.reason as Error).message })
    },
    /** Marks every article shown read. */
    markAllRead() {
      return this.mark(this.posts, true)
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
