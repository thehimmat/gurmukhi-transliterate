---
id: US-005
title: Identify the transliteration/encoding of unknown input
status: delivered
created: 2026-07-22
updated: 2026-10-07
linked_issues: [16, 27]
linked_tests: [tests/test_compare.py, tests/test_language.py]
supersedes: null
superseded_by: null
---

## Story

As a user with mystery text, I want detection of the likely system/encoding, so I can process it correctly.

## Acceptance criteria

- Detects the likely transliteration system/encoding of unknown input.
- Tells English from romanized Gurmukhi, and abstains when there's too little evidence (names only).
- Ranks systems by likelihood, with confidences that are low for English text, and flags systems the input can't tell apart.
- Recognises common informal spellings (Waheguru, Sat Sri Akal) as their own class.

## Evidence

- `api/identify.py` (`include_english=1` ranks English too)
- `identify_system` and `detect_latin`: character-trigram models (`gurmukhi_transliterate/language.py`, `data/ngrams.tsv.gz`), replacing token-coverage scoring (#27)
- `docs/eval/baseline.md`: detector and identification accuracy by line length
