---
title: "ci: update the GitHub Actions to versions that run on Node.js 24"
date: 2026-11-26
branch: chore/update-actions
request-source: "project chat, 2026-11-26"
---

## Request

The v0.4.0 release run warned that `actions/checkout@v4`, `actions/setup-node@v4`, `actions/upload-artifact@v4`, and `astral-sh/setup-uv@v5` target Node.js 20, which GitHub has deprecated and now forces onto Node.js 24. Update them.

## Changes

In `.github/workflows/ci.yml` and `.github/workflows/release.yml`:

| Action | From | To |
| :--- | :--- | :--- |
| `actions/checkout` | v4 | v7 |
| `actions/setup-node` | v4 | v7 |
| `actions/upload-artifact` | v4 | v7 |
| `astral-sh/setup-uv` | v5 | v10 |

None of the breaking changes in between affect these workflows:

- `setup-node` v5–v6 changed automatic caching; every use here sets `cache: npm` and its lock files explicitly.
- `setup-uv` v6 stopped activating the virtual environment by default; the backend runs through `uv run`. v9 stopped pruning the cache, and v10 turns the automatic cache off for `pull_request_target`, `workflow_run`, and `release` events, none of which start these workflows.
- `checkout` v6 keeps its credentials in a separate file; no step reads them.
- `upload-artifact` v7 adds direct uploads of unzipped files, which are off unless `archive: false` is set.

## Verification

- The CI run on this PR passes without the Node.js 20 warnings.
- The release workflow is checked on the next release tag.
