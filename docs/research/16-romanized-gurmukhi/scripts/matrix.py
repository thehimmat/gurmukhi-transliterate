"""Collision matrix built from the static maps (no engine context)."""
from common import *
from itertools import combinations
from collections import defaultdict
ISO, PR = GurmukhiISO15919, GurmukhiPractical

BASE_CONS = list('ਸਹਕਖਗਘਙਚਛਜਝਞਟਠਡਢਣਤਥਦਧਨਪਫਬਭਮਯਰਲਵੜ')
NUKTA_CONS = ['ਸ਼','ਖ਼','ਗ਼','ਜ਼','ਫ਼','ਲ਼','ਕ਼']
MATRAS = ['∅'] + list('ਾਿੀੁੂੇੈੋੌ')   # ∅ = inherent vowel (mukta)
VOWELS = list('ਅਆਇਈਉਊਏਐਓਔ')
NASALS = ['ੰ','ਂ']

def maps(sid):
    if sid == 'iso15919':
        c = dict(ISO.CONSONANTS); vd = dict(ISO.VOWEL_DIACRITICS); vw = dict(ISO.VOWELS)
        vd['∅'] = 'a'; nas = {'ੰ': 'ṃ', 'ਂ': 'ṁ'}
    elif sid == 'practical':
        c = dict(PR.CONSONANTS); vd = dict(PR.VOWEL_DIACRITICS); vw = dict(PR.VOWELS)
        vd['∅'] = 'a'; nas = {'ੰ': 'n/m', 'ਂ': 'n/m'}   # context: m before labial else n
    else:
        s = SYSTEMS[sid]
        c = dict(s.consonants); vd = dict(s.vowel_diacritics); vw = dict(s.vowels)
        vd['∅'] = s.vowels.get('ਅ') or 'a'; nas = {'ੰ': s.nasal_tippi, 'ਂ': s.nasal_bindi}
    for k in NUKTA_CONS:
        c.setdefault(k, None)   # absent key == unsupported (engine skips/falls back)
    return c, vd, vw, nas

RETRO = {('ਟ','ਤ'),('ਠ','ਥ'),('ਡ','ਦ'),('ਢ','ਧ')}
ASP = {('ਕ','ਖ'),('ਗ','ਘ'),('ਚ','ਛ'),('ਜ','ਝ'),('ਟ','ਠ'),('ਡ','ਢ'),('ਤ','ਥ'),('ਦ','ਧ'),('ਪ','ਫ'),('ਬ','ਭ')}
UNASP = {b:a for a,b in ASP}
RET2DEN = {a:b for a,b in RETRO} | {'ਣ':'ਨ','ੜ':'ਰ'}
SHORTLONG_M = {frozenset(p) for p in [('∅','ਾ'),('ਿ','ੀ'),('ੁ','ੂ')]}
SHORTLONG_V = {frozenset(p) for p in [('ਅ','ਆ'),('ਇ','ਈ'),('ਉ','ਊ')]}

def kind(a, b, cat):
    p = frozenset((a, b))
    if cat == 'cons':
        if any(p == frozenset(x) for x in RETRO): return 'retroflex/dental'
        if p == frozenset(('ਣ','ਨ')): return 'ṇ/n'
        if p == frozenset(('ੜ','ਰ')): return 'ṛ/r'
        if any(p == frozenset(x) for x in ASP): return 'aspiration'
        if '਼' in a + b:
            base = {x.replace('਼','') for x in p}
            if len(base) == 1: return 'nukta'
            return 'nukta+other'
        # retroflex/dental crossed with aspiration (e.g. ਠ vs ਤ)
        def norm(x): x = UNASP.get(x, x); return RET2DEN.get(x, x)
        if norm(a) == norm(b): return 'retroflex/dental+aspiration'
        return 'other-consonant'
    if cat in ('matra', 'vowel'):
        if p in SHORTLONG_M or p in SHORTLONG_V: return 'short/long vowel'
        return 'other-vowel'
    if cat == 'nasal': return 'tippi/bindi'

def analyse(sid):
    c, vd, vw, nas = maps(sid)
    cats = {
        'cons': [(k, c.get(k)) for k in BASE_CONS + NUKTA_CONS],
        'matra': [(k, vd.get(k)) for k in MATRAS],
        'vowel': [(k, vw.get(k)) for k in VOWELS],
        'nasal': [(k, nas.get(k)) for k in NASALS],
    }
    # ISO/practical/shackle have ਕ਼; others don't define it -> treat as unsupported
    collisions, unsupported, pairs, kept = [], [], 0, 0
    for cat, items in cats.items():
        for k, v in items:
            if v is None: unsupported.append(k)
        for (a, va), (b, vb) in combinations(items, 2):
            pairs += 1
            if va is None or vb is None:
                continue  # counted as loss via unsupported, not as a collision pair
            if va.lower() == vb.lower():
                collisions.append((cat, a, b, va, vb, kind(a, b, cat), va == vb))
            else:
                kept += 1
    # pairs involving an unsupported item are lost
    return dict(collisions=collisions, unsupported=unsupported, pairs=pairs, kept=kept)

if __name__ == '__main__':
    import json
    rows = {}
    for sid in ALL:
        r = analyse(sid)
        by = defaultdict(list)
        for cat, a, b, va, vb, k, exact in r['collisions']:
            by[k].append(f"{a}/{b}={va}" + ('' if exact else f"~{vb}(case)"))
        rows[sid] = r
        print(f"\n## {sid}: distinct pairs kept {r['kept']}/{r['pairs']} = {r['kept']/r['pairs']:.3f}; unsupported={''.join(r['unsupported']) or '-'}")
        for k, v in sorted(by.items()):
            print(f"  {k}: {', '.join(v)}")
