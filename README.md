# Gurmukhi Transliterate

Gurmukhi script transliteration: **ISO 15919** academic transliteration, a readable **practical**
romanization, and **legacy** font conversion. A small Python library with a matching HTTP API
(deployable to Vercel) and a browser demo.

## What's inside

- `gurmukhi_transliterate/`: the library, with three transliterators:
  - `GurmukhiISO15919`: standards-compliant academic transliteration
  - `GurmukhiPractical`: readable, pronunciation-oriented romanization
  - `GurmukhiLegacy`: converts older ASCII or legacy Gurmukhi font encodings to Unicode
  - plus data-driven systems in `systems.py` (Dr. Sant Singh, Dr. Thind, STTM,
    Gursevak, **Shackle**, IPA, …) via `GurmukhiRomanizer`
  - **reverse** direction: `reverse_transliterate` / `CorpusMatcher` turn
    Shackle romanization back into Gurmukhi (see below)
- `api/`: serverless endpoints (transliterate, compare, identify, legacy) for Vercel
- `index.html`: a minimal browser demo
- `tests/`: unit tests for each transliterator

## Reverse transliteration (Shackle → Gurmukhi)

Christopher Shackle's phonemic transcription (*A Guru Nanak Glossary*) preserves
the distinctions Gurmukhi marks but most romanizations collapse, so it can be
turned back into Gurmukhi. Because the transcription is phonemic (not 1:1), a
few cases are genuinely ambiguous — the engine emits a **primary** spelling plus
flagged alternatives, and an optional corpus matcher picks the attested one.

```python
from gurmukhi_transliterate import reverse_transliterate, shackle_to_gurmukhi

shackle_to_gurmukhi('sravaṇu')        # → 'ਸ੍ਰਵਣੁ'
res = reverse_transliterate('sāṁ')    # res.gurmukhi → 'ਸਾੰ'
res.ambiguities                        # [Ambiguity(kind='nasalization', …)]
```

Resolve ambiguities against a real word list (the library stays corpus-agnostic
— you inject the lexicon; e.g. the glossary head-words ∪ the SGGS word index):

```python
from gurmukhi_transliterate import CorpusMatcher

matcher = CorpusMatcher({'ਸਾਂ': 40, 'ਸੰਤ': 691, ...})   # {word: frequency}
m = matcher.match('sāṁ')
m.best        # → 'ਸਾਂ'  (most frequent attested candidate; primary if none match)
m.matches     # ranked in-corpus candidates
```

Accuracy on real Shackle text: 92% exact, 97% including flagged candidates, on
the 5,959 Gurmukhi-bearing head-words of *A Guru Nanak Glossary*. This was
measured on 2026-07-22 (commit `1677fa4`). The glossary is a copyrighted book
and isn't in the repo, so this figure can't be re-run from here.

The reproducible check is a round trip: the 1,951 distinct words of the gold
lines (tests/fixtures/gold/) are romanized with our Shackle map and reversed.
It gives 96.1% exact and 97.3% including flagged candidates; run
`python tools/eval.py` and see `docs/eval/baseline.md`. A round trip only tests
the engine against our own forward map, so expect real transcriptions to score
lower. See `systems.py::SHACKLE` for the scheme and the `notes` field for the
rules the generic forward engine only approximates.

## Install

```bash
pip install -e .
```

```python
from gurmukhi_transliterate import GurmukhiISO15919, GurmukhiPractical, GurmukhiLegacy
```

### Legacy font conversion

`GurmukhiLegacy.to_unicode` converts AnmolLipi/GurbaniAkhar-encoded text to Unicode.
It keeps line structure exactly (same newlines in and out) and never drops input:
ASCII punctuation passes through, and anything unmapped is kept and logged.
Use `convert` to get those warnings as data:

```python
GurmukhiLegacy.to_unicode('ikæsmq')      # 'ਕ਼ਿਸਮਤ' (consonant, nukta, sihari)
result = GurmukhiLegacy.convert('kèk')
result.text                               # 'ਕèਕ'
result.warnings                           # [ConversionWarning(position=1, char='è', kind='unmapped', ...)]
```

`detect_encoding` guesses whether text is `'unicode'`, `'anmollipi'` (GurbaniAkhar family),
`'latin'` (English or romanised text — don't run it through the legacy converter) or
`'unknown'`. `detect_lines` returns one `EncodingGuess(label, score)` per line, for pages
that mix legacy-font verses with romanised headings.

```python
GurmukhiLegacy.detect_encoding('Awid scu jugwid scu ]')   # 'anmollipi'
GurmukhiLegacy.detect_encoding('Hanūmān Nāṭak')           # 'latin'
```

`conversion_report(text)` bundles all of this into one JSON-ready dict, which is what
`GET /api/legacy?text=…` returns:

```json
{"unicode": "ਕèਕ", "encoding": "latin",
 "lines": [{"label": "latin", "score": 1.0}],
 "warnings": [{"position": 1, "char": "è", "kind": "unmapped", "message": "no mapping; passed through"}]}
```

Real-text regression fixtures live in `tests/fixtures/legacy/` as parallel
`<name>.gurbaniakhar.txt` / `<name>.unicode.txt` files, compared line by line.

## Real-world schemes

- **`sttm`** and **`banidb_ipa`** match BaniDB / SikhiToTheMax output byte for byte.
  They run a line-for-line Python port of Khalis Foundation's
  [anvaad-js](https://github.com/KhalisFoundation/anvaad-js) (MIT; the licence is
  in `gurmukhi_transliterate/_anvaad_tables.py`), which is the code that produces
  BaniDB's `english` and `ipa` fields. It's checked against 1,200 lines in
  `tests/test_conformance.py`.
- **`shabados`** reproduces Shabad OS English (`gurmukhi-utils` toEnglish). It's a
  clean-room reimplementation built only from that library's output, so it's
  close rather than exact: 96.9% of held-out lines and 99.5% of words match.
- **Informal and 3HO spellings** (`Waheguru`, `Sat Sri Akal`, `Ek Ong Kaar`,
  `Japji Sahib`, `Khalsa`, …) are covered by a table of 96 common terms and their
  variants in `informal.py`. `reverse_words(..., system='informal')` uses it, and
  `to_gurmukhi` tries it first. Matching ignores case, spacing, `w`/`v`, and
  `ee`/`i`, `oo`/`u` and doubled letters.

## Verse matching (romanized or noisy Gurbani → canonical Gurmukhi)

`match_verse` finds the canonical line for Gurbani written in any common
romanization (BaniDB/SikhiToTheMax, Shabad OS, ISO, IAST, IPA, informal), in
GurbaniAkhar ASCII, or as OCR-damaged Unicode. It searches the ~141k lines of
Guru Granth Sahib, Dasam Granth, Bhai Gurdas and Bhai Nand Lal bundled with the
package, and returns an empty list when nothing matches confidently.

```python
from gurmukhi_transliterate import match_verse, to_gurmukhi

m = match_verse('kiv sachiaaraa hoieeaai kiv kooRai tuTai paal')[0]
m.gurmukhi, m.source, m.page     # ('ਕਿਵ ਸਚਿਆਰਾ ਹੋਈਐ ਕਿਵ ਕੂੜੈ ਤੁਟੈ ਪਾਲਿ ॥', 'sggs', 1)
m.locations                      # every place the line occurs (repeated lines share one match)

to_gurmukhi('hukam rajaiee chalanaa naanak likhiaa naal')   # 'ਹੁਕਮਿ ਰਜਾਈ ਚਲਣਾ ਨਾਨਕ ਲਿਖਿਆ ਨਾਲਿ ॥੧॥'
to_gurmukhi('mera phone kharab ho gaya')                    # raises UnableToReverse
```

`to_gurmukhi` falls back to word-by-word reverse (below) for lines that aren't verses.

On real romanized lines it gets about 99.5% top-1 and 100% top-3. Lines of three
or more words can match a half-line (the start or end of a verse); shorter
headings must match a whole line. The index is built on first use, which takes
a few seconds; after that a query takes about 10 ms. Numbers and method are in
`docs/eval/baseline.md`.

## Word-by-word reverse for a known system

For romanized text that isn't a Gurbani line (single words, glossary terms,
names), `reverse_words` looks each word up in an index built from the bundled
lexicon, romanized forward with the system:

```python
from gurmukhi_transliterate import reverse_words

r = reverse_words('naanak', system='sttm')
r.gurmukhi                       # 'ਨਾਨਕ'
r.words[0].candidates            # (('ਨਾਨਕ', 4797), ...) best first, by frequency
reverse_words('satigur prasaadi').system    # picked automatically when not given
reverse_words('naanak xyzzy').missing       # ['xyzzy']; gurmukhi is None, nothing is guessed
```

`to_gurmukhi` tries a verse match first and falls back to this. If a word has
no known spelling it raises `UnableToReverse` and names the word. Words outside
the lexicon (and spellings the system maps don't produce yet, see #26) aren't
reversed. An index is built the first time each system is used, which takes
about a second.

## English or romanized? Which system?

`detect_latin` tells English from romanized Gurmukhi, line by line and word by
word. `identify_system` ranks the romanization systems that could have written
a line. Both score words with character-trigram models: one per system, trained
on its romanization of the bundled lexicon, and one for English, trained on
SCOWL.

```python
from gurmukhi_transliterate import detect_latin, identify_system

detect_latin('The English translation of the text').label   # 'english'
detect_latin('mera phone kharab ho gaya').label             # 'romanized'
detect_latin('Guru Gobind Singh').label                     # 'unknown' (names only: abstains)

identify_system('kiv sachiaaraa hoieeaai kiv kooRai tuTai paal')[0]
# {'system': 'sttm', 'label': ..., 'confidence': 0.999, 'equivalent': True}
identify_system('Sat Sri Akal')[0]['system']                 # 'informal'
identify_system('The quick brown fox', include_english=True)[0]['system']  # 'english'
```

`equivalent` marks the systems the text can't tell apart from the best one,
for example IAST and Shackle, which write most lines identically. On gold
lines of 5+ words, the true system is ranked first or marked equivalent to it
95–100% of the time (`docs/eval/baseline.md`). `to_gurmukhi` refuses lines that
read as English, and `reverse_words` tries systems in `identify_system`'s order.

## Develop

```bash
pip install -e ".[dev]"
pytest
python tools/eval.py          # scores against real romanized text; see docs/eval/baseline.md
```

### Bundled word list

`gurmukhi_transliterate.lexicon.load_lexicon()` returns word counts for Gurbani
(Guru Granth Sahib, Dasam Granth, Bhai Gurdas and Bhai Nand Lal), taken from
the public-domain Shabad OS database. You can pass a list of sources, e.g.
`load_lexicon(['sggs'])`. Provenance is in `gurmukhi_transliterate/data/README.md`.
Rebuild it with `python tools/build_lexicon.py master.sqlite`.

### Evaluation data

`tests/fixtures/gold/` holds 500 public-domain lines, each romanized by the
scheme's own code (BaniDB's `anvaad-js`, Shabad OS's `gurmukhi-utils`), plus
English negatives. Rebuild it with `python tools/build_gold.py master.sqlite`
(needs Node/npm). `tools/eval.py --dakshina DIR` also scores the Dakshina
Punjabi test set, which isn't committed because it's CC BY-SA.

---

One of a suite of Gurmukhi and Gurbani tools. More at [thehimmat.com](https://thehimmat.com).
