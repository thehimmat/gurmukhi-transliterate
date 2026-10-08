---
id: US-009
title: Match romanized or noisy Gurbani to the canonical line
status: delivered
created: 2026-10-08
updated: 2026-10-08
linked_issues: [16]
linked_tests: [tests/test_lexicon.py, tests/test_verse.py]
supersedes: null
superseded_by: null
---

## Story

As someone holding a line of Gurbani in romanization, GurbaniAkhar ASCII or OCR-damaged Unicode, I want the canonical Gurmukhi line and where it occurs, so I can recover the exact text without knowing which scheme was used.

## Acceptance criteria

- Finds the canonical line in the bundled corpus (Guru Granth Sahib, Dasam Granth, Bhai Gurdas, Bhai Nand Lal) from any common romanization, GurbaniAkhar or noisy Unicode.
- Returns every location of a repeated line, with source and page.
- Returns nothing, rather than a guess, when no line matches confidently; `to_gurmukhi` refuses English.

## Evidence

- `verse.py` (`match_verse`, `to_gurmukhi`), `lexicon.py`, `data/`
- `docs/eval/baseline.md`: ~99.5% top-1, 100% top-3 on real romanized lines

## Notes

Related: #16.
