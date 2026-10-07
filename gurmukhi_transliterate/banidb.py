"""
BaniDB / SikhiToTheMax transliteration: a line-for-line Python port of
anvaad-js 1.5.1 (Khalis Foundation, MIT; see _anvaad_tables.py for the
licence). BaniDB's `english` and `ipa` fields are produced by this code, so
the port is what the ``sttm`` and ``banidb_ipa`` systems use.

    GurmukhiBaniDB.to_english('ਕਿਵ ਸਚਿਆਰਾ ਹੋਈਐ')   # 'kiv sachiaaraa hoieeaai'
    GurmukhiBaniDB.to_ipa('ਕਿਵ ਸਚਿਆਰਾ ਹੋਈਐ')

The algorithm works on GurbaniAkhar ASCII (Unicode is converted first, as
anvaad's ``unicode(text, true)`` does) and is reproduced as written, quirks
included, because the goal is byte-identical output: e.g. some "literal"
replacements are regexes (``(N)`` matches ``N``), and character tests are
JavaScript substring tests (``'aeiou ooaiee'.indexOf(x)``).
"""

from __future__ import annotations

import re
import unicodedata

from . import _anvaad_tables as T

# ---------------------------------------------------------------------------
# Unicode → GurbaniAkhar ASCII (anvaad src/unicode.js, ascii(text, false))
# ---------------------------------------------------------------------------

_RM = T.REVERSE_MAPPING


def to_ascii(text: str) -> str:
    chars = list(text)
    out: list[str | None] = []
    n = len(chars)
    j = 0

    def at(k: int) -> str | None:
        return chars[k] if k < n else None

    while j < n:
        cur, nxt, nxt2 = chars[j], at(j + 1), at(j + 2)
        if nxt is not None and cur + nxt in T.SUPPLEMENTARY_CHARS:
            out.append(_RM.get(cur, '') + _RM.get(nxt, ''))
            j += 1
        elif cur == 'ਿ':                                   # sihari goes first
            last = out.pop() if out else None
            out.append('i')
            out.append(last)
        elif cur == '੍':                                   # virama + letter
            if nxt2 == 'ਿ':
                last = out.pop() if out else None
                out.append('i')
                out.append(last)
                j += 1
            out.append(_RM.get(cur + (nxt if nxt is not None else 'undefined')))
            if nxt2 == 'ੁ':
                out.append('ü')
                j += 1
            elif nxt2 == 'ੂ':
                out.append('¨')
                j += 1
            j += 1
        elif cur in ('ੑ', 'ੵ'):
            out.append(_RM.get(cur) or cur)
            if nxt == 'ੁ':
                out.append('ü')
                j += 1
            elif nxt == 'ੂ':
                out.append('¨')
                j += 1
        elif cur == 'ਨ' and nxt == 'ੂ' and nxt2 == 'ੰ':
            out.append('ƒ')
            j += 2
        elif cur == 'ੋ' and nxt == 'ੁ':
            out.append(_RM.get(cur + nxt))
            j += 1
        elif cur == 'ੱ' and nxt2 in T.ABOVE_CHARS:
            out.append('¤')
        elif cur == 'ਾ' and nxt == 'ਂ':
            out.append('W')
            j += 1
        elif cur == 'ਆ' and nxt == 'ਂ':
            out.append('AW')
            j += 1
        elif cur == 'ਈ' and nxt == '':
            out.append('eˆØI')
            j += 1
        elif cur == 'ਈ' and nxt == '':
            out.append('eµØI')
            j += 1
        elif (cur == 'ਂ' and nxt == 'ੀ') or (cur == 'ੀ' and nxt == ''):
            out.append('ˆØI')
            j += 1
        elif (cur == 'ੰ' and nxt == 'ੀ') or (cur == 'ੀ' and nxt == ''):
            out.append('µØI')
            j += 1
        else:
            out.append(_RM.get(cur) or cur)
        j += 1
    return ''.join(x or '' for x in out)   # JS join renders undefined as ''


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def _unescape(s: str) -> str:
    """lodash.unescape: only these five entities."""
    return re.sub(r'&(?:amp|lt|gt|quot|#39);',
                  lambda m: {'&amp;': '&', '&lt;': '<', '&gt;': '>',
                             '&quot;': '"', '&#39;': "'"}[m.group(0)], s)


def _swap_sihari(s: str) -> str:
    """'If current letter is "i", move behind next letter' (/i./gm)."""
    return re.sub(r'i.', lambda m: m.group(0)[::-1], s)


def _first_wins(pairs) -> dict[str, str]:
    d: dict[str, str] = {}
    for k, v in pairs:
        d.setdefault(k, v)   # JS indexOf finds the first entry
    return d


def _lit(fn):
    """A JS replace callback/replacement string, taken literally."""
    return fn if callable(fn) else (lambda m: fn)


# ---------------------------------------------------------------------------
# English (anvaad src/translit_modules/english.js)
# ---------------------------------------------------------------------------

_EN2 = _first_wins(T.ENGLISH_STEP2)
_EN_NOT_THIS = 'aeiou ooaiee'
_EN_NEXT_VOWELS = 'iaeouyw'
_EN_NEXT_BLOCK = 'I@ HR\xaa\xc5\xc6\xc7\xcd\xcf\xd2\xd3\xd4\xd8\xda\xe5\xe6\xe7\xfcŒœ:[]()'
_EN_NO_A = {_EN2['N'], _EN2['M'], 'hoo', 'ye', 'noo(n)', _EN2['<'], _EN2['>']}
_ALPHA = re.compile(r'^[a-zA-Z]+$')
_FORMAL_EN = [' ', 'pehilaa', 'doojaa', 'teejaa', 'chauthhaa', 'panjavaa', 'chhayvaa', 'satvaa',
              'atthvaa', 'nauvaa', 'dasvaa', 'gayaarvaa', 'baarvaa', 'tayrvaa', 'chaudavaa',
              'pandaravaa', 'solavaa', 'sataaravaa']


def english(gurmukhi: str) -> str:
    """anvaad ``translit(ascii)`` — GurbaniAkhar ASCII in, BaniDB English out."""
    if gurmukhi == '':
        return gurmukhi
    trans = gurmukhi
    for pat, rep in T.ENGLISH_STEP1:
        trans = re.sub(pat, _lit(rep), trans)
    trans = _unescape(trans)
    trans = _swap_sihari(trans)

    chars: list[str] = list(trans)
    count = len(chars)
    for x in range(count):
        this = chars[x]
        nxt = chars[x + 1] if x + 1 < count else ' '
        if this != ' ':
            if this in _EN2:
                this = _EN2[this]
            elif not this.isdigit() or not this.isascii():
                this = ''
        # 2. add an inherent "a"
        if (this != ''
                and this.lower() not in _EN_NOT_THIS
                and _ALPHA.match(this)
                and this not in _EN_NO_A
                and nxt.lower() not in _EN_NEXT_VOWELS
                and nxt not in _EN_NEXT_BLOCK
                and not ('i' in nxt.lower() and x + 2 < count and chars[x + 2] == ' ')):
            this = this + 'a'
        # 3. word-initial e before i → i
        prev = chars[x - 1] if x > 0 else None
        if this == 'e' and prev and nxt.lower() in 'i':
            this = 'i'
        # pehar rara
        if this == _EN2['R'] and prev == 'i':
            this = 'i'
            chars[x - 1] = 'r'
        chars[x] = this
    trans = ''.join(chars)

    trans = re.sub(r'[^aeiouy]i(\s|$|\|)', lambda m: m.group(0).replace('i', '', 1), trans, flags=re.M)
    trans = re.sub(r'((m:|mahalaa|mahalu|ghar|gharu)\s*([0-9][0-7]?))',
                   lambda m: f"{m.group(2).replace('m:', 'mahalaa', 1)} {_FORMAL_EN[int(m.group(3))]}",
                   trans, flags=re.M)
    trans = re.sub(r'([aeiou]|oo|ai|ee)(ie)aaa', lambda m: m.group(0).replace('ie', 'i', 1), trans, flags=re.M)
    trans = re.sub(r'ih\s+|$', lambda m: m.group(0).replace('ih', 'eh', 1), trans, flags=re.M)
    trans = re.sub(r'aie\s+|$', lambda m: m.group(0).replace('ie', 'ey', 1), trans, flags=re.M)
    trans = re.sub(r'gura[dmbs][a-zA-Z]+', lambda m: m.group(0).replace('gura', 'gur', 1), trans, flags=re.M)
    trans = re.sub(r'mana[m][a-zA-Z]+', lambda m: m.group(0).replace('mana', 'man', 1), trans, flags=re.M)
    trans = trans.replace('x', 'r')
    trans = re.sub(r'mirat[a-zA-Z]+', lambda m: m.group(0).replace('mirat', 'mrit', 1), trans, flags=re.M)
    for pat, rep in T.ENGLISH_STEP4:
        trans = re.sub(pat, _lit(rep), trans)
    return trans


# ---------------------------------------------------------------------------
# IPA (anvaad src/translit_modules/ipa.js)
# ---------------------------------------------------------------------------

_IPA2 = _first_wins(T.IPA_STEP2)
_IPA_NOT_THIS = 'əɑeɔɵ u\xe6ijɪəɛʊ̀'
_IPA_NEXT_VOWELS = 'iaɑeouywɪə̀ɛʊ'
_IPA_NEXT_BLOCK = '@ HR\xaa\xc5\xc6\xc7\xcd\xcf\xd2\xd3\xd4\xd8\xda\xe5\xe6\xe7\xfcŒœ:ɪ[]()'
_IPA_NO_A = {_IPA2['N'], _IPA2['M'], 'nuⁿ', _IPA2['<'], _IPA2['>'], 'e'}
_FORMAL_IPA = [' ', 'pəhɪlɑ', 'd̪ud͡ʒɑ', 't̪id͡ʒɑ',
               't͡ʃɵɵt̪ʰɑ', 'pəŋd͡ʒʋɑ',
               't͡ɕeʋɑ', 'sət̪ʋɑ', 'əʈʰʋɑ',
               'nɑʋɑ', 'd̪səʋɑ', 'Gɪəɑɾʋɑ',
               'bɑɾhəʋɑ', 't̪eɾʋɑ',
               't͡ʃɒd̪ʰʋɑ', 'pəŋd̪ʰɾʋɑ',
               'sɔlʰʋɑ', 'sət̪ɑɾʋɑ']
_IPA_STEP4 = [
    # JS string '(?!(\s))' is '(?!(s))': the backslash is an identity escape
    (r'(?!(s)).rəɓ(?!(s)).', lambda m: m.group(0).replace('rəɓ', 'rɓ', 1)),
    ('eiə', 'ei'),
    (' n ', ' nə '),
    (' k ', ' kə '),
    ('əə', 'ə'),
    ('əi', 'i'),
    ('eɪə', 'ɪ'),
    ('ʊ ', ' '),
    ('ə\xe6', '\xe6'),
    ('ɑeih', 'ɑɪ\xe6h'),
    (r' \.', '.'),
]


def ipa(gurmukhi: str) -> str:
    """anvaad ``translit(ascii, 'ipa')`` — GurbaniAkhar ASCII in, BaniDB IPA out."""
    trans = _unescape(gurmukhi)
    trans = _swap_sihari(trans)
    chars: list[str] = list(trans)
    count = len(chars)
    for x in range(count):
        this = chars[x]
        nxt = chars[x + 1] if x + 1 < count else ''
        if this != ' ':
            if this in _IPA2:
                this = _IPA2[this]
            elif not this.isdigit() or not this.isascii():
                this = ''
        if (this != ''
                and this not in _IPA_NOT_THIS
                and (_ALPHA.match(this) or this in T.IPA_CHARSET)
                and this not in _IPA_NO_A
                and nxt != ''
                and nxt.lower() not in _IPA_NEXT_VOWELS
                and (_ALPHA.match(nxt) or nxt in T.IPA_CHARSET)
                and nxt not in _IPA_NEXT_BLOCK):
            this = this + 'ə'
        chars[x] = this
    trans = ''.join(chars)
    trans = re.sub('[^ɑⁿəe\xe6ɪiɵouyɒɔɛ]ɪ(\\s|$|\\|)',
                   lambda m: m.group(0).replace('ɪ', '', 1), trans, flags=re.M)
    trans = re.sub('((m:|məhəlɑ|məhəlɵ|Gʰə̀ɾɵ|'
                   'Gʰə̀ɾ)\\s*([0-9]0?))',
                   lambda m: f"{m.group(2).replace('m:', 'mahalaa', 1)} {_FORMAL_IPA[int(m.group(3))]}",
                   trans, flags=re.M)
    trans = re.sub('ə̀[iaɑeouywɪəʊ̀ɔ]',
                   lambda m: m.group(0).replace('ə̀', '', 1), trans, flags=re.M)
    for pat, rep in _IPA_STEP4:
        trans = re.sub(pat, _lit(rep), trans)
    return trans


# ---------------------------------------------------------------------------
# Public class
# ---------------------------------------------------------------------------

class GurmukhiBaniDB:
    """BaniDB transliterations of Unicode Gurmukhi (as on SikhiToTheMax)."""

    @staticmethod
    def to_english(text: str) -> str:
        return english(to_ascii(unicodedata.normalize('NFC', text)))

    @staticmethod
    def to_ipa(text: str) -> str:
        return ipa(to_ascii(unicodedata.normalize('NFC', text)))
