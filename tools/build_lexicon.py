"""Build gurmukhi_transliterate/data/lexicon.tsv.gz from the Shabad OS database.

Usage:
    python tools/build_lexicon.py path/to/master.sqlite

Get the database (pinned version) with:
    npm pack @shabados/database@5.0.0-next.0 && tar xzf shabados-database-*.tgz
    # → package/dist/master.sqlite

Only the primary (scripture) text is counted, never translations. Output is a
gzipped TSV: word, total, then one count column per source in SOURCES order.
Words are NFC-normalised Gurmukhi (nukta letters decomposed, as NFC requires).
"""

from __future__ import annotations

import collections
import gzip
import io
import sqlite3
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
from gurmukhi_transliterate.lexicon import SOURCES, words  # noqa: E402

DB_VERSION = '@shabados/database@5.0.0-next.0'
OUT = REPO / 'gurmukhi_transliterate' / 'data' / 'lexicon.tsv.gz'

# Shabad OS source id → our source bucket
SOURCE_OF = {
    'SGGS': 'sggs',
    'SDGR': 'dasam',
    'VBGJ': 'bhai_gurdas', 'KSBG': 'bhai_gurdas',
    'GZNL': 'bhai_nand_lal', 'JBNL': 'bhai_nand_lal',
    'GJNL': 'bhai_nand_lal', 'ZNNL': 'bhai_nand_lal',
}


def build(db_path: str) -> dict[str, collections.Counter]:
    con = sqlite3.connect(f'file:{db_path}?mode=ro', uri=True)
    rows = con.execute(
        """
        SELECT s.source_id, al.data
        FROM asset_lines al
        JOIN lines l ON l.id = al.line_id
        JOIN line_groups g ON g.id = l.line_group_id
        JOIN sections s ON s.id = g.section_id
        WHERE al.type = 'primary'
        """
    )
    counts: dict[str, collections.Counter] = collections.defaultdict(collections.Counter)
    for source_id, text in rows:
        bucket = SOURCE_OF.get(source_id, 'other')
        for w in words(text or ''):
            counts[w][bucket] += 1
    return counts


def write(counts: dict[str, collections.Counter]) -> None:
    buf = io.StringIO()
    buf.write('word\ttotal\t' + '\t'.join(SOURCES) + '\n')
    for w in sorted(counts, key=lambda w: (-sum(counts[w].values()), w)):
        c = counts[w]
        buf.write(f'{w}\t{sum(c.values())}\t' + '\t'.join(str(c[s]) for s in SOURCES) + '\n')
    OUT.parent.mkdir(parents=True, exist_ok=True)
    # mtime=0 keeps the file byte-identical across rebuilds
    with open(OUT, 'wb') as raw, gzip.GzipFile(fileobj=raw, mode='wb', mtime=0, compresslevel=9) as gz:
        gz.write(buf.getvalue().encode('utf-8'))


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    counts = build(sys.argv[1])
    write(counts)
    per = {s: sum(1 for c in counts.values() if c[s]) for s in SOURCES}
    tokens = {s: sum(c[s] for c in counts.values()) for s in SOURCES}
    print(f'{DB_VERSION}: {len(counts)} distinct words → {OUT.relative_to(REPO)} '
          f'({OUT.stat().st_size // 1024} KB)')
    for s in SOURCES:
        print(f'  {s:14} {per[s]:>7} distinct  {tokens[s]:>8} running')


if __name__ == '__main__':
    main()
