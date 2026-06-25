"""
Cross-system comparison and system identification for Gurmukhi romanization.

comparison_table(text) → {system_id: romanized_text}
identify_system(romanized) → [(system_id, confidence), ...]
"""

from __future__ import annotations
import re
from .systems import SYSTEMS, SYSTEM_ORDER, SystemMap
from .romanizer import GurmukhiRomanizer
from .iso15919 import GurmukhiISO15919
from .practical import GurmukhiPractical


# ---------------------------------------------------------------------------
# Comparison
# ---------------------------------------------------------------------------

def comparison_table(
    text: str,
    systems: list[str] | None = None,
    delete_schwa: bool = False,
) -> dict[str, str]:
    """Romanize *text* with every known system.

    Args:
        text:         Gurmukhi Unicode input.
        systems:      Optional list of system IDs to include. Defaults to all.
        delete_schwa: Pass through to each romanizer.

    Returns:
        Ordered dict {system_id: romanized_string} including 'iso15919' and
        'practical' as the first two entries.
    """
    order = ['iso15919', 'practical'] + SYSTEM_ORDER
    if systems is not None:
        order = [s for s in order if s in systems]

    result: dict[str, str] = {}
    for sid in order:
        if sid == 'iso15919':
            result[sid] = GurmukhiISO15919.to_phonetic(
                text, delete_schwa=delete_schwa
            )
        elif sid == 'practical':
            result[sid] = GurmukhiPractical.to_practical(
                text, delete_schwa=delete_schwa
            )
        elif sid in SYSTEMS:
            result[sid] = GurmukhiRomanizer(sid).romanize(
                text, delete_schwa=delete_schwa
            )
    return result


# ---------------------------------------------------------------------------
# System identification
# ---------------------------------------------------------------------------

# Build a reverse index at module load time:
#   token → set of system IDs that produce this token for some Gurmukhi char.
# A token is a multi-character romanization string (e.g. 'kh', 'aa', 'ṃ').

def _build_token_index() -> dict[str, set[str]]:
    """token → set[system_id] across all known systems."""
    index: dict[str, set[str]] = {}

    def _add(token: str | None, sid: str) -> None:
        if not token:
            return
        token = token.lower()
        if token not in index:
            index[token] = set()
        index[token].add(sid)

    # ISO 15919 signatures
    iso_sig = {
        'ś': 'iso15919', 'ṭ': 'iso15919', 'ḍ': 'iso15919',
        'ṛ': 'iso15919', 'ṅ': 'iso15919', 'ṇ': 'iso15919',
        'ñ': 'iso15919', 'ā': 'iso15919', 'ī': 'iso15919',
        'ū': 'iso15919', 'ē': 'iso15919', 'ō': 'iso15919',
        'ṃ': 'iso15919', 'ṁ': 'iso15919',
    }
    for tok, sid in iso_sig.items():
        _add(tok, sid)

    # Practical signatures
    _add('aa', 'practical')
    _add('ee', 'practical')
    _add('oo', 'practical')

    # All other systems
    for sid, smap in SYSTEMS.items():
        for val in smap.consonants.values():
            _add(val, sid)
        for val in smap.vowel_diacritics.values():
            _add(val, sid)
        for val in smap.vowels.values():
            _add(val, sid)
        _add(smap.nasal_tippi, sid)
        _add(smap.nasal_bindi, sid)

    return index


_TOKEN_INDEX: dict[str, set[str]] = _build_token_index()

# Sorted longest-first for greedy matching
_SORTED_TOKENS: list[str] = sorted(_TOKEN_INDEX.keys(), key=len, reverse=True)

# All known system IDs (including iso/practical)
_ALL_SYSTEMS = ['iso15919', 'practical'] + SYSTEM_ORDER


def _tokenise(text: str) -> list[str]:
    """Greedy longest-match tokeniser against all known roman tokens."""
    text = text.lower()
    tokens: list[str] = []
    i = 0
    n = len(text)
    while i < n:
        matched = False
        for tok in _SORTED_TOKENS:
            if text[i:i+len(tok)] == tok:
                tokens.append(tok)
                i += len(tok)
                matched = True
                break
        if not matched:
            tokens.append(text[i])  # unknown single char
            i += 1
    return tokens


def identify_system(
    romanized: str,
    top_n: int = 5,
) -> list[dict]:
    """Score *romanized* text against all known systems.

    Algorithm:
      1. Tokenise input with greedy longest-match against the token index.
      2. For each system, score = (tokens that appear in its output set) / total_tokens.
      3. Return top_n results sorted by confidence descending.

    Returns:
        List of dicts: [{system, label, confidence}] sorted descending.
    """
    tokens = _tokenise(romanized)
    if not tokens:
        return []

    scores: dict[str, int] = {sid: 0 for sid in _ALL_SYSTEMS}
    for tok in tokens:
        if tok in _TOKEN_INDEX:
            for sid in _TOKEN_INDEX[tok]:
                if sid in scores:
                    scores[sid] += 1

    total = len(tokens)
    labels = {
        'iso15919': 'ISO 15919',
        'practical': 'Practical',
        **{s.id: s.label for s in SYSTEMS.values()},
    }

    ranked = sorted(
        (
            {
                'system': sid,
                'label': labels.get(sid, sid),
                'confidence': round(count / total, 3),
            }
            for sid, count in scores.items()
        ),
        key=lambda d: d['confidence'],
        reverse=True,
    )
    return ranked[:top_n]
