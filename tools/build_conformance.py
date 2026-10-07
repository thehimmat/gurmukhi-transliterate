"""Build tests/fixtures/conformance.tsv: scheme outputs to match byte for byte.

Usage:
    python tools/build_conformance.py [--node-modules DIR]

Samples 1,200 lines (fixed seed, every source) from the bundled corpus
(gurmukhi_transliterate/data/lines.tsv.gz) and records what each scheme's own
code produces for them (see tools/gold_romanize.cjs): BaniDB English and IPA
(anvaad-js), and Shabad OS English (gurmukhi-utils). Tests check that this
library's sttm, banidb_ipa and shabados systems reproduce them exactly.
"""

from __future__ import annotations

import argparse
import csv
import gzip
import random
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / 'tools'))
from build_gold import PACKAGES, romanize  # noqa: E402

OUT = REPO / 'tests' / 'fixtures' / 'conformance.tsv'
N, SEED = 1200, 26
COLUMNS = ['id', 'source', 'gurmukhi', 'banidb', 'banidb_ipa', 'shabados']


def sample() -> list[dict]:
    raw = gzip.decompress((REPO / 'gurmukhi_transliterate' / 'data' / 'lines.tsv.gz').read_bytes())
    rows = [r.split('\t') for r in raw.decode('utf-8').splitlines()[1:]]
    rows = [r for r in rows if r[5].strip()]
    return [{'id': r[0], 'source': r[1], 'gurmukhi': r[5]} for r in random.Random(SEED).sample(rows, N)]


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--node-modules', type=Path)
    args = ap.parse_args()
    lines = sample()
    if args.node_modules:
        rows = romanize(lines, args.node_modules)
    else:
        with tempfile.TemporaryDirectory() as tmp:
            subprocess.run(['npm', 'install', '--silent', '--prefix', tmp, *PACKAGES], check=True)
            rows = romanize(lines, Path(tmp) / 'node_modules')
    with open(OUT, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, COLUMNS, delimiter='\t', lineterminator='\n',
                           quoting=csv.QUOTE_NONE, escapechar='\\')
        w.writeheader()
        for r in rows:
            w.writerow({k: r[k] for k in COLUMNS})
    print(f'{len(rows)} lines → {OUT.relative_to(REPO)}')


if __name__ == '__main__':
    main()
