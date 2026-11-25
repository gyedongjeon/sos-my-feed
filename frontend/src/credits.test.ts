import { describe, expect, it } from 'vitest'
import notices from '../public/THIRD_PARTY_NOTICES.txt?raw'
import { CREDITS } from './credits'

describe('the work the app is built with', () => {
  it('is listed as the series lists it, the heading font first', () => {
    expect(CREDITS.map((c) => c.name)).toEqual([
      'Bricolage Grotesque (heading font)',
      'Vue',
      'Vue Router',
      'Pinia',
      'daisyUI',
      'Tailwind CSS',
      'uv (desktop app)',
    ])
  })

  it('names the holders whose notices are shipped with the app', () => {
    for (const credit of CREDITS) {
      const holder = credit.copyright.replace(/^© (\d{4}(-present)? )?/, '')
      expect(notices, credit.name).toContain(holder)
    }
  })
})
