---
title: "feat: show the pages in the series' 19 languages"
date: 2026-11-25
branch: feat/page-languages
request-source: "project chat, 2026-11-25"
---

## Request

Offer every major language for the pages, the same ones as `sos-my-english` of the SOS series.

## Changes

- The pages are written in the 19 languages of `sos-my-english` (and `sos-my-language`): English, Korean, Japanese, Simplified and Traditional Chinese, Spanish, French, German, Italian, Portuguese, Polish, Russian, Ukrainian, Turkish, Vietnamese, Thai, Indonesian, Hindi, and Bengali. 17 files were added in `frontend/src/i18n/`.
- `frontend/src/languages.ts` lists them with their own names and the browser language tags each stands for. The first visit starts in the browser's language, with region- and script-specific tags first (`zh-TW` and `zh-HK` are Traditional Chinese, `zh-CN` Simplified) and English for any other language. The selector under Settings offers all of them.
- Languages are kept by code (`ja`, `zh-Hans`, ...), and `/api/settings` accepts each of them; dates in the list are formatted in the chosen language.
- English and Korean were written by hand. The other 17 were translated by AI and not checked by native speakers; the README says so and welcomes corrections. The backend's error messages and the desktop app's dialogs stay in English, as in `sos-my-language`.
- `README.md`, `README.ko.md`, and `AGENTS.md` describe the languages and how to add one.

## Verification

- `cd backend && uv run pytest`: 32 tests pass. The test that every language can be chosen was written first and failed.
- `cd frontend && npm test`: 94 tests pass. The tests for the list of languages, the browser language matching, and the files of texts (one per language, every key, the same names to fill in) were written first and failed. `npm run build` passes.
- `frontend/tests/article_reader.py` passes in Chrome.
- Looked at screenshots of the settings page in Vietnamese and German at 375 pixels and in Japanese at 990, and of the reader's guide in Hindi: no text overflows.
