"""
Shabad OS English transliteration (as produced by gurmukhi-utils toEnglish).

A clean-room reimplementation: the rules here were derived only from the
library's output on corpus lines, never from its (GPL-3.0) source code. It is
checked byte for byte against that output in tests/test_conformance.py.

    GurmukhiShabadOS.to_english('ਕਿਵ ਸਚਿਆਰਾ ਹੋਈਐ ਕਿਵ ਕੂੜੈ ਤੁਟੈ ਪਾਲਿ ॥')
    # 'kiv sachiaaraa hoeeai kiv koorrai tuttai paal |'
"""

from __future__ import annotations

import re

from ._tokens import TIPPI, normalize, tokenize

CONSONANTS = {
    'ਕ': 'k', 'ਖ': 'kh', 'ਗ': 'g', 'ਘ': 'gh', 'ਙ': 'ng',
    'ਚ': 'ch', 'ਛ': 'chh', 'ਜ': 'j', 'ਝ': 'jh', 'ਞ': 'ny',
    'ਟ': 'tt', 'ਠ': 'tth', 'ਡ': 'dd', 'ਢ': 'dt', 'ਣ': 'n',
    'ਤ': 't', 'ਥ': 'th', 'ਦ': 'd', 'ਧ': 'dh', 'ਨ': 'n',
    'ਪ': 'p', 'ਫ': 'f', 'ਬ': 'b', 'ਭ': 'bh', 'ਮ': 'm',
    'ਯ': 'y', 'ਰ': 'r', 'ਲ': 'l', 'ਵ': 'v', 'ੜ': 'rr',
    'ਸ': 's', 'ਹ': 'h',
    'ਸ਼': 'sh', 'ਖ਼': 'kh', 'ਗ਼': 'g', 'ਜ਼': 'z', 'ਫ਼': 'f', 'ਲ਼': 'l', 'ਕ਼': 'k',
}
SIGNS = {'ਾ': 'aa', 'ਿ': 'i', 'ੀ': 'ee', 'ੁ': 'u', 'ੂ': 'oo', 'ੇ': 'e', 'ੈ': 'ai', 'ੋ': 'o', 'ੌ': 'au'}
VOWELS = {'ਅ': 'a', 'ਆ': 'aa', 'ਇ': 'i', 'ਈ': 'ee', 'ਉ': 'u', 'ਊ': 'aoo',
          'ਏ': 'e', 'ਐ': 'ai', 'ਓ': 'o', 'ਔ': 'aau', 'ੳ': 'u', 'ੲ': 'e'}
# marks kept inside a word but not written (udaat, yakash, visarg, variation selector)
_SILENT = '\u0a51\u0a75\u0a03\ufe00'
OTHER = {'॥': '|', '।': '|', 'ੴ': 'ik oankaar', **{g: a for g, a in zip('੦੧੨੩੪੫੬੭੮੯', '0123456789')}}


def _is(tok, kind: str, chars: str | None = None) -> bool:
    return tok is not None and tok.kind == kind and (chars is None or tok.text in chars)


def _word(tokens, line_start: bool = False) -> str:
    if len(tokens) >= 2 and tokens[0].text == 'ਮ' and tokens[1].text == 'ਃ':
        return 'mahalaa' + _word(tokens[2:]) if len(tokens) > 2 else 'mahalaa'
    tokens = [t for t in tokens if t.text not in '\ufe00ਃ']   # not written, no effect
    n = len(tokens)
    akhars = [t for t in tokens if t.kind in ('cons', 'vowel')]
    single = len(akhars) <= 1         # one-letter words keep their vowels
    # C ਹ C [ਿੁ] (e.g. ਸਹਜਿ, ਮਹਲ): the first a is written e
    kinds = ''.join('C' if t.kind == 'cons' else 'S' if t.kind == 'sign' else 'x' for t in tokens)
    eh_initial = (kinds in ('CCC', 'CCCS') and tokens[1].text == 'ਹ' and tokens[2].text != 'ਹ'
                  and (kinds == 'CCC' or tokens[3].text in 'ਿੁ'))
    out: list[str] = []
    for k, tok in enumerate(tokens):
        prev = tokens[k - 1] if k else None
        nxt = tokens[k + 1] if k + 1 < n else None
        rest = tokens[k + 1:]
        last = not rest or all(t.kind in ('nasal', 'addak') for t in rest)
        if tok.kind == 'cons':
            out.append(CONSONANTS.get(tok.text) or CONSONANTS.get(tok.text[0], ''))
            if nxt is None:
                if single and not line_start:
                    out.append('a')
                continue
            if nxt.kind in ('sign', 'virama', 'vowel'):
                continue
            # a consonant right before a C+ਉ syllable loses its a (ਕਰਉ krau, ਨਿਰਭਉ nirbhau)
            after = tokens[k + 2] if k + 2 < n else None
            before_cu = (nxt.kind in ('cons', 'nasal') and after is not None and after.text == 'ਉ')
            if (not last or single or nxt.kind == 'nasal') and not before_cu:
                out.append('e' if (eh_initial and k == 0) else 'a')
        elif tok.kind == 'sign':
            final = all(t.kind == 'nasal' for t in rest)
            subjoined = k >= 2 and _is(tokens[k - 2], 'virama')
            if final and tok.text in 'ਿੁ' and not single and not _is(prev, 'cons', 'ਹ') and not subjoined:
                continue
            out.append(SIGNS[tok.text])
            if tok.text == 'ੌ' and nxt is not None and nxt.kind in ('cons', 'nasal'):
                out.append('a')
        elif tok.kind == 'vowel':
            v = tok.text
            if v == 'ਇ' and prev is None:
                out.append('ei' if line_start else 'i')
            elif v == 'ਇ':
                out.append('ei' if _is(nxt, 'cons') else 'e')
            elif v == 'ਉ' and prev is None:
                out.append('au' if line_start else 'u')
            elif v == 'ਉ':
                out.append('u' if (_is(prev, 'sign', 'ਾ') or _is(prev, 'vowel', 'ਆ'))
                           else 'o' if _is(prev, 'sign', 'ੀੇ') else 'au')
            elif v == 'ਏ' and _is(prev, 'sign', 'ੀ'):
                pass                                     # ਕੀਏ → kee
            elif v == 'ਆ' and nxt is None and (_is(prev, 'sign', 'ੀ') or _is(prev, 'vowel', 'ਈ')):
                out.append('a')                          # ਕੀਆ → keea, ਪਾਈਆ → paaeea
            else:
                out.append(VOWELS[v])
            if v == 'ਔ' and nxt is not None and nxt.kind in ('cons', 'nasal'):
                out.append('a')
        elif tok.kind == 'nasal':
            after = tokens[k + 2] if k + 2 < n else None
            collapses = (nxt is not None and nxt.text in ('ਮ', 'ਨ')
                         and not (_is(after, 'virama') and _is(prev, 'sign', 'ਿ')))
            ending_noo = _is(prev, 'sign', 'ੂ') and k >= 2 and tokens[k - 2].text == 'ਨ'
            if not collapses and not ending_noo:      # ੰਮ → m, ੰਨ → n, ਨੂੰ → noo
                out.append('n')
        # addak and virama are not written
    word = ''.join(out)
    word = word.replace('aaa', 'aa')
    # word-final ਹ / ਹਿ after a plain consonant: ah → eh, ahi → eh, aahi → aeh
    h_at = n - 1 if tokens and tokens[-1].text == 'ਹ' else (
        n - 2 if n >= 2 and tokens[-2].text == 'ਹ' and tokens[-1].text == 'ਿ' else None)
    bare_two = h_at == n - 1 and len(akhars) == 2
    if (h_at is not None and h_at >= 1 and not single and (h_at == n - 2 or bare_two)
            and not (h_at >= 2 and _is(tokens[h_at - 2], 'virama'))):
        if word.endswith('aahi'):
            word = word[:-4] + 'aeh'
        elif re.search(r'[^aeiou]ahi?$', word) or (akhars[0].kind == 'vowel' and re.search(r'ahi?$', word)):
            word = re.sub(r'ahi?$', 'eh', word)
        elif bare_two and akhars[0].text in 'ਏਓ':
            word = word[:-1] + 'eh'                      # ਏਹ → eeh, ਓਹ → oeh
    return word


class GurmukhiShabadOS:
    @staticmethod
    def to_english(text: str) -> str:
        out: list[str] = []
        word: list = []
        line_start = True   # nothing but whitespace written on this line yet

        def flush() -> None:
            nonlocal line_start
            if word:
                out.append(_word(word, line_start))
                word.clear()
                line_start = False

        for tok in tokenize(normalize(text)):
            if tok.kind == 'other' and tok.text not in _SILENT:
                flush()
                out.append(OTHER.get(tok.text, tok.text))
                if tok.text == '\n':
                    line_start = True
                elif not tok.text.isspace():
                    line_start = False
            else:
                word.append(tok)
        flush()
        return ''.join(out)
