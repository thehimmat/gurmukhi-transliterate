---
id: US-007
title: Scholarly Shackle transliteration
status: delivered
created: 2026-10-08
updated: 2026-10-08
linked_issues: [7, 9, 11]
linked_tests: [tests/test_systems.py]
supersedes: null
superseded_by: null
---

## Story

As a scholar citing Gurbani, I want Gurmukhi rendered in Christopher Shackle's phonemic transcription, so my romanization matches *A Guru Nanak Glossary* and stays reversible.

## Acceptance criteria

- Renders Gurmukhi in Shackle's system as stated in *A Guru Nanak Glossary* (2nd ed. 2011), Transcription pp. xxi–xxv.
- Writes tippi before a stop as that stop's class nasal (ṅ ñ ṇ n m), and as ṁ elsewhere.
- Output reverses to the same Gurmukhi for class-nasal words.

## Evidence

- `systems.py::SHACKLE` (scheme and `notes` on the rules the generic engine approximates)

## Notes

Formalized from #11. Related: #7, #9.
