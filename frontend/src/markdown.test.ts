import { describe, expect, it } from 'vitest'
import { articleMarkdown, markdownFileName } from './markdown'

const article = { title: 'Ships "at sea"', url: 'https://example.org/ships' }

describe('an article as Markdown', () => {
  it('starts with where it came from, then its title and its text', () => {
    const blocks = [
      { kind: 'paragraph' as const, text: 'First.' },
      { kind: 'heading' as const, text: 'Part one' },
      { kind: 'quote' as const, text: 'Quoted.' },
      { kind: 'paragraph' as const, text: 'Last.' },
    ]
    expect(articleMarkdown(article, blocks, '2026-11-25')).toBe(
      [
        '---',
        'title: "Ships \\"at sea\\""',
        'url: "https://example.org/ships"',
        'date: 2026-11-25',
        '---',
        '',
        '# Ships "at sea"',
        '',
        'First.',
        '',
        '## Part one',
        '',
        '> Quoted.',
        '',
        'Last.',
        '',
      ].join('\n'),
    )
  })
})

describe('pictures and videos in Markdown', () => {
  it('shows a picture by its address with its caption, and links a video', () => {
    const blocks = [
      { kind: 'image' as const, src: 'https://example.org/a.jpg', alt: 'A [ship]', text: 'At sea' },
      { kind: 'image' as const, src: 'https://example.org/b.jpg', alt: '', text: '' },
      { kind: 'video' as const, src: 'https://www.youtube-nocookie.com/embed/abc', text: 'Launch' },
      { kind: 'video' as const, src: '', text: '' },
    ]
    expect(articleMarkdown(article, blocks, '2026-11-25').split('\n\n').slice(2)).toEqual([
      '![A \\[ship\\]](https://example.org/a.jpg)\n*At sea*',
      '![](https://example.org/b.jpg)',
      '[▶ Launch](https://www.youtube-nocookie.com/embed/abc)',
      '[▶ Video](https://example.org/ships)\n',
    ])
  })
})

describe('the name of the file', () => {
  it('is the date and the title, without what a file name cannot hold', () => {
    expect(markdownFileName('Ships: "at sea" / part 1?', '2026-11-25')).toBe('2026-11-25_Ships_at_sea_part_1.md')
  })

  it('keeps Korean titles', () => {
    expect(markdownFileName('바다 위의 배', '2026-11-25')).toBe('2026-11-25_바다_위의_배.md')
  })

  it('is cut at 60 characters of title', () => {
    expect(markdownFileName('a'.repeat(80), '2026-11-25')).toBe(`2026-11-25_${'a'.repeat(60)}.md`)
  })

  it('has a name of its own when the title leaves nothing', () => {
    expect(markdownFileName(' ?? ', '2026-11-25')).toBe('2026-11-25_article.md')
  })
})
