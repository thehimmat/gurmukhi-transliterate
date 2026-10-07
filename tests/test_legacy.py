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


# --- Issue #14 -------------------------------------------------------------

NUKTA = '਼'
SIHARI = 'ਿ'


class TestSihariWithNuktaCombinations:
    """Sihari must land after the whole consonant cluster: base, nukta, subjoined."""

    @pytest.mark.parametrize('legacy, expected', [
        ('ikæsmq', 'ਕ਼ਿਸਮਤ'),          # ਕ਼ਿਸਮਤ
        ('iKæAwl', 'ਖ਼ਿਆਲ'),                # ਖ਼ਿਆਲ
        ('ijækr kr', 'ਜ਼ਿਕਰ ਕਰ'),  # ਜ਼ਿਕਰ ਕਰ
        ('zUikæ cunIN',                                              # ਜ਼ੂਕ਼ਿ ਚੁਨੀਂ
         'ਜ਼ੂਕ਼ਿ ਚੁਨੀਂ'),
    ])
    def test_issue_rows(self, legacy, expected):
        assert to_unicode(legacy) == expected

    def test_code_point_order_is_consonant_nukta_sihari(self):
        assert to_unicode('ikæ') == 'ਕ' + NUKTA + SIHARI

    def test_nukta_combo_with_subjoined(self):
        # ਕ਼੍ਰਿਪਾ: cluster is ਕ ਼ ੍ਰ, then sihari
        assert to_unicode('ikæRpw') == 'ਕ਼੍ਰਿਪਾ'

    def test_standalone_nukta_key_is_part_of_cluster(self):
        # 'b' + 'æ' has no SPECIAL_COMBINATIONS entry
        assert to_unicode('ibæ') == 'ਬ' + NUKTA + SIHARI

    def test_sihari_never_crosses_word_boundary(self):
        out = to_unicode('ki kr')
        assert out.split(' ')[1] == 'ਕਰ'


class TestOrphanSihari:
    def test_sihari_at_end_of_input_attaches_to_last_consonant(self):
        result = GurmukhiLegacy.convert('ki')
        assert result.text == 'ਕ' + SIHARI
        assert [w.kind for w in result.warnings] == ['orphan_sihari']
        assert result.warnings[0].position == 1

    def test_sihari_before_space_stays_in_its_word(self):
        result = GurmukhiLegacy.convert('kri kr')
        assert result.text == 'ਕਰ' + SIHARI + ' ਕਰ'
        assert [w.kind for w in result.warnings] == ['orphan_sihari']

    def test_sihari_with_no_consonant_in_word_is_kept_in_place(self):
        result = GurmukhiLegacy.convert('i kr')
        assert result.text == SIHARI + ' ਕਰ'
        assert [w.kind for w in result.warnings] == ['orphan_sihari']

    def test_sihari_never_attaches_to_digit_or_punctuation(self):
        result = GurmukhiLegacy.convert('ki1')
        assert result.text == 'ਕ' + SIHARI + '੧'


class TestPunctuationPassthrough:
    @pytest.mark.parametrize('legacy, expected', [
        ('b-Xwd', 'ਬ-ਯਾਦ'),
        ('ik: dr', 'ਕਿ: ਦਰ'),
        ('ic: kunM`d ?', 'ਚਿ: ਕੁਨੰੱਦ ?'),
        ('(Ehu)', '(ਓਹੁ)'),
        ('dIno dunIAw, dr', 'ਦੀਨੋ ਦੁਨੀਆ, ਦਰ'),
        ('eh! [1[ *****', 'ੲਹ! ।੧। *****'),
    ])
    def test_issue_rows(self, legacy, expected):
        assert to_unicode(legacy) == expected

    @pytest.mark.parametrize('ch', list(',:;-?!()\'".*\t'))
    def test_known_punctuation_passes_through_without_warning(self, ch):
        result = GurmukhiLegacy.convert(f'k{ch}k')
        assert result.text == f'ਕ{ch}ਕ'
        assert result.warnings == []


class TestUnmappedCharacters:
    def test_unmapped_char_is_kept_and_warned(self):
        result = GurmukhiLegacy.convert('kèk')
        assert result.text == 'ਕèਕ'
        assert len(result.warnings) == 1
        w = result.warnings[0]
        assert (w.kind, w.char, w.position) == ('unmapped', 'è', 1)

    def test_to_unicode_never_drops_unmapped(self):
        assert to_unicode('kèk') == 'ਕèਕ'

    def test_to_unicode_logs_warnings(self, caplog):
        with caplog.at_level('WARNING', logger='gurmukhi_transliterate.legacy'):
            to_unicode('kèk')
        assert 'è' in caplog.text

    def test_convert_result_on_empty_input(self):
        result = GurmukhiLegacy.convert('')
        assert (result.text, result.warnings) == ('', [])


class TestLineStructure:
    def test_single_newlines_preserved(self):
        assert to_unicode('kr\nkr\n\nkr') == 'ਕਰ\nਕਰ\n\nਕਰ'

    def test_line_count_matches_input(self):
        src = '\nkr\n\n\nkr  \n'
        assert to_unicode(src).count('\n') == src.count('\n')

    def test_surrounding_whitespace_not_stripped(self):
        assert to_unicode('  kr ') == '  ਕਰ '

    def test_crlf_preserved(self):
        assert to_unicode('kr\r\nkr') == 'ਕਰ\r\nਕਰ'


class TestNuktaNormalisation:
    """Nukta letters come out as base + U+0A3C, never the precomposed form."""

    @pytest.mark.parametrize('legacy', ['S', 'z', 'Z', '^', '&', 'L', 'sæ', 'Kæ', 'gæ', 'jæ', 'Pæ', 'læ'])
    def test_no_precomposed_nukta_letters(self, legacy):
        out = to_unicode(legacy)
        assert len(out) == 2 and out[1] == NUKTA
        assert not any(c in out for c in 'ਲ਼ਸ਼ਖ਼ਗ਼ਜ਼ਫ਼')


class TestConversionReport:
    def test_shape(self):
        from gurmukhi_transliterate import conversion_report
        report = conversion_report('Introduction\nkèk')
        assert report['unicode'] == GurmukhiLegacy.to_unicode('Introduction\nkèk')
        assert report['encoding'] in {'unicode', 'anmollipi', 'latin', 'unknown'}
        assert [line['label'] for line in report['lines']] == ['latin', 'latin']
        assert all(0.0 <= line['score'] <= 1.0 for line in report['lines'])
        assert {'position': 14, 'char': 'è', 'kind': 'unmapped'}.items() <= report['warnings'][-1].items()

    def test_json_serialisable(self):
        import json
        from gurmukhi_transliterate import conversion_report
        json.dumps(conversion_report('ki b-Xwd'))

    def test_empty(self):
        from gurmukhi_transliterate import conversion_report
        assert conversion_report('') == {'unicode': '', 'encoding': 'unknown', 'converted_with': 'anmollipi',
                                         'lines': [{'label': 'unknown', 'score': 0.0}],
                                         'warnings': []}
