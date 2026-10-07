import csv
import pathlib

import pytest

from gurmukhi_transliterate import UnableToReverse, VerseMatch, match_verse, to_gurmukhi

GOLD = pathlib.Path(__file__).parent / 'fixtures' / 'gold'


def gold():
    with open(GOLD / 'lines.tsv', encoding='utf-8', newline='') as f:
        return list(csv.DictReader(f, delimiter='\t', quoting=csv.QUOTE_NONE, escapechar='\\'))


def hit(matches, line_id):
    return bool(matches) and any(loc.id == line_id for loc in matches[0].locations)


class TestMatchesRealRomanizations:
    @pytest.mark.parametrize('scheme', ['banidb', 'shabados', 'gurbaniakhar', 'gurmukhi'])
    def test_first_rows(self, scheme):
        rows = [r for r in gold() if len(r['gurmukhi'].split()) >= 4][:25]
        hits = sum(hit(match_verse(r[scheme]), r['id']) for r in rows)
        assert hits >= 24, f'{scheme}: {hits}/25'

    def test_partial_line(self):
        rows = [r for r in gold() if len(r['banidb'].split()) >= 6][:20]
        hits = 0
        for r in rows:
            words = r['banidb'].split()
            hits += hit(match_verse(' '.join(words[:max(4, len(words) * 6 // 10)])), r['id'])
        assert hits >= 16

    def test_noisy_gurmukhi(self):
        # OCR-style damage: one vowel sign dropped
        assert match_verse('ਕਿਵ ਸਚਿਆਰਾ ਹੋਈਐ ਕਿਵ ਕੂੜੈ ਤੁਟ ਪਾਲਿ')[0].gurmukhi == 'ਕਿਵ ਸਚਿਆਰਾ ਹੋਈਐ ਕਿਵ ਕੂੜੈ ਤੁਟੈ ਪਾਲਿ ॥'


class TestResult:
    def test_fields(self):
        m = match_verse('kiv sachiaaraa hoieeaai kiv kooRai tuTai paal')[0]
        assert isinstance(m, VerseMatch)
        assert m.gurmukhi == 'ਕਿਵ ਸਚਿਆਰਾ ਹੋਈਐ ਕਿਵ ਕੂੜੈ ਤੁਟੈ ਪਾਲਿ ॥'
        assert m.source == 'sggs' and m.page == 1
        assert 0.0 < m.score <= 1.0

    def test_repeated_line_returns_every_location(self):
        m = match_verse('so purakh niranjan har purakh niranjan har agamaa agam apaaraa')[0]
        assert len(m.locations) >= 2
        assert {loc.page for loc in m.locations} >= {10, 348}

    def test_ranked_best_first(self):
        ms = match_verse('har har naam dhiaaeeai', top_n=5)
        assert [m.score for m in ms] == sorted((m.score for m in ms), reverse=True)


class TestAbstains:
    def test_english(self):
        for line in (GOLD / 'english.txt').read_text().splitlines()[:10]:
            assert match_verse(line) == [], line

    def test_modern_punjabi(self):
        lines = (GOLD / 'punjabi_romanized.txt').read_text().splitlines()
        accepted = [l for l in lines if match_verse(l)]
        assert len(accepted) <= 1, accepted

    def test_empty(self):
        assert match_verse('') == []


class TestToGurmukhi:
    def test_returns_canonical_line(self):
        assert to_gurmukhi('hukam rajaiee chalanaa naanak likhiaa naal') == \
            'ਹੁਕਮਿ ਰਜਾਈ ਚਲਣਾ ਨਾਨਕ ਲਿਖਿਆ ਨਾਲਿ ॥੧॥'

    def test_raises_when_unmatched(self):
        with pytest.raises(UnableToReverse):
            to_gurmukhi('mera phone kharab ho gaya')
