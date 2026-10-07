"""Baseline accuracy of compare.identify_system on the Japji sample.

Measured the token-coverage implementation that #27 replaced; run it at
commit c45e542 (the internals it imports no longer exist).
"""
from common import *
from gurmukhi_transliterate.compare import identify_system, _tokenise, _TOKEN_INDEX
from collections import Counter, defaultdict
import re, json

lines = sample_lines()
words = sample_words()

def evaluate(units, ds, label):
    top1 = top3 = strict1 = tied = n = 0
    conf = Counter()
    rank_by_sys = defaultdict(list)
    for sid in ALL:
        for u in units:
            try: rom = fwd(sid, u, ds)
            except Crash: rom = fwd(sid, u + ' ', ds).rstrip()
            res = identify_system(rom, top_n=99)
            ids = [r['system'] for r in res]
            sc = {r['system']: r['confidence'] for r in res}
            pos = ids.index(sid) + 1
            better = sum(1 for s in ids if sc[s] > sc[sid])
            ties = sum(1 for s in ids if sc[s] == sc[sid]) - 1
            n += 1
            top1 += pos == 1; top3 += pos <= 3
            strict1 += better == 0 and ties == 0
            tied += better == 0 and ties > 0
            rank_by_sys[sid].append(pos)
            if pos != 1: conf[(sid, ids[0])] += 1
    print(f"\n### {label}: n={n}  top1={top1/n:.3f} ({top1})  top3={top3/n:.3f} ({top3})  "
          f"unique-top1={strict1/n:.3f} ({strict1})  tied-at-top={tied/n:.3f} ({tied})")
    for sid in ALL:
        r = rank_by_sys[sid]
        print(f"  {sid:14s} top1={sum(p==1 for p in r)}/{len(r)} top3={sum(p<=3 for p in r)}/{len(r)} mean_rank={sum(r)/len(r):.1f}")
    print("  confusions (true -> predicted top1):", ', '.join(f"{a}->{b}:{c}" for (a, b), c in conf.most_common(20)))
    return conf

for ds in (False, True):
    evaluate(lines, ds, f"LINES (10 Japji lines), delete_schwa={ds}")
    evaluate(sorted(set(words), key=words.index), ds, f"WORDS (57 unique Japji words), delete_schwa={ds}")

# Illustrate a failure: full score table for line 1 in a few systems
print()
for sid in ['iso15919', 'practical', 'shackle', 'sttm', 'gursevak', 'dr_thind']:
    rom = fwd(sid, lines[2])
    res = identify_system(rom, top_n=99)
    print(sid, repr(rom)); print('   ', [(r['system'], r['confidence']) for r in res[:6]], ' true@', [r['system'] for r in res].index(sid)+1, 'score', [r['confidence'] for r in res if r['system']==sid][0])
    print('    tokens:', _tokenise(rom)[:30])

# token index stats
print('\nindex size', len(_TOKEN_INDEX))
sizes = Counter(len(v) for v in _TOKEN_INDEX.values())
print('tokens by #systems sharing them:', sorted(sizes.items()))
for sid in ALL:
    excl = sorted(t for t, v in _TOKEN_INDEX.items() if v == {sid})
    tot = sorted(t for t, v in _TOKEN_INDEX.items() if sid in v)
    print(f"  {sid:14s} tokens={len(tot):3d} exclusive={len(excl):2d} {excl}")
