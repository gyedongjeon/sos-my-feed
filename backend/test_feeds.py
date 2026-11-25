import unittest
from feeds import parse_feed


class FeedTests(unittest.TestCase):
    def test_atom_relative_article_link(self):
        feed = parse_feed(b'<feed xmlns="http://www.w3.org/2005/Atom"><title>Lab</title><entry><title>Note</title><link href="/note"/></entry></feed>', 'https://example.org/feed')
        self.assertEqual(feed['articles'][0]['url'], 'https://example.org/note')

    def test_rss_preserves_publication_date_and_strips_summary_markup(self):
        feed = parse_feed(b"""<rss><channel><title>News</title><item>
            <title>Report</title><link>https://example.org/report</link>
            <pubDate>Tue, 24 Nov 2026 16:00:00 GMT</pubDate>
            <description><![CDATA[<p>Latest news</p>]]></description>
            </item></channel></rss>""", 'https://example.org/rss')
        article = feed['articles'][0]
        self.assertEqual(article['summary'], 'Latest news')
        self.assertEqual(article['date'], 'Tue, 24 Nov 2026 16:00:00 GMT')

    def test_html_page_is_rejected(self):
        with self.assertRaises(ValueError):
            parse_feed(b'<html><body/></html>', 'https://example.org')
