"""
Legacy encoding conversion system for Gurmukhi script.

Handles conversion from:
- Font-based encodings: the phonetic AnmolLipi/GurbaniAkhar layout and the
  typewriter layout of Asees and Joy (``ENCODINGS``)
- Keyboard mappings (ASCII-based input)
to Unicode Gurmukhi.

Each font family is a ``Layout``: a key map plus a few typing conventions
(sihari is typed before its consonant; Asees/Joy type subjoined letters
after the vowel sign and use one key for tippi and bindi). One conversion
loop serves every layout.

This module serves as a pre-processor for other transliteration systems,
allowing them to work with both Unicode and legacy input formats.
"""

import logging
import re
import unicodedata
from dataclasses import asdict, dataclass, field
from functools import lru_cache

from ._legacy_layouts import ASEES_KEYS, JOY_COMBOS, JOY_KEYS


@dataclass(frozen=True)
class ConversionWarning:
    position: int  # index into the input text
    char: str
    kind: str      # 'unmapped' | 'orphan_sihari'
    message: str


@dataclass(frozen=True)
class EncodingGuess:
    label: str    # 'unicode' | one of ENCODINGS | 'latin' | 'unknown'
    score: float  # confidence in label, 0..1


@dataclass
class ConversionResult:
    text: str
    warnings: list[ConversionWarning] = field(default_factory=list)
    encoding: str = 'anmollipi'   # the layout used


@dataclass(frozen=True)
class Layout:
    """A legacy font's keyboard layout."""
    name: str
    label: str
    keys: dict          # single key → Unicode (one or more code points)
    combos: dict        # key sequences matched before single keys, in order
    sihari: frozenset   # keys for sihari, typed before the consonant
    passthrough: frozenset  # unmapped keys that are literal text, not errors
    fonts: tuple = ()   # font names (lowercase prefixes) that use this layout
    one_nasal_key: bool = False  # tippi and bindi share a key: pick by vowel
    join_dandas: bool = False    # '।।' typed as two single dandas → '॥'


# Independent vowels some layouts build from a carrier plus a sign
_COMPOSE = (('ਅਾ', 'ਆ'), ('ਅੈ', 'ਐ'), ('ਅੌ', 'ਔ'), ('ੲਿ', 'ਇ'), ('ੲੀ', 'ਈ'), ('ੲੇ', 'ਏ'),
            ('ੳੁ', 'ਉ'), ('ੳੂ', 'ਊ'), ('ੳੋ', 'ਓ'))
# Bindi, not tippi, goes with these vowels
_BINDI_AFTER = re.compile('(?<=[ਾੀੇੈੋੌਆਈਏਐਓਔ])ੰ')
# Keys whose output joins the preceding consonant: nukta, virama, yakash
_JOINS = ('\u0a3c', '\u0a4d', '\u0a75')


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

    @staticmethod
    def _is_word_break(unicode_char: str) -> bool:
        """Characters a sihari may never attach to or move across."""
        c = unicode_char[0]
        return (not '\u0A00' <= c <= '\u0A7F'      # spaces, punctuation, Latin digits
                or '\u0A66' <= c <= '\u0A6F'       # Gurmukhi digits
                or c in '।॥ੴ')

    @staticmethod
    def _match(layout: 'Layout', text: str, i: int):
        """Return (unicode, length) for the token at i, or (None, 1) if unmapped."""
        for combo, replacement in layout.combos.items():
            if text.startswith(combo, i):
                return replacement, len(combo)
        if text[i] in layout.keys:
            return layout.keys[text[i]], 1
        return None, 1

    @classmethod
    def layout(cls, encoding: str) -> 'Layout':
        try:
            return LAYOUTS[encoding.lower()]
        except KeyError:
            raise ValueError(f"Unsupported encoding: {encoding}; choose from {ENCODINGS}") from None

    @classmethod
    def convert(cls, text: str, encoding: str = 'anmollipi') -> 'ConversionResult':
        """Convert legacy encoded text to Unicode Gurmukhi, reporting anything suspect.

        *encoding* is one of ``ENCODINGS``, or ``'auto'`` to detect it (falling
        back to AnmolLipi when the text doesn't look legacy-encoded).

        Line structure is preserved exactly, and no input character is dropped:
        unmapped characters pass through and are reported in ``warnings``.
        """
        if encoding.lower() == 'auto':
            guess = cls._guess(text).label
            encoding = guess if guess in LAYOUTS else 'anmollipi'
        layout = cls.layout(encoding)
        sihari = 'ਿ'
        chars = []
        warnings = []
        pending_sihari = None    # input position of a sihari waiting for its consonant
        last_cluster_end = None  # where an orphan sihari goes, within the current word
        cons_end = None          # end of the current cluster's consonant part

        def flush_orphan():
            nonlocal pending_sihari
            if pending_sihari is None:
                return
            at = last_cluster_end if last_cluster_end is not None else len(chars)
            chars.insert(at, sihari)
            warnings.append(ConversionWarning(
                pending_sihari, text[pending_sihari], 'orphan_sihari',
                'sihari with no following consonant in its word'))
            pending_sihari = None

        i = 0
        while i < len(text):
            unicode_char, length = cls._match(layout, text, i)

            if unicode_char is None:
                if text[i] in layout.passthrough:
                    unicode_char = text[i]
                else:
                    flush_orphan()
                    last_cluster_end = cons_end = None
                    chars.append(text[i])
                    warnings.append(ConversionWarning(
                        i, text[i], 'unmapped', 'no mapping; passed through'))
                    i += 1
                    continue

            if not unicode_char:       # decorative key (e.g. a headline bar)
                i += length
                continue

            if length == 1 and text[i] in layout.sihari:
                if pending_sihari is not None:
                    flush_orphan()
                pending_sihari = i
                i += 1
                continue

            if cls._is_cluster_base(unicode_char):
                # a key may carry a whole syllable (Joy: ਕੇ, ਪ੍ਰ): split off its signs
                k = 1
                while k < len(unicode_char) and (unicode_char[k] in _JOINS
                                                 or cls._is_cluster_base(unicode_char[k])):
                    k += 1
                chars.append(unicode_char[:k])
                i += length
                # The cluster continues through a nukta, subjoined letters and
                # a bare virama with its consonant.
                while i < len(text):
                    nxt, n = cls._match(layout, text, i)
                    if not nxt or nxt[0] not in _JOINS:
                        break
                    chars.append(nxt)
                    i += n
                    if nxt == '\u0a4d' and i < len(text):
                        after, n = cls._match(layout, text, i)
                        if after and cls._is_cluster_base(after):
                            chars.append(after)
                            i += n
                cons_end = len(chars)
                if pending_sihari is not None:
                    chars.append(sihari)
                    pending_sihari = None
                if unicode_char[k:]:
                    chars.append(unicode_char[k:])
                last_cluster_end = len(chars)
                continue

            if unicode_char[0] in _JOINS and cons_end is not None:
                # typed after the vowel sign (Asees/Joy): belongs with the consonant
                chars.insert(cons_end, unicode_char)
                cons_end += 1
                last_cluster_end = len(chars)
                i += length
                continue

            if cls._is_word_break(unicode_char):
                flush_orphan()
                last_cluster_end = cons_end = None

            chars.append(unicode_char)
            i += length

        flush_orphan()
        out = ''.join(chars)
        for parts, vowel in _COMPOSE:
            out = out.replace(parts, vowel)
        if layout.one_nasal_key:
            out = _BINDI_AFTER.sub('ਂ', out)
        if layout.join_dandas:
            out = out.replace('।।', '॥')
        return ConversionResult(unicodedata.normalize('NFC', out), warnings, layout.name)

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

    # Dependent signs that can never start a word in AnmolLipi. Sihari ('i') is
    # typed before its consonant, so it may.
    VOWEL_SIGN_KEYS = set('wIuUyYoOü¨')
    NON_INITIAL_KEYS = VOWEL_SIGN_KEYS | set('MNµˆWæÚ`~@') | set(SUBJOINED_MAP)
    # Minimum (length-weighted) share of plausible words to call ASCII text legacy.
    LEGACY_THRESHOLD = 0.8

    @classmethod
    def _is_plausible_legacy_word(cls, word: str) -> bool:
        """Whether a word obeys AnmolLipi spelling structure.

        English (and most romanised) words break these rules constantly: in
        AnmolLipi 'a' (ੳ) only carries u/U/o, 'e' (ੲ) only carries sihari,
        bihari or lavan, and dependent vowel signs never start a word or stack.
        """
        letters = [c for c in word if c not in cls.PASSTHROUGH]
        if not letters or letters[0] in cls.NON_INITIAL_KEYS:
            return False
        for j, c in enumerate(letters):
            nxt = letters[j + 1] if j + 1 < len(letters) else ''
            prev = letters[j - 1] if j else ''
            if c == 'a' and nxt not in ('u', 'U', 'o', 'ü', '¨'):
                return False
            if c == 'e' and prev != 'i' and nxt not in ('I', 'y', 'Y'):
                return False
            if c in cls.VOWEL_SIGN_KEYS and nxt in cls.VOWEL_SIGN_KEYS:
                return False
        return True

    @classmethod
    def _guess(cls, text: str) -> EncodingGuess:
        legacy_keys = (set(cls.ANMOLLIPI_MAP) | set(cls.SUBJOINED_MAP)
                       | {k for k in cls.SPECIAL_COMBINATIONS if len(k) == 1})
        gurmukhi = sum(1 for c in text if '\u0A00' <= c <= '\u0A7F')
        latin = sum(1 for c in text if c.isalpha() and c not in legacy_keys
                    and not '\u0A00' <= c <= '\u0A7F')
        if gurmukhi and gurmukhi >= latin:
            letters = gurmukhi + sum(1 for c in text if c.isalpha() and c.isascii())
            return EncodingGuess('unicode', gurmukhi / max(letters, gurmukhi))

        plausible = total = 0
        for raw in text.split():
            # Digits and brackets carry no signal: they occur in both encodings.
            word = ''.join(c for c in raw if not (c.isdigit() or c in '[]<>¡'))
            if not any(c.isalpha() for c in word):
                continue
            weight = len(word)
            total += weight
            if not any(c.isalpha() and c not in legacy_keys for c in word) \
                    and cls._is_plausible_legacy_word(word):
                plausible += weight
        if not total:
            return EncodingGuess('unknown', 0.0)
        # Asees/Joy put letters on punctuation keys, so AnmolLipi's spelling
        # rules can't judge them: convert and look the words up instead.
        typewriter, found = max(((e, cls._lexicon_share(text, e)) for e in TYPEWRITER),
                                key=lambda x: x[1])
        if found >= cls.LEXICON_THRESHOLD and found > cls._lexicon_share(text, 'anmollipi'):
            return EncodingGuess(typewriter, found)
        share = plausible / total
        if share >= cls.LEGACY_THRESHOLD:
            return EncodingGuess('anmollipi', share)
        return EncodingGuess('latin', 1 - share)

    # Share of converted words found in the Gurbani lexicon needed to call text
    # Asees/Joy-encoded.
    LEXICON_THRESHOLD = 0.6

    @classmethod
    def _lexicon_share(cls, text: str, encoding: str) -> float:
        # one-letter words match the lexicon by chance, so they don't count
        words = [w for w in re.findall('[\u0A01-\u0A63\u0A70-\u0A75]+', cls.convert(text, encoding).text)
                 if len(w) > 1]
        lexicon = _lexicon_words()
        return sum(w in lexicon for w in words) / len(words) if words else 0.0

    @staticmethod
    def encoding_for_font(font_name: str) -> str | None:
        """The encoding a font uses, from its name as a PDF or word processor
        reports it ('CKPHAK+Asees', 'GurbaniAkharThick'), or None if unknown."""
        name = re.sub(r'^[A-Z]{6}\+', '', font_name).lower()
        name = re.sub(r'[\s_-]', '', name)
        for layout in LAYOUTS.values():
            if any(name.startswith(f) for f in layout.fonts):
                return layout.name
        return None

    @classmethod
    def detect_encoding(cls, text: str) -> str:
        """Guess the encoding of *text*: 'unicode', one of ``ENCODINGS``
        ('anmollipi', 'asees', 'joy'), 'latin' or 'unknown'.

        'anmollipi' covers the GurbaniAkhar/AnmolLipi keyboard family. 'latin'
        means Latin-script text that isn't legacy Gurmukhi: English, or
        romanised Gurmukhi (see ``detect_latin`` for telling those apart).

        Asees and Joy are recognised by converting the text and looking the
        words up in the Gurbani lexicon; they share their letter keys, so text
        without their few differing keys reads as 'asees'. AnmolLipi is
        recognised structurally: ASCII words are checked against its spelling
        rules. A short line made only of words that are also valid AnmolLipi
        (e.g. 'so is it') is genuinely ambiguous and reads as legacy. When
        the font is known, ``encoding_for_font`` is more reliable.
        """
        return cls._guess(text).label

    @classmethod
    def detect_lines(cls, text: str) -> list[EncodingGuess]:
        """One :class:`EncodingGuess` per line of *text*, for routing mixed pages."""
        return [cls._guess(line) for line in text.split('\n')]


@lru_cache(maxsize=1)
def _lexicon_words() -> frozenset[str]:
    from .lexicon import load_lexicon
    return frozenset(load_lexicon())


_ANMOLLIPI = GurmukhiLegacy
LAYOUTS = {
    'anmollipi': Layout(
        'anmollipi', 'AnmolLipi / GurbaniAkhar',
        keys={**_ANMOLLIPI.ANMOLLIPI_MAP, **_ANMOLLIPI.SUBJOINED_MAP},
        combos=_ANMOLLIPI.SPECIAL_COMBINATIONS,
        sihari=frozenset(_ANMOLLIPI.SIHARI_KEY),
        passthrough=frozenset(_ANMOLLIPI.PASSTHROUGH),
        fonts=('anmollipi', 'gurbaniakhar', 'gurbanilipi', 'prabhki', 'webakhar')),
    'asees': Layout(
        'asees', 'Asees', keys=ASEES_KEYS, combos={}, sihari=frozenset('f'),
        passthrough=frozenset(' \t\r\n0123456789,()'), fonts=('asees',),
        one_nasal_key=True, join_dandas=True),
    'joy': Layout(
        'joy', 'Joy', keys=JOY_KEYS, combos=JOY_COMBOS, sihari=frozenset('f\xd0'),
        passthrough=frozenset(' \t\r\n0123456789,()'), fonts=('joy',),
        one_nasal_key=True, join_dandas=True),
}
ENCODINGS = tuple(LAYOUTS)
TYPEWRITER = ('asees', 'joy')


def conversion_report(text: str, encoding: str | None = None, font: str | None = None) -> dict:
    """Convert *text* and describe it, as a JSON-ready dict for API responses.

    The encoding is *encoding* if given, else the one *font* uses (see
    ``encoding_for_font``), else detected; text that doesn't look legacy is
    converted as AnmolLipi.

    Keys: ``unicode`` (converted text), ``encoding`` (whole-text guess),
    ``converted_with`` (the layout used), ``lines`` (one ``{label, score}``
    per input line) and ``warnings``.
    """
    detected = GurmukhiLegacy.detect_encoding(text)
    used = (encoding or (GurmukhiLegacy.encoding_for_font(font) if font else None)
            or (detected if detected in LAYOUTS else 'anmollipi'))
    result = GurmukhiLegacy.convert(text, used)
    return {
        'unicode': result.text,
        'encoding': detected,
        'converted_with': result.encoding,
        'lines': [asdict(g) for g in GurmukhiLegacy.detect_lines(text)],
        'warnings': [asdict(w) for w in result.warnings],
    }
