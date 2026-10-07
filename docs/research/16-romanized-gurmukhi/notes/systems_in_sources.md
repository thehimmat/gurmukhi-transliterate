# Romanization systems for Gurmukhi/Gurbani as they appear in real sources (as of Oct 2026)

Research method note: most Sikh websites (searchgurbani.com, srigranth.org, sikhnet.com, sikhdharma.org, 3ho.org, sikhs.org, wikipedia.org, interscript.org, archive.org mirrors) were blocked by this session's egress proxy, so they could only be seen through web-search result titles and snippets. Three sources could be read directly and give **verbatim, machine-verified** strings: (1) the BaniDB REST API (`api.banidb.com`), (2) igurbani.com, and (3) the npm packages `anvaad-js` 1.5.1 (Khalis Foundation) and `gurmukhi-utils` 3.2.2 (Shabad OS), which I ran locally on the same Gurmukhi input. Anything taken only from a search snippet is marked "(snippet)". Anything from background knowledge that I could not re-check is in Inferences or Gaps, never in Cited Findings.

## Q1. What conventions do the major sources use? (inventory with signature tokens, lossiness, real examples)

### Takeaway
The conventions you will actually meet online are a small family of ASCII "STTM-style" schemes — the current BaniDB/STTM scheme, the legacy STTM scheme (iGurbani, SearchGurbani), and a separate Shabad OS scheme — plus devotional 3HO spellings, informal ad-hoc Punjabi, and academic diacritic schemes (ISO 15919/IAST/Shackle) that turn up almost only in print and scholarship. A common non-romanization "lookalike" is GurbaniAkhar ASCII font encoding (`siqnwmu krqw purKu`), which a detector has to recognise and send elsewhere.

### Cited Findings

#### A. BaniDB / SikhiToTheMax, current scheme (field `transliteration.english`, alias `en`)
- The BaniDB v2 API returns, for each verse, `transliteration` with keys `english`, `en` (same value), `hindi`, `hi`, `ipa`, `ur` (Shahmukhi). There is no separate "Roman with diacritics" field. — [BaniDB API /v2/shabads/1](https://api.banidb.com/v2/shabads/1) (fetched 2026-10-06)
- Verbatim pairs (Gurmukhi → `english`): — [BaniDB /v2/shabads/1](https://api.banidb.com/v2/shabads/1); [BaniDB /v2/angs/2/G](https://api.banidb.com/v2/angs/2/G)
  - `ੴ ਸਤਿ ਨਾਮੁ ਕਰਤਾ ਪੁਰਖੁ ਨਿਰਭਉ ਨਿਰਵੈਰੁ ਅਕਾਲ ਮੂਰਤਿ ਅਜੂਨੀ ਸੈਭੰ ਗੁਰ ਪ੍ਰਸਾਦਿ ॥` → `ikOankaar sat naam karataa purakh nirabhau niravair akaal moorat ajoonee saibha(n) gur prasaadh ||`
  - `ਕਿਵ ਸਚਿਆਰਾ ਹੋਈਐ ਕਿਵ ਕੂੜੈ ਤੁਟੈ ਪਾਲਿ ॥` → `kiv sachiaaraa hoieeaai kiv kooRai tuTai paal ||`
  - `ਅੰਮ੍ਰਿਤ ਵੇਲਾ ਸਚੁ ਨਾਉ ਵਡਿਆਈ ਵੀਚਾਰੁ ॥` → `a(n)mirat velaa sach naau vaddiaaiee veechaar ||`
  - `ਜੇਤੀ ਸਿਰਠਿ ਉਪਾਈ ਵੇਖਾ ਵਿਣੁ ਕਰਮਾ ਕਿ ਮਿਲੈ ਲਈ ॥` → `jetee siraTh upaiee vekhaa vin karamaa k milai liee ||`
  - `ਮੁਹੌ ਕਿ ਬੋਲਣੁ ਬੋਲੀਐ ਜਿਤੁ ਸੁਣਿ ਧਰੇ ਪਿਆਰੁ ॥` → `muhau k bolan boleeaai jit sun dhare piaar ||`
- Signature tokens seen in that data: capital `T`/`Th` for ਟ/ਠ (`tuTai`, `siraTh`, `koTee`), capital `R` for ੜ (`kooRai`), parenthesised nasal `(n)` (`saibha(n)`, `ba(n)naa`, `a(n)mirat`), `dh` for dental ਦ (`prasaadh`, `aadh`) **and** for ਧ (`dhare`), `dd` for ਡ (`vaddiaaiee`), `ikOankaar` with a capital O, `||` for ॥, `ee`/`oo`/`aa` long vowels, `e` (not `ay`/`ae`) for ੇ (`je`, `velaa`), standalone `k` for ਕਿ (`k milai`) and `na` for ਨ. — same sources
- ਣ is written plain `n` (`bolan`, `sun`, `vin`), so ਣ/ਨ merge; ਦ/ਧ merge (`dh`); ਡ/ਢ merge (`dd`, see below); short final ਿ/ੁ are dropped (`moorat`, `purakh`, `paal`). — same sources
- **The open-source Khalis Foundation library `anvaad-js` (v1.5.1, function `translit(ascii, 'english'|'ipa'|...)`) reproduces the BaniDB `english` and `ipa` fields exactly** on every line I tested, so its code is the de facto spec for the BaniDB scheme. Extra outputs from running it: `ਸਿੱਖੀ ਸਿਖਿਆ ਗੁਰ ਵੀਚਾਰਿ ॥` → `si'khee sikhiaa gur veechaar ||` (addak = apostrophe); `ਭਾਂਡਾ ਭਾਉ ਅੰਮ੍ਰਿਤੁ ਤਿਤੁ ਢਾਲਿ ॥` → `bhaa(n)ddaa bhaau a(n)mrit tit ddaal ||` (ਢ → `dd`, same as ਡ); `ਖ਼ਾਲਸਾ ਫ਼ਤਿਹ ॥` → `khaalasaa fteh ||` (ਖ਼ → `kh`, ਫ਼ → `f`). — [anvaad-js on npm](https://www.npmjs.com/package/anvaad-js) (tarball 1.5.1, run locally 2026-10-06)
- The anvaad-js README's own example shows an **older** English style: `translit('Awie imlu gurisK Awie imlu qU myry gurU ky ipAwry ]')` → `'aai mil gurasikh aai mil too mayray guroo kay piaaaray ||'` (`ay` for ੇ). The current code outputs `e`, so the README is out of date — evidence that the BaniDB scheme itself has changed over time. — [anvaad-js README](https://www.npmjs.com/package/anvaad-js)

#### B. BaniDB IPA (field `transliteration.ipa`)
- Verbatim: `ੴ ਸਤਿ ਨਾਮੁ ...` → `ɪk oəŋkɑɾ sət̪ nɑm kərət̪ɑ pʊrəkʰ nɪrɓo nɪrəʋær əkɑl murət̪ əd͡ʒuni sæɓəŋ Gʊr pɹəsɑd̪.`; `ਆਦਿ ਸਚੁ ਜੁਗਾਦਿ ਸਚੁ ॥` → `əɑd̪ sət͡ʃ d͡ʒʊGɑd̪ sət͡ʃ.`; `ਕਥਿ ਕਥਿ ਕਥੀ ਕੋਟੀ ਕੋਟਿ ਕੋਟਿ ॥` → `kət̪ʰ kət̪ʰ kət̪ʰi kɔʈi kɔʈ kɔʈ.` — [BaniDB](https://api.banidb.com/v2/shabads/1); [BaniDB ang 2](https://api.banidb.com/v2/angs/2/G)
- Signatures: capital `G` for ਗ (`Gʊr`, `d͡ʒʊGɑd̪`), tie bars `t͡ʃ d͡ʒ`, dental bridge `t̪ d̪`, `ɓ` for ਭ, `ɹ` for subjoined ੍ਰ (`pɹəsɑd̪`), ॥ → `.` (and `.1.` for ॥੧॥), no length marks. The verse-level IPA keeps `ɾ` in one place (`oəŋkɑɾ`) but `r` elsewhere. The IPA drops addak (`ਸਿੱਖੀ` → `sɪkʰi`) and renders ਖ਼ as `kʰ` (`kʰɑləsɑ`), ਫ਼ as `f`. — same sources; anvaad-js run

#### C. Legacy SikhiToTheMax scheme (iGurbani, SearchGurbani, older STTM desktop)
- igurbani.com serves these verbatim lines (Gurmukhi from BaniDB above): — [iGurbani shabad 1](https://www.igurbani.com/shabad/1) (fetched 2026-10-06)
  - ਮੂਲ ਮੰਤਰ → `ikoankaar sathnaam karathaa purakh nirabho niravair akaal moorath ajoonee saibhan gurprasaadh ||`
  - `ਸੋਚੈ ਸੋਚਿ ਨ ਹੋਵਈ ਜੇ ਸੋਚੀ ਲਖ ਵਾਰ` → `sochai soch n hovee jae sochee lakh vaar ||`
  - `ਭੁਖਿਆ ਭੁਖ ਨ ਉਤਰੀ ਜੇ ਬੰਨਾ ਪੁਰੀਆ ਭਾਰ ॥` → `bhukhiaa bhukh n outharee jae bannaa pureeaa bhaar ||`
  - `ਸਹਸ ਸਿਆਣਪਾ ਲਖ ਹੋਹਿ ਤ ਇਕ ਨ ਚਲੈ ਨਾਲਿ` → `sehas siaanapaa lakh hohi th eik n chalai naal ||`
  - `ਕਿਵ ਸਚਿਆਰਾ ਹੋਈਐ ਕਿਵ ਕੂੜੈ ਤੁਟੈ ਪਾਲਿ ॥` → `kiv sachiaaraa hoeeai kiv koorrai thuttai paal ||`
- Signatures: `th` for dental ਤ (`sathnaam`, `karathaa`, `outharee`, `th eik`), `tt` for ਟ (`thuttai`), `rr` for ੜ (`koorrai`), `ae` for ੇ (`jae`), `eh` where ਹ follows a short a (`sehas`, `rehaa`), glide-prefixed initial vowels (`outharee` for ਉ, `eik` for ਇ), `o` for word-final ਉ (`nirabho`), bare `n` for ਨ, plain `n` for nasals (`saibhan`, `bannaa`), no capitals, `||`. — same source
- SearchGurbani uses the same legacy family, but in Title Case and with sihari kept in ਸਤਿ: page title `Ik Oankaar Sathinaam Karathaa Purakh Nirabho Niravair Akaal Moorath Ajoonee Saibhan Gur Prasaadh ||` (snippet). Another snippet from the same search attributes the lowercase variant `Ik oa(n)kaar sath naam karathaa purakh nirabho niravair akaal moorath ajoonee saibha(n) gur prasaadh`, which mixes legacy `th`/`o` with BaniDB-style `(n)` (snippet; I could not confirm which page it came from). — [SearchGurbani SGGS shabad 1656 line 1](https://www.searchgurbani.com/guru-granth-sahib/shabad/1656/line/1)
- SikhiWiki page titles mix several Romanizations of the same words: `Aadh sach`, `Jugaadh sach`, `Hai bhee sach`, `Naanak hosee bhee sach`, alongside `Ad Sach` (snippet titles). — [SikhiWiki Aadh sach](https://www.sikhiwiki.org/index.php/Aadh_sach); [SikhiWiki Ad Sach](https://www.sikhiwiki.org/index.php/Ad_Sach)

#### D. Shabad OS scheme (`gurmukhi-utils` `toEnglish`), not in the repo
- `gurmukhi-utils` v3.2.2 (homepage github.com/ShabadOS/gurmukhi-utils) ships its own `toEnglish` transliterator with an explicit, readable rule table. Mappings from the code include ਟ `tt`, ਠ `tth`, ਡ `dd`, ਢ `dt`, ਤ `t`, ਥ `th`, ਦ `d`, ਧ `dh`, ਣ `n`, ੜ `rr`, ਙ `ng`, ਛ `chh`, ਯ `y`, ਸ਼ `sh`, ੇ `e`, ੌ `au`, tippi/bindi `(n)`, and `ik oankaar` for ੴ. — [gurmukhi-utils on npm](https://www.npmjs.com/package/gurmukhi-utils) (lib/toEnglish.js)
- Its documented rules: drop word-final aunkar/sihari "except when on Haha (h), Ooraa (a), or on a standalone akhar"; `ahi`→`eh` and `yhi`→`yeh` at word end; standalone `tit`→`tith`; standalone `n`→`na`, `t`→`ta`; parentheses stripped and `nn`→`n`, `anm`→`am`; insert `y` in three-letter words with ਹ in the middle ("per issue #123"). — same (lib/toEnglish.js)
- Local run, verbatim output: `ਕਿਵ ਸਚਿਆਰਾ ਹੋਈਐ ਕਿਵ ਕੂੜੈ ਤੁਟੈ ਪਾਲਿ ॥` → `kiv sachiaaraa hoeeai kiv koorrai tuttai paal |`; `ਭਾਂਡਾ ਭਾਉ ਅੰਮ੍ਰਿਤੁ ਤਿਤੁ ਢਾਲਿ ॥` → `bhaanddaa bhaau amrit tith dtaal |`; `ਅੰਮ੍ਰਿਤ ਵੇਲਾ ਸਚੁ ਨਾਉ ਵਡਿਆਈ ਵੀਚਾਰੁ ॥` → `amrit velaa sach naau vaddiaaee veechaar |`; `ਖ਼ਾਲਸਾ ਫ਼ਤਿਹ ॥` → `khaalasaa fatih |`; `ਸਿੱਖੀ ਸਿਖਿਆ...` → `sikhee sikhiaa gur veechaar |` (addak dropped). — same, run 2026-10-06
- Its README example (`bhaa(n)ddaa bhaou anmrit tit dtaal ||`) no longer matches the code's output. — [gurmukhi-utils README](https://www.npmjs.com/package/gurmukhi-utils)

#### E. GurbaniAkhar / AnmolLipi ASCII font encoding (a Latin-letter lookalike, not a romanization)
- iGurbani's page source carries the Gurmukhi as legacy-font ASCII next to the romanization: `siqnwmu krqw purKu inrBau inrvYru Akwl mUriq AjUnI sYBµ gurpRswid ]`, `Awid scu jugwid scu ]`, `hY BI scu nwnk hosI BI scu ]1]`, `kUVY qutY pwil ]`. — [iGurbani shabad 1](https://www.igurbani.com/shabad/1)
- The same encoding is the native input format of anvaad-js `translit` (`ikv sicAwrw hoeIAY ikv kUVY qutY pwil ]`) and of the Shabad OS pipeline (`toEnglish` converts to ASCII first; its map has `w`→`aa`, `q`→`t`, `]`→`|`, `µ`/`M`/`N`→`(n)`). — [anvaad-js](https://www.npmjs.com/package/anvaad-js); [gurmukhi-utils](https://www.npmjs.com/package/gurmukhi-utils)

#### F. 3HO / Sikh Dharma (Kundalini Yoga) devotional spellings
- Sikh Dharma's own page on the Mool Mantra (a lecture by the Siri Singh Sahib) comes up for the query "Ek Ong Kaar, Sat Naam, Kartaa Purakh, Nirbhao, Nirvair"; the snippets use `Ek Ong Kaar`, `Sat Naam`, `Kartaa Purakh`, `Nirbhao`, `Nirvair` (snippet). — [sikhdharma.org ?p=3222](https://www.sikhdharma.org/?p=3222)
- In 3HO usage the Maha Mantar is titled `Aad Such Jugaad Such`, and the full form quoted is `Aad Such, Jugaad Such, Hai Bhee Such, Naanak Hosee Bhee Such`. Snippets connect it to a meditation Yogi Bhajan gave on 30 Nov 1977 (snippet). — [Siri Shabd Singh, "Aad Such Jugaad Such" (Bandcamp)](https://sirishabdsingh.bandcamp.com/track/aad-such-jugaad-such); [Invincible Music "Aad Sach Jugaad Sach"](https://www.invinciblemusic.com/mera-man-loche-aad-sach-jugaad-sach)
- Even within 3HO-adjacent music the spellings vary: `Aad Such` (Bandcamp) vs `Aad Sach` (Invincible Music, "Sat Kartar - Aad Sach" lyrics). — same sources; [muztext](https://en.muztext.com/lyrics/sat-kartar-aad-sach)

#### G. Academic / official standards
- ISO 15919 (2001) has a Gurmukhi table. Per the Wikipedia summary, `ṃ` stands specifically for Gurmukhi tippi (ੰ) and `ṁ` for anusvara/bindi in general (snippet). — [Wikipedia: ISO 15919](https://en.wikipedia.org/wiki/ISO_15919)
- Punjabi University's GTrans ("Gurmukhi to Roman Transliteration software", learnpunjabi.org) "is mainly based on the ISO 15919 international standard" (snippet). — [learnpunjabi.org GTrans](https://learnpunjabi.org/gtrans/index.asp)
- A UN 1972 romanization of Punjabi (Gurmukhi) exists as a machine-readable map, `un-pan-Guru-Latn-1972`, in Interscript (snippet; page blocked). A UNGEGN working-group report on Punjabi romanization also exists. — [Interscript map](https://interscript.org/maps/un-pan-Guru-Latn-1972); [UNGEGN WG report (Punjabi)](https://unstats.un.org/unsd/ungegn/working_groups/wg5/documents/wgrr4punjabi.pdf)

#### H. srigranth.org (Dr. Kulbir Singh Thind) / Dr. Sant Singh Khalsa
- SriGranth offers the original Gurmukhi, a "Roman notation" and translations into English and other languages (SikhiWiki snippet). — [SikhiWiki: Srigranth](https://www.sikhiwiki.org/index.php/Srigranth)
- The English translation that iGurbani shows beside the legacy-STTM transliteration reads `One Universal Creator God, TheName Is Truth Creative Being Personified No Fear No Hatred Image Of The Undying, Beyond Birth, Self-Existent. By Guru's Grace~`. — [iGurbani shabad 1](https://www.igurbani.com/shabad/1)

### Inferences
- **Same line, three online schemes** (useful as a detector test vector). For ਕਿਵ ਸਚਿਆਰਾ ਹੋਈਐ ਕਿਵ ਕੂੜੈ ਤੁਟੈ ਪਾਲਿ ॥: BaniDB `kooRai tuTai ... hoieeaai ||`, legacy `koorrai thuttai ... hoeeai ||`, Shabad OS `koorrai tuttai ... hoeeai |`. The tokens that separate them are ਤ (`t` vs `th`), ਟ (`T` vs `tt`), ੜ (`R` vs `rr`) and the line ending (`||` vs `|`).
- The iGurbani English is the well-known Dr. Sant Singh Khalsa translation (from background knowledge; the page does not credit it). The transliteration printed under it on iGurbani/SearchGurbani/srigranth is legacy STTM, not a separate "Sant Singh" scheme. I found no online source showing a distinct Sant Singh Khalsa transliteration with dotted retroflexes (`ṭ ḍ ṇ ṛ`) as in the repo's `dr_sant_singh` map; that map's provenance (the comparison spreadsheet) should be checked against a scan of the printed source.
- **Repo discrepancies found:**
  - The repo's `sttm` map has `ਖ਼` → `khh` and `ਫ਼` → `ph`. The current BaniDB code (anvaad-js 1.5.1) produces `kh` and `f` (`khaalasaa fteh`).
  - Its note that `ਊ` → `uoo` was not checked here.
  - The repo's `sttm_legacy` `ਤ` → `th` and `ੇ` → `ae` match iGurbani exactly.
- **Missing from the repo's system list, ranked by how often they appear online:**
  1. Informal / ad-hoc English-style Punjabi (`Waheguru`, `Satnam`, `Ek Onkar`); the repo's server placeholder already hints at it.
  2. GurbaniAkhar/AnmolLipi ASCII font encoding. It is not a romanization, but it is Latin-letter text that claims to be Gurbani, so detect it first and convert it with a font map.
  3. The Shabad OS `toEnglish` scheme (current, open-source, used by the Shabad OS presenter ecosystem).
  4. 3HO/Sikh Dharma devotional spellings (`Ek Ong Kaar`, `Such`, `Wahe Guru`).
  5. SearchGurbani Title-Case legacy (can be treated as `sttm_legacy` after case-folding, plus a `Sathinaam`-style sihari rule).
  6. UN 1972 / UNGEGN and ALA-LC (Library of Congress) Panjabi romanization, used in library catalogues and some academic books. ALA-LC is background knowledge, not verified here.

### Gaps
- Could not open SearchGurbani, srigranth.org, SikhNet, sikhdharma.org, 3ho.org or archive.org (all blocked by egress), so I have no verbatim multi-line samples from them. SearchGurbani's options menu and any non-STTM transliteration it offers are unknown.
- **Macauliffe (1909), Gopal Singh, Manmohan Singh (SGPC):** no verbatim Romanized strings found. From background knowledge (unverified), these are translations whose Gurmukhi words appear only as proper names and terms, not as line-by-line transliteration. Macauliffe used a 19th-century diacritic-light Anglo-Indian style. Needs scans.
- **Shackle:** nothing beyond what the repo already holds (taken from the book).
- **Punjabi learner books** (e.g. Punjabi University primers, Colloquial Panjabi, Teach Yourself Panjabi): no samples retrieved. Their conventions, often ISO-like with macrons and underdots, are unverified.
- **Gurbani CDs / kirtan slides:** no direct samples. Slide software usually pulls from BaniDB or Shabad OS (STTM desktop, Shabad OS presenter), so the slides should inherit schemes A, C or D. That is an inference.

## Q2. Which conventions are ad hoc or inconsistent, and how common is diacritic loss?

### Takeaway
Every online Gurbani database scheme is plain ASCII. Diacritics show up only in academic or ISO work and in IPA fields, so "diacritic loss" is the normal state online, not an exception. Inconsistency is high between sources, between versions of one source, and in informal and devotional writing. The schemes generated by code (BaniDB, legacy STTM, Shabad OS) are internally consistent, because a program produces them.

### Cited Findings
- **BaniDB, iGurbani and Shabad OS use no diacritics at all** in their English transliteration (all samples above). Retroflex marking is pushed into ASCII by capitals (`T`, `R`) or doubling (`tt`, `rr`). — [BaniDB](https://api.banidb.com/v2/angs/2/G); [iGurbani](https://www.igurbani.com/shabad/1); [gurmukhi-utils](https://www.npmjs.com/package/gurmukhi-utils)
- **Version drift inside one product.** The STTM/BaniDB English went from legacy (`sathnaam`, `jae`, `thuttai`, `koorrai`) to current (`sat naam`, `je`, `tuTai`, `kooRai`), and the anvaad-js README still shows a third, older form (`mayray`, `kay`, `piaaaray`). — [iGurbani](https://www.igurbani.com/shabad/1); [BaniDB](https://api.banidb.com/v2/shabads/1); [anvaad-js README](https://www.npmjs.com/package/anvaad-js)
- **ੴ is written differently by each source:** `ikOankaar` (BaniDB), `ikoankaar` (iGurbani), `Ik Oankaar` (SearchGurbani title), `ik oankaar` (Shabad OS map), `Ek Ong Kaar` (Sikh Dharma, snippet). — sources above
- **ਸਚੁ is written differently by each source:** `sach` (BaniDB/iGurbani/SikhiWiki) vs `Such` (3HO, snippet) vs `Sach` (Invincible Music); and ਆਦਿ `aadh` vs `Aad` vs `Ad`. — [Bandcamp](https://sirishabdsingh.bandcamp.com/track/aad-such-jugaad-such); [SikhiWiki Ad Sach](https://www.sikhiwiki.org/index.php/Ad_Sach)
- **Collisions documented in code** (lossy by design):
  - BaniDB: ਦ=ਧ=`dh`, ਡ=ਢ=`dd`, ਣ=ਨ=`n`, ੰ=ਂ=`(n)`.
  - Shabad OS: ੰ=ਂ=`(n)` (then the parentheses are stripped), addak dropped, ਣ=ਨ=`n`.
  - Legacy STTM: ਣ=ਨ=`n` and ੰ/ਂ=`n`.

  — [anvaad-js](https://www.npmjs.com/package/anvaad-js); [gurmukhi-utils lib/toEnglish.js](https://www.npmjs.com/package/gurmukhi-utils); [iGurbani](https://www.igurbani.com/shabad/1)

### Inferences
- The aa/a, ee/i, oo/u and w/v alternations come mainly from informal and devotional text (`Waheguru` vs BaniDB-style `vaahiguroo`, `Nirbhao` vs `nirabhau`). The database schemes are steady on `aa`/`ee`/`oo` and `v`. So the presence of `w` for ਵ, single `a` for ਾ, and Title Case are strong signs of informal or devotional input (based on the samples; no frequency counts).
- Schwa insertion separates the families. Database schemes write a medial inherent `a` (`karataa`, `nirabhau`, `niravair`), while devotional and informal text drops it (`Kartaa`, `Nirbhao`, `Nirvair`). This is a strong cue.

### Gaps
- I found no quantitative study of how often diacritics appear in the wild (e.g. on social media or in printed gutkas). "Diacritic loss is the norm online" rests on the major Gurbani databases sampled here, not on corpus statistics.

## Q3. Are there documented style guides?

### Takeaway
No prose style guide was found for BaniDB/STTM or 3HO. The working "style guides" are open-source code: Khalis Foundation's `anvaad-js` (reproduces BaniDB output exactly) and Shabad OS's `gurmukhi-utils` `toEnglish` (an explicit, commented rule list). ISO 15919 and the UN 1972 system are formal standards.

### Cited Findings
- A web search for BaniDB/Khalis transliteration rules turned up only the BaniDB-API GitHub repo, no rules document. — [KhalisFoundation/BaniDB-API](https://github.com/KhalisFoundation/BaniDB-API)
- `anvaad-js` exposes `translit(gurmukhi, language?: 'english' | 'devnagri' | 'ipa' | 'shahmukhi', map?)`, and its output matches the BaniDB API fields byte for byte on the lines tested. — [anvaad-js](https://www.npmjs.com/package/anvaad-js) (dist/index.d.ts; local run vs [BaniDB](https://api.banidb.com/v2/angs/2/G))
- `gurmukhi-utils` `toEnglish` documents its rules inline (character map, "extra a" insertion rules, initial and final regex replacements, issue-referenced exceptions). — [gurmukhi-utils](https://www.npmjs.com/package/gurmukhi-utils)
- ISO 15919 (2001) covers Gurmukhi, and GTrans (Punjabi University) implements it (snippets). — [ISO 15919](https://en.wikipedia.org/wiki/ISO_15919); [GTrans](https://learnpunjabi.org/gtrans/index.asp)

### Inferences
- For reverse transliteration of BaniDB English, port or test against anvaad-js (MIT-licensed npm package). For Shabad OS, port the gurmukhi-utils rules. Both can generate unlimited labelled training and test data for the detector from BaniDB Gurmukhi.

### Gaps
- No 3HO/KRI Romanization guide was found. The KRI/3HO "Sadhana" and Kundalini manuals likely follow an in-house convention (`Ong`, `Wahe Guru`, `Siri`), but no rules document was accessible.
- The legacy STTM scheme's rule source (the old STTM desktop/database) was not located. Only its output (iGurbani) was observed.

## Q4. Which signature features best distinguish the systems?

### Takeaway
A small set of tokens identifies the family with high confidence:
- capital-letter retroflexes and `(n)` → BaniDB
- `th`-for-ਤ plus `ae` plus `||` → legacy STTM
- `dt`, `tth` and single `|` → Shabad OS
- `ṭ ḍ ṇ ā ī ū ṃ/ṁ` → academic (ISO/IAST/Shackle/Sacred Nitnem)
- `ʈ ɖ ɳ ə ɑ` with capital `G` → BaniDB IPA
- `ⁿ` and subscripts → Gursevak
- `Ong`, `Such`, Title Case → 3HO
- `q w ] µ` inside "words" (`siqnwmu`) → GurbaniAkhar ASCII, not a romanization

### Cited Findings
- **BaniDB:** `T`/`Th`/`R` capitals mid-word (`tuTai`, `siraTh`, `kooRai`), `(n)`, `ikOankaar`, addak apostrophe `si'khee`, `||`. — [BaniDB](https://api.banidb.com/v2/angs/2/G); [anvaad-js](https://www.npmjs.com/package/anvaad-js)
- **Legacy STTM:** `th` for ਤ (`sathnaam`, `karathaa`), `ae` (`jae`), `rr`/`tt` (`koorrai thuttai`), `eh` (`sehas`, `rehaa`), `ou`/`ei` initials (`outharee`, `eik`), bare `n`, `||`. — [iGurbani](https://www.igurbani.com/shabad/1)
- **Shabad OS:** `dt` for ਢ (`dtaal`), `tth` for ਠ, single `|` for ॥ (`paal |`), `tith`, `na`/`ta` for standalone ਨ/ਤ, no parentheses. — [gurmukhi-utils](https://www.npmjs.com/package/gurmukhi-utils)
- **BaniDB IPA:** `Gʊr`, `t͡ʃ`, `t̪`, `ɓ`, `ɹ`, lines ending in `.` — [BaniDB](https://api.banidb.com/v2/shabads/1)
- **GurbaniAkhar ASCII:** `]` and `]1]` line ends, `w` = ਾ, `q` = ਤ, `I` = ੀ, `U` = ੂ, `Y` = ੈ, `µ`/`M` = tippi, `` ` `` = addak (`siqnwmu`, `kUVY qutY pwil ]`). — [iGurbani](https://www.igurbani.com/shabad/1); [gurmukhi-utils map](https://www.npmjs.com/package/gurmukhi-utils)
- **3HO:** `Ek Ong Kaar`, `Aad Such, Jugaad Such`, comma-separated Title Case (snippets). — [sikhdharma.org](https://www.sikhdharma.org/?p=3222); [Bandcamp](https://sirishabdsingh.bandcamp.com/track/aad-such-jugaad-such)
- **ISO 15919:** `ṃ` for tippi (snippet). — [ISO 15919](https://en.wikipedia.org/wiki/ISO_15919)

### Inferences
- Suggested detector order:
  1. Unicode IPA symbols → BaniDB IPA vs academic IPA. BaniDB has capital `G`, `ɓ` and no `ː`; academic IPA has `ː` and `ɦ`.
  2. Combining diacritics/macrons → ISO/IAST/Shackle/Sacred Nitnem. Separate them by `c` vs `ch` for ਚ, and by `ṃ`/`ṁ`/`ṅ` for nasals.
  3. GurbaniAkhar test: many words containing `w`, `q`, `]`, or vowel-letter capitals in mid-word positions that are impossible in English, e.g. `siqnwmu`.
  4. Superscript `ⁿ` or subscripts → Gursevak.
  5. Mid-word capital `T`/`R` or `(n)` → BaniDB.
  6. Single `|` line end, `dt` → Shabad OS.
  7. `th`-dominant ਤ with `ae`/`eh` → legacy STTM.
  8. Title Case, `Ong`, `such`, `w` for ਵ, dropped medial schwa → devotional/informal.
- Line terminators are a cheap, strong feature: `||`/`||1||` (BaniDB, legacy), `|` (Shabad OS), `.`/`.1.` (BaniDB IPA), `]`/`]1]` (GurbaniAkhar).
- Short strings (single words like `waheguru`) will often be ambiguous between families. The detector should return ranked candidates, not a single answer.

### Gaps
- No verified signature list for Macauliffe, Gopal Singh, Manmohan Singh, Dr. Thind's srigranth "Roman notation", or learner books (pages blocked; no samples retrieved).
