---
title: "feat: read feed articles in the app"
date: 2026-11-25
branch: feat/article-reader
request-source: "project chat, 2026-11-25"
---

## Request

Let readers open feed stories inside SOS My Feed and turn pages like an ebook, using Re:Leaf as a reference.

## Changes

- Extract the existing public URL fetcher in a separate structural commit and use it for article requests. Extract plain paragraphs on the server so the reader never needs to execute publisher scripts.
- Open article cards in a single-page reading view with keyboard navigation, a page count, and a saved text size. Closing the view returns focus to the selected card. Show the saved summary when extraction fails.
- Add English and Korean controls and usage instructions. Include the extractor in both desktop installers and the runnable ZIP.

## Verification

- Ran the offline backend tests, frontend clean install, type check, and production build.
- Added failing cases for article text extraction and related-news filtering before implementing the corresponding behavior. Checked extraction on public BBC News and Mozilla Blog articles.
- Exercised the built UI in Chrome at desktop and phone widths. Verified page turns through the final page, font resizing, cached-summary fallback, and return to the original card. Reproduced the focus regression and verified the fix in the browser test.
