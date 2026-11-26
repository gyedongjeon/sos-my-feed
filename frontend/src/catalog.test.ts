import { describe, expect, it } from 'vitest'
import { CATALOG, recommend, TOPICS } from './catalog'
import { LANGUAGES } from './languages'

describe('the catalog of feeds', () => {
  it('has feeds in every language of the pages', () => {
    for (const { code } of LANGUAGES) expect(CATALOG.some((feed) => feed.language === code), code).toBe(true)
  })

  it('lists each address once, as the subscribing writes it', () => {
    const urls = CATALOG.map((feed) => feed.url)
    expect(new Set(urls).size).toBe(urls.length)
    for (const url of urls) expect(new URL(url).href, url).toBe(url)
  })

  it('gives every feed a name and at least one known topic', () => {
    for (const feed of CATALOG) {
      expect(feed.title.trim(), feed.url).not.toBe('')
      expect(feed.topics.length, feed.url).toBeGreaterThan(0)
      for (const topic of feed.topics) expect(TOPICS, feed.url).toContain(topic)
    }
  })
})

describe('recommending feeds', () => {
  it('recommends the feeds in the language asked for', () => {
    const korean = recommend('ko', [])
    expect(korean.length).toBeGreaterThan(0)
    expect(korean.every((feed) => feed.language === 'ko')).toBe(true)
  })

  it('narrows them to the interests chosen', () => {
    const chosen = recommend('en', ['tech', 'science'])
    expect(chosen.length).toBeGreaterThan(0)
    expect(chosen.every((feed) => feed.topics.some((topic) => topic === 'tech' || topic === 'science'))).toBe(true)
    expect(chosen.length).toBeLessThan(recommend('en', []).length)
  })

  it('keeps the order of the catalog', () => {
    const english = CATALOG.filter((feed) => feed.language === 'en')
    expect(recommend('en', [])).toEqual(english)
  })
})
