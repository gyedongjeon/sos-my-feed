---
title: "feat: add the English editions of outlets from other countries"
date: 2026-11-26
branch: feat/english-editions
request-source: "project chat, 2026-11-26"
---

## Request

Many outlets outside the English-speaking world, such as DW (see DW's list of RSS feeds), publish in English as well. Find them and add them to the English feeds of the catalog. The request covered European outlets, Korean outlets that can be read in English, and the English news of Japanese outlets.

Then, since many sites refused the app: (1) try asking with a name like a browser's, and adopt the form that works; (2) find the real feed addresses of the outlets whose guessed addresses did not exist.

## Changes

- The English section of `frontend/src/catalog.ts` has 108 more feeds, and 12 more feeds were added in other languages, so the catalog now has 803. The new feeds are sorted into the English list by topic, ahead of the blogs. Lesser-known names carry their country, e.g. "Notes from Poland" or "Dawn (Pakistan)".
- Europe:
    - DW's English sections, taken from DW's own list of feeds: top stories, world, Germany, Europe, Asia, business, science, environment, culture, sports.
    - Major outlets: DER SPIEGEL International, Le Monde in English, RFI English, El País in English, ANSA English, and France 24 and Euronews sections.
    - Public broadcasters: Yle News, Radio Sweden, Radio Prague International, ERR News, LRT, LSM, RTÉ.
    - The Local in nine countries.
    - Smaller national outlets and regional sites: DutchNews.nl, NL Times, The Copenhagen Post, Iceland Review, Helsinki Times, Notes from Poland, Hungary Today, Daily News Hungary, Greek Reporter, Cyprus Mail, Times of Malta, Portugal Resident, Irish Times, Balkan Insight, POLITICO Europe, Euractiv.
    - Ukraine and Russia: Kyiv Post, Ukrainska Pravda English, Ukrinform English, Meduza in English, The Moscow Times, Novaya Gazeta Europe in English.
    - Türkiye: Daily Sabah, Turkish Minute.
- Korea: The Hankyoreh English, The Kyunghyang Shinmun English, The Korea Times, KBS World, Yonhap News Agency (national, culture, sports, next to the main feed already listed), BusinessKorea, KED Global (The Korea Economic Daily), NK News, Korea Pro, Daily NK.
- Japan: The Asahi Shimbun AJW, The Japan Times sections (opinion, business, culture, life, sports, next to the main feed already listed), Nikkei Asia, Japan Today, nippon.com, JAPAN Forward (Sankei), SoraNews24, Unseen Japan, GaijinPot.
- Ukraine also gets The Kyiv Independent. Elsewhere: Focus Taiwan (CNA), Taipei Times, RTHK English, Sixth Tone, The Straits Times, CNA, Bangkok Post, VnExpress International, Antara English, Rappler, Dawn, Haaretz, The Times of Israel, Al-Monitor, The National, Buenos Aires Times, MercoPress, Mexico News Daily.
- The request name. The backend's `fetch_public` now names the app `Mozilla/5.0 (compatible; SOS-My-Feed/0.1; +https://github.com/gyedongjeon/sos-my-feed)` instead of `SOS-My-Feed/0.1`, the form feed readers use. Every candidate that had answered with a refusal was tried three ways:
    - the old name;
    - this form, which opened 8 more (Japan Today, GaijinPot, News18 Hindi, and others; 7 of them fresh);
    - a Chrome browser's name, which opened 1. Seth Godin, Stratechery, and Schneier answer 403 to a browser's name sent by a script.

  The compatible form still says which app is asking, so the app does not pretend to be a browser. Adding an `Accept` header changed nothing.
- Most refusals were not about the name. NHK WORLD, Kyodo, Jiji, Dong-A, and others answered 404, because the guessed addresses do not exist. A few sites (Seth Godin, Schneier, Yahoo! Japan) answer curl with 200 but Python with 403 under the same name and headers; they seem to recognise Python's connection itself, which no name changes.
- Real addresses. Feed links were read from the outlets' home and RSS pages:
    - Hankyoreh English (`/rss/english_edition/`), Kyunghyang English (from its RSS help page), The Kyiv Independent, Focus Taiwan, Liputan6's sections, MGR Online, and Dân trí's technology and science sections.
    - The Asahi Shimbun AJW (`/ajw/feed_msn/`) came from a feed directory and was checked to be AJW's own current English articles on asahi.com.
    - No official feed was found for NHK WORLD-JAPAN (only an audio podcast), Kyodo (now Japan Wire), Jiji, Korea JoongAng Daily, or The Dong-A Ilbo.
- How they were checked: about 200 candidates were read through the backend's `download` with the checks of the other news feeds: readable, newest article under two weeks old, titles in English, and not mostly repeating a feed already listed. A feed without dates was kept when its newest articles were checked by hand to be current (Nikkei Asia, KED Global, Sixth Tone, NL Times).
- Left out:
    - Feeds with no official address found, or that refuse the app, or are broken: NHK WORLD-JAPAN, Kyodo News, The Japan News (Yomiuri), The Mainichi (malformed XML), Jiji Press, Korea JoongAng Daily, The Dong-A Ilbo, The Chosun Ilbo English, Arirang, swissinfo.ch (410), TVP World, Ekathimerini.
    - Aaj Tak's `/rss`, which repeats the Aaj Tak feed already listed, and Zee 24 Ghanta, whose newest article was 36 days old.
    - Duplicates: The Japan Times · News and two Korea Times sections repeat feeds already listed.
    - Sources that are not outlets of those countries: Korea Economic Institute of America, Anime News Network, The Korea Daily (US), and a travel guide.

## Verification

- `cd frontend && npm test`: 106 tests pass. The catalog tests check that every new address is unique, already in the form subscribing writes, and filed under known topics. `npx vue-tsc --noEmit` passes.
- `cd backend && uv run pytest`: 33 tests pass. The new test (the app names itself in the compatible form) was written first and failed on the old name.
- Read every added feed on 2026-11-26 as described above, and looked at the first articles of the feeds whose title is in another language (Le Monde in English, Novaya Gazeta Europe) to confirm they are in English.
