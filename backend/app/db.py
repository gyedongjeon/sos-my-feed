"""SQLite access."""

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager

from .paths import DATA_DIR

DB_PATH = DATA_DIR / "app.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS feeds (
    id INTEGER PRIMARY KEY,
    -- The address subscribed to.
    url TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL
);

-- The articles a feed held when it was last read, in the feed's own order.
CREATE TABLE IF NOT EXISTS articles (
    id INTEGER PRIMARY KEY,
    feed_id INTEGER NOT NULL REFERENCES feeds (id) ON DELETE CASCADE,
    url TEXT NOT NULL,
    title TEXT NOT NULL,
    summary TEXT NOT NULL,
    -- As the feed wrote it; empty when the feed gave none.
    date TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS articles_by_feed ON articles (feed_id);
"""


@contextmanager
def get_connection() -> Iterator[sqlite3.Connection]:
    """A connection for one block of work: what the block changed is saved when it ends and
    dropped when it fails, and the connection is closed either way. Leaving it open would
    keep the database file locked on Windows."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        with conn:
            yield conn
    finally:
        conn.close()


def init_db() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with get_connection() as conn:
        conn.executescript(SCHEMA)
