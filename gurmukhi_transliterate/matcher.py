"""
Corpus matcher: resolve Shackle reverse-transliteration ambiguities against a
real Gurmukhi lexicon.

:func:`reverse_transliterate` (see reverse.py) produces a *primary* Gurmukhi
spelling plus flagged :class:`Ambiguity` points where Shackle's rules leave the
spelling underdetermined (nasalization sign, subjoined ੍ਹ, gemination,
Perso-Arabic collision). This module enumerates the candidate spellings implied
by those flags and keeps the ones actually attested in a supplied lexicon,
ranked by corpus frequency — so an ambiguous reverse-transliterated word
resolves to the spelling that really occurs (e.g. in the SGGS word index).

The library stays corpus-agnostic: the caller injects the lexicon (a set of
words, or a ``word → frequency`` mapping). A loader that pulls the SGGS word
index out of the suite's Supabase ``words`` table lives outside this pure
module (see the corpus-matcher issue).

    from gurmukhi_transliterate.matcher import CorpusMatcher

    matcher = CorpusMatcher({'ਸਾਂ': 40, 'ਸਾੰ': 3})
    result = matcher.match('sāṁ')
    result.best          # → 'ਸਾਂ'  (most frequent attested candidate)
    result.matches       # → [Candidate('ਸਾਂ', 40, ...), Candidate('ਸਾੰ', 3, ...)]
"""

from __future__ import annotations

import unicodedata
from dataclasses import dataclass, field
from itertools import product
from pathlib import Path
from typing import Iterable, Mapping

from .reverse import ReverseResult, reverse_transliterate


# Safety cap: a word has at most a handful of ambiguities, each with 1-2
# alternatives, so the candidate set is tiny. Guard against pathological input.
_MAX_CANDIDATES = 256


def candidate_spellings(result: ReverseResult) -> list[str]:
    """All Gurmukhi spellings implied by a reverse result's ambiguity flags.

    The primary spelling is always first. Each ambiguity contributes its
    ``chosen`` fragment plus its ``alternatives`` at the recorded offset;
    substitutions are applied right-to-left so earlier offsets stay valid.
    """
    base = result.gurmukhi
    if not result.ambiguities:
        return [base]

    # Each ambiguity → list of (start, chosen_len, option) choices.
    # chosen is listed first so the primary combination comes out first.
    choice_sets: list[list[tuple[int, int, str]]] = []
    for a in result.ambiguities:
        opts = [a.chosen] + [alt for alt in a.alternatives if alt != a.chosen]
        choice_sets.append([(a.start, len(a.chosen), opt) for opt in opts])

    seen: set[str] = set()
    candidates: list[str] = []
    for combo in product(*choice_sets):
        # apply right-to-left so splicing does not shift later offsets
        word = base
        for start, chosen_len, option in sorted(combo, key=lambda c: c[0],
                                                reverse=True):
            word = word[:start] + option + word[start + chosen_len:]
        word = unicodedata.normalize('NFC', word)
        if word not in seen:
            seen.add(word)
            candidates.append(word)
        if len(candidates) >= _MAX_CANDIDATES:
            break
    return candidates


@dataclass
class Candidate:
    gurmukhi: str
    frequency: int          # corpus frequency (0 if not attested)
    in_corpus: bool
    is_primary: bool        # was this the reverse engine's primary spelling?


@dataclass
class MatchResult:
    roman: str
    reverse: ReverseResult
    candidates: list[Candidate]              # every enumerated spelling
    matches: list[Candidate] = field(default_factory=list)  # in-corpus, ranked

    @property
    def best(self) -> str:
        """The most frequent attested spelling, or the primary if none match."""
        if self.matches:
            return self.matches[0].gurmukhi
        return self.reverse.gurmukhi

    @property
    def resolved(self) -> bool:
        """True if at least one candidate is attested in the corpus."""
        return bool(self.matches)


class CorpusMatcher:
    """Resolve Shackle reverse-transliterations against an injected lexicon."""

    def __init__(self, lexicon: Mapping[str, int] | Iterable[str]) -> None:
        # Normalize to {NFC word: frequency}. A bare iterable → frequency 1.
        freq: dict[str, int] = {}
        if isinstance(lexicon, Mapping):
            for word, f in lexicon.items():
                freq[unicodedata.normalize('NFC', word)] = int(f)
        else:
            for word in lexicon:
                freq[unicodedata.normalize('NFC', word)] = 1
        self._freq = freq

    def __contains__(self, word: str) -> bool:
        return unicodedata.normalize('NFC', word) in self._freq

    def match(self, roman_or_result: str | ReverseResult) -> MatchResult:
        """Reverse-transliterate (if needed) and rank candidates by the corpus.

        Accepts either a Shackle-romanized string or a pre-computed
        :class:`ReverseResult`.
        """
        if isinstance(roman_or_result, ReverseResult):
            rev = roman_or_result
            roman = ''
        else:
            roman = roman_or_result
            rev = reverse_transliterate(roman)

        primary = rev.gurmukhi
        spellings = candidate_spellings(rev)

        candidates: list[Candidate] = []
        for sp in spellings:
            f = self._freq.get(sp, 0)
            candidates.append(Candidate(
                gurmukhi=sp,
                frequency=f,
                in_corpus=sp in self._freq,
                is_primary=(sp == primary),
            ))

        # Attested candidates, ranked by frequency desc, then primary-first,
        # then by shorter spelling as a mild tie-breaker.
        matches = sorted(
            (c for c in candidates if c.in_corpus),
            key=lambda c: (-c.frequency, not c.is_primary, len(c.gurmukhi)),
        )
        return MatchResult(
            roman=roman,
            reverse=rev,
            candidates=candidates,
            matches=matches,
        )

    @classmethod
    def from_file(cls, path: str | Path) -> "CorpusMatcher":
        """Build a matcher from a lexicon file.

        Accepts one word per line, optionally ``word<TAB>frequency`` (extra
        columns ignored). Blank lines and lines starting with ``#`` are
        skipped. This is the seam for the SGGS word index: export the kosh
        ``words`` table (gurmukhi, frequency) to such a file, or inject the
        list directly via the constructor.
        """
        return cls(load_lexicon(path))


def load_lexicon(path: str | Path) -> dict[str, int]:
    """Read a ``word[<TAB>frequency]`` lexicon file into a frequency map."""
    freq: dict[str, int] = {}
    for raw in Path(path).read_text(encoding='utf-8').splitlines():
        line = raw.strip()
        if not line or line.startswith('#'):
            continue
        parts = line.split('\t')
        word = unicodedata.normalize('NFC', parts[0].strip())
        if not word:
            continue
        try:
            freq[word] = int(parts[1]) if len(parts) > 1 else 1
        except ValueError:
            freq[word] = 1
    return freq
