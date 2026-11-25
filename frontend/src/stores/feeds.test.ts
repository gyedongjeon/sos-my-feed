import { createPinia, setActivePinia } from 'pinia'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import type { Feed } from '../types'
import { useFeedsStore } from './feeds'

const article = (path: string, date = '') => ({ title: path, url: `https://example.org/${path}`, summary: '', date })
const NEWS: Feed = { title: 'News', url: 'https://example.org/news', articles: [article('old', '2026-11-01'), article('new', '2026-11-20')] }
const BLOG: Feed = { title: 'Blog', url: 'https://example.org/blog', articles: [article('post', '2026-11-10')] }

// A backend that answers each feed address with the feed given for it, and fails for any other.
function backend(feeds: Record<string, Omit<Feed, 'url'>>) {
  const fetchMock = vi.fn(async (_url: string, init?: RequestInit) => {
    const feed = feeds[JSON.parse(init!.body as string).url]
    return feed ? new Response(JSON.stringify(feed)) : new Response('{"error":"Could not read this feed"}', { status: 422 })
  })
  vi.stubGlobal('fetch', fetchMock)
  return fetchMock
}

function saved(feeds: Feed[]) {
  vi.stubGlobal('localStorage', { getItem: () => JSON.stringify({ feeds, language: 'en', theme: '' }) })
}

beforeEach(() => setActivePinia(createPinia()))
afterEach(() => vi.unstubAllGlobals())

describe('subscribing', () => {
  it('adds the feed and shows only its articles', async () => {
    saved([])
    backend({ 'https://example.org/news': { title: 'News', articles: NEWS.articles } })
    const store = useFeedsStore()
    expect(await store.subscribe(' https://example.org/news#top ')).toBe(true)
    expect(store.feeds).toEqual([NEWS])
    expect(store.filter).toBe(NEWS.url)
  })

  it('does not fetch a feed that is already there', async () => {
    saved([NEWS])
    const fetchMock = backend({})
    const store = useFeedsStore()
    expect(await store.subscribe(NEWS.url)).toBe(false)
    expect(store.message).toBe('feed.duplicate')
    expect(fetchMock).not.toHaveBeenCalled()
  })

  it('reports an address that is not a feed', async () => {
    saved([])
    backend({})
    const store = useFeedsStore()
    expect(await store.subscribe('https://example.org/page')).toBe(false)
    expect(store.message).toBe('feed.failed')
    expect(store.feeds).toEqual([])
    expect(store.busy).toBe(false)
  })
})

describe('refreshing', () => {
  it('takes the current articles of every feed', async () => {
    saved([NEWS])
    backend({ [NEWS.url]: { title: 'News', articles: [article('newest')] } })
    const store = useFeedsStore()
    await store.refresh()
    expect(store.feeds[0].articles).toEqual([article('newest')])
    expect(store.message).toBe('feed.updated')
  })

  it('keeps the articles of a feed that could not be read, and names it', async () => {
    saved([NEWS, BLOG])
    backend({ [BLOG.url]: { title: 'Blog', articles: [] } })
    const store = useFeedsStore()
    await store.refresh()
    expect(store.feeds[0]).toEqual(NEWS)
    expect(store.failures).toEqual(['News'])
    expect(store.message).toBe('feed.failed')
  })
})

describe('the articles shown', () => {
  it('are those of every feed, newest first', () => {
    saved([NEWS, BLOG])
    expect(useFeedsStore().posts.map((post) => post.article.title)).toEqual(['new', 'post', 'old'])
  })

  it('are those of the chosen feed only', () => {
    saved([NEWS, BLOG])
    const store = useFeedsStore()
    store.filter = BLOG.url
    expect(store.posts.map((post) => post.article.title)).toEqual(['post'])
  })
})

describe('unsubscribing', () => {
  it('removes the feed and shows every feed again', () => {
    saved([NEWS, BLOG])
    const store = useFeedsStore()
    store.filter = NEWS.url
    store.remove(NEWS.url)
    expect(store.feeds).toEqual([BLOG])
    expect(store.filter).toBe('')
  })
})
