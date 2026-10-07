"""Tests for comparison_table and identify_system."""

import pytest

from gurmukhi_transliterate import comparison_table, identify_system, SYSTEMS, SYSTEM_ORDER


class TestComparisonTable:
    def test_returns_all_systems(self):
        tbl = comparison_table('ਸਿੰਘ')
        expected_keys = {'iso15919', 'practical'} | set(SYSTEM_ORDER)
        assert set(tbl.keys()) == expected_keys

    def test_order_iso_practical_first(self):
        keys = list(comparison_table('ਸਿੰਘ').keys())
        assert keys[0] == 'iso15919'
        assert keys[1] == 'practical'

    def test_subset(self):
        tbl = comparison_table('ਸਿੰਘ', systems=['iso15919', 'dr_thind'])
        assert set(tbl.keys()) == {'iso15919', 'dr_thind'}

    def test_values_are_strings(self):
        tbl = comparison_table('ਰਾਮ')
        for v in tbl.values():
            assert isinstance(v, str)

    def test_iso_uses_macron(self):
        tbl = comparison_table('ਕਾ')
        assert 'ā' in tbl['iso15919']

    def test_practical_uses_doubles(self):
        tbl = comparison_table('ਕਾ')
        assert 'aa' in tbl['practical']

    def test_schwa_deletion_propagates(self):
        with_del = comparison_table('ਸਿੰਘ', delete_schwa=True)
        without_del = comparison_table('ਸਿੰਘ', delete_schwa=False)
        assert 'singha' in without_del['dr_sant_singh']
        assert 'singh' == with_del['dr_sant_singh']


class TestIdentifySystem:
    def test_returns_list_of_dicts(self):
        results = identify_system('waheguru')
        assert isinstance(results, list)
        assert all(isinstance(r, dict) for r in results)
        assert all({'system', 'label', 'confidence'} <= r.keys() for r in results)

    def test_sorted_descending(self):
        results = identify_system('waheguru')
        scores = [r['confidence'] for r in results]
        assert scores == sorted(scores, reverse=True)

    def test_top_n(self):
        results = identify_system('waheguru', top_n=3)
        assert len(results) <= 3

    def test_vaahiguroo_ranks_practical_systems_high(self):
        # 'aa' and 'oo' are signatures of the practical / Sant Singh family
        results = identify_system('vaahiguroo')
        top_ids = {r['system'] for r in results[:4]}
        practical_systems = {'dr_sant_singh', 'dr_thind', 'sttm', 'gfs', 'practical'}
        assert top_ids & practical_systems  # at least one in top 4

    def test_macron_text_ranks_scholarly_high(self):
        # ā ī ū are signatures of ISO 15919 / IAST / Sacred Nitnem
        results = identify_system('vahigurū')
        top_ids = {r['system'] for r in results[:3]}
        scholarly = {'iso15919', 'iast', 'sacred_nitnem'}
        assert top_ids & scholarly

    def test_ipa_chars_rank_ipa_high(self):
        results = identify_system('ʋaːɦɪɡʊruː')
        top_system = results[0]['system']
        assert top_system == 'ipa'

    def test_confidence_range(self):
        results = identify_system('singh')
        for r in results:
            assert 0.0 <= r['confidence'] <= 1.0

    def test_empty_input(self):
        results = identify_system('')
        assert results == []


# --- #27: likelihood-based identification ------------------------------------

def _gold():
    import csv, pathlib
    path = pathlib.Path(__file__).parent / 'fixtures' / 'gold' / 'lines.tsv'
    with open(path, encoding='utf-8', newline='') as f:
        return list(csv.DictReader(f, delimiter='\t', quoting=csv.QUOTE_NONE, escapechar='\\'))


class TestIdentifyLikelihood:
    @pytest.mark.parametrize('scheme, system, top1', [('banidb', 'sttm', 0.8), ('shabados', 'shabados', 0.85),
                                                      ('banidb_ipa', 'banidb_ipa', 0.95)])
    def test_true_system_on_real_lines(self, scheme, system, top1):
        rows = [r for r in _gold() if len(r[scheme].split()) >= 5]
        first = in_class = 0
        for r in rows:
            ranked = identify_system(r[scheme], top_n=20)
            first += ranked[0]['system'] == system
            in_class += any(d['system'] == system and d['equivalent'] for d in ranked)
        assert first / len(rows) >= top1, f'{scheme}: top-1 {first}/{len(rows)}'
        assert in_class / len(rows) >= 0.95, f'{scheme}: equivalence class {in_class}/{len(rows)}'

    def test_identical_outputs_are_equivalent(self):
        from gurmukhi_transliterate import GurmukhiRomanizer, GurmukhiISO15919
        text = 'ਸਤਿਗੁਰ ਪ੍ਰਸਾਦਿ ਨਾਮੁ'
        assert GurmukhiRomanizer('iast').romanize(text) == GurmukhiISO15919.to_phonetic(text)
        ranked = identify_system(GurmukhiRomanizer('iast').romanize(text), top_n=16)
        eq = {r['system'] for r in ranked if r['equivalent']}
        assert {'iast', 'iso15919'} <= eq

    def test_english_gets_low_confidence(self):
        ranked = identify_system('The quick brown fox jumps over the lazy dog')
        assert all(r['confidence'] < 0.5 for r in ranked)

    def test_english_can_be_ranked(self):
        ranked = identify_system('The quick brown fox jumps over the lazy dog', include_english=True)
        assert ranked[0]['system'] == 'english'

    def test_informal_phrase(self):
        assert identify_system('Waheguru Ji Ka Khalsa Waheguru Ji Ki Fateh')[0]['system'] == 'informal'

    def test_case_signals_kept(self):
        # BaniDB's capital retroflexes point at sttm
        assert identify_system('kooRai tuTai paal')[0]['system'] == 'sttm'
