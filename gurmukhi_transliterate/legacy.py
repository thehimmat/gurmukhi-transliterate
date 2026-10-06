"""
Legacy encoding conversion system for Gurmukhi script.

Handles conversion from:
- Font-based encodings (AnmolLipi, GurbaniAkhar, etc.)
- Keyboard mappings (ASCII-based input)
to Unicode Gurmukhi.

This module serves as a pre-processor for other transliteration systems,
allowing them to work with both Unicode and legacy input formats.
"""

import logging
import unicodedata
from dataclasses import dataclass, field


@dataclass(frozen=True)
class ConversionWarning:
    position: int  # index into the input text
    char: str
    kind: str      # 'unmapped' | 'orphan_sihari'
    message: str


@dataclass
class ConversionResult:
    text: str
    warnings: list[ConversionWarning] = field(default_factory=list)


class GurmukhiLegacy:
    # Special combinations that need to be processed first
    SPECIAL_COMBINATIONS = {
        '<>': 'ੴ',    # Ik Onkar
        'ÅÆ': 'ੴ',    # Ik Onkar (alternative)
        '[]': '॥',     # Double danda
        ']': '॥',      # Single closing bracket to double danda
        '[': '।',      # Single opening bracket to single danda
        'W': 'ਾਂ',     # pre-composed kanna + bindi
        '`N': 'ਁ',     # udaat
        '`ˆ': 'ਁ',     # udaat (alternative)
        '~N': 'ਁ',     # udaat (alternative)
        '~ˆ': 'ਁ',     # udaat (alternative)
        'ƒ': 'ਨੂੰ',    # noon + dulainkar + tippi
        
        # Vowel combinations with ਅ (airha)
        'Aw': 'ਆ',     # airha + kanna
        'AW': 'ਆਂ',    # airha + kanna + bindi
        'AY': 'ਐ',     # airha + dulavan
        'AO': 'ਔ',     # airha + kanaura
        
        # Vowel combinations with ੲ (iri)
        'ie': 'ਇ',   # iri + sihari
        'eI': 'ਈ',   # iri + bihari
        'ey': 'ਏ',   # iri + lavan
        
        # Vowel combinations with ੳ (oora)
        'au': 'ਉ',   # oora + aunkar
        'aU': 'ਊ',   # oora + dulainkar
        'E': 'ਓ',   # oora + hora
        
        # Persian character combinations (alternatives to pre-built characters)
        'sæ': '\u0A36',    # Alternative to 'S' (ਸ਼)
        'Kæ': '\u0A59',    # Alternative to '^' (ਖ਼)
        'gæ': '\u0A5A',    # Alternative to 'Z' (ਗ਼)
        'jæ': '\u0A5B',    # Alternative to 'z' (ਜ਼)
        'Pæ': '\u0A5E',    # Alternative to '&' (ਫ਼)
        'læ': '\u0A33',    # Alternative to 'L' (ਲ਼)
        
        # Persian combinations without pre-built alternatives
        'kæ': 'ਕ਼',    # k + nukta (no pre-built version)
        'Aæ': 'ਅ਼',    # A + nukta (no pre-built version)
    }

    # AnmolLipi font mapping for single characters
    ANMOLLIPI_MAP = {
        # Base vowel carriers
        'a': 'ੳ',     # oora
        'A': 'ਅ',     # airha
        'e': 'ੲ',     # iri

        # Vowel marks with alternatives
        'w': 'ਾ',     # kanna
        'i': 'ਿ',     # sihari
        'I': 'ੀ',     # bihari
        'u': 'ੁ',     # aunkar
        'ü': 'ੁ',     # aunkar (alternative)
        'U': 'ੂ',     # dulainkar
        '¨': 'ੂ',     # dulainkar (alternative)
        'y': 'ੇ',     # lavan
        'Y': 'ੈ',     # dulavan
        'o': 'ੋ',     # hora
        'O': 'ੌ',     # kanaura

        # Special marks with alternatives
        'M': 'ੰ',     # tippi
        'µ': 'ੰ',     # tippi (alternative)
        'N': 'ਂ',     # bindi
        'ˆ': 'ਂ',     # bindi (alternative)
        'æ': '਼',     # nukta
        'Ú': 'ਃ',     # visarg
        
        # Single character Ik Onkar
        '¡': 'ੴ',     # Ik Onkar
        
        # Alternative characters that map to same output
        '<': 'Å',     # Maps to Å
        'Å': 'Å',     # Ura
        '>': 'Æ',     # Maps to Æ
        'Æ': 'Æ',     # Ura
        
        # Consonants
        's': 'ਸ',
        'h': 'ਹ',
        'k': 'ਕ',
        'K': 'ਖ',
        'g': 'ਗ',
        'G': 'ਘ',
        '|': 'ਙ',
        'c': 'ਚ',
        'C': 'ਛ',
        'j': 'ਜ',
        'J': 'ਝ',
        '\\': 'ਞ',
        't': 'ਟ',
        'T': 'ਠ',
        'f': 'ਡ',
        'F': 'ਢ',
        'x': 'ਣ',
        'q': 'ਤ',
        'Q': 'ਥ',
        'd': 'ਦ',
        'D': 'ਧ',
        'n': 'ਨ',
        'p': 'ਪ',
        'P': 'ਫ',
        'b': 'ਬ',
        'B': 'ਭ',
        'm': 'ਮ',
        'X': 'ਯ',
        'r': 'ਰ',
        'l': 'ਲ',
        'v': 'ਵ',
        'V': 'ੜ',

        # Special characters
        'M': 'ੰ',   # tippi
        'N': 'ਂ',   # bindi
        '`': 'ੱ',   # addak
        '~': 'ੱ',   # addak (alternative)
        '@': '੍',   # halant/virama
        '¤': 'ੴ',   # Ek Onkar
        
        # Numbers
        '0': '੦',
        '1': '੧',
        '2': '੨',
        '3': '੩',
        '4': '੪',
        '5': '੫',
        '6': '੬',
        '7': '੭',
        '8': '੮',
        '9': '੯',

        # Preserve spaces and newlines
        ' ': ' ',
        '\n': '\n',

        # Persian characters (using pre-composed characters)
        'L': 'ਲ਼',    # Laam (pre-composed)
        'S': 'ਸ਼',    # Sheen (pre-composed)
        'z': 'ਜ਼',    # Zaal (pre-composed)
        'Z': 'ਗ਼',    # Ghayn (pre-composed)
        '^': 'ਖ਼',    # Khay (pre-composed)
        '&': 'ਫ਼',    # Faa (pre-composed)

        # Move E to ANMOLLIPI_MAP
        'E': 'ਓ',     # oora + hora (direct mapping)
    }

    # Special subjoined characters in AnmolLipi
    SUBJOINED_MAP = {
        'H': '੍ਹ',    # pair haha
        '†': '੍ਟ',    # pair tainka
        '˜': '੍ਨ',    # pair nanna
        'œ': '੍ਤ',    # pair tatta
        'R': '੍ਰ',    # pair rara
        'Î': '੍ਯ',    # sanyukt yayya
        '´': 'ੵ',     # yakash
        'Ï': 'ੵ',     # yakash (alternate)
        'Í': '੍ਵ',    # pair vava
        'ç': '੍ਚ',    # pair chachha
        '®': '੍ਰ',    # pair rara
    }

    # ASCII punctuation with no Gurmukhi meaning in the font; passed through as-is.
    # ':' is a literal colon here (visarg is 'Ú').
    PASSTHROUGH = set(' \t\r\n,:;-?!()\'".*')

    SIHARI_KEY = 'i'
    NUKTA_KEY = 'æ'

    @staticmethod
    def _is_cluster_base(unicode_char: str) -> bool:
        """True for consonants (incl. nukta forms) and the vowel carriers ੳ ਅ ੲ."""
        cp = ord(unicode_char[0])
        return (0x0A15 <= cp <= 0x0A39 or 0x0A59 <= cp <= 0x0A5E
                or unicode_char[0] in 'ਅੲੳ')

    @classmethod
    def _is_word_break(cls, unicode_char: str) -> bool:
        """Characters a sihari may never attach to or move across."""
        cp = ord(unicode_char[0])
        return (unicode_char[0] in cls.PASSTHROUGH
                or 0x0A66 <= cp <= 0x0A6F       # digits
                or unicode_char[0] in '।॥ੴ')

    @classmethod
    def _match(cls, text: str, i: int):
        """Return (unicode, length) for the token at i, or (None, 1) if unmapped."""
        for combo, replacement in cls.SPECIAL_COMBINATIONS.items():
            if text.startswith(combo, i):
                return replacement, len(combo)
        if text[i] in cls.ANMOLLIPI_MAP:
            return cls.ANMOLLIPI_MAP[text[i]], 1
        if text[i] in cls.SUBJOINED_MAP:
            return cls.SUBJOINED_MAP[text[i]], 1
        return None, 1

    @classmethod
    def convert(cls, text: str, encoding: str = 'anmollipi') -> 'ConversionResult':
        """Convert legacy encoded text to Unicode Gurmukhi, reporting anything suspect.

        Line structure is preserved exactly, and no input character is dropped:
        unmapped characters pass through and are reported in ``warnings``.
        """
        if encoding.lower() != 'anmollipi':
            raise ValueError(f"Unsupported encoding: {encoding}")

        sihari = cls.ANMOLLIPI_MAP[cls.SIHARI_KEY]
        chars = []
        warnings = []
        pending_sihari = None    # input position of a sihari waiting for its consonant
        last_cluster_end = None  # where an orphan sihari goes, within the current word

        def flush_orphan():
            nonlocal pending_sihari
            if pending_sihari is None:
                return
            at = last_cluster_end if last_cluster_end is not None else len(chars)
            chars.insert(at, sihari)
            warnings.append(ConversionWarning(
                pending_sihari, cls.SIHARI_KEY, 'orphan_sihari',
                'sihari with no following consonant in its word'))
            pending_sihari = None

        i = 0
        while i < len(text):
            unicode_char, length = cls._match(text, i)

            if unicode_char is None:
                if text[i] in cls.PASSTHROUGH:
                    unicode_char = text[i]
                else:
                    flush_orphan()
                    last_cluster_end = None
                    chars.append(text[i])
                    warnings.append(ConversionWarning(
                        i, text[i], 'unmapped', 'no mapping; passed through'))
                    i += 1
                    continue

            if length == 1 and text[i] == cls.SIHARI_KEY:
                if pending_sihari is not None:
                    flush_orphan()
                pending_sihari = i
                i += 1
                continue

            if cls._is_cluster_base(unicode_char):
                chars.append(unicode_char)
                i += length
                # The cluster continues through a nukta and any subjoined letters.
                while i < len(text) and (text[i] == cls.NUKTA_KEY or text[i] in cls.SUBJOINED_MAP):
                    chars.append(cls.SUBJOINED_MAP.get(text[i], cls.ANMOLLIPI_MAP[cls.NUKTA_KEY]))
                    i += 1
                if pending_sihari is not None:
                    chars.append(sihari)
                    pending_sihari = None
                last_cluster_end = len(chars)
                continue

            if cls._is_word_break(unicode_char):
                flush_orphan()
                last_cluster_end = None

            chars.append(unicode_char)
            i += length

        flush_orphan()
        return ConversionResult(unicodedata.normalize('NFC', ''.join(chars)), warnings)

    @classmethod
    def to_unicode(cls, text: str, encoding: str = 'anmollipi') -> str:
        """Convert legacy encoded text to Unicode Gurmukhi.

        Warnings (unmapped characters, orphan sihari) are logged; use ``convert``
        to receive them as data.
        """
        result = cls.convert(text, encoding)
        logger = logging.getLogger(__name__)
        for w in result.warnings:
            logger.warning("%s at position %d (%r): %s", w.kind, w.position, w.char, w.message)
        return result.text

    @classmethod
    def detect_encoding(cls, text: str) -> str:
        """Attempt to detect the encoding of the input text."""
        return 'unicode' 