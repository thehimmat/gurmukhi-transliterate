"""Tests for the "Other" romanization systems via GurmukhiRomanizer."""

import pytest
from gurmukhi_transliterate import GurmukhiRomanizer, SYSTEMS, SYSTEM_ORDER

pytestmark = pytest.mark.story('US-004')


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
    """Current BaniDB scheme (sikhitothemax.org), via the anvaad-js port.

    Expected values are BaniDB's own output (see tests/test_conformance.py)."""

    def test_waheguru(self):
        assert rom('sttm', 'ਵਾਹਿਗੁਰੂ') == 'vaahiguroo'

    def test_final_short_vowels_dropped_before_a_space(self):
        assert rom('sttm', 'ਸਤਿ ਨਾਮੁ ॥') == 'sat naam ||'

    def test_retroflex_capitals(self):
        assert rom('sttm', 'ਕੂੜੈ ਤੁਟੈ ॥') == 'kooRai tuTai ||'

    def test_nasal_parenthesised(self):
        assert rom('sttm', 'ਸੈਭੰ ਗੁਰ ॥') == 'saibha(n) gur ||'

    def test_dh_merger(self):
        assert rom('sttm', 'ਦਇਆ ਧਰਮ ॥') == 'dhiaa dharam ||'

    def test_addak_apostrophe(self):
        assert rom('sttm', 'ਸਿੱਖੀ ਸਿਖਿਆ ॥') == "si'khee sikhiaa ||"

    def test_mahalaa_ordinal(self):
        assert rom('sttm', 'ਮਹਲਾ ੫ ॥') == 'mahalaa panjavaa ||'

    def test_ik_oankaar(self):
        assert rom('sttm', 'ੴ ਸਤਿ ਨਾਮੁ ॥') == 'ikOankaar sat naam ||'

    def test_delete_schwa_has_no_effect(self):
        assert rom('sttm', 'ਨਾਮ ਜਪੈ ॥', delete_schwa=True) == rom('sttm', 'ਨਾਮ ਜਪੈ ॥')


class TestSTTMLegacy:
    """Old SikhiToTheMax scheme, still used by iGurbani."""

    def test_waheguru(self):
        assert rom('sttm_legacy', 'ਵਾਹਿਗੁਰੂ') == 'vaahiguroo'

    def test_dental_t_is_th(self):
        assert rom('sttm_legacy', 'ਤ') == 'tha'

    def test_retroflex_tt(self):
        assert rom('sttm_legacy', 'ਟ') == 'tta'

    def test_satnam(self):
        assert rom('sttm_legacy', 'ਸਤਿ') == 'sathi'

    def test_ek_is_eaek(self):
        # iGurbani-verified: ਏਕ → eaek
        assert rom('sttm_legacy', 'ਏਕ') == 'eaeka'

    @pytest.mark.parametrize('text, expected', [('ਵਞਾਈਐ', 'vanjaaeeai'), ('ਵੰਞਾ', 'vannjaa')])
    def test_nya_is_nj(self, text, expected):
        # iGurbani (#4): ਞ → nj
        assert rom('sttm_legacy', text) == expected


class TestBaniDBIPA:
    """BaniDB's IPA field, via the anvaad-js port."""

    def test_bh_is_implosive(self):
        assert rom('banidb_ipa', 'ਭੀ ਸਚੁ ॥') == 'ɓi sət͡ʃ.'

    def test_line(self):
        assert rom('banidb_ipa', 'ਕੂੜੈ ਤੁਟੈ ॥') == 'kuɽæ t̪ʊʈæ.'


class TestGursevak:
    """Expectations verified against the app's Gursevak.sqlite (v3.01)."""

    def test_sihari_is_e(self):
        # ਲਿਖ → lekh + inherent a (sihari → e)
        assert rom('gursevak', 'ਲਿਖ') == 'lekha'

    def test_tippi_superscript(self):
        # ਸੈਭੰ → saibhaⁿ
        assert rom('gursevak', 'ਸੈਭੰ') == 'saibhaⁿ'

    def test_laavaan_is_ay(self):
        # DB: ਜੇ → j‹ay›
        assert rom('gursevak', 'ਜੇ') == 'jay'

    def test_retroflex_series(self):
        # DB: ਤੋਟਿ → t‹o›tt‹e›, ਠਾਕ → tth‹aa›k, ਢਾਲਿ → ddh‹aa›l‹e›
        assert rom('gursevak', 'ਤੋਟਿ') == 'totte'
        assert rom('gursevak', 'ਠਾਕ') == 'tthaaka'
        assert rom('gursevak', 'ਢਾਲਿ') == 'ddhaale'

    def test_nn_for_nanna(self):
        # DB: ਜਾਣੈ → j‹aa›nn‹ai›
        assert rom('gursevak', 'ਜਾਣੈ') == 'jaannai'

    def test_capital_Y(self):
        # DB: ਯਯਾ → YaY‹aa›
        assert rom('gursevak', 'ਯਯਾ') == 'YaYaa'

    def test_dental_d_plain(self):
        # DB: ਦੁਖ → d‹u›kh (d, not dh)
        assert rom('gursevak', 'ਦੁਖ') == 'dukha'


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
# Shackle (Sacred Language of the Sikhs)
# ---------------------------------------------------------------------------

@pytest.mark.story('US-007')
class TestShackle:
    """Expectations from Shackle, A Guru Nanak Glossary (2011), pp. xxi-xxv."""

    def test_waheguru(self):
        assert rom('shackle', 'ਵਾਹਿਗੁਰੂ') == 'vāhigurū'

    def test_inherent_a_written(self):
        # Inherent -a written after every unmarked consonant (§2)
        assert rom('shackle', 'ਸ') == 'sa'
        assert rom('shackle', 'ਸਤਿ') == 'sati'

    def test_c_and_ch(self):
        # ਚ → c (not ch); ਛ → ch
        assert rom('shackle', 'ਚ') == 'ca'
        assert rom('shackle', 'ਛ') == 'cha'

    def test_retroflex_dots(self):
        assert rom('shackle', 'ਟ') == 'ṭa'
        assert rom('shackle', 'ਡ') == 'ḍa'
        assert rom('shackle', 'ਣ') == 'ṇa'
        assert rom('shackle', 'ੜ') == 'ṛa'

    def test_long_vowels_macron(self):
        assert rom('shackle', 'ਕਾ') == 'kā'
        assert rom('shackle', 'ਕੀ') == 'kī'
        assert rom('shackle', 'ਕੂ') == 'kū'

    def test_e_o_short(self):
        # ਏ → e, ਓ → o (no macron)
        assert rom('shackle', 'ਏਕ') == 'eka'
        assert rom('shackle', 'ਸੋ') == 'so'

    def test_conjunct_r_v(self):
        # §3a subjoined clusters (only -r common)
        assert rom('shackle', 'ਸ੍ਰਵਣੁ') == 'sravaṇu'
        assert rom('shackle', 'ਸ੍ਵਾਦੁ') == 'svādu'

    def test_doubling_via_addak(self):
        # §4 doubling; ਪੱਕਾ → pakkā
        assert rom('shackle', 'ਪੱਕਾ') == 'pakkā'


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


# --- #21: addak / nasals in any position ------------------------------------

MAP_DRIVEN = [s for s in __import__('gurmukhi_transliterate').SYSTEM_ORDER
              if s not in ('sttm', 'banidb_ipa', 'shabados')]   # dedicated engines


def _shape_cases():
    from gurmukhi_transliterate import SYSTEMS
    for sid in MAP_DRIVEN:
        m = SYSTEMS[sid]
        c, vd, vw = m.consonants, m.vowel_diacritics, m.vowels
        a = vw.get('ਅ') or 'a'
        cases = [
            # addak after a vowel sign
            ('ਸਿੱਖ', [c['ਸ'], vd['ਿ'], c['ਖ'], c['ਖ'], a]),
            # addak after an independent vowel
            ('ਇੱਕ', [vw['ਇ'], c['ਕ'], c['ਕ'], a]),
            # tippi after an independent vowel
            ('ਅੰਗ', [vw['ਅ'], m.nasal_by_class.get('velar', m.nasal_tippi), c['ਗ'], a]),
            # bindi after an independent vowel following a sign
            ('ਕਿਉਂ', [c['ਕ'], vd['ਿ'], vw['ਉ'], m.nasal_bindi]),
        ]
        for text, parts in cases:
            if None in parts:
                continue  # system has no value for one of the parts
            yield pytest.param(sid, text, ''.join(parts), id=f'{sid}-{text}')


class TestAddakAndNasalsAnywhere:
    @pytest.mark.parametrize('sid, text, expected', list(_shape_cases()))
    def test_marks_are_not_dropped(self, sid, text, expected):
        assert rom(sid, text) == expected

    @pytest.mark.parametrize('sid, text, expected', [
        ('dr_thind', 'ਸਿੱਖ', 'sikhkha'),
        ('shackle', 'ਇੱਕ', 'ikka'),
        ('dr_thind', 'ਅੰਗ', 'anga'),
        ('dr_thind', 'ਕਿਉਂ', 'kiun'),
        ('iast', 'ਆਂਖ', 'āṁkha'),
    ])
    def test_issue_rows(self, sid, text, expected):
        assert rom(sid, text) == expected

    def test_addak_after_nukta_letter_keeps_following_vowel(self):
        assert rom('dr_thind', 'ਜ਼ੱਮੀਨ') == 'zammeena'

    def test_precomposed_nukta_input_matches_decomposed(self):
        assert rom('iast', 'ਸ਼ਾ') == rom('iast', 'ਸ਼ਾ')

    def test_addak_at_end_does_not_crash(self):
        assert rom('dr_thind', 'ਕੱ') == 'ka'


# --- #22: no silent drops; subjoined forms ----------------------------------

class TestFallbacks:
    def report(self, sid, text):
        from gurmukhi_transliterate import GurmukhiRomanizer
        return GurmukhiRomanizer(sid).romanize_report(text)

    def test_letter_missing_from_system_uses_iso(self):
        r = self.report('iast', 'ਪੜ')            # IAST map has no ੜ
        assert r.text == 'paṛa'
        assert [(w.kind, w.char, w.position) for w in r.warnings] == [('fallback_iso', 'ੜ', 1)]

    def test_missing_nukta_letter_uses_base(self):
        r = self.report('sttm_legacy', 'ਲ਼')      # sttm_legacy has no ਲ਼
        assert r.text == 'la'
        assert [w.kind for w in r.warnings] == ['fallback_base']

    def test_missing_consonant_without_nukta(self):
        assert self.report('sacred_nitnem', 'ਙ').text == 'ṅa'

    def test_missing_independent_vowel(self):
        import dataclasses
        from gurmukhi_transliterate import GurmukhiRomanizer, SYSTEMS
        base = SYSTEMS['dr_thind']
        no_au = dataclasses.replace(base, id='no_au', vowels={k: v for k, v in base.vowels.items() if k != 'ਔ'})
        r = GurmukhiRomanizer(no_au).romanize_report('ਔ')
        assert r.text == 'au' and r.warnings[0].kind == 'fallback_iso'

    def test_missing_bindi_uses_tippi_value(self):
        r = self.report('gfs', 'ਨਾਂ')             # gfs defines no bindi
        assert r.text == rom('gfs', 'ਨਾ') + 'n'
        assert r.warnings[0].kind == 'fallback_nasal'

    def test_clean_text_has_no_warnings(self):
        assert self.report('sttm', 'ਸਤਿ ਨਾਮੁ').warnings == []

    def test_romanize_still_returns_str_and_logs(self, caplog):
        with caplog.at_level('WARNING', logger='gurmukhi_transliterate._core'):
            assert rom('iast', 'ਪੜ') == 'paṛa'
        assert 'ੜ' in caplog.text


class TestSubjoined:
    def test_gursevak_subscript(self):
        assert rom('gursevak', 'ਪ੍ਰੀਤਮ') == 'pᵣeetama'

    def test_undefined_subjoined_uses_consonant(self):
        # dr_sant_singh leaves ੍ਹ undefined → plain consonant value
        from gurmukhi_transliterate import SYSTEMS
        c = SYSTEMS['dr_sant_singh'].consonants
        assert rom('dr_sant_singh', 'ਪੜ੍ਹ') == c['ਪ'] + 'a' + c['ੜ'] + c['ਹ'] + 'a'


@pytest.mark.story('US-007', 'US-008')
class TestHomorganicNasals:
    """Shackle §5: tippi before a stop is written as that stop's class nasal."""

    @pytest.mark.parametrize('text, expected', [
        ('ਸੰਤ', 'santa'),
        ('ਸੰਕ', 'saṅka'),
        ('ਸੰਚ', 'sañca'),
        ('ਸੰਟ', 'saṇṭa'),
        ('ਸੰਪ', 'sampa'),
        ('ਕੰਮ', 'kamma'),
        ('ਸੰਸਾਰ', 'saṁsāra'),   # not before a stop: plain nasalisation
    ])
    def test_shackle(self, text, expected):
        assert rom('shackle', text) == expected

    def test_shackle_reverse_round_trip(self):
        from gurmukhi_transliterate.reverse import shackle_to_gurmukhi
        for w in ('ਸੰਤ', 'ਸੰਕ', 'ਸੰਚ', 'ਸੰਟ', 'ਸੰਪ'):
            assert shackle_to_gurmukhi(rom('shackle', w)) == w


class TestLabialNasalsByEvidence:
    """Per docs/research/16-romanized-gurmukhi/notes/nasal_conventions.md."""

    @pytest.mark.parametrize('sid', ['dr_thind', 'dr_sant_singh'])
    def test_labial_m(self, sid):
        assert rom(sid, 'ਕੰਮ') == 'kamma'
        assert rom(sid, 'ਸੰਤ') == 'santa'          # other classes keep n

    def test_ipa_full_class_table(self):
        assert [rom('ipa', w)[1:3] for w in ('ਸੰਕ', 'ਸੰਚ', 'ਸੰਟ', 'ਸੰਤ', 'ਸੰਪ')] == \
            ['əŋ', 'əɲ', 'əɳ', 'ən', 'əm']

    @pytest.mark.parametrize('sid, expected', [
        ('sttm_legacy', 'kanma'),       # iGurbani: kanm
        ('sacred_nitnem', 'kaṅma'),
    ])
    def test_fixed_nasal_systems_unchanged(self, sid, expected):
        assert rom(sid, 'ਕੰਮ') == expected

    def test_banidb_keeps_parenthesised_nasal_before_labials(self):
        assert rom('sttm', 'ਕੰਮ ॥') == 'ka(n)m ||'
