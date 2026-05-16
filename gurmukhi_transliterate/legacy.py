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

    @classmethod
    def to_unicode(cls, text: str, encoding: str = 'anmollipi') -> str:
        """Convert legacy encoded text to Unicode Gurmukhi."""
        if not text:
            return ""
            
        if encoding.lower() != 'anmollipi':
            raise ValueError(f"Unsupported encoding: {encoding}")

        logger = logging.getLogger(__name__)
        
        try:
            chars = []
            sihari_position = None
            i = 0
            while i < len(text):
                # Check for special combinations FIRST
                found_special = False
                for combo, replacement in cls.SPECIAL_COMBINATIONS.items():
                    if text[i:i+len(combo)] == combo:
                        chars.append(replacement)
                        i += len(combo)
                        found_special = True
                        break
                
                if found_special:
                    continue

                char = text[i]
                next_char = text[i + 1] if i + 1 < len(text) else None

                # Handle sihari
                if char == 'i':  # sihari
                    sihari_position = len(chars)  # Mark position for later insertion
                    i += 1
                    continue

                # Process regular characters first
                if char in cls.ANMOLLIPI_MAP:
                    base_pos = len(chars)
                    chars.append(cls.ANMOLLIPI_MAP[char])
                    
                    # Look ahead for subjoined characters
                    next_pos = i + 1
                    while next_pos < len(text) and text[next_pos] in cls.SUBJOINED_MAP:
                        chars.append(cls.SUBJOINED_MAP[text[next_pos]])
                        next_pos += 1
                    
                    # Insert sihari after base and its subjoined characters
                    if sihari_position is not None and sihari_position <= base_pos:
                        chars.insert(len(chars), cls.ANMOLLIPI_MAP['i'])
                        sihari_position = None
                        
                    i = next_pos
                    continue
                
                i += 1

            # Add any remaining sihari
            if sihari_position is not None:
                chars.append(cls.ANMOLLIPI_MAP['i'])

        except Exception as e:
            logger.error(f"Error at position {i}: {str(e)}")
            raise

        result = ''.join(chars)
        lines = [line.strip() for line in result.split('\n') if line.strip()]
        return unicodedata.normalize('NFC', '\n\n'.join(lines))

    @classmethod
    def detect_encoding(cls, text: str) -> str:
        """Attempt to detect the encoding of the input text."""
        return 'unicode' 