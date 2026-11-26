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


def test_images_keep_their_place_caption_and_description():
    """As BBC marks a photo: a picture with a credit, and a caption after a label only screen readers get."""
    parser = ArticleParser("https://www.bbc.com/news/articles/x")
    parser.feed(
        '<article><p>Before.</p><div data-block="image"><figure><picture>'
        '<source srcSet="https://ichef.bbci.co.uk/a/240.jpg.webp 240w" type="image/webp"/>'
        '<img alt="A presenter in the studio" src="https://ichef.bbci.co.uk/a/1920.jpg"/></picture>'
        '<span role="text"><span class="visually-hidden">Image source, </span>BBC</span>'
        '<figcaption><span class="visually-hidden">Image caption, </span><p>Bulletins get a new look</p></figcaption>'
        "</figure></div><p>After.</p></article>"
    )
    assert parser.blocks() == [
        {"kind": "paragraph", "text": "Before."},
        {"kind": "image", "src": "https://ichef.bbci.co.uk/a/1920.jpg", "alt": "A presenter in the studio", "text": "Bulletins get a new look"},
        {"kind": "paragraph", "text": "After."},
    ]


def test_a_lazy_image_is_taken_at_a_reading_size_from_its_real_address():
    parser = ArticleParser("https://example.org/news/story")
    parser.feed(
        '<article><p>Text.</p><img src="data:image/gif;base64,R0lG" alt="Map"'
        ' data-srcset="/img/400.jpg 400w, /img/800.jpg 800w, /img/1600.jpg 1600w"/>'
        '<img src="/pixel.gif" width="1" height="1"/></article>'
    )
    assert parser.blocks() == [
        {"kind": "paragraph", "text": "Text."},
        {"kind": "image", "src": "https://example.org/img/800.jpg", "alt": "Map", "text": ""},
    ]


def test_a_video_the_site_plays_itself_leads_to_the_page():
    parser = ArticleParser("https://www.bbc.com/news/articles/x")
    parser.feed(
        '<article><div data-block="media"><figure><div data-testid="media-player-container-landscape">'
        "<noscript><h2>To play this video you need to enable JavaScript in your browser.</h2></noscript></div>"
        '<figcaption><span class="visually-hidden">Figure caption, </span><p>New look for the app</p></figcaption>'
        "</figure></div><p>News.</p></article>"
    )
    assert parser.blocks() == [
        {"kind": "video", "src": "", "text": "New look for the app"},
        {"kind": "paragraph", "text": "News."},
    ]


def test_a_youtube_or_vimeo_video_is_kept_to_play_and_other_frames_are_not():
    parser = ArticleParser("https://example.org/story")
    parser.feed(
        '<article><p>Watch:</p><iframe src="https://www.youtube.com/embed/dQw4w9WgXcQ?si=abc"></iframe>'
        '<iframe data-src="//player.vimeo.com/video/76979871?h=1"></iframe>'
        '<iframe src="https://ads.example.net/frame"></iframe><video src="/clip.mp4"></video></article>'
    )
    assert parser.blocks() == [
        {"kind": "paragraph", "text": "Watch:"},
        {"kind": "video", "src": "https://www.youtube-nocookie.com/embed/dQw4w9WgXcQ", "text": ""},
        {"kind": "video", "src": "https://player.vimeo.com/video/76979871", "text": ""},
        {"kind": "video", "src": "", "text": ""},
    ]


def test_the_page_image_leads_an_article_without_pictures():
    parser = ArticleParser("https://example.org/story")
    parser.feed(
        '<html><head><meta property="og:image" content="/lead.jpg"></head>'
        "<body><article><p>Only text.</p></article></body></html>"
    )
    assert parser.blocks() == [
        {"kind": "image", "src": "https://example.org/lead.jpg", "alt": "", "text": ""},
        {"kind": "paragraph", "text": "Only text."},
    ]


def test_images_are_read_from_the_address_the_page_was_found_at(monkeypatch):
    headers = Message()
    headers["Content-Type"] = "text/html"
    page = b'<article><p>News.</p><img src="photo.jpg" alt=""></article>'
    monkeypatch.setattr(articles, "fetch_public", lambda url: (page, "https://example.org/2026/story/", headers))
    assert read_article("https://example.org/s")["blocks"][1]["src"] == "https://example.org/2026/story/photo.jpg"


def test_an_image_is_passed_on_through_the_backend(client, monkeypatch):
    headers = Message()
    headers["Content-Type"] = "image/jpeg"
    asked = []
    monkeypatch.setattr(articles, "fetch_public", lambda url: (asked.append(url), (b"\xff\xd8jpeg", url, headers))[1])
    response = client.get("/api/image", params={"url": "https://ichef.bbci.co.uk/a/1920.jpg"})
    assert response.status_code == 200
    assert response.content == b"\xff\xd8jpeg"
    assert response.headers["content-type"] == "image/jpeg"
    assert asked == ["https://ichef.bbci.co.uk/a/1920.jpg"]


def test_only_pictures_are_passed_on_as_images(client, monkeypatch):
    headers = Message()
    headers["Content-Type"] = "text/html"
    monkeypatch.setattr(articles, "fetch_public", lambda url: (b"<script>", url, headers))
    assert client.get("/api/image", params={"url": "https://example.org/page"}).status_code == 502


def test_the_article_answer_carries_its_pictures(client, monkeypatch):
    headers = Message()
    headers["Content-Type"] = "text/html"
    page = b'<article><p>News.</p><figure><img src="https://example.org/a.jpg" alt="A"><figcaption>Cap</figcaption></figure></article>'
    monkeypatch.setattr(articles, "fetch_public", lambda url: (page, url, headers))
    assert client.post("/api/article", json={"url": "https://example.org/story"}).json() == {
        "blocks": [
            {"kind": "paragraph", "text": "News."},
            {"kind": "image", "src": "https://example.org/a.jpg", "alt": "A", "text": "Cap"},
        ]
    }


def test_a_quotation_set_in_a_figure_is_still_read():
    parser = ArticleParser("https://example.org/story")
    parser.feed("<article><figure><blockquote><p>Words.</p></blockquote><figcaption>A speaker</figcaption></figure></article>")
    assert parser.blocks() == [{"kind": "quote", "text": "Words."}, {"kind": "paragraph", "text": "A speaker"}]


def test_a_picture_is_taken_at_a_reading_size_from_its_sources():
    """As the Guardian marks a photo: one size per source, told by a width in the address."""
    parser = ArticleParser("https://www.theguardian.com/world/story")
    parser.feed(
        '<article><p>Text.</p><figure><picture>'
        '<source srcSet="https://i.guim.co.uk/img/a.jpg?width=700&amp;dpr=2" media="(min-width: 740px)"/>'
        '<source srcSet="https://i.guim.co.uk/img/a.jpg?width=700&amp;dpr=1" media="(min-width: 740px)"/>'
        '<source srcSet="https://i.guim.co.uk/img/a.jpg?width=465&amp;dpr=2" media="(min-width: 320px)"/>'
        '<img alt="Cairo" src="https://i.guim.co.uk/img/a.jpg?width=445&amp;dpr=1" width="445"/></picture></figure></article>'
    )
    # Twice 465 is the smallest at least as wide as a page is read at.
    assert parser.blocks()[1]["src"] == "https://i.guim.co.uk/img/a.jpg?width=465&dpr=2"


def test_the_widest_size_offered_is_taken_when_none_is_as_wide_as_a_page():
    parser = ArticleParser("https://example.org/story")
    parser.feed(
        '<article><p>Text.</p><picture><source srcset="/a.jpg?width=700"/>'
        '<img alt="A" src="/a.jpg?width=445" width="445"/></picture></article>'
    )
    assert parser.blocks()[1]["src"] == "https://example.org/a.jpg?width=700"


def test_portraits_of_the_writers_and_small_pictures_are_left_out():
    parser = ArticleParser("https://example.org/story")
    parser.feed(
        '<article><p>Text.</p>'
        '<a href="/authors/stevie"><img alt="Stevie" width="36" height="36" src="/s.jpg?w=96"/></a>'
        '<figure><a href="/reporter/list?id=3"><img src="https://img.example.org/reporter/3.jpg" alt="Kim"></a></figure>'
        '<img alt="Icon" srcset="/i.png?w=48 1x, /i.png?w=96 2x"/>'
        '<a href="/full/photo.jpg"><img src="/photo-small.jpg" alt="Photo"/></a></article>'
    )
    assert parser.blocks() == [
        {"kind": "paragraph", "text": "Text."},
        {"kind": "image", "src": "https://example.org/photo-small.jpg", "alt": "Photo", "text": ""},
    ]


def test_a_picture_shown_twice_is_kept_once():
    parser = ArticleParser("https://example.org/story")
    parser.feed('<article><img src="/a.jpg" alt="A"/><p>Text.</p><img src="/a.jpg" alt="A"/></article>')
    assert [block["kind"] for block in parser.blocks()] == ["image", "paragraph"]
