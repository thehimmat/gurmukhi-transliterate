import pytest

from gurmukhi_transliterate import lookup_informal, reverse_informal, reverse_words, to_gurmukhi
from gurmukhi_transliterate.informal import TERMS

pytestmark = pytest.mark.story('US-005')


class TestTable:
    def test_small(self):
        assert len(TERMS) < 100

    @pytest.mark.parametrize('spelling', ['Waheguru', 'Vaheguru', 'WAAHEGUROO', 'wahe-guru', 'Wahiguru'])
    def test_variants(self, spelling):
        assert lookup_informal(spelling) == 'ਵਾਹਿਗੁਰੂ'

    @pytest.mark.parametrize('spelling', ['Ik Onkar', 'Ek Ong Kaar', 'Ek Onkar', 'ikoankar'])
    def test_ik_oankaar(self, spelling):
        assert lookup_informal(spelling) == 'ੴ'

    def test_unknown(self):
        assert lookup_informal('pizza') is None
        assert lookup_informal('') is None


class TestPhrases:
    def test_longest_match_first(self):
        assert reverse_informal('Bole So Nihal Sat Sri Akal')[0] == 'ਬੋਲੇ ਸੋ ਨਿਹਾਲ ਸਤਿ ਸ੍ਰੀ ਅਕਾਲ'

    def test_punctuation_inside_phrase(self):
        out, missing = reverse_informal('Waheguru Ji Ka Khalsa, Waheguru Ji Ki Fateh!')
        assert out == 'ਵਾਹਿਗੁਰੂ ਜੀ ਕਾ ਖ਼ਾਲਸਾ ਵਾਹਿਗੁਰੂ ਜੀ ਕੀ ਫ਼ਤਿਹ' and missing == []

    def test_combinations(self):
        assert reverse_informal('Guru Nanak Dev Ji')[0] == 'ਗੁਰੂ ਨਾਨਕ ਦੇਵ ਜੀ'

    def test_missing_words_reported(self):
        out, missing = reverse_informal('Waheguru pizza')
        assert out is None and missing == ['pizza']


@pytest.mark.story('US-010')
class TestIntegration:
    def test_reverse_words_auto_picks_informal(self):
        r = reverse_words('Sat Sri Akal')
        assert (r.system, r.gurmukhi) == ('informal', 'ਸਤਿ ਸ੍ਰੀ ਅਕਾਲ')

    def test_reverse_words_explicit(self):
        assert reverse_words('Khalsa', system='informal').gurmukhi == 'ਖ਼ਾਲਸਾ'

    @pytest.mark.parametrize('text, expected', [
        ('Waheguru', 'ਵਾਹਿਗੁਰੂ'),
        ('Sat Sri Akal', 'ਸਤਿ ਸ੍ਰੀ ਅਕਾਲ'),
        ('Japji Sahib\nRehras Sahib', 'ਜਪੁਜੀ ਸਾਹਿਬ\nਰਹਿਰਾਸ ਸਾਹਿਬ'),
    ])
    def test_to_gurmukhi(self, text, expected):
        assert to_gurmukhi(text) == expected
