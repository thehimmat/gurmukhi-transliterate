"""
Schwa deletion algorithm for Gurmukhi transliteration.

Rules applied right-to-left within each whitespace-delimited word:

  R1  Word-final consonant with inherent schwa → delete
  R2  Consonant with inherent schwa immediately before a consonant that
      carries an explicit vowel diacritic → delete
        (not applied to the first consonant in the word)

Unlike Hindi, Punjabi does NOT use a cascade rule (Hindi's R3). Cascading
produces unpronounceable clusters in many Punjabi words — e.g. ਹਿੰਮਤ would
become "hiṁmt" instead of the correct "hiṁmat". Punjabi's schwa deletion is
primarily positional (word-final) and morphophonological (pre-suffix), not a
phonotactic cascade.

Reference: Goyal et al. "A Rule Based Schwa Deletion Algorithm for Punjabi
TTS System", Springer CCIS 139, 2011; Wikipedia "Schwa deletion in
Indo-Aryan languages".
"""

from __future__ import annotations

_WORD_BOUNDARIES: frozenset[str] = frozenset(' \t\n।॥')
_VIRAMA = '੍'
_NUKTA = '਼'


def compute_deletions(
    text: str,
    consonants: set[str],
    vowel_diacritics: set[str],
) -> set[int]:
    """Return the set of character positions in *text* where the inherent
    schwa ('a') should be omitted during transliteration.

    Args:
        text:            Raw Gurmukhi Unicode string.
        consonants:      Set of Gurmukhi characters that are consonants
                         (i.e. the keys of the transliterator's CONSONANTS dict,
                         including two-char nukta combinations like 'ਜ਼').
        vowel_diacritics: Set of characters that supply an explicit vowel
                         (keys of VOWEL_DIACRITICS dict).
    """
    deletions: set[int] = set()
    n = len(text)
    i = 0

    while i < n:
        if text[i] in _WORD_BOUNDARIES:
            i += 1
            continue

        # Find end of word
        j = i
        while j < n and text[j] not in _WORD_BOUNDARIES:
            j += 1

        syllables = _collect_syllables(text, i, j, consonants, vowel_diacritics)
        if syllables:
            _apply_rules(syllables, deletions)

        i = j

    return deletions


def _collect_syllables(
    text: str,
    start: int,
    end: int,
    consonants: set[str],
    vowel_diacritics: set[str],
) -> list[tuple[int, bool]]:
    """Return (position, has_explicit_vowel) for each consonant in text[start:end].

    position            = index of the consonant's first character in text.
    has_explicit_vowel  = True if the consonant is followed by a vowel
                          diacritic or a virama (which suppresses the schwa).
    """
    syllables: list[tuple[int, bool]] = []
    k = start

    while k < end:
        char = text[k]

        # Two-char consonant: base + nukta (e.g. ਜ਼ = ਜ + ਼, ਖ਼ = ਖ + ਼)
        if (
            k + 1 < end
            and text[k + 1] == _NUKTA
            and char in consonants  # base consonant is valid alone
        ):
            two = char + _NUKTA
            # Only treat as two-char unit if it's in the consonants set
            if two in consonants:
                after = k + 2
                has_explicit = after < end and (
                    text[after] in vowel_diacritics or text[after] == _VIRAMA
                )
                syllables.append((k, has_explicit))
                k = after + (1 if has_explicit else 0)
                continue

        if char in consonants:
            after = k + 1
            has_explicit = after < end and (
                text[after] in vowel_diacritics or text[after] == _VIRAMA
            )
            syllables.append((k, has_explicit))
            k = after + (1 if has_explicit else 0)
            continue

        k += 1

    return syllables


def _apply_rules(
    syllables: list[tuple[int, bool]],
    deletions: set[int],
) -> None:
    """Mutate *deletions* in place using R1 and R2 (no cascade for Punjabi)."""
    m = len(syllables)
    to_del = [False] * m

    for k in range(m - 1, -1, -1):
        _pos, has_explicit = syllables[k]
        if has_explicit:
            continue  # never delete an explicitly-marked vowel

        is_first = k == 0

        if k == m - 1:
            # R1: word-final consonant — always deleted
            to_del[k] = True
        elif syllables[k + 1][1]:
            # R2: next consonant has explicit vowel (skip for first consonant)
            # e.g. ਕਰਤਾ → ਰ deleted (before ਤਾ), ਕ kept (first)
            if not is_first:
                to_del[k] = True
        # Punjabi does NOT cascade (unlike Hindi's R3). Cascading over
        # schwa-schwa sequences creates unpronounceable clusters:
        # ਹਿੰਮਤ would become "hiṁmt" instead of the correct "hiṁmat".

    for k in range(m):
        if to_del[k]:
            deletions.add(syllables[k][0])
