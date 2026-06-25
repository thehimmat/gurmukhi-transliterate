"""Tests for comparison_table and identify_system."""

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
