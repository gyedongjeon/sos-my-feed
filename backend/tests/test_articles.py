"""Extracting the reading text of an article."""

from email.message import Message

from app import articles
from app.articles import ArticleParser, read_article


def test_reader_returns_article_paragraphs_without_page_controls(monkeypatch):
    html = b"""<main><p>Other news</p><article><h1>Title</h1>
        <div>First <em>sentence</em>.</div><aside><p>Subscribe</p></aside>
        <p>Second &amp; last.</p><script>alert(1)</script></article></main>"""
    headers = Message()
    headers["Content-Type"] = "text/html"
    monkeypatch.setattr(articles, "fetch_public", lambda url: (html, url, headers))
    assert read_article("https://example.org") == {"paragraphs": ["First sentence.", "Second & last."]}


def test_related_links_and_media_controls_are_excluded_from_news_text():
    parser = ArticleParser()
    parser.feed(
        '<article><div data-block="media">Play video</div><p>News.</p>'
        '<div data-block="promoList">Other headlines</div></article>'
    )
    assert parser.paragraphs() == ["News."]
