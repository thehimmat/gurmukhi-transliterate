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
        deletions: set[int] = (
            compute_deletions(
                text,
                set(GurmukhiISO15919.CONSONANTS.keys()),
                set(GurmukhiISO15919.VOWEL_DIACRITICS.keys()),
            )
            if delete_schwa
            else set()
        )
        result = ''
        i = 0
        while i < len(text):
            if text[i] in GurmukhiISO15919.SPECIAL_SYMBOLS:
                result += GurmukhiISO15919.SPECIAL_SYMBOLS[text[i]]
                i += 1
                continue

            if text[i] in GurmukhiISO15919.PUNCTUATION:
                result += GurmukhiISO15919.PUNCTUATION[text[i]]
                i += 1
                continue

            if text[i] in GurmukhiISO15919.NUMBERS:
                result += GurmukhiISO15919.NUMBERS[text[i]]
                i += 1
                continue

            char = text[i]
            next_char = text[i + 1] if i + 1 < len(text) else None
            next_next_char = text[i + 2] if i + 2 < len(text) else None

            # Handle gemination (addak)
            if next_char == 'ੱ':
                if i + 2 < len(text):
                    doubled_char = text[i + 2]
                    if doubled_char in GurmukhiISO15919.CONSONANTS:
                        if char in GurmukhiISO15919.CONSONANTS:
                            result += GurmukhiISO15919.CONSONANTS[char] + 'a'
                        elif char in GurmukhiISO15919.VOWEL_DIACRITICS:
                            result += GurmukhiISO15919.VOWEL_DIACRITICS[char]
                        else:
                            result += GurmukhiISO15919.VOWELS[char]

                        if doubled_char in GurmukhiISO15919.CONSONANTS and len(GurmukhiISO15919.CONSONANTS[doubled_char]) > 1 and GurmukhiISO15919.CONSONANTS[doubled_char][1] == 'h':
                            result += GurmukhiISO15919.CONSONANTS[doubled_char][0] + GurmukhiISO15919.CONSONANTS[doubled_char]
                        else:
                            result += GurmukhiISO15919.CONSONANTS[doubled_char] + GurmukhiISO15919.CONSONANTS[doubled_char]
                        doubled_pos = i + 2  # position of the doubled consonant
                        i += 3
                        if text[i] not in GurmukhiISO15919.VOWEL_DIACRITICS:
                            if not delete_schwa or doubled_pos not in deletions:
                                result += 'a'
                        continue

            # Handle nasalization
            if next_char == 'ੰ':  # tippi → anusvara ṃ (dot below)
                if char in GurmukhiISO15919.CONSONANTS:
                    result += GurmukhiISO15919.CONSONANTS[char] + 'a'
                elif char in GurmukhiISO15919.VOWEL_DIACRITICS:
                    result += GurmukhiISO15919.VOWEL_DIACRITICS[char]
                else:
                    result += GurmukhiISO15919.VOWELS[char]
                result += "ṃ"
                i += 2
                continue
            elif next_char == 'ਂ':  # bindi → chandrabindu ṁ (dot above)
                if char in GurmukhiISO15919.CONSONANTS:
                    result += GurmukhiISO15919.CONSONANTS[char]
                elif char in GurmukhiISO15919.VOWEL_DIACRITICS:
                    result += GurmukhiISO15919.VOWEL_DIACRITICS[char]
                else:
                    result += GurmukhiISO15919.VOWELS[char]
                result += "ṁ"
                i += 2
                continue

            # Handle vowel sequences
            if result and result[-1] == 'a' and char in GurmukhiISO15919.VOWELS:
                result += "'" + GurmukhiISO15919.VOWELS[char]
                i += 1
                continue

            # Check two-char Persian combinations (base consonant + nukta ਼)
            # before the single-char lookup, which would match the base alone
            two_char = text[i:i+2] if i + 1 < len(text) else ''
            if two_char in GurmukhiISO15919.CONSONANTS:
                result += GurmukhiISO15919.CONSONANTS[two_char]
                after = text[i + 2] if i + 2 < len(text) else None
                if after not in GurmukhiISO15919.VOWEL_DIACRITICS and after != '੍':
                    if not delete_schwa or i not in deletions:
                        result += 'a'
                i += 2
                continue

            # Process regular characters
            if char in GurmukhiISO15919.CONSONANTS:
                result += GurmukhiISO15919.CONSONANTS[char]
                if next_char not in GurmukhiISO15919.VOWEL_DIACRITICS and next_char != '੍':
                    if not delete_schwa or i not in deletions:
                        result += 'a'
            elif char in GurmukhiISO15919.VOWEL_DIACRITICS:
                result += GurmukhiISO15919.VOWEL_DIACRITICS[char]
            elif char in GurmukhiISO15919.VOWELS:
                result += GurmukhiISO15919.VOWELS[char]

            i += 1

        return result
