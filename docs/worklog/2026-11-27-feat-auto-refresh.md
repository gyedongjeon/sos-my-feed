---
title: "feat: refresh the feeds on a schedule"
date: 2026-11-27
branch: feat/auto-refresh
request-source: "project chat, 2026-11-26"
---

## Request

The second of three features for daily use (read state, refreshing on a schedule, OPML import and export): read the feeds again on their own, at an interval the reader chooses, instead of only when **Refresh** is pressed.

## Changes

### Backend
- A new setting, `refresh_minutes`: one of 0, 15, 30, 60, or 180, and 30 by default; 0 refreshes only when asked. It is an `int` checked against those values rather than a `Literal`, because the database gives back the text `"30"`, which a `Literal` of numbers refuses.

### Frontend
- The schedule runs in the frontend (`src/autoRefresh.ts`), since the backend runs only while the app is open anyway. Once the settings and the feeds have loaded, the feeds are refreshed at once and then every interval. Choosing another interval starts it again from then, without refreshing at once.
- A refresh on a schedule is quiet: it takes the new articles but leaves the message and the names of failed feeds as they were, and it is skipped when something else (subscribing, a refresh asked for) is under way.
- **Settings** has a **Refresh feeds** choice: only when asked, every 15 or 30 minutes, every hour, or every 3 hours. Five new texts, in all 19 languages.

## Verification

- Backend: the interval is 30 at first, each offered value is kept, and other values (7, −15) are refused.
- Frontend: tests for the schedule (at once and each interval, waiting a whole interval, never at 0, stopping), the quiet refresh (says nothing; skipped while busy), and the interval in the settings store (loaded, and saved with the other choices).
- `cd backend && uv run pytest`, `cd frontend && npm test && npm run build`, `cd desktop && npm test && npx tsc --noEmit`, and `frontend/tests/article_reader.py` pass.
- Checked in Chrome on a temporary database: the feeds were refreshed once when the page opened, and choosing **Every hour** in Settings was saved without another refresh.
