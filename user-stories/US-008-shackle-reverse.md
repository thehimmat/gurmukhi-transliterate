---
id: US-008
title: Reverse Shackle transcription to Gurmukhi with ambiguity flags
status: delivered
created: 2026-10-08
updated: 2026-10-08
linked_issues: [7, 8, 10, 11, 13]
linked_tests: [tests/test_matcher.py, tests/test_reverse.py, tests/test_systems.py]
supersedes: null
superseded_by: null
---

## Story

As a dictionary maintainer with words printed only in Shackle's transcription, I want them turned back into Gurmukhi with the uncertain spots flagged, so I can store them as lemmas and send only the doubtful ones to human review.

## Acceptance criteria

- Reverses Shackle transcription to a primary Gurmukhi spelling, following the worked examples on pp. xxi–xxv.
- Flags each genuinely ambiguous spot (nasalization, gemination, aspirate sonorants, Perso-Arabic dots) with its alternatives.
- Ranks candidate spellings against an injected word list, preferring the attested and most frequent; falls back to the primary when none match.

## Evidence

- `reverse.py` (`reverse_transliterate`, `shackle_to_gurmukhi`), `matcher.py` (`CorpusMatcher`)
- README "Reverse transliteration": 92% exact / 97% with flagged candidates on the glossary head-words; reproducible round trip in `docs/eval/baseline.md`

## Notes

Formalized from #11. Consumer: thehimmat/gurmukhi-kosh#10. Related: #7, #8, #10, #13.
