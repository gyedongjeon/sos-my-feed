---
title: "feat: keep track of the articles read"
date: 2026-11-26
branch: feat/read-state
request-source: "project chat, 2026-11-26"
---

## Request

The first of three features for daily use (read state, refreshing on a schedule, OPML import and export): know which articles have been read, see how many are unread, show only those, and mark them all as read.

## Changes

### Backend
- A new table, `read_articles (feed_id, url)`, holds the articles read. It is kept apart from `articles`, which is replaced each time a feed is read, so an article stays read through refreshes. Once an article is no longer in its feed it is forgotten, so the table does not grow without end; an article that comes back later is unread. Unsubscribing removes a feed's rows with it.
- Every article in `GET /api/feeds` (and in subscribing and refreshing) carries `read`.
- `PUT /api/feeds/{id}/read` with `{"urls": [...], "read": true | false}` marks articles read or unread again. Only the articles the feed holds are marked; other addresses are ignored. An unknown feed is a 404.
- The table is created with `CREATE TABLE IF NOT EXISTS`, so an existing `app.db` gains it at startup without other steps.

### Frontend
- An article counts as read once it is opened, in the reader or on its site. A dot beside each article (filled while unread, a ring once read) marks it the other way by hand. Read articles are dimmed.
- The feed buttons show how many articles are unread. A second row under them holds an **Unread only** switch and **Mark all as read**, which marks every article shown (of the chosen feed, or of all). With only unread articles shown and none left, the list says so.
- A mark is shown at once and taken back, with an error, if the backend cannot keep it.
- Six new texts, in all 19 languages.
- Whether only unread articles are shown is not saved; the list starts with all of them.

## Verification

- Backend: tests for articles unread at first, marking read and unread, staying read through a refresh, forgetting an article that left its feed, ignoring addresses the feed does not hold, an unknown feed, and subscribing again.
- Frontend: store tests for the unread counts, the unread-only list, marking (and not asking again for an article already marked so), marking all of every feed or of one, and taking a mark back when the backend refuses.
- `cd backend && uv run pytest`, `cd frontend && npm test && npm run build`, `cd desktop && npm test && npx tsc --noEmit`, and `frontend/tests/article_reader.py` pass.
- Checked in Chrome on a temporary database: the counts, marking with the dot, the unread-only switch, marking all read, and the read state after reloading the page.
