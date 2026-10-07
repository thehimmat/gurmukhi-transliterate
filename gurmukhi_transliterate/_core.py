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
    directly; other unmapped characters are skipped

A letter the system leaves undefined (None or missing) is never dropped: a
nukta letter falls back to its base letter, anything else to its ISO 15919
value, and a missing bindi to the system's tippi value. Each fallback is
recorded as a ConversionWarning (see GurmukhiRomanizer.romanize_report).
After a virama, the system's ``subjoined`` form is used when it defines one.
"""

from __future__ import annotations
from .systems import SystemMap
from .schwa import compute_deletions
from ._tokens import TIPPI, VIRAMA, normalize, tokenize
from .iso15919 import GurmukhiISO15919
from .legacy import ConversionWarning

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


def transliterate(
    text: str,
    system: SystemMap,
    delete_schwa: bool = False,
    warnings: list[ConversionWarning] | None = None,
) -> str:
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

    def warn(pos: int, char: str, kind: str, message: str) -> None:
        if warnings is not None:
            warnings.append(ConversionWarning(pos, char, kind, message))

    def consonant(tok) -> str | None:
        if cons.get(tok.text) is not None:
            return cons[tok.text]
        if len(tok.text) == 2 and cons.get(tok.text[0]) is not None:
            warn(tok.pos, tok.text, 'fallback_base',
                 f'{system.id} has no {tok.text}; used its base letter')
            return cons[tok.text[0]]
        iso = GurmukhiISO15919.CONSONANTS.get(tok.text)
        if iso is not None:
            warn(tok.pos, tok.text, 'fallback_iso',
                 f'{system.id} has no {tok.text}; used ISO 15919 {iso!r}')
        return iso

    def subjoined(tok, prev) -> str | None:
        if prev is not None and prev.kind == 'virama':
            return system.subjoined.get(VIRAMA + tok.text)
        return None

    tokens = tokenize(text)
    result: list[str] = []
    geminate = False
    j = 0
    while j < len(tokens):
        tok = tokens[j]
        nxt = tokens[j + 1] if j + 1 < len(tokens) else None

        if tok.kind == 'cons':
            rom = subjoined(tok, tokens[j - 1] if j else None) or consonant(tok)
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
            if nasal is None and system.nasal_tippi is not None:
                nasal = system.nasal_tippi
                warn(tok.pos, tok.text, 'fallback_nasal',
                     f'{system.id} has no bindi; used its tippi value')
            if nasal:
                result.append(nasal)
        elif tok.kind == 'sign':
            if vd.get(tok.text) is not None:
                result.append(vd[tok.text])  # type: ignore[arg-type]
        elif tok.kind == 'vowel':
            if vw.get(tok.text) is not None:
                result.append(vw[tok.text])  # type: ignore[arg-type]
            elif tok.text in GurmukhiISO15919.VOWELS:
                iso = GurmukhiISO15919.VOWELS[tok.text]
                warn(tok.pos, tok.text, 'fallback_iso',
                     f'{system.id} has no {tok.text}; used ISO 15919 {iso!r}')
                result.append(iso)
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
