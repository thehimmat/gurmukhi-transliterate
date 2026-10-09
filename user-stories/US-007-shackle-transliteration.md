---
id: US-007
title: Scholarly Shackle transliteration
status: delivered
created: 2026-10-08
updated: 2026-10-09
linked_issues: [7, 9, 10, 11]
linked_tests: [tests/test_systems.py]
supersedes: null
superseded_by: null
---

## Story

As a scholar citing Gurbani, I want Gurmukhi rendered in Christopher Shackle's phonemic transcription, so my romanization matches *A Guru Nanak Glossary* and stays reversible.

## Acceptance criteria

- Renders Gurmukhi in Shackle's system as stated in *A Guru Nanak Glossary* (2nd ed. 2011), Transcription pp. xxi–xxv.
- Writes tippi before a stop or s as the class nasal (ṅ ñ ṇ n m), and as ṁ elsewhere, after the whole vowel group (ਭਉਂ bhaüṁ).
- Marks ਉ/ਇ after a as vowels of their own (ਸਉ saü, ਅਇ aï) and double pointing ੋ + ੁ as ü (ਸੋੁ sü).
- Leaves out what the spelling can't show: doubling (ਮਤਿ mati/matti) and an omitted ੍ਹ.
- Output reverses to the same Gurmukhi for these words.

## Evidence

- `systems.py::SHACKLE` (scheme and `notes` on the rules the generic engine approximates)

## Notes

Formalized from #11. Related: #7, #9, #10.
