"""
Practical transliteration system for Gurmukhi script.

Provides intuitive phonetic mappings for general use:
- Keyboard-accessible doubles instead of diacritics (aa, ee, oo)
- Context-aware nasalization (m before labials, n elsewhere)

Use cases:
- General text display
- User-friendly searching
- Casual transliteration
"""

from .schwa import compute_deletions


class GurmukhiPractical:
    SPECIAL_SYMBOLS = {
        'ੴ': 'ik oankaar'
    }

    NUMBERS = {
        '੦': '0', '੧': '1', '੨': '2', '੩': '3', '੪': '4',
        '੫': '5', '੬': '6', '੭': '7', '੮': '8', '੯': '9'
    }

    VOWELS = {
        'ਅ': 'a', 'ਆ': 'aa', 'ਇ': 'i', 'ਈ': 'ee',
        'ਉ': 'u', 'ਊ': 'oo', 'ਏ': 'e', 'ਐ': 'ai',
        'ਓ': 'o', 'ਔ': 'au'
    }

    VOWEL_DIACRITICS = {
        'ਾ': 'aa', 'ਿ': 'i', 'ੀ': 'ee',
        'ੁ': 'u', 'ੂ': 'oo', 'ੇ': 'e',
        'ੈ': 'ai', 'ੋ': 'o', 'ੌ': 'au',
    }

    CONSONANTS = {
        'ਸ': 's', 'ਹ': 'h',
        'ਕ': 'k', 'ਖ': 'kh', 'ਗ': 'g', 'ਘ': 'gh', 'ਙ': 'ng',
        'ਚ': 'ch', 'ਛ': 'chh', 'ਜ': 'j', 'ਝ': 'jh', 'ਞ': 'ny',
        'ਟ': 'ṭ', 'ਠ': 'ṭh', 'ਡ': 'ḍ', 'ਢ': 'ḍh', 'ਣ': 'ṇ',
        'ਤ': 't', 'ਥ': 'th', 'ਦ': 'd', 'ਧ': 'dh', 'ਨ': 'n',
        'ਪ': 'p', 'ਫ': 'ph', 'ਬ': 'b', 'ਭ': 'bh', 'ਮ': 'm',
        'ਯ': 'y', 'ਰ': 'r', 'ਲ': 'l', 'ਵ': 'v', 'ੜ': 'ṛ',
        # Persian-influenced letters
        'ਖ਼': 'k̲h', 'ਗ਼': 'ġh', 'ਜ਼': 'z', 'ਫ਼': 'f',
        'ਸ਼': 'sh', 'ਲ਼': 'ḷ', 'ਕ਼': 'q',
    }

    PUNCTUATION = {
        '॥': '||', '।': '|', ' ': ' ', '.': '.', ',': ',',
        '?': '?', '!': '!', '"': '"', "'": "'", '\n': '\n',
    }

    MODIFIERS = {
        '੍': '', 'ੰ': 'ṁ', 'ਂ': 'ṃ', 'ੱ': '', '਼': '',
    }

    LABIAL_CONSONANTS = {'ਬ', 'ਭ', 'ਪ', 'ਫ', 'ਮ'}

    @classmethod
    def to_practical(cls, text: str, delete_schwa: bool = False) -> str:
        """Convert Gurmukhi text to practical romanization.

        Args:
            text:         Gurmukhi Unicode string.
            delete_schwa: Apply schwa deletion rules (R1 word-final, R2
                          pre-vocalic, R3 cascade). Default False.
        """
        deletions: set[int] = (
            compute_deletions(
                text,
                set(cls.CONSONANTS.keys()),
                set(cls.VOWEL_DIACRITICS.keys()),
            )
            if delete_schwa
            else set()
        )
        result = ""
        i = 0
        while i < len(text):
            char = text[i]
            next_char = text[i + 1] if i + 1 < len(text) else None
            next_next_char = text[i + 2] if i + 2 < len(text) else None

            # Nasalization (tippi/bindi) — resolve before consonant
            if next_char in ['ੰ', 'ਂ']:
                if char in cls.CONSONANTS:
                    result += cls.CONSONANTS[char] + 'a'  # include inherent vowel
                elif char in cls.VOWELS:
                    result += cls.VOWELS[char]
                elif char in cls.VOWEL_DIACRITICS:
                    result += cls.VOWEL_DIACRITICS[char]
                result += 'm' if next_next_char in cls.LABIAL_CONSONANTS else 'n'
                i += 2
                continue

            if char in cls.SPECIAL_SYMBOLS:
                result += cls.SPECIAL_SYMBOLS[char]
                i += 1
                continue

            if char in cls.NUMBERS:
                result += cls.NUMBERS[char]
                i += 1
                continue

            if char in cls.PUNCTUATION:
                result += cls.PUNCTUATION[char]
                i += 1
                continue

            if char in cls.CONSONANTS:
                result += cls.CONSONANTS[char]
                if next_char in cls.VOWEL_DIACRITICS:
                    result += cls.VOWEL_DIACRITICS[next_char]
                    # Check for nasalization after the vowel diacritic
                    after_diacritic = text[i + 2] if i + 2 < len(text) else None
                    if after_diacritic in ('ੰ', 'ਂ'):
                        after_nasal = text[i + 3] if i + 3 < len(text) else None
                        result += 'm' if after_nasal in cls.LABIAL_CONSONANTS else 'n'
                        i += 3
                        continue
                    i += 2
                    continue
                elif next_char in cls.MODIFIERS:
                    if next_char == 'ੰ':
                        result += 'n'
                    elif next_char == 'ਂ':
                        result += 'n'
                    elif next_char == 'ੱ':
                        if i + 2 < len(text) and text[i + 2] in cls.CONSONANTS:
                            result += cls.CONSONANTS[text[i + 2]]
                    i += 2
                    continue
                elif next_char not in ['੍', ' ', '।', '॥']:
                    if not delete_schwa or i not in deletions:
                        result += 'a'
                i += 1
                continue

            if char in cls.VOWELS:
                result += cls.VOWELS[char]
                i += 1
                continue

            if char in cls.VOWEL_DIACRITICS:
                result += cls.VOWEL_DIACRITICS[char]
                i += 1
                continue

            if char in cls.MODIFIERS:
                # Standalone tippi/bindi (e.g. word-final after a vowel diacritic)
                if char in ('ੰ', 'ਂ'):
                    result += 'm' if next_char in cls.LABIAL_CONSONANTS else 'n'
                i += 1
                continue

            if char == ' ':
                result += ' '
            i += 1

        return result
