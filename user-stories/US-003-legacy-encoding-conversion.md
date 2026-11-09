---
id: US-003
title: Legacy font/encoding conversion to Unicode
status: delivered
created: 2026-07-22
updated: 2026-11-09
linked_issues: [4, 19]
linked_tests: [tests/test_detect_encoding.py, tests/test_legacy.py, tests/test_legacy_fixtures.py, tests/test_legacy_fonts.py, tests/test_legacy_mac_paste.py]
supersedes: null
superseded_by: null
---

## Story

As someone with old documents, I want legacy ASCII/font Gurmukhi converted to Unicode, so older texts work in modern tools.

## Acceptance criteria

- Converts legacy ASCII/font Gurmukhi encodings to Unicode.
- Supports the common font layouts: GurbaniAkhar/AnmolLipi family, Asees, Joy, AnandpurSahib, Satluj (and Sarover, which shares its layout), SONY.
- Detects the likely layout from the text (lexicon-based), and accepts a font-name hint.
- Leaves English and romanized lines in the same document untouched.
- Reads text copied out of a PDF on a Mac, where the clipboard has split font keys into other characters (`¨` into a space and a combining diaeresis, `¼` into `1⁄4`, `¹` into `1`).
- "Identify system" names the legacy font instead of ranking romanization systems.

## Evidence

- `legacy.py`, `_legacy_layouts.py`
- `tests/fixtures/legacy/`: hand-checked real documents

## Notes

Related: #4, #19.
