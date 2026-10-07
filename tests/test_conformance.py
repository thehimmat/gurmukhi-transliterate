"""Byte-for-byte conformance with each scheme's own code.

tests/fixtures/conformance.tsv holds 1,200 corpus lines romanized by anvaad-js
(BaniDB) and gurmukhi-utils (Shabad OS); see tools/build_conformance.py.
"""

import csv
import pathlib

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
