import { describe, expect, it } from 'vitest'
import { imageAddress, isTap, PAGE_GAP, pageCount, READER_THEMES, tapZone } from './reader'

describe('a tap on the page', () => {
  it('turns back on the left fifth and forward on the right fifth', () => {
    expect(tapZone(0, 1000)).toBe('previous')
    expect(tapZone(199, 1000)).toBe('previous')
    expect(tapZone(801, 1000)).toBe('next')
    expect(tapZone(999, 1000)).toBe('next')
  })

  it('shows or hides the menu anywhere between', () => {
    expect(tapZone(200, 1000)).toBe('menu')
    expect(tapZone(500, 1000)).toBe('menu')
    expect(tapZone(800, 1000)).toBe('menu')
  })

  it('is a short press that stays in place', () => {
    const down = { x: 100, y: 100, time: 1000 }
    expect(isTap(down, { x: 104, y: 97, time: 1200 })).toBe(true)
    // Dragging selects text; holding opens the system's menu.
    expect(isTap(down, { x: 130, y: 100, time: 1200 })).toBe(false)
    expect(isTap(down, { x: 100, y: 115, time: 1200 })).toBe(false)
    expect(isTap(down, { x: 100, y: 100, time: 1400 })).toBe(false)
  })
})

describe('the number of pages', () => {
  const width = 800
  // What the browser reports for text laid out in `columns` columns, each as wide as `column`.
  const laidOut = (columns: number, column: number) => columns * column + (columns - 1) * PAGE_GAP

  it('is one for text that fits', () => {
    expect(pageCount(width, width)).toBe(1)
    expect(pageCount(0, width)).toBe(1)
  })

  it('is the number of columns when one page is shown', () => {
    expect(pageCount(laidOut(7, width), width)).toBe(7)
  })

  it('is half the columns when two are shown side by side, with a last page that may be half empty', () => {
    const column = (width - PAGE_GAP) / 2
    expect(pageCount(laidOut(6, column), width)).toBe(3)
    expect(pageCount(laidOut(7, column), width)).toBe(4)
  })

  it('is not raised by the fraction of a pixel a browser may add', () => {
    expect(pageCount(laidOut(3, width) + 2, width)).toBe(3)
  })
})

describe('the colours of the paper', () => {
  it('are the six of Re:Leaf, light first', () => {
    expect(Object.keys(READER_THEMES)).toEqual(['light', 'sepia', 'mint', 'forest', 'gray', 'dark'])
  })
})

describe('a picture of an article', () => {
  it('is asked of the backend, which reads it like the article', () => {
    expect(imageAddress('https://ichef.bbci.co.uk/a.jpg?w=800&q=1')).toBe('/api/image?url=https%3A%2F%2Fichef.bbci.co.uk%2Fa.jpg%3Fw%3D800%26q%3D1')
  })
})
