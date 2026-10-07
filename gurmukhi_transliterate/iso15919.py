"""
ISO 15919 transliteration system for Gurmukhi script.

Strictly follows the ISO 15919 standard for scholarly transliteration.
For more practical/accessible transliteration, see practical.py.

Use cases:
- Academic/scholarly work requiring strict ISO 15919 compliance
- Search functionality requiring exact phonetic matching
"""

from typing import Dict

from .schwa import compute_deletions
from ._tokens import TIPPI, normalize, tokenize


class GurmukhiISO15919:
    """Gurmukhi to ISO 15919 transliteration."""

    SPECIAL_SYMBOLS: Dict[str, str] = {
        'ੴ': 'ika oaṁkāra'
    }

    NUMBERS: Dict[str, str] = {
        '੦': '0', '੧': '1', '੨': '2', '੩': '3', '੪': '4',
        '੫': '5', '੬': '6', '੭': '7', '੮': '8', '੯': '9'
    }

    VOWELS: Dict[str, str] = {
        'ਅ': 'a', 'ਆ': 'ā', 'ਇ': 'i', 'ਈ': 'ī',
        'ਉ': 'u', 'ਊ': 'ū', 'ਏ': 'ē', 'ਐ': 'ai',
        'ਓ': 'ō', 'ਔ': 'au'
    }

    VOWEL_DIACRITICS: Dict[str, str] = {
        'ਾ': 'ā', 'ਿ': 'i', 'ੀ': 'ī',
        'ੁ': 'u', 'ੂ': 'ū', 'ੇ': 'ē',
        'ੈ': 'ai', 'ੋ': 'ō', 'ੌ': 'au'
    }

    CONSONANTS: Dict[str, str] = {
        'ਸ': 's', 'ਹ': 'h',
        'ਕ': 'k', 'ਖ': 'kh', 'ਗ': 'g', 'ਘ': 'gh', 'ਙ': 'ṅ',
        'ਚ': 'c', 'ਛ': 'ch', 'ਜ': 'j', 'ਝ': 'jh', 'ਞ': 'ñ',
        'ਟ': 'ṭ', 'ਠ': 'ṭh', 'ਡ': 'ḍ', 'ਢ': 'ḍh', 'ਣ': 'ṇ',
        'ਤ': 't', 'ਥ': 'th', 'ਦ': 'd', 'ਧ': 'dh', 'ਨ': 'n',
        'ਪ': 'p', 'ਫ': 'ph', 'ਬ': 'b', 'ਭ': 'bh', 'ਮ': 'm',
        'ਯ': 'y', 'ਰ': 'r', 'ਲ': 'l', 'ਵ': 'v', 'ੜ': 'ṛ',
        # Persian-influenced letters
        'ਖ਼': 'k̲h', 'ਗ਼': 'ġ', 'ਜ਼': 'z', 'ਫ਼': 'f',
        'ਸ਼': 'ś', 'ਲ਼': 'ḷ', 'ਕ਼': 'q',
    }

    PUNCTUATION: Dict[str, str] = {
        '॥': '||', '।': '|', ' ': ' ', '.': '.', ',': ',',
        '?': '?', '!': '!', '"': '"', "'": "'", '\n': '\n',
    }

    MODIFIERS: Dict[str, str] = {
        '੍': '', 'ੰ': 'ṃ', 'ਂ': 'ṁ', 'ੱ': '', '਼': '',
    }

    @staticmethod
    def to_phonetic(text: str, delete_schwa: bool = False) -> str:
        """Convert Gurmukhi text to ISO 15919 phonetic representation.

        Args:
            text:         Gurmukhi Unicode string.
            delete_schwa: Apply schwa deletion rules (R1 word-final, R2
                          pre-vocalic, R3 cascade). Produces more natural
                          romanization. Default False (full scholarly form).

        Nasalization marks (ISO 15919):
        - ੰ (tippi / anusvara)    → ṃ (dot below)
        - ਂ (bindi / chandrabindu) → ṁ (dot above)
        """
        C = GurmukhiISO15919.CONSONANTS
        text = normalize(text)
        deletions: set[int] = (
            compute_deletions(
                text,
                set(C.keys()),
                set(GurmukhiISO15919.VOWEL_DIACRITICS.keys()),
            )
            if delete_schwa
            else set()
        )

        tokens = tokenize(text)
        result = ''
        geminate = False
        j = 0
        while j < len(tokens):
            tok = tokens[j]
            nxt = tokens[j + 1] if j + 1 < len(tokens) else None

            if tok.kind == 'cons':
                rom = C.get(tok.text) or C.get(tok.text[0])
                if rom is None:
                    geminate = False
                    j += 1
                    continue
                if geminate:
                    # Aspirates geminate as unaspirated + aspirate: ṭṭh, kkh
                    result += rom[0] if len(rom) > 1 and rom[1] == 'h' else rom
                    geminate = False
                result += rom
                if nxt is not None and nxt.kind == 'sign':
                    result += GurmukhiISO15919.VOWEL_DIACRITICS[nxt.text]
                    j += 2
                    continue
                if nxt is not None and nxt.kind == 'virama':
                    j += 2
                    continue
                if nxt is not None and nxt.kind in ('nasal', 'addak'):
                    result += 'a'
                elif tok.pos not in deletions:
                    result += 'a'
                j += 1
                continue

            geminate = False
            if tok.kind == 'addak':
                geminate = nxt is not None and nxt.kind == 'cons'
            elif tok.kind == 'nasal':
                # tippi → anusvara ṃ (dot below); bindi → chandrabindu ṁ (dot above)
                result += 'ṃ' if tok.text == TIPPI else 'ṁ'
            elif tok.kind == 'sign':
                result += GurmukhiISO15919.VOWEL_DIACRITICS[tok.text]
            elif tok.kind == 'vowel' and tok.text in GurmukhiISO15919.VOWELS:
                vowel = GurmukhiISO15919.VOWELS[tok.text]
                # Hiatus after an inherent a is marked with an apostrophe: ka'i
                result += "'" + vowel if result.endswith('a') else vowel
            elif tok.kind == 'other':
                ch = tok.text
                if ch in GurmukhiISO15919.SPECIAL_SYMBOLS:
                    result += GurmukhiISO15919.SPECIAL_SYMBOLS[ch]
                elif ch in GurmukhiISO15919.PUNCTUATION:
                    result += GurmukhiISO15919.PUNCTUATION[ch]
                elif ch in GurmukhiISO15919.NUMBERS:
                    result += GurmukhiISO15919.NUMBERS[ch]
            j += 1

        return result
