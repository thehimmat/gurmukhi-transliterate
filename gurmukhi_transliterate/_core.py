"""
Generic Gurmukhi → Roman transliteration engine.

Used by GurmukhiRomanizer for the "Other" systems (dr_sant_singh, dr_thind,
sttm, gfs, sacred_nitnem, iast, ipa).

The existing GurmukhiISO15919 and GurmukhiPractical classes are not refactored
to use this engine — they keep their own tested implementations.

Processing order per character position:
  1. Special symbols (ੴ)
  2. Punctuation / numbers
  3. Nasalization lookahead (tippi / bindi as next char)
  4. Addak lookahead (gemination)
  5. Two-char consonants (base + nukta ਼)
  6. Single consonant:
       a. followed by vowel diacritic → consonant + diacritic
       b. followed by virama (੍)     → consonant only (no inherent vowel)
       c. otherwise                   → consonant + inherent_vowel
  7. Standalone vowel diacritics (e.g. word-medial when preceding consonant
     was already consumed)
  8. Independent vowel letters (ਅ ਆ …)
  9. Unmapped characters → skipped
"""

from __future__ import annotations
from .systems import SystemMap
from .schwa import compute_deletions

_VIRAMA = '੍'
_ADDAK = 'ੱ'
_NUKTA = '਼'
_TIPPI = 'ੰ'
_BINDI = 'ਂ'

_PUNCTUATION: dict[str, str] = {
    '॥': '||', '।': '|', ' ': ' ', '.': '.', ',': ',',
    '?': '?', '!': '!', '"': '"', "'": "'", '\n': '\n', '\t': '\t',
}

_NUMBERS: dict[str, str] = {
    '੦': '0', '੧': '1', '੨': '2', '੩': '3', '੪': '4',
    '੫': '5', '੬': '6', '੭': '7', '੮': '8', '੯': '9',
}

_SPECIAL: dict[str, str] = {
    'ੴ': 'ik oankaar',  # universal approximation
}


def transliterate(text: str, system: SystemMap, delete_schwa: bool = False) -> str:
    """Transliterate *text* using the given system map.

    Limitations vs. the dedicated ISO/Practical implementations:
    - Nasalization uses simple nasal_tippi / nasal_bindi values (no
      labial-context m/n switching).
    - Addak doubles the full romanized consonant string (e.g. 'kh'+'kh').
      Aspirate-aware splitting (k+kh) is not applied.
    - IPA combining characters may not render perfectly in all contexts.
    """
    cons = system.consonants
    vd = system.vowel_diacritics
    vw = system.vowels
    nasal_t = system.nasal_tippi
    nasal_b = system.nasal_bindi
    sub = system.subjoined
    inherent = vw.get('ਅ', 'a') or 'a'

    # Build combined consonant set for schwa deletion
    all_cons: set[str] = set(cons.keys())
    all_vd: set[str] = set(vd.keys())

    deletions: set[int] = (
        compute_deletions(text, all_cons, all_vd)
        if delete_schwa
        else set()
    )

    result: list[str] = []
    i = 0
    n = len(text)

    def _char(idx: int) -> str | None:
        return text[idx] if idx < n else None

    while i < n:
        ch = text[i]

        # 1. Special symbols
        if ch in _SPECIAL:
            result.append(_SPECIAL[ch])
            i += 1
            continue

        # 2. Punctuation / numbers
        if ch in _PUNCTUATION:
            result.append(_PUNCTUATION[ch])
            i += 1
            continue
        if ch in _NUMBERS:
            result.append(_NUMBERS[ch])
            i += 1
            continue

        # --- resolve subjoined conjuncts (virama + consonant) as a unit ---
        # These are already handled naturally: virama suppresses inherent vowel
        # and the following consonant is processed on the next iteration.
        # The subjoined dict is used for lookup when we see virama explicitly,
        # but since the engine handles virama inline, we mainly use it for
        # the server's comparison table.  Nothing extra needed here.

        # 3 + 4. Two-char consonant (base + nukta)
        two = text[i:i+2] if i + 1 < n else ''
        if two and two[1] == _NUKTA and two in cons:
            rom = cons[two]
            if rom is None:
                i += 2
                continue
            nxt = _char(i + 2)
            if nxt in (_TIPPI, _BINDI):
                nasal = nasal_t if nxt == _TIPPI else nasal_b
                result.append(rom)
                result.append(inherent)
                if nasal:
                    result.append(nasal)
                i += 3
            elif nxt in vd and vd[nxt] is not None:
                result.append(rom)
                result.append(vd[nxt])  # type: ignore[arg-type]
                i += 3
            elif nxt == _VIRAMA:
                result.append(rom)
                i += 3  # consume base + nukta + virama
            elif nxt == _ADDAK and _char(i + 3) in cons:
                doubled = cons[_char(i + 3)]  # type: ignore[index]
                if doubled:
                    result.append(rom)
                    result.append(inherent)
                    result.append(doubled + doubled)
                    dbl_nxt = _char(i + 4)
                    if dbl_nxt not in vd and dbl_nxt != _VIRAMA:
                        if not delete_schwa or (i + 3) not in deletions:
                            result.append(inherent)
                    i += 5
                else:
                    i += 2
            else:
                result.append(rom)
                if nxt not in vd and nxt != _VIRAMA:
                    if not delete_schwa or i not in deletions:
                        result.append(inherent)
                i += 2
            continue

        # 5. Single consonant
        if ch in cons:
            rom = cons[ch]
            if rom is None:
                i += 1
                continue
            nxt = _char(i + 1)

            # Nasalization as next char
            if nxt in (_TIPPI, _BINDI):
                nasal = nasal_t if nxt == _TIPPI else nasal_b
                result.append(rom)
                result.append(inherent)
                if nasal:
                    result.append(nasal)
                i += 2
                continue

            # Addak (gemination)
            if nxt == _ADDAK:
                dbl_ch = _char(i + 2)
                if dbl_ch and dbl_ch in cons and cons[dbl_ch] is not None:
                    doubled = cons[dbl_ch]
                    result.append(rom)
                    result.append(inherent)
                    result.append(doubled + doubled)  # type: ignore[operator]
                    dbl_nxt = _char(i + 3)
                    if dbl_nxt in vd and vd[dbl_nxt] is not None:
                        result.append(vd[dbl_nxt])  # type: ignore[arg-type]
                        i += 4  # consonant + addak + doubled + diacritic
                    elif dbl_nxt != _VIRAMA:
                        if not delete_schwa or (i + 2) not in deletions:
                            result.append(inherent)
                        i += 3  # consonant + addak + doubled
                    else:
                        i += 3  # virama: no inherent vowel
                    continue

            # Vowel diacritic follows
            if nxt in vd and vd[nxt] is not None:
                result.append(rom)
                result.append(vd[nxt])  # type: ignore[arg-type]
                # Check for tippi/bindi after diacritic
                after_vd = _char(i + 2)
                if after_vd in (_TIPPI, _BINDI):
                    nasal = nasal_t if after_vd == _TIPPI else nasal_b
                    if nasal:
                        result.append(nasal)
                    i += 3
                else:
                    i += 2
                continue

            # Virama (suppress inherent vowel)
            if nxt == _VIRAMA:
                result.append(rom)
                i += 2
                continue

            # Inherent vowel
            result.append(rom)
            if not delete_schwa or i not in deletions:
                result.append(inherent)
            i += 1
            continue

        # 6. Standalone vowel diacritic
        if ch in vd and vd[ch] is not None:
            result.append(vd[ch])  # type: ignore[arg-type]
            i += 1
            continue

        # 7. Independent vowel
        if ch in vw and vw[ch] is not None:
            result.append(vw[ch])  # type: ignore[arg-type]
            i += 1
            continue

        # 8. Virama (standalone, e.g. between two consonants in a conjunct)
        if ch == _VIRAMA:
            i += 1
            continue

        # 9. Skip unmapped
        i += 1

    return ''.join(result)
