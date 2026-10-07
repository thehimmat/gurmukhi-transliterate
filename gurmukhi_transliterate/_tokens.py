"""
Shared Gurmukhi tokenizer for the romanizers.

Splits text into the parts a syllable is built from, so renderers can apply
each mark wherever it occurs instead of only directly after a consonant:

  cons    consonant, with its nukta merged in (ਜ਼ = ਜ + ਼)
  sign    dependent vowel sign (ਾ ਿ ੀ ੁ ੂ ੇ ੈ ੋ ੌ)
  vowel   independent vowel (ਅ ਆ ਇ … ਔ) or bare carrier (ੳ ੲ)
  addak   ੱ — geminates the *next* consonant
  nasal   ੰ (tippi) or ਂ (bindi) — nasalises the vowel just before it
  virama  ੍ — suppresses the inherent vowel
  other   anything else (spaces, punctuation, digits, ੴ, unknown marks)

Input is NFC-normalised first, which decomposes the precomposed nukta letters
(U+0A33/36/59–5B/5E) into base + ਼; token positions index that normalised text.
"""

from __future__ import annotations

import unicodedata
from dataclasses import dataclass

NUKTA = '਼'
ADDAK = 'ੱ'
VIRAMA = '੍'
TIPPI = 'ੰ'
BINDI = 'ਂ'

_SIGNS = frozenset('ਾਿੀੁੂੇੈੋੌ')
_VOWELS = frozenset('ਅਆਇਈਉਊਏਐਓਔੳੲ')


def _is_consonant(ch: str) -> bool:
    return 'ਕ' <= ch <= 'ਹ' or 'ਖ਼' <= ch <= 'ਫ਼'


@dataclass(frozen=True)
class Token:
    kind: str
    text: str
    pos: int


def normalize(text: str) -> str:
    return unicodedata.normalize('NFC', text)


def tokenize(text: str) -> list[Token]:
    """Tokenize *text* (normalised with :func:`normalize`)."""
    text = normalize(text)
    tokens: list[Token] = []
    i = 0
    while i < len(text):
        ch = text[i]
        if _is_consonant(ch):
            end = i + 2 if text.startswith(NUKTA, i + 1) else i + 1
            tokens.append(Token('cons', text[i:end], i))
            i = end
            continue
        if ch in _SIGNS:
            kind = 'sign'
        elif ch in _VOWELS:
            kind = 'vowel'
        elif ch == ADDAK:
            kind = 'addak'
        elif ch in (TIPPI, BINDI):
            kind = 'nasal'
        elif ch == VIRAMA:
            kind = 'virama'
        else:
            kind = 'other'
        tokens.append(Token(kind, ch, i))
        i += 1
    return tokens
