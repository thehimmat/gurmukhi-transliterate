# Legacy-font fixtures

Each `NAME.ENCODING.txt` holds lines as typed in a legacy font, and
`NAME.unicode.txt` the same lines in Unicode Gurmukhi. Only verse (public-domain
scripture and historical text) is included, never a modern translation.

| file | font | source | how the Unicode was checked |
|---|---|---|---|
| `japji.gurbaniakhar.txt`, `ghazal1.gurbaniakhar.txt` | GurbaniAkhar | | by hand |
| `chandi_charitar.joy.txt` | unnamed 1990s Joy-like font (`MSTT31c5cb`) | Chandi Charitar II, Punjabi edition PDF | every word matches the canonical Dasam Granth line (`match_verse`) |
| `gur_sobha.asees.txt` | Asees | Sri Gur Sobha (Sainapati), Institute of Sikh Studies, 2014 | every word is in the Gurbani lexicon; hand-checked against the book (2026-10-07) |
| `zafarnama.anandpursahib.txt` | AnandpurSahib | Zafarnama with Persian text and English translation (2005 PDF) | every word appears in the Dasam Granth's Zafarnama |
| `gur_sobha_joy.joy.txt` | Joy | the same book's introduction (quoted verse) | every word is in the Gurbani lexicon; hand-checked against the book (2026-10-07) |

The legacy text is the PDFs' text layer, decoded as Windows-1252. For the
Chandi Charitar PDF, pdfminer applies Adobe StandardEncoding (so `'` arrives
as `’`); those characters were mapped back to their bytes first.

The Sri Gur Sobha lines are a sample: evenly spaced picks from the lines that
converted with no unmapped keys and with every word in the lexicon. They are
on these pages of the PDF (the viewer's page number, not the printed one):

| file | line → PDF page |
|---|---|
| `gur_sobha.asees.txt` | 1→46, 2→70, 3→106, 4→124, 5→146, 6→172, 7→196, 8→224, 9→246, 10→264, 11→292, 12→314, 13→348, 14→378, 15→400 |
| `gur_sobha_joy.joy.txt` | 1–2→38, 3–4→39, 5–6→40, 7–9→41, 10–12→42 |
