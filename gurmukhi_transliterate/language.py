"""
Character-trigram models for Latin-script text: is it English or romanized
Gurmukhi, and which romanization system wrote it?

    from gurmukhi_transliterate.language import detect_latin
    detect_latin('The English translation of the text').label     # 'english'
    detect_latin('kiv sachiaaraa hoieeaai kiv kooRai tuTai').label  # 'romanized'

One model per romanization system (trained on that system's romanization of
the bundled Gurbani lexicon) and one for English (SCOWL); see
data/README.md and tools/build_models.py. Each word is scored under every
model; a word's evidence is the best system's log-likelihood minus English's.
Sikh names and terms that appear in English prose too (Guru, Nanak, Singh,
Amritsar, …) are neutral and don't vote.
"""

from __future__ import annotations

import gzip
import math
import re
from collections import defaultdict
from dataclasses import dataclass, field
from functools import lru_cache
from importlib.resources import files

ORDER = 3
PAD = '^' * (ORDER - 1)

# Latin words: letters (incl. diacritics and IPA), BaniDB's (n), apostrophes
_WORD = re.compile(r"(?:\(n\)|[A-Za-zÀ-ɏɐ-˿ᴀ-ᶿḀ-ỿⁿₐ-ₜ'̀-ͯ])+")
# per-word evidence (nats per character) needed before a word counts as decided
_WORD_MARGIN = 0.15
# line decision: mean per-character evidence of decided words must clear this
_LINE_MARGIN = 0.25


def grams(word: str):
    """All n-grams (orders 1..ORDER) of a padded word, as counted for training."""
    s = PAD + word + '$'
    for i in range(ORDER - 1, len(s)):
        for k in range(1, ORDER + 1):
            yield s[i - k + 1:i + 1]


class _LM:
    __slots__ = ('counts', 'ctx', 'floor')

    def __init__(self, counts: dict[str, int]) -> None:
        self.counts = counts
        ctx: dict[str, int] = defaultdict(int)
        for g, n in counts.items():
            ctx[g[:-1]] += n
        self.ctx = dict(ctx)
        vocab = sum(1 for g in counts if len(g) == 1) + 1
        self.floor = 1 / (vocab * 50)

    def logp(self, word: str) -> float:
        """Interpolated trigram log-probability of *word* (higher orders weigh more)."""
        s = PAD + word + '$'
        lp = 0.0
        for i in range(ORDER - 1, len(s)):
            p = self.floor
            for k in range(1, ORDER + 1):
                g = s[i - k + 1:i + 1]
                c = self.ctx.get(g[:-1], 0)
                if c:
                    p = 0.4 * p + 0.6 * self.counts.get(g, 0) / c
            lp += math.log(p)
        return lp


@lru_cache(maxsize=1)
def models() -> dict[str, _LM]:
    data = files('gurmukhi_transliterate').joinpath('data/ngrams.tsv.gz').read_bytes()
    raw: dict[str, dict[str, int]] = defaultdict(dict)
    for line in gzip.decompress(data).decode('utf-8').splitlines()[1:]:
        name, g, n = line.split('\t')
        raw[name][g] = int(n)
    return {name: _LM(c) for name, c in raw.items()}


@lru_cache(maxsize=1)
def _neutral() -> frozenset[str]:
    """Lowercased words of the informal-terms table: names that English uses too."""
    from .informal import TERMS
    return frozenset(w.lower() for spellings in TERMS.values() for s in spellings
                     for w in re.findall(r'[A-Za-z]+', s))


def latin_words(text: str) -> list[str]:
    return _WORD.findall(text)


def word_scores(word: str) -> dict[str, float]:
    """Log-likelihood of *word* under each model. English is scored lowercase.
    Systems are case-sensitive (BaniDB's kooRai, tuTai) but Title Case and
    ALL CAPS words are also tried lowercase: that is sentence case, not
    a retroflex."""
    out = {}
    lower = word.lower()
    fold = lower != word and (word.istitle() or word.isupper())
    for name, lm in models().items():
        if name == 'english':
            out[name] = lm.logp(lower)
        else:
            out[name] = max(lm.logp(word), lm.logp(lower)) if fold else lm.logp(word)
    return out


@dataclass(frozen=True)
class LatinWord:
    word: str
    label: str      # 'romanized' | 'english' | 'name' | 'unclear'
    evidence: float  # nats per character, + = romanized, - = English


@dataclass(frozen=True)
class LatinGuess:
    label: str       # 'romanized' | 'english' | 'unknown'
    score: float     # confidence in label, 0..1
    words: tuple[LatinWord, ...] = field(default=())


def detect_latin(text: str) -> LatinGuess:
    """Is Latin-script *text* English or romanized Gurmukhi (any system)?

    Each word's evidence is smoothed with its neighbours' (a word in a
    romanized line is likely romanized). Returns 'unknown' when no word is
    decisive, e.g. a heading made only of names ("Guru Gobind Singh").
    """
    ws = latin_words(text)
    raw: list[float | None] = []
    for w in ws:
        if w.lower() in _neutral():
            raw.append(None)
            continue
        sc = word_scores(w)
        eng = sc.pop('english')
        raw.append((max(sc.values()) - eng) / (len(w) + 1))
    smoothed: list[float | None] = []
    for i, e in enumerate(raw):
        if e is None:
            smoothed.append(None)
            continue
        near = [x for x in raw[max(0, i - 1):i + 2] if x is not None]
        smoothed.append(0.5 * e + 0.5 * sum(near) / len(near))
    words = tuple(
        LatinWord(w, 'name' if e is None else 'romanized' if e > _WORD_MARGIN
                  else 'english' if e < -_WORD_MARGIN else 'unclear', 0.0 if e is None else round(e, 3))
        for w, e in zip(ws, smoothed))
    decided = [e for e in smoothed if e is not None]
    if not decided:
        return LatinGuess('unknown', 0.0, words)
    mean = sum(decided) / len(decided)
    if abs(mean) < _LINE_MARGIN:
        return LatinGuess('unknown', 0.0, words)
    confidence = 1 / (1 + math.exp(-abs(mean) * 4 * min(len(decided), 5)))
    return LatinGuess('romanized' if mean > 0 else 'english', round(confidence, 3), words)
