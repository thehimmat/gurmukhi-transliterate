"""Tests for Shackle → Gurmukhi reverse transliteration.

Expected outputs are taken from the worked examples in Shackle,
A Guru Nanak Glossary (2nd ed. 2011), Transcription pp. xxi-xxv.
"""

import pytest
from gurmukhi_transliterate.reverse import (
    shackle_to_gurmukhi,
    reverse_transliterate,
)

pytestmark = pytest.mark.story('US-008')


# ---------------------------------------------------------------------------
# Deterministic core (single unambiguous answer)
# ---------------------------------------------------------------------------

class TestVowelsOnConsonant:
    """§2 table: vowels written on the base consonant ਸ."""

    @pytest.mark.parametrize("roman,gurmukhi", [
        ('sa', 'ਸ'),
        ('sā', 'ਸਾ'),
        ('si', 'ਸਿ'),
        ('sī', 'ਸੀ'),
        ('su', 'ਸੁ'),
        ('sū', 'ਸੂ'),
        ('se', 'ਸੇ'),
        ('sai', 'ਸੈ'),
        ('so', 'ਸੋ'),
        ('sau', 'ਸੌ'),
    ])
    def test_vowel_forms(self, roman, gurmukhi):
        assert shackle_to_gurmukhi(roman) == gurmukhi


class TestIndependentVowels:
    """Word-initial vowels become independent letters, not matras."""

    @pytest.mark.parametrize("roman,gurmukhi", [
        ('a', 'ਅ'),
        ('ā', 'ਆ'),
        ('i', 'ਇ'),
        ('ī', 'ਈ'),
        ('u', 'ਉ'),
        ('ū', 'ਊ'),
        ('e', 'ਏ'),
        ('ai', 'ਐ'),
        ('o', 'ਓ'),
        ('au', 'ਔ'),
        ('eka', 'ਏਕ'),
    ])
    def test_initial_vowel(self, roman, gurmukhi):
        assert shackle_to_gurmukhi(roman) == gurmukhi


class TestWords:
    @pytest.mark.parametrize("roman,gurmukhi", [
        ('sati', 'ਸਤਿ'),
        ('nāmu', 'ਨਾਮੁ'),
        ('vāhigurū', 'ਵਾਹਿਗੁਰੂ'),
    ])
    def test_word(self, roman, gurmukhi):
        assert shackle_to_gurmukhi(roman) == gurmukhi


class TestInherentFinalA:
    """Shackle writes the inherent -a; a word-final -a is a bare consonant."""

    def test_final_a_no_matra(self):
        assert shackle_to_gurmukhi('ka') == 'ਕ'
        assert shackle_to_gurmukhi('kamala') == 'ਕਮਲ'


class TestRetroflexAndAspirates:
    def test_retroflex_preserved(self):
        # ṭ ≠ t on reverse
        assert shackle_to_gurmukhi('ṭa') == 'ਟ'
        assert shackle_to_gurmukhi('ta') == 'ਤ'

    def test_aspirated_stops_single_letter(self):
        # kh gh ch jh ṭh ḍh th dh ph bh are single Gurmukhi letters
        assert shackle_to_gurmukhi('kha') == 'ਖ'
        assert shackle_to_gurmukhi('gha') == 'ਘ'
        assert shackle_to_gurmukhi('cha') == 'ਛ'
        assert shackle_to_gurmukhi('ṭha') == 'ਠ'
        assert shackle_to_gurmukhi('dha') == 'ਧ'
        assert shackle_to_gurmukhi('pha') == 'ਫ'

    def test_c_is_cha(self):
        assert shackle_to_gurmukhi('ca') == 'ਚ'


class TestConjuncts:
    """§3a: two consonants with no vowel between = subjoined conjunct."""

    def test_r_conjunct(self):
        assert shackle_to_gurmukhi('sravaṇu') == 'ਸ੍ਰਵਣੁ'

    def test_v_conjunct(self):
        assert shackle_to_gurmukhi('svādu') == 'ਸ੍ਵਾਦੁ'


class TestNasalGroups:
    """§5: homorganic nasal before a consonant reverses to ੰ (ṭippī)."""

    @pytest.mark.parametrize("roman,gurmukhi", [
        ('saṅka', 'ਸੰਕ'),
        ('sañca', 'ਸੰਚ'),
        ('saṇṭa', 'ਸੰਟ'),
        ('santa', 'ਸੰਤ'),
        ('sampa', 'ਸੰਪ'),
    ])
    def test_nasal_group(self, roman, gurmukhi):
        assert shackle_to_gurmukhi(roman) == gurmukhi

    def test_nasal_before_vowel_is_plain_consonant(self):
        # A nasal followed by a vowel is a real consonant, not a group
        assert shackle_to_gurmukhi('nāmu') == 'ਨਾਮੁ'


# ---------------------------------------------------------------------------
# Ambiguous cases: primary answer + flagged alternatives
# ---------------------------------------------------------------------------

class TestGemination:
    """§4: doubling is not marked in (old) Gurmukhi → collapses on reverse."""

    def test_doubling_collapses(self):
        assert shackle_to_gurmukhi('matti') == 'ਮਤਿ'
        assert shackle_to_gurmukhi('mati') == 'ਮਤਿ'

    def test_gemination_flagged_with_addak_alternative(self):
        res = reverse_transliterate('matti')
        kinds = {a.kind for a in res.ambiguities}
        assert 'gemination' in kinds
        # addak-marked form offered as an alternative candidate
        assert any('ੱ' in alt for a in res.ambiguities for alt in a.alternatives)


class TestAspirateSonorants:
    """§3b: nh mh lh rh ṇh ṛh carry a subjoined ੍ਹ that print often omits."""

    def test_subjoined_h_primary(self):
        assert shackle_to_gurmukhi('nhātā') == 'ਨ੍ਹਾਤਾ'

    def test_aspirate_flagged(self):
        res = reverse_transliterate('nhātā')
        assert any(a.kind == 'aspirate_sonorant' for a in res.ambiguities)


class TestNasalization:
    """§6: ṁ may be written with ṭippī ੰ or bindī ਂ."""

    def test_primary_is_tippi(self):
        assert shackle_to_gurmukhi('sāṁ') == 'ਸਾੰ'

    def test_bindi_flagged(self):
        res = reverse_transliterate('sāṁ')
        assert any(a.kind == 'nasalization' for a in res.ambiguities)
        assert any('ਂ' in alt for a in res.ambiguities for alt in a.alternatives)


class TestPersian:
    def test_distinct_persian_letters(self):
        # ġ, z, f, q, ś carry their own diacritic → reversible
        assert shackle_to_gurmukhi('ġa') == 'ਗ਼'
        assert shackle_to_gurmukhi('za') == 'ਜ਼'
        assert shackle_to_gurmukhi('fa') == 'ਫ਼'
        assert shackle_to_gurmukhi('śa') == 'ਸ਼'


# --- #25: nasal groups only before homorganic consonants; ï hiatus -----------

class TestNasalGroupHomorganic:
    @pytest.mark.parametrize('roman, expected', [
        ('amritu', 'ਅਮ੍ਰਿਤੁ'),      # m + r is a conjunct, not a nasal group
        ('ammritu', 'ਅੰਮ੍ਰਿਤੁ'),    # geminate m (ੰ+ਮ), then ਮ੍ਰ — no doubled tippi
        ('santa', 'ਸੰਤ'),           # homorganic groups still take tippi
        ('saṅka', 'ਸੰਕ'),
        ('sañca', 'ਸੰਚ'),
        ('saṇṭa', 'ਸੰਟ'),
        ('sampa', 'ਸੰਪ'),
    ])
    def test_nasal_groups(self, roman, expected):
        assert shackle_to_gurmukhi(roman) == expected

    def test_no_doubled_tippi(self):
        assert 'ੰੰ' not in shackle_to_gurmukhi('ammritu')

    def test_amritu_offers_tippi_spelling(self):
        from gurmukhi_transliterate.matcher import candidate_spellings
        assert 'ਅੰਮ੍ਰਿਤੁ' in candidate_spellings(reverse_transliterate('amritu'))

    def test_forward_shackle_round_trips(self):
        from gurmukhi_transliterate import GurmukhiRomanizer
        roman = GurmukhiRomanizer('shackle').romanize('ਅੰਮ੍ਰਿਤੁ')
        assert shackle_to_gurmukhi(roman) == 'ਅੰਮ੍ਰਿਤੁ'


class TestDiaeresisHiatus:
    def test_i_diaeresis(self):
        assert shackle_to_gurmukhi('daïā') == 'ਦਇਆ'

    def test_no_latin_leaks(self):
        out = shackle_to_gurmukhi('daïā saü')
        assert not any('a' <= ch.lower() <= 'z' or ch in 'ïü' for ch in out)


class TestKoshCrossCheck:
    """#13: words the Shackle OCR cross-check (gurmukhi-kosh #6) reversed
    wrongly; the printed Gurmukhi was right."""

    @pytest.mark.parametrize('roman, gurmukhi', [
        ('jūṭhā', 'ਜੂਠਾ'),        # ṭh is retroflex ਠ, not dental ਥ
        ('kaṅkaṇu', 'ਕੰਕਣੁ'),     # ṇ is ਣ, not ਨ
        ('bālaṇu', 'ਬਾਲਣੁ'),
        ('putru', 'ਪੁਤ੍ਰੁ'),       # subjoined ਰ kept
        ('mitru', 'ਮਿਤ੍ਰੁ'),
        ('pavitru', 'ਪਵਿਤ੍ਰੁ'),
        ('daïā', 'ਦਇਆ'),          # no Latin ï leaks
        ('ammritu', 'ਅੰਮ੍ਰਿਤੁ'),   # no doubled tippi
    ])
    def test_reverses_to_printed_spelling(self, roman, gurmukhi):
        assert shackle_to_gurmukhi(roman) == gurmukhi
