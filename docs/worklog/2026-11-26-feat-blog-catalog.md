---
title: "feat: recommend the blogs of well-known people"
date: 2026-11-26
branch: feat/blog-catalog
request-source: "project chat, 2026-11-26"
---

## Request

Add the blogs of well-known people to the popular feeds, as one more choice next to the news sites.

## Changes

- The catalog has an eighth topic, `blogs`. The chip is called "Blogs" in English and "블로그" in Korean, with a label in all 19 languages. Each blog is also filed under what it is mostly about (most of them under technology, business, science, or culture), so choosing Technology shows the tech blogs as well as the news sites.
- 84 blogs were added, so the catalog now has 683 feeds. 阮一峰的网络日志, already listed under technology, is now also filed under blogs.
    - English (44): Simon Willison, Daring Fireball, Marginal Revolution, Astral Codex Ten, Noahpinion, Paul Krugman, Pluralistic, Letters from an American, Silver Bulletin, Money Stuff, Martin Fowler, Coding Horror, Krebs on Security, Troy Hunt, The Old New Thing, Julia Evans, Andrej Karpathy, Lilian Weng, Vitalik Buterin, Lenny's Newsletter, The Marginalian, and others.
    - Korean (5): 향로 (이동욱), 기계인간 John Grib, 어쩐지 오늘은 (변성윤), 컴퓨터 vs 책 (박재호), Channy's Blog (윤석찬).
    - Japanese (6): ちきりん, けんすう, 落合陽一, 深津貴之, 山本一郎, 伊藤穰一.
    - Chinese: 5 Simplified (云风, 张鑫旭, 月光博客, 宝玉, 潮流周刊) and 3 Traditional (Mr. Market 市場先生, 閱讀前哨站, KENLU.net).
    - French (6): Korben, Bortzmeyer, Affordance, Ploum, Maître Eolas, sebsauvage.
    - German (3): Isotopp, wirres.net, Indiskretion Ehrensache.
    - Italian (3): Beppe Grillo, Luca De Biase, Manteblog.
    - Spanish (2): Enrique Dans, Microsiervos.
    - Portuguese (2): Manual do Usuário, Blog do Noblat.
    - One each in Polish, Russian, Turkish, Indonesian, and Bengali.
- How they were chosen: 209 candidates were read through the backend's `download`, using the checks the news feeds passed (readable, in the expected script or language). People post less often than newsrooms, so a blog is kept when its newest post is under six months old rather than two weeks. That dropped Wait But Why, Sam Altman, and Gwern. Feeds that refuse the app's requests were dropped too: Seth Godin, Stratechery, Paul Graham (no dates), Bruce Schneier, Terence Tao, and Naver and Brunch blogs.
- Company blogs (NAVER D2), group blogs and outlets (44BITS, Bildblog, Volksverpetzer, Webrazzi, Meio Bit), anonymous boards (はてな匿名ダイアリー), and blogs of people who are not widely known were left out.
- Blogs follow the news feeds of their language, so the list without interests still starts with the main news.
- `README.md` and `README.ko.md` mention the blogs.
- Not done: Vietnamese, Thai, Ukrainian, and Hindi have no blogs. The candidates in those languages were stale, unreadable, or not personal blogs.

## Verification

- `cd frontend && npm test`: 106 tests pass. The new test (blogs are recommended as an interest of their own) was written first and failed for the missing topic. `npm run build` passes.
- `cd backend && uv run pytest`: 32 tests pass.
- Ran the built app in Chrome with a Korean locale: the Blogs chip shows the 5 Korean blogs with "블로그, 기술" under each, and with English chosen it shows the 44 English blogs.
- `frontend/tests/article_reader.py` passes in Chrome.
