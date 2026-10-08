import pytest
from gurmukhi_transliterate import GurmukhiISO15919

pytestmark = pytest.mark.story('US-001')

t = GurmukhiISO15919.to_phonetic


class TestNasalization:
    def test_tippi_before_consonant(self):
        assert t('ਹਿੰਮਤ') == 'hiṃmata'

    def test_tippi_mid_word(self):
        assert t('ਸਿੰਘ') == 'siṃgha'

    def test_tippi_short_vowel(self):
        assert t('ਕੰਮ') == 'kaṃma'

    def test_tippi_with_conjunct(self):
        assert t('ਅੰਮ੍ਰਿਤ') == 'aṃmrita'

    def test_bindi_after_long_vowel(self):
        assert t('ਸਾਂਝਾ') == 'sāṁjhā'

    def test_bindi_word_final(self):
        assert t('ਨਾਂ') == 'nāṁ'

    def test_bindi_after_diphthong(self):
        assert t('ਮੈਂ') == 'maiṁ'

    def test_bindi_vowel_sequence(self):
        assert t('ਸਿਉਂ') == 'siuṁ'

    def test_bindi_long_vowel_sequence(self):
        assert t('ਨਾਉਂ') == 'nāuṁ'


class TestVowelSequences:
    def test_long_i_sequence(self):
        assert t('ਭਾਈ') == 'bhāī'

    def test_diphthong_au(self):
        assert t('ਕੌਰ') == 'kaura'

    def test_short_vowel_sequence(self):
        assert t('ਸਿਉ') == 'siu'

    def test_long_a_plus_u(self):
        assert t('ਭਾਉ') == 'bhāu'

    def test_long_vowel_sequence_with_bindi(self):
        assert t('ਆਈਆਂ') == 'āīāṁ'


class TestConjuncts:
    def test_pair_rara(self):
        assert t('ਪ੍ਰੇਮ') == 'prēma'

    def test_pair_rara_long_vowel(self):
        assert t('ਸ੍ਰੀ') == 'srī'

    def test_pair_rara_short_vowel(self):
        assert t('ਕ੍ਰਿਪਾ') == 'kripā'

    def test_pair_vava(self):
        assert t('ਸ੍ਵਾਮੀ') == 'svāmī'


class TestGemination:
    def test_addak_k(self):
        assert t('ਪੱਕਾ') == 'pakkā'

    def test_addak_l(self):
        assert t('ਚੱਲਣਾ') == 'callaṇā'

    def test_addak_c(self):
        assert t('ਕੱਚਾ') == 'kaccā'

    def test_addak_t(self):
        assert t('ਕਿੱਤਾ') == 'kittā'

    def test_addak_t_medial(self):
        assert t('ਪੁੱਤਰ') == 'puttara'

    def test_addak_d(self):
        assert t('ਅੱਦਕ') == 'addaka'

    def test_addak_aspirated(self):
        assert t('ਮਿੱਠਾ') == 'miṭṭhā'


class TestConsonants:
    @pytest.mark.parametrize("gurmukhi,expected", [
        ('ਸ', 'sa'), ('ਹ', 'ha'), ('ਕ', 'ka'), ('ਖ', 'kha'),
        ('ਗ', 'ga'), ('ਘ', 'gha'), ('ਙ', 'ṅa'), ('ਚ', 'ca'),
        ('ਛ', 'cha'), ('ਜ', 'ja'), ('ਝ', 'jha'), ('ਞ', 'ña'),
        ('ਟ', 'ṭa'), ('ਠ', 'ṭha'), ('ਡ', 'ḍa'), ('ਢ', 'ḍha'),
        ('ਣ', 'ṇa'), ('ਤ', 'ta'), ('ਥ', 'tha'), ('ਦ', 'da'),
        ('ਧ', 'dha'), ('ਨ', 'na'), ('ਪ', 'pa'), ('ਫ', 'pha'),
        ('ਬ', 'ba'), ('ਭ', 'bha'), ('ਮ', 'ma'), ('ਯ', 'ya'),
        ('ਰ', 'ra'), ('ਲ', 'la'), ('ਵ', 'va'), ('ੜ', 'ṛa'),
    ])
    def test_consonant_with_inherent_a(self, gurmukhi, expected):
        assert t(gurmukhi) == expected

    @pytest.mark.parametrize("gurmukhi,expected", [
        ('ਜ਼', 'za'), ('ਫ਼', 'fa'), ('ਸ਼', 'śa'),
    ])
    def test_persian_consonants(self, gurmukhi, expected):
        assert t(gurmukhi) == expected


class TestVowels:
    @pytest.mark.parametrize("gurmukhi,expected", [
        ('ਅ', 'a'), ('ਆ', 'ā'), ('ਇ', 'i'), ('ਈ', 'ī'),
        ('ਉ', 'u'), ('ਊ', 'ū'), ('ਏ', 'ē'), ('ਐ', 'ai'),
        ('ਓ', 'ō'), ('ਔ', 'au'),
    ])
    def test_independent_vowels(self, gurmukhi, expected):
        assert t(gurmukhi) == expected


class TestIssue20:
    @pytest.mark.parametrize('gurmukhi', ['ਸਿੱਖ', 'ਕੱ', 'ਸਿੱਖ ਜੀ', 'ਮੁੱਖ', 'ਸੱਚ', 'ਹੱਥ', 'ਲੱਖ'])
    def test_final_addak_cluster_does_not_crash(self, gurmukhi):
        t(gurmukhi)

    def test_sikh(self):
        assert t('ਸਿੱਖ') == 'sikkha'

    @pytest.mark.parametrize('gurmukhi, expected', [('ਸੱਚ', 'sacca'), ('ਹੱਥ', 'hattha')])
    def test_final_geminate_after_consonant(self, gurmukhi, expected):
        assert t(gurmukhi) == expected
        assert t(gurmukhi, delete_schwa=True) == expected[:-1]

    def test_comparison_table_on_sikh(self):
        from gurmukhi_transliterate import comparison_table
        assert comparison_table('ਸਿੱਖ')['iso15919'] == 'sikkha'

    @pytest.mark.parametrize('gurmukhi, expected', [
        ('ਜ਼ੱਮੀਨ', 'zammīna'),
        ('ਜ਼ੰਮੀਨ', 'zaṃmīna'),
        ('ਜ਼ਮੀਨ', 'zamīna'),
        ('ਕਂ', 'kaṁ'),
    ])
    def test_marks_around_nukta_letters(self, gurmukhi, expected):
        assert t(gurmukhi) == expected

    def test_no_collisions_between_nukta_variants(self):
        outs = {t(w) for w in ('ਜ਼ੱਮੀਨ', 'ਜ਼ੰਮੀਨ', 'ਜ਼ਮੀਨ')}
        assert len(outs) == 3
