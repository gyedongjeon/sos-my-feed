"""Reading RSS and Atom feeds."""

import pytest

from app.feeds import parse_feed


def test_atom_relative_article_link():
    feed = parse_feed(
        b'<feed xmlns="http://www.w3.org/2005/Atom"><title>Lab</title>'
        b'<entry><title>Note</title><link href="/note"/></entry></feed>',
        "https://example.org/feed",
    )
    assert feed["articles"][0]["url"] == "https://example.org/note"


def test_rss_preserves_publication_date_and_strips_summary_markup():
    feed = parse_feed(
        b"""<rss><channel><title>News</title><item>
        <title>Report</title><link>https://example.org/report</link>
        <pubDate>Tue, 24 Nov 2026 16:00:00 GMT</pubDate>
        <description><![CDATA[<p>Latest news</p>]]></description>
        </item></channel></rss>""",
        "https://example.org/rss",
    )
    article = feed["articles"][0]
    assert article["summary"] == "Latest news"
    assert article["date"] == "Tue, 24 Nov 2026 16:00:00 GMT"


def test_html_page_is_rejected():
    with pytest.raises(ValueError):
        parse_feed(b"<html><body/></html>", "https://example.org")


def test_requests_name_the_app_in_a_form_sites_accept(monkeypatch):
    """Some sites refuse a bare client name; the app names itself the way feed readers do."""
    import http.client
    import socket

    from app import feeds

    sent = {}

    def request(self, method, path, headers=None, **kwargs):
        sent.update(headers or {})
        raise OSError("stop before the network")

    monkeypatch.setattr(socket, "getaddrinfo", lambda *a, **k: [(None, None, None, None, ("93.184.215.14", 443))])
    monkeypatch.setattr(http.client.HTTPConnection, "request", request)
    with pytest.raises(OSError):
        feeds.fetch_public("https://example.org/feed")
    assert sent["User-Agent"] == "Mozilla/5.0 (compatible; SOS-My-Feed/0.1; +https://github.com/gyedongjeon/sos-my-feed)"
