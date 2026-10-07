"""
Bundled Gurmukhi word-frequency list, derived from the Shabad OS database.

    from gurmukhi_transliterate.lexicon import load_lexicon
    counts = load_lexicon()                  # every source
    sggs = load_lexicon(['sggs'])            # Guru Granth Sahib only

Counts come from the primary (scripture) text only. Words are NFC-normalised,
so look up NFC strings. See data/README.md for provenance and licence; rebuild
with tools/build_lexicon.py.
"""

from __future__ import annotations

import gzip
import re
import unicodedata
from functools import lru_cache
from importlib.resources import files
from typing import Iterable, Iterator

SOURCES = ('sggs', 'dasam', 'bhai_gurdas', 'bhai_nand_lal', 'other')

_SPLIT = re.compile(r'[\s\-]+')
_STRIP = str.maketrans('', '', ';,.\u200c\u200d')  # vishraams, ZWNJ, ZWJ


def _is_word(token: str) -> bool:
    return bool(token) and all(
        '\u0a01' <= ch <= '\u0a75' and not '\u0a64' <= ch <= '\u0a6f' and ch != 'ੴ'
        for ch in token
    )


def words(text: str) -> Iterator[str]:
    """Yield the Gurmukhi words of *text* as the lexicon counts them: NFC,
    without vishraams, dandas, digits, ੴ or zero-width joiners; hyphenated
    compounds split."""
    text = unicodedata.normalize('NFC', text).translate(_STRIP)
    for tok in _SPLIT.split(text):
        if _is_word(tok):
            yield tok


@lru_cache(maxsize=None)
def _table() -> tuple[tuple[str, tuple[int, ...]], ...]:
    data = files('gurmukhi_transliterate').joinpath('data/lexicon.tsv.gz').read_bytes()
    lines = gzip.decompress(data).decode('utf-8').splitlines()
    header = lines[0].split('\t')
    assert tuple(header[2:]) == SOURCES, header
    rows = []
    for line in lines[1:]:
        word, _total, *per = line.split('\t')
        rows.append((word, tuple(int(n) for n in per)))
    return tuple(rows)


def load_lexicon(sources: Iterable[str] | None = None) -> dict[str, int]:
    """Return ``{word: count}`` summed over *sources* (default: all)."""
    wanted = SOURCES if sources is None else tuple(sources)
    unknown = set(wanted) - set(SOURCES)
    if unknown:
        raise ValueError(f'unknown source(s) {sorted(unknown)}; choose from {SOURCES}')
    idx = [SOURCES.index(s) for s in wanted]
    out: dict[str, int] = {}
    for word, per in _table():
        n = sum(per[i] for i in idx)
        if n:
            out[word] = n
    return out
