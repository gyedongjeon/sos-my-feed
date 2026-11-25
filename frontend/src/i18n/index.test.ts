import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it } from 'vitest'
import { LANGUAGES } from '../languages'
import { useSettingsStore } from '../stores/settings'
import { PAGE_LANGUAGES, t } from './index'

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

  it('have their names filled in', () => {
    useSettingsStore().language = 'en'
    expect(t('settings.saveFailed', { error: 'disk full' })).toBe('Could not save the setting: disk full')
    useSettingsStore().language = 'ko'
    expect(t('settings.saveFailed', { error: 'disk full' })).toBe('설정을 저장하지 못했습니다: disk full')
  })

  it('are written in every language of the pages', () => {
    expect(PAGE_LANGUAGES).toEqual(LANGUAGES.map((l) => l.code))
    useSettingsStore().language = 'ja'
    expect(t('nav.settings')).toBe('設定')
    useSettingsStore().language = 'de'
    expect(t('nav.settings')).toBe('Einstellungen')
  })
})
