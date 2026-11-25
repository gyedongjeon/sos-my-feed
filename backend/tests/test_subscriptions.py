"""Subscribing to feeds, refreshing them, and unsubscribing."""

import pytest

from app import subscriptions

NEWS = "https://example.org/news"
BLOG = "https://example.org/blog"


def article(path: str, date: str = "") -> dict:
    return {"title": path.title(), "url": f"https://example.org/{path}", "summary": f"About {path}.", "date": date}


@pytest.fixture
def web(monkeypatch):
    """The feeds that can be read, by address; any other address cannot be."""
    feeds: dict[str, dict] = {}

    def download(url: str) -> dict:
        if url not in feeds:
            raise ValueError("Expected RSS or Atom")
        return feeds[url]

    monkeypatch.setattr(subscriptions, "download", download)
    return feeds


def test_there_are_no_feeds_at_first(client):
    assert client.get("/api/feeds").json() == []


def test_subscribing_keeps_the_feed_with_its_articles(client, web):
    web[NEWS] = {"title": "News", "articles": [article("first", "Tue, 24 Nov 2026 16:00:00 GMT"), article("second")]}
    response = client.post("/api/feeds", json={"url": NEWS})
    assert response.status_code == 201
    feed = response.json()
    assert feed == {"id": feed["id"], "url": NEWS, "title": "News", "articles": web[NEWS]["articles"]}
    assert client.get("/api/feeds").json() == [feed]


def test_feeds_are_listed_in_the_order_they_were_subscribed_to(client, web):
    web[NEWS] = {"title": "News", "articles": []}
    web[BLOG] = {"title": "Blog", "articles": []}
    client.post("/api/feeds", json={"url": NEWS})
    client.post("/api/feeds", json={"url": BLOG})
    assert [feed["title"] for feed in client.get("/api/feeds").json()] == ["News", "Blog"]


def test_a_feed_is_subscribed_to_only_once(client, web):
    web[NEWS] = {"title": "News", "articles": []}
    client.post("/api/feeds", json={"url": NEWS})
    response = client.post("/api/feeds", json={"url": NEWS})
    assert response.status_code == 409
    assert len(client.get("/api/feeds").json()) == 1


def test_an_address_that_cannot_be_read_is_not_subscribed_to(client, web):
    response = client.post("/api/feeds", json={"url": "https://example.org/page"})
    assert response.status_code == 502
    assert response.json()["detail"] == "Could not read this feed."
    assert client.get("/api/feeds").json() == []


def test_refreshing_replaces_the_articles_of_every_feed(client, web):
    web[NEWS] = {"title": "News", "articles": [article("old")]}
    client.post("/api/feeds", json={"url": NEWS})
    web[NEWS] = {"title": "News today", "articles": [article("new"), article("newer")]}
    result = client.post("/api/feeds/refresh").json()
    assert result["failed"] == []
    assert result["feeds"] == client.get("/api/feeds").json()
    assert result["feeds"][0]["title"] == "News today"
    assert result["feeds"][0]["articles"] == [article("new"), article("newer")]


def test_a_feed_that_cannot_be_refreshed_keeps_its_articles_and_is_named(client, web):
    web[NEWS] = {"title": "News", "articles": [article("old")]}
    web[BLOG] = {"title": "Blog", "articles": [article("post")]}
    client.post("/api/feeds", json={"url": NEWS})
    client.post("/api/feeds", json={"url": BLOG})
    del web[NEWS]
    web[BLOG] = {"title": "Blog", "articles": [article("latest")]}
    result = client.post("/api/feeds/refresh").json()
    assert result["failed"] == ["News"]
    assert [feed["articles"] for feed in result["feeds"]] == [[article("old")], [article("latest")]]


def test_unsubscribing_removes_the_feed_and_its_articles(client, web):
    web[NEWS] = {"title": "News", "articles": [article("old")]}
    feed = client.post("/api/feeds", json={"url": NEWS}).json()
    assert client.delete(f"/api/feeds/{feed['id']}").status_code == 204
    assert client.get("/api/feeds").json() == []
    # Subscribing again starts from what the feed holds now, not from what was kept.
    web[NEWS] = {"title": "News", "articles": [article("new")]}
    assert client.post("/api/feeds", json={"url": NEWS}).json()["articles"] == [article("new")]


def test_unsubscribing_from_an_unknown_feed_is_reported(client):
    assert client.delete("/api/feeds/7").status_code == 404
