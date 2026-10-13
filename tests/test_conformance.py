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


def igurbani_rows():
    path = FIXTURE.parent / 'igurbani.tsv'
    with open(path, encoding='utf-8', newline='') as f:
        data = list(csv.DictReader(f, delimiter='\t', quoting=csv.QUOTE_NONE, escapechar='\\'))
    assert len(data) >= 1500
    return data


@pytest.mark.parametrize('part, line_floor', [('held-out', 0.93), ('all', 0.93)])
def test_sttm_legacy_clean_room_close_match(part, line_floor):
    """iGurbani's scheme is reimplemented from igurbani.com's output alone.

    The rules were written looking only at shabads whose id is not a multiple
    of 3; the rest are held out, so their score is the honest one (94.6% of
    lines, 99.8% of words). What's left are spellings in iGurbani's database,
    e.g. ਤਿਨ੍ਹ੍ਹਾ written both thinhaa and thinaa.
    """
    r = GurmukhiRomanizer('sttm_legacy')
    data = [x for x in igurbani_rows() if part == 'all' or int(x['shabad']) % 3 == 0]
    lines = words = word_hits = 0
    for x in data:
        got, want = r.romanize(x['gurmukhi']), x['igurbani']
        lines += got == want
        g, w = got.split(), want.split()
        if len(g) == len(w):
            words += len(w)
            word_hits += sum(a == b for a, b in zip(g, w))
    assert len(data) >= 500
    assert lines / len(data) >= line_floor
    assert word_hits / words >= 0.99
