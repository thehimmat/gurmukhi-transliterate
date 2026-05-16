import unicodedata
import pytest
from gurmukhi_transliterate import GurmukhiLegacy


def to_unicode(text):
    return GurmukhiLegacy.to_unicode(text)


def nfc(s):
    return unicodedata.normalize('NFC', s)


class TestIkOnkar:
    def test_angle_brackets(self):
        assert to_unicode('<>') == 'ੴ'

    def test_latin_aa(self):
        assert to_unicode('ÅÆ') == 'ੴ'

    def test_inverted_exclamation(self):
        assert to_unicode('¡') == 'ੴ'


class TestNasalization:
    def test_tippi_M(self):
        assert to_unicode('isMG') == 'ਸਿੰਘ'

    def test_tippi_mu(self):
        assert to_unicode('isµG') == 'ਸਿੰਘ'

    def test_bindi_N(self):
        assert to_unicode('qwN') == 'ਤਾਂ'

    def test_bindi_hat(self):
        assert to_unicode('qwˆ') == 'ਤਾਂ'

    def test_precomposed_kanna_bindi(self):
        assert to_unicode('qW') == 'ਤਾਂ'


class TestVowelMarkAlternatives:
    def test_aunkar_u(self):
        assert to_unicode('guru') == 'ਗੁਰੁ'

    def test_aunkar_umlaut(self):
        assert to_unicode('gurü') == 'ਗੁਰੁ'

    def test_dulainkar_U(self):
        assert to_unicode('pUrw') == 'ਪੂਰਾ'

    def test_dulainkar_umlaut_u(self):
        assert to_unicode('p¨rw') == 'ਪੂਰਾ'


class TestAddak:
    def test_backtick(self):
        assert to_unicode('p`kw') == 'ਪੱਕਾ'

    def test_tilde(self):
        assert to_unicode('p~kw') == 'ਪੱਕਾ'


class TestUdaat:
    def test_backtick_N(self):
        assert to_unicode('h`N') == 'ਹਁ'

    def test_backtick_hat(self):
        assert to_unicode('h`ˆ') == 'ਹਁ'

    def test_tilde_N(self):
        assert to_unicode('h~N') == 'ਹਁ'

    def test_tilde_hat(self):
        assert to_unicode('h~ˆ') == 'ਹਁ'


class TestSubjoinedCharacters:
    def test_pair_haha(self):
        assert to_unicode('nwnHw') == 'ਨਾਨ੍ਹਾ'

    def test_pair_rara_R(self):
        assert to_unicode('pRym') == 'ਪ੍ਰੇਮ'

    def test_pair_vava(self):
        assert to_unicode('sÍwmI') == 'ਸ੍ਵਾਮੀ'

    def test_pair_rara_complex(self):
        assert to_unicode('pRBU') == 'ਪ੍ਰਭੂ'


class TestPersianCharacters:
    def test_khalsa(self):
        result = nfc(to_unicode('Kæwlsw'))
        assert result == nfc('ਖ਼ਾਲਸਾ')

    def test_shiv(self):
        assert to_unicode('iSv') == 'ਸ਼ਿਵ'

    def test_shanti(self):
        assert to_unicode('SWqI') == 'ਸ਼ਾਂਤੀ'


class TestVowelCombinations:
    def test_aatam(self):
        assert to_unicode('Awqm') == 'ਆਤਮ'

    def test_aisa(self):
        assert to_unicode('AYsw') == 'ਐਸਾ'

    def test_bhaee(self):
        assert to_unicode('BweI') == 'ਭਾਈ'

    def test_hoiaa(self):
        assert to_unicode('hoieAw') == 'ਹੋਇਆ'

    def test_oankaar(self):
        assert to_unicode('EAMkwr') == 'ਓਅੰਕਾਰ'


class TestComplexCombinations:
    def test_amrit(self):
        assert to_unicode('AMimRq') == 'ਅੰਮ੍ਰਿਤ'

    def test_praapat(self):
        assert to_unicode('pRwpiq') == 'ਪ੍ਰਾਪਤਿ'

    def test_noon_combo(self):
        assert to_unicode('ƒ') == 'ਨੂੰ'
