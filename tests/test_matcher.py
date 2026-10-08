"""Tests for the corpus matcher (Shackle reverse → attested Gurmukhi word)."""

import pytest

from gurmukhi_transliterate.matcher import (
    CorpusMatcher,
    candidate_spellings,
    load_lexicon,
)
from gurmukhi_transliterate.reverse import reverse_transliterate

pytestmark = pytest.mark.story('US-008')


class TestCandidateEnumeration:
    def test_no_ambiguity_single_candidate(self):
        res = reverse_transliterate('sati')
        assert candidate_spellings(res) == ['ਸਤਿ']

    def test_primary_is_first(self):
        res = reverse_transliterate('sāṁ')
        cands = candidate_spellings(res)
        assert cands[0] == 'ਸਾਂ'          # bindī after ā (primary)
        assert 'ਸਾੰ' in cands             # ṭippī alternative

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
        # ਖ/ਖ਼  ×  ੰ/ਂ/(dropped)  → 6 spellings
        assert 'ਖੰ' in cands     # ṭippī
        assert 'ਖਂ' in cands     # bindī
        assert 'ਖ' in cands      # nasal dropped (§6 "only sometimes marked")
        assert 'ਖਾਂ' not in cands  # sanity: no spurious matra
        assert len(cands) == 6


class TestMatching:
    def test_more_frequent_form_wins(self):
        # the alternative (ṭippī) beats the primary when the corpus prefers it
        matcher = CorpusMatcher({'ਸਾਂ': 2, 'ਸਾੰ': 40})
        res = matcher.match('sāṁ')
        assert res.resolved
        assert res.best == 'ਸਾੰ'
        assert res.matches[0].frequency == 40

    def test_primary_wins_when_only_attested(self):
        matcher = CorpusMatcher({'ਨ੍ਹਾਤਾ': 5})
        res = matcher.match('nhātā')
        assert res.best == 'ਨ੍ਹਾਤਾ'

    def test_falls_back_to_primary_when_nothing_attested(self):
        matcher = CorpusMatcher({'ਹੋਰ': 9})  # unrelated word
        res = matcher.match('sāṁ')
        assert not res.resolved
        assert res.best == 'ਸਾਂ'  # primary reverse output

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


class TestFileLoader:
    def test_from_file(self, tmp_path):
        # word<TAB>frequency, with a comment and a bare-word line
        p = tmp_path / 'lex.tsv'
        p.write_text(
            '# SGGS sample\nਸਾਂ\t40\nਸੰਤ\t691\nਨਾਮੁ\n',
            encoding='utf-8',
        )
        freq = load_lexicon(p)
        assert freq['ਸਾਂ'] == 40
        assert freq['ਨਾਮੁ'] == 1  # bare word → frequency 1
        matcher = CorpusMatcher.from_file(p)
        # saṁta primary is ਸੰਤ, attested in the file
        assert matcher.match('santa').best == 'ਸੰਤ'
