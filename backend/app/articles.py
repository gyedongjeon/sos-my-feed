"""Extract plain reading text from a public article without loading its resources."""
import re
from html.parser import HTMLParser
from typing import Literal, NamedTuple

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from .feeds import UNREADABLE, fetch_public

router = APIRouter(prefix="/api")


class ArticleRequest(BaseModel):
    url: str = Field(min_length=1, max_length=2000)


class Block(BaseModel):
    kind: Literal["paragraph", "heading", "quote"]
    text: str


class ArticleText(BaseModel):
    # The text of the article in reading order.
    blocks: list[Block]


class State(NamedTuple):
    """What holds inside an element: whether its text is left out, and the group it is read into."""
    hidden: bool
    group: int


class ArticleParser(HTMLParser):
    block_tags = set('article main section div p br hr h2 h3 h4 h5 h6 li blockquote pre'.split())
    ignored = set('head header footer nav aside script style template noscript form button iframe svg h1'.split())
    news_extras = {'byline', 'metadata', 'media', 'image', 'eventPromo', 'promoList', 'topicList'}
    headings = set('h2 h3 h4 h5 h6'.split())
    void = set('area base br col embed hr img input link meta param source track wbr'.split())

    def __init__(self):
        super().__init__()
        self.stack = []
        self.groups = [[]]
        self.ranks = [0]
        self.state = State(hidden=False, group=0)
        self.fragments = []

    @property
    def hidden(self):
        return self.state.hidden

    @property
    def group(self):
        return self.state.group

    def flush(self):
        line = ' '.join(''.join(self.fragments).split())
        if line:
            self.groups[self.group].append({'kind': self.kind(), 'text': line})
        self.fragments.clear()

    def kind(self):
        """What the text being collected is, by the innermost element that says so."""
        for tag, _ in reversed(self.stack):
            if tag in self.headings:
                return 'heading'
            if tag == 'blockquote':
                return 'quote'
        return 'paragraph'

    def handle_starttag(self, tag, attrs):
        if tag in self.block_tags:
            self.flush()
        if tag in self.void:
            return
        attrs = dict(attrs)
        self.stack.append((tag, self.state))
        hidden = (self.hidden or tag in self.ignored or 'hidden' in attrs
                  or attrs.get('aria-hidden') == 'true' or attrs.get('data-block') in self.news_extras)
        self.state = self.state._replace(hidden=hidden)
        if self.hidden:
            return
        if attrs.get('itemprop') == 'articleBody' or attrs.get('id') in ('dic_area', 'articleBody'):
            rank = 3
        elif tag == 'article':
            rank = 2
        elif tag == 'main' or attrs.get('role') == 'main':
            rank = 1
        else:
            return
        if rank > self.ranks[self.group]:
            self.flush()
            self.state = self.state._replace(group=len(self.groups))
            self.groups.append([])
            self.ranks.append(rank)

    def handle_endtag(self, tag):
        if tag in self.void:
            return
        for index in range(len(self.stack) - 1, -1, -1):
            name, state = self.stack[index]
            if name == tag:
                if tag in self.block_tags or state.group != self.group:
                    self.flush()
                self.state = state
                del self.stack[index:]
                break

    def handle_data(self, data):
        if not self.hidden:
            self.fragments.append(data)

    def blocks(self):
        self.flush()
        candidates = (i for i, lines in enumerate(self.groups) if lines)
        best = max(candidates, key=lambda i: (self.ranks[i], sum(len(line['text']) for line in self.groups[i])),
                   default=None)
        if best is None:
            raise ValueError('No readable content')
        return self.groups[best]


def read_article(url):
    data, _, headers = fetch_public(url)
    if headers.get_content_type() not in ('text/html', 'application/xhtml+xml'):
        raise ValueError('Expected an HTML article')
    charset = headers.get_content_charset()
    if not charset:
        match = re.search(br'<meta\b[^>]*?charset\s*=\s*["\']?([\w.-]+)', data[:4096], re.I)
        charset = match.group(1).decode('ascii') if match else 'utf-8-sig'
    try:
        html = data.decode(charset, errors='replace')
    except LookupError:
        html = data.decode('utf-8', errors='replace')
    parser = ArticleParser()
    parser.feed(html)
    parser.close()
    return {'blocks': parser.blocks()}


@router.post("/article", response_model=ArticleText)
def article(body: ArticleRequest) -> ArticleText:
    try:
        return ArticleText(**read_article(body.url))
    except UNREADABLE as e:
        # The page is gone, is not HTML, or has no text to read; the reader shows the feed's summary.
        raise HTTPException(status_code=502, detail="Could not read this article.") from e
