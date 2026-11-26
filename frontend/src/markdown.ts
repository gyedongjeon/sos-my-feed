// An article as a Markdown file, as Re:Leaf saves one.
import type { Block } from './types'

const label = (text: string) => text.replace(/[[\]]/g, '\\$&')

// A piece in Markdown; a video the reader cannot play links to the article's page.
function line(block: Block, page: string, video: string): string {
  switch (block.kind) {
    case 'heading':
      return `## ${block.text}`
    case 'quote':
      return `> ${block.text}`
    case 'image':
      return `![${label(block.alt)}](${block.src})` + (block.text ? `\n*${block.text}*` : '')
    case 'video':
      return `[▶ ${label(block.text || video)}](${block.src || page})`
    default:
      return block.text
  }
}

/** The article as Markdown: where it came from in a front matter, then its title, text, and
 * pictures (by their addresses on the site). */
export function articleMarkdown(article: { title: string; url: string }, blocks: Block[], date: string, video = 'Video'): string {
  const frontMatter = ['---', `title: "${article.title.replace(/"/g, '\\"')}"`, `url: "${article.url}"`, `date: ${date}`, '---']
  return [frontMatter.join('\n'), `# ${article.title}`, ...blocks.map((block) => line(block, article.url, video))].join('\n\n') + '\n'
}

/** A file name from the date and the title, without what a file name cannot hold. */
export function markdownFileName(title: string, date: string): string {
  const name = title
    .replace(/[<>:"/\\|?*\u0000-\u001f]/g, '')
    .trim()
    .replace(/\s+/g, '_')
    .replace(/_+/g, '_')
    .replace(/^_|_$/g, '')
    .slice(0, 60)
    .replace(/_$/, '')
  return `${date}_${name || 'article'}.md`
}
