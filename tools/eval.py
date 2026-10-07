"""Evaluate detection, system identification and reverse transliteration on
real romanized text (tests/fixtures/gold/). See tests/fixtures/gold/README.md.

Usage:
    python tools/eval.py                      # print the tables
    python tools/eval.py --write docs/eval/baseline.md
    python tools/eval.py --dakshina DIR       # also score the Dakshina pa test set

The numbers are a baseline for #16 phases 2-6, not a pass/fail gate.
"""

from __future__ import annotations

import argparse
import collections
import csv
import datetime
import statistics
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from gurmukhi_transliterate import GurmukhiLegacy, GurmukhiRomanizer, identify_system  # noqa: E402
from gurmukhi_transliterate.lexicon import load_lexicon, words  # noqa: E402
from gurmukhi_transliterate.matcher import candidate_spellings  # noqa: E402
from gurmukhi_transliterate.reverse import reverse_transliterate  # noqa: E402
from gurmukhi_transliterate.verse import _corpus, match_verse  # noqa: E402
from gurmukhi_transliterate.system_reverse import ALL_SYSTEMS, _forward, reverse_words  # noqa: E402
from gurmukhi_transliterate.reverse import shackle_to_gurmukhi  # noqa: E402

# Candidates per word measured in docs/research/16-romanized-gurmukhi (≤ ~1.4 = near-lossless)
NEAR_LOSSLESS = ('iso15919', 'ipa', 'iast', 'banidb_ipa', 'shackle', 'gursevak',
                 'sacred_nitnem', 'dr_sant_singh')

GOLD = REPO / 'tests' / 'fixtures' / 'gold'

# Gold scheme column → this repo's matching system (None: not implemented yet)
SCHEME_SYSTEM = {'banidb': 'sttm', 'banidb_ipa': 'banidb_ipa', 'shabados': 'shabados'}


def load_gold() -> list[dict]:
    with open(GOLD / 'lines.tsv', encoding='utf-8', newline='') as f:
        return list(csv.DictReader(f, delimiter='\t', quoting=csv.QUOTE_NONE, escapechar='\\'))


def load_english() -> list[str]:
    return [l for l in (GOLD / 'english.txt').read_text(encoding='utf-8').splitlines() if l.strip()]


def load_punjabi() -> list[str]:
    return [l for l in (GOLD / 'punjabi_romanized.txt').read_text(encoding='utf-8').splitlines()
            if l.strip()]


def roman_words(text: str) -> list[str]:
    return [t for t in text.split() if any(ch.isalpha() for ch in t)]


def overlap(pred: list[str], gold: list[str]) -> int:
    """Multiset overlap: how many gold tokens appear in pred."""
    return sum((collections.Counter(pred) & collections.Counter(gold)).values())


def pct(n: int, d: int) -> str:
    return f'{100 * n / d:.1f}%' if d else 'n/a'


# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------

def eval_detection(gold: list[dict], english: list[str]) -> list[dict]:
    cases = [
        ('Unicode Gurmukhi', 'unicode', [g['gurmukhi'] for g in gold]),
        ('GurbaniAkhar ASCII', 'anmollipi', [g['gurbaniakhar'] for g in gold]),
        ('BaniDB English', 'latin', [g['banidb'] for g in gold]),
        ('Shabad OS English', 'latin', [g['shabados'] for g in gold]),
        ('English', 'latin', english),
    ]
    out = []
    for name, expected, lines in cases:
        labels = collections.Counter(GurmukhiLegacy.detect_encoding(l) for l in lines)
        out.append({'input': name, 'expected': expected, 'n': len(lines),
                    'correct': labels[expected], 'labels': dict(labels)})
    return out


def _unique_first(ranked: list[dict]) -> str | None:
    if not ranked:
        return None
    if len(ranked) > 1 and ranked[1]['confidence'] == ranked[0]['confidence']:
        return None  # tie: no unique answer
    return ranked[0]['system']


def eval_identify(gold: list[dict], english: list[str]) -> dict:
    schemes = []
    for scheme, system in SCHEME_SYSTEM.items():
        firsts = collections.Counter()
        unique = top3 = 0
        for g in gold:
            ranked = identify_system(g[scheme], top_n=13)
            firsts[ranked[0]['system']] += 1
            if system:
                unique += _unique_first(ranked) == system
                top3 += system in [r['system'] for r in ranked[:3]]
        schemes.append({'scheme': scheme, 'system': system, 'n': len(gold), 'unique_top1': unique,
                        'top3': top3, 'most_common_top1': firsts.most_common(3)})
    eng = [identify_system(l)[0]['confidence'] for l in english]
    return {'schemes': schemes,
            'english': {'n': len(eng), 'mean_top_conf': sum(eng) / len(eng),
                        'conf_ge_0_5': sum(c >= 0.5 for c in eng)}}


def eval_forward(gold: list[dict]) -> list[dict]:
    out = []
    for scheme, system in SCHEME_SYSTEM.items():
        if not system:
            continue
        r = GurmukhiRomanizer(system)
        exact = word_hits = word_total = 0
        for g in gold:
            pred = r.romanize(g['gurmukhi'])
            exact += pred == g[scheme]
            gw = roman_words(g[scheme])
            word_hits += overlap(roman_words(pred), gw)
            word_total += len(gw)
        out.append({'system': system, 'scheme': scheme, 'n': len(gold), 'exact_lines': exact,
                    'word_hits': word_hits, 'words': word_total})
    return out


def eval_reverse(gold: list[dict]) -> list[dict]:
    """Only the Shackle reverse exists today; scoring it on other schemes gives
    the cross-scheme floor that phase 3 (map-driven reverse) must beat."""
    out = []
    for scheme in ('banidb', 'shabados'):
        hits = in_cands = total = 0
        for g in gold:
            gw = list(words(g['gurmukhi']))
            result = reverse_transliterate(g[scheme])
            hits += overlap(list(words(result.gurmukhi)), gw)
            cands = {w for c in candidate_spellings(result)[:64] for w in words(c)}
            in_cands += sum(1 for w in gw if w in cands)
            total += len(gw)
        out.append({'engine': 'shackle reverse', 'scheme': scheme, 'words': total,
                    'exact': hits, 'in_candidates': in_cands})
    return out


def eval_verse(gold: list[dict], english: list[str], punjabi: list[str]) -> dict:
    """Verse matching: top-1/top-3 per input scheme, partial lines, abstention
    on non-Gurbani input, latency. Top-1 counts a hit when the gold line is
    among the locations of the best match (repeated lines share one match)."""
    t0 = time.perf_counter()
    _corpus()
    build = time.perf_counter() - t0
    times: list[float] = []

    def run(text: str, n: int = 3):
        t = time.perf_counter()
        ms = match_verse(text, top_n=n)
        times.append(time.perf_counter() - t)
        return ms

    def ids(m):
        return {loc.id for loc in m.locations}

    schemes = []
    for scheme in ('banidb', 'shabados', 'gurbaniakhar', 'gurmukhi', 'banidb_ipa'):
        top1 = top3 = 0
        for g in gold:
            ms = run(g[scheme])
            top1 += bool(ms) and g['id'] in ids(ms[0])
            top3 += any(g['id'] in ids(m) for m in ms)
        schemes.append({'scheme': scheme, 'n': len(gold), 'top1': top1, 'top3': top3})
    partial = [g for g in gold if len(g['banidb'].split()) >= 6]
    partial_hits = 0
    for g in partial:
        w = g['banidb'].split()
        ms = run(' '.join(w[:max(4, len(w) * 6 // 10)]))
        partial_hits += bool(ms) and g['id'] in ids(ms[0])
    return {
        'schemes': schemes,
        'partial': {'n': len(partial), 'top1': partial_hits},
        'false_accept': {'punjabi': (sum(bool(run(l)) for l in punjabi), len(punjabi)),
                         'english': (sum(bool(run(l)) for l in english), len(english))},
        'latency_ms': {'median': 1000 * statistics.median(times),
                       'p95': 1000 * sorted(times)[int(0.95 * len(times))]},
        'build_s': build,
    }


def eval_system_reverse(gold: list[dict]) -> dict:
    """Word-level reverse via each system's lexicon index (reverse_words).

    Round trip: gold Gurmukhi words → our forward romanizer → reverse; this
    checks the engine, not real-world input. Real input: the schemes' own
    romanizations of the gold lines, reversed word by word."""
    vocab = sorted({w for g in gold for w in words(g['gurmukhi'])})
    round_trip = []
    for system in ALL_SYSTEMS:
        for delete_schwa in (False, True):
            romans = _forward(system, ' '.join(vocab), delete_schwa).split(' ')
            top1 = top5 = 0
            for w, roman in zip(vocab, romans):
                cands = [c for c, _ in reverse_words(roman, system=system).words[0].candidates] \
                    if roman else []
                top1 += bool(cands) and cands[0] == w
                top5 += w in cands[:5]
            round_trip.append({'system': system, 'delete_schwa': delete_schwa, 'n': len(vocab),
                               'top1': top1, 'top5': top5,
                               'tier': 'near-lossless' if system in NEAR_LOSSLESS else 'lossy'})
    real = []
    for scheme, system in (('banidb', 'sttm'), ('banidb', None), ('shabados', 'shabados'),
                           ('shabados', None), ('banidb_ipa', 'banidb_ipa')):
        found = total = hits = gold_words = 0
        chosen: collections.Counter = collections.Counter()
        for g in gold:
            r = reverse_words(g[scheme], system=system)
            chosen[r.system] += 1
            total += len(r.words)
            found += len(r.words) - len(r.missing)
            gw = list(words(g['gurmukhi']))
            gold_words += len(gw)
            hits += overlap([w.best for w in r.words if w.best], gw)
        real.append({'scheme': scheme, 'system': system or 'auto', 'found': found, 'words': total,
                     'hits': hits, 'gold_words': gold_words, 'chosen': chosen.most_common(2)})
    shackle_romans = _forward('shackle', ' '.join(vocab), False).split(' ')
    old = sum(shackle_to_gurmukhi(r) == w for w, r in zip(vocab, shackle_romans))
    return {'round_trip': round_trip, 'real': real,
            'shackle': {'n': len(vocab), 'rule_based': old,
                        'index': next(r['top1'] for r in round_trip
                                      if r['system'] == 'shackle' and not r['delete_schwa'])}}


def eval_lexicon(gold: list[dict]) -> dict:
    lex, sggs = load_lexicon(), load_lexicon(['sggs'])
    gw = [w for g in gold for w in words(g['gurmukhi'])]
    return {'words': len(gw), 'in_lexicon': sum(w in lex for w in gw),
            'in_sggs': sum(w in sggs for w in gw), 'lexicon_size': len(lex)}


def eval_dakshina(path: Path) -> dict:
    """Word-level top-1 of the Shackle reverse on Dakshina pa test pairs
    (native \\t roman \\t count). IndicXlit reports 47.24% top-1 on this set."""
    candidates = [path / 'pa' / 'lexicons' / 'pa.translit.sampled.test.tsv', path]
    tsv = next((p for p in candidates if p.is_file()), None)
    if tsv is None:
        raise FileNotFoundError(f'no Dakshina pa test TSV under {path}')
    pairs = {}
    for line in tsv.read_text(encoding='utf-8').splitlines():
        native, roman, *_ = line.split('\t')
        pairs.setdefault(roman, set()).add(native)
    hits = sum(reverse_transliterate(roman).gurmukhi in natives for roman, natives in pairs.items())
    return {'file': str(tsv), 'pairs': len(pairs), 'top1': hits}


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------

def report(dakshina: Path | None = None, limit: int | None = None) -> str:
    gold, english = load_gold()[:limit], load_english()
    commit = subprocess.run(['git', 'rev-parse', '--short', 'HEAD'], cwd=REPO,
                            capture_output=True, text=True).stdout.strip() or 'unknown'
    md = [f'# Evaluation baseline\n',
          f'Generated by `python tools/eval.py` on {datetime.date.today()} at commit `{commit}`. '
          f'Gold data: {len(gold)} lines (tests/fixtures/gold/), {len(english)} English lines.\n']

    md += ['## Encoding detection (`detect_encoding`, per line)\n',
           '| input | expected | correct | labels |', '|---|---|---|---|']
    for r in eval_detection(gold, english):
        md.append(f"| {r['input']} | `{r['expected']}` | {pct(r['correct'], r['n'])} | "
                  + ', '.join(f'{k} {v}' for k, v in sorted(r['labels'].items())) + ' |')

    ident = eval_identify(gold, english)
    md += ['\n## System identification (`identify_system`, per line)\n',
           '| gold scheme | repo system | unique top-1 | in top 3 | most common top-1 |',
           '|---|---|---|---|---|']
    for r in ident['schemes']:
        sys_ = f"`{r['system']}`" if r['system'] else 'none yet'
        u = pct(r['unique_top1'], r['n']) if r['system'] else 'n/a'
        t = pct(r['top3'], r['n']) if r['system'] else 'n/a'
        common = ', '.join(f'{s} {n}' for s, n in r['most_common_top1'])
        md.append(f"| {r['scheme']} | {sys_} | {u} | {t} | {common} |")
    e = ident['english']
    md.append(f"\nEnglish lines (should be rejected; there is no reject option yet): mean top confidence "
              f"{e['mean_top_conf']:.2f}, {e['conf_ge_0_5']}/{e['n']} score ≥ 0.5.")

    md += ['\n## Forward fidelity (our romanizer vs the scheme\'s own output)\n',
           '| repo system | gold scheme | exact lines | words matched |', '|---|---|---|---|']
    for r in eval_forward(gold):
        md.append(f"| `{r['system']}` | {r['scheme']} | {pct(r['exact_lines'], r['n'])} | "
                  f"{pct(r['word_hits'], r['words'])} |")

    md += ['\n## Reverse transliteration (word level)\n',
           'Only the Shackle reverse exists; on other schemes this is the floor that phase 3 must beat.\n',
           '| engine | input scheme | exact words | truth in candidates |', '|---|---|---|---|']
    for r in eval_reverse(gold):
        md.append(f"| {r['engine']} | {r['scheme']} | {pct(r['exact'], r['words'])} | "
                  f"{pct(r['in_candidates'], r['words'])} |")

    vm = eval_verse(gold, english, load_punjabi())
    md += ['\n## Verse matching (`match_verse`, per line)\n',
           '| input scheme | top-1 | top-3 |', '|---|---|---|']
    for r in vm['schemes']:
        md.append(f"| {r['scheme']} | {pct(r['top1'], r['n'])} | {pct(r['top3'], r['n'])} |")
    fp, fe = vm['false_accept']['punjabi'], vm['false_accept']['english']
    md.append(f"\nPartial lines (first ~60% of BaniDB words): top-1 {pct(vm['partial']['top1'], vm['partial']['n'])}. "
              f"False accepts: romanized modern Punjabi {fp[0]}/{fp[1]}, English {fe[0]}/{fe[1]}. "
              f"Latency median {vm['latency_ms']['median']:.1f} ms, p95 {vm['latency_ms']['p95']:.1f} ms; "
              f"index build on first use {vm['build_s']:.1f} s.")

    sr = eval_system_reverse(gold)
    md += ['\n## System-based reverse (`reverse_words`, word level)\n',
           'Round trip: gold words → our forward romanizer → reverse. This checks the engine '
           'and the index, not real-world input.\n',
           '| system | tier | exact (top-1) | in top 5 | exact, schwa deleted | in top 5, schwa deleted |',
           '|---|---|---|---|---|---|']
    by = collections.defaultdict(dict)
    for r in sr['round_trip']:
        by[(r['system'], r['tier'])][r['delete_schwa']] = r
    for (system, tier), d in by.items():
        a, b = d[False], d[True]
        md.append(f"| `{system}` | {tier} | {pct(a['top1'], a['n'])} | {pct(a['top5'], a['n'])} | "
                  f"{pct(b['top1'], b['n'])} | {pct(b['top5'], b['n'])} |")
    md += ['\nReal input (the schemes\' own romanizations, reversed word by word):\n',
           '| input scheme | system | words found | gold words recovered | system chosen |',
           '|---|---|---|---|---|']
    for r in sr['real']:
        md.append(f"| {r['scheme']} | {r['system']} | {pct(r['found'], r['words'])} | "
                  f"{pct(r['hits'], r['gold_words'])} | "
                  + ', '.join(f'{s} {n}' for s, n in r['chosen']) + ' |')
    sh = sr['shackle']
    md.append(f"\nShackle round trip, exact words: rule-based `reverse_transliterate` "
              f"{pct(sh['rule_based'], sh['n'])}, lexicon index {pct(sh['index'], sh['n'])}.")

    lx = eval_lexicon(gold)
    md += ['\n## Lexicon coverage\n',
           f"{pct(lx['in_lexicon'], lx['words'])} of gold Gurmukhi words are in the bundled lexicon "
           f"({lx['lexicon_size']} words); {pct(lx['in_sggs'], lx['words'])} are in its SGGS part. "
           'Expected near 100%, since both come from Shabad OS; a drop flags a tokenisation change.']

    if dakshina:
        d = eval_dakshina(dakshina)
        md += ['\n## Dakshina pa test set\n',
               f"Shackle reverse top-1: {pct(d['top1'], d['pairs'])} of {d['pairs']} romanizations "
               f"(IndicXlit reports 47.24%). File: `{d['file']}`."]
    return '\n'.join(md) + '\n'


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--write', type=Path, help='also write the report to this file')
    ap.add_argument('--dakshina', type=Path, help='Dakshina dataset dir (or the pa test TSV)')
    ap.add_argument('--limit', type=int, help='use only the first N gold lines (quick check)')
    args = ap.parse_args()
    md = report(args.dakshina, args.limit)
    print(md)
    if args.write:
        args.write.parent.mkdir(parents=True, exist_ok=True)
        args.write.write_text(md, encoding='utf-8')


if __name__ == '__main__':
    main()
