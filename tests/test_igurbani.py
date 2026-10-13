"""Rules of iGurbani's spelling (sttm_legacy), from the examples in #48.

The engine is checked against igurbani.com's own output in
tests/test_conformance.py; these pin each rule on its own.
"""

import pytest

from gurmukhi_transliterate import GurmukhiRomanizer

pytestmark = pytest.mark.story('US-004')


def ig(text, **kw):
    return GurmukhiRomanizer('sttm_legacy').romanize(text, **kw)


@pytest.mark.parametrize('gurmukhi, want', [
    # final ਿ/ੁ dropped
    ('ਹਰਿ', 'har'), ('ਨਾਮੁ', 'naam'), ('ਗੁਰੁ', 'gur'),
    # medial schwas kept, final schwa dropped
    ('ਕਿਰਪਾ', 'kirapaa'), ('ਗੁਰਮੁਖਿ', 'guramukh'), ('ਨਾਨਕ', 'naanak'),
    # ਹ softens the vowel before it
    ('ਮਹਲਾ', 'mehalaa'), ('ਰਹਾਉ', 'rehaao'), ('ਨਹੀ', 'nehee'), ('ਸਿਮਰਹਿ', 'simarehi'),
    # ਉ/ਇ after a letter
    ('ਕਉ', 'ko'), ('ਹਉ', 'ho'), ('ਜੀਉ', 'jeeo'), ('ਗਉੜੀ', 'gourree'), ('ਹੋਇ', 'hoe'), ('ਆਇ', 'aae'),
    # subjoined ਰ carries the vowel; ਕ੍ਰਿ → kira
    ('ਪ੍ਰਭੁ', 'prabh'), ('ਕ੍ਰਿਪਾ', 'kirapaa'),
    # independent ਆ + bindi
    ('ਬਿਜੁਲੀਆਂ', 'bijuleeaaan'),
    ('ਮ꞉', 'ma'),
])
def test_word(gurmukhi, want):
    assert ig(gurmukhi) == want


def test_line_punctuation_dropped():
    assert ig('ਨਾਨਕ, ਜੇ ਕੋ ਆਪੁ ਗਣਾਇਦਾ; ਸੋ ਮੂਰਖੁ ਗਾਵਾਰੁ ॥੧॥') == 'naanak jae ko aap ganaaeidhaa so moorakh gaavaar ||1||'


def test_doubled_subjoined_written_once():
    assert ig('ਨ੍ਹ੍ਹ') == ig('ਨ੍ਹ')


def test_delete_schwa_has_no_effect():
    assert ig('ਗੁਰਮੁਖਿ ਨਾਨਕ', delete_schwa=True) == ig('ਗੁਰਮੁਖਿ ਨਾਨਕ') == 'guramukh naanak'
