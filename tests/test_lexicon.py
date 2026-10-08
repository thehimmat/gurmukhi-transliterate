import unicodedata
import pytest
from gurmukhi_transliterate.lexicon import SOURCES, load_lexicon

pytestmark = pytest.mark.story('US-009')


@pytest.fixture(scope='module')
def lex():
    return load_lexicon()


class TestShippedLexicon:
    def test_sources(self):
        assert SOURCES == ('sggs', 'dasam', 'bhai_gurdas', 'bhai_nand_lal', 'other')

    def test_size_matches_research(self, lex):
        sggs = load_lexicon(['sggs'])
        assert 29_000 <= len(sggs) <= 30_500          # ~29.5k distinct SGGS words
        assert 390_000 <= sum(sggs.values()) <= 405_000  # ~398.5k running words
        assert len(lex) > len(sggs)

    def test_common_words(self, lex):
        assert lex['ਨਾਨਕ'] > 4000
        assert lex['ਹਰਿ'] > 8000

    def test_keys_are_nfc_and_clean(self, lex):
        for w in list(lex)[:5000]:
            assert unicodedata.normalize('NFC', w) == w
            assert all('਀' <= ch <= '੿' for ch in w), w
            assert not any(ch in '।॥੦੧੨੩੪੫੬੭੮੯' for ch in w), w

    @pytest.mark.parametrize('word', ['ਖ਼ਾਲਸਾ',         # precomposed ਖ਼
                                      'ਖ਼ਾਲਸਾ'])  # ਖ + ਼
    def test_nukta_words_found_with_nfc_lookup(self, lex, word):
        assert unicodedata.normalize('NFC', word) in lex

    def test_source_filter(self):
        bng = load_lexicon(['bhai_nand_lal'])
        assert bng and set(bng) - set(load_lexicon(['sggs']))  # largely Persian vocabulary

    def test_unknown_source_rejected(self):
        with pytest.raises(ValueError):
            load_lexicon(['nope'])

    def test_usable_with_corpus_matcher(self, lex):
        from gurmukhi_transliterate import CorpusMatcher
        assert 'ਨਾਨਕ' in CorpusMatcher(lex)
