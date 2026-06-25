"""
Tests for schwa deletion (delete_schwa=True).

Rules under test:
  R1  Word-final consonant loses its inherent 'a'
  R2  Consonant before explicit-vowel consonant loses its inherent 'a'
        (not first consonant in word)

Punjabi does NOT use the Hindi cascade rule (R3): cascading over schwa-schwa
sequences creates unpronounceable clusters (ਹਿੰਮਤ → "hiṃmt" not "hiṃmat").
"""

import pytest
from gurmukhi_transliterate import GurmukhiISO15919, GurmukhiPractical


def iso(text):
    return GurmukhiISO15919.to_phonetic(text, delete_schwa=True)


def prac(text):
    return GurmukhiPractical.to_practical(text, delete_schwa=True)


# ---------------------------------------------------------------------------
# ISO 15919 with schwa deletion
# ---------------------------------------------------------------------------

class TestISO15919SchwaDeletion:
    def test_word_final_simple(self):
        # R1: ਮ is word-final
        assert iso('ਰਾਮ') == 'rām'

    def test_word_final_nasal(self):
        # R1: ਘ is word-final; tippi on ਸਿ is unchanged
        assert iso('ਸਿੰਘ') == 'siṃgh'

    def test_pre_vocalic_not_first(self):
        # R2: ਰ before ਤਾ (explicit ā) → delete ਰ's schwa
        # ਕ is first consonant → kept
        assert iso('ਕਰਤਾ') == 'kartā'

    def test_word_final_only_no_cascade(self):
        # R1: ਤ final deleted; ਮ is NOT deleted (no cascade in Punjabi)
        assert iso('ਹਿੰਮਤ') == 'hiṃmat'

    def test_two_consonant_cluster_final(self):
        # R1: ਨ final; ਰ is not before an explicit vowel → ਰ's schwa kept
        assert iso('ਕਰਨ') == 'karan'

    def test_virama_conjunct_unchanged(self):
        # ਪ੍ਰੇਮ — ਪ has virama (no schwa to delete), ਰੇ explicit, ਮ final
        assert iso('ਪ੍ਰੇਮ') == 'prēm'

    def test_all_explicit_vowels_unchanged(self):
        # All diacritics present → nothing to delete
        assert iso('ਸਤਿ ਨਾਮੁ') == 'sati nāmu'

    def test_r2_does_not_cascade(self):
        # ਕ is first, R2 deletes ਰ before ਤਾ but does NOT cascade to ਕ
        assert iso('ਕਰਤਾ') == 'kartā'
        assert not iso('ਕਰਤਾ').startswith('rt')


# ---------------------------------------------------------------------------
# Practical with schwa deletion
# ---------------------------------------------------------------------------

class TestPracticalSchwaDeletion:
    def test_word_final_simple(self):
        assert prac('ਰਾਮ') == 'raam'

    def test_word_final_nasal(self):
        assert prac('ਸਿੰਘ') == 'singh'

    def test_pre_vocalic_not_first(self):
        assert prac('ਕਰਤਾ') == 'kartaa'

    def test_word_final_only_no_cascade(self):
        # R1 only: ਤ final deleted, ਮ's schwa kept (no cascade)
        assert prac('ਹਿੰਮਤ') == 'himmat'

    def test_two_cluster_final(self):
        # R1 only: ਨ final deleted, ਰ's schwa kept
        assert prac('ਕਰਨ') == 'karan'

    def test_all_explicit_vowels_unchanged(self):
        assert prac('ਸਤਿ ਨਾਮੁ') == 'sati naamu'

    def test_multi_word(self):
        # Each word processed independently
        result = prac('ਰਾਮ ਸਿੰਘ')
        assert result == 'raam singh'

    def test_explicit_vowel_word_untouched(self):
        # ਗੁਰੂ — all vowels explicit, nothing deleted
        assert prac('ਗੁਰੂ') == 'guroo'


# ---------------------------------------------------------------------------
# Existing behaviour (delete_schwa=False) must not change
# ---------------------------------------------------------------------------

class TestNoRegressionISO:
    def test_default_off(self):
        assert GurmukhiISO15919.to_phonetic('ਸਿੰਘ') == 'siṃgha'
        assert GurmukhiISO15919.to_phonetic('ਰਾਮ') == 'rāma'
        assert GurmukhiISO15919.to_phonetic('ਕਰਤਾ') == 'karatā'

    def test_explicit_false(self):
        assert GurmukhiISO15919.to_phonetic('ਸਿੰਘ', delete_schwa=False) == 'siṃgha'


class TestNoRegressionPractical:
    def test_default_off(self):
        assert GurmukhiPractical.to_practical('ਸਿੰਘ') == 'singha'
        assert GurmukhiPractical.to_practical('ਵਾਹਿਗੁਰੂ') == 'vaahiguroo'
