import { createPinia, setActivePinia } from 'pinia'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import type { Feed } from '../types'
import { useFeedsStore } from './feeds'

const article = (path: string, date = '', read = false) => ({ title: path, url: `https://example.org/${path}`, summary: '', date, read })
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

describe('subscribing to several feeds', () => {
  const WORLD: Feed = { id: 3, title: 'World', url: 'https://example.org/world', articles: [] }

  // A backend that subscribes to the given feeds by their addresses, and to no other.
  async function readable(feeds: Feed[], subscribed: Feed[] = []) {
    const { store } = await loaded(subscribed)
    const fetchMock = vi.fn(async (_url: string, init?: RequestInit) => {
      const found = feeds.find((feed) => feed.url === JSON.parse(String(init?.body)).url)
      return found
        ? new Response(JSON.stringify(found), { status: 201 })
        : new Response(JSON.stringify({ detail: 'Could not read this feed.' }), { status: 502 })
    })
    vi.stubGlobal('fetch', fetchMock)
    return { store, fetchMock }
  }

  it('adds every feed chosen, in the order chosen, and shows all of them', async () => {
    const { store } = await readable([NEWS, BLOG])
    store.filter = 7
    expect(await store.subscribeAll([BLOG, NEWS])).toBe(2)
    expect(store.feeds).toEqual([BLOG, NEWS])
    expect(store.filter).toBeNull()
    expect(store.message).toBe('catalog.added')
    expect(store.busy).toBe(false)
  })

  it('names the feeds that could not be read and keeps the others', async () => {
    const { store } = await readable([NEWS])
    expect(await store.subscribeAll([NEWS, WORLD])).toBe(1)
    expect(store.feeds).toEqual([NEWS])
    expect(store.failures).toEqual(['World'])
    expect(store.message).toBe('feed.failed')
  })

  it('does not ask again for a feed that is already there', async () => {
    const { store, fetchMock } = await readable([NEWS, BLOG], [NEWS])
    expect(await store.subscribeAll([NEWS, BLOG])).toBe(1)
    expect(fetchMock).toHaveBeenCalledTimes(1)
    expect(store.feeds).toEqual([NEWS, BLOG])
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

  it('says nothing when it is done on its own', async () => {
    const newest = { ...NEWS, articles: [article('newest')] }
    const { store } = await loaded([NEWS], { 'POST /api/feeds/refresh': { body: { feeds: [newest], failed: ['Blog'] } } })
    store.message = 'catalog.added'
    await store.refresh({ quiet: true })
    expect(store.feeds).toEqual([newest])
    expect(store.message).toBe('catalog.added')
    expect(store.failures).toEqual([])
  })

  it('is not done on its own while something else is under way', async () => {
    const { store, fetchMock } = await loaded([NEWS])
    store.busy = true
    await store.refresh({ quiet: true })
    expect(fetchMock).not.toHaveBeenCalled()
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

describe('reading', () => {
  const MIXED: Feed = { ...NEWS, articles: [article('old', '2026-11-01', true), article('new', '2026-11-20')] }

  it('counts the unread articles of every feed or of one', async () => {
    const { store } = await loaded([MIXED, BLOG])
    expect(store.unread(null)).toBe(2)
    expect(store.unread(NEWS.id)).toBe(1)
    expect(store.unread(BLOG.id)).toBe(1)
  })

  it('shows only the unread articles when asked to', async () => {
    const { store } = await loaded([MIXED, BLOG])
    store.unreadOnly = true
    expect(store.posts.map((post) => post.article.title)).toEqual(['new', 'post'])
  })

  it('marks an article read and tells the backend', async () => {
    const { store, fetchMock } = await loaded([NEWS], { 'PUT /api/feeds/1/read': { status: 204 } })
    await store.mark([store.posts[0]], true)
    expect(store.feeds[0].articles.map((a) => a.read)).toEqual([false, true])
    expect(fetchMock).toHaveBeenCalledTimes(1)
    expect(fetchMock.mock.calls[0][1]!.body).toBe('{"urls":["https://example.org/new"],"read":true}')
  })

  it('does not ask the backend about an article that is already marked so', async () => {
    const { store, fetchMock } = await loaded([MIXED])
    await store.mark(store.posts.filter((post) => post.article.read), true)
    expect(fetchMock).not.toHaveBeenCalled()
  })

  it('marks every article shown read, feed by feed', async () => {
    const { store, fetchMock } = await loaded([NEWS, BLOG], {
      'PUT /api/feeds/1/read': { status: 204 },
      'PUT /api/feeds/2/read': { status: 204 },
    })
    await store.markAllRead()
    expect(store.unread(null)).toBe(0)
    expect(fetchMock.mock.calls.map((call) => call[0]).sort()).toEqual(['/api/feeds/1/read', '/api/feeds/2/read'])
  })

  it("marks only the chosen feed's articles read", async () => {
    const { store } = await loaded([NEWS, BLOG], { 'PUT /api/feeds/2/read': { status: 204 } })
    store.filter = BLOG.id
    await store.markAllRead()
    expect(store.unread(NEWS.id)).toBe(2)
    expect(store.unread(BLOG.id)).toBe(0)
  })

  it('takes the mark back and reports an error when the backend refuses', async () => {
    const { store } = await loaded([NEWS], { 'PUT /api/feeds/1/read': { status: 500, body: { detail: 'disk full' } } })
    await store.mark(store.posts, true)
    expect(store.unread(null)).toBe(2)
    expect(store.error).toBe('Could not save what you have read: disk full')
  })
})

describe('importing an OPML file', () => {
  // A backend that lists the given feeds from any OPML file and subscribes to those it can read.
  function importing(listed: { title: string; url: string }[], readable: Feed[]) {
    const fetchMock = vi.fn(async (url: string, init?: RequestInit) => {
      if (url === '/api/opml') return new Response(JSON.stringify(listed), { status: 200 })
      const found = readable.find((feed) => feed.url === JSON.parse(String(init?.body)).url)
      return found
        ? new Response(JSON.stringify(found), { status: 201 })
        : new Response(JSON.stringify({ detail: 'Could not read this feed.' }), { status: 502 })
    })
    vi.stubGlobal('fetch', fetchMock)
    return fetchMock
  }

  it('subscribes to the feeds it lists', async () => {
    const { store } = await loaded([])
    const fetchMock = importing([NEWS, BLOG].map(({ title, url }) => ({ title, url })), [NEWS, BLOG])
    expect(await store.importOpml('<opml/>')).toBe(2)
    expect(fetchMock.mock.calls[0][1]!.body).toBe('<opml/>')
    expect(store.feeds).toEqual([NEWS, BLOG])
    expect(store.message).toBe('opml.added')
  })

  it('names the feeds that could not be read', async () => {
    const { store } = await loaded([])
    importing([NEWS, BLOG].map(({ title, url }) => ({ title, url })), [NEWS])
    expect(await store.importOpml('<opml/>')).toBe(1)
    expect(store.failures).toEqual(['Blog'])
    expect(store.message).toBe('feed.failed')
  })

  it('says so when the file lists no feed to add', async () => {
    const { store } = await loaded([NEWS])
    importing([{ title: NEWS.title, url: NEWS.url }], [NEWS])
    expect(await store.importOpml('<opml/>')).toBe(0)
    expect(store.message).toBe('opml.nothing')
  })

  it('reports a file that is not OPML', async () => {
    const { store } = await loaded([])
    vi.stubGlobal('fetch', async () => new Response(JSON.stringify({ detail: 'Not an OPML file.' }), { status: 422 }))
    expect(await store.importOpml('hello')).toBe(0)
    expect(store.message).toBe('opml.invalid')
    expect(store.busy).toBe(false)
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
