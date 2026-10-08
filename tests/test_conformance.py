"""Conformance with each scheme's own code, or its own output.

tests/fixtures/conformance.tsv holds 1,200 corpus lines romanized by anvaad-js
(BaniDB) and gurmukhi-utils (Shabad OS); see tools/build_conformance.py.
tests/fixtures/igurbani.tsv holds 1,683 lines as igurbani.com serves them
(sttm_legacy); see tools/build_igurbani.py.
"""

import csv
import pathlib
import re

import pytest

from gurmukhi_transliterate import GurmukhiRomanizer

FIXTURE = pathlib.Path(__file__).parent / 'fixtures' / 'conformance.tsv'


def rows():
    with open(FIXTURE, encoding='utf-8', newline='') as f:
        return list(csv.DictReader(f, delimiter='\t', quoting=csv.QUOTE_NONE, escapechar='\\'))


@pytest.mark.parametrize('system, column', [('sttm', 'banidb'), ('banidb_ipa', 'banidb_ipa')])
def test_banidb_byte_for_byte(system, column):
    r = GurmukhiRomanizer(system)
    mismatches = [(x['gurmukhi'], x[column], r.romanize(x['gurmukhi']))
                  for x in rows() if r.romanize(x['gurmukhi']) != x[column]]
    assert len(rows()) >= 1000
    assert mismatches == [], mismatches[:3]


def test_shabados_clean_room_close_match():
    """Shabad OS is reimplemented from its outputs alone, so it is close, not
    exact: 96.9% of held-out lines and 99.5% of words when written."""
    r = GurmukhiRomanizer('shabados')
    data = rows()
    lines = words = word_hits = 0
    for x in data:
        got, want = r.romanize(x['gurmukhi']), x['shabados']
        lines += got == want
        g, w = got.split(), want.split()
        if len(g) == len(w):
            words += len(w)
            word_hits += sum(a == b for a, b in zip(g, w))
    assert lines / len(data) >= 0.96
    assert word_hits / words >= 0.99


def igurbani_words():
    path = FIXTURE.parent / 'igurbani.tsv'
    with open(path, encoding='utf-8', newline='') as f:
        data = list(csv.DictReader(f, delimiter='\t', quoting=csv.QUOTE_NONE, escapechar='\\'))
    assert len(data) >= 1500
    pairs = []
    for x in data:
        g, w = re.sub('[;,.]', '', x['gurmukhi']).split(), x['igurbani'].split()
        if len(g) == len(w):
            pairs += zip(g, w)
    return pairs


IGURBANI_SPELLINGS = {
    ('ਤਿਨਾ', 'thinhaa'), ('ਕੀਨੋ', 'keenho'),      # ੍ਹ in the transliteration only
    ('ਬਾਂਚੇ', 'baachae'), ('ਊਂਚੌ', 'oonacha'),    # nasal dropped or vowel added
}


def test_sttm_legacy_letters_match_igurbani():
    """The letter table, on words iGurbani's spelling rules can't touch.

    iGurbani drops final ਿ/ੁ, softens the vowel before ਹ, writes ਉ/ਇ after a
    letter as o/e and keeps medial schwas; sttm_legacy doesn't model those
    yet, so this checks only words ending in a long vowel with no ਹ, no
    non-initial ਉ/ਇ and no ੍ਰਿ. The misses allowed are spellings in
    iGurbani's database that its own Unicode text doesn't carry.
    """
    r = GurmukhiRomanizer('sttm_legacy')
    words = [(g, w) for g, w in igurbani_words()
             if g[-1] in 'ਾੀੂੇੈੋੌ' and 'ਹ' not in g and not re.search('.[ਉਇ]|੍ਰਿ|[੦-੯]', g)]
    misses = [(g, w, r.romanize(g)) for g, w in words if r.romanize(g) != w]
    assert len(words) >= 2000
    assert {(g, w) for g, w, _ in misses} <= IGURBANI_SPELLINGS, misses
