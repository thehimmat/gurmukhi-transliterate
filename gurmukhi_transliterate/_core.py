"""
Generic Gurmukhi → Roman transliteration engine.

Used by GurmukhiRomanizer for the "Other" systems (dr_sant_singh, dr_thind,
sttm, gfs, sacred_nitnem, iast, ipa, …).

The existing GurmukhiISO15919 and GurmukhiPractical classes are not refactored
to use this engine — they keep their own tested implementations.

Text is split into syllable parts by :mod:`._tokens`, then rendered:
  - consonant → its romanization, plus the vowel that follows it:
      a vowel sign, nothing before a virama, or the inherent vowel (kept
      before tippi/bindi/addak, otherwise subject to schwa deletion)
  - addak     → doubles the romanization of the next consonant, wherever it
                occurs (after a consonant, vowel sign or independent vowel)
  - tippi/bindi → the system's nasal value, after whatever vowel precedes it
  - independent vowels, standalone signs, ੴ, punctuation and numbers map
    directly; unmapped characters are skipped
"""

from __future__ import annotations
from .systems import SystemMap
from .schwa import compute_deletions
from ._tokens import TIPPI, normalize, tokenize

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
    inherent = vw.get('ਅ', 'a') or 'a'

    text = normalize(text)
    deletions: set[int] = (
        compute_deletions(text, set(cons.keys()), set(vd.keys()))
        if delete_schwa
        else set()
    )

    def consonant(tok_text: str) -> str | None:
        if tok_text in cons:
            return cons[tok_text]
        return cons.get(tok_text[0])  # nukta letter missing from the map

    tokens = tokenize(text)
    result: list[str] = []
    geminate = False
    j = 0
    while j < len(tokens):
        tok = tokens[j]
        nxt = tokens[j + 1] if j + 1 < len(tokens) else None

        if tok.kind == 'cons':
            rom = consonant(tok.text)
            if rom is None:
                geminate = False
                j += 1
                continue
            if geminate:
                result.append(rom)
                geminate = False
            result.append(rom)
            if nxt is not None and nxt.kind == 'sign':
                sign = vd.get(nxt.text)
                result.append(sign if sign is not None else inherent)
                j += 2
                continue
            if nxt is not None and nxt.kind == 'virama':
                j += 2
                continue
            if nxt is not None and nxt.kind in ('nasal', 'addak'):
                result.append(inherent)
            elif tok.pos not in deletions:
                result.append(inherent)
            j += 1
            continue

        geminate = False
        if tok.kind == 'addak':
            geminate = nxt is not None and nxt.kind == 'cons'
        elif tok.kind == 'nasal':
            nasal = system.nasal_tippi if tok.text == TIPPI else system.nasal_bindi
            if nasal:
                result.append(nasal)
        elif tok.kind == 'sign':
            if vd.get(tok.text) is not None:
                result.append(vd[tok.text])  # type: ignore[arg-type]
        elif tok.kind == 'vowel':
            if vw.get(tok.text) is not None:
                result.append(vw[tok.text])  # type: ignore[arg-type]
        elif tok.kind == 'other':
            ch = tok.text
            if ch in _SPECIAL:
                result.append(_SPECIAL[ch])
            elif ch in _PUNCTUATION:
                result.append(_PUNCTUATION[ch])
            elif ch in _NUMBERS:
                result.append(_NUMBERS[ch])
        # virama on its own: nothing to emit
        j += 1

    return ''.join(result)
