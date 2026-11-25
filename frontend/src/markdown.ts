// An article as a Markdown file, as Re:Leaf saves one.
import type { Block } from './types'

const line = (block: Block) => (block.kind === 'heading' ? `## ${block.text}` : block.kind === 'quote' ? `> ${block.text}` : block.text)

/** The article as Markdown: where it came from in a front matter, then its title and text. */
export function articleMarkdown(article: { title: string; url: string }, blocks: Block[], date: string): string {
  const frontMatter = ['---', `title: "${article.title.replace(/"/g, '\\"')}"`, `url: "${article.url}"`, `date: ${date}`, '---']
  return [frontMatter.join('\n'), `# ${article.title}`, ...blocks.map(line)].join('\n\n') + '\n'
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
