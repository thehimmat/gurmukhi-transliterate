import pytest

from gurmukhi_transliterate import (
    GurmukhiISO15919, GurmukhiPractical, GurmukhiRomanizer, SYSTEM_ORDER,
    UnableToReverse, reverse_words, to_gurmukhi,
)

ALL_SYSTEMS = ['iso15919', 'practical'] + SYSTEM_ORDER
WORDS = ['ਨਾਨਕ', 'ਸਤਿਗੁਰ', 'ਹਰਿ', 'ਨਾਮੁ', 'ਪ੍ਰਭ', 'ਸਿੱਖ', 'ਅੰਮ੍ਰਿਤੁ']


def forward(system, text, delete_schwa=False):
    if system == 'iso15919':
        return GurmukhiISO15919.to_phonetic(text, delete_schwa=delete_schwa)
    if system == 'practical':
        return GurmukhiPractical.to_practical(text, delete_schwa=delete_schwa)
    return GurmukhiRomanizer(system).romanize(text, delete_schwa=delete_schwa)


class TestRoundTrip:
    @pytest.mark.parametrize('system', ALL_SYSTEMS)
    @pytest.mark.parametrize('delete_schwa', [False, True])
    def test_lexicon_words_come_back(self, system, delete_schwa):
        for w in WORDS:
            r = reverse_words(forward(system, w, delete_schwa), system=system)
            assert w in [c for c, _ in r.words[0].candidates], (system, w, r.words[0])


class TestResult:
    def test_best_first_by_frequency(self):
        r = reverse_words('naanak', system='sttm')
        assert r.gurmukhi == 'ਨਾਨਕ'
        counts = [n for _, n in r.words[0].candidates]
        assert counts == sorted(counts, reverse=True)

    def test_case_insensitive_fallback(self):
        assert reverse_words('Naanak', system='sttm').gurmukhi == 'ਨਾਨਕ'

    def test_punctuation_and_numbers(self):
        # real BaniDB drops the final sihari: ਹਰਿ → har (ਹਰਿ outranks ਹਰ by frequency)
        assert reverse_words('har har ||1||', system='sttm').gurmukhi == 'ਹਰਿ ਹਰਿ ॥੧॥'

    def test_banidb_parenthesised_nasal(self):
        r = reverse_words('a(n)mrit', system='sttm')
        assert 'ਅੰਮ੍ਰਿਤੁ' in [c for c, _ in r.words[0].candidates]

    def test_banidb_standalone_word_form(self):
        # a word on its own keeps its final vowel in BaniDB: ਨਾਮੁ → naamu
        assert reverse_words('naamu', system='sttm').gurmukhi == 'ਨਾਮੁ'

    def test_ik_oankaar(self):
        assert reverse_words('ik oankaar', system='sttm').gurmukhi == 'ੴ'

    def test_missing_word_reported(self):
        r = reverse_words('naanak xyzzyq', system='sttm')
        assert r.missing == ['xyzzyq'] and r.gurmukhi is None

    def test_unknown_system(self):
        with pytest.raises(ValueError):
            reverse_words('naanak', system='nope')


class TestAutoSelect:
    @pytest.mark.parametrize('system', ['iast', 'sttm', 'iso15919', 'banidb_ipa'])
    def test_picks_a_system_that_explains_the_input(self, system):
        roman = forward(system, 'ਸਤਿਗੁਰ ਪ੍ਰਸਾਦਿ ਹਰਿ ਨਾਮੁ')
        r = reverse_words(roman)
        assert r.gurmukhi == 'ਸਤਿਗੁਰ ਪ੍ਰਸਾਦਿ ਹਰਿ ਨਾਮੁ', (roman, r.system, r.missing)


class TestToGurmukhiFallback:
    def test_word_outside_any_verse(self):
        assert to_gurmukhi('naanak') == 'ਨਾਨਕ'

    def test_verse_still_preferred(self):
        assert to_gurmukhi('hukam rajaiee chalanaa naanak likhiaa naal') == \
            'ਹੁਕਮਿ ਰਜਾਈ ਚਲਣਾ ਨਾਨਕ ਲਿਖਿਆ ਨਾਲਿ ॥੧॥'

    def test_unknown_word_raises_and_names_it(self):
        with pytest.raises(UnableToReverse, match='xyzzyq'):
            to_gurmukhi('naanak xyzzyq')

    def test_english_refused_up_front(self):
        with pytest.raises(UnableToReverse, match='English'):
            to_gurmukhi('The English translation of the text')


class TestRankedAutoSelect:
    LINE = 'ਕਿਵ ਸਚਿਆਰਾ ਹੋਈਐ ਕਿਵ ਕੂੜੈ ਤੁਟੈ ਪਾਲਿ'

    @pytest.mark.parametrize('system', ALL_SYSTEMS)
    def test_identified_system_is_used(self, system):
        roman = forward(system, self.LINE)
        r = reverse_words(roman)
        assert not r.missing
        # systems that write this line identically are indistinguishable
        assert forward(r.system, self.LINE) == roman, (system, r.system)
