# Gurmukhi word lists, lexicons and corpora for ranking candidate spellings in a reverse transliterator

Method note: besides web research, I downloaded the Shabad OS database npm package (`@shabados/database@5.0.0-next.0`, SQLite) and computed word-frequency statistics directly from it (scripts kept in the `scripts/` folder; not committed). Wherever a number says "computed here", it comes from that package. Tokenisation for those numbers: NFC-normalise each line, take maximal runs of Gurmukhi-block characters (U+0A00–U+0A7F), drop runs made only of Gurmukhi digits, and use the highest-priority `primary` reading per line. Punctuation such as `॥`, `;`, `,` and `.` (vishraam marks) therefore splits tokens and is thrown away. Some hosts (huggingface.co, wortschatz.uni-leipzig.de, data.statmt.org, cdn.jsdelivr.net) were blocked by the sandbox egress proxy. Facts from those sites come from search-engine snippets of their pages and are flagged as such.

## Q1. Gurbani-domain resources: frequency lists from SGGS, Dasam Granth, Bhai Gurdas and Bhai Nand Lal (BaniDB / Shabad OS); existing concordances and dictionaries

### Takeaway
The Shabad OS database is the best source here. It ships as a single SQLite file in Unicode Gurmukhi and states that its Gurbani and Panthic texts are in the public domain (its code is MIT). From it we can build a frequency list of the full Gurbani-domain corpus: about 926k tokens and 67.5k word types. Gzipped, that list is about 310 KB, or about 147 KB if we keep only words seen at least twice, which fits the "few MB" budget easily. BaniDB's code is MIT too, but its data is reached through an API or Docker image, and I found no explicit licence for the data. Digital versions of the Mahan Kosh and the SGGS dictionaries have no clear redistribution licence.

### Cited Findings
**Shabad OS database (shabados/database)**
- Licence. The code is under the MIT License, and the README says this "Applies to code and content resting outside of the `data` folder." For texts "inside the `data` folder, generated inside the `build` folder, and as releases (e.g. GitHub, npm)", the README says "most gurbani and panthic texts are free of known copyright restrictions. We identify it as being in the public domain [PDM 1.0] … Derogatory treatments (including adding to, deleting from, altering of, or adapting) the words in a way that distorts or mutilates the original work is forbidden." — [Shabad OS database README](https://raw.githubusercontent.com/shabados/database/main/README.md)
- Sources. The README cites physical sources, for example SGPC's *Shabadaarth* Vol. 1–4 (2009–2012) for SGGS, SGPC *Nitnem Te Hor Baniaa(n)* for parts of Dasam Granth, and Damdami Taksaal's *Shudh Ucharan* pothi for vishraams. Translations come from published works such as Prof. Sahib Singh's *Sri Guru Granth Darpan*, the Faridkot Teeka and Manmohan Singh's SGPC translation. — [Shabad OS database README](https://raw.githubusercontent.com/shabados/database/main/README.md)
- Distribution. The npm `latest` dist-tag is `5.0.0-next.0`, published 2025-05-05, with an unpacked size of 152 MB and an MIT licence field. The last non-prerelease line is 4.8.5–4.8.7 (2022-10-15). — [npm registry metadata for @shabados/database](https://registry.npmjs.org/@shabados/database)
- Format, computed here. The 47.6 MB tarball contains `dist/master.sqlite` (145 MB). Its tables are `sources`, `sections`, `line_groups`, `lines`, `asset_lines`, `assets`, `authors`, `banis` and `bani_lines`. The Gurbani text sits in `asset_lines` (type `primary`, 141,264 rows) and is already in **Unicode Gurmukhi**, not the legacy ASCII font encoding. There are also 479,256 translation rows (en/pa/es) and 49,486 note rows. — [@shabados/database 5.0.0-next.0 tarball](https://registry.npmjs.org/@shabados/database/-/database-5.0.0-next.0.tgz)
- Sources in the database, computed here: SGGS, SDGR (Dasam Granth), VBGJ (Vaaran Bhai Gurdas), KSBG (Kabitt Savaiye Bhai Gurdas), GJNL / ZNNL / GZNL / JBNL (Bhai Nand Lal: Ganj Nama, Zindagi Nama, Divan-i-Goya, Jot Bigas), SRBL (Sarbloh Granth, only 78 lines) and ARDS (Ardas). — [@shabados/database tarball](https://registry.npmjs.org/@shabados/database/-/database-5.0.0-next.0.tgz)
- Vocabulary sizes, computed here (lines / tokens / types / hapax legomena):
  - Dasam Granth (SDGR): 67,758 / 425,860 / 36,593 / 19,427
  - SGGS: 60,555 / 398,527 / 29,504 / 14,526
  - Vaaran Bhai Gurdas (VBGJ): 7,585 / 49,409 / 12,139 / 6,945
  - Kabitt Savaiye Bhai Gurdas (KSBG): 2,761 / 35,343 / 6,279 / 3,274
  - Bhai Nand Lal (four works combined): about 2,510 lines / 15,800 tokens. Separately: ZNNL 1,574 types, GZNL 1,893, JBNL 1,001, GJNL 768.
  - All sources: 141,264 lines / 925,705 tokens / **67,517 types** / 34,856 hapax
  — [@shabados/database tarball](https://registry.npmjs.org/@shabados/database/-/database-5.0.0-next.0.tgz)
- The SGGS figures computed here agree with published counts. SikhiWiki reports 398,697 total words and 29,445 "dictionary words" (distinct words) in SGGS, with ਹਰਿ/ਹਰ the most repeated word (9,288 times). — [SikhiWiki: Words in the Guru Granth Sahib](https://www.sikhiwiki.org/index.php/Words_in_the_Guru_Granth_Sahib). My counts are 398,527 tokens and 29,504 types, with ਹਰਿ at 10,609 across all sources.
- Coverage of the combined list, computed here: the top 100 types cover 24.4% of tokens, the top 1k 57.3%, the top 5k 80.2%, the top 10k 87.6%, the top 20k 93.2% and the top 30k 95.7%. — [@shabados/database tarball](https://registry.npmjs.org/@shabados/database/-/database-5.0.0-next.0.tgz)
- Embedding size, computed here. As a `word<TAB>count` TSV:
  - all 67.5k types: 1.26 MB raw, **311 KB gzip -9**
  - SGGS only: 528 KB raw, 132 KB gzipped
  - top 30k types: 135 KB gzipped
  - types with count ≥ 2 (32,661): 147 KB gzipped
  — [@shabados/database tarball](https://registry.npmjs.org/@shabados/database/-/database-5.0.0-next.0.tgz)
- Overlap between corpora, computed here:
  - Only 22.1% of Dasam Granth *types* also occur in SGGS, but 70.8% of Dasam *tokens* do.
  - SGGS vocabulary covers 83.8% of Bhai Gurdas tokens.
  - SGGS vocabulary covers only 34.4% of Bhai Nand Lal tokens, because those works are largely Persian written in Gurmukhi script.
  — [@shabados/database tarball](https://registry.npmjs.org/@shabados/database/-/database-5.0.0-next.0.tgz)

**BaniDB (Khalis Foundation)**
- The BaniDB-API repository is under the MIT License, "Copyright (c) 2019 Khalis Foundation". — [BaniDB-API LICENSE](https://github.com/KhalisFoundation/BaniDB-API/blob/master/LICENSE)
- BaniDB describes itself as having "over 43,000 corrections/changes" and as "the only database in the world that is being standardized for lagamatras (spelling) and padh chhedh (word separation) versus the … SGPC's published Gurbani pothis". For local development, contributors run a `khalisfoundation/banidb-dev` Docker image. The README does not describe a public bulk data dump or state a separate data licence. — [BaniDB-API README](https://github.com/KhalisFoundation/BaniDB-API)
- There is also a Python client, `banidb`, on PyPI for querying the API. — [banidb on PyPI](https://pypi.org/project/banidb)

**Dictionaries and concordances**
- The Mahan Kosh (*Gur Shabad Ratnakar Mahan Kosh*) by Bhai Kahn Singh Nabha was published on 13 April 1930. — [Wikipedia: Mahankosh](https://www.wikipedia.com/wiki/Mahankosh)
- A Unicode digital Mahan Kosh was "made available for all" by Bhai Baljinder Singh (Rara Sahib) at ik13.com, about 23 MB as of August 2002. I found no licence statement for it. — [PunjabOnline Gurmukhi index](https://punjabonline.com/gurmukhi/index.htm)

### Inferences
- **Copyright of a derived frequency list.** A word-frequency list made from Shabad OS's public-domain texts should be redistributable inside an MIT Python library. A frequency list neither "distorts" nor "mutilates" the text, so the moral-rights-style clause should not bite, but the library should credit Shabad OS and leave the text unaltered. The translations in the same SQLite file are separate copyrighted works (for example Prof. Sahib Singh, Manmohan Singh/SGPC). The PD statement covers "gurbani and panthic texts", so do **not** build the lexicon from the translation rows.
- **BaniDB vs Shabad OS.** BaniDB is said to be more closely aligned with SGPC spelling, but it offers no bulk dump with an explicit data licence. It is therefore a weaker basis for an embedded lexicon. It could still be used to cross-check spellings.
- **Size.** The whole Gurbani-domain list fits comfortably (about 0.15–0.3 MB gzipped). No pruning is needed for size; pruning hapaxes would mainly reduce noise.
- **Bhai Nand Lal.** These works are Persian in Gurmukhi script. They should be a separate, down-weighted sub-lexicon, or left out, so that Persian forms don't outrank Sant Bhasha forms.
- **Concordances.** The type counts of existing SGGS concordances (about 29.4k) are matched by what can be computed directly. Licensing a printed concordance therefore adds little apart from lemma/meaning information, which a ranker doesn't need.

### Gaps
- I could not verify the licence of the SGPC/Punjabi University *Gurbani Shabdarth* or *SGGS Kosh* digital editions, or of the online Gurbani concordance at gurbanifiles/srigranth. No primary licence pages were found, so treat them as all-rights-reserved.
- I did not compute BaniDB vocabulary sizes. There was no bulk data access, and the API would need many calls.
- Shabad OS's GitHub `data/` folder licence file could not be fetched: the GitHub API is blocked for this repo in the sandbox, and LICENSE.md only covers code. The PD statement is quoted from the README.
- Shabad OS `5.0.0-next.0` is a prerelease. Whether it has spelling differences from the 4.8.x line was not checked.

## Q2. Modern Punjabi corpora and word lists: sizes, licences, quality issues

### Takeaway
Among large modern Punjabi (Gurmukhi) sources, AI4Bharat's IndicCorp v2 stands out. Its Punjabi part is about 773M tokens of news text, released CC0, which suits an embedded frequency list best. The other options:
- Wikipedia (pa) is smaller and CC BY-SA.
- OSCAR, CC-100 and MADLAD-400 are Common Crawl derivatives with weaker or less clear licensing and more noise.
- The Leipzig corpora are CC BY.
- EMILLE is restricted to research use.
- wordfreq does **not** support Punjabi. I could not verify whether hermitdave/FrequencyWords has a Punjabi list.

### Cited Findings
**IndicCorp v2 (AI4Bharat)**
- Data licence: "All the datasets created as part of this work will be released under a CC-0 license and all models & code will be release under an MIT license." The corpus totals 20.9B tokens across 24 languages and is distributed on Hugging Face (`ai4bharat/IndicCorpV2`). — [AI4Bharat IndicBERT README](https://github.com/AI4Bharat/IndicBERT)
- Punjabi (`pa`, file `data/pa.txt`, pan_Guru): 29.2M sentences and 773M tokens. The search snippet also mentioned 2.64M news articles. Of the 20.9B total tokens, 14.4B are Indic and 6.5B are Indian English. This comes from a search-engine snippet of the HF dataset card, because huggingface.co was blocked. — [IndicCorpV2 README (HF)](https://huggingface.co/datasets/ai4bharat/IndicCorpV2/blob/main/README.md)

**Wikipedia (pa) and the separate Shahmukhi Wikipedia (pnb)**
- The Gurmukhi Punjabi Wikipedia has 59,725 articles (104th largest). The Shahmukhi Punjabi Wikipedia (pnb) has 75,754 articles (90th largest). — [Wikipedia: Punjabi Wikipedia](https://en.wikipedia.org/wiki/Punjabi_Wikipedia)
- Punjabi Wikipedia passed 50,000 articles in 2023. — [Global Voices, 2023](https://globalvoices.org/2023/06/20/punjabi-wikipedia-for-21-years-celebrating-50000-articles-and-looking-ahead/)
- Wikipedia text is licensed CC BY-SA. — [Wikipedia: Copyrights](https://en.wikipedia.org/wiki/Wikipedia:Copyrights)

**OSCAR 23.01**
- The Punjabi (pa) subcorpus is 1.1 GB: 68,094 documents and 70,068,604 space-separated words. — [OSCAR 23.01 release notes](https://oscar-project.org/post/news-23-01/)

**CC-100**
- The Punjabi (pa) file is listed at 90M (search snippet of the HF dataset card). — [statmt/cc100 on HF](https://huggingface.co/datasets/statmt/cc100)

**MADLAD-400**
- 419 languages, document-level, built from Common Crawl. It has a "noisy" split (document-level LangID only) and a "clean" split (filtered, but "naturally has a fair amount of noise itself"). The dataset licence is **ODC-By**. The Punjabi row of the language table could not be retrieved (HF blocked). — [MADLAD-400 dataset card](https://huggingface.co/datasets/allenai/MADLAD-400/blob/01ad5c885296970ecf9828c14218b8fd75436774/README.md); [MADLAD-400 paper](https://arxiv.org/pdf/2309.04662)

**Leipzig Corpora Collection**
- Downloads are "normed size corpora" of 10k, 30k, 100k, 300k or 1M random sentences. "All corpora provided for download are licensed under CC BY." Each corpus also ships a word-frequency list file (see the format document). — [Leipzig download page](https://wortschatz.uni-leipzig.de/en/download); [Format of download files (PDF)](https://www.wortschatz.uni-leipzig.de/public/documents/Format_Download_File-eng.pdf)
- Western Panjabi (pnb, Shahmukhi) is a **separate language code**. For example, `pnb_community_2017` has 1,052,347 tokens, 64,365 types and 63,683 sentences. — [Leipzig corpus info: pnb](https://curl.corpora.uni-leipzig.de/languages/pnb)

**EMILLE**
- A corpus of 14 South Asian languages including Punjabi, distributed by ELRA, with about 92.8M words of monolingual text in total (including 2.6M words of transcribed speech for Bengali, Gujarati, Hindi, Punjabi and Urdu). The EMILLE/CIIL corpus (ELRA-W0037) is free **for non-profit research only**. The EMILLE Lancaster Corpus (ELRA-W0038) is a commercial licence. — [EMILLE project page](https://www.lancaster.ac.uk/fass/projects/corpus/emille/); [ISLRN record](https://www.islrn.org/resources/039-846-040-604-0/)

**wordfreq**
- The supported-language table covers ar, bn, bs, bg, ca, zh, hr, cs, da, nl, en, fi, fr, de, el, he, hi, hu, is, id, it, ja, ko, lv, lt, mk, ms, nb, fa, pl, pt, ro, ru, sk, sl, sr, es, sv, fil, ta, tr, uk, ur and vi. **Punjabi (pa) is not listed.** The code is Apache-2.0 and the data CC BY-SA 4.0. — [wordfreq README](https://github.com/rspeer/wordfreq)

**hermitdave/FrequencyWords**
- Lists are generated from OpenSubtitles 2016/2018 in `word count` format. Licence: "MIT License for code. CC-by-sa-4.0 for content." — [FrequencyWords README](https://github.com/hermitdave/FrequencyWords)

**Other**
- LDC-IL publishes "A Gold Standard Punjabi Raw Text Corpus". Its licence terms were not retrieved. — [LDC-IL](https://data.ldcil.org/a-gold-standard-punjabi-raw-text-corpus)

### Inferences
- **Licensing for an embedded list.** Only CC0 (IndicCorp v2) avoids attribution and share-alike obligations when the derived list ships inside an MIT library. A frequency list derived from CC BY (Leipzig) needs attribution. One derived from CC BY-SA (Wikipedia, wordfreq, FrequencyWords) may make the shipped data file CC BY-SA. That is workable if the data file is licensed separately from the code. EMILLE cannot be used in a redistributable library.
- **Domain and spelling.** IndicCorp v2 is news-domain (formal register), so it suits modern-Punjabi input but not Gurbani spelling (see Q3).
- **Shahmukhi contamination.** Shahmukhi is Arabic script, so any token with a code point outside U+0A00–U+0A7F (plus ZWJ/ZWNJ if they are kept) can simply be dropped. Gurmukhi-script contamination from Hindi or Sanskrit loans and from English transliterations is harder to filter. A minimum count threshold (for example ≥ 5) handles most remaining noise.
- **Size estimate.** A modern-Punjabi top-100k list would likely be about 1–2 MB gzipped, extrapolated from the Gurbani list at about 4.5 bytes per entry gzipped. That is within budget; a top-50k cut would roughly halve it.

### Gaps
- The Leipzig *Panjabi (pan)* corpus names, years and sizes could not be retrieved (site blocked; search only surfaced pnb).
- I could not confirm whether FrequencyWords has `pa` lists. Raw-URL probes returned 404 even for known languages such as `hi`, so the probe was inconclusive. OpenSubtitles Punjabi coverage, if it exists, would be tiny.
- IndicCorp **v1** Punjabi size and licence were not verified in this session. My recollection is a few hundred million tokens under a non-commercial licence, but treat this as unverified.
- The CC-100 licence/terms, the OSCAR access terms (gated on HF) and the MADLAD-400 Punjabi row were not verified from primary pages.
- I found no published measurements of Shahmukhi or Devanagari contamination rates, or of nukta-form inconsistency, in the Punjabi portions of these corpora.

## Q3. How much do Gurbani spellings differ from modern Punjabi spellings? Does that argue for separate lexicons?

### Takeaway
They differ a great deal. In SGGS, about 15% of tokens end in aunkar (ੁ) and 17% in sihari (ਿ). In a modern Punjabi gloss of the same text the figures are 0.07% and 1.0%. Only 14% of SGGS word types occur in modern-Punjabi vocabulary, and SGGS uses no addak (ੱ) at all, whereas modern Punjabi uses it in about 5% of tokens. This strongly supports **separate, domain-tagged lexicons**, or at least separate counts, rather than one merged list.

### Cited Findings
All figures below were computed here from the Shabad OS SQLite. The "modern Punjabi" comparison set is Prof. Sahib Singh's Punjabi translation (asset PSST): 1,172,556 tokens, 15,992 types. This is a modern-prose gloss of the same content, which limits topic confound. Note that it sometimes quotes Gurbani words in parentheses, which inflates overlap. — [@shabados/database tarball](https://registry.npmjs.org/@shabados/database/-/database-5.0.0-next.0.tgz)

**Word-final aunkar and sihari (share of tokens)**

| Corpus | Final aunkar ੁ | Final sihari ਿ |
|---|---|---|
| SGGS | 15.2% | 16.9% |
| Dasam Granth | 3.4% | 11.3% |
| Modern Punjabi translation | 0.07% | 1.03% |

**Overlap with modern vocabulary**
- 14.0% of SGGS types occur in the modern translation vocabulary, covering 54.7% of SGGS tokens.
- After stripping a word-final aunkar or sihari on both sides, token coverage rises to 67.4%.

**Frequent SGGS forms absent from the modern vocabulary**
ਮਨਿ, ਬਿਨੁ, ਮਹਿ, ਤਿਸੁ, ਸਭੁ, ਸਬਦਿ, ਸੁਖੁ, ਪ੍ਰਸਾਦਿ, ਘਰਿ, ਜਿਉ, ਕਿਛੁ, ਗੁਰਿ, ਕਹੁ, ਘਰੁ, ਨਾਨਕੁ, ਤੁਧੁ, ਫਿਰਿ, ਏਕੁ, ਘਟਿ, ਜਨੁ, ਅਨਦਿਨੁ, ਜਿਤੁ.

**One lemma, several inflected spellings**
- ਨਾਮੁ 3,401, ਨਾਮ 856, ਨਾਮਿ 654, ਨਾਮੈ 54
- ਸੰਤ 691, ਸੰਤੁ 48, ਸੰਤਹੁ 93

**Nasal and gemination marks (tokens containing each)**

| Mark | SGGS (398.5k tokens) | Modern translation (1.17M tokens) |
|---|---|---|
| Tippi ੰ | 21,661 | 79,180 |
| Bindi ਂ | 1,976 | 131,388 |
| Addak ੱ | **0** | 63,044 |

Across the whole Gurbani corpus, addak occurs 1,168 times (Dasam Granth, Bhai Gurdas and others).

**Nukta and special characters**
- SGGS in Shabad OS has **zero** nukta-bearing words.
- Nukta letters do occur elsewhere in the Gurbani corpus: U+0A36 ਸ਼ 3,101 times, U+0A5B ਜ਼ 2,704, ਖ਼ 1,483, ਫ਼ 1,093, ਗ਼ 455. These are mostly in Dasam Granth and the Persian works.
- Gurbani-specific code points:
  - udaat U+0A51: 1,189 occurrences in 314 types
  - yakash U+0A75: 269 occurrences in 181 types
  - adak bindi U+0A01: 28 occurrences
  - visarga U+0A03: 947 occurrences (for example ਮਃ)
- Subscript letters written with virama U+0A4D (for example ਪ੍ਰਭੁ, ਅੰਮ੍ਰਿਤੁ) occur in 1,029 SGGS types and 4,567 types across the whole corpus.

### Inferences
- In SGGS orthography, word-final aunkar and sihari act as grammatical (case/number) markers, not pronounced vowels in the modern sense. This matches the near-absence of final aunkar in modern prose seen above. Romanised input will often drop these vowels (for example "naam" vs ਨਾਮੁ), so the reverse transliterator has to generate the marked variants as candidates and let a Gurbani-domain lexicon choose between them. A modern lexicon would systematically prefer the unmarked form.
- A modern lexicon would also push candidates towards addak and bindi spellings that never occur in SGGS. Using it to rank Gurbani candidates would therefore actively hurt.
- **Recommended design.** Keep two counts per word (Gurbani and modern), or two lists. Select the domain from context or from a user flag, or by detecting Gurbani-typical features in the input (for example "mahala", "rahau", frequent final -u/-i). Use the other lexicon only as a back-off, with a penalty.
- **Dasam Granth vs SGGS.** Dasam Granth has much less final aunkar (3.4% vs 15.2%) and a much larger Braj/Sanskritised vocabulary (only 22% of its types appear in SGGS). Keeping per-source counts, even if they ship merged, lets the ranker weight SGGS higher for typical kirtan/nitnem input.

### Gaps
- The modern comparison set is a single author's mid-20th-century gloss, not contemporary news. Running the same measurement on IndicCorp v2 would give a cleaner modern baseline; this was not done because the download was blocked.
- I did not retrieve a primary grammatical source (for example Prof. Sahib Singh's *Gurbani Viakaran*) to cite the case-marker function of final aunkar and sihari. That point is inferred from the data and from general knowledge.

## Q4. What normalisation to apply before counting (NFC, nukta, tippi/bindi, addak, etc.)

### Takeaway
Use NFC. Be aware that for the six nukta letters, NFC (and NFD) produce the **decomposed** sequence (base + U+0A3C). This is because U+0A33, U+0A36, U+0A59, U+0A5A, U+0A5B and U+0A5E are composition exclusions. Normalise the lexicon and the candidates the same way. Keep tippi/bindi and addak distinctions in the stored keys (they are real spelling differences, and folding bindi into tippi merges only 41 of 67.5k types). Strip only presentation-level noise: ZWJ/ZWNJ, vishraam punctuation, digits and Shahmukhi or Latin text. Treat udaat (U+0A51) and adak bindi (U+0A01) as optional, foldable marks.

### Cited Findings
- U+0A36 GURMUKHI LETTER SHA canonically decomposes to U+0A38 + U+0A3C and is listed in CompositionExclusions.txt, so it is not recomposed under NFC. — [codepoints.net U+0A36](https://codepoints.net/U+0A36); [Unicode Gurmukhi chart](https://www.unicode.org/charts/PDF/U0A00.pdf)
- Unicode list discussion confirms that script-specific composition exclusions exist because, for these characters, the decomposed form is preferred in regular use. — [Unicode mailing list, Oct 2024](https://corp.unicode.org/pipermail/unicode/2024-October/011095.html)
- Computed here with Python `unicodedata`: NFC and NFKC map U+0A36→0A38+0A3C, U+0A33→0A32+0A3C, U+0A59→0A16+0A3C, U+0A5A→0A17+0A3C, U+0A5B→0A1C+0A3C and U+0A5E→0A2B+0A3C. The raw Shabad OS text stores these letters **precomposed** (for example U+0A36 3,101 times, standalone U+0A3C 0 times). A list counted on raw text and queried with NFC strings would therefore silently miss every nukta word. — [@shabados/database tarball](https://registry.npmjs.org/@shabados/database/-/database-5.0.0-next.0.tgz)
- Folding effects, computed here on the 67,517-type Gurbani vocabulary:
  - bindi→tippi folding reduces it to 67,476 types (−41)
  - removing udaat U+0A51 and adak bindi U+0A01 reduces it to 67,274 types (−243)
  - SGGS bindi words include ਤਾਂ, ਸਾਂਤਿ, ਹਾਂ, ਜਾਂ, ਭਾਂਤਿ, ਕਹਾਂ and ਜਨਾਂ
  — [@shabados/database tarball](https://registry.npmjs.org/@shabados/database/-/database-5.0.0-next.0.tgz)

### Inferences
**Recommended pipeline, applied identically when building the list and when looking up candidates:**
1. Apply `unicodedata.normalize("NFC", s)`. This yields decomposed nukta letters. Optionally convert to a single canonical form of your own, but do so consistently.
2. Remove ZWJ/ZWNJ (U+200D/U+200C), which appear in some modern text around virama/subscript forms.
3. Tokenise on runs of U+0A00–U+0A7F, excluding the danda/double danda (U+0964/U+0965, which sit outside the Gurmukhi block anyway) and Gurmukhi digits U+0A66–U+0A6F.
4. Drop tokens containing Arabic-script (Shahmukhi), Devanagari or Latin characters.
5. Keep tippi vs bindi, addak, final aunkar/sihari, virama subscripts and nukta in the key, because these are exactly the distinctions the ranker has to choose between.
6. Optionally keep a second, "loose" key that folds udaat, adak bindi, nukta and bindi/tippi. Use it to back off when the exact key is missing.

**Other points**
- **Modern text.** Modern sources mix nukta and non-nukta spellings (for example ਸ/ਸ਼, ਜ/ਜ਼) and precomposed vs decomposed forms. Counting after NFC merges the encoding variants but keeps the spelling variants. That is the right behaviour for a ranker, which should learn the spelling users expect.
- **Gurbani spelling of loanwords.** Because SGGS has no nukta, a Gurbani-domain ranker should never prefer a nukta form for an SGGS word.

### Gaps
- There are no published statistics on how often modern Punjabi corpora (IndicCorp, Wikipedia) use precomposed vs decomposed nukta letters, or how often they contain the stray ZWJ/ZWNJ. Measuring this would require downloading the corpora.

## Q5. Recommendation: primary and fallback lexicon (catalogue summary)

### Takeaway
**Primary:** a Gurbani-domain frequency list built from the Shabad OS SQLite, with per-source counts (SGGS, Dasam Granth, Bhai Gurdas; Bhai Nand Lal and Sarbloh separate or excluded). Licence: public domain texts with MIT tooling. Size: about 67.5k types, about 150–310 KB gzipped. **Fallback:** a modern Punjabi list derived from IndicCorp v2 `pa` (CC0, about 773M tokens), cut to the top 50–100k Gurmukhi-only types (est. 0.5–2 MB gzipped). If IndicCorp v2 cannot be fetched, use a Punjabi Wikipedia (pa) dump with the derived data file marked CC BY-SA.

### Cited Findings
**Catalogue, from the sources cited in Q1–Q2**

| Resource | Domain | Size | Format | Licence | Fit for embedded list |
|---|---|---|---|---|---|
| Shabad OS database | Gurbani / Panthic | 926k tokens, 67.5k types (computed) | SQLite in npm tarball (47.6 MB) | Texts PD (PDM 1.0) + moral clause; code MIT | Excellent |
| BaniDB | Gurbani | Not measured | API / Docker dev image | Code MIT; data licence not stated | Cross-check only |
| Mahan Kosh (digital) | Gurbani lexicon | ~23 MB file (2002) | Unicode document | Not stated | Poor (licence unclear) |
| IndicCorp v2 pa | Modern news | 29.2M sentences, 773M tokens | Plain text | CC0 | Excellent |
| Wikipedia pa | Modern encyclopedic | 59,725 articles | XML dump | CC BY-SA | Good (share-alike) |
| OSCAR 23.01 pa | Web | 70.1M words, 1.1 GB | JSONL | Not verified (gated) | Fair |
| CC-100 pa | Web | ~90M (file) | Plain text | Not verified | Fair |
| MADLAD-400 pa | Web | Row not retrieved | JSONL | ODC-By | Fair |
| Leipzig (pan) | Mixed | Not retrieved | Sentence + word-frequency files | CC BY | Good (attribution) |
| EMILLE/CIIL | Mixed | Part of 92.8M words | ELRA | Non-profit research only | Unusable |
| wordfreq | — | No `pa` | — | Apache / CC BY-SA | N/A |
| FrequencyWords | Subtitles | `pa` unverified | `word count` | CC BY-SA 4.0 | Unknown |

Sources for the table: [Shabad OS README](https://raw.githubusercontent.com/shabados/database/main/README.md); [npm @shabados/database](https://registry.npmjs.org/@shabados/database); [BaniDB-API](https://github.com/KhalisFoundation/BaniDB-API); [PunjabOnline (Mahan Kosh)](https://punjabonline.com/gurmukhi/index.htm); [IndicBERT README](https://github.com/AI4Bharat/IndicBERT); [IndicCorpV2 card](https://huggingface.co/datasets/ai4bharat/IndicCorpV2/blob/main/README.md); [Punjabi Wikipedia](https://en.wikipedia.org/wiki/Punjabi_Wikipedia); [OSCAR 23.01](https://oscar-project.org/post/news-23-01/); [statmt/cc100](https://huggingface.co/datasets/statmt/cc100); [MADLAD-400 card](https://huggingface.co/datasets/allenai/MADLAD-400/blob/01ad5c885296970ecf9828c14218b8fd75436774/README.md); [Leipzig download](https://wortschatz.uni-leipzig.de/en/download); [EMILLE](https://www.lancaster.ac.uk/fass/projects/corpus/emille/); [wordfreq](https://github.com/rspeer/wordfreq); [FrequencyWords](https://github.com/hermitdave/FrequencyWords).

### Inferences
**Suggested build steps**
1. Use a build-time script (not shipped) to download `@shabados/database`, read `asset_lines` where `type='primary'` (best priority per `line_id`) joined to `sources`, normalise as in Q4, and count per source.
2. Emit a single TSV of `word, sggs, dasam, gurdas, other`, compressed with gzip. Expected size is about 300–400 KB including all hapaxes, or about 150 KB with count ≥ 2. Include an attribution file.
3. Build the modern list the same way from IndicCorp v2 `pa.txt`. Streaming the 773M tokens with a Counter is feasible offline. Keep Gurmukhi-only tokens with count ≥ 5 and the top 50–100k types.

**Ranking scheme**
- Score candidates as log P(word | domain), with add-k smoothing and a back-off to the other domain's list at a fixed penalty.
- Default to the Gurbani domain for this project's use case (Gurbani/Sant Bhasha romanisation), and switch to modern when input features suggest it.
- For candidates absent from both lists, fall back to the "loose" key or a character n-gram model trained on the same Gurbani text.

**Licence hygiene**
- Ship the Gurbani list with credit to Shabad OS and a note that the source texts are public domain.
- Ship the IndicCorp-derived list as CC0, with optional attribution.
- If Wikipedia is used, license that data file CC BY-SA 4.0 separately from the MIT code.

### Gaps
- I did not benchmark ranking accuracy, so the choice between the Gurbani-only list, the modern-only list and a mixture is not empirically validated.
- I could not confirm that IndicCorp v2 can be downloaded without a gated agreement.
- The modern-list size estimate (0.5–2 MB) is extrapolated, not measured.
