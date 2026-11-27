---
title: "chore: release v0.5.0"
date: 2026-11-27
branch: chore/release-v0.5.0
request-source: "project chat, 2026-11-27"
---

## Request

Prepare the release of what was merged since v0.4.0.

## Changes

Raise the version from 0.4.0 to 0.5.0 in the three files that carry it (`backend/pyproject.toml`, `frontend/package.json`, `desktop/package.json`) and their lock files.

Merged since v0.4.0:

- #17 `ci: update the GitHub Actions to versions that run on Node.js 24`.
- #18 `feat: keep track of the articles read` — unread counts, an unread-only switch, marking read or unread, and marking all as read.
- #19 `feat: refresh the feeds on a schedule` — when the app opens and then every 30 minutes by default; the interval is chosen in Settings.
- #20 `feat: import and export the subscriptions as OPML`.

These add features and nothing that 0.4.0 users rely on breaks: an existing `app.db` gains the table of articles read when the app starts, without other steps. By `docs/git-workflow/versioning.md` this raises MINOR: 0.5.0.

After this PR is merged, tag the merge commit `v0.5.0` and push the tag; the release workflow builds the installers and publishes the release.

## Verification

- `.github/scripts/check-version.sh v0.5.0` passes: all three files are at 0.5.0.
- `cd backend && uv run pytest`, `cd frontend && npm test && npm run build`, and `cd desktop && npm test && npx tsc --noEmit` pass.
