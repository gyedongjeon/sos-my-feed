---
title: "feat: show pictures and videos in the reader, and open the original page"
date: 2026-11-26
branch: feat/reader-media
request-source: "project chat, 2026-11-26"
---

## Request

Taking the Re:Leaf reader as the model again, show an article's pictures in the reader (BBC News, for example). Play its videos in the reader if that can be done, or else lead to the original page. And since some readers want the site's own page rather than the reader view, add a way to open it.

## Changes

- **Extraction** (`backend/app/articles.py`). Besides paragraphs, headings, and quotations, the parser keeps an article's pictures and videos where they stand.
    - **Blocks:** a picture becomes an `image` block (`src`, `alt`, and its caption as `text`), and a video becomes a `video` block (`src` and caption). The answer's blocks are a union discriminated by `kind`, so text blocks are answered as before.
    - **Picture size:**
        - A picture is taken at a reading size from the sizes it offers: its `srcset`, its `<picture>`'s `<source>`s, a `width=`/`w=` in the address times a `dpr=`, and its `width`.
        - The smallest size at least 800 pixels wide wins, or else the widest. A source whose width is unknown is taken as the original.
        - Lazily loaded pictures (`data-src`, `data-srcset`, …) are read from their real addresses.
    - **Pictures left out:**
        - a picture under 200 pixels wide, or with a side under 100 (writers' portraits, icons, tracking pixels);
        - a picture inside a link to another page (Yonhap's reporter photo, The Verge's author);
        - inline images and SVG;
        - a picture already shown in the same article, which is kept once.
    - **Captions:**
        - A `<figcaption>` becomes the caption of the figure's picture or video.
        - Other text inside a figure or a BBC picture/media block (credits, "Play video") is not read as the article's text, except a quotation set in a figure.
        - Text only screen readers get (`visually-hidden`, `sr-only`) is left out, such as BBC's "Image caption, ".
    - **Videos:**
        - A YouTube or Vimeo `<iframe>` is kept as a player address rebuilt from the video's id, `youtube-nocookie.com/embed/<id>` or `player.vimeo.com/video/<id>`. Any other frame is still dropped.
        - A `<video>`, or a BBC media player, becomes a video with no player: it plays only with the site's own scripts.
    - **Lead picture:** when the article shows no picture or video, the page's `og:image` leads it, as Re:Leaf brings in the header picture.
    - **Page address:** addresses are read against the address the page was found at, after redirects.
- **Pictures through the backend** (`GET /api/image?url=`). The reader does not load pictures from the sites itself. The backend reads them with `fetch_public`, as it reads articles, so the project's rule that only the backend fetches, and only public addresses, still holds. Only JPEG, PNG, GIF, WebP, and AVIF are passed on (not SVG or HTML), and they are cached for a day.
- **Reader** (`ArticleReader.vue`):
    - **Picture:** shown with its caption, in a frame 55% of a page high, so the pages do not move as pictures load. A picture that fails to load is left out.
    - **YouTube/Vimeo:** shows a "Play video" button, and the player is loaded only when it is pressed.
    - **Other videos:** show a "Watch on the original page" link with the caption, as Re:Leaf does.
    - **Menu:** gets **Open the original page**. The note shown when only the feed's summary could be read links the page too.
- **List:** each article in the list has an icon that opens its page on the site. The card became a box holding the button that opens the reader and this link, since a link cannot sit inside a button. The desktop app already opens such links in the regular browser.
- **Markdown:** the export writes pictures as `![alt](address)` with the caption, and videos as links (the player, or the article's page).
- **Texts:** four new texts in all 19 languages (open the original page, play video, watch on the original page, video).
- **READMEs:** `README.md` and `README.ko.md` describe it.
- **Tidying:** a `refactor:` commit first made the parser keep what holds inside an element as one named state, so that new kinds of state (in a figure, in a caption, in a link) could be added.
- **Not done:**
    - BBC's own videos cannot be played in the reader: the player is built by BBC's scripts and the page holds no video address.
    - Le Monde's pages answer the app with a "required part of this site couldn't load" page; they did so before this change too.
    - Some sites still bring in a few extra pictures (TechCrunch's author, NHK's video promotion) or trailing links (Electrek).

## Verification

- `cd backend && uv run pytest`: 47 tests pass. Each new behavior was given a failing test first:
    - BBC-style picture with caption and credit;
    - lazy picture and pixel;
    - BBC video;
    - YouTube/Vimeo and other frames;
    - `og:image` lead;
    - address after redirect;
    - the image endpoint, and its refusal of non-pictures;
    - the answer's shape;
    - a quotation in a figure;
    - the Guardian's sources;
    - the widest size when none reaches 800;
    - portraits and small pictures;
    - a picture shown twice.
- `cd frontend && npm test`: 108 tests pass, with new tests for Markdown pictures and videos and for the picture's address. `npm run build` passes.
- `frontend/tests/article_reader.py` passes in Chrome. It now also opens an article with a picture, a site video, and a YouTube video, and checks the following. Changing the expected caption made it fail, as it should.
    - The picture is read through `/api/image`, loads, and fits on a page, with its caption.
    - The site video links the article's page.
    - No player is loaded before "Play video" is pressed.
    - The menu and the list link the original page in a new window.
- Read real articles from BBC News and Sport, the Guardian, The Verge, Yonhap, Hankyoreh, DER SPIEGEL, NHK, Simon Willison, and TechCrunch: their photos come with their captions, and portraits, duplicates, and promotions are left out as listed above.
- In Chrome against the real sites:
    - A BBC Sport article showed its photos and the "Watch on the original page" link under the video's caption.
    - An Electrek article's YouTube video played in the reader.
    - Each article in the list showed the icon to its page.
