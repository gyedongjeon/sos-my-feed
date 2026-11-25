import unittest
from email.message import Message
from unittest.mock import patch

from articles import ArticleParser, read_article


class ArticleTests(unittest.TestCase):
    def test_reader_returns_article_paragraphs_without_page_controls(self):
        html = b"""<main><p>Other news</p><article><h1>Title</h1>
            <div>First <em>sentence</em>.</div><aside><p>Subscribe</p></aside>
            <p>Second &amp; last.</p><script>alert(1)</script></article></main>"""
        headers = Message()
        headers['Content-Type'] = 'text/html'
        with patch('articles.fetch_public', return_value=(html, 'https://example.org', headers)):
            self.assertEqual(read_article('https://example.org'),
                             {'paragraphs': ['First sentence.', 'Second & last.']})

    def test_related_links_and_media_controls_are_excluded_from_news_text(self):
        parser = ArticleParser()
        parser.feed('<article><div data-block="media">Play video</div><p>News.</p>'
                    '<div data-block="promoList">Other headlines</div></article>')
        self.assertEqual(parser.paragraphs(), ['News.'])
