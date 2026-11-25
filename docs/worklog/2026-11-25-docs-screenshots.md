---
title: "docs: add screenshots of the app to the READMEs"
date: 2026-11-25
branch: docs/screenshots
request-source: chat session, 2026-11-25
---

## Request

The READMEs had no pictures of the app. Add screenshots, kept in `docs/images/` as in
`sos-my-language`.

## Changes

- `docs/images/` has four screenshots, 1200 pixels wide:
  - `feed.png` and `feed.ko.png`: My feed, with the articles of three feeds in one list, in
    English and in Korean.
  - `reader.png` and `reader.ko.png`: the first of those articles open in the reader, on sepia
    paper with two pages side by side and the menu shown.
- `README.md` and `README.ko.md` each show the list under the introduction and the reader at the
  start of "How it works" (`사용 방법`).
- The feeds and articles are made up for the pictures (fictional blogs and news on `example.org`,
  `example.com`, and `example.net`), so no third-party text is shown. They were taken with
  Playwright and Chrome against the real backend serving the built frontend, with the feed and
  article fetching replaced by that sample content in the manner of
  `frontend/tests/article_reader.py`, and a new data folder for each language. The script was a
  one-off and is not part of this change.

## Verification

- Each picture was looked at after it was taken: the pages are in the language meant, the list
  ends on a whole card, the reader shows two pages with a heading, and nothing personal is on
  them.
- The four image links of the two READMEs point at files that exist in `docs/images/`.
- No code changed, so the test suites were not run.
- Not verified: how the READMEs are drawn on GitHub with the pictures.
