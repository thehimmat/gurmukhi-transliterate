"""
Reverse transliteration: Shackle romanization → Gurmukhi.

Shackle's transcription (see systems.SHACKLE and the source glossary,
Transcription pp. xxi-xxv) is unusually reversible because it preserves the
distinctions Gurmukhi marks but most romanizations collapse: retroflex vs
dental, aspiration, gemination, nasal class, nasalization, and final short
vowels. The inherent ``-a`` written after every unmarked consonant also makes
conjunct detection clean — two consonants with no vowel between them are a
subjoined conjunct, never two syllables.

So the reverse is *mostly deterministic*. The residual ambiguities (documented
per Shackle's own rules) are handled by emitting a single **primary** Gurmukhi
string plus a list of flagged :class:`Ambiguity` points, each carrying the
alternative spelling(s). A later corpus-matching layer can use those flags to
choose among candidate spellings of a real word; this module deliberately does
not guess — it surfaces the choice.

Known ambiguities (kind → resolver is the corpus):
  - ``nasalization``      §6  ṁ → ੰ (ṭippī, primary) or ਂ (bindī)
  - ``aspirate_sonorant`` §3b nh/mh/lh/rh/ṇh/ṛh → subjoined ੍ਹ (primary),
                              which print often omits (ਨਹ / bare)
  - ``gemination``        §4  doubling not marked in old Gurmukhi → collapses
                              (primary); modern addak ੱ offered as alternative
  - ``persian_collision`` §8  a degraded (underline-dropped) kh could be ਖ or ਖ਼

This is a first, rule-based cut. It does not yet handle the rarer bearer-vowel
hiatus forms (ਸਉ saü, ਅਇ aï, §2) or the underlined Perso-Arabic source signs
(s̲ s̲h̲ ż ẓ k͟h, §8) beyond the letters that already carry a distinct diacritic.
"""

from __future__ import annotations

import unicodedata
from dataclasses import dataclass, field


# ---------------------------------------------------------------------------
# Gurmukhi building blocks
# ---------------------------------------------------------------------------

_VIRAMA = '੍'
_ADDAK = 'ੱ'
_TIPPI = 'ੰ'
_BINDI = 'ਂ'
_SUBJOINED_HA = '੍ਹ'


@dataclass(frozen=True)
class _Cons:
    """A consonant token's Gurmukhi data."""
    base: str                     # base Gurmukhi letter (or letter + nukta)
    is_nasal: bool = False        # can head a homorganic nasal group (§5)
    aspirate_sonorant: bool = False  # nh/mh/lh/rh/ṇh/ṛh → base + ੍ਹ (§3b)
    persian_collision: bool = False  # degraded underline could be Persian


# Consonant tokens, longest romanization first for greedy matching.
# Order matters: 'ṇh' before 'ṇ', 'kh' before 'k', etc.
_CONSONANTS: list[tuple[str, _Cons]] = [
    # aspirate sonorants (§3b) — base + subjoined ੍ਹ
    ('ṇh', _Cons('ਣ', aspirate_sonorant=True)),
    ('nh', _Cons('ਨ', aspirate_sonorant=True)),
    ('mh', _Cons('ਮ', aspirate_sonorant=True)),
    ('rh', _Cons('ਰ', aspirate_sonorant=True)),
    ('lh', _Cons('ਲ', aspirate_sonorant=True)),
    ('ṛh', _Cons('ੜ', aspirate_sonorant=True)),
    # aspirated stops — single Gurmukhi letters
    ('kh', _Cons('ਖ', persian_collision=True)),  # or Persian ਖ਼ if underlined
    ('gh', _Cons('ਘ')),
    ('ch', _Cons('ਛ')),
    ('jh', _Cons('ਝ')),
    ('ṭh', _Cons('ਠ')),
    ('ḍh', _Cons('ਢ')),
    ('th', _Cons('ਥ')),
    ('dh', _Cons('ਧ')),
    ('ph', _Cons('ਫ')),
    ('bh', _Cons('ਭ')),
    # Perso-Arabic letters with a distinct diacritic (reversible)
    ('ś', _Cons('ਸ਼')),
    ('ṣ', _Cons('ਸ਼')),
    ('ġ', _Cons('ਗ਼')),
    ('z', _Cons('ਜ਼')),
    ('f', _Cons('ਫ਼')),
    ('q', _Cons('ਕ਼')),
    # simple consonants
    ('s', _Cons('ਸ')),
    ('h', _Cons('ਹ')),
    ('k', _Cons('ਕ')),
    ('g', _Cons('ਗ')),
    ('ṅ', _Cons('ਙ', is_nasal=True)),
    ('c', _Cons('ਚ')),
    ('j', _Cons('ਜ')),
    ('ñ', _Cons('ਞ', is_nasal=True)),
    ('ṭ', _Cons('ਟ')),
    ('ḍ', _Cons('ਡ')),
    ('ṇ', _Cons('ਣ', is_nasal=True)),
    ('t', _Cons('ਤ')),
    ('d', _Cons('ਦ')),
    ('n', _Cons('ਨ', is_nasal=True)),
    ('p', _Cons('ਪ')),
    ('b', _Cons('ਬ')),
    ('m', _Cons('ਮ', is_nasal=True)),
    ('y', _Cons('ਯ')),
    ('r', _Cons('ਰ')),
    ('l', _Cons('ਲ')),
    ('v', _Cons('ਵ')),
    ('ṛ', _Cons('ੜ')),
]


@dataclass(frozen=True)
class _Vowel:
    matra: str        # matra form ('' = inherent -a, no sign)
    independent: str   # independent letter form


# Vowel tokens, longest first ('ā' before 'a', 'ai'/'au' before 'a').
_VOWELS: list[tuple[str, _Vowel]] = [
    ('ā', _Vowel('ਾ', 'ਆ')),
    ('ī', _Vowel('ੀ', 'ਈ')),
    ('ū', _Vowel('ੂ', 'ਊ')),
    ('ai', _Vowel('ੈ', 'ਐ')),
    ('au', _Vowel('ੌ', 'ਔ')),
    ('a', _Vowel('', 'ਅ')),          # inherent vowel
    ('i', _Vowel('ਿ', 'ਇ')),
    ('ī', _Vowel('ੀ', 'ਈ')),
    ('u', _Vowel('ੁ', 'ਉ')),
    ('e', _Vowel('ੇ', 'ਏ')),
    ('o', _Vowel('ੋ', 'ਓ')),
    ('ü', _Vowel('ੁ', 'ਉ')),          # §2 metrical double-pointing, groups with -u
]

_NASALIZATION = 'ṁ'


# ---------------------------------------------------------------------------
# Result types
# ---------------------------------------------------------------------------

@dataclass
class Ambiguity:
    """A point where the reverse mapping is not one-to-one.

    ``chosen`` is what the primary output used; ``alternatives`` are other
    valid Gurmukhi spellings a corpus-matcher could try instead.
    """
    kind: str                 # 'nasalization' | 'aspirate_sonorant' | ...
    source: str               # the romanized fragment that was ambiguous
    chosen: str               # Gurmukhi fragment used in the primary output
    alternatives: list[str]   # other valid Gurmukhi fragments
    note: str = ''


@dataclass
class ReverseResult:
    gurmukhi: str                       # primary best-guess Gurmukhi
    ambiguities: list[Ambiguity] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Tokenizer
# ---------------------------------------------------------------------------

@dataclass
class _Tok:
    kind: str          # 'C' | 'V' | 'N' | '?'
    roman: str
    cons: _Cons | None = None
    vowel: _Vowel | None = None


def _tokenize(text: str) -> list[_Tok]:
    """Greedy longest-match tokenizer over Shackle graphemes."""
    toks: list[_Tok] = []
    i = 0
    n = len(text)
    while i < n:
        # spaces and punctuation pass through as literal '?' tokens
        ch = text[i]
        if ch.isspace() or ch in ".,;:!?|'\"()[]-":
            toks.append(_Tok('?', ch))
            i += 1
            continue

        matched = False
        # consonants (longest first)
        for rom, cons in _CONSONANTS:
            if text.startswith(rom, i):
                toks.append(_Tok('C', rom, cons=cons))
                i += len(rom)
                matched = True
                break
        if matched:
            continue
        # vowels (longest first)
        for rom, vowel in _VOWELS:
            if text.startswith(rom, i):
                toks.append(_Tok('V', rom, vowel=vowel))
                i += len(rom)
                matched = True
                break
        if matched:
            continue
        # nasalization sign
        if text.startswith(_NASALIZATION, i):
            toks.append(_Tok('N', _NASALIZATION))
            i += len(_NASALIZATION)
            continue
        # unknown character — pass through
        toks.append(_Tok('?', ch))
        i += 1
    return toks


# ---------------------------------------------------------------------------
# Reverse engine
# ---------------------------------------------------------------------------

def reverse_transliterate(roman: str) -> ReverseResult:
    """Convert a Shackle-romanized string to Gurmukhi.

    Returns a :class:`ReverseResult` with the primary Gurmukhi spelling and a
    list of :class:`Ambiguity` points (each with alternative spellings) for the
    cases Shackle's rules leave genuinely underdetermined.
    """
    roman = unicodedata.normalize('NFC', roman)
    toks = _tokenize(roman)
    out: list[str] = []
    ambiguities: list[Ambiguity] = []

    # State: index of the last emitted base consonant in `out` that is still
    # "awaiting" its vowel (so a following vowel becomes a matra). -1 = none.
    awaiting_cons = False
    prev_cons_base: str | None = None  # for gemination detection

    def next_nonspace(idx: int) -> _Tok | None:
        j = idx + 1
        while j < len(toks):
            if toks[j].kind != '?':
                return toks[j]
            j += 1
        return None

    i = 0
    while i < len(toks):
        tok = toks[i]

        if tok.kind == '?':
            out.append(tok.roman)
            awaiting_cons = False
            prev_cons_base = None
            i += 1
            continue

        if tok.kind == 'N':
            # Nasalization: ṭippī (primary) or bindī (alternative)
            out.append(_TIPPI)
            ambiguities.append(Ambiguity(
                kind='nasalization',
                source='ṁ',
                chosen=_TIPPI,
                alternatives=[_BINDI],
                note='§6: ṁ may be written with ṭippī ੰ or bindī ਂ',
            ))
            awaiting_cons = False
            prev_cons_base = None
            i += 1
            continue

        if tok.kind == 'V':
            v = tok.vowel
            assert v is not None
            if awaiting_cons:
                # vowel sits on the preceding consonant → matra ('' for -a)
                if v.matra:
                    out.append(v.matra)
            else:
                # word-initial or post-vowel hiatus → independent letter
                out.append(v.independent)
            awaiting_cons = False
            prev_cons_base = None
            i += 1
            continue

        # tok.kind == 'C'
        c = tok.cons
        assert c is not None
        nxt = next_nonspace(i)
        nxt_is_cons = nxt is not None and nxt.kind == 'C'

        # 1. Gemination: identical consonant, no vowel between → collapses (§4).
        #    The already-emitted base keeps awaiting the upcoming vowel.
        if (awaiting_cons and prev_cons_base is not None
                and c.base == prev_cons_base and not c.aspirate_sonorant):
            base_g = c.base
            ambiguities.append(Ambiguity(
                kind='gemination',
                source=tok.roman + tok.roman,
                chosen=base_g,
                alternatives=[base_g[0] + _ADDAK + base_g[0]
                              if len(base_g) == 1 else base_g],
                note='§4: doubling unmarked in old Gurmukhi; '
                     'modern spelling may use addak ੱ',
            ))
            # do not emit a second letter; stay awaiting the vowel
            i += 1
            continue

        # 2. Homorganic nasal group: nasal + consonant, no vowel → ੰ (§5).
        if c.is_nasal and nxt_is_cons:
            out.append(_TIPPI)
            awaiting_cons = False
            prev_cons_base = None
            i += 1
            continue

        # 3. Emit the base consonant.
        out.append(c.base)
        if c.aspirate_sonorant:
            out.append(_SUBJOINED_HA)  # base + ੍ਹ (§3b)
            ambiguities.append(Ambiguity(
                kind='aspirate_sonorant',
                source=tok.roman,
                chosen=c.base + _SUBJOINED_HA,
                alternatives=[c.base + 'ਹ', c.base],
                note='§3b: subjoined ੍ਹ is often omitted in print',
            ))
        elif c.persian_collision:
            ambiguities.append(Ambiguity(
                kind='persian_collision',
                source=tok.roman,
                chosen=c.base,
                alternatives=['ਖ਼'],
                note='§8: a degraded (underline-dropped) k͟h could be ਖ਼',
            ))

        # 4. Conjunct: this consonant is immediately followed by another
        #    consonant (no vowel) and it is not a nasal group or gemination →
        #    subjoin the following consonant via virama (§3a). An *identical*
        #    following consonant is gemination (§4), not a conjunct, so leave it
        #    awaiting its vowel and let the next iteration collapse it.
        gemination_ahead = nxt_is_cons and nxt.cons.base == c.base  # type: ignore[union-attr]
        if nxt_is_cons and not c.aspirate_sonorant and not gemination_ahead:
            out.append(_VIRAMA)
            awaiting_cons = False
            prev_cons_base = None
        else:
            awaiting_cons = True
            prev_cons_base = c.base
        i += 1

    return ReverseResult(gurmukhi=''.join(out), ambiguities=ambiguities)


def shackle_to_gurmukhi(roman: str) -> str:
    """Convenience wrapper returning only the primary Gurmukhi string."""
    return reverse_transliterate(roman).gurmukhi
