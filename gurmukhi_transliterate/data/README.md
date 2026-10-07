# Bundled data

## lexicon.tsv.gz

Word frequencies of Gurbani and related texts, used to rank candidate spellings
(reverse transliteration, verse matching). Load it with
`gurmukhi_transliterate.lexicon.load_lexicon()`.

- **Source:** [Shabad OS database](https://github.com/shabados/database),
  npm `@shabados/database@5.0.0-next.0`, primary (scripture) text only. No
  translations are used.
- **Licence:** Shabad OS identifies these Gurbani and Panthic texts as being in
  the [public domain](https://creativecommons.org/publicdomain/mark/1.0/), on
  condition that the words are not distorted or altered. This file only counts
  words; it doesn't change them. With thanks to the Shabad OS project.
- **Format:** gzipped UTF-8 TSV. The columns are `word`, `total`, `sggs`, `dasam`,
  `bhai_gurdas`, `bhai_nand_lal` and `other`. Words are NFC-normalised Gurmukhi,
  with vishraam marks, punctuation, digits and zero-width joiners removed.
  Hyphenated compounds are split.
- **Rebuild:** `python tools/build_lexicon.py path/to/master.sqlite`. The output is
  byte-for-byte reproducible.

| source | distinct words | running words |
|---|---|---|
| sggs (Guru Granth Sahib) | 29,494 | 397,849 |
| dasam (Dasam Granth) | 36,437 | 417,431 |
| bhai_gurdas (Vaaran, Kabitt Savaiye) | 16,413 | 84,546 |
| bhai_nand_lal (largely Persian vocabulary) | 3,978 | 15,788 |
| other (Sarabloh Granth excerpts, Ardas) | 452 | 766 |
| **all** | **67,355** | **916,380** |

## lines.tsv.gz

This is the corpus that `match_verse` searches: every primary line of the same
Shabad OS release (141,264 lines), in reading order. The columns are `id`,
`source`, `shabad` (line group), `page` (ang for SGGS), `line` and `gurmukhi`.
Vishraam marks were removed; the words are unchanged. The same public-domain
terms apply. Rebuild it with `python tools/build_corpus.py path/to/master.sqlite`
(the output is byte-for-byte reproducible).
