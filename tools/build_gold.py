"""Build tests/fixtures/gold/lines.tsv: real romanizations of public-domain lines.

Usage:
    python tools/build_gold.py path/to/master.sqlite [--node-modules DIR]

Samples lines (fixed seed) from the Shabad OS database and romanizes each with
the schemes' own code, so no fixture is this library's own output:
  gurbaniakhar  anvaad-js unicode(…, true)       — GurbaniAkhar ASCII encoding
  banidb        anvaad-js translit(…)             — BaniDB / SikhiToTheMax English
  banidb_ipa    anvaad-js translit(…, 'ipa')      — BaniDB IPA
  shabados      gurmukhi-utils toEnglish(…)       — Shabad OS English
Without --node-modules, the pinned packages are installed into a temp dir (npm).
"""

from __future__ import annotations

import argparse
import csv
import json
import random
import sqlite3
import subprocess
import sys
import tempfile
import unicodedata
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
OUT = REPO / 'tests' / 'fixtures' / 'gold' / 'lines.tsv'
PACKAGES = ['anvaad-js@1.5.1', 'gurmukhi-utils@3.2.2']
SAMPLE = {'SGGS': ('sggs', 300), 'SDGR': ('dasam', 100), 'VBGJ': ('bhai_gurdas', 100)}
SEED = 16
COLUMNS = ['id', 'source', 'gurmukhi', 'gurbaniakhar', 'banidb', 'banidb_ipa', 'shabados']

_VISHRAAMS = str.maketrans('', '', ';,.')


def sample_lines(db_path: str) -> list[dict]:
    con = sqlite3.connect(f'file:{db_path}?mode=ro', uri=True)
    rng = random.Random(SEED)
    picked = []
    for source_id, (source, n) in SAMPLE.items():
        rows = con.execute(
            """
            SELECT al.line_id, al.data FROM asset_lines al
            JOIN lines l ON l.id = al.line_id
            JOIN line_groups g ON g.id = l.line_group_id
            JOIN sections s ON s.id = g.section_id
            WHERE al.type = 'primary' AND s.source_id = ?
            ORDER BY al.line_id
            """,
            (source_id,),
        ).fetchall()
        for line_id, text in rng.sample(rows, n):
            text = ' '.join(unicodedata.normalize('NFC', text).translate(_VISHRAAMS).split())
            picked.append({'id': line_id, 'source': source, 'gurmukhi': text})
    return picked


def romanize(lines: list[dict], node_modules: Path) -> list[dict]:
    script = REPO / 'tools' / 'gold_romanize.cjs'
    payload = json.dumps([{'id': l['id'], 'gurmukhi': l['gurmukhi']} for l in lines])
    res = subprocess.run(['node', str(script), str(node_modules)], input=payload,
                         capture_output=True, text=True, check=True)
    by_id = {r['id']: r for r in json.loads(res.stdout)}
    return [{**l, **by_id[l['id']]} for l in lines]


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('db')
    ap.add_argument('--node-modules', type=Path)
    args = ap.parse_args()
    lines = sample_lines(args.db)
    if args.node_modules:
        rows = romanize(lines, args.node_modules)
    else:
        with tempfile.TemporaryDirectory() as tmp:
            subprocess.run(['npm', 'install', '--silent', '--prefix', tmp, *PACKAGES], check=True)
            rows = romanize(lines, Path(tmp) / 'node_modules')
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, COLUMNS, delimiter='\t', lineterminator='\n', quoting=csv.QUOTE_NONE,
                           escapechar='\\')
        w.writeheader()
        for r in rows:
            w.writerow({k: r[k] for k in COLUMNS})
    print(f'{len(rows)} lines → {OUT.relative_to(REPO)}')


if __name__ == '__main__':
    sys.exit(main())
