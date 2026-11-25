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
    assert read_article("https://example.org") == {
        "blocks": [
            {"kind": "paragraph", "text": "First sentence."},
            {"kind": "paragraph", "text": "Second & last."},
        ]
    }


def test_related_links_and_media_controls_are_excluded_from_news_text():
    parser = ArticleParser()
    parser.feed(
        '<article><div data-block="media">Play video</div><p>News.</p>'
        '<div data-block="promoList">Other headlines</div></article>'
    )
    assert parser.blocks() == [{"kind": "paragraph", "text": "News."}]


def test_headings_and_quotations_keep_their_kind():
    parser = ArticleParser()
    parser.feed(
        "<article><p>Opening.</p><h2>Part <em>one</em></h2><p>Body.</p>"
        "<blockquote><p>Quoted line.</p><p>Second quoted line.</p></blockquote><p>Closing.</p></article>"
    )
    assert parser.blocks() == [
        {"kind": "paragraph", "text": "Opening."},
        {"kind": "heading", "text": "Part one"},
        {"kind": "paragraph", "text": "Body."},
        {"kind": "quote", "text": "Quoted line."},
        {"kind": "quote", "text": "Second quoted line."},
        {"kind": "paragraph", "text": "Closing."},
    ]


def test_the_text_of_an_article_is_answered(client, monkeypatch):
    headers = Message()
    headers["Content-Type"] = "text/html"
    monkeypatch.setattr(articles, "fetch_public", lambda url: (b"<article><p>News.</p></article>", url, headers))
    response = client.post("/api/article", json={"url": "https://example.org/story"})
    assert response.json() == {"blocks": [{"kind": "paragraph", "text": "News."}]}


def test_an_article_that_cannot_be_read_is_reported(client, monkeypatch):
    def offline(url):
        raise OSError("offline")

    monkeypatch.setattr(articles, "fetch_public", offline)
    response = client.post("/api/article", json={"url": "https://example.org/story"})
    assert response.status_code == 502
    assert response.json()["detail"] == "Could not read this article."
