import pytest
from gurmukhi_transliterate._tokens import tokenize


def kinds(text):
    return [(t.kind, t.text) for t in tokenize(text)]


class TestTokenize:
    def test_addak_after_vowel_sign(self):
        assert kinds('ਸਿੱਖ') == [('cons', 'ਸ'), ('sign', 'ਿ'), ('addak', 'ੱ'), ('cons', 'ਖ')]

    def test_nasal_after_independent_vowel(self):
        assert kinds('ਅੰਗ') == [('vowel', 'ਅ'), ('nasal', 'ੰ'), ('cons', 'ਗ')]

    def test_nukta_merges_into_consonant(self):
        assert kinds('ਜ਼ੱਮ') == [('cons', 'ਜ਼'), ('addak', 'ੱ'), ('cons', 'ਮ')]

    def test_precomposed_nukta_letter_is_normalised(self):
        assert kinds('ਸ਼') == [('cons', 'ਸ਼')]

    def test_virama_and_other(self):
        assert kinds('ਪ੍ਰ ॥੧') == [('cons', 'ਪ'), ('virama', '੍'), ('cons', 'ਰ'),
                                   ('other', ' '), ('other', '॥'), ('other', '੧')]

    def test_positions_index_the_normalised_text(self):
        toks = tokenize('ਕਿ ਜ਼ਰ')
        assert [t.pos for t in toks] == [0, 1, 2, 3, 5]
