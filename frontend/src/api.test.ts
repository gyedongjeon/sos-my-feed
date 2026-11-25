import { afterEach, describe, expect, it, vi } from 'vitest'
import { api } from './api'

function respondWith(status: number, body?: unknown) {
  const text = body === undefined ? null : typeof body === 'string' ? body : JSON.stringify(body)
  const fetchMock = vi.fn(async (..._args: Parameters<typeof fetch>) => new Response(text, { status }))
  vi.stubGlobal('fetch', fetchMock)
  return fetchMock
}

afterEach(() => vi.unstubAllGlobals())

describe('api', () => {
  it('returns the parsed body of a successful request', async () => {
    const fetchMock = respondWith(200, { title: 'News' })
    expect(await api('/feed')).toEqual({ title: 'News' })
    expect(fetchMock.mock.calls[0][0]).toBe('/api/feed')
  })

  it('sends `json` as a JSON body', async () => {
    const fetchMock = respondWith(200, {})
    await api('/feed', { method: 'POST', json: { url: 'https://example.org/feed' } })
    const init = fetchMock.mock.calls[0][1]!
    expect(init.method).toBe('POST')
    expect(init.headers).toEqual({ 'Content-Type': 'application/json' })
    expect(init.body).toBe('{"url":"https://example.org/feed"}')
  })

  it('returns nothing for 204 No Content', async () => {
    respondWith(204)
    expect(await api('/feed', { method: 'DELETE' })).toBeUndefined()
  })

  it("throws the backend's message when a request fails", async () => {
    respondWith(502, { detail: 'Could not read this feed.' })
    await expect(api('/feed')).rejects.toThrow('Could not read this feed.')
  })

  it('throws the status when the failure has no readable message', async () => {
    respondWith(500, 'Internal Server Error')
    await expect(api('/feed')).rejects.toThrow('HTTP 500')
    respondWith(422, { detail: [{ msg: 'field required' }] })
    await expect(api('/feed')).rejects.toThrow('HTTP 422')
  })
})
