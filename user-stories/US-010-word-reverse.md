---
id: US-010
title: Reverse romanized words for a known or detected system
status: delivered
created: 2026-10-08
updated: 2026-10-08
linked_issues: [16, 26]
linked_tests: [tests/test_informal.py, tests/test_system_reverse.py]
supersedes: null
superseded_by: null
---

## Story

As a user with romanized words that aren't a Gurbani line (names, glossary terms, informal spellings), I want them turned into Gurmukhi using the system they were written in, so I get attested spellings without a verse to match against.

## Acceptance criteria

- Reverses word by word for any supported system, ranking candidate spellings by corpus frequency.
- Picks the system automatically when it isn't given, including informal spellings (Waheguru, Sat Sri Akal).
- Never guesses: unknown words are reported as missing and `to_gurmukhi` raises `UnableToReverse` naming them.
- `to_gurmukhi` falls back to this when the input isn't a verse.

## Evidence

- `system_reverse.py` (`reverse_words`), `informal.py`

## Notes

Related: #16, #26 (spellings the system maps don't produce yet).
