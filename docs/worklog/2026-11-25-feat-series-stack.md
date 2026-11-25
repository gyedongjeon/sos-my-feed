---
title: "feat: run on FastAPI, SQLite, and Electron"
date: 2026-11-25
branch: feat/series-stack
request-source: "project chat, 2026-11-25"
---

## Request

Bring the whole project in line with `sos-my-language`, the previous app of the SOS series, and keep the data in SQLite as that app does. The frontend's structure was aligned in the PR before this one (`refactor/frontend-structure`), which this branch builds on; this PR covers the backend, where the data is kept, the desktop app, the release workflow, and the documents. Carrying over subscriptions saved by earlier versions was explicitly not asked for: the app has a single user so far.

## Changes

- **Backend layout** (structural, its own `refactor:` commit): the modules moved to `backend/app/` and the tests to `backend/tests/`, run with pytest in a uv project (`pyproject.toml`, `uv.lock`, `.python-version`).
- **FastAPI and SQLite**: the standard-library server is replaced by a FastAPI app. Subscriptions, their articles, and the settings are kept in `backend/data/app.db` instead of the browser's local storage. New endpoints: `GET/POST /api/feeds`, `POST /api/feeds/refresh`, `DELETE /api/feeds/{id}`, `GET/PUT /api/settings`, `GET /api/health`; `POST /api/article` stays. Fetching still goes through `fetch_public` only, which refuses addresses that are not public.
- **Frontend**: the `feeds` and `settings` stores load from and save to the backend. A setting or a removal that cannot be saved is not applied and is reported in the reader's language. `storage.ts` is gone.
- **Desktop**: the Swift window (macOS) and the Inno Setup installer that opened the default browser (Windows) are replaced by the Electron shell of the series. It starts the backend with a bundled uv on a free port, shows it in a window on both systems, keeps everything in the app's own folder in the user's profile, and offers new releases. The microphone handling of the language app was left out; the window refuses every permission a page can ask for.
- **CI and release**: `ci.yml` runs the backend, frontend, and desktop suites, the Chrome reading test, and a Windows job that starts the server on the shipped Python and builds the installer. `release.yml` checks the tag against the three version files, publishes the `.dmg` and the update `.zip`, then adds the Windows installer. The checks moved to `.github/scripts/`. `installers.yml` and the runnable ZIP are gone.
- **Versions** are written in three files that must match (`backend/pyproject.toml`, `frontend/package.json`, `desktop/package.json`); all are at 0.2.0 and are not raised here.
- **Documents**: `README.md`, `README.ko.md`, `AGENTS.md`, `versioning.md`, and `branching-strategy.md` describe the new stack; third-party notices were added.
- Not done: screenshots for the README (`docs/images/`), which the language app has.

Saved data of 0.2.0 and earlier is not read by this version, and those installed apps do not update themselves; the README says so. By `versioning.md` this is a breaking change, to be reflected when the next version is chosen.

## Verification

- `cd backend && uv run pytest`: 30 tests pass. The tests for the database, subscriptions, settings, the article endpoint, and serving the frontend were written first and failed for the missing modules.
- `cd frontend && npm test`: 27 tests pass; the store tests were rewritten against a fake backend first and failed. `npm run build` passes.
- `cd desktop && npm test`: 46 tests pass; `npx tsc --noEmit` passes.
- `frontend/tests/article_reader.py` passes in Chrome against the built frontend and the FastAPI backend (page turns, text size saved through the API, summary fallback, focus return, the settings page reloaded from its own address).
- `.github/scripts/check-version.sh v0.2.0` and `.github/scripts/start-server-check.sh` pass on macOS.
- `npm run package` built the macOS app; the packaged app was opened once: the first launch installed the packages, the backend answered `/api/health`, the page loaded and saved its first settings, and quitting stopped the backend.
- Not verified locally: the Windows installer and the release workflow. The Windows job of CI covers the former on this PR; the latter runs only for a version tag.
