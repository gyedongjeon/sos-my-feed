import { describe, expect, it } from 'vitest'
import { browserLanguage, LANGUAGES } from './languages'

describe('the languages of the pages', () => {
  it('are the nineteen of the series, English first', () => {
    expect(LANGUAGES.map((l) => l.code)).toEqual([
      'en', 'ko', 'ja', 'zh-Hans', 'zh-Hant', 'es', 'fr', 'de', 'it', 'pt',
      'pl', 'ru', 'uk', 'tr', 'vi', 'th', 'id', 'hi', 'bn',
    ])
  })

  it('are each named in themselves', () => {
    expect(LANGUAGES.find((l) => l.code === 'ja')?.label).toBe('日本語')
    expect(LANGUAGES.find((l) => l.code === 'zh-Hant')?.label).toBe('繁體中文')
  })
})

describe('the language of the browser', () => {
  it.each([
    ['ko-KR', 'ko'],
    ['ja', 'ja'],
    ['zh-CN', 'zh-Hans'],
    ['zh', 'zh-Hans'],
    ['zh-TW', 'zh-Hant'],
    ['zh-HK', 'zh-Hant'],
    ['zh-Hant-TW', 'zh-Hant'],
    ['pt-BR', 'pt'],
    ['de-AT', 'de'],
    ['uk-UA', 'uk'],
    ['bn-BD', 'bn'],
    ['en-GB', 'en'],
  ])('is matched to the pages: %s -> %s', (tag, expected) => {
    expect(browserLanguage(tag)).toBe(expected)
  })

  it('is English where the pages are not written in it', () => {
    expect(browserLanguage('sv-SE')).toBe('en')
    expect(browserLanguage('')).toBe('en')
  })
})
