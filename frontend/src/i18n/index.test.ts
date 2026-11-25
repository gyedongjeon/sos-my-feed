import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it } from 'vitest'
import { useSettingsStore } from '../stores/settings'
import en from './en'
import { PAGE_LANGUAGES, t } from './index'
import ko from './ko'

beforeEach(() => setActivePinia(createPinia()))

describe('the texts of the pages', () => {
  it('are in English when English is chosen', () => {
    useSettingsStore().language = 'en'
    expect(t('nav.settings')).toBe('Settings')
  })

  it('are in Korean when Korean is chosen', () => {
    useSettingsStore().language = 'ko'
    expect(t('nav.settings')).toBe('설정')
  })

  it('are written in English and Korean, with the same keys', () => {
    expect(PAGE_LANGUAGES).toEqual(['en', 'ko'])
    expect(Object.keys(ko).sort()).toEqual(Object.keys(en).sort())
  })
})
