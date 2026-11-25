"""Extract plain reading text from a public article without loading its resources."""
import re
from html.parser import HTMLParser

from .feeds import fetch_public


class ArticleParser(HTMLParser):
    blocks = set('article main section div p br hr h2 h3 h4 h5 h6 li blockquote pre'.split())
    ignored = set('head header footer nav aside script style template noscript form button iframe svg h1'.split())
    news_extras = {'byline', 'metadata', 'media', 'image', 'eventPromo', 'promoList', 'topicList'}
    void = set('area base br col embed hr img input link meta param source track wbr'.split())

    def __init__(self):
        super().__init__()
        self.stack = []
        self.groups = [[]]
        self.ranks = [0]
        self.group = 0
        self.hidden = False
        self.fragments = []

    def flush(self):
        line = ' '.join(''.join(self.fragments).split())
        if line:
            self.groups[self.group].append(line)
        self.fragments.clear()

    def handle_starttag(self, tag, attrs):
        if tag in self.blocks:
            self.flush()
        if tag in self.void:
            return
        attrs = dict(attrs)
        self.stack.append((tag, self.hidden, self.group))
        self.hidden = (self.hidden or tag in self.ignored or 'hidden' in attrs
                       or attrs.get('aria-hidden') == 'true' or attrs.get('data-block') in self.news_extras)
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
            self.group = len(self.groups)
            self.groups.append([])
            self.ranks.append(rank)

    def handle_endtag(self, tag):
        if tag in self.void:
            return
        for index in range(len(self.stack) - 1, -1, -1):
            name, hidden, group = self.stack[index]
            if name == tag:
                if tag in self.blocks or group != self.group:
                    self.flush()
                self.group, self.hidden = group, hidden
                del self.stack[index:]
                break

    def handle_data(self, data):
        if not self.hidden:
            self.fragments.append(data)

    def paragraphs(self):
        self.flush()
        candidates = (i for i, lines in enumerate(self.groups) if lines)
        best = max(candidates, key=lambda i: (self.ranks[i], sum(map(len, self.groups[i]))),
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
    return {'paragraphs': parser.paragraphs()}
