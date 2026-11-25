import { describe, expect, it } from 'vitest'
import { LANGUAGES } from '../languages'
import en from './en'

// Every file of texts next to this one, by its name.
const pages = import.meta.glob<Record<string, string>>(['./*.ts', '!./en.ts', '!./index.ts', '!./*.test.ts'], {
  eager: true,
  import: 'default',
})

const keys = Object.keys(en) as (keyof typeof en)[]
const names = (text: string) => new Set([...text.matchAll(/\{(\w+)\}/g)].map((m) => m[1]))

describe('the files of texts', () => {
  it('are one for each language of the pages but English', () => {
    const files = Object.keys(pages).map((file) => file.replace(/^\.\/|\.ts$/g, ''))
    expect(files.sort()).toEqual(LANGUAGES.map((l) => l.code).filter((code) => code !== 'en').sort())
  })
})

describe.each(Object.entries(pages))('the texts of the pages in %s', (_file, texts) => {
  it('have every text', () => {
    expect(Object.keys(texts).sort()).toEqual([...keys].sort())
    for (const key of keys) expect(texts[key].trim(), key).not.toBe('')
  })

  it('have the same names to fill in', () => {
    for (const key of keys) expect(names(texts[key]), key).toEqual(names(en[key]))
  })
})
