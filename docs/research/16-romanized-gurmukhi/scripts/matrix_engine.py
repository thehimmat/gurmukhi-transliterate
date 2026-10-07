"""Reversibility matrix measured through the real forward code with minimal pairs.
Cell: 'kept' if the two Gurmukhi strings romanize differently, else 'LOST' (+ detail)."""
from common import *
def F(s, g, ds=False):
    try: return fwd(s, g + ' ', ds).rstrip(' ')
    except Crash: return 'CRASH'
COLS = [
 ('retroflex/dental', [('ਟ','ਤ'),('ਠ','ਥ'),('ਡ','ਦ'),('ਢ','ਧ')]),
 ('ṇ/n', [('ਣ','ਨ')]),
 ('ṛ/r', [('ੜ','ਰ')]),
 ('aspiration', [('ਕ','ਖ'),('ਗ','ਘ'),('ਚ','ਛ'),('ਜ','ਝ'),('ਟ','ਠ'),('ਡ','ਢ'),('ਤ','ਥ'),('ਦ','ਧ'),('ਪ','ਫ'),('ਬ','ਭ')]),
 ('ਸ਼/ਸ', [('ਸ਼','ਸ')]),
 ('other nukta', [('ਖ਼','ਖ'),('ਗ਼','ਗ'),('ਜ਼','ਜ'),('ਫ਼','ਫ'),('ਲ਼','ਲ')]),
 ('tippi/bindi', [('ਕਿੰ','ਕਿਂ'),('ਕੰ','ਕਂ'),('ਕਾਂ','ਕਾੰ')]),
 ('nasal present (after matra)', [('ਕਾਂ','ਕਾ'),('ਕਿੰ','ਕਿ')]),
 ('nasal after indep. vowel', [('ਆਂ','ਆ'),('ਅੰਗ','ਅਗ')]),
 ('addak after consonant', [('ਪੱਕਾ','ਪਕਾ')]),
 ('addak after vowel sign', [('ਸਿੱਖ','ਸਿਖ'),('ਇੱਕ','ਇਕ')]),
 ('short/long vowel', [('ਕ','ਕਾ'),('ਕਿ','ਕੀ'),('ਕੁ','ਕੂ'),('ਇ','ਈ'),('ਉ','ਊ'),('ਅ','ਆ')]),
 ('ੇ/ੈ, ੋ/ੌ', [('ਕੇ','ਕੈ'),('ਕੋ','ਕੌ')]),
 ('ੈ/ੌ vs hiatus ਇ/ਉ', [('ਕੈ','ਕਇ'),('ਕੌ','ਕਉ')]),
 ('ੌ vs inherent', [('ਕੌ','ਕ')]),
 ('final aunkar/sihari vs none', [('ਕਰੁ','ਕਰ'),('ਕਰਿ','ਕਰ')]),
 ('schwa (no deletion): C+a vs conjunct', [('ਕਰਤਾਰ','ਕਰ੍ਤਾਰ')]),
 ('schwa (delete_schwa=True)', 'DS'),
 ('other static collisions', 'STATIC'),
]
from matrix import analyse
KNOWN = {'retroflex/dental','ṇ/n','ṛ/r','aspiration','nukta','tippi/bindi','short/long vowel'}
print('| system | ' + ' | '.join(c for c, _ in COLS) + ' |')
print('|---|' + '---|' * len(COLS))
summary = {}
for s in ALL:
    cells = []; lost = 0; tot = 0
    for name, pairs in COLS:
        if pairs == 'STATIC':
            oth = [f'{a}={b}→`{va}`' for cat, a, b, va, vb, k, ex in analyse(s)['collisions'] if k not in KNOWN and ex]
            cells.append('LOST: ' + '; '.join(oth) if oth else '—'); continue
        if pairs == 'DS':
            a = F(s, 'ਕਰਤਾਰ', True); b = F(s, 'ਕਰ੍ਤਾਰ', True)
            bad = [f'ਕਰਤਾਰ=ਕਰ੍ਤਾਰ→`{a}`'] if a == b else []
            cells.append('LOST ' + ','.join(bad) if bad else 'kept'); continue
        bad = []
        for x, y in pairs:
            fx, fy = F(s, x), F(s, y)
            tot += 1
            if fx == fy:
                bad.append(f'{x}={y}→`{fx}`' if fx else f'{x}={y}→∅'); lost += 1
            elif fx == '' or fy == '':
                bad.append(f'{x if fx=="" else y} dropped'); lost += 1
        cells.append(('LOST: ' + '; '.join(bad)) if bad else 'kept')
    summary[s] = (lost, tot)
    print(f'| {s} | ' + ' | '.join(cells) + ' |')
print()
for s, (l, t) in summary.items(): print(f'{s}: minimal pairs collapsed {l}/{t}; kept {(t-l)/t:.2f}')
