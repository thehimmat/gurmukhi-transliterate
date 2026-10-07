# Gold fixtures (real romanized text)

Used by `tools/eval.py`. None of this is output from this library.

## lines.tsv

There are 500 lines: 300 from Guru Granth Sahib, 100 from Dasam Granth and 100
from the Vaaran of Bhai Gurdas. They were sampled with a fixed seed from the
public-domain Shabad OS database (`@shabados/database@5.0.0-next.0`, see
`gurmukhi_transliterate/data/README.md`). Vishraam marks were removed.

Each line is romanized by the scheme's own code:

| column | produced by | scheme |
|---|---|---|
| `gurbaniakhar` | anvaad-js 1.5.1 `unicode(text, true)` (MIT, Khalis Foundation) | GurbaniAkhar ASCII font encoding |
| `banidb` | anvaad-js 1.5.1 `translit(ascii)` | BaniDB / SikhiToTheMax English (this repo's `sttm`) |
| `banidb_ipa` | anvaad-js 1.5.1 `translit(ascii, 'ipa')` | BaniDB IPA (this repo's `banidb_ipa`) |
| `shabados` | gurmukhi-utils 3.2.2 `toEnglish(text)` (GPL-3.0; run to produce data, no code copied) | Shabad OS English (no matching system in this repo yet) |

The file is TSV with `\` as the escape character. Rebuild it with
`python tools/build_gold.py path/to/master.sqlite`.

## english.txt

English lines written for this repo: headings, prose and Sikh names. They are
negatives for detection and system identification.

## Not committed

The Dakshina Punjabi test set (CC BY-SA 4.0) is read from a local path with
`tools/eval.py --dakshina DIR`.
