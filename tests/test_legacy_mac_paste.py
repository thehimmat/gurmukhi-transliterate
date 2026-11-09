"""Legacy-font text copied out of a PDF on a Mac (#62).

macOS hands the clipboard a compatibility-normalised (NFKC) copy of a PDF's
text layer, which splits several font keys into other characters: Satluj's
``¨`` (॥) arrives as a space and a combining diaeresis, ``¼`` (ੱ) as ``1⁄4``,
``¹`` (ੁ) as the digit ``1``. The fixture is Brahm Kavach from the Nitnem
Sahib (Nangali) gutka, as pasted from Preview.
"""

import pathlib
import unicodedata

import pytest

from gurmukhi_transliterate import GurmukhiLegacy, conversion_report, identify_system

pytestmark = pytest.mark.story('US-003')

FIXTURES = pathlib.Path(__file__).parent / 'fixtures' / 'legacy'
PASTED = (FIXTURES / 'brahm_kavach_mac_paste.satluj.txt').read_text(encoding='utf-8').splitlines()
EXPECTED = (FIXTURES / 'brahm_kavach_mac_paste.unicode.txt').read_text(encoding='utf-8').splitlines()


def convert(text, encoding='satluj'):
    return GurmukhiLegacy.convert(text, encoding)


class TestFixture:
    def test_fixture_is_the_normalised_form(self):
        text = '\n'.join(PASTED)
        assert unicodedata.normalize('NFKC', text) == text
        assert '\u0308' in text and '\u2044' in text

    def test_lines_convert(self):
        assert len(PASTED) == len(EXPECTED)
        for pasted, expected in zip(PASTED, EXPECTED):
            result = convert(pasted)
            assert result.text == expected, pasted
            assert not result.warnings, pasted

    def test_whole_paste_detected_as_satluj(self):
        assert GurmukhiLegacy.detect_encoding('\n'.join(PASTED)) == 'satluj'

    def test_pasted_on_one_line(self):
        # a single-line input box joins the lines with spaces
        text = ' '.join(PASTED)
        assert GurmukhiLegacy.detect_encoding(text) == 'satluj'
        assert convert(text).text == ' '.join(EXPECTED)

    def test_report_converts_without_being_told_the_font(self):
        report = conversion_report('\n'.join(PASTED))
        assert report['encoding'] == report['converted_with'] == 'satluj'
        assert report['unicode'] == '\n'.join(EXPECTED)
        assert report['warnings'] == []


class TestSatlujByItsLetters:
    """Satluj keeps its letters on accented Latin-1 keys, which no language
    builds whole words from: that is enough to know it, with or without the
    words being Gurbani vocabulary (Brahm Kavach's compounds mostly aren't)."""

    def test_verses_alone(self):
        text = '\n'.join(PASTED[5:15])
        assert GurmukhiLegacy.detect_encoding(text) == 'satluj'
        assert conversion_report(text)['unicode'] == '\n'.join(EXPECTED[5:15])

    @pytest.mark.parametrize('n', range(len(PASTED)))
    def test_every_line_on_its_own(self, n):
        assert GurmukhiLegacy.detect_encoding(PASTED[n]) == 'satluj'
        assert conversion_report(PASTED[n])['unicode'] == EXPECTED[n]

    @pytest.mark.parametrize('text', ['òÅÇÔ×1ðÈ', 'òÅÇÔ×¹ðÈ', 'ÕðòÅÇð ÔËo íòÅéÆ', '√Ã∆ Ú≈«‘◊π» ‹∆ ’∆ ÎÂ‘ ®'])
    def test_a_word_or_two(self, text):
        assert GurmukhiLegacy.detect_encoding(text) == 'satluj'
        assert identify_system(text)[0]['system'] == 'legacy:satluj'

    def test_only_satluj_is_known_this_way(self):
        from gurmukhi_transliterate.legacy import _ACCENTED_LAYOUTS
        assert _ACCENTED_LAYOUTS == ('satluj',)

    @pytest.mark.parametrize('text, expected', [
        ('Â¶Õ Â¶Õ ÕÆ', 'ਏਕ ਏਕ ਕੀ'),            # keys Joy also has
        ('\x0cÃÌÆ ÜÅê¹ ÃÅÇÔì/41', '\x0cਸ੍ਰੀ ਜਾਪੁ ਸਾਹਿਬ/੪੧'),   # a page header, form feed and all
    ])
    def test_lines_other_layouts_or_punctuation_confused(self, text, expected):
        report = conversion_report(text)
        assert report['encoding'] == 'satluj'
        assert report['unicode'] == expected

    @pytest.mark.parametrize('text', [
        'vāhigurū jī kā ḵẖālsā', 'café déjà été à Paris', 'été à', 'ÉTÉ À ÎLE', 'Ñandú', 'ñ', 'è', 'señor año',
        'ʋaːɦɪɡʊruː', 'siq nwmu krqw purKu', 'waheguru',
    ])
    def test_accented_latin_is_not_satluj(self, text):
        assert GurmukhiLegacy.detect_encoding(text) != 'satluj'
        assert not any(r['system'] == 'legacy:satluj' for r in identify_system(text, top_n=20))


class TestSplitKeys:
    @pytest.mark.parametrize('pasted, expected', [
        ('þ \u0308', 'ਹੈ॥'),                    # ¨ → space + combining diaeresis
        ('Á1\u20444åzÆ', 'ਅੱਤ੍ਰੀ'),               # ¼ → 1\u20444
        ('òÅÇÔ×1ðÈ', 'ਵਾਹਿਗੁਰੂ'),                # ¹ → 1, after a consonant
        ('í×À1åÆ', 'ਭਗਉਤੀ'),                    # ... and after a vowel carrier
        ('Õ \u0304 ìåÆÃÅ', 'ਕੋ ਬਤੀਸਾ'),                # ¯ → space + combining macron
        ('ÔËo', 'ਹੈਂ'),                          # º → o
    ])
    def test_key(self, pasted, expected):
        result = convert(pasted)
        assert result.text == expected
        assert not result.warnings

    @pytest.mark.parametrize('pasted, expected', [
        ('êÅÇåÃÅÔÆ 10 \u0308', 'ਪਾਤਿਸਾਹੀ ੧੦॥'),   # a number stays a number
        ('ÁÕ¿êåÅ \u03086 \u03081 \u0308', 'ਅਕੰਪਤਾ॥੬॥੧॥'),
        ('îÔñÅ 1', 'ਮਹਲਾ ੧'),
        ('êÅÇåôÅÔÆ10 \u0308', 'ਪਾਤਿਸ਼ਾਹੀ੧੦॥'),          # ... even run on from the word
    ])
    def test_digits_that_are_numbers(self, pasted, expected):
        assert convert(pasted).text == expected

    @pytest.mark.parametrize('pasted, expected', [
        ('Ãî31ç', 'ਸਮੁੰਦ'),              # ³¹: aunkar typed after the tippi
        ('õ1ç', 'ਖ਼ੁਦ'),                  # after a letter with a nukta
        ('ê1\u204441åzË', 'ਪੁੱਤ੍ਰੈ'),         # after an adhak
        ('× \u03041Çì¿ç¶', 'ਗੋੁਬਿੰਦੇ'),        # after another vowel sign
        ('ì2Ý \u0304î', 'ਬ੍ਯੋਮ'),             # ², a zero-width spacer, leaves nothing
        ('ÃÚ1', 'ਸਚੁ'),                  # at the end of a word
    ])
    def test_signs_after_signs(self, pasted, expected):
        assert convert(pasted).text == expected

    @pytest.mark.parametrize('typed, expected', [
        ('çÃÕ1¨', 'ਦਸਕ੧॥'),
        ('êÅÇåôÅÔÆ10¨', 'ਪਾਤਿਸ਼ਾਹੀ੧੦॥'),
        ('ÃÚ¹ çÃÕ1', 'ਸਚੁ ਦਸਕ੧'),
    ])
    def test_text_that_was_never_split_keeps_its_numbers(self, typed, expected):
        # an unsplit ¨ or ¹ shows the text is as typed: a digit after a letter is a number
        assert convert(typed).text == expected

    def test_adhak_lines_are_not_read_as_mac_roman(self):
        # '\u2044' is a Mac Roman character; it must not send the line through that repair
        assert convert('ð1\u20444åêÅéÕÅ').text == 'ਰੱਤਪਾਨਕਾ'

    def test_warning_positions_index_the_pasted_text(self):
        pasted = 'þ \u0308 Q ÕòÚ'
        (warning,) = convert(pasted).warnings
        assert pasted[warning.position] == warning.char == 'Q'

    def test_unnormalised_text_is_untouched(self):
        assert convert('ÃÇå×¹ð').text == 'ਸਤਿਗੁਰ'

    def test_other_layouts_keep_their_spaces(self):
        assert convert('siq nwmu', 'anmollipi').text == 'ਸਤਿ ਨਾਮੁ'


class TestIdentify:
    def test_legacy_font_is_named_first(self):
        top = identify_system(' '.join(PASTED), include_english=True)[0]
        assert top['system'] == 'legacy:satluj'
        assert 'Satluj' in top['label'] and 'font' in top['label']
        assert top['confidence'] >= 0.6

    def test_clean_legacy_text_is_named_too(self):
        assert identify_system('ÃÇå×¹ð êÌÃÅÇç ¨ ÁÅÇç ÃÚ¹ Ü¹×ÅÇç ÃÚ¹ ¨')[0]['system'] == 'legacy:satluj'
        assert identify_system('siq nwmu krqw purKu inrBau inrvYru')[0]['system'] == 'legacy:anmollipi'

    @pytest.mark.parametrize('text', ['waheguru', 'vaahiguroo', 'kiv sachiaaraa hoieeaai',
                                      'The quick brown fox jumps over the lazy dog'])
    def test_romanised_and_english_are_not_called_fonts(self, text):
        assert not any(r['system'].startswith('legacy:') for r in identify_system(text, top_n=20))
