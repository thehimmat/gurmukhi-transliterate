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
from ._tokens import normalize, tokenize


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

    # Same convention as ISO 15919 (tippi ṃ, bindi ṁ); practical output itself
    # writes nasals as m/n by context.
    MODIFIERS = {
        '੍': '', 'ੰ': 'ṃ', 'ਂ': 'ṁ', 'ੱ': '', '਼': '',
    }

    LABIAL_CONSONANTS = {'ਬ', 'ਭ', 'ਪ', 'ਫ', 'ਮ'}

    # An aspirate geminates as its unaspirated partner + itself (ਮੁੱਖ → mukkh).
    UNASPIRATED = {
        'ਖ': 'ਕ', 'ਘ': 'ਗ', 'ਛ': 'ਚ', 'ਝ': 'ਜ', 'ਠ': 'ਟ',
        'ਢ': 'ਡ', 'ਥ': 'ਤ', 'ਧ': 'ਦ', 'ਫ': 'ਪ', 'ਭ': 'ਬ',
    }

    @classmethod
    def to_practical(cls, text: str, delete_schwa: bool = False) -> str:
        """Convert Gurmukhi text to practical romanization.

        Args:
            text:         Gurmukhi Unicode string.
            delete_schwa: Apply schwa deletion rules (R1 word-final, R2
                          pre-vocalic, R3 cascade). Default False.
        """
        C = cls.CONSONANTS
        text = normalize(text)
        deletions: set[int] = (
            compute_deletions(text, set(C.keys()), set(cls.VOWEL_DIACRITICS.keys()))
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
                    partner = cls.UNASPIRATED.get(tok.text)
                    result += C[partner] if partner else rom
                    geminate = False
                result += rom
                if nxt is not None and nxt.kind == 'sign':
                    result += cls.VOWEL_DIACRITICS[nxt.text]
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
                labial = nxt is not None and nxt.kind == 'cons' and nxt.text in cls.LABIAL_CONSONANTS
                result += 'm' if labial else 'n'
            elif tok.kind == 'sign':
                result += cls.VOWEL_DIACRITICS[tok.text]
            elif tok.kind == 'vowel' and tok.text in cls.VOWELS:
                result += cls.VOWELS[tok.text]
            elif tok.kind == 'other':
                ch = tok.text
                if ch in cls.SPECIAL_SYMBOLS:
                    result += cls.SPECIAL_SYMBOLS[ch]
                elif ch in cls.NUMBERS:
                    result += cls.NUMBERS[ch]
                elif ch in cls.PUNCTUATION:
                    result += cls.PUNCTUATION[ch]
            j += 1

        return result
