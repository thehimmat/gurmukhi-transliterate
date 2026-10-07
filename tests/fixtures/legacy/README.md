# Legacy-font fixtures

Each `NAME.ENCODING.txt` holds lines as typed in a legacy font, and
`NAME.unicode.txt` the same lines in Unicode Gurmukhi. Only verse (public-domain
scripture and historical text) is included, never a modern translation.

| file | font | source | how the Unicode was checked |
|---|---|---|---|
| `japji.gurbaniakhar.txt`, `ghazal1.gurbaniakhar.txt` | GurbaniAkhar | | by hand |
| `chandi_charitar.joy.txt` | unnamed 1990s Joy-like font (`MSTT31c5cb`) | Chandi Charitar II, Punjabi edition PDF | every word matches the canonical Dasam Granth line (`match_verse`) |
| `gur_sobha.asees.txt` | Asees | Sri Gur Sobha (Sainapati), Institute of Sikh Studies, 2014 | every word is in the Gurbani lexicon; read through, not yet hand-checked by a fluent reader |
| `zafarnama.anandpursahib.txt` | AnandpurSahib | Zafarnama with Persian text and English translation (2005 PDF) | every word appears in the Dasam Granth's Zafarnama |
| `gur_sobha_joy.joy.txt` | Joy | the same book's introduction (quoted verse) | every word is in the Gurbani lexicon; first line agrees with the book's printed romanization; not yet hand-checked |

The legacy text is the PDFs' text layer, decoded as Windows-1252. For the
Chandi Charitar PDF, pdfminer applies Adobe StandardEncoding (so `'` arrives
as `’`); those characters were mapped back to their bytes first.
