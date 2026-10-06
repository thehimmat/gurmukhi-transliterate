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

Validated against the 5,959 Gurmukhi-bearing glossary head-words: 92% exact,
97% including flagged candidates. See `systems.py::SHACKLE` for the scheme and
the `notes` field for the rules the generic forward engine only approximates.

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

## Develop

```bash
pip install -e ".[dev]"
pytest
```

---

One of a suite of Gurmukhi and Gurbani tools. More at [thehimmat.com](https://thehimmat.com).
