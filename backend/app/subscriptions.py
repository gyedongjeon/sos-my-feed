"""The feeds the reader subscribed to, kept in the database with the articles they held when
they were last read."""

import sqlite3

from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel, Field

from .db import get_connection
from .feeds import UNREADABLE, download

router = APIRouter(prefix="/api")


class Article(BaseModel):
    title: str
    url: str
    summary: str
    # As the feed wrote it; empty when the feed gave none.
    date: str
    read: bool


class Feed(BaseModel):
    id: int
    url: str
    title: str
    articles: list[Article]


class Subscription(BaseModel):
    url: str = Field(min_length=1, max_length=2000)


class Marked(BaseModel):
    # The addresses of articles of the feed; any other address is ignored.
    urls: list[str] = Field(max_length=1000)
    read: bool


class Refreshed(BaseModel):
    feeds: list[Feed]
    # The titles of the feeds that could not be read; they keep the articles they had.
    failed: list[str]


def _feeds(conn: sqlite3.Connection) -> list[Feed]:
    articles: dict[int, list[Article]] = {}
    rows = conn.execute(
        "SELECT a.feed_id, a.title, a.url, a.summary, a.date, r.url IS NOT NULL AS read FROM articles a"
        " LEFT JOIN read_articles r ON r.feed_id = a.feed_id AND r.url = a.url ORDER BY a.id"
    )
    for row in rows:
        articles.setdefault(row["feed_id"], []).append(Article(**{key: row[key] for key in Article.model_fields}))
    return [
        Feed(id=row["id"], url=row["url"], title=row["title"], articles=articles.get(row["id"], []))
        for row in conn.execute("SELECT id, url, title FROM feeds ORDER BY id")
    ]


def _keep(conn: sqlite3.Connection, feed_id: int, read: dict) -> None:
    """Replaces what is kept of a feed by what was just read from it."""
    conn.execute("UPDATE feeds SET title = ? WHERE id = ?", (read["title"], feed_id))
    conn.execute("DELETE FROM articles WHERE feed_id = ?", (feed_id,))
    conn.executemany(
        "INSERT INTO articles (feed_id, title, url, summary, date) VALUES (?, ?, ?, ?, ?)",
        [(feed_id, a["title"], a["url"], a["summary"], a["date"]) for a in read["articles"]],
    )
    conn.execute(
        "DELETE FROM read_articles WHERE feed_id = ? AND url NOT IN (SELECT url FROM articles WHERE feed_id = ?)",
        (feed_id, feed_id),
    )


@router.get("/feeds", response_model=list[Feed])
def list_feeds() -> list[Feed]:
    with get_connection() as conn:
        return _feeds(conn)


@router.post("/feeds", response_model=Feed, status_code=201)
def subscribe(body: Subscription) -> Feed:
    url = body.url.strip()
    with get_connection() as conn:
        if conn.execute("SELECT 1 FROM feeds WHERE url = ?", (url,)).fetchone():
            raise HTTPException(status_code=409, detail="Already subscribed.")
    try:
        read = download(url)
    except UNREADABLE as e:
        raise HTTPException(status_code=502, detail="Could not read this feed.") from e
    with get_connection() as conn:
        try:
            feed_id = conn.execute("INSERT INTO feeds (url, title) VALUES (?, ?)", (url, read["title"])).lastrowid
        except sqlite3.IntegrityError as e:
            # Subscribed to in the meantime, by a second request for the same address.
            raise HTTPException(status_code=409, detail="Already subscribed.") from e
        _keep(conn, feed_id, read)
        return next(feed for feed in _feeds(conn) if feed.id == feed_id)


@router.post("/feeds/refresh", response_model=Refreshed)
def refresh() -> Refreshed:
    with get_connection() as conn:
        subscribed = conn.execute("SELECT id, url, title FROM feeds ORDER BY id").fetchall()
    failed = []
    for feed in subscribed:
        try:
            read = download(feed["url"])
        except UNREADABLE:
            failed.append(feed["title"])
            continue
        # Each feed is saved as soon as it is read, so one that fails later does not undo it.
        with get_connection() as conn:
            _keep(conn, feed["id"], read)
    with get_connection() as conn:
        return Refreshed(feeds=_feeds(conn), failed=failed)


@router.put("/feeds/{feed_id}/read", status_code=204)
def mark(feed_id: int, body: Marked) -> Response:
    """Marks articles of a feed as read, or as unread again."""
    with get_connection() as conn:
        if not conn.execute("SELECT 1 FROM feeds WHERE id = ?", (feed_id,)).fetchone():
            raise HTTPException(status_code=404, detail="No such feed.")
        for url in set(body.urls):
            if body.read:
                conn.execute(
                    "INSERT OR IGNORE INTO read_articles (feed_id, url)"
                    " SELECT feed_id, url FROM articles WHERE feed_id = ? AND url = ?",
                    (feed_id, url),
                )
            else:
                conn.execute("DELETE FROM read_articles WHERE feed_id = ? AND url = ?", (feed_id, url))
    return Response(status_code=204)


@router.delete("/feeds/{feed_id}", status_code=204)
def unsubscribe(feed_id: int) -> Response:
    with get_connection() as conn:
        if conn.execute("DELETE FROM feeds WHERE id = ?", (feed_id,)).rowcount == 0:
            raise HTTPException(status_code=404, detail="No such feed.")
    return Response(status_code=204)
