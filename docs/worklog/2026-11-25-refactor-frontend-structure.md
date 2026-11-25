---
title: "refactor: structure the frontend like the series"
date: 2026-11-25
branch: refactor/frontend-structure
request-source: "project chat, 2026-11-25"
---

## Request

SOS My Feed was built as the next app of the SOS series, but its layout did not match `sos-my-language`. Bring the whole project in line with that app. This PR is the first step and covers the frontend's structure only; the backend, the desktop shell, and the release workflow follow in a second PR.

## Changes

- Split the single `App.vue` into the layout of the series: `router/` (Vue Router, with `/` and `/settings`), `stores/` (Pinia: `feeds` and `settings`), `views/` (`FeedView`, `SettingsView`), `i18n/` (`en.ts`, `ko.ts`, and `t('key')`), `api.ts`, and `types.ts`. What the pages do is unchanged.
- The library is still kept in the browser's local storage, under the same key and in the same shape (`storage.ts`), so saved subscriptions keep working. Moving it to the backend is left to the next PR.
- Added Vitest with tests for the API helper, the texts of the pages, and both stores, and run them in CI before the build.
- The settings page now has an address of its own, so the server answers a path that is not a built file with the index page. This is the one behavioral change and is a separate `feat:` commit with its own test.
- Renamed `feed-icon.svg` to `favicon.svg`, the package to `sos-my-feed-frontend`, and wrote `index.html` out over several lines, as in the series.
- `AGENTS.md` and `README.md` name the new place of the texts and the frontend test command.

## Verification

- `python3 -m unittest discover -s backend`: 6 tests pass. The new server test failed with a 404 before the change.
- `cd frontend && npm test`: 21 tests pass. They were written first and failed for the missing modules.
- `npm run build`: the type check and the build pass.
- `frontend/tests/article_reader.py` passes in Chrome against the built frontend, including the new check that the settings page opens from its own address after a reload.
