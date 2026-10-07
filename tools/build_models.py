"""Build gurmukhi_transliterate/data/ngrams.tsv.gz: character trigram counts
for every romanization system and for English.

Usage:
    python tools/build_models.py path/to/scowl-wl50.txt

Each system's model is trained on its own romanization of the bundled lexicon
(both schwa modes; case kept, so BaniDB's T/R count as evidence). The English
model is trained on SCOWL/ESDB size 50, American, lowercase entries only (no
proper nouns). Produce that list from https://github.com/en-wl/wordlist with:

    make && ./scowl --db scowl.db word-list 50 A 1 > scowl-wl50.txt

The output is a gzipped TSV of `model, n-gram, count` (orders 1-3, with ^ and $
as word-boundary padding) and is byte-for-byte reproducible.
"""

from __future__ import annotations

import collections
import gzip
import io
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
from gurmukhi_transliterate.language import ORDER, grams  # noqa: E402
from gurmukhi_transliterate.lexicon import load_lexicon  # noqa: E402
from gurmukhi_transliterate.system_reverse import ALL_SYSTEMS, _forward  # noqa: E402

OUT = REPO / 'gurmukhi_transliterate' / 'data' / 'ngrams.tsv.gz'


def counts(train: set[str]) -> collections.Counter:
    c: collections.Counter = collections.Counter()
    for w in sorted(train):
        c.update(grams(w))
    return c


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    words = list(load_lexicon())
    models: dict[str, collections.Counter] = {}
    for system in ALL_SYSTEMS:
        train: set[str] = set()
        for delete_schwa in (False, True):
            train.update(w for w in _forward(system, ' '.join(words), delete_schwa).split(' ') if w)
        models[system] = counts(train)
    english = set(Path(sys.argv[1]).read_text(encoding='utf-8').split())
    models['english'] = counts({w for w in english if re.fullmatch(r'[a-z]+', w)})

    buf = io.StringIO()
    buf.write(f'model\tgram\tcount\t# order {ORDER}\n')
    for name in sorted(models):
        for g, n in sorted(models[name].items()):
            buf.write(f'{name}\t{g}\t{n}\n')
    with open(OUT, 'wb') as raw, gzip.GzipFile(fileobj=raw, mode='wb', mtime=0, compresslevel=9) as gz:
        gz.write(buf.getvalue().encode('utf-8'))
    total = sum(len(c) for c in models.values())
    print(f'{len(models)} models, {total} n-grams → {OUT.relative_to(REPO)} ({OUT.stat().st_size // 1024} KB)')


if __name__ == '__main__':
    main()
