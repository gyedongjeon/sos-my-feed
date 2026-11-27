"""Importing and exporting the subscriptions as OPML, the file other feed readers use."""

import xml.etree.ElementTree as ET

import pytest

from app import subscriptions

OPML = """<?xml version="1.0" encoding="UTF-8"?>
<opml version="2.0">
  <head><title>From another reader</title></head>
  <body>
    <outline text="News" title="News" type="rss" xmlUrl="https://example.org/news" htmlUrl="https://example.org/"/>
    <outline text="Tech">
      <outline text="Blog &amp; more" type="rss" xmlUrl="https://example.org/blog"/>
      <outline title="No text" xmlUrl="https://example.org/untitled"/>
    </outline>
    <outline text="A folder with nothing to read"/>
    <outline text="Again" xmlUrl="https://example.org/news"/>
    <outline text="Not on the web" xmlUrl="file:///etc/passwd"/>
  </body>
</opml>"""


def read(client, text: str | bytes):
    return client.post("/api/opml", content=text, headers={"Content-Type": "text/x-opml"})


def test_the_feeds_of_an_opml_file_are_listed_once_each_folders_and_all(client):
    response = read(client, OPML)
    assert response.status_code == 200
    assert response.json() == [
        {"title": "News", "url": "https://example.org/news"},
        {"title": "Blog & more", "url": "https://example.org/blog"},
        {"title": "No text", "url": "https://example.org/untitled"},
    ]


def test_reading_an_opml_file_subscribes_to_nothing(client):
    read(client, OPML)
    assert client.get("/api/feeds").json() == []


@pytest.mark.parametrize("text", ["", "not xml", "<rss><channel/></rss>"])
def test_a_file_that_is_not_opml_is_refused(client, text):
    response = read(client, text)
    assert response.status_code == 422
    assert response.json()["detail"] == "Not an OPML file."


def test_an_opml_file_that_is_too_large_is_refused(client):
    assert read(client, b" " * (5 * 1024 * 1024 + 1)).status_code == 413


def test_the_subscriptions_are_exported_as_opml(client, monkeypatch):
    feeds = {
        "https://example.org/news": {"title": "News & views", "articles": []},
        "https://example.org/blog": {"title": "Blog", "articles": []},
    }
    monkeypatch.setattr(subscriptions, "download", lambda url: feeds[url])
    for url in feeds:
        client.post("/api/feeds", json={"url": url})
    response = client.get("/api/opml")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/x-opml")
    assert 'filename="sos-my-feed.opml"' in response.headers["content-disposition"]
    root = ET.fromstring(response.content)
    assert root.tag == "opml"
    outlines = [(o.get("text"), o.get("title"), o.get("type"), o.get("xmlUrl")) for o in root.iter("outline")]
    assert outlines == [
        ("News & views", "News & views", "rss", "https://example.org/news"),
        ("Blog", "Blog", "rss", "https://example.org/blog"),
    ]


def test_an_exported_file_can_be_read_back(client, monkeypatch):
    monkeypatch.setattr(subscriptions, "download", lambda url: {"title": "News", "articles": []})
    client.post("/api/feeds", json={"url": "https://example.org/news"})
    exported = client.get("/api/opml").content
    assert read(client, exported).json() == [{"title": "News", "url": "https://example.org/news"}]
