# Gurmukhi Transliterate

Gurmukhi script transliteration: **ISO 15919** academic transliteration, a readable **practical**
romanization, and **legacy** font conversion. A small Python library with a matching HTTP API
(deployable to Vercel) and a browser demo.

## What's inside

- `gurmukhi_transliterate/` — the library, with three transliterators:
  - `GurmukhiISO15919` — standards-compliant academic transliteration
  - `GurmukhiPractical` — readable, pronunciation-oriented romanization
  - `GurmukhiLegacy` — converts older ASCII / legacy Gurmukhi font encodings to Unicode
- `api/` — serverless endpoints (transliterate, compare, identify, legacy) for Vercel
- `index.html` — a minimal browser demo
- `tests/` — unit tests for each transliterator

## Install

```bash
pip install -e .
```

```python
from gurmukhi_transliterate import GurmukhiISO15919, GurmukhiPractical, GurmukhiLegacy
```

## Develop

```bash
pip install -e ".[dev]"
pytest
```

---

One of a suite of Gurmukhi / Gurbani tools. More at [thehimmat.com](https://thehimmat.com).
