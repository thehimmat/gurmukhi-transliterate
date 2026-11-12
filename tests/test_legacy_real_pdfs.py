"""Regressions found by converting text layers of real legacy-font PDFs.

Each raw string was copied from a PDF's text layer (PyMuPDF), and each
expected value was checked against a rendering of that PDF page.
"""
import pytest

from gurmukhi_transliterate import GurmukhiLegacy


def convert(text, encoding):
    return GurmukhiLegacy.convert(text, encoding)


class TestAnmolLipiKeys:
    @pytest.mark.parametrize('legacy, expected', [
        # '@' draws pairin haha under the letter; Shabad OS / BaniDB encode it as ੑ
        ('isK miq sB buiD qum@wrI', 'ਸਿਖ ਮਤਿ ਸਭ ਬੁਧਿ ਤੁਮੑਾਰੀ'),   # LORD-BoldA gutka
        ('ismirE nwih kn@weI', 'ਸਿਮਰਿਓ ਨਾਹਿ ਕਨੑਾਈ'),           # GurbaniAkharHeavy
        ('ijih ijih hir ko nwmu sm@wir', 'ਜਿਹਿ ਜਿਹਿ ਹਰਿ ਕੋ ਨਾਮੁ ਸਮੑਾਰਿ'),
    ])
    def test_at_sign_is_pairin_haha(self, legacy, expected):
        r = convert(legacy, 'anmollipi')
        assert r.text == expected
        assert not r.warnings

    @pytest.mark.parametrize('legacy, expected', [
        ('suixAY AMØDy pwvih rwhu ]', 'ਸੁਣਿਐ ਅੰਧੇ ਪਾਵਹਿ ਰਾਹੁ ॥'),
        ('mMØny kI giq khI n jwie ]', 'ਮੰਨੇ ਕੀ ਗਤਿ ਕਹੀ ਨ ਜਾਇ ॥'),
    ])
    def test_O_slash_is_an_invisible_spacer(self, legacy, expected):
        r = convert(legacy, 'anmollipi')
        assert r.text == expected
        assert not r.warnings

    def test_greek_mu_is_tippi_like_micro_sign(self):
        # PDFs give U+03BC for the font's µ (U+00B5) key
        assert convert('jIA jμq', 'anmollipi').text == 'ਜੀਅ ਜੰਤ'


class TestSonyKeys:
    def test_backslash_and_bar_are_brackets(self):
        r = convert('\\3|', 'sony')
        assert r.text == '(੩)'
        assert not r.warnings


class TestOverlaidSigns:
    """Typists overlay two glyphs that look like one sign; Unicode has one."""

    @pytest.mark.parametrize('legacy, encoding, expected', [
        ('pzd[{e', 'asees', 'ਬੰਦੂਕ'),        # aunkar + dulainkar drawn as dulainkar
        ('B[{z', 'asees', 'ਨੂੰ'),
        ('ÔËºÍ', 'satluj', 'ਹੈਂ'),            # two bindi keys, one bindi on the page
        ('hngbJ@', 'sony', 'ਹਠੀਆਂ'),          # ਾਂ key plus a bindi key
    ])
    def test_overlaid_signs_merge(self, legacy, encoding, expected):
        assert convert(legacy, encoding).text == expected


class TestSatlujMacRoman:
    """PDFs made on a Mac decode Satluj's bytes as Mac Roman ('√' for byte 0xC3)."""

    @pytest.mark.parametrize('legacy, expected', [
        ('˝ √«Â◊π ÍÃ√≈«Á ®', 'ੴ ਸਤਿਗੁਰ ਪ੍ਰਸਾਦਿ ॥'),
        ('√Ã∆ Ú≈«‘◊π» ‹∆ ’∆ ÎÂ‘ ®', 'ਸ੍ਰੀ ਵਾਹਿਗੁਰੂ ਜੀ ਕੀ ਫਤਹ ॥'),
    ])
    def test_mac_roman_text_layer(self, legacy, expected):
        r = convert(legacy, 'satluj')
        assert r.text == expected
        assert not r.warnings

    def test_windows_text_layer_unchanged(self):
        assert convert('ÃÇå×¹ð', 'satluj').text == 'ਸਤਿਗੁਰ'


class TestDetection:
    @pytest.mark.parametrize('legacy', [
        'nE fB;[`G i[X eEB`',          # Joy's ` is tippi; in Asees it is '!'
        "Bw' yr dr` Mwk Mw pkV`.",
    ])
    def test_joy_beats_asees_when_asees_leaves_punctuation_in_words(self, legacy):
        assert GurmukhiLegacy.detect_encoding(legacy) == 'joy'

    @pytest.mark.parametrize('text', [
        'KE CHALAAK DAST AST CHABAK RAKEB',
        'SHAHAN-SHAH RA BANDEH-E CHAAKAR-AM',
        'HAR AAN KAS KI KAUL-E KORAAN AAYAD-ASH',
    ])
    def test_all_caps_romanisation_is_latin(self, text):
        assert GurmukhiLegacy.detect_encoding(text) == 'latin'


class TestIkOnkar:
    def test_lone_less_than_is_whole_ik_onkar_in_gurbanilipi(self):
        # GurbaniLipi draws the whole ੴ on '<' (Vaar Bhagauti PDF, p. 1)
        r = convert('< siqgurpRswid ]', 'anmollipi')
        assert r.text == 'ੴ ਸਤਿਗੁਰਪ੍ਰਸਾਦਿ ॥'

    def test_two_part_ik_onkar_still_one_sign(self):
        assert convert('<> siqgur pRswid', 'anmollipi').text == 'ੴ ਸਤਿਗੁਰ ਪ੍ਰਸਾਦਿ'
