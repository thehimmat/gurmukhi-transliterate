"""Round-trip: Gurmukhi -> Shackle (GurmukhiRomanizer) -> reverse_transliterate."""
from common import *
from gurmukhi_transliterate.reverse import reverse_transliterate
from gurmukhi_transliterate.matcher import candidate_spellings, CorpusMatcher
from collections import Counter
import unicodedata, sys

def run(words, sid='shackle', ds=False, show=True):
    ok = cand = 0; n = 0; kinds = Counter(); ncands = []; fails = []
    for w in words:
        rom = fwd(sid, w + ' ', ds).rstrip(' ')
        r = reverse_transliterate(rom)
        cs = candidate_spellings(r)
        n += 1
        ok += r.gurmukhi == w
        cand += w in cs
        ncands.append(len(cs))
        for a in r.ambiguities: kinds[a.kind] += 1
        if r.gurmukhi != w: fails.append((w, rom, r.gurmukhi, w in cs, len(cs)))
    print(f"{sid} ds={ds}: tokens={n} exact={ok} ({ok/n:.1%}) truth-in-candidates={cand} ({cand/n:.1%}) "
          f"mean#candidates={sum(ncands)/n:.2f} max={max(ncands)} ambiguity kinds={dict(kinds)}")
    if show:
        for f in fails: print('   FAIL', f)
    return ok, cand, n

words = sample_words()
uniq = sorted(set(words), key=words.index)
print('== Japji tokens (71 running words) ==')
run(words, show=False)
print('== Japji unique words (57) ==')
run(uniq)
# matcher with a lexicon = the sample itself (oracle lexicon: upper bound)
m = CorpusMatcher(Counter(words))
best = sum(m.match(fwd('shackle', w + ' ').rstrip()).best == w for w in uniq)
print(f'CorpusMatcher with oracle lexicon (sample words, freq=count): best==truth {best}/{len(uniq)}')
print('== Supplement (20 hand-picked words) ==')
SUPP = ['ਸਿੱਖ','ਪੱਕਾ','ਇੱਕ','ਅੰਮ੍ਰਿਤ','ਸਿੰਘ','ਮਾਂ','ਸੰਤ','ਗੁਰੂ','ਵਾਹਿਗੁਰੂ','ਖ਼ਾਲਸਾ',
        'ਜ਼ਮੀਨ','ਸ਼ਬਦ','ਪੰਥ','ਠਾਕੁਰ','ਡਰ','ਢਾਡੀ','ਪ੍ਰੀਤਮ','ਨ੍ਹਾਵਣ','ਕਿਉਂ','ਆਂਖ']
run(SUPP)
print('== Shackle reverse applied to other systems (Japji unique words) ==')
for sid in ['iso15919', 'iast', 'sacred_nitnem', 'shackle', 'dr_sant_singh', 'practical']:
    run(uniq, sid=sid, show=False)
print('== Shackle with delete_schwa=True (not Shackle convention; shows schwa sensitivity) ==')
run(uniq, ds=True, show=False)
