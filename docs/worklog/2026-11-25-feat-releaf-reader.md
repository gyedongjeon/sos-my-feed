---
title: "feat: read articles like the Re:Leaf reader"
date: 2026-11-25
branch: feat/releaf-reader
request-source: "project chat, 2026-11-25"
---

## Request

The reader was asked to work like Re:Leaf (the browser extension of the same author), but the first version kept little of it: pages and a text size only. Bring it as close to Re:Leaf as possible. Named in the request: changing the background color, the two-page view, and turning a page at once with a tap on the left or right; "and so on" for the rest.

## Changes

What Re:Leaf has was read from its source, and the reader now has the same:

- **Tap navigation**: a tap or click on the left or right fifth of the window turns the page; a tap in the middle shows or hides the menu. A drag (text selection) or a long press is not a tap. The arrow keys still turn pages; Page Up, Page Down, and the space bar were added.
- **Two-page view**: one page or two side by side, 60 pixels apart as in Re:Leaf. Pages are moved with a transform instead of scrolling, so the last page of an odd number of columns needs none of Re:Leaf's overscroll correction. Below 720 pixels of width one page is shown whatever was chosen.
- **Background colors**: the six themes of Re:Leaf with its colors (white, sepia, mint, forest, gray, dark), independent of the app's light and dark theme.
- **View settings**: sliders for text size (14–32), line spacing (1.2–2.4), vertical margin (40–120), and horizontal margin (20–80), with Re:Leaf's ranges and defaults. The page follows a slider while it is dragged, and the choice is saved when it is let go.
- **Menu bar** at the bottom, out of sight while reading: settings, page counter, Markdown download, close. It is in sight for three seconds when an article opens. Added to Re:Leaf's: buttons for the previous and next page beside the counter, so that a screen reader has them; the menu also comes into sight when reached with the Tab key.
- **Markdown download** with Re:Leaf's front matter and file name rules.
- **First-use guide** in three steps with "Don't show again".
- **Text structure**: the backend now answers an article as blocks (`paragraph`, `heading`, `quote`) instead of plain paragraphs, so headings and quotations look like ones. `POST /api/article` answers `blocks` in place of `paragraphs`.
- **Settings**: `reader_theme`, `reader_line_height`, `reader_margin_v`, `reader_margin_h`, `reader_pages`, and `reader_tutorial_seen` were added to `/api/settings`, and `reader_size` now starts at 14. They are kept in SQLite like the others.

Left out, and why:

- **Images, links, and code blocks** in the text. The backend takes text only and the reader loads nothing from the publisher; showing images would mean loading them from the publisher's servers. This is the largest remaining difference from Re:Leaf.
- **Video placeholders** and Re:Leaf's page-specific extraction rules, which depend on the live page of a browser.
- The **Merriweather and Inter web fonts**: the app loads nothing from font servers, so the serif fonts of the system are used.
- The menu and the settings follow the app's theme instead of Re:Leaf's fixed white glass.

## Verification

- `cd backend && uv run pytest`: 31 tests pass. The tests for the kinds of blocks and for the new settings and their limits were written first and failed.
- `cd frontend && npm test`: 42 tests pass. The tests for tap zones, what counts as a tap, the number of pages (one and two per view, an odd number of columns, rounding), the Markdown text and file name, and trying and saving the reader's layout were written first and failed. `npm run build` passes.
- `frontend/tests/article_reader.py` passes in Chrome: the guide on the first article and its absence after a reload, a tap on the right and on the left, the left arrow key, the menu shown and hidden by a tap in the middle, sepia paper, text size from the slider, two pages side by side, Escape closing the settings before the reader, one page in a 375-pixel window, the last page holding the end of the text, focus returning to the article's card, the summary fallback, and the Markdown download's file name.
- Looked at screenshots of the guide, the settings over a sepia two-page view, and dark paper while reading, at 1200×800.
- Not verified: the download and the taps inside the packaged Electron window, and touch on a real touch screen (taps were made with the mouse).
