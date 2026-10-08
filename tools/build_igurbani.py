"""Build tests/fixtures/igurbani.tsv: iGurbani's romanization, for sttm_legacy.

Usage:
    python tools/build_igurbani.py

iGurbani (igurbani.com) still serves the pre-BaniDB SikhiToTheMax scheme that
the sttm_legacy system follows. No code for it is published (anvaad-js's old
translit is a different scheme), so the reference is what the site serves:
each shabad page embeds its verses' Unicode Gurmukhi and English
transliteration as JSON. This samples shabads of Guru Granth Sahib (fixed
seed) and records every verse; a shabad the site keeps failing to serve is
skipped and reported. Gurmukhi is stored as served, vishraam
punctuation included.
"""

from __future__ import annotations

import csv
import json
import random
import re
import sys
import time
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
OUT = REPO / 'tests' / 'fixtures' / 'igurbani.tsv'
URL = 'https://www.igurbani.com/shabad/{}'
SHABADS, N, SEED = range(1, 5500), 150, 4   # Guru Granth Sahib shabad ids
COLUMNS = ['id', 'shabad', 'gurmukhi', 'igurbani']
HEADERS = {'User-Agent': 'gurmukhi-transliterate (conformance fixture builder)'}
DATA = re.compile(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', re.S)


def fetch(shabad: int, tries: int = 3) -> list[dict]:
    for attempt in range(tries):
        try:
            req = urllib.request.Request(URL.format(shabad), headers=HEADERS)
            html = urllib.request.urlopen(req, timeout=30).read().decode('utf-8')
            break
        except OSError:
            if attempt == tries - 1:
                raise
            time.sleep(2 ** attempt)
    data = json.loads(DATA.search(html).group(1))['props']['pageProps']['shabad']
    return [{'id': v['uid'], 'shabad': shabad, 'gurmukhi': v['gurmukhiUnicode'],
             'igurbani': v['transliteration']['english']} for v in data['verses']]


def main() -> None:
    rows, skipped = [], []
    for shabad in random.Random(SEED).sample(SHABADS, N):
        try:
            rows += fetch(shabad)
        except OSError as e:
            skipped.append(shabad)
            print(f'skipped shabad {shabad}: {e}', file=sys.stderr)
        time.sleep(0.5)
    with open(OUT, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, COLUMNS, delimiter='\t', lineterminator='\n',
                           quoting=csv.QUOTE_NONE, escapechar='\\')
        w.writeheader()
        w.writerows(rows)
    print(f'{len(rows)} lines from {N - len(skipped)} shabads → {OUT.relative_to(REPO)}', file=sys.stderr)


if __name__ == '__main__':
    main()
