"""
Reverse transliteration for text that follows a known romanization system.

    from gurmukhi_transliterate import reverse_words
    reverse_words('naanak', system='sttm').gurmukhi        # 'ਨਾਨਕ'
    r = reverse_words('satigur prasaad')                   # system picked automatically
    r.system, r.gurmukhi, r.words[0].candidates

How it works: for each system, every word of the bundled Gurbani lexicon is
romanized forward (with and without schwa deletion) and the results are
inverted into an index, romanization → Gurmukhi words ranked by frequency.
Lookup is therefore exact for lexicon words and follows every forward rule
(nasals, addak, subjoined forms, fallbacks) automatically. Words outside the
lexicon are reported in ``missing``; nothing is guessed.

An index is built on first use of its system (about a second). Without
``system=``, systems are tried in an order suggested by the input's
characters until one explains every word.
"""

from __future__ import annotations

import re
import unicodedata
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from functools import lru_cache

from .iso15919 import GurmukhiISO15919
from .lexicon import load_lexicon
from .practical import GurmukhiPractical
from .romanizer import _DEDICATED, GurmukhiRomanizer
from .systems import SYSTEM_ORDER

ALL_SYSTEMS = ('iso15919', 'practical', *SYSTEM_ORDER)

# Which systems to try, in order, given the characters in the input.
_IPA_CHARS = set('ɪəɑʊɛæɔŋɲɳɽɾɹʋɦʃʈɖʒ')
_FAMILIES = {
    'ipa': ('banidb_ipa', 'ipa'),
    'diacritics': ('iso15919', 'iast', 'shackle', 'sacred_nitnem', 'dr_sant_singh', 'gursevak'),
    'banidb': ('sttm', 'sttm_legacy', 'practical'),
    'ascii': ('sttm', 'practical', 'dr_thind', 'dr_sant_singh', 'sttm_legacy', 'gfs', 'gursevak'),
}

# words may contain BaniDB's parenthesised nasal, a(n)mrit; other brackets are punctuation
_TOKEN = re.compile(r'\s+|\|\||\||\d+|(?:\(n\)|[^\s|\d.,;:!?()\[\]"])+|[.,;:!?()\[\]"]')
_DIGITS = str.maketrans('0123456789', '੦੧੨੩੪੫੬੭੮੯')
_IK_OANKAAR = '\x00'  # placeholder for ੴ while tokenizing


@dataclass(frozen=True)
class WordCandidates:
    roman: str
    candidates: tuple[tuple[str, int], ...] = ()   # (Gurmukhi, count), best first

    @property
    def best(self) -> str | None:
        return self.candidates[0][0] if self.candidates else None


@dataclass
class ReverseWords:
    system: str
    words: list[WordCandidates] = field(default_factory=list)
    gurmukhi: str | None = None      # None when any word is missing
    missing: list[str] = field(default_factory=list)

    @property
    def coverage(self) -> float:
        return 1 - len(self.missing) / len(self.words) if self.words else 0.0


def _forward(system: str, text: str, delete_schwa: bool) -> str:
    if system == 'iso15919':
        return GurmukhiISO15919.to_phonetic(text, delete_schwa=delete_schwa)
    if system == 'practical':
        return GurmukhiPractical.to_practical(text, delete_schwa=delete_schwa)
    return GurmukhiRomanizer(system).romanize_report(text, delete_schwa=delete_schwa).text


class _Index:
    def __init__(self, system: str) -> None:
        lexicon = load_lexicon()
        words = list(lexicon)
        exact: dict[str, Counter] = defaultdict(Counter)
        dedicated = system in _DEDICATED
        # Dedicated engines (BaniDB) ignore delete_schwa but depend on context:
        # a word mid-line ('naam') differs from the same word alone ('naamu').
        for delete_schwa in ((False,) if dedicated else (False, True)):
            # one call for the whole lexicon; output words align with input words
            out = _forward(system, ' '.join(words), delete_schwa).split(' ')
            if len(out) != len(words):  # pragma: no cover - defensive
                out = [_forward(system, w, delete_schwa) for w in words]
            for w, roman in zip(words, out):
                if roman:
                    exact[roman][w] = lexicon[w]
        if dedicated:
            for w in words:
                roman = _forward(system, w, False)
                if roman:
                    exact[roman][w] = lexicon[w]
        lower: dict[str, Counter] = defaultdict(Counter)
        for roman, c in exact.items():
            lower[roman.lower()].update(c)
        self.exact = {k: tuple(c.most_common()) for k, c in exact.items()}
        self.lower = {k: tuple(c.most_common()) for k, c in lower.items()}
        self.ik_oankaar = {_forward(system, 'ੴ', False).lower(), 'ikoankaar', 'ik oankaar'}

    def lookup(self, word: str) -> tuple[tuple[str, int], ...]:
        return (self.exact.get(word) or self.lower.get(word.lower())
                or self.lower.get(word.lower().replace("'", '')) or ())


@lru_cache(maxsize=None)
def _index(system: str) -> _Index:
    return _Index(system)


def _reverse_with(system: str, text: str) -> ReverseWords:
    index = _index(system)
    for phrase in sorted(index.ik_oankaar, key=len, reverse=True):
        text = re.sub(re.escape(phrase).replace(r'\ ', r'\s+'), _IK_OANKAAR, text, flags=re.I)
    result = ReverseWords(system)
    out: list[str] = []
    for tok in _TOKEN.findall(text):
        if tok.isspace():
            out.append(tok)
        elif tok == _IK_OANKAAR:
            out.append('ੴ')
        elif tok == '||':
            out.append('॥')
        elif tok == '|':
            out.append('।')
        elif tok.isdigit():
            out.append(tok.translate(_DIGITS))
        elif not any(ch.isalpha() for ch in tok):
            out.append(tok)
        else:
            wc = WordCandidates(tok, index.lookup(unicodedata.normalize('NFC', tok)))
            result.words.append(wc)
            if wc.best is None:
                result.missing.append(tok)
            else:
                out.append(wc.best)
    if not result.missing:
        result.gurmukhi = ''.join(out).strip()
    return result


def _candidate_systems(text: str) -> tuple[str, ...]:
    if any(ch in _IPA_CHARS for ch in text):
        return _FAMILIES['ipa']
    decomposed = unicodedata.normalize('NFD', text)
    if any(unicodedata.combining(ch) for ch in decomposed) or not text.isascii():
        return _FAMILIES['diacritics']
    if '(n)' in text or re.search(r'[a-z][TR]', text):
        return _FAMILIES['banidb']
    return _FAMILIES['ascii']


def reverse_words(text: str, system: str | None = None) -> ReverseWords:
    """Reverse romanized *text* word by word using a system's lexicon index.

    With *system* None, candidate systems (chosen from the input's characters)
    are tried in order until one explains every word; otherwise the one that
    explains the most words (ties: the higher total frequency) is returned.
    """
    if system is not None:
        if system not in ALL_SYSTEMS:
            raise ValueError(f'unknown system {system!r}; choose from {ALL_SYSTEMS}')
        return _reverse_with(system, text)
    best: ReverseWords | None = None
    best_key = (-1.0, -1)
    for s in _candidate_systems(text):
        r = _reverse_with(s, text)
        key = (r.coverage, sum(w.candidates[0][1] for w in r.words if w.candidates))
        if key > best_key:
            best, best_key = r, key
        if not r.missing and r.words:
            break
    assert best is not None
    return best
