---
title: "feat: add the English editions of outlets from other countries"
date: 2026-11-26
branch: feat/english-editions
request-source: "project chat, 2026-11-26"
---

## Request

Many outlets outside the English-speaking world, such as DW (see DW's list of RSS feeds), publish in English as well. Find them and add them to the English feeds of the catalog. The request covered European outlets, Korean outlets that can be read in English, and the English news of Japanese outlets.

## Changes

- The English section of `frontend/src/catalog.ts` has 100 more feeds, so the catalog now has 783. The new feeds are sorted into the English list by topic, ahead of the blogs. Lesser-known names carry their country, e.g. "Notes from Poland" or "Dawn (Pakistan)".
- Europe:
    - DW's English sections, taken from DW's own list of feeds: top stories, world, Germany, Europe, Asia, business, science, environment, culture, sports.
    - Major outlets: DER SPIEGEL International, Le Monde in English, RFI English, El País in English, ANSA English, and France 24 and Euronews sections.
    - Public broadcasters: Yle News, Radio Sweden, Radio Prague International, ERR News, LRT, LSM, RTÉ.
    - The Local in nine countries.
    - Smaller national outlets and regional sites: DutchNews.nl, NL Times, The Copenhagen Post, Iceland Review, Helsinki Times, Notes from Poland, Hungary Today, Daily News Hungary, Greek Reporter, Cyprus Mail, Times of Malta, Portugal Resident, Irish Times, Balkan Insight, POLITICO Europe, Euractiv.
    - Ukraine and Russia: Kyiv Post, Ukrainska Pravda English, Ukrinform English, Meduza in English, The Moscow Times, Novaya Gazeta Europe in English.
    - Türkiye: Daily Sabah, Turkish Minute.
- Korea: The Korea Times, KBS World, Yonhap News Agency (national, culture, sports, next to the main feed already listed), BusinessKorea, KED Global (The Korea Economic Daily), NK News, Korea Pro, Daily NK.
- Japan: The Japan Times sections (opinion, business, culture, life, sports, next to the main feed already listed), Nikkei Asia, nippon.com, JAPAN Forward (Sankei), SoraNews24, Unseen Japan.
- Elsewhere: Taipei Times, RTHK English, Sixth Tone, The Straits Times, CNA, Bangkok Post, VnExpress International, Antara English, Rappler, Dawn, Haaretz, The Times of Israel, Al-Monitor, The National, Buenos Aires Times, MercoPress, Mexico News Daily.
- How they were checked: about 200 candidates were read through the backend's `download` with the checks of the other news feeds: readable, newest article under two weeks old, titles in English, and not mostly repeating a feed already listed. A feed without dates was kept when its newest articles were checked by hand to be current (Nikkei Asia, KED Global, Sixth Tone, NL Times).
- Left out:
    - Feeds that refuse the app's requests or are broken: NHK WORLD-JAPAN, Kyodo News, The Japan News (Yomiuri), The Asahi Shimbun AJW, The Mainichi, Jiji Press, Japan Today, Korea JoongAng Daily, The Dong-A Ilbo, The Chosun Ilbo English, Arirang, swissinfo.ch, The Kyiv Independent, TVP World, Ekathimerini.
    - Hankyoreh English, whose address now serves the Korean feed.
    - Duplicates: The Japan Times · News and two Korea Times sections repeat feeds already listed.
    - Sources that are not outlets of those countries: Korea Economic Institute of America, Anime News Network, The Korea Daily (US), and a travel guide.

## Verification

- `cd frontend && npm test`: 106 tests pass. The catalog tests check that every new address is unique, already in the form subscribing writes, and filed under known topics. `npx vue-tsc --noEmit` passes.
- `cd backend && uv run pytest`: 32 tests pass.
- Read every added feed on 2026-11-26 as described above, and looked at the first articles of the feeds whose title is in another language (Le Monde in English, Novaya Gazeta Europe) to confirm they are in English.
