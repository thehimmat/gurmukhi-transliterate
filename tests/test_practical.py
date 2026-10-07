import pytest
from gurmukhi_transliterate import GurmukhiPractical

t = GurmukhiPractical.to_practical


class TestBasicConsonants:
    @pytest.mark.parametrize("gurmukhi,expected", [
        ('ਸ', 'sa'), ('ਹ', 'ha'), ('ਕ', 'ka'), ('ਖ', 'kha'),
        ('ਗ', 'ga'), ('ਘ', 'gha'), ('ਙ', 'nga'), ('ਚ', 'cha'),
        ('ਜ', 'ja'), ('ਨ', 'na'), ('ਪ', 'pa'), ('ਮ', 'ma'),
        ('ਰ', 'ra'), ('ਲ', 'la'), ('ਵ', 'va'),
    ])
    def test_consonant_with_inherent_a(self, gurmukhi, expected):
        assert t(gurmukhi) == expected


class TestVowelDiacritics:
    def test_long_a(self):
        assert t('ਕਾ') == 'kaa'

    def test_short_i(self):
        assert t('ਕਿ') == 'ki'

    def test_long_i(self):
        assert t('ਕੀ') == 'kee'

    def test_short_u(self):
        assert t('ਕੁ') == 'ku'

    def test_long_u(self):
        assert t('ਕੂ') == 'koo'

    def test_e(self):
        assert t('ਕੇ') == 'ke'

    def test_ai(self):
        assert t('ਕੈ') == 'kai'

    def test_o(self):
        assert t('ਕੋ') == 'ko'

    def test_au(self):
        assert t('ਕੌ') == 'kau'


class TestNasalization:
    def test_tippi_before_non_labial(self):
        # ਸਿੰਘ — tippi before velar ਘ → n; inherent 'a' retained on ਘ
        assert t('ਸਿੰਘ') == 'singha'

    def test_tippi_before_labial(self):
        # ਕੰਮ — tippi before labial ਮ → m; inherent 'a' on both consonants
        assert t('ਕੰਮ') == 'kamma'

    def test_bindi(self):
        assert t('ਨਾਂ') == 'naan'


class TestSpecialSymbols:
    def test_ik_onkar(self):
        assert t('ੴ') == 'ik oankaar'


class TestNumbers:
    def test_gurmukhi_digits(self):
        assert t('੧੨੩') == '123'


class TestWords:
    def test_waheguru(self):
        assert t('ਵਾਹਿਗੁਰੂ') == 'vaahiguroo'

    def test_satnam(self):
        assert t('ਸਤਿਨਾਮੁ') == 'satinaamu'


class TestIssue23:
    @pytest.mark.parametrize("gurmukhi,expected", [
        ('ਜ਼ਮੀਨ', 'zameena'),
        ('ਸ਼ਸ', 'shasa'),
        ('ਫ਼ਤਿਹ', 'fatiha'),
        ('ਗ਼ਰੀਬ', 'ġhareeba'),
    ])
    def test_nukta_letters_keep_their_own_values(self, gurmukhi, expected):
        assert t(gurmukhi) == expected

    def test_precomposed_nukta_input(self):
        assert t('ਸ਼ਸ') == 'shasa'

    @pytest.mark.parametrize("gurmukhi,expected", [
        ('ਪੱਕਾ', 'pakkaa'),
        ('ਕਿੱਤਾ', 'kittaa'),
        ('ਮੁੱਖ', 'mukkha'),     # aspirate geminates as k + kh
        ('ਇੱਕ', 'ikka'),
        ('ਸੱਚ', 'sachcha'),
    ])
    def test_addak(self, gurmukhi, expected):
        assert t(gurmukhi) == expected

    def test_final_schwa_same_at_end_and_before_space(self):
        assert t('ਸਿੰਘ') == 'singha'
        assert t('ਸਿੰਘ ਜੀ') == 'singha jee'
        assert t('ਸਿੰਘ ਜੀ', delete_schwa=True) == 'singh jee'

    @pytest.mark.parametrize("gurmukhi,expected", [
        ('ਅੰਮ੍ਰਿਤ', 'ammrita'),   # tippi before labial → m, wherever it sits
        ('ਅੰਗ', 'anga'),
        ('ਕਿਉਂ', 'kiun'),
    ])
    def test_nasals_after_vowels(self, gurmukhi, expected):
        assert t(gurmukhi) == expected

    def test_modifiers_match_iso(self):
        from gurmukhi_transliterate import GurmukhiISO15919
        assert GurmukhiPractical.MODIFIERS['ੰ'] == GurmukhiISO15919.MODIFIERS['ੰ'] == 'ṃ'
        assert GurmukhiPractical.MODIFIERS['ਂ'] == GurmukhiISO15919.MODIFIERS['ਂ'] == 'ṁ'
