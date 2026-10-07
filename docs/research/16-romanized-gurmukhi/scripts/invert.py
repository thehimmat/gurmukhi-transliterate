"""Brute-force inverse at akshara level: enumerate every orthographically
plausible Gurmukhi word whose forward romanization (computed by the repo's own
transliterators) equals the target roman word.

Akshara grammar:  [ੱ] C [੍ S] [M] [N]   |   V [N]
  C = any consonant the system maps to a non-None value (incl. nukta forms)
  S = subjoinable consonant (ਰ ਵ ਹ ਤ ਯ), M = vowel sign, N = ੰ or ਂ
  V = independent vowel (ਅ only word-initially); ੱ never word-initial.
"""
from common import *
import unicodedata, time
import os
TLIM = float(os.environ.get('TLIM', 30))
from collections import defaultdict
from matrix import maps, BASE_CONS, NUKTA_CONS, VOWELS

MATRAS = list('ਾਿੀੁੂੇੈੋੌ')
SUBJ = list('ਰਵਹਤਯ')
SONORANT = set('ਨਮਰਲੜਣਵ')  # only these take subjoined ਹ in practice (cf. reverse.py aspirate sonorants)
CAP = 2000
TIPPI_OK = set(['', 'ਿ', 'ੁ', 'ੂ', 'ਅ', 'ਇ', 'ਉ'])  # modern tippi/bindi rule

_cache = {}
def aksharas(sid):
    if sid in _cache: return _cache[sid]
    c, vd, vw, nas = maps(sid)
    cons = [k for k in BASE_CONS + NUKTA_CONS if c.get(k) is not None]
    subj = [k for k in SUBJ if c.get(k) is not None]
    mat = [''] + [k for k in MATRAS if vd.get(k) is not None]
    vow = [k for k in VOWELS if vw.get(k) is not None]
    aks = []  # (string, vowelkey, is_vowel_initial)
    for C in cons:
        for cj in [''] + ['੍' + s for s in subj if s != 'ਹ' or C in SONORANT]:
            for m in mat:
                for n in ['', 'ੰ', 'ਂ']:
                    aks.append((C + cj + m + n, m, n, False))
    for v in vow:
        for n in ['', 'ੰ', 'ਂ']:
            aks.append((v + n, v, n, True))
    idx = defaultdict(list)
    for a in aks:
        try: s = fwd(sid, a[0])
        except Crash: s = ''
        key = s[:1]
        idx[key].append(a)
        if sid == 'iso15919' and a[3]:
            idx["'"].append(a)
    _cache[sid] = idx
    return idx

def render(sid, g, ds):
    return fwd(sid, g + ' ', ds).rstrip(' ')

def invert(sid, target, ds=False, tb_rule=False):
    idx = aksharas(sid)
    out = set()
    deadline = [time.time() + TLIM]
    inh = maps(sid)[1]['∅']
    def can_align(r, T):
        # can r match a prefix of T if some occurrences of the inherent vowel
        # string in r are dropped (schwa deletion)?
        L = len(inh); seen = set(); stack = [(0, 0)]
        while stack:
            i, j = stack.pop()
            if i == len(r): return True
            if (i, j) in seen: continue
            seen.add((i, j))
            if j < len(T) and r[i] == T[j]: stack.append((i + 1, j + 1))
            if r.startswith(inh, i): stack.append((i + L, j))
            if sid == 'practical' and r[i] == 'n' and j < len(T) and T[j] == 'm': stack.append((i + 1, j + 1))
        return False
    def viable(g):
        if time.time() > deadline[0]: return False, None
        try: r = fwd(sid, g, False)
        except Crash:
            try: r = fwd(sid, g + ' ', False).rstrip(' ')
            except Crash: return True, None
        if ds:
            return can_align(r, target), r
        if target.startswith(r): return True, r
        if sid == 'practical':
            if r.endswith('n') and target.startswith(r[:-1]): return True, r
            if (target + 'a').startswith(r): return True, r
        return False, r
    def dfs(g, depth):
        if len(out) >= CAP or depth > len(target): return
        if g:
            try:
                if render(sid, g, ds) == target:
                    out.add(unicodedata.normalize('NFC', g))
            except Crash:
                pass
        try: pos = len(fwd(sid, g, ds)) if g else 0
        except Crash: pos = 0
        keys = set()
        rng = range(len(target)) if ds else ([pos - 1, pos, pos + 1] if sid == 'practical' else [pos])
        for p in rng:
            if 0 <= p < len(target): keys.add(target[p])
        keys.add('')
        cands = []
        for k in keys:
            cands += idx.get(k, [])
        for a, vk, n, isv in cands:
            if isv and vk == 'ਅ' and g: continue
            if tb_rule and n and ((n == 'ੰ') != (vk in TIPPI_OK)): continue
            for pre in ([''] if (not g or isv or g[-1] in 'ੰਂ') else ['', 'ੱ']):
                g2 = g + pre + a
                ok, _ = viable(g2)
                if ok: dfs(g2, depth + 1)
    dfs('', 0)
    return out if time.time() <= deadline[0] else (out, 'TIMEOUT')

if __name__ == '__main__':
    import time
    t0 = time.time()
    for w in ['ਸਤਿ', 'ਨਾਮੁ', 'ਕਰਤਾ', 'ਸਿੰਘ', 'ਸਿੱਖ', 'ਪ੍ਰਸਾਦਿ', 'ਨਿਰਭਉ']:
        for sid in ['iso15919', 'practical', 'dr_thind', 'shackle', 'sttm_legacy']:
            t = render(sid, w, False)
            c = invert(sid, t)
            print(sid, w, t, len(c), w in c, sorted(c)[:6])
    print(time.time() - t0)
