"""
iGurbani's English transliteration (the pre-BaniDB SikhiToTheMax scheme,
sttm_legacy).

A clean-room engine: no published code produces this scheme, so the rules
were derived only from what igurbani.com serves. The letter values come from
the sttm_legacy map in systems.py; this module adds the spelling rules. It
is checked against igurbani.com's output in tests/test_conformance.py.

    GurmukhiIGurbani.to_english('ਨਾਨਕ, ਜੇ ਕੋ ਆਪੁ ਗਣਾਇਦਾ; ਸੋ ਮੂਰਖੁ ਗਾਵਾਰੁ ॥੧॥')
    # 'naanak jae ko aap ganaaeidhaa so moorakh gaavaar ||1||'
"""

from __future__ import annotations

from ._tokens import normalize, tokenize
from .systems import STTM_LEGACY

CONSONANTS = {k: v for k, v in STTM_LEGACY.consonants.items() if v is not None}
SIGNS = STTM_LEGACY.vowel_diacritics
VOWELS = STTM_LEGACY.vowels
SUBJOINED = {k[1]: v for k, v in STTM_LEGACY.subjoined.items()}   # ਰ → r, others silent
OTHER = {'॥': '||', '।': '|', 'ੴ': 'ik oankaar',
         **{g: a for g, a in zip('੦੧੨੩੪੫੬੭੮੯', '0123456789')}}
# not written: vishraam punctuation, udaat, yakash, visarg, variation selector
_DROP = ';,.ੑੵਃ︀'


def _cons(ch: str) -> str:
    return CONSONANTS.get(ch) or CONSONANTS.get(ch[0], '')


def _word(tokens) -> str:
    if [t.text for t in tokens] == ['ਮ', '꞉']:
        return 'ma'
    tokens = [t for t in tokens if t.text != '꞉']
    # a doubled subjoined letter (ਤ੍ਯ੍ਯ, ਨ੍ਹ੍ਹ) is written once
    dedup = []
    for t in tokens:
        if len(dedup) >= 3 and t.text == dedup[-2].text and dedup[-1].kind == 'virama' \
                and dedup[-3].kind == 'virama':
            dedup.pop()
            continue
        dedup.append(t)
    tokens = dedup
    n = len(tokens)

    def at(i):
        return tokens[i] if 0 <= i < n else None

    def is_final(i):
        """Nothing after position i but nasals and addak."""
        return all(t.kind in ('nasal', 'addak') for t in tokens[i + 1:])

    out: list[str] = []
    k = 0
    while k < n:
        tok, prev, nxt = tokens[k], at(k - 1), at(k + 1)
        if tok.kind == 'cons':
            subjoined = prev is not None and prev.kind == 'virama'
            if subjoined:
                out.append(SUBJOINED.get(tok.text[0]) or '')
            else:
                out.append(_cons(tok.text))
            if nxt is None:
                pass                                    # final schwa dropped
            elif nxt.kind == 'virama':
                pass
            elif nxt.kind == 'sign':
                # ਕ੍ਰਿ → kira: the ਿ is said before the ਰ, which keeps its a
                if (subjoined and tok.text == 'ਰ' and nxt.text == 'ਿ' and at(k - 2).text == 'ਕ'
                        and not is_final(k + 1)):
                    out.insert(len(out) - 1, 'i')
                    out.append('a')
                    k += 2
                    continue
            elif nxt.kind == 'vowel' and nxt.text != 'ਇ':
                pass                                    # ਕਉ → ko, ਗਏ → geae, ਗਈ → gee
            elif nxt.kind == 'addak' and is_final(k):
                pass
            else:
                # ਹ softens the a before it (ਮਹਲਾ → mehalaa), but not before ਹੁ (ਕਹੁ → kahu)
                h_at = k + 1 if nxt.text == 'ਹ' else k + 2 if nxt.kind in ('nasal', 'addak') else None
                h = at(h_at) if h_at is not None else None
                soft = (h is not None and h.text == 'ਹ' and tok.text != 'ਹ'
                        and not (at(h_at + 1) is not None and at(h_at + 1).text == 'ੁ'))
                out.append('e' if soft else 'a')
        elif tok.kind == 'sign':
            if tok.text in 'ਿੁ' and is_final(k) and not (prev is not None and prev.text == 'ਹ'):
                pass                                    # ਹਰਿ → har, ਨਾਮੁ → naam
            else:
                out.append(SIGNS[tok.text])
        elif tok.kind == 'vowel':
            v = tok.text
            if prev is not None and v == 'ਉ':
                out.append('o' if is_final(k) else 'ou')
            elif prev is not None and v == 'ਇ':
                out.append('e' if is_final(k) else 'ei')
            else:
                out.append(VOWELS.get(v, ''))
        elif tok.kind == 'addak' and nxt is not None and nxt.kind == 'cons':
            out.append(_cons(nxt.text))                 # unattested on iGurbani; doubled as in the map
        elif tok.kind == 'nasal':
            # independent ਆ + bindi: ਬਿਜੁਲੀਆਂ → bijuleeaaan
            out.append('an' if prev is not None and prev.text == 'ਆ' and tok.text == 'ਂ' else 'n')
        # virama is not written
        k += 1
    return ''.join(out)


class GurmukhiIGurbani:
    @staticmethod
    def to_english(text: str) -> str:
        out: list[str] = []
        word: list = []

        def flush() -> None:
            if word:
                out.append(_word(word))
                word.clear()

        for tok in tokenize(normalize(text)):
            if tok.kind == 'other' and tok.text in _DROP:
                continue
            if tok.kind == 'other' and tok.text != '꞉':
                flush()
                out.append(OTHER.get(tok.text, tok.text))
            else:
                word.append(tok)
        flush()
        return ''.join(out)
