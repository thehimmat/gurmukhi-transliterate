import pytest
from gurmukhi_transliterate import GurmukhiLegacy, EncodingGuess

detect = GurmukhiLegacy.detect_encoding

GURBANI_AKHAR = [
    'hvwey bMdgI Awvurd, dr vjUd mrw [ vgrnh, zUikæ cunIN Awmdn, nbUd mrw ]1]',
    'Awid scu jugwid scu ] hY BI scu nwnk hosI BI scu ]1]',
    'socY soic n hoveI jy socI lK vwr ]',
    '<> siqnwmu krqw purKu inrBau inrvYru',
    'gur pRswid',
    'AMimRq vylw',
]

ROMANISED = [
    'Hanūmān Nāṭak',
    'Chaṇḍī Charitar',
    'Srī Gur Sobhā, translated by Kharak Singh',
    'socai soci na hovaī je socī lakh vār',     # IAST-style
    'sochai soch na hovaee je sochee lakh vaar', # plain/practical
]

ENGLISH = [
    'The English translation of the text',
    'Sri Guru Granth Sahib',
    'This edition was printed by the Institute of Sikh Studies in 2014.',
    'Introduction',
    'Guru Nanak was born in 1469 at Talwandi, now known as Nankana Sahib.',
]


class TestDetectEncoding:
    @pytest.mark.parametrize('text', GURBANI_AKHAR)
    def test_gurbani_akhar(self, text):
        assert detect(text) == 'anmollipi'

    @pytest.mark.parametrize('text', ['ਸਤਿਗੁਰ ਪ੍ਰਸਾਦਿ', 'ੴ ਸਤਿ ਨਾਮੁ ਕਰਤਾ ਪੁਰਖੁ ॥੧॥'])
    def test_unicode(self, text):
        assert detect(text) == 'unicode'

    @pytest.mark.parametrize('text', ROMANISED + ENGLISH)
    def test_latin(self, text):
        assert detect(text) == 'latin'

    @pytest.mark.parametrize('text', ['', '   ', '\n\n', '123 ]1]', '*****'])
    def test_unknown_when_no_words(self, text):
        assert detect(text) == 'unknown'

    def test_mixed_text_uses_whole_text_majority(self):
        text = 'Japji\n' + '\n'.join(GURBANI_AKHAR)
        assert detect(text) == 'anmollipi'

    def test_returns_str(self):
        assert isinstance(detect('gur pRswid'), str)


class TestDetectLines:
    def test_one_guess_per_line(self):
        text = 'Hanūmān Nāṭak\n\nAwid scu jugwid scu ]\nਸਤਿਗੁਰ ਪ੍ਰਸਾਦਿ'
        guesses = GurmukhiLegacy.detect_lines(text)
        assert [g.label for g in guesses] == ['latin', 'unknown', 'anmollipi', 'unicode']
        assert len(guesses) == text.count('\n') + 1

    def test_guess_has_score_in_unit_range(self):
        (g,) = GurmukhiLegacy.detect_lines('gur pRswid')
        assert isinstance(g, EncodingGuess)
        assert 0.0 <= g.score <= 1.0

    def test_unknown_scores_zero(self):
        (g,) = GurmukhiLegacy.detect_lines('')
        assert (g.label, g.score) == ('unknown', 0.0)


class TestWordValidity:
    """The structural rules the detector relies on."""

    @pytest.mark.parametrize('word', ['aus', 'Ehu', 'hoieAw', 'ieku', 'eyk', 'BweI', 'ikæsmq', 'b-Xwd', 'siqnwmu'])
    def test_valid_legacy_words(self, word):
        assert GurmukhiLegacy._is_plausible_legacy_word(word)

    @pytest.mark.parametrize('word', [
        'cat',    # oora (a) not followed by u/U/o
        'the',    # iri (e) with no vowel sign
        'of',     # word starts with a dependent vowel sign (hora)
        'with',   # starts with kanna
        'book',   # doubled vowel sign
        'Hanuman',  # starts with a subjoined letter
    ])
    def test_invalid_legacy_words(self, word):
        assert not GurmukhiLegacy._is_plausible_legacy_word(word)


class TestCombinationKeys:
    """Single-key entries of SPECIAL_COMBINATIONS (e.g. W = ਾਂ) are legacy keys too."""

    @pytest.mark.parametrize('text', [
        'nwmu inrMjnu aucrW piq isau Gir jWeI ]',   # found by tools/eval.py
        'vIhW dY vrqwrY EeI [10[',
    ])
    def test_kanna_bindi_W(self, text):
        assert detect(text) == 'anmollipi'
