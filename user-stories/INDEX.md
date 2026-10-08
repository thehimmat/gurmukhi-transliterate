# User stories

User-story records for gurmukhi-transliterate. Each story's acceptance tests are tagged
`@pytest.mark.story('US-NNN')`; run one story with `pytest --story US-NNN`.
`tests/test_user_stories.py` keeps the tags, each record's `linked_tests` and this index in step.

| ID | Title | Status | Linked issues | Tests |
|------|------|------|------|------|
| US-001 | Academic-standard (ISO 15919) transliteration | delivered | — | `pytest --story US-001` |
| US-002 | Readable practical romanization | delivered | — | `pytest --story US-002` |
| US-003 | Legacy font/encoding conversion to Unicode | delivered | #4, #19 | `pytest --story US-003` |
| US-004 | Compare multiple transliteration systems side by side | delivered | #4, #1 | `pytest --story US-004` |
| US-005 | Identify the transliteration/encoding of unknown input | delivered | #16, #27 | `pytest --story US-005` |
| US-006 | Browser demo backed by a deployable API | delivered | #2, #3, #5 | `pytest --story US-006` |
| US-007 | Scholarly Shackle transliteration | delivered | #7, #9, #10, #11 | `pytest --story US-007` |
| US-008 | Reverse Shackle transcription to Gurmukhi with ambiguity flags | delivered | #7, #8, #9, #10, #11, #13 | `pytest --story US-008` |
| US-009 | Match romanized or noisy Gurbani to the canonical line | delivered | #16 | `pytest --story US-009` |
| US-010 | Reverse romanized words for a known or detected system | delivered | #16, #26 | `pytest --story US-010` |
