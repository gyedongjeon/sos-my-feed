---
title: "feat: recommend popular feeds by language and interest"
date: 2026-11-25
branch: feat/feed-catalog
request-source: "project chat, 2026-11-25"
---

## Request

Gather the RSS feeds of well-known news outlets and organise them, so that the first screen recommends feeds by the reader's language and interests. Copying and pasting each feed address one at a time is too much work.

## Changes

- `frontend/src/catalog.ts` lists 599 feeds in all 19 languages of the pages, 76 in English, 46 in Korean, and at least 21 in every language. Each feed has a name, an address, the language it is written in, and one or more of seven topics: top stories, world, business, technology, science, sports, culture. `recommend(language, interests)` returns the feeds in a language on any of the chosen interests, in the catalog's order, or every feed in the language when no interest is chosen.
- How the list was made: about 860 candidate addresses were read through the backend's own `download` on 2026-11-25 and 2026-11-26. The candidates were the main pages and sections of major outlets, public broadcasters, news agencies, the BBC, DW, VOA, and RFI language services, and leading business, tech, science, sports, and culture sites. A feed was kept only if all of these held:
    - it was readable and had articles, and its newest article was under two weeks old;
    - its titles are in the expected script or language (a check by characters and common words);
    - it does not mostly repeat another kept feed in the same language (a section that returns the front page's articles).

  The last pass read every kept feed again. Dropped, among others: NHK's old RSS (stale since mid-2025), Yahoo! Japan, Livedoor, the Wall Street Journal, CNN (stale since 2024), the Washington Post (timed out), Corriere della Sera, La Gazzetta dello Sport, Sina, People's Daily, and RTVE. Also dropped: unofficial mirrors of other sites' feeds (feedx.net, wor.jp), an address carrying an API key (Kompas), and a sitemap passed off as a feed (Tirto).
- Within a language the feeds are ordered by topic (top stories first), so the list without interests starts with the main news.
- The catalog is a file of the frontend, not a table or endpoint of the backend. It is fixed data shipped with the app, and the types check its languages and topics. Subscribing still goes through `POST /api/feeds`, so every fetch still goes through `fetch_public`.
- `feeds.subscribeAll` subscribes to several feeds at once: it skips those already subscribed, asks for the others together so one slow site does not hold up the rest, adds them in the order chosen, names the ones that could not be read, and then shows every feed.
- `FeedCatalog.vue` (**Popular feeds**) has a language selector, which starts at the language of the pages, interest chips, a two-column checklist with host and topics, **Select all**, and **Subscribe (n)**. The chips show only the topics the chosen language has feeds on, and only chosen interests among them count, so changing the language never leaves an empty list. Feeds already subscribed are ticked, greyed out, and marked "Subscribed".
- The feed page shows the catalog where the "Subscribe to your first feed" card was, until there is a subscription. After that, **Browse popular feeds** next to **Refresh** shows or hides it. The empty card now only says "No articles yet", so `feed.hint` was removed.
- 16 new texts in all 19 languages. `README.md` and `README.ko.md` describe the catalog in Features and First setup.
- Not done: the interests are not saved, and a subscribed feed takes the title the feed gives itself (as with pasted addresses), not the catalog's name. Some of those titles are long (e.g. Hankyoreh's). No automatic check that the feeds still work: tests cannot reach the network.

## Verification

- `cd frontend && npm test`: 105 tests pass. The catalog tests (feeds in every language; unique addresses already in the form subscribing writes; known topics; recommending by language, interests, and order) and the three `subscribeAll` tests were written first and failed for the missing module and action. `npm run build` passes.
- `cd backend && uv run pytest`: 32 tests pass. `frontend/tests/article_reader.py` passes in Chrome.
- Ran the built app against the real network in Chrome with a Korean locale. On the empty first screen, Popular feeds showed the 46 Korean feeds. Choosing Technology and Science narrowed the list to 11. Select all and Subscribe (11) subscribed all eleven, showed "고른 피드를 구독했습니다.", and listed their articles. Browse popular feeds, with the language switched to Japanese, showed the Japanese feeds.
