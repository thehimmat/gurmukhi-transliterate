"""Candidate-spellings-per-word experiment on the Japji sample."""
from invert import *
from matrix import maps, RETRO, ASP
from itertools import combinations
import difflib, json, statistics, sys, time, math, re

def vowelchars(sid):
    c, vd, vw, nas = maps(sid)
    s = set()
    for v in list(vd.values()) + list(vw.values()):
        if v: s |= set(v)
    return s

def invert_ds(sid, T):
    vc = vowelchars(sid)
    inh = maps(sid)[1]['∅']
    pos = [p for p in range(1, len(T) + 1)
           if T[p - 1] not in vc and (p == len(T) or T[p] not in vc)]
    pos = pos[:8]
    out = set(); timeouts = 0
    for k in range(len(pos) + 1):
        for sub in combinations(pos, k):
            Tp = T
            for p in sorted(sub, reverse=True):
                Tp = Tp[:p] + inh + Tp[p:]
            res = invert(sid, Tp, False)
            if isinstance(res, tuple): timeouts += 1; res = res[0]
            for g in res:
                try:
                    if render(sid, g, True) == T: out.add(g)
                except Crash: pass
    return out, timeouts

TIPPI_OK = set('ਿੁੂਅਇਉ')
# _core engine drops addak after a vowel sign/independent vowel and ੰ/ਂ after an independent vowel
ARTIFACT = re.compile('[ਾਿੀੁੂੇੈੋੌਅਆਇਈਉਊਏਐਓਔ]ੱ|[ਅਆਇਈਉਊਏਐਓਔ][ੰਂ]')
SUPP = ['ਸਿੱਖ','ਪੱਕਾ','ਇੱਕ','ਅੰਮ੍ਰਿਤ','ਸਿੰਘ','ਮਾਂ','ਸੰਤ','ਗੁਰੂ','ਵਾਹਿਗੁਰੂ','ਖ਼ਾਲਸਾ',
        'ਜ਼ਮੀਨ','ਸ਼ਬਦ','ਪੰਥ','ਠਾਕੁਰ','ਡਰ','ਢਾਡੀ','ਪ੍ਰੀਤਮ','ਨ੍ਹਾਵਣ','ਕਿਉਂ','ਆਂਖ']
def tb_ok(g):
    for i, ch in enumerate(g):
        if ch in 'ੰਂ':
            prev = g[i - 1] if i else ''
            tippi_ctx = prev in TIPPI_OK or not (prev in 'ਾੀੇੈੋੌਆਈਊਏਐਓਔ')
            if (ch == 'ੰ') != tippi_ctx: return False
    return True

RET = {frozenset(p) for p in RETRO}
ASPS = {frozenset(p) for p in ASP}
SL = {frozenset(p) for p in [('ਾ', ''), ('ਿ', 'ੀ'), ('ੁ', 'ੂ'), ('ਅ', 'ਆ'), ('ਇ', 'ਈ'), ('ਉ', 'ਊ')]}
MATR = set('ਾਿੀੁੂੇੈੋੌ'); INDV = set('ਅਆਇਈਉਊਏਐਓਔ')
def diff_kinds(a, b):
    kinds = set()
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op == 'equal': continue
        x, y = a[i1:i2], b[j1:j2]
        p = frozenset((x, y))
        if p in RET: kinds.add('retroflex/dental')
        elif p == frozenset(('ਣ', 'ਨ')): kinds.add('ṇ/n')
        elif p == frozenset(('ੜ', 'ਰ')): kinds.add('ṛ/r')
        elif p in ASPS: kinds.add('aspiration')
        elif '਼' in x + y and x.replace('਼', '') == y.replace('਼', ''): kinds.add('nukta')
        elif set(x + y) <= set('ੰਂ'): kinds.add('tippi/bindi (incl. presence)')
        elif set(x + y) <= set('ੱ'): kinds.add('addak presence')
        elif p in SL or (set(x + y) <= MATR | INDV and len(x + y) <= 2 and any(frozenset((x, y)) == q for q in SL)): kinds.add('short/long vowel')
        elif '੍' in x + y: kinds.add('conjunct/segmentation')
        elif set(x + y) <= MATR | INDV: kinds.add('other vowel')
        else: kinds.add('other/segmentation')
    return kinds

if __name__ == '__main__':
    mode = sys.argv[1]  # 'nods' or 'ds'
    SAMPLE = sys.argv[2]  # 'japji' or 'supp'
    sids = sys.argv[3:] or ALL
    words = sample_words() if SAMPLE == 'japji' else SUPP
    uniq = sorted(set(words), key=words.index)
    res = {}
    for sid in sids:
        t0 = time.time()
        rows = []
        for w in uniq:
            T = render(sid, w, mode == 'ds')
            if mode == 'ds':
                cands, to = invert_ds(sid, T)
            else:
                r = invert(sid, T, False); to = 0
                if isinstance(r, tuple): to = 1; r = r[0]
                cands = r
            kinds = set()
            for g in cands:
                if g != w: kinds |= diff_kinds(w, g)
            core = sid not in ('iso15919', 'practical')
            n_noart = sum(1 for g in cands if not (core and ARTIFACT.search(g)) or g == w)
            rows.append(dict(w=w, T=T, n=len(cands), n_noart=n_noart, n_tb=sum(1 for g in cands if tb_ok(g)),
                             truth=w in cands, timeouts=to, kinds=sorted(kinds),
                             ex=sorted(cands)[:12]))
        res[sid] = rows
        ns = [r['n'] for r in rows]; ntb = [r['n_tb'] for r in rows]; nna = [r['n_noart'] for r in rows]
        found = sum(r['truth'] for r in rows)
        print(f"{sid:14s} words={len(rows)} truth_found={found} unique(n==1)={sum(n==1 for n in ns)} "
              f"median={statistics.median(ns)} mean={statistics.mean(ns):.1f} max={max(ns)} "
              f"geo={math.exp(statistics.mean(math.log(max(n,1)) for n in ns)):.2f} "
              f"| tb-rule median={statistics.median(ntb)} geo={math.exp(statistics.mean(math.log(max(n,1)) for n in ntb)):.2f} "
              f"| no-engine-artifact median={statistics.median(nna)} geo={math.exp(statistics.mean(math.log(max(n,1)) for n in nna)):.2f} uniq={sum(n==1 for n in nna)} "
              f"timeouts={sum(r['timeouts'] for r in rows)} t={time.time()-t0:.0f}s", flush=True)
    json.dump(res, open(f'cands_{mode}_{SAMPLE}_{"_".join(sids) if len(sids)<3 else "all"}.json', 'w'), ensure_ascii=False, indent=1)
