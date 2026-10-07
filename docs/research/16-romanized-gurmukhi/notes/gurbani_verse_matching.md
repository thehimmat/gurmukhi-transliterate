# Gurbani databases and search APIs for matching romanized or OCR'd lines to canonical verses

Research date: 2026-10-06. Method notes: GitHub source files were read from raw.githubusercontent.com (primary). The live BaniDB API (api.banidb.com/v2, version 2.10.3) was called directly. The Shabad OS SQLite (npm `@shabados/database@5.0.0-next.0`) was downloaded and inspected locally. A prototype matcher was built on it and benchmarked. The network egress proxy blocked banidb.com, sikher.com, readsggs.com, opensource.org, archive.org and api.gurbaninow.com. Claims about those sites come from search-engine snippets and are marked as such.

## 1. BaniDB API (api.banidb.com, Khalis Foundation): search types, endpoints, response fields, terms, licence, rate limits

### Takeaway
BaniDB is a free REST API that needs no key. It has nine search types (0 to 8), including two romanized ones (4 and 7). Both are only substring matches on a precomputed first-letters-in-English column (`FirstLetterEng`), and results come back in ShabadID order, not ranked by relevance. So the API can supply candidate verses, but it does not do fuzzy alignment. The data is covered by restrictive ToS (attribution and logo required, data used "in its entirety") plus NPOSL-3.0. Rate limits are per IP: 250 requests/min on /search and 100/min on most other routes.

### Cited Findings
**Endpoints** (Express routes in `api/routes/index.js`, dev branch):
- `GET /v2/search/:query`, `/search-results/:VerseIds`, `/shabads/:ShabadID`, `/angs/:PageNo/:SourceID?`, `/hukamnamas/:y?/:m?/:d?`, `/random/:SourceID?`, `/banis`, `/banis/:BaniID`, `/amritkeertan/...`, `/kosh/...`, `/rehats/...`, `/writers`, `/raags`, `/sources`, and `POST/GET /graphql` — [banidb-api routes/index.js](https://raw.githubusercontent.com/KhalisFoundation/banidb-api/dev/api/routes/index.js)

**Rate limiting:**
- Middleware `limiter.rate250` applies to `/search`, `/search-results`, `/health` and `/rehats/search`. `limiter.rate100` applies to everything else — [routes/index.js](https://raw.githubusercontent.com/KhalisFoundation/banidb-api/dev/api/routes/index.js)
- The limiter is an in-memory token bucket keyed on `req.ip`: `new RateLimiter(rate, 'minute')`. It returns HTTP 429 "Too Many Requests" when tokens run out. The bucket sits in `memory-cache` with a 10,000 ms TTL that is refreshed on every request — [limiter.js](https://raw.githubusercontent.com/KhalisFoundation/banidb-api/dev/api/controllers/limiter.js)
- In live tests, no `X-RateLimit-*` headers were returned. Responses carry `cache-control: max-age=21600` (6 h) and `access-control-allow-origin: *`. No API key was needed (observed 2026-10-06 against `https://api.banidb.com/v2/search/...`).

**The root endpoint names the terms and data licence:**
- `GET https://api.banidb.com/v2/` returns `{"name":"BaniDB API","version":"2.10.3","documentation":"https://www.banidb.com","terms-of-service":"https://www.banidb.com/tos","data-license":"http://www.banidb.com/nposl"}` (live call, 2026-10-06; same strings in [routes/index.js](https://raw.githubusercontent.com/KhalisFoundation/banidb-api/dev/api/routes/index.js))

**Search types** (the `searchtype` query parameter). The Swagger doc defines 0 to 7: "0: First letter each word from start (Gurmukhi), 1: First letter each word anywhere (Gurmukhi), 2: Full Word (Gurmukhi), 3: Full Word Translation (English), 4: Romanized Gurmukhi (English), 5: Ang, 6: Main Letter (Gurmukhi), 7: Romanized first letter anywhere (English)" — [swagger.json](https://raw.githubusercontent.com/KhalisFoundation/banidb-api/dev/swagger.json). The official JS wrapper adds index 8, "Auto Detect" — [@sttm/banidb src/index.js (npm 3.0.1)](https://registry.npmjs.org/@sttm/banidb/latest)

**Other search parameters:**
- `source` (G=SGGS, D=Dasam, B=Bhai Gurdas Vaaran, A=Amrit Keertan, S=Bhai Gurdas Singh Vaaran, N=Bhai Nand Lal, R=Rehatnamas & Panthic, all), `ang`, `raag`, `writer`, `page`, `results`, plus undocumented `updatedsince`, `livesearch`, `isGurmukhi` — [swagger.json](https://raw.githubusercontent.com/KhalisFoundation/banidb-api/dev/swagger.json); [shabads.js](https://raw.githubusercontent.com/KhalisFoundation/banidb-api/dev/api/controllers/shabads.js)

**How each search type works in code:**
- Types 0 and 1 strip spaces, convert Unicode to the legacy ASCII font encoding via `anvaad.unicode(q, true)`, turn each character into a zero-padded char code, and run `LIKE` against `v.FirstLetterStr`. Operators `+ - * " '` are supported. Nukta letters are treated as equivalent to their base letters via a `bindiCharacters` table: ਸ/ਸ਼, ਖ/ਖ਼, ਗ/ਗ਼, ਜ/ਜ਼, ਫ/ਫ਼ — [shabads.js](https://raw.githubusercontent.com/KhalisFoundation/banidb-api/dev/api/controllers/shabads.js); [searchOperators.js](https://raw.githubusercontent.com/KhalisFoundation/banidb-api/dev/api/lib/searchOperators.js)
- Type 4 ("Romanized Gurmukhi") takes the first character of each romanized word and builds `v.FirstLetterEng LIKE '%<letters>%'`. It is not a full-word or phonetic match — [searchOperators.js `fullWordRomanizedToQuery`](https://raw.githubusercontent.com/KhalisFoundation/banidb-api/dev/api/lib/searchOperators.js)
- Type 7 lower-cases the query, strips spaces, and runs `v.FirstLetterEng LIKE '%q%'` — [shabads.js](https://raw.githubusercontent.com/KhalisFoundation/banidb-api/dev/api/controllers/shabads.js)
- Type 6 ("main letters", Gurmukhi with vowel signs removed) runs `MainLetters LIKE BINARY` — [searchOperators.js](https://raw.githubusercontent.com/KhalisFoundation/banidb-api/dev/api/lib/searchOperators.js)
- Type 8 ("omni"/Auto Detect) calls a MeiliSearch index `verses`, limited to 20 hits:
  - Non-Gurmukhi input is searched over `FirstLetterEng` and the English translations `Translation_bdb/ms/ssk`.
  - If that finds nothing, it falls back to the first letters of the query words.
  - Gurmukhi input is searched over `FirstLetterChar` or `FirstLetterStr`/`MainLetters`/`Gurmukhi` — [omni.js](https://raw.githubusercontent.com/KhalisFoundation/banidb-api/dev/api/controllers/omni.js)
- SQL search results are sorted by `ORDER BY ${orderBy} ShabadID ASC` (with `FirstLetterLen` first for queries under 3 characters), so there is no relevance ranking — [shabads.js](https://raw.githubusercontent.com/KhalisFoundation/banidb-api/dev/api/controllers/shabads.js)
- Database columns read by search include `Gurmukhi, GurmukhiUni, Translations, PageNo, LineNo, FirstLetterStr, MainLetters, Visraam, FirstLetterEng, Transliterations, WriterID, RaagID, SourceID` — [shabads.js](https://raw.githubusercontent.com/KhalisFoundation/banidb-api/dev/api/controllers/shabads.js)

**Response fields** (live result for verse 64):
- `verseId`, `shabadId`
- `verse.gurmukhi` (ASCII font encoding) and `verse.unicode`
- `larivaar.gurmukhi` and `larivaar.unicode`
- `translation.en.{ms,bdb,ssk}`, `translation.pu.{ft,ms,ss,bdb,pss}`, `translation.es.sn`, `translation.hi.{ss,sts}`
- `transliteration.{english,hindi,en,hi,ipa,ur}`
- `pageNo`, `lineNo`, `updated`
- `visraam.{sttm,igurbani,sttm2}` as arrays of `{p: wordIndex, t: type}`
- `writer`, `source{sourceId,...,pageNo}`, `raag`
- Paging is in `resultsInfo{totalResults,pageResults,pages{page,resultsPerPage,totalPages,nextPage}}` (live call `api.banidb.com/v2/search/so%20purakh%20niranjan?searchtype=4`, 2026-10-06)

**Live behaviour observed:**
- Type 4 with "so purakh niranjan" returned 253 results. The top hit was the unrelated "ਸੁਣਿਐ ਪੋਹਿ ਨ ਸਕੈ ਕਾਲੁ", which matched only because the substring "spn" appears in its first letters (live call).
- Type 4 with the full line "tati vao na lagai paarbrahm sharnai" returned exactly one, correct, result: ਤਾਤੀ ਵਾਉ ਨ ਲਗਈ ਪਾਰਬ੍ਰਹਮ ਸਰਣਾਈ ॥ (live call). Long queries are therefore discriminative.
- "ik oankaar sat naam" (type 4) and "osnkpn" (type 7) both returned 0 results, while "snkpn" (type 7) found the Mool Mantar. So ੴ adds nothing to `FirstLetterEng`, and a user who types "ik oankaar" puts extra letters in the query that break the match (live calls).
- Type 8 (omni) with the misspelled "so purkh niranjen har purkh" returned 20 hits. The top three were "ਰਾਗੁ ਆਸਾ ਮਹਲਾ ੪ ਸੋ ਪੁਰਖੁ", "ਬਿਰਖ ਬਸੇਰੋ ਪੰਖਿ ਕੋ ...", and "ਕਿਵ ਸਚਿਆਰਾ ਹੋਈਐ ...". The intended line was not among them (live call).
- Type 1 with ASCII first letters "spnhp" (source G) returned the two occurrences of "ਸੋ ਪੁਰਖੁ ਨਿਰੰਜਨੁ ਹਰਿ ਪੁਰਖੁ ਨਿਰੰਜਨੁ ਹਰਿ ਅਗਮਾ ਅਗਮ ਅਪਾਰਾ ॥" (angs 10 and 348), plus one other line (live call).

**Source coverage** (`/v2/sources`): A Amrit Keertan, B Bhai Gurdas Ji Vaaran, D Dasam Bani, G Sri Guru Granth Sahib Ji, N Bhai Nand Lal Ji Vaaran, R Rehatnamas and Panthic sources, S Bhai Gurdas Singh Ji Vaaran (live call to `api.banidb.com/v2/sources`).

**Licences and terms:**
- The API code (banidb-api repo) is MIT, "Copyright (c) 2019 Khalis Foundation" — [LICENSE](https://raw.githubusercontent.com/KhalisFoundation/banidb-api/master/LICENSE). This covers the server code, not the data.
- BaniDB says it deliberately keeps the data closed: "we have chosen to take a controlled approach ... have seen too many instances of Gurbani being misused and altered to feel comfortable making the data completely open." The README claims 46,810 verified changes as of 04/13/2024, at least 3 peer reviews per change, and standardisation against SGPC pothis — [banidb-api README](https://raw.githubusercontent.com/KhalisFoundation/banidb-api/master/README.md)
- ToS, as relayed by a search-engine summary because banidb.com was egress-blocked:
  - users "must provide written acknowledgement to BaniDB in the Project and include the BaniDB logo";
  - must "use BaniDB data in its entirety and cannot exclude any Gurbani data from the Project without express written permission from the Khalis Foundation";
  - may not claim copyright over the data;
  - "BaniDB API Data is additionally subject to The Non-Profit Open Software License version 3.0 (NPOSL-3.0), which is subordinate to the terms and conditions."
  - Source: [BaniDB Terms of Service](https://www.banidb.com/tos/) (snippet via WebSearch; not fetched directly)
- Khalis Foundation publishes a Python wrapper (`pip install banidb`, e.g. `banidb.search("bhbgggr")`) — [banidb-api-python README](https://raw.githubusercontent.com/KhalisFoundation/banidb-api-python/main/README.md). The JS wrappers `@sttm/banidb` and `banidb` are MIT on npm — [npm registry](https://registry.npmjs.org/@sttm/banidb/latest)

### Inferences
- API types 4 and 7 match first letters, not words, and they do no tie-breaking or ranking. So "query the API with the romanized line" works only as candidate retrieval, and only when every word's first letter is right. A library still has to re-rank candidates itself by comparing `transliteration.en` or `verse.unicode` with the input.
- The "use in its entirety / no exclusion" clause and the logo requirement are awkward for a small transliteration library that only wants to look up verses. NPOSL-3.0 is an OSI licence derived from OSL-3.0; from background knowledge, not verified this session, OSL-family licences treat network deployment as distribution. This should get legal review before bundling or caching BaniDB data. Calling the public API at runtime with attribution is the lowest-risk way to use BaniDB.
- The 6 h `cache-control` header suggests short-term caching is expected. The token bucket allows about 4 searches/s per IP, which is enough for interactive use but not for bulk matching of large documents.

### Gaps
- The full ToS and NPOSL pages could not be fetched (egress-blocked), so exact clause wording, last-updated date and any commercial-use language are unverified.
- The live API does not return `FirstLetterEng` values, so how it maps ambiguous letters is not fully known. For example, whether ਟ/ਠ are stored as "t" and ਸ਼ as "s" or "sh" was not confirmed. The probe for "ਟੂਟੀ ..." was inconclusive.
- The total verse count in BaniDB was not found.

## 2. Downloadable or offline databases (BaniDB dumps, Shabad OS SQLite, gurbanidb): licence, coverage, size

### Takeaway
No public, openly licensed BaniDB dump was found; BaniDB says it keeps the data controlled. The practical offline option is the Shabad OS Database: a single 152 MB SQLite file on npm (`@shabados/database@5.0.0-next.0`). Its code is MIT and its Gurbani text is marked public domain, with a "no derogatory alteration" condition. It covers SGGS (60,555 lines), Dasam Granth, Bhai Gurdas Vaaran and Kabitt Savaiye, Bhai Nand Lal, Sarabloh Granth (partial) and Ardas. It stores Unicode text with vishraam marks inline, but has no transliteration or first-letter columns, so a library must compute those itself.

### Cited Findings
**Shabad OS database:**
- The `shabados/database` repo is archived: "Development has moved to shabados/shabados" — [shabados/database README](https://raw.githubusercontent.com/shabados/database/main/README.md)
- Licence:
  - code outside `data` is MIT;
  - for the texts: "We identify it as being in the public domain [CC PDM 1.0] ... Derogatory treatments (including adding to, deleting from, altering of, or adapting) the words in a way that distorts or mutilates the original work is forbidden."
  - Sources: [shabados/database README](https://raw.githubusercontent.com/shabados/database/main/README.md); same text in [shabados/shabados database/README.md](https://raw.githubusercontent.com/shabados/shabados/main/database/README.md)
- The monorepo README says code is MIT "unless a package states otherwise (`packages/gurmukhi`, `database`)". Gurbani under `database/collections` is "public domain, but derogatory alteration of the source text is not [permitted]". The corpus is "600MB+ `collections/` corpus (154k JSON files)" — [shabados/shabados README](https://raw.githubusercontent.com/shabados/shabados/main/README.md)
- npm `@shabados/database`:
  - latest tag is `5.0.0-next.0`, published 2025-05-05, licence "MIT", unpacked size 152,059,067 bytes;
  - previous stable 4.8.7 dates from 2022-10-15 (~159 MB unpacked);
  - 72 versions in total.
  - Source: [npm registry @shabados/database](https://registry.npmjs.org/@shabados%2fdatabase)
- The 5.0.0-next.0 tarball is 47.6 MB compressed and contains `dist/master.sqlite` at 151,965,696 bytes. Its tables, with row counts from local inspection:
  - `lines` 141,264; `line_groups` 12,730; `sections` 127; `sources` 10; `authors` 40; `banis` 29; `bani_lines` 9,424; `assets` 23;
  - `asset_lines` 670,006, split by type into primary 141,264, translation 479,256, note 49,486.
  - Source: [tarball](https://registry.npmjs.org/@shabados/database/-/database-5.0.0-next.0.tgz)
- Lines per source in that SQLite (local inspection, same tarball):

  | Source | Lines |
  |---|---|
  | Dasam Granth | 67,758 |
  | Guru Granth Sahib | 60,555 |
  | Vaaran (Bhai Gurdas) | 7,585 |
  | Kabitt Savaiye | 2,761 |
  | Zindagi Nama | 1,021 |
  | Divan-i-Goya | 806 |
  | Jot Bigas (Farsi) | 352 |
  | Ganj Nama | 331 |
  | Sarabloh Granth | 78 |
  | Ardas | 17 |

  SGGS primary text comes from asset `SSA2` (SGPC *Shabadaarth* 2009-12) and Dasam from `DGDG` (SGPC *Das Granthi* 2014).
- Primary text is Unicode Gurmukhi with vishraam punctuation inline, e.g. `ਆਤਮ ਜੋਤਿ ਭਈ ਪਰਫੂਲਿਤ; ਪੁਰਖੁ ਨਿਰੰਜਨੁ ਦੇਖਿਆ ਹਜੂਰਿ ॥੧॥` with `additional` = `{"type":"primary","page":1198,"line":9}`. Because of these marks, a plain `LIKE '%ਸੋ ਪੁਰਖੁ ਨਿਰੰਜਨੁ ਹਰਿ ਪੁਰਖੁ%'` query found nothing (local inspection).

**gurmukhi-utils and its successor:**
- `gurmukhi-utils` (JS, npm 3.2.2) is licensed GPL-3.0 — [npm registry](https://registry.npmjs.org/gurmukhi-utils/latest)
- Its repo is archived. The successor is `gurmukhi`: a Rust core with JS (WASM), Python (`pip install gurmukhi`), Ruby, Kotlin and Swift bindings. It provides `to_ascii`, `to_unicode`, `normalize_unicode`, `transcribe` (Latin, LatinScholar, Devanagari), and feature detection/removal for vishraams, line endings (`RahaoEnding`, `NumberedEnding`), vowels and modifiers — [gurmukhi-utils README](https://raw.githubusercontent.com/shabados/gurmukhi-utils/main/README.md)
- The `packages/gurmukhi` LICENSE file contains MIT permission text — [LICENSE](https://raw.githubusercontent.com/shabados/shabados/main/packages/gurmukhi/LICENSE)
- `firstLetters` was dropped. The migration guide says to "Compose with `remove` + split ... Strip modifiers/vowels, then take first character of each word" — [MIGRATING.md](https://raw.githubusercontent.com/shabados/gurmukhi-utils/main/MIGRATING.md)

**anvaad-js** (Khalis Foundation, MIT, npm 1.5.1): "Utilities to prime Gurmukhi script for search. Unicode, first letters, main letters, transliteration". `firstLetters(words, eng=false, simplify)`, where `simplify` collapses "embedded vowels and other characters (eg. E to a, ^ to K)". Example: `firstLetters('Awie imlu gurisK ...') => 'AmgAmqmgkp'` — [anvaad-js README](https://raw.githubusercontent.com/KhalisFoundation/anvaad-js/master/README.md); [npm](https://registry.npmjs.org/anvaad-js/latest)

**BaniDB offline:**
- The banidb-api README describes local development with a `khalisfoundation/banidb-dev` Docker image (`npm run local`) — [banidb-api README](https://raw.githubusercontent.com/KhalisFoundation/banidb-api/master/README.md)
- SikhiToTheMax desktop depends on `realm ^10.19.5`, which implies an on-device Realm database — [sttm-desktop package.json](https://raw.githubusercontent.com/KhalisFoundation/sttm-desktop/dev/package.json)

**GurbaniDB / Sikher:** a search snippet describes GurbaniDB as "openly available at http://api.sikher.com" with "53 translations and 22 transliterations", and iGurbani as its showcase app — [sikher.com GurbaniDB](https://sikher.com/projects/gurbanidb/) (snippet only; site egress-blocked)

### Inferences
- For a library that must work offline and redistribute freely, Shabad OS is the only well-licensed option found. The library can ship a derived index (first-letter classes plus transliterations, a few MB) instead of the 152 MB SQLite, and load the full DB on demand.
- The "no derogatory alteration" clause should be respected by never emitting altered Gurbani text. The matcher returns the canonical line exactly as stored.
- 5.0.0-next.0 is a pre-release. Pin the exact version and record the line IDs, which are 4-character IDs such as `SPJ0`.
- Whether the `khalisfoundation/banidb-dev` image and STTM's Realm database may be reused is unknown, and the ToS says the data is controlled. They should not be treated as redistributable without permission from Khalis Foundation.

### Gaps
- The contents and licence of the `khalisfoundation/banidb-dev` Docker image, and the download URL and licence of STTM's offline Realm database, were not verified (codeload and GitHub API were blocked in this session).
- The current status and licence of Sikher's GurbaniDB (api.sikher.com) could not be checked.
- Coverage of Bhai Nand Lal and Dasam Granth in BaniDB versus Shabad OS was not compared line by line.

## 3. Other sources: GurbaniNow, SikhiToTheMax, SearchGurbani, Shabad OS, iGurbani — comparison

### Takeaway
The only actively maintained, programmatically usable sources found are BaniDB (an online API under restrictive terms) and Shabad OS (an offline SQLite, public domain plus MIT). GurbaniNow is officially deprecated. SikhiToTheMax is a BaniDB client. SearchGurbani/iSearchGurbani and iGurbani are end-user apps, and no documented, licensed API or dump for them was found.

### Cited Findings
- GurbaniNow API: "This API has been deprecated. No support will be provided." Its code is AGPL-3.0, "Copyright © 2015-2022 GurbaniNow Dev Team" — [GurbaniNow/gurbaninow-api README](https://raw.githubusercontent.com/GurbaniNow/gurbaninow-api/master/README.md). A third-party directory still lists it as "Fast and Accurate Gurbani RESTful API" with no authentication, "last checked on Apr 16, 2026" — [public-api.org](https://public-api.org/api/109/gurbaninow) (aggregator).
- SikhiToTheMax Web "Uses BaniDB". BaniDB's self-published table rates SikhiToTheMax 2 and iGurbani at "80-90%" accuracy. This is a competitor's own claim, not independently verified — [banidb-api README](https://raw.githubusercontent.com/KhalisFoundation/banidb-api/master/README.md)
- BaniDB and SikhiToTheMax "now power the captioning you see on live broadcasts from Sri Darbar Sahib Amritsar" — [banidb-api README](https://raw.githubusercontent.com/KhalisFoundation/banidb-api/master/README.md)
- iSearchGurbani covers SGGS, Bhai Gurdas Vaaran, Kabit Bhai Gurdas, Bhai Nand Lal and Dasam banis. It offers "First Letter Beginning and Anywhere in Romanisation and Gurmukhi" — [searchgurbani.com iSG](https://searchgurbani.com/sgdv/isg) (search snippet)
- iGurbani search supports first letter (start or anywhere), Ang/Vaar, and full word in Gurmukhi and English — [App Store iGurbani](https://apps.apple.com/app/id569235977) (search snippet)
- Shabad OS: open, Git-based proofreading with citations ("Photographic evidence continuously reviewed"), public domain texts, and SQLite/npm distribution — [shabados/database README](https://raw.githubusercontent.com/shabados/database/main/README.md)

Comparison:

| Source | Access | Romanized search | Licence / terms | Offline | Status |
|---|---|---|---|---|---|
| BaniDB | REST and GraphQL, no key | Types 4 and 7, first letters only, substring LIKE; type 8 MeiliSearch | ToS (attribution, logo, use "in its entirety") + NPOSL-3.0 | No public dump | Active (v2.10.3) |
| Shabad OS DB | npm SQLite 152 MB | None built in (DIY) | Text public domain (no derogatory alteration); code MIT | Yes | v5 pre-release May 2025; monorepo active |
| GurbaniNow | REST | Unknown | AGPL code | No | Deprecated |
| STTM | App (BaniDB client) | First-letter UI | BaniDB terms | Desktop Realm DB | Active |
| SearchGurbani / iGurbani | Apps/web | First letter, romanized | No API licence found | App-internal | Unknown |

### Inferences
- For a library: use Shabad OS offline as the primary corpus. Treat BaniDB as an optional online re-check when the user accepts its terms, for example to get BaniDB-specific transliterations or newer corrections.
- The two corpora differ slightly in spelling and in where they split pangtis. A matched line ID from one is not portable to the other, so cross-referencing needs (source, ang, line) or text alignment.

### Gaps
- No documented public API for SearchGurbani or iGurbani was found.
- GurbaniNow's wiki docs (github.com/GurbaniNow/api) returned 404, so its search modes are undocumented here.

## 4. How first-letter search from romanized input works, and a robust matching pipeline

### Takeaway
Existing apps reduce a line to the first letter of each word. Gurmukhi first letters are compared against `FirstLetterStr` (ASCII codes), and romanized first letters against `FirstLetterEng`, using a SQL `LIKE` substring with no ranking. A better pipeline collapses ambiguous letters into coarse classes, retrieves candidates with class n-grams, and re-ranks them with edit distance on a consonant skeleton plus semi-global alignment for partial lines. A prototype of this on Shabad OS SGGS scored 97.7% top-1 on clean romanizations in a different romanization system, and about 77 to 89% under 10 to 20% character noise.

### Cited Findings
- BaniDB romanized search takes `word.substr(0,1)` for each word and runs `FirstLetterEng LIKE '%...%'` — [searchOperators.js](https://raw.githubusercontent.com/KhalisFoundation/banidb-api/dev/api/lib/searchOperators.js)
- The omni search falls back to `words.map(w => w[0]).join('')` against `FirstLetterEng` when a full-text search finds nothing — [omni.js](https://raw.githubusercontent.com/KhalisFoundation/banidb-api/dev/api/controllers/omni.js)
- anvaad-js `firstLetters(words, eng, simplify)` produces first-letter strings and can simplify vowels and nukta forms, e.g. "^ to K" — [anvaad-js README](https://raw.githubusercontent.com/KhalisFoundation/anvaad-js/master/README.md)
- `gurmukhi` (Shabad OS) can strip vishraams and line endings (`remove(text, vishraams())`, `Feature.RahaoEnding`, `NumberedEnding`) before indexing — [gurmukhi-utils README](https://raw.githubusercontent.com/shabados/gurmukhi-utils/main/README.md)

**Prototype evaluation** (this session; script at `scripts/proto_match.py`, run against `@shabados/database@5.0.0-next.0` `master.sqlite`, SGGS asset `SSA2`, 60,555 lines):

Index (built in 1.8 s):
- Gurmukhi first letters are collapsed into classes:
  - V = ਅ ਆ ਇ ਈ ਉ ਊ ਏ ਐ ਓ ਔ ੳ ੲ
  - s = ਸ ਸ਼; h = ਹ
  - k = ਕ ਖ ਖ਼; g = ਗ ਘ ਗ਼
  - n = ਙ ਞ ਣ ਨ; c = ਚ ਛ; j = ਜ ਝ ਜ਼
  - t = ਟ ਠ ਤ ਥ; d = ਡ ਢ ਦ ਧ
  - p = ਪ ਫ ਫ਼; b = ਬ ਭ
  - r = ਰ ੜ; l = ਲ ਲ਼; m, y, v
- Romanized first letters map the same way (a/e/i/o/u→V, q/x→k, z→j, f→p, w→v) after NFD diacritic stripping. Vishraam marks, ॥, digits and ਰਹਾਉ are removed.
- Each line also stores an STTM-system romanization, made with this repo's `GurmukhiRomanizer("sttm")`.

Retrieval and scoring:
- Retrieval takes the top 300 lines by count of shared class trigrams.
- Each candidate is scored as `min(full, partial + 0.05)`:
  - `full` = 0.4 × normalized Levenshtein on class strings + 0.6 × normalized Levenshtein on consonant skeletons (vowels removed, aspirate h dropped after k/g/c/j/t/d/p/b, repeated letters collapsed);
  - `partial` is the same formula with semi-global alignment, where the query aligns to the best substring of the candidate.

Queries: 300 random SGGS lines romanized in a different system (`dr_sant_singh`), then corrupted.

| Condition | Top-1 | Top-5 | Time per query (pure Python) |
|---|---|---|---|
| Clean | 97.7% | 98.7% | 13–22 ms |
| 10% character noise | 87.7–89.0% | 89.3–89.7% | — |
| 20% character noise | 74.3–77.0% | 77.7–79.3% | — |
| First 60% of words only, with semi-global alignment | 80.3% | 92.7% | — |
| First 60% of words only, without semi-global alignment | 23.0% | 44.0% | — |

Ranges span two runs. A query counts as correct if the returned line text equals the source text, since identical repeated lines cannot be told apart.

Example outputs:
- "tati vao na lagai paarbrahm sharnai" → ਤਾਤੀ ਵਾਉ ਨ ਲਗਈ ਪਾਰਬ੍ਰਹਮ ਸਰਣਾਈ (score 0.040). The runner-up was ਤਤੀ ਵਾਉ ਨ ਲਗਈ ਸਤਿਗੁਰਿ ਰਖੇ ਆਪਿ (0.531).
- "sooraj kiran mile jal ka jal hooa ram" → ਸੂਰਜ ਕਿਰਣਿ ਮਿਲੇ ਜਲ ਕਾ ਜਲੁ ਹੂਆ ਰਾਮ (0.000).

### Inferences
Recommended pipeline:
1. **Normalize the input.** NFC/NFD, lowercase, strip diacritics after recording them as hints (ṭ ḍ ṇ ṛ ś ṁ resolve ambiguity when present). Remove `||`, `॥`, digits, "rahaau/rahau/rahao", "mahalaa N" headers and vishraam punctuation. Detect and handle ੴ: drop "ik oankaar/ekonkar/ikOankaar" tokens because BaniDB adds no first letter for ੴ. Also detect script, so Gurmukhi or legacy-ASCII input skips romanization (this repo's `legacy.detect_encoding` and `identify_system` can help).
2. **Derive candidate first letters.** Use coarse classes so that t→{ਤ,ਥ,ਟ,ਠ}, d→{ਦ,ਧ,ਡ,ਢ}, s/sh→{ਸ,ਸ਼}, n→{ਨ,ਣ,ਙ,ਞ}, r→{ਰ,ੜ}, any vowel→{ਅ,ੲ,ੳ}, k/kh/q→{ਕ,ਖ,ਖ਼}, ph/f→{ਪ,ਫ,ਫ਼}, j/jh/z→{ਜ,ਝ,ਜ਼}. Matching on class strings avoids enumerating the combinations; refine afterwards with diacritic hints.
3. **Retrieve candidates.** Use n-gram (trigram) postings over class strings, or a FirstLetter LIKE / FTS5 query in SQLite. Optionally also query BaniDB type 4 or 7 online. Keep about 100 to 300 candidates. Add a fallback using word-level skeleton n-grams so that noise in the first letter of a word does not lose the target. In the prototype, nearly all noise failures were retrieval misses, since top-5 is close to top-1.
4. **Align and score.** Combine (a) Levenshtein on class strings, (b) Levenshtein or Jaro-Winkler on consonant skeletons of the romanization, and (c) semi-global alignment so that half-line slides and partial OCR lines still match. Possible extras: per-word alignment (Needleman-Wunsch over words, using a word-level edit cost) to report which input word matches which canonical word, so a library can flag uncertain words; and a weighted substitution matrix for t/ṭ, d/ḍ, n/ṇ, s/sh, v/w, aa/a, ee/i, oo/u.
5. **Disambiguate in context.** For multi-line input such as a whole shabad, slides or a document, prefer candidates from the same `shabadId` or line group and in the same order (an HMM/Viterbi pass or a simple "previous line + 1" bonus). This resolves repeated rahao lines and pangtis that occur more than once.
6. **Accept or abstain.** Use a score threshold; in the prototype, true matches scored below about 0.1 and runners-up above about 0.5. Return the canonical Unicode line, source/ang/line metadata, and the alignment. Fall back to word-by-word reversal (this repo's `reverse_transliterate` + `CorpusMatcher`) when nothing passes the threshold.
- Pure Python at about 15 ms per query is fine for interactive use. A compiled edit-distance library (e.g. rapidfuzz) or SQLite FTS5 trigram tokenizer would cut this further; neither is used in the prototype.

### Gaps
- No public description was found of how SikhiToTheMax or SearchGurbani pick and rank results internally, beyond the BaniDB API code.
- The prototype noise model is synthetic (random substitutions and deletions). Real OCR confusions (e.g. ਠ/ਨ, ਮ/ਸ, or matras dropped by Gurmukhi OCR) and real user romanizations were not tested.
- Only SGGS was tested. Dasam Granth, which has 67,758 lines with many repeated formulaic lines, will probably be harder; this was not measured.

## 5. Published accuracy figures and known pitfalls (repeated rahao lines, pangati breaks, vishraams, kirtan slides)

### Takeaway
No published accuracy figures for romanized-to-verse matching were found. The pitfalls are concrete and measurable:
- about 10% of SGGS lines repeat verbatim somewhere else;
- about 8,700 lines share a first-letter signature with a different line;
- vishraam punctuation inside lines breaks naive substring search;
- ੴ has no first letter;
- BaniDB "verses" can contain more than one ॥-delimited half-line;
- slides often show partial lines.

### Cited Findings
- In Shabad OS SGGS, 5,997 of 60,555 lines (9.9%) have exact text (vishraams and numbering removed) that occurs more than once. 8,657 lines share their coarse first-letter class string with at least one different text (local measurement on [@shabados/database 5.0.0-next.0](https://registry.npmjs.org/@shabados/database/-/database-5.0.0-next.0.tgz)).
- "ਸੋ ਪੁਰਖੁ ਨਿਰੰਜਨੁ ਹਰਿ ਪੁਰਖੁ ਨਿਰੰਜਨੁ ਹਰਿ ਅਗਮਾ ਅਗਮ ਅਪਾਰਾ ॥" appears at ang 10 (verse 472) and ang 348 (verse 15809) in BaniDB, and twice in Shabad OS (line IDs `SPJ0`, `546S`). Matching on text alone cannot choose between them (live API call; local prototype).
- A single BaniDB verse can hold two half-lines and the rahao marker, e.g. verse 33883: "ਸਤਿਗੁਰਿ ਪਰਚੈ ਹਰਿ ਨਾਮਿ ਸਮਾਨਾ ॥ ਜਿਸੁ ਕਰਮੁ ਹੋਵੈ ਸੋ ਸਤਿਗੁਰੁ ਪਾਏ ਅਨਦਿਨੁ ਲਾਗੈ ਸਹਜ ਧਿਆਨਾ ॥੧॥ ਰਹਾਉ ॥" (live API call, searchtype 7)
- Shabad OS stores vishraams inline as `;` `,` `.` (e.g. "ਇਕ ਮਨਿ; ਪੁਰਖੁ ਨਿਰੰਜਨੁ ਧਿਆਵਉ ॥"). BaniDB keeps them separately in `visraam.{sttm,igurbani,sttm2}` as word-index/type pairs (local inspection; live API).
- The `gurmukhi` package can detect and remove vishraam marks and `RahaoEnding` / `NumberedEnding` — [gurmukhi-utils README](https://raw.githubusercontent.com/shabados/gurmukhi-utils/main/README.md)
- ੴ adds no first letter in BaniDB: "snkpn" finds the Mool Mantar, while "osnkpn" and the romanized "ik oankaar sat naam" return 0 (live API calls).
- BaniDB types 4 and 7 use unranked substring matching, so short queries return hundreds of results ordered by ShabadID: 253 results for "so purakh niranjan" (live call; [shabads.js](https://raw.githubusercontent.com/KhalisFoundation/banidb-api/dev/api/controllers/shabads.js)).
- In the prototype, partial lines (first 60% of words) dropped from 97.7% to 23.0% top-1 with full-line edit distance, and recovered to 80.3% with semi-global alignment (local experiment, section 4).
- The only accuracy figures found are BaniDB's claims about database accuracy, not matching accuracy: "43,000+" or "46,810" verified corrections, and competitors rated "80-90%" — [banidb-api README](https://raw.githubusercontent.com/KhalisFoundation/banidb-api/master/README.md)

### Inferences
Pitfalls a library must handle:
- **Repeated lines.** Return every location with identical text, or use context (neighbouring lines, shabad) to pick one. Never report a single ang as certain unless context confirms it.
- **Rahao and refrain repetition on kirtan slides.** Slide sequences repeat the rahao line between verses. Order-aware decoding has to allow jumps back to the rahao line.
- **Pangati versus verse granularity.** Input lines may be half a BaniDB verse, a whole verse, or span two. Semi-global alignment plus a merge-adjacent-lines step (try line i alone, then lines i and i+1 joined) handles this.
- **Vishraam and ending noise.** Strip them on both sides before indexing. Never compare raw strings.
- **Headers** (ਰਾਗੁ ਆਸਾ ਮਹਲਾ ੪, ੴ ਸਤਿਗੁਰ ਪ੍ਰਸਾਦਿ) match many inputs loosely; BaniDB's omni top hit for the test query was such a header. Down-weight header lines or handle them separately.
- **Corpus spelling differences** between BaniDB and Shabad OS (lagamatra standardisation) mean the canonical line depends on the corpus. Record which corpus and version was used.

### Gaps
- No published benchmark or paper on Gurbani line retrieval from romanized or OCR text was found. Figures in these notes come from the prototype in this session and should be confirmed on real user and OCR data.
- No primary documentation was found on how STTM or Shabad OS Presenter handle repeated rahao lines in live "shabad navigator" mode.
