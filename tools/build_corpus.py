"""Build gurmukhi_transliterate/data/lines.tsv.gz (the verse matcher's corpus).

Usage:
    python tools/build_corpus.py path/to/master.sqlite

Every primary line of the Shabad OS database (see build_lexicon.py for the
pinned version), in reading order: source, then section, line group (shabad)
and line order. Columns: id, source, shabad, page, line, gurmukhi. Vishraam
marks are removed (the words are untouched), so repeated lines compare equal.
"""

from __future__ import annotations

import gzip
import io
import json
import sqlite3
import sys
import unicodedata
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / 'tools'))
from build_lexicon import DB_VERSION, SOURCE_OF  # noqa: E402

OUT = REPO / 'gurmukhi_transliterate' / 'data' / 'lines.tsv.gz'
SOURCE_ORDER = ['SGGS', 'SDGR', 'VBGJ', 'KSBG', 'GZNL', 'JBNL', 'GJNL', 'ZNNL', 'SRBL', 'ARDS']
_VISHRAAMS = str.maketrans('', '', ';,.')


def build(db_path: str) -> list[tuple]:
    con = sqlite3.connect(f'file:{db_path}?mode=ro', uri=True)
    rows = con.execute(
        """
        SELECT al.line_id, s.source_id, g.id, al.additional, al.data,
               s.source_order, g.section_order, l.line_group_order
        FROM asset_lines al
        JOIN lines l ON l.id = al.line_id
        JOIN line_groups g ON g.id = l.line_group_id
        JOIN sections s ON s.id = g.section_id
        WHERE al.type = 'primary'
        """
    ).fetchall()
    rank = {s: i for i, s in enumerate(SOURCE_ORDER)}
    rows.sort(key=lambda r: (rank.get(r[1], len(rank)), r[5], r[6], r[7]))
    out = []
    for line_id, source_id, shabad, additional, text, *_ in rows:
        meta = json.loads(additional or '{}')
        text = ' '.join(unicodedata.normalize('NFC', text or '').translate(_VISHRAAMS).split())
        out.append((line_id, SOURCE_OF.get(source_id, 'other'), shabad,
                    meta.get('page', ''), meta.get('line', ''), text))
    return out


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    rows = build(sys.argv[1])
    buf = io.StringIO()
    buf.write('id\tsource\tshabad\tpage\tline\tgurmukhi\n')
    for r in rows:
        buf.write('\t'.join(str(x) for x in r) + '\n')
    with open(OUT, 'wb') as raw, gzip.GzipFile(fileobj=raw, mode='wb', mtime=0, compresslevel=9) as gz:
        gz.write(buf.getvalue().encode('utf-8'))
    print(f'{DB_VERSION}: {len(rows)} lines → {OUT.relative_to(REPO)} ({OUT.stat().st_size // 1024} KB)')


if __name__ == '__main__':
    main()
