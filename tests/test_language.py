"""Tests for detect_latin: English vs romanized Gurmukhi (#16 phase 5)."""

import csv
import pathlib

import pytest

from gurmukhi_transliterate import LatinGuess, LatinWord, detect_latin

GOLD = pathlib.Path(__file__).parent / 'fixtures' / 'gold'


def _lines(name):
    return [l.strip() for l in open(GOLD / name, encoding='utf-8') if l.strip()]


def _gold(scheme):
    with open(GOLD / 'lines.tsv', encoding='utf-8', newline='') as f:
        rows = csv.DictReader(f, delimiter='\t', quoting=csv.QUOTE_NONE, escapechar='\\')
        return [r[scheme] for r in rows]


class TestDetectLatin:
    def test_returns_guess(self):
        g = detect_latin('satinaam vaahiguroo')
        assert isinstance(g, LatinGuess)
        assert all(isinstance(w, LatinWord) for w in g.words)
        assert 0.0 <= g.score <= 1.0

    def test_english_prose(self):
        assert detect_latin('The English translation of the text').label == 'english'
        assert detect_latin('The quick brown fox jumps over the lazy dog').label == 'english'

    def test_romanized_gurbani(self):
        assert detect_latin('kiv sachiaaraa hoieeai kiv kooRai tuTai paal').label == 'romanized'

    def test_modern_punjabi(self):
        assert detect_latin('mera phone kharab ho gaya').label == 'romanized'

    def test_names_only_abstains(self):
        g = detect_latin('Guru Gobind Singh')
        assert g.label == 'unknown'
        assert {w.label for w in g.words} == {'name'}

    def test_empty(self):
        assert detect_latin('').label == 'unknown'
        assert detect_latin('ਸਤਿ ਨਾਮੁ ॥').label == 'unknown'

    def test_per_word_labels(self):
        g = detect_latin('saare dost park vich mile')
        labels = {w.word: w.label for w in g.words}
        assert labels['vich'] == 'romanized'
        assert labels['park'] == 'english'

    def test_english_never_romanized(self):
        lines = _lines('english.txt')
        wrong = [l for l in lines if detect_latin(l).label == 'romanized']
        assert not wrong
        assert sum(detect_latin(l).label == 'english' for l in lines) / len(lines) >= 0.85

    def test_punjabi_never_english(self):
        lines = _lines('punjabi_romanized.txt')
        assert not [l for l in lines if detect_latin(l).label == 'english']
        assert sum(detect_latin(l).label == 'romanized' for l in lines) / len(lines) >= 0.85

    @pytest.mark.parametrize('scheme', ['banidb', 'shabados', 'banidb_ipa'])
    def test_gold_lines_romanized(self, scheme):
        lines = [l for l in _gold(scheme) if len(l.split()) >= 5]
        right = sum(detect_latin(l).label == 'romanized' for l in lines)
        assert right / len(lines) >= 0.98, f'{scheme}: {right}/{len(lines)}'
