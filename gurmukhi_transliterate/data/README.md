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

## ngrams.tsv.gz

These are character trigram counts used by `detect_latin` (English vs romanized
Gurmukhi) and `identify_system` (which romanization system). There is one model
per romanization system and one for English. Each system's model is trained on
that system's romanization of `lexicon.tsv.gz`, with and without schwa
deletion. The columns are `model`, `gram` and `count`, covering orders 1–3,
with `^` and `$` padding the word boundaries. Rebuild it with
`python tools/build_models.py path/to/scowl-wl50.txt` (the output is
byte-for-byte reproducible).

The English model counts only the lowercase entries (no proper nouns) of a word
list generated from SCOWL/ESDB at size 50, American spelling, from
[en-wl/wordlist](https://github.com/en-wl/wordlist) at commit `1e5b7d3`:
`./scowl --db scowl.db word-list 50 A 1`. That list is 61,650 words; only the
n-gram counts are bundled, not the words. It is a non-Australian list of size
80 or below, so only the following notice applies:

> Copyright 2000-2026 by Kevin Atkinson
>
> Permission to use, copy, modify, distribute, and sell any part of the English
> Speller Database (ESDB, previously known as SCOWLv2), or word lists
> created from it, is hereby granted without fee, provided that the above
> copyright notice appears in all copies and that both the above copyright
> notice and this notice appear in supporting documentation.  Kevin Atkinson
> makes no representations about the suitability of this database for any
> purpose.  It is provided "as is" without express or implied warranty.
>
> ESDB is derived from many sources, most of which are in the Public Domain.
> Data from the Corpus of Contemporary American English (COCA) was also used.
>
> All data from COCA comes from 3-gram data that is not freely available;
> however, the usage is within the rights given by the NDA that was signed when
> purchasing the data.  More information on COCA is available at
> https://www.english-corpora.org/coca/.
>
> The primary source of words for ESDB comes from 12dicts and ENABLE2K.  Both
> are in the Public Domain, but Alan Beale <biljir@pobox.com> deserves special
> credit as he is the author of 12dicts and a major contributor to ENABLE2K.  In
> addition, he gave me an incredible amount of feedback and created a number of
> special lists in order to help improve the overall quality of ESDB.
