---
id: US-004
title: Compare multiple transliteration systems side by side
status: delivered
created: 2026-07-22
updated: 2026-10-08
linked_issues: [4, 1]
linked_tests: [tests/test_character_coverage.py, tests/test_compare.py, tests/test_conformance.py, tests/test_systems.py]
supersedes: null
superseded_by: null
---

## Story

As a user evaluating schemes, I want one input rendered across many systems at once (ISO 15919, Practical, IPA, BaniDB/STTM, iGurbani, Gursevak), so I can compare them directly.

## Acceptance criteria

- Renders a single input across multiple systems simultaneously: ISO 15919, Practical, IPA, BaniDB/STTM, iGurbani, Gursevak.

## Evidence

- `compare.py`, `systems.py`

## Notes

Related: #4, #1.
