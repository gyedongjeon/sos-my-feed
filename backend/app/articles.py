"""Extract the text, pictures, and videos of a public article without running its scripts."""
import re
from html.parser import HTMLParser
from typing import Annotated, Literal, NamedTuple, Union
from urllib.parse import urljoin, urlsplit

from fastapi import APIRouter, HTTPException, Query, Response
from pydantic import BaseModel, Field

from .feeds import UNREADABLE, fetch_public

router = APIRouter(prefix="/api")


class ArticleRequest(BaseModel):
    url: str = Field(min_length=1, max_length=2000)


class TextBlock(BaseModel):
    kind: Literal["paragraph", "heading", "quote"]
    text: str


class ImageBlock(BaseModel):
    kind: Literal["image"]
    src: str
    alt: str
    # The caption; empty when the picture has none.
    text: str


class VideoBlock(BaseModel):
    kind: Literal["video"]
    # A player that can be shown in the reader; empty when the video plays only on the page itself.
    src: str
    # The caption; empty when the video has none.
    text: str


Block = Annotated[Union[TextBlock, ImageBlock, VideoBlock], Field(discriminator="kind")]


class ArticleText(BaseModel):
    # The text of the article in reading order.
    blocks: list[Block]


class State(NamedTuple):
    """What holds inside an element: whether its text is left out, the group it is read into,
    whether it shows a picture or video (whose text, but the caption, is not the article's),
    whether it is inside a link to another page, whether its text is a caption, and how many
    figures it is inside."""
    hidden: bool
    group: int
    media: bool = False
    linked: bool = False
    caption: bool = False
    figures: int = 0


# The pictures a page can show; anything else (a script, a page, an SVG) is not passed on.
IMAGE_TYPES = {'image/jpeg', 'image/png', 'image/gif', 'image/webp', 'image/avif'}
# A picture this wide reads well on a page; of the sizes offered, the next larger one is taken.
READING_WIDTH = 800
# A picture narrower than this is a portrait of the writer, an icon, or a tracking pixel.
SMALLEST_WIDTH = 200
SMALLEST_SIDE = 100
PICTURE_FILE = re.compile(r'\.(jpe?g|png|gif|webp|avif)$', re.I)
# The players kept for the reader, rebuilt from the video's id; YouTube's sets no cookies.
PLAYERS = (
    (re.compile(r'^(?:https?:)?//(?:www\.)?youtube(?:-nocookie)?\.com/embed/([\w-]{6,20})'), 'https://www.youtube-nocookie.com/embed/{}'),
    (re.compile(r'^(?:https?:)?//player\.vimeo\.com/video/(\d+)'), 'https://player.vimeo.com/video/{}'),
)


def player(src):
    """The address of a YouTube or Vimeo player for an embedded frame; empty for any other frame."""
    for pattern, address in PLAYERS:
        match = pattern.match(src or '')
        if match:
            return address.format(match.group(1))
    return ''


def sizes(srcset):
    """The (width, address) of each candidate of a srcset; the width is the one it is described by,
    or else the one its address asks for (`?width=620`, times `dpr=2`), or else 0."""
    found = []
    for candidate in re.split(r',\s+', (srcset or '').strip()):
        bits = candidate.split()
        if not bits or bits[0].startswith('data:'):
            continue
        described = bits[1][:-1] if len(bits) > 1 and bits[1].endswith('w') else ''
        asked = re.search(r'[?&](?:w|width)=(\d+)', bits[0])
        width = described if described.isdigit() else asked.group(1) if asked else '0'
        ratio = re.search(r'[?&]dpr=(\d+)', bits[0]) if not described else None
        found.append((int(width) * (int(ratio.group(1)) if ratio else 1), bits[0]))
    return found


def picture(attrs, base, sources=()):
    """The address of a picture at a reading size, from the sizes it and its <picture>'s sources
    offer, or else from its (lazily loaded) source; empty for a small picture or an inline image."""
    if any(attrs.get(side, '').isdigit() and int(attrs[side]) < SMALLEST_SIDE for side in ('width', 'height')):
        return ''
    src = ''
    for key in ('data-src', 'data-original', 'data-lazy-src', 'src'):
        if attrs.get(key) and not attrs[key].startswith('data:'):
            src = attrs[key]
            break
    offered = [size for srcset in (attrs.get('data-srcset'), attrs.get('srcset'), *sources) for size in sizes(srcset)]
    # The source's own width, as the <img> says it or its address asks for it; 0 when unknown.
    own = int(attrs['width']) if attrs.get('width', '').isdigit() else (sizes(src)[0][0] if src else 0)
    if src:
        offered.append((own, src))
    known = [size for size in offered if size[0]]
    if known and max(known)[0] < SMALLEST_WIDTH and (own or not src):
        return ''
    wide = [size for size in known if size[0] >= READING_WIDTH]
    if wide:
        src = min(wide)[1]
    elif known and (not src or own and max(known)[0] > own):
        # A source of unknown width is taken as the original; one known to be narrower gives way.
        src = max(known)[1]
    elif not src and offered:
        src = offered[0][1]
    address = urljoin(base, src.strip()) if src else ''
    parts = urlsplit(address)
    if parts.scheme not in ('http', 'https') or parts.path.lower().endswith('.svg'):
        return ''
    return address


class ArticleParser(HTMLParser):
    block_tags = set('article main section div p br hr h2 h3 h4 h5 h6 li blockquote pre'.split())
    ignored = set('head header footer nav aside script style template noscript form button iframe svg h1 video audio'.split())
    news_extras = {'byline', 'metadata', 'eventPromo', 'promoList', 'topicList'}
    # BBC's blocks of a picture or a video: only their captions are read.
    news_media = {'media', 'image'}
    # Text only screen readers are given, such as BBC's "Image caption, ".
    unseen = {'visually-hidden', 'sr-only', 'screen-reader-text'}
    headings = set('h2 h3 h4 h5 h6'.split())
    void = set('area base br col embed hr img input link meta param source track wbr'.split())

    def __init__(self, base=''):
        super().__init__()
        # The address of the page, against which pictures' addresses are read.
        self.base = base
        # The picture the page gives for sharing; it leads an article that shows none.
        self.page_image = ''
        # The figures being read: the picture or video each shows, and its caption so far.
        self.figures = []
        # The srcsets of the <picture> being read, for its <img>.
        self.sources = []
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

    def add(self, block):
        """Puts a picture or video where it stands in the text; the first in a figure takes its caption."""
        self.flush()
        # A picture shown twice (a page's placeholder and the picture itself) is kept once.
        shown = next((b for b in self.groups[self.group] if block['kind'] == 'image' and b.get('src') == block['src']), None)
        if shown is None:
            self.groups[self.group].append(block)
        if self.state.figures and self.figures[-1]['media'] is None:
            self.figures[-1]['media'] = shown or block

    def end_figure(self):
        figure = self.figures.pop()
        caption = ' '.join(''.join(figure['caption']).split())
        if figure['media'] is not None:
            figure['media']['text'] = caption
        elif caption:
            self.groups[self.group].append({'kind': 'paragraph', 'text': caption})

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
        attrs = {name: value or '' for name, value in attrs}
        if tag == 'meta' and attrs.get('property') == 'og:image' and not self.page_image:
            self.page_image = picture({'src': attrs.get('content', '')}, self.base)
        if tag == 'picture':
            self.sources = []
        elif tag == 'source' and (attrs.get('srcset') or attrs.get('data-srcset')):
            self.sources.append(attrs.get('srcset') or attrs.get('data-srcset'))
        if tag == 'img':
            sources, self.sources = self.sources, []
        if tag == 'img' and not self.hidden and not self.state.linked:
            src = picture(attrs, self.base, sources)
            if src:
                self.add({'kind': 'image', 'src': src, 'alt': ' '.join(attrs.get('alt', '').split()), 'text': ''})
        if tag in self.void:
            return
        if not self.hidden:
            if tag == 'iframe' and player(attrs.get('src') or attrs.get('data-src')):
                self.add({'kind': 'video', 'src': player(attrs.get('src') or attrs.get('data-src')), 'text': ''})
            elif tag == 'video' or attrs.get('data-testid', '').startswith('media-player-container'):
                # A video the site plays with its own player: the reader leads to the page.
                self.add({'kind': 'video', 'src': '', 'text': ''})
        self.stack.append((tag, self.state))
        hidden = (self.hidden or tag in self.ignored or 'hidden' in attrs
                  or attrs.get('aria-hidden') == 'true' or attrs.get('data-block') in self.news_extras
                  or not self.unseen.isdisjoint(attrs.get('class', '').split()))
        self.state = self.state._replace(hidden=hidden)
        if self.hidden:
            return
        if tag == 'a' and attrs.get('href'):
            # A picture in a link to a page is a writer's portrait or a promotion, not the article's.
            self.state = self.state._replace(linked=not PICTURE_FILE.search(urlsplit(attrs['href']).path))
        if tag == 'figure':
            self.flush()
            self.figures.append({'media': None, 'caption': []})
            self.state = self.state._replace(figures=self.state.figures + 1, media=True)
        elif attrs.get('data-block') in self.news_media:
            self.state = self.state._replace(media=True)
        elif tag == 'blockquote':
            # A quotation set in a figure is still read.
            self.state = self.state._replace(media=False)
        elif tag == 'figcaption' and self.state.figures:
            self.flush()
            self.state = self.state._replace(caption=True)
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
                while len(self.figures) > state.figures:
                    self.end_figure()
                self.state = state
                del self.stack[index:]
                break

    def handle_data(self, data):
        if self.hidden:
            return
        if self.state.caption:
            self.figures[-1]['caption'].append(data)
        elif not self.state.media:
            self.fragments.append(data)

    def blocks(self):
        self.flush()
        while self.figures:
            self.end_figure()
        # Pictures and videos do not count toward which part of the page is the article.
        candidates = (i for i, lines in enumerate(self.groups) if any(line['kind'] not in ('image', 'video') for line in lines))
        best = max(candidates, key=lambda i: (self.ranks[i], sum(len(line['text']) for line in self.groups[i])),
                   default=None)
        if best is None:
            raise ValueError('No readable content')
        blocks = self.groups[best]
        if self.page_image and not any(block['kind'] in ('image', 'video') for block in blocks):
            blocks = [{'kind': 'image', 'src': self.page_image, 'alt': '', 'text': ''}, *blocks]
        return blocks


def read_article(url):
    data, address, headers = fetch_public(url)
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
    parser = ArticleParser(address)
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


@router.get("/image")
def image(url: str = Query(min_length=1, max_length=2000)) -> Response:
    """A picture of an article, read by the backend like the article itself, so that the reader's
    pages load nothing from the sites directly."""
    try:
        data, _, headers = fetch_public(url)
    except UNREADABLE as e:
        raise HTTPException(status_code=502, detail="Could not read this image.") from e
    if headers.get_content_type() not in IMAGE_TYPES:
        raise HTTPException(status_code=502, detail="Not an image.")
    return Response(content=data, media_type=headers.get_content_type(), headers={"Cache-Control": "max-age=86400"})
