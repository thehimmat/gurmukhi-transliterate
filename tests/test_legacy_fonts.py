"""Asees, Joy, AnandpurSahib, Satluj and SONY legacy fonts, encoding detection and font hints (#19)."""

import pathlib

import pytest

from gurmukhi_transliterate import GurmukhiLegacy, conversion_report
from gurmukhi_transliterate.legacy import ENCODINGS

FIXTURES = pathlib.Path(__file__).parent / 'fixtures' / 'legacy'
CASES = [('chandi_charitar', 'joy'), ('gur_sobha', 'asees'), ('gur_sobha_joy', 'joy'),
         ('zafarnama', 'anandpursahib'), ('nitnem_nangali', 'satluj'), ('gutka_nitnem', 'sony')]


def _pairs(name, encoding):
    legacy = (FIXTURES / f'{name}.{encoding}.txt').read_text(encoding='utf-8').splitlines()
    unicode = (FIXTURES / f'{name}.unicode.txt').read_text(encoding='utf-8').splitlines()
    assert len(legacy) == len(unicode)
    return list(zip(legacy, unicode))


def convert(text, encoding):
    return GurmukhiLegacy.convert(text, encoding).text


class TestFixtures:
    @pytest.mark.parametrize('name, encoding', CASES)
    def test_lines(self, name, encoding):
        for legacy, expected in _pairs(name, encoding):
            result = GurmukhiLegacy.convert(legacy, encoding)
            assert result.text == expected, legacy
            assert not result.warnings, legacy

    @pytest.mark.parametrize('name, encoding', CASES)
    def test_whole_text_detected(self, name, encoding):
        text = '\n'.join(l for l, _ in _pairs(name, encoding))
        # Asees and Joy share their letter keys; text without Joy's few
        # distinct keys may read as either.
        family = {'asees', 'joy'} if encoding in ('asees', 'joy') else {encoding}
        assert GurmukhiLegacy.detect_encoding(text) in family


class TestAsees:
    @pytest.mark.parametrize('legacy, expected', [
        ('uzvh', 'ਚੰਡੀ'),
        ('gzikph', 'ਪੰਜਾਬੀ'),
        ('fgqfE', 'ਪ੍ਰਿਥਿ'),          # sihari typed first, after the subjoined ਰ
        ('j?_', 'ਹ੍ਵੈ'),              # subjoined ਵ typed after the vowel sign
        ('d[qrk', 'ਦ੍ਰੁਗਾ'),
        ('n"o', 'ਔਰ'),                # ਅ + ੌ → ਔ
        ('T[gkfJ', 'ਉਪਾਇ'),           # ੳ + ੁ → ਉ, ੲ + ਿ → ਇ
        ('ekz', 'ਕਾਂ'),               # one nasal key: bindi after kanna
        ('ezs', 'ਕੰਤ'),
        ('n;a', 'ਅਸ਼'),               # nukta key
        (']17]', '॥17॥'),
    ])
    def test_words(self, legacy, expected):
        assert convert(legacy, 'asees') == expected


class TestJoy:
    @pytest.mark.parametrize('legacy, expected', [
        ('uzvh', 'ਚੰਡੀ'),
        ('j{`', 'ਹੂੰ'),               # ` is the nasal key: tippi after dulainkar
        ('ok`', 'ਰਾਂ'),               # ... bindi after kanna
        ('Bw;s\xa4:`', 'ਨਮਸਤ੍ਯੰ'),    # ¤ before ਯ is a virama in the older fonts
        ('dèth', 'ਦੇਵੀ'),             # è is lavan in the older fonts
        ('\xcbGk', 'ਪ੍ਰਭਾ'),           # a key carrying a whole conjunct
        ('f\xcbG', 'ਪ੍ਰਿਭ'),           # ... sihari still lands after it
        ('ozr..', 'ਰੰਗ॥'),
    ])
    def test_words(self, legacy, expected):
        assert convert(legacy, 'joy') == expected


class TestAnandpurSahib:
    @pytest.mark.parametrize('legacy, expected', [
        ('pµj;bI', 'ਪੰਜਾਬੀ'),          # the published example
        ('b<iSMdh', 'ਬਖ਼ਸ਼ਿੰਦਹ'),       # sihari typed first, nukta letters
        ('am"', 'ਅਮਾਂ'),               # " is kanna + bindi
        ("XI'", 'ਈਂ'),                 # ੲ + ੀ → ਈ; ' is bindi
        ('aESo', 'ਐਸ਼ੋ'),              # ਅ + ੈ → ਐ
        ('kPule', 'ਕਉਲੇ'),            # P is ੳ
        ('mohLmd', 'ਮੋਹੱਮਦ'),          # L is addak
        ('rOSn', 'ਰੌਸ਼ਨ'),
        ('AmdMd', 'ਆਮਦੰਦ'),
        ('_', 'ਓ'),
    ])
    def test_words(self, legacy, expected):
        assert convert(legacy, 'anandpursahib') == expected

    def test_unseen_keys_are_reported_not_guessed(self):
        # the Zafarnama never uses ਟ ਡ ਣ …, so their keys aren't mapped yet
        result = GurmukhiLegacy.convert('kT', 'anandpursahib')
        assert [w.char for w in result.warnings] == ['T']


class TestSatluj:
    @pytest.mark.parametrize('legacy, expected', [
        ('ý ÃÇå×¹ðêÌÃÅÇç¨', 'ੴ ਸਤਿਗੁਰਪ੍ਰਸਾਦਿ॥'),   # sihari typed first, subjoined ਰ
        ('ÃÌÆ Üê¹ ÜÆ ÃÅÇÔì', 'ਸ੍ਰੀ ਜਪੁ ਜੀ ਸਾਹਿਬ'),
        ('Ãî³¹Çç', 'ਸਮੁੰਦਿ'),                    # tippi typed before aunkar
        ('Ç´êÅ', 'ਕ੍ਰਿਪਾ'),                      # a key carrying a conjunct
        ('îÈó·', 'ਮੂੜ੍ਹ'),
        ('ÃÝÅî', 'ਸ੍ਯਾਮ'),
        ('ÇÂÃ|', 'ਇਸ਼'),                         # | is a nukta
        ('ÇÃ¼Îè¶', 'ਸਿੱਧੇ'),                     # Î is a zero-width spacer
        ('ÔËº', 'ਹੈਂ'),
        ('¨1¨', '॥੧॥'),
    ])
    def test_words(self, legacy, expected):
        assert convert(legacy, 'satluj') == expected


class TestSony:
    @pytest.mark.parametrize('legacy, expected', [
        ('O ldaepi f+ljds mm', 'ੴ ਸਤਿਗੁਰ ਪ੍ਰਸਾਦਿ ॥'),   # d is sihari, typed first
        ("Vq' liW wjv[ mm", 'ਨਮੋ ਸਰਬ ਕਾਲੇ ॥'),
        ('H[w', 'ਏਕ'),                           # H is ੲ
        ('ihjRp', 'ਰਹਾਉ'),                       # R is ੳ
        ('l:I[', 'ਸ੍ਵਯੇ'),
        ('d*fj', 'ਕ੍ਰਿਪਾ'),
        ('duV%J', 'ਜਿਨ੍ਹਾਂ'),
        ('y"fHg', 'ਚੌਪਈ'),
        ('LWs h;ji[', 'ਸ਼ਬਦ ਹਜ਼ਾਰੇ'),
        ('f+DFp', 'ਪ੍ਰਭੁ'),                      # D is a zero-width spacer
    ])
    def test_words(self, legacy, expected):
        assert convert(legacy, 'sony') == expected


class TestEncodingChoice:
    def test_encodings(self):
        assert ENCODINGS == ('anmollipi', 'asees', 'joy', 'anandpursahib', 'satluj', 'sony')

    def test_unknown_encoding(self):
        with pytest.raises(ValueError, match='asees'):
            GurmukhiLegacy.convert('x', 'drchatrik')

    def test_auto(self):
        result = GurmukhiLegacy.convert('s[w w/ok fJe gzE ubkt\'. ;[wfs d/j b\'rB ;wMkt\']18]', 'auto')
        assert result.encoding == 'asees'
        assert result.text == 'ਤੁਮ ਮੇਰਾ ਇਕ ਪੰਥ ਚਲਾਵੋ। ਸੁਮਤਿ ਦੇਹ ਲੋਗਨ ਸਮਝਾਵੋ॥18॥'

    def test_auto_keeps_anmollipi(self):
        assert GurmukhiLegacy.convert('siqnwmu', 'auto').encoding == 'anmollipi'

    @pytest.mark.parametrize('font, encoding', [
        ('CKPHAK+Asees', 'asees'), ('Joy', 'joy'), ('GurbaniAkharThick', 'anmollipi'),
        ('GLAJKC+AnandpurSahib', 'anandpursahib'), ('Satluj,Bold', 'satluj'), ('SatlujBold', 'satluj'),
        ('SONYBoldA', 'sony'), ('SONY-NormalItalicA', 'sony'), ('LORD-BoldA', 'anmollipi'),
        ('GOD-BoldA', 'anmollipi'), ('GurbaniWebThick', 'anmollipi'),
        ('CKPPLH+GurbaniLipi', 'anmollipi'), ('AnmolLipi Bold', 'anmollipi'), ('Prabhki', 'anmollipi'),
        ('MSTT31c5cb', None), ('TimesNewRoman', None),
    ])
    def test_encoding_for_font(self, font, encoding):
        assert GurmukhiLegacy.encoding_for_font(font) == encoding

    def test_report_with_font_hint(self):
        report = conversion_report('uzvh', font='Asees')
        assert report['converted_with'] == 'asees'
        assert report['unicode'] == 'ਚੰਡੀ'

    def test_report_with_encoding(self):
        assert conversion_report('uzvh', encoding='joy')['converted_with'] == 'joy'

    def test_report_detects(self):
        report = conversion_report("fsj py;h; eoh eoskoz. gqG{ pke fJw ej' fpukoz.")
        assert (report['encoding'], report['converted_with']) == ('asees', 'asees')
