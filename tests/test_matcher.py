"""Tests for the corpus matcher (Shackle reverse → attested Gurmukhi word)."""

from gurmukhi_transliterate.matcher import (
    CorpusMatcher,
    candidate_spellings,
)
from gurmukhi_transliterate.reverse import reverse_transliterate


class TestCandidateEnumeration:
    def test_no_ambiguity_single_candidate(self):
        res = reverse_transliterate('sati')
        assert candidate_spellings(res) == ['ਸਤਿ']

    def test_primary_is_first(self):
        res = reverse_transliterate('sāṁ')
        cands = candidate_spellings(res)
        assert cands[0] == 'ਸਾੰ'          # ṭippī primary
        assert 'ਸਾਂ' in cands             # bindī alternative

    def test_aspirate_alternatives(self):
        res = reverse_transliterate('nhātā')
        cands = candidate_spellings(res)
        assert 'ਨ੍ਹਾਤਾ' in cands          # subjoined ੍ਹ (primary)
        assert 'ਨਹਾਤਾ' in cands           # print-omitted variant
        assert 'ਨਾਤਾ' in cands            # bare

    def test_multiple_ambiguities_product(self):
        # a word with both a persian collision and a nasalization
        res = reverse_transliterate('khaṁ')
        cands = candidate_spellings(res)
        # ਖ/ਖ਼  ×  ੰ/ਂ  → 4 spellings
        assert 'ਖੰ' in cands
        assert 'ਖਾਂ' not in cands  # sanity: no spurious matra
        assert len(cands) == 4


class TestMatching:
    def test_bindi_form_wins_when_more_frequent(self):
        # corpus has the bindī spelling far more often than the ṭippī one
        matcher = CorpusMatcher({'ਸਾਂ': 40, 'ਸਾੰ': 2})
        res = matcher.match('sāṁ')
        assert res.resolved
        assert res.best == 'ਸਾਂ'
        assert res.matches[0].frequency == 40

    def test_primary_wins_when_only_attested(self):
        matcher = CorpusMatcher({'ਨ੍ਹਾਤਾ': 5})
        res = matcher.match('nhātā')
        assert res.best == 'ਨ੍ਹਾਤਾ'

    def test_falls_back_to_primary_when_nothing_attested(self):
        matcher = CorpusMatcher({'ਹੋਰ': 9})  # unrelated word
        res = matcher.match('sāṁ')
        assert not res.resolved
        assert res.best == 'ਸਾੰ'  # primary reverse output

    def test_gemination_resolves_to_addak_form(self):
        # Shackle 'matti' → primary ਮਤਿ; corpus attests the addak form ਮੱਤਿ
        matcher = CorpusMatcher({'ਮੱਤਿ': 12})
        res = matcher.match('matti')
        assert res.best == 'ਮੱਤਿ'

    def test_set_lexicon_frequency_one(self):
        matcher = CorpusMatcher({'ਸਤਿ'})
        res = matcher.match('sati')
        assert res.resolved
        assert res.best == 'ਸਤਿ'
        assert res.matches[0].frequency == 1

    def test_contains(self):
        matcher = CorpusMatcher({'ਸਤਿ': 3})
        assert 'ਸਤਿ' in matcher
        assert 'ਨਾਮੁ' not in matcher
