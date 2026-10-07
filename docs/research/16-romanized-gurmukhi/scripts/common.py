import pathlib
import sys, unicodedata
REPO = pathlib.Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO))
from gurmukhi_transliterate.iso15919 import GurmukhiISO15919
from gurmukhi_transliterate.practical import GurmukhiPractical
from gurmukhi_transliterate.romanizer import GurmukhiRomanizer
from gurmukhi_transliterate.systems import SYSTEMS, SYSTEM_ORDER
ALL = ['iso15919', 'practical'] + SYSTEM_ORDER
_R = {s: GurmukhiRomanizer(s) for s in SYSTEMS}
class Crash(Exception): pass
def fwd(sid, text, ds=False):
    try:
        if sid == 'iso15919': return GurmukhiISO15919.to_phonetic(text, delete_schwa=ds)
        if sid == 'practical': return GurmukhiPractical.to_practical(text, delete_schwa=ds)
        return _R[sid].romanize(text, delete_schwa=ds)
    except Exception as e:
        raise Crash(repr(e))
def sample_lines(path=REPO / 'tests/fixtures/legacy/japji.unicode.txt'):
    return [unicodedata.normalize('NFC', l.strip()) for l in open(path, encoding='utf-8') if l.strip()]
def sample_words():
    import re
    ws = []
    for l in sample_lines():
        for w in l.split():
            w = re.sub(r'[॥।੦-੯ੴ]', '', w)
            if w: ws.append(w)
    return ws
