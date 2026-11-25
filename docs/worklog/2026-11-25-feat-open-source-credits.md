---
title: "feat: credit open-source work under Settings"
date: 2026-11-25
branch: feat/open-source-credits
request-source: "project chat, 2026-11-25"
---

## Request

Add the "Open source" section of the settings page, as `sos-my-interview` has it (shown with a screenshot of the same section in `sos-my-language`).

## Changes

- The settings page ends with an **Open source** card: a line saying the app is MIT-licensed open source, the work it is built with (Bricolage Grotesque, Vue, Vue Router, Pinia, daisyUI, Tailwind CSS, uv) with each copyright and a license badge, and a link to the full license texts at `/THIRD_PARTY_NOTICES.txt`. Markup and list are those of `sos-my-interview`.
- The list is in `frontend/src/credits.ts`, and a test checks that every holder it names is in `public/THIRD_PARTY_NOTICES.txt`, so the two cannot drift apart.
- The three texts are in all 19 languages, taken from `sos-my-interview` with the app's name changed.
- `README.md` and `README.ko.md` mention the section.

## Verification

- `cd frontend && npm test`: 96 tests pass; the credits test was written first and failed for the missing module. `npm run build` passes.
- `cd backend && uv run pytest`: 32 tests pass.
- `frontend/tests/article_reader.py` passes in Chrome, now also checking the section, a credit, and that the license link serves the notices file.
- Looked at screenshots of the section in Korean at 990 pixels and in German at 375: it matches the one of `sos-my-language`, and long names wrap without overflow.
