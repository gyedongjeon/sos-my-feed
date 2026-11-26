---
title: "chore: release v0.4.0"
date: 2026-11-26
branch: chore/release-v0.4.0
request-source: "project chat, 2026-11-26"
---

## Request

Prepare the release of what was merged since v0.3.0.

## Changes

Raise the version from 0.3.0 to 0.4.0 in the three files that carry it (`backend/pyproject.toml`, `frontend/package.json`, `desktop/package.json`) and their lock files.

Merged since v0.3.0:

- #11 `docs: add screenshots of the app to the READMEs`.
- #12 `feat: recommend popular feeds by language and interest`.
- #13 `feat: recommend the blogs of well-known people`.
- #14 `feat: add the English editions of outlets from other countries` — also names the app in a form more sites accept, and adds feeds found at their real addresses.
- #15 `feat: show pictures and videos in the reader, and open the original page`.

These add features and nothing that 0.3.0 users rely on breaks, so by `docs/git-workflow/versioning.md` this raises MINOR: 0.4.0.

After this PR is merged, tag the merge commit `v0.4.0` and push the tag; the release workflow builds the installers and publishes the release.

## Verification

- `.github/scripts/check-version.sh v0.4.0` passes: all three files are at 0.4.0.
- `cd backend && uv run pytest`, `cd frontend && npm test && npm run build`, and `cd desktop && npm test && npx tsc --noEmit` pass.
