---
id: US-003
title: Legacy font/encoding conversion to Unicode
status: delivered
created: 2026-07-22
updated: 2026-10-08
linked_issues: [4, 19]
linked_tests: [tests/test_detect_encoding.py, tests/test_legacy.py, tests/test_legacy_fixtures.py, tests/test_legacy_fonts.py]
supersedes: null
superseded_by: null
---

## Story

As someone with old documents, I want legacy ASCII/font Gurmukhi converted to Unicode, so older texts work in modern tools.

## Acceptance criteria

- Converts legacy ASCII/font Gurmukhi encodings to Unicode.
- Supports the common font layouts: GurbaniAkhar/AnmolLipi family, Asees, Joy, AnandpurSahib, Satluj, SONY.
- Detects the likely layout from the text (lexicon-based), and accepts a font-name hint.
- Leaves English and romanized lines in the same document untouched.

## Evidence

- `legacy.py`, `_legacy_layouts.py`
- `tests/fixtures/legacy/`: hand-checked real documents

## Notes

Related: #4, #19.
