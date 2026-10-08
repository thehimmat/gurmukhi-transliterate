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
  - ``nasalization``      §6  ṁ → ਂ (bindī) after ā ī e ai o au, ੰ (ṭippī)
                              otherwise, as the corpus writes them; the other
                              sign and no sign are the alternatives
  - ``aspirate_sonorant`` §3b nh/mh/lh/rh/ṇh/ṛh → subjoined ੍ਹ (primary),
                              which print often omits (ਨਹ / bare)
  - ``gemination``        §4  doubling not marked in old Gurmukhi → collapses
                              (primary); modern addak ੱ offered as alternative
  - ``persian_collision`` §8  a degraded (underline-dropped) kh could be ਖ or ਖ਼

ü and ï after a are vowels of their own (ਸਉ saü, ਅਇ aï); ü straight after a
consonant is double pointing, ੋ + ੁ (ਸੋੁ sü). The Perso-Arabic signs of
p. xxv (used in etymologies) map to the Gurmukhi letter written for each:
s̲ ṡ → ਸ, s͟h → ਸ਼, h̲ → ਹ, k͟h → ਖ਼, g͟h → ਗ਼, z̲ ż ẓ → ਜ਼, t̲ → ਤ, and ʿ to the
vowel letter after it with a nukta (ʿarab → ਅ਼ਰਬ, ʿilm → ਇ਼ਲਮ). Silent و (ẉ)
and hamza (ʾ, or an apostrophe between letters) are dropped. Underlines may be
written with U+0332, U+0331 or, across a digraph, U+035F.
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
_NUKTA = '਼'
# Vowels the corpus nasalizes with bindī (≥97% of the time); everything else
# takes ṭippī.
_TAKES_BINDI = frozenset('ਾੀੇੈੋੌਆਈਉਊਏਐਓਔ')
_SUBJOINED_HA = '੍ਹ'

# Aspirate → its unaspirated counterpart (§4: a geminated aspirate is written
# unaspirate + aspirate, e.g. vaddhi = ਵਧਿ, ugghaṛi = ਉਘੜਿ). Reverse collapses
# such a pair to the single aspirate letter.
_UNASPIRATE_OF: dict[str, str] = {
    'ਖ': 'ਕ', 'ਘ': 'ਗ', 'ਛ': 'ਚ', 'ਝ': 'ਜ', 'ਠ': 'ਟ',
    'ਢ': 'ਡ', 'ਥ': 'ਤ', 'ਧ': 'ਦ', 'ਫ': 'ਪ', 'ਭ': 'ਬ',
}


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
    # Perso-Arabic signs of p. xxv, underlines normalised to U+0332
    ('k\u0332h\u0332', _Cons('ਖ਼')),
    ('g\u0332h\u0332', _Cons('ਗ਼')),
    ('s\u0332h\u0332', _Cons('ਸ਼')),
    ('k\u0332h', _Cons('ਖ਼')),
    ('g\u0332h', _Cons('ਗ਼')),
    ('s\u0332h', _Cons('ਸ਼')),
    ('s\u0332', _Cons('ਸ')),
    ('h\u0332', _Cons('ਹ')),
    ('z\u0332', _Cons('ਜ਼')),
    ('t\u0332', _Cons('ਤ')),
    ('ṡ', _Cons('ਸ')),
    ('ż', _Cons('ਜ਼')),
    ('ẓ', _Cons('ਜ਼')),
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
    ('ü', _Vowel('ੋੁ', 'ਉ')),         # p. xxi: double pointing on a consonant, hiatus after a
    ('ï', _Vowel('ਿ', 'ਇ')),          # §2 hiatus i (daïā = ਦਇਆ), groups with -i
]

# Homorganic class of each nasal (§5): a nasal heads a nasal group (→ ੰ) only
# before a stop of its own class; before anything else it is a plain
# consonant (m + r = ਮ੍ਰ).
_NASAL_CLASS: dict[str, frozenset[str]] = {
    'ਙ': frozenset('ਕਖਗਘਙ'),
    'ਞ': frozenset('ਚਛਜਝਞ'),
    'ਣ': frozenset('ਟਠਡਢਣ'),
    'ਨ': frozenset('ਤਥਦਧਨਸ'),         # p. xxiii: n before s too
    'ਮ': frozenset('ਪਫਬਭਮ'),
}

_NASALIZATION = 'ṁ'
_AIN = 'ʿ'
_SILENT = frozenset('ẉʾ')            # silent و and hamza (p. xxv)
_UNDERLINES = str.maketrans({'\u0331': '\u0332', '\u035f': '\u0332'})
_PRECOMPOSED_UNDERLINES = str.maketrans({
    'ṯ': 't\u0332', 'ẖ': 'h\u0332', 'ḵ': 'k\u0332', 'ẕ': 'z\u0332',
})


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
    start: int = 0            # offset of `chosen` within ReverseResult.gurmukhi
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
    kind: str          # 'C' | 'V' | 'N' | 'A' (ʿ) | '?'
    roman: str
    cons: _Cons | None = None
    vowel: _Vowel | None = None


def _tokenize(text: str) -> list[_Tok]:
    """Greedy longest-match tokenizer over Shackle graphemes."""
    toks: list[_Tok] = []
    i = 0
    n = len(text)
    while i < n:
        ch = text[i]
        # silent signs; an apostrophe between letters is hamza (p. xxv)
        if ch in _SILENT or (ch in "'’" and 0 < i < n - 1
                             and text[i - 1].isalpha() and text[i + 1].isalpha()):
            i += 1
            continue
        if text.startswith('w\u0324', i):
            i += 2
            continue
        if ch == _AIN:
            toks.append(_Tok('A', ch))
            i += 1
            continue
        # spaces and punctuation pass through as literal '?' tokens
        if ch.isspace() or ch in ".,;:!?|'\"()[]-":
            toks.append(_Tok('?', ch))
            i += 1
            continue

        matched = False
        # consonants (longest first)
        for rom, cons in _CONSONANTS:
            # an underline belongs to the letter it follows (nh̲ is n + h̲)
            if text.startswith(rom, i) and not text.startswith('\u0332', i + len(rom)):
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
    roman = roman.translate(_PRECOMPOSED_UNDERLINES).translate(_UNDERLINES)
    toks = _tokenize(roman)
    out: list[str] = []
    ambiguities: list[Ambiguity] = []

    # State: index of the last emitted base consonant in `out` that is still
    # "awaiting" its vowel (so a following vowel becomes a matra). -1 = none.
    awaiting_cons = False
    prev_cons_base: str | None = None  # for gemination detection
    prev_cons_offset = 0               # offset of prev base for gemination flag

    def pos() -> int:
        return sum(len(x) for x in out)

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

        if tok.kind == 'A':
            # ʿ: a nukta on the vowel letter that follows, else ਅ਼
            nxt = toks[i + 1] if i + 1 < len(toks) else None
            if nxt is not None and nxt.kind == 'V':
                out.append(nxt.vowel.independent + _NUKTA)  # type: ignore[union-attr]
                i += 1
            else:
                out.append('ਅ' + _NUKTA)
            awaiting_cons = False
            prev_cons_base = None
            i += 1
            continue

        if tok.kind == 'N':
            # Nasalization: the sign the corpus uses after this vowel, with
            # the other sign (and no sign) as alternatives
            sign, other = ((_BINDI, _TIPPI) if out and out[-1][-1:] in _TAKES_BINDI
                           else (_TIPPI, _BINDI))
            ambiguities.append(Ambiguity(
                kind='nasalization',
                source='ṁ',
                chosen=sign,
                alternatives=[other, ''],
                start=pos(),
                note='§6: ṁ may be written with ṭippī ੰ or bindī ਂ, and is '
                     'only sometimes marked in the script (often omitted)',
            ))
            out.append(sign)
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

        # 1. Gemination (§4), two shapes, both collapsing since Gurmukhi does
        #    not mark doubling:
        #      a) identical consonant (matti → ਮਤਿ): keep the emitted base.
        #      b) unaspirate + its aspirate (ugghaṛi → ਉਘੜਿ): a geminated
        #         aspirate; replace the emitted unaspirate with the aspirate.
        if awaiting_cons and prev_cons_base is not None and not c.aspirate_sonorant:
            is_identical = c.base == prev_cons_base
            is_aspirate_gem = _UNASPIRATE_OF.get(c.base) == prev_cons_base
            if is_identical or is_aspirate_gem:
                base_g = c.base
                if is_aspirate_gem:
                    # swap the single unaspirate already in `out` for the aspirate
                    if out and out[-1] == prev_cons_base:
                        out[-1] = c.base
                    else:
                        out.append(c.base)
                    prev_cons_base = c.base
                # Modern spelling marks the geminate with addak *before* the
                # base consonant (ਮਤਿ → ਮੱਤਿ), so the alternative replacing the
                # single base is ੱ + base.
                ambiguities.append(Ambiguity(
                    kind='gemination',
                    source=tok.roman,
                    chosen=base_g,
                    alternatives=[_ADDAK + base_g],
                    start=prev_cons_offset,
                    note='§4: doubling unmarked in old Gurmukhi; '
                         'modern spelling may use addak ੱ',
                ))
                # do not emit a second base; stay awaiting the vowel
                i += 1
                continue

        # 2. Homorganic nasal group: nasal + same-class consonant, no vowel → ੰ (§5).
        if (c.is_nasal and nxt_is_cons
                and nxt.cons.base in _NASAL_CLASS[c.base]):  # type: ignore[union-attr]
            # A geminate nasal (nn, mm, …) is written either ੰ+nasal (§5) or,
            # as the glossary often prints it, a single collapsed nasal (§4).
            # Flag the single-nasal alternative (drop the ੰ) for the matcher.
            if nxt.cons.base == c.base:  # type: ignore[union-attr]
                ambiguities.append(Ambiguity(
                    kind='gemination',
                    source=tok.roman + tok.roman,
                    chosen=_TIPPI,
                    alternatives=[''],
                    start=pos(),
                    note='§4/§5: geminate nasal may be ੰ+nasal or a single nasal',
                ))
            out.append(_TIPPI)
            awaiting_cons = False
            prev_cons_base = None
            i += 1
            continue

        # 3. Emit the base consonant.
        base_offset = pos()
        out.append(c.base)
        if c.aspirate_sonorant:
            out.append(_SUBJOINED_HA)  # base + ੍ਹ (§3b)
            ambiguities.append(Ambiguity(
                kind='aspirate_sonorant',
                source=tok.roman,
                chosen=c.base + _SUBJOINED_HA,
                alternatives=[c.base + 'ਹ', c.base],
                start=base_offset,
                note='§3b: subjoined ੍ਹ is often omitted in print',
            ))
        elif c.persian_collision:
            ambiguities.append(Ambiguity(
                kind='persian_collision',
                source=tok.roman,
                chosen=c.base,
                alternatives=['ਖ਼'],
                start=base_offset,
                note='§8: a degraded (underline-dropped) k͟h could be ਖ਼',
            ))

        # 4. Conjunct: this consonant is immediately followed by another
        #    consonant (no vowel) and it is not a nasal group or gemination →
        #    subjoin the following consonant via virama (§3a). An *identical*
        #    following consonant is gemination (§4), not a conjunct, so leave it
        #    awaiting its vowel and let the next iteration collapse it.
        gemination_ahead = nxt_is_cons and (
            nxt.cons.base == c.base                          # type: ignore[union-attr]
            or _UNASPIRATE_OF.get(nxt.cons.base) == c.base   # type: ignore[union-attr]
        )
        if nxt_is_cons and not c.aspirate_sonorant and not gemination_ahead:
            if c.is_nasal:
                # A nasal heading a conjunct is often written geminated with
                # ṭippī in Gurmukhi (amritu: ਅਮ੍ਰਿਤੁ or ਅੰਮ੍ਰਿਤੁ).
                ambiguities.append(Ambiguity(
                    kind='gemination',
                    source=tok.roman,
                    chosen=c.base,
                    alternatives=[_TIPPI + c.base],
                    start=base_offset,
                    note='§4/§5: a nasal before a conjunct may be written ੰ+nasal',
                ))
            out.append(_VIRAMA)
            awaiting_cons = False
            prev_cons_base = None
        else:
            awaiting_cons = True
            prev_cons_base = c.base
            prev_cons_offset = base_offset
        i += 1

    return ReverseResult(gurmukhi=''.join(out), ambiguities=ambiguities)


def shackle_to_gurmukhi(roman: str) -> str:
    """Convenience wrapper returning only the primary Gurmukhi string."""
    return reverse_transliterate(roman).gurmukhi
