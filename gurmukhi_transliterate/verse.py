"""
Match a romanized, GurbaniAkhar or noisy Gurmukhi line to its canonical verse.

    from gurmukhi_transliterate import match_verse, to_gurmukhi
    match_verse('kiv sachiaaraa hoieeaai kiv kooRai tuTai paal')[0].gurmukhi
    # 'ਕਿਵ ਸਚਿਆਰਾ ਹੋਈਐ ਕਿਵ ਕੂੜੈ ਤੁਟੈ ਪਾਲਿ ॥'
    to_gurmukhi('mera phone kharab ho gaya')   # raises UnableToReverse

How it works: every line — the query and each of the ~141k canonical lines
bundled from Shabad OS (data/lines.tsv.gz) — is reduced to a *skeleton* of
consonant classes. Classes merge what romanization schemes write ambiguously
(ਤ ਥ ਟ ਠ → t, ਸ ਸ਼ → s, ਨ ਣ ਙ ਞ and tippi/bindi → n, …); vowels and doubling
are dropped. Candidates come from an index of each word's first-letter class
(trigrams), and are scored by edit distance of the query skeleton against the
best-matching part of the candidate's skeleton, so partial lines match too.
Below MIN_SCORE, or with fewer than MIN_WORDS words, it abstains.
"""

from __future__ import annotations

import gzip
import math
import re
import unicodedata
from array import array
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from functools import lru_cache
from importlib.resources import files

from .legacy import GurmukhiLegacy

MIN_WORDS = 3
MIN_SCORE = 0.75
_CANDIDATES = 60          # candidates scored per query
_RARE_GRAMS = 8           # rarest first-letter trigrams used for retrieval
_COMMON_WORD = 20000      # skip word postings longer than this
_COVERAGE_PENALTY = 0.3

# --- Gurmukhi → class -------------------------------------------------------

_G_CLASS: dict[str, str] = {}
for _chars, _cls in [
    ('ਕਖ', 'k'), ('ਗਘ', 'g'), ('ਙਞਣਨ', 'n'), ('ਚਛ', 'c'), ('ਜਝ', 'j'),
    ('ਟਠਤਥ', 't'), ('ਡਢਦਧ', 'd'), ('ਪਫ', 'p'), ('ਬਭ', 'b'), ('ਮ', 'm'),
    ('ਯ', 'y'), ('ਰੜ', 'r'), ('ਲ', 'l'), ('ਵ', 'v'), ('ਸ', 's'), ('ਹ', 'h'),
    ('ੰਂ', 'n'),
]:
    for _ch in _chars:
        _G_CLASS[_ch] = _cls
_G_VOWEL_START = frozenset('ਅਆਇਈਉਊਏਐਓਔੳੲ')

# --- Roman (any scheme, incl. IPA) → class ------------------------------------

_R_GRAPHEMES: list[tuple[str, str]] = sorted([
    ('chh', 'c'), ('ch', 'c'), ('kh', 'k'), ('gh', 'g'), ('jh', 'j'), ('th', 't'),
    ('dh', 'd'), ('ph', 'p'), ('bh', 'b'), ('sh', 's'), ('dʒ', 'j'), ('tʃ', 'c'),
    ('k', 'k'), ('q', 'k'), ('x', 'k'), ('g', 'g'), ('c', 'c'), ('j', 'j'),
    ('z', 'j'), ('t', 't'), ('d', 'd'), ('n', 'n'), ('p', 'p'), ('f', 'p'),
    ('b', 'b'), ('m', 'm'), ('y', 'y'), ('r', 'r'), ('l', 'l'), ('v', 'v'),
    ('w', 'v'), ('s', 's'), ('h', 'h'),
    # IPA
    ('ʈ', 't'), ('ɖ', 'd'), ('ɳ', 'n'), ('ŋ', 'n'), ('ɲ', 'n'), ('ɽ', 'r'),
    ('ɾ', 'r'), ('ɹ', 'r'), ('ʋ', 'v'), ('ɦ', 'h'), ('ʃ', 's'), ('ɡ', 'g'),
    ('ɣ', 'g'), ('χ', 'k'), ('ɓ', 'b'), ('ʄ', 'j'), ('ɗ', 'd'), ('ʐ', 'j'),
], key=lambda p: -len(p[0]))
_R_VOWELS = frozenset('aeiouɪəɑʊɛæɔɐ')
_R_DROP = re.compile(r"[|.,;:!?'\"()\[\]ʰ˥]+")
# BaniDB spells the number after mahalaa/ghar as an ordinal (ਮਹਲਾ ੫ → mahalaa panjavaa)
_ORDINALS = ['pehilaa', 'doojaa', 'teejaa', 'chauthhaa', 'panjavaa', 'chhayvaa', 'satvaa',
             'atthvaa', 'nauvaa', 'dasvaa', 'gayaarvaa', 'baarvaa', 'tayrvaa', 'chaudavaa',
             'pandaravaa', 'solavaa', 'sataaravaa']
_ORDINAL_RE = re.compile(r'\b(mahalaa|mahalu|ghar|gharu)\s+(' + '|'.join(_ORDINALS) + r')\b')


@dataclass(frozen=True)
class Location:
    id: str
    source: str
    shabad: str
    page: int | None
    line: int | None


@dataclass(frozen=True)
class VerseMatch:
    """A canonical line and every place it occurs (repeated lines share one match)."""
    gurmukhi: str
    score: float
    locations: tuple[Location, ...] = field(default=())

    @property
    def id(self) -> str:
        return self.locations[0].id

    @property
    def source(self) -> str:
        return self.locations[0].source

    @property
    def page(self) -> int | None:
        return self.locations[0].page


class UnableToReverse(ValueError):
    """Raised when input can't be confidently mapped back to Gurmukhi."""


# ---------------------------------------------------------------------------
# Skeletons
# ---------------------------------------------------------------------------

_REPEATS = re.compile(r'(.)\1+')
_WORD_REPEATS = re.compile(r'([a-z])\1+')
_NON_ASCII = re.compile(r'[^\x00-\x7f]+')
_G_TABLE = str.maketrans(_G_CLASS)
_G_CLEAN = str.maketrans({**{ch: None for ch in ';,.'}, '।': ' ', '॥': ' ', '-': ' ',
                          **{g: a for g, a in zip('੦੧੨੩੪੫੬੭੮੯', '0123456789')}})
_DIGIT_RUN = re.compile(r'(\d+)')


def _collapse(s: str) -> str:
    return _REPEATS.sub(r'\1', s)


def _g_parts(text: str) -> tuple[str, list[str]]:
    """(first-letter classes, word skeletons) of a Gurmukhi line.

    One pass per line (the corpus has ~141k). Numbers (verse counts, ਮਹਲਾ ੫)
    have no first letter but keep their digits as a skeleton word, so ੨੧ and
    ੨੨ tell repeated lines apart. Words with no consonants drop out.
    """
    # ੴ is read ik oankaar; ਮਃ abbreviates ਮਹਲਾ (BaniDB writes both as mahalaa)
    text = unicodedata.normalize('NFC', text).replace('ੴ', 'ਇਕ ਓਅੰਕਾਰ').replace('ਮਃ', 'ਮਹਲਾ')
    words = _DIGIT_RUN.sub(r' \1 ', text.translate(_G_CLEAN)).split()
    first = ''.join('' if w.isdigit() else
                    'V' if w[0] in _G_VOWEL_START else _G_CLASS.get(w[0], 'V') for w in words)
    skels = _WORD_REPEATS.sub(r'\1', _NON_ASCII.sub('', ' '.join(words).translate(_G_TABLE))).split()
    return first, skels


def _r_word(word: str) -> tuple[str, str]:
    if word.isdigit():
        return '', word
    out = []
    i = 0
    while i < len(word):
        for g, cls in _R_GRAPHEMES:
            if word.startswith(g, i):
                out.append(cls)
                i += len(g)
                break
        else:
            i += 1  # vowel or unknown symbol
    skel = _collapse(''.join(out))
    first = 'V' if (word[0] in _R_VOWELS or not out) else out[0]
    return first, skel


def _r_words(text: str) -> list[str]:
    text = unicodedata.normalize('NFD', text)
    text = ''.join(ch for ch in text if not unicodedata.combining(ch)).lower()
    text = _ORDINAL_RE.sub(lambda m: f'{m.group(1)} {_ORDINALS.index(m.group(2)) + 1}', text)
    text = _R_DROP.sub(' ', text.replace('(n)', 'n'))
    text = re.sub(r'(\d+)', r' \1 ', text)
    return [w for w in re.split(r'[\s\-]+', text) if w]


def _query(text: str) -> tuple[str, list[str], str] | None:
    """(first-letter classes, word skeletons, line skeleton) of the query."""
    encoding = GurmukhiLegacy.detect_encoding(text)
    if encoding == 'anmollipi':
        text, encoding = GurmukhiLegacy.convert(text).text, 'unicode'
    if encoding == 'unicode':
        first, skels = _g_parts(text)
    elif encoding == 'latin':
        parts = [_r_word(w) for w in _r_words(text)]
        first, skels = ''.join(p[0] for p in parts), [p[1] for p in parts if p[1]]
    else:
        return None
    if not skels:
        return None
    return first, skels, ''.join(skels)


# ---------------------------------------------------------------------------
# Corpus and index
# ---------------------------------------------------------------------------

class _Corpus:
    def __init__(self) -> None:
        data = files('gurmukhi_transliterate').joinpath('data/lines.tsv.gz').read_bytes()
        rows = gzip.decompress(data).decode('utf-8').splitlines()[1:]
        self.text: list[str] = []
        self.loc: list[Location] = []
        self.skel: list[str] = []
        self.nwords: list[int] = []
        firsts: dict[str, array] = defaultdict(lambda: array('I'))
        words: dict[str, array] = defaultdict(lambda: array('I'))
        self.exact: dict[str, list[int]] = defaultdict(list)
        self.same: dict[str, list[int]] = defaultdict(list)   # identical lines
        for i, row in enumerate(rows):
            line_id, source, shabad, page, line, text = row.split('\t')
            self.text.append(text)
            self.loc.append(Location(line_id, source, shabad,
                                     int(page) if page else None, int(line) if line else None))
            first, skels = _g_parts(text)
            skel = ''.join(skels)
            self.skel.append(skel)
            self.nwords.append(len(first))
            self.exact[skel].append(i)
            self.same[text].append(i)
            for gram in {first[k:k + 3] for k in range(max(1, len(first) - 2))}:
                firsts[gram].append(i)
            for w in {w for w in skels if not w.isdigit()}:
                words[w].append(i)
        self.firsts = dict(firsts)
        self.words = dict(words)


@lru_cache(maxsize=1)
def _corpus() -> _Corpus:
    return _Corpus()


def _global(q: str, c: str) -> int:
    """Plain edit distance."""
    prev = list(range(len(c) + 1))
    for i, cq in enumerate(q, 1):
        cur = [i]
        for j, cc in enumerate(c, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (cq != cc)))
        prev = cur
    return prev[-1]


def _anchored(q: str, c: str) -> int:
    """Edit distance of all of *q* against the start or the end of *c*.

    A partial line (a half-line on a slide) is a prefix or suffix of the
    canonical line; a fragment from its middle is not accepted.
    """
    def dp(free_start: bool) -> list[int]:
        prev = [0] * (len(c) + 1) if free_start else list(range(len(c) + 1))
        for i, cq in enumerate(q, 1):
            cur = [i]
            for j, cc in enumerate(c, 1):
                cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (cq != cc)))
            prev = cur
        return prev
    return min(min(dp(False)), dp(True)[-1])


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def match_verse(text: str, top_n: int = 3, min_score: float = MIN_SCORE) -> list[VerseMatch]:
    """Return up to *top_n* canonical lines matching *text*, best first.

    Accepts romanized text in any common scheme (BaniDB/STTM, Shabad OS, ISO,
    IAST, IPA, informal), Unicode Gurmukhi (including OCR-damaged), or
    GurbaniAkhar ASCII. Returns [] when nothing scores at least *min_score*.

    Lines of MIN_WORDS words or more may match part of a canonical line (a
    half-line on a kirtan slide); shorter input (headings such as ਚੌਪਈ ॥)
    must match a whole line.
    """
    q = _query(text or '')
    if q is None or len(q[2]) < 2:
        return []
    first, wskels, skel = q
    corpus = _corpus()
    short = len(first) < MIN_WORDS
    n = len(corpus.text)

    # Candidates: rare query words count most (idf), first-letter trigrams
    # catch noisy words, and exact skeleton matches are always included.
    votes: Counter[int] = Counter()
    for w in set(wskels):
        postings = corpus.words.get(w)
        if postings and len(postings) < _COMMON_WORD:
            weight = math.log(n / len(postings))
            for i in postings:
                votes[i] += weight
    if not short:
        grams = {first[k:k + 3] for k in range(len(first) - 2)}
        for postings in sorted((corpus.firsts.get(g, array('I')) for g in grams), key=len)[:_RARE_GRAMS]:
            for i in postings:
                votes[i] += 0.5
    for i in corpus.exact.get(skel, ()):
        votes[i] += 1000

    scored: dict[str, float] = {}
    for i, _ in votes.most_common(_CANDIDATES):
        cand = corpus.skel[i]
        if short:
            if corpus.nwords[i] != len(first):
                continue  # a heading must match the whole line, word for word
            score = 1 - _global(skel, cand) / max(len(skel), len(cand))
        else:
            score = 1 - _anchored(skel, cand) / len(skel)
            # a query covering only a fragment of a long line is weak evidence
            score -= _COVERAGE_PENALTY * (1 - min(1.0, len(skel) / max(1, len(cand))))
        t = corpus.text[i]
        if score >= min_score and score > scored.get(t, -1):
            scored[t] = score
    # ties (e.g. ਸਲੋਕੁ ਮਃ ੩ vs ਸਲੋਕ ਮਹਲਾ ੩, identical in BaniDB romanization)
    # go to the line that occurs more often
    ranked = sorted(scored.items(), key=lambda kv: (-kv[1], -len(corpus.same[kv[0]])))[:top_n]
    return [VerseMatch(t, round(s, 4), tuple(corpus.loc[i] for i in corpus.same[t]))
            for t, s in ranked]


def to_gurmukhi(text: str) -> str:
    """Return Gurmukhi for each line of *text*.

    Each line is first matched to a canonical verse (match_verse); failing
    that, it is reversed word by word with a known romanization system
    (reverse_words). Raises UnableToReverse, naming the words that couldn't be
    reversed, rather than guessing.
    """
    from .system_reverse import reverse_words

    out = []
    for line in text.split('\n'):
        if not line.strip():
            out.append(line)
            continue
        matches = match_verse(line, top_n=1)
        if matches:
            out.append(matches[0].gurmukhi)
            continue
        words = reverse_words(line)
        if words.gurmukhi is None:
            raise UnableToReverse(
                f'unable to reverse transliterate {line!r}: no known spelling for '
                + ', '.join(repr(w) for w in words.missing))
        out.append(words.gurmukhi)
    return '\n'.join(out)
