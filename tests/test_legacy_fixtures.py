"""Differential tests on real lines: legacy-font input vs hand-checked Unicode.

Each ``<name>.gurbaniakhar.txt`` has a parallel ``<name>.unicode.txt``; lines
must convert 1:1. Japji text follows the SGGS (BaniDB) reading; the Ghazal
line is from Bhai Nand Lal's Diwan-e-Goya as given in issue #14.
"""

import pathlib
import pytest
from gurmukhi_transliterate import GurmukhiLegacy

pytestmark = pytest.mark.story('US-003')

FIXTURES = pathlib.Path(__file__).parent / 'fixtures' / 'legacy'
NAMES = sorted(p.name.split('.')[0] for p in FIXTURES.glob('*.gurbaniakhar.txt'))


def _load(name):
    legacy = (FIXTURES / f'{name}.gurbaniakhar.txt').read_text().split('\n')
    expected = (FIXTURES / f'{name}.unicode.txt').read_text().split('\n')
    return legacy, expected


@pytest.mark.parametrize('name', NAMES)
def test_line_count_preserved(name):
    legacy, _ = _load(name)
    source = '\n'.join(legacy)
    assert GurmukhiLegacy.to_unicode(source).count('\n') == source.count('\n')


@pytest.mark.parametrize('name', NAMES)
def test_lines_match(name):
    legacy, expected = _load(name)
    assert len(legacy) == len(expected)
    for n, (src, want) in enumerate(zip(legacy, expected), 1):
        if GurmukhiLegacy.detect_encoding(src) == 'latin':
            continue  # headings in English are routed elsewhere, not converted
        assert GurmukhiLegacy.to_unicode(src) == want, f'{name} line {n}: {src!r}'


@pytest.mark.parametrize('name', NAMES)
def test_no_warnings_on_clean_text(name):
    legacy, _ = _load(name)
    for src in legacy:
        if GurmukhiLegacy.detect_encoding(src) == 'anmollipi':
            assert GurmukhiLegacy.convert(src).warnings == []


def test_ghazal_heading_detected_as_latin():
    legacy, _ = _load('ghazal1')
    labels = [g.label for g in GurmukhiLegacy.detect_lines('\n'.join(legacy))]
    assert labels[:2] == ['latin', 'anmollipi']
