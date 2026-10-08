"""Conformance with each scheme's own code.

tests/fixtures/conformance.tsv holds 1,200 corpus lines romanized by anvaad-js
(BaniDB) and gurmukhi-utils (Shabad OS); see tools/build_conformance.py.
"""

import csv
import pathlib

import pytest

from gurmukhi_transliterate import GurmukhiRomanizer

pytestmark = pytest.mark.story('US-004')

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
