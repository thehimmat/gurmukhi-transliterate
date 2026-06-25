"""Tests for the "Other" romanization systems via GurmukhiRomanizer."""

import pytest
from gurmukhi_transliterate import GurmukhiRomanizer, SYSTEMS, SYSTEM_ORDER


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def rom(system_id: str, text: str, delete_schwa: bool = False) -> str:
    return GurmukhiRomanizer(system_id).romanize(text, delete_schwa=delete_schwa)


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

class TestRegistry:
    def test_all_system_ids_present(self):
        assert set(SYSTEM_ORDER) == set(SYSTEMS.keys())

    def test_unknown_system_raises(self):
        with pytest.raises(ValueError):
            GurmukhiRomanizer('nonexistent')


# ---------------------------------------------------------------------------
# Dr. Sant Singh Khalsa
# ---------------------------------------------------------------------------

class TestDrSantSingh:
    def test_waheguru(self):
        assert rom('dr_sant_singh', 'ਵਾਹਿਗੁਰੂ') == 'vaahiguroo'

    def test_satnam(self):
        assert rom('dr_sant_singh', 'ਸਤਿ ਨਾਮੁ') == 'sati naamu'

    def test_retroflex_with_dot(self):
        # ṭ ḍ ṇ ṛ all present in Sant Singh
        assert rom('dr_sant_singh', 'ਟ') == 'ṭa'
        assert rom('dr_sant_singh', 'ਡ') == 'ḍa'
        assert rom('dr_sant_singh', 'ਣ') == 'ṇa'

    def test_singh(self):
        assert rom('dr_sant_singh', 'ਸਿੰਘ') == 'singha'

    def test_schwa_deletion(self):
        assert rom('dr_sant_singh', 'ਸਿੰਘ', delete_schwa=True) == 'singh'
        assert rom('dr_sant_singh', 'ਕਰਤਾ', delete_schwa=True) == 'kartaa'  # R2: ਰ before ਤਾ


# ---------------------------------------------------------------------------
# Dr. Thind
# ---------------------------------------------------------------------------

class TestDrThind:
    def test_waheguru(self):
        assert rom('dr_thind', 'ਵਾਹਿਗੁਰੂ') == 'vaahiguroo'

    def test_retroflex_merged_with_dental(self):
        # Thind merges retroflex and dental
        assert rom('dr_thind', 'ਟ') == 'ta'
        assert rom('dr_thind', 'ਤ') == 'ta'

    def test_ng_is_ny(self):
        # Thind uses ny for ਙ
        assert rom('dr_thind', 'ਙ') == 'nya'

    def test_rh(self):
        assert rom('dr_thind', 'ੜ') == 'rha'


# ---------------------------------------------------------------------------
# STTM
# ---------------------------------------------------------------------------

class TestSTTM:
    def test_waheguru(self):
        assert rom('sttm', 'ਵਾਹਿਗੁਰੂ') == 'vaahiguroo'

    def test_dental_t_is_th(self):
        # STTM uses th for dental ਤ
        assert rom('sttm', 'ਤ') == 'tha'

    def test_retroflex_tt(self):
        # STTM uses tt for retroflex ਟ
        assert rom('sttm', 'ਟ') == 'tta'

    def test_satnam(self):
        # ਸਤਿ with STTM: ਤ → th
        assert rom('sttm', 'ਸਤਿ') == 'sathi'


# ---------------------------------------------------------------------------
# Guru Fatha Singh
# ---------------------------------------------------------------------------

class TestGFS:
    def test_waheguru(self):
        assert rom('gfs', 'ਵਾਹਿਗੁਰੂ') == 'vaahiguroo'

    def test_ph_for_pha(self):
        assert rom('gfs', 'ਫ') == 'pha'

    def test_gn_for_ng(self):
        # GFS uses gn for ਙ (not ng)
        assert rom('gfs', 'ਙ') == 'gna'

    def test_ny_for_nj(self):
        assert rom('gfs', 'ਞ') == 'nya'


# ---------------------------------------------------------------------------
# Sacred Nitnem
# ---------------------------------------------------------------------------

class TestSacredNitnem:
    def test_macron_vowels(self):
        # Long vowels use macrons
        assert rom('sacred_nitnem', 'ਕਾ') == 'kā'
        assert rom('sacred_nitnem', 'ਕੀ') == 'kī'
        assert rom('sacred_nitnem', 'ਕੂ') == 'kū'

    def test_nasal(self):
        assert rom('sacred_nitnem', 'ਸਿੰਘ') == 'siṅgha'

    def test_retroflex(self):
        assert rom('sacred_nitnem', 'ਟ') == 'ṭa'


# ---------------------------------------------------------------------------
# IAST
# ---------------------------------------------------------------------------

class TestIAST:
    def test_conjunct(self):
        assert rom('iast', 'ਪ੍ਰੇਮ') == 'prema'

    def test_macron_vowels(self):
        assert rom('iast', 'ਕਾ') == 'kā'

    def test_nasal(self):
        # IAST: tippi → ṃ
        assert rom('iast', 'ਸਿੰਘ') == 'siṃgha'

    def test_persian_none(self):
        # IAST doesn't support Persian letters → skip silently
        result = rom('iast', 'ਜ਼')
        assert 'z' not in result


# ---------------------------------------------------------------------------
# IPA
# ---------------------------------------------------------------------------

class TestIPA:
    def test_inherent_vowel_is_schwa(self):
        assert rom('ipa', 'ਕ') == 'kə'

    def test_long_vowel(self):
        assert rom('ipa', 'ਕਾ') == 'kaː'

    def test_voiced_h(self):
        assert rom('ipa', 'ਹ') == 'ɦə'

    def test_waheguru(self):
        assert rom('ipa', 'ਵਾਹਿਗੁਰੂ') == 'ʋaːɦɪɡʊruː'

    def test_schwa_deletion(self):
        # With deletion, word-final ə suppressed
        assert rom('ipa', 'ਰਾਮ', delete_schwa=True) == 'raːm'


# ---------------------------------------------------------------------------
# Addak (gemination) across systems
# ---------------------------------------------------------------------------

class TestAddak:
    def test_addak_doubles_sant_singh(self):
        # ਪੱਕਾ → pakkaa
        assert rom('dr_sant_singh', 'ਪੱਕਾ') == 'pakkaa'

    def test_addak_doubles_iast(self):
        assert rom('iast', 'ਪੱਕਾ') == 'pakkā'
