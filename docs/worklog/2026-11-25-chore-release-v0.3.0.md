---
title: "chore: release v0.3.0"
date: 2026-11-25
branch: chore/release-v0.3.0
request-source: "project chat, 2026-11-25"
---

## Request

Prepare the release of what was merged since v0.2.0.

## Changes

Raise the version from 0.2.0 to 0.3.0 in the three files that carry it (`backend/pyproject.toml`, `frontend/package.json`, `desktop/package.json`) and their lock files.

Merged since v0.2.0:

- #5 `refactor: structure the frontend like the series` — router, Pinia stores, views, i18n, and Vitest.
- #6 `feat: run on FastAPI, SQLite, and Electron` — subscriptions and settings move from the browser to SQLite; the desktop app becomes an Electron window that updates itself.
- #7 `feat: read articles like the Re:Leaf reader` — taps on either side turn pages, one or two pages, six paper colours, view settings, Markdown download, and a first-use guide.
- #8 `feat: show the pages in the series' 19 languages`.
- #9 `feat: credit open-source work under Settings`.

#6 breaks what 0.2.0 users rely on: their subscriptions are not carried over, and the 0.2.0 app does not update itself. By "Before 1.0.0" in `docs/git-workflow/versioning.md` a breaking change raises MINOR, so this is 0.3.0. The README tells 0.2.0 users to remove the old app and subscribe again.

After this PR is merged, tag the merge commit `v0.3.0` and push the tag; the release workflow builds the macOS `.dmg` and update `.zip` and the Windows installer and publishes the release. This is the first run of that workflow in this repository.

## Verification

- `.github/scripts/check-version.sh v0.3.0` passes: all three files are at 0.3.0.
- `cd backend && uv run pytest`, `cd frontend && npm test && npm run build`, and `cd desktop && npm test && npx tsc --noEmit` pass.
