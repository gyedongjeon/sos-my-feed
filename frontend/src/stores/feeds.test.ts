import { createPinia, setActivePinia } from 'pinia'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import type { Feed } from '../types'
import { useFeedsStore } from './feeds'

const article = (path: string, date = '') => ({ title: path, url: `https://example.org/${path}`, summary: '', date })
const NEWS: Feed = { id: 1, title: 'News', url: 'https://example.org/news', articles: [article('old', '2026-11-01'), article('new', '2026-11-20')] }
const BLOG: Feed = { id: 2, title: 'Blog', url: 'https://example.org/blog', articles: [article('post', '2026-11-10')] }

type Answer = { status?: number; body?: unknown }

// A backend that answers each "METHOD /path" with what is given for it, and fails any other.
function backend(answers: Record<string, Answer>) {
  const fetchMock = vi.fn(async (url: string, init?: RequestInit) => {
    const answer = answers[`${init?.method ?? 'GET'} ${url}`] ?? { status: 502, body: { detail: 'Could not read this feed.' } }
    return new Response(answer.body === undefined ? null : JSON.stringify(answer.body), { status: answer.status ?? 200 })
  })
  vi.stubGlobal('fetch', fetchMock)
  return fetchMock
}

// The store as it is once the page has loaded the given subscriptions.
async function loaded(feeds: Feed[], answers: Record<string, Answer> = {}) {
  const fetchMock = backend({ 'GET /api/feeds': { body: feeds }, ...answers })
  const store = useFeedsStore()
  await store.load()
  fetchMock.mockClear()
  return { store, fetchMock }
}

beforeEach(() => {
  // The pages start in the browser's language; the messages here are checked in English.
  vi.stubGlobal('navigator', { language: 'en-US' })
  setActivePinia(createPinia())
})
afterEach(() => vi.unstubAllGlobals())

describe('loading', () => {
  it('takes the subscriptions the backend keeps', async () => {
    const { store } = await loaded([NEWS, BLOG])
    expect(store.feeds).toEqual([NEWS, BLOG])
    expect(store.error).toBe('')
  })

  it('reports a backend that does not answer', async () => {
    backend({ 'GET /api/feeds': { status: 500, body: { detail: 'database is locked' } } })
    const store = useFeedsStore()
    await store.load()
    expect(store.error).toBe('Could not load your feeds: database is locked')
  })
})

describe('subscribing', () => {
  it('adds the feed and shows only its articles', async () => {
    const { store, fetchMock } = await loaded([], { 'POST /api/feeds': { status: 201, body: NEWS } })
    expect(await store.subscribe(' https://example.org/news#top ')).toBe(true)
    expect(fetchMock.mock.calls[0][1]!.body).toBe('{"url":"https://example.org/news"}')
    expect(store.feeds).toEqual([NEWS])
    expect(store.filter).toBe(NEWS.id)
  })

  it('does not ask for a feed that is already there', async () => {
    const { store, fetchMock } = await loaded([NEWS])
    expect(await store.subscribe(NEWS.url)).toBe(false)
    expect(store.message).toBe('feed.duplicate')
    expect(fetchMock).not.toHaveBeenCalled()
  })

  it('reports an address that is not a feed', async () => {
    const { store } = await loaded([])
    expect(await store.subscribe('https://example.org/page')).toBe(false)
    expect(store.message).toBe('feed.failed')
    expect(store.feeds).toEqual([])
    expect(store.busy).toBe(false)
  })
})

describe('refreshing', () => {
  it('takes the current articles of every feed', async () => {
    const newest = { ...NEWS, articles: [article('newest')] }
    const { store } = await loaded([NEWS], { 'POST /api/feeds/refresh': { body: { feeds: [newest], failed: [] } } })
    await store.refresh()
    expect(store.feeds).toEqual([newest])
    expect(store.message).toBe('feed.updated')
  })

  it('names the feeds that could not be read', async () => {
    const { store } = await loaded([NEWS, BLOG], { 'POST /api/feeds/refresh': { body: { feeds: [NEWS, BLOG], failed: ['News'] } } })
    await store.refresh()
    expect(store.feeds).toEqual([NEWS, BLOG])
    expect(store.failures).toEqual(['News'])
    expect(store.message).toBe('feed.failed')
  })

  it('keeps what is shown when the backend does not answer', async () => {
    const { store } = await loaded([NEWS])
    await store.refresh()
    expect(store.feeds).toEqual([NEWS])
    expect(store.message).toBe('feed.failed')
    expect(store.busy).toBe(false)
  })
})

describe('the articles shown', () => {
  it('are those of every feed, newest first', async () => {
    const { store } = await loaded([NEWS, BLOG])
    expect(store.posts.map((post) => post.article.title)).toEqual(['new', 'post', 'old'])
  })

  it('are those of the chosen feed only', async () => {
    const { store } = await loaded([NEWS, BLOG])
    store.filter = BLOG.id
    expect(store.posts.map((post) => post.article.title)).toEqual(['post'])
  })
})

describe('unsubscribing', () => {
  it('removes the feed and shows every feed again', async () => {
    const { store } = await loaded([NEWS, BLOG], { 'DELETE /api/feeds/1': { status: 204 } })
    store.filter = NEWS.id
    expect(await store.remove(NEWS.id)).toBe(true)
    expect(store.feeds).toEqual([BLOG])
    expect(store.filter).toBeNull()
  })

  it('keeps the feed and reports an error when the backend refuses', async () => {
    const { store } = await loaded([NEWS], { 'DELETE /api/feeds/1': { status: 500, body: { detail: 'disk full' } } })
    expect(await store.remove(NEWS.id)).toBe(false)
    expect(store.feeds).toEqual([NEWS])
    expect(store.error).toBe('Could not unsubscribe: disk full')
  })
})
