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
