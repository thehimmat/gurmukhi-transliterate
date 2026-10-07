# Telling romanized Punjabi/Gurbani (and Hindi) apart from English in Latin-script text, by word and by line

Research date: 2026-10-06. Network note: aclanthology.org, arxiv.org, huggingface.co, researchgate, semanticscholar and similar paper hosts were blocked by the egress proxy in this session. Numbers from papers below therefore come from (a) GitHub READMEs and model tables that were downloaded and read in full (IndicLID, GlotLID, CLD3, lingua-py, langid.py, fastText, OpenLID, wordfreq, Shabad OS gurmukhi-utils, word lists), or (b) search-engine snippets and abstracts. Items in group (b) are marked "(snippet)" and should be checked against the PDF before anyone quotes them as final.

## Q1. What the code-mixed LID literature reports: features and accuracy

### Takeaway
For word-level LID of romanized Indic text mixed with English, the methods that consistently work are character n-gram classifiers combined with dictionary lookup, with word context added through a CRF (or another sequence model). Reported token accuracies are about 88% for a dictionary plus n-gram system trained on little data, about 95–97% for CRFs on social-media corpora (Bengali/Hindi/Punjabi with English), and 96–98% for fine-tuned multilingual transformers (mBERT, XLM-R). Context or CRF features usually add a few points over word-only classifiers.

### Cited Findings
- **FIRE 2013 Transliterated Search, subtask 1 (query word labelling).** The task was word-level language ID for Indian languages written in Roman script and mixed with English. Gella, Sharma and Bali (Microsoft Research India) submitted the best-performing system. It used maximum-entropy classifiers on character n-grams of Hindi and English words, plus hierarchical dictionaries to speed up LID and back-transliteration. — [MSR publication page](https://www.microsoft.com/en-us/research/publication/query-word-labeling-and-back-transliteration-for-indian-languages-shared-task-system-description/); [Semantic Scholar entry](https://www.semanticscholar.org/paper/Query-word-labeling-and-Back-Transliteration-for-Gella-Sharma/2a8e510005a633cbbbe1c67fe670d7f09ba01650)
- (snippet) A FIRE-2013 Hindi-English system reported English token precision of 0.895 and Indian-language token recall of 0.915, and back-transliteration accuracy of only 0.15. The snippet comes from an academia.edu copy titled "Hindi-English Language Identification, Named Entity Recognition and Back Transliteration: Shared Task System Description". I could not confirm whether these are Gella et al.'s exact figures. — [academia.edu](https://www.academia.edu/68316695/Hindi_English_Language_Identification_Named_Entity_Recognition_and_Back_Transliteration_Shared_Task_System_Description)
- The MSIR (Mixed Script IR) track ran at FIRE from 2013 to 2016, and a consolidated report covers all four years. — [MSIR@FIRE: A Comprehensive Report from 2013 to 2016 (SN Computer Science)](https://link.springer.com/article/10.1007/s42979-019-0058-0); [Overview of FIRE 2013 Track on Transliterated Search](https://www.researchgate.net/publication/297664872_Overview_of_the_FIRE_2013_Track_on_Transliterated_Search)
- **Barman, Das, Wagner & Foster (2014), "Code Mixing: A Challenge for Language Identification in the Language of Social Media"** (First Workshop on Computational Approaches to Code Switching, EMNLP 2014). The data was Facebook posts and comments mixing Bengali, Hindi and English, more than 180,000 tokens annotated at word level. They compared four approaches: an unsupervised dictionary-based method, supervised word-level classification without context, the same with contextual clues, and CRF sequence labelling. (snippet) The best accuracy reported in citing work is 95.76% for statistical models using monolingual dictionaries. Features were word context, capitalization, character n-grams and word length. — [ACL Anthology W14-3902](https://aclanthology.org/W14-3902/); figure via [Shallow Parsing Pipeline for Hindi-English Code-Mixed Social Media Text (arXiv 1604.03136)](https://arxiv.org/pdf/1604.03136) search snippet
- (snippet) On Hindi-English LID, CRF models beat neural-network models by 3–5 percentage points (W18-3206, "Language Identification and Analysis of Code-Switched ..."). — [ACL W18-3206](https://aclanthology.org/W18-3206.pdf)
- **LinCE** is a benchmark of 11 corpora covering four code-switched pairs (Spanish-English, Nepali-English, Hindi-English, MSA-Egyptian Arabic). It has four tasks, one of which is LID. Punjabi-English is not included. (snippet) Recent mBERT-based systems report weighted F1 of 96.72 and 96.45 on the LinCE Hindi-English LID dev set. — [LinCE, LREC 2020](https://aclanthology.org/2020.lrec-1.223/); [arXiv 2005.04322](https://arxiv.org/abs/2005.04322)
- (snippet) A word-level CRF trained by MSR India for the code-switching shared task. — [ResearchGate: "Word-level Language Identification using CRF: Code-switching Shared Task Report of MSR India System"](https://www.researchgate.net/publication/301409063_Word-level_Language_Identification_using_CRF_Code-switching_Shared_Task_Report_of_MSR_India_System)
- **Punjabi-English specifically** (all snippets; I could not open the PDFs):
  - A corpus of Facebook and Twitter messages with about 80,025 tokens, tagged English, Punjabi, Universal, Mixed, Named Entity and Acronym. A CRF baseline reached 96.8% accuracy under five-fold cross-validation, and about 97% on the bilingual English-Punjabi set. The work also built a dictionary of romanized-to-Gurmukhi pairs for normalization. Most likely source: "Language Identification and Normalization of Code Mixed English and Punjabi Text" (ICON 2020 demo). — [ACL 2020.icon-demos.12](https://aclanthology.org/2020.icon-demos.12.pdf); [Papers with Code entry](https://paperswithcode.com/paper/language-identification-and-normalization-of)
  - With a small dataset, a combined morphological-dictionary and character n-gram language model approach reached 88% (snippet; same search cluster). — [ACL 2020.icon-demos.12](https://aclanthology.org/2020.icon-demos.12.pdf)
  - XLM-RoBERTa reached 98% on English-Punjabi code-mixed data. The figure appears in a 2023–2024 study; the candidates are Uchoi & Kaur "Language Identification of English and Punjabi Code-Mixing and Code-Switching Sentences" (SSRN) or the JESTR 17(1) 2024 article. — [SSRN 4473174](https://papers.ssrn.com/sol3/Delivery.cfm/SSRN_ID4473174_code5909045.pdf?abstractid=4473174&mirid=1); [JESTR 17(1) 2024](https://jestr.org/downloads/Volume17Issue1/fulltext91712024.pdf)
- A related line of work: "Word-Level Language Identification and Back Transliteration of Romanized Text" and "Word Level Language Identification in Code-Mixed Data using Word Embedding Methods for Indian Languages". — [ResearchGate 301454369](https://www.researchgate.net/publication/301454369_Word-Level_Language_Identification_and_Back_Transliteration_of_Romanized_Text); [ResearchGate 329392142](https://www.researchgate.net/publication/329392142_Word_Level_Language_Identification_in_Code-Mixed_Data_using_Word_Embedding_Methods_for_Indian_Languages)

### Inferences
- The ordering of features is consistent across Hindi-, Bengali- and Punjabi-English studies:
  - Dictionary lookup alone is the weakest, because romanized Indic spelling varies too much for a fixed lexicon to cover.
  - Character n-grams (roughly 1–5) carry most of the signal.
  - Adding neighbouring-word context (CRF or HMM-style smoothing) adds a few points.
  - Transformers add another 1–2 points, but they need an ML framework.
- A dependency-free design can reasonably reach the CRF tier if it implements the context step itself (for example a two-state Viterbi with a switch penalty) on top of n-gram and lexicon scores.
- All of these numbers come from social-media text with many "Universal" tokens (punctuation, emoji, numbers). Headings and lines taken from PDFs are cleaner but shorter, so accuracy will differ.

### Gaps
- I could not open the Barman et al. PDF, so the per-method breakdown (dictionary vs SVM vs CRF accuracies) is unverified. From memory, the CRF was best at around 96%, slightly above 95.76%; treat this as unverified.
- I could not confirm which FIRE MSIR years included Punjabi as a language pair, or find per-language FIRE results for Punjabi.
- I could not confirm the exact authors, venue or dataset for the Punjabi-English 96.8% / 97% / 98% / 88% figures, because the PDFs were blocked. They should be verified before being quoted.
- Not checked: King & Abney (2013) weakly supervised word-level LID, Nguyen & Doğruöz (2013), Das & Gambäck (2014), Solorio et al. CALCS shared-task overviews (2014, 2016).

## Q2. Off-the-shelf LID tools and romanized Punjabi (is there a `pa-Latn` label?)

### Takeaway
Only two widely available tools have an explicit romanized-Punjabi label: **IndicLID** (`pan_Latn`, MIT licence) and **GlotLID v3** (`pan_Latn`, Apache-2.0). Both are fastText-based (IndicLID can also use a BERT stage), so neither can be used dependency-free.

- **CLD3** has `hi-Latn` but only Gurmukhi `pa`.
- **fastText lid.176**, **langid.py** and **lingua** list Punjabi only as a language with no romanized variant, so in practice they recognize Gurmukhi-script Punjabi.

IndicLID's romanized accuracy across 21 romanized classes is modest (about 80% accuracy, 0.75 F1).

### Cited Findings
- **IndicLID (AI4Bharat, ACL 2023, "Bhasha-Abhijnaanam")**
  - Covers 47 classes: 24 native-script, 21 roman-script, plus English (`eng_Latn`) and Others. Includes `pan_Guru` and `pan_Latn`, `hin_Latn` and `urd_Latn`. Described as "the first LID for romanized text in Indian languages".
  - Romanized test set results:

    | Model | Precision | Recall | F1 | Accuracy | Size |
    |---|---|---|---|---|---|
    | IndicLID-FTR (fastText, dim 8) | 0.63 | 0.78 | 0.63 | 0.71 | 357 MB |
    | IndicLID-BERT | 0.73 | 0.84 | 0.75 | 0.80 | 1.1 GB |
    | Two-stage ensemble (threshold 0.6) | 0.73 | 0.85 | 0.75 | 0.80 | 1.4 GB |

  - Native script: IndicLID-FTN reaches 0.98 F1.
  - MIT licence; depends on fastText and Transformers. — [AI4Bharat/IndicLID README](https://github.com/AI4Bharat/IndicLID)
- Bhasha-Abhijnaanam names two main problems for romanized LID: lack of training data and confusion between closely related languages. The authors removed from the romanized Dakshina test set sentences that were shorter than 5 words and where the native-script LID was not confident. Their reason was that such sentences were often "just named entities and English loan words". — [Bhasha-Abhijnaanam paper (search abstract)](https://arxiv.org/abs/2305.15814); [ACL 2023.acl-short.71](https://aclanthology.org/2023.acl-short.71/)
- **Benton, Gutkin, Kirov & Roark (Google), "Improving Informally Romanized Language Identification", EMNLP 2025.**
  - On the 20-language romanized Bhasha-Abhijnaanam test set, test F1 went from 74.7% (IndicLID's pretrained neural model) to 85.4% with a linear classifier trained only on synthetic romanizations, and to 88.2% when harvested natural text was added.
  - The key change was to sample many romanizations from pair n-gram models, capturing natural spelling variation, instead of using one "best" transliteration. — [Google Research page](https://research.google/pubs/improving-informally-romanized-language-identification/); [ACL 2025.emnlp-main.117](https://aclanthology.org/2025.emnlp-main.117/); [arXiv 2504.21540](https://arxiv.org/abs/2504.21540)
- **GlotLID v3 (CIS LMU)**
  - fastText model, Apache-2.0 licence.
  - Its label table includes `pan_Latn`: F1 0.963, precision 0.989, recall 0.939, with 4,782 in the "total number of sentences" column.
  - Other relevant rows:

    | Label | F1 | Precision | Recall | Sentences |
    |---|---|---|---|---|
    | `pan_Guru` | 1.000 | | | 761,081 |
    | `hin_Latn` | 0.986 | | | 40,756 |
    | `urd_Latn` | 0.987 | | | 45,149 |
    | `ben_Latn` | 0.971 | | | |
    | `eng_Latn` | 0.885 | 0.794 | 0.999 | |

  - These are GlotLID's own held-out sets, not short code-mixed spans.
  - GlotLID also has `zxx_Latn` for non-linguistic text such as OCR or PDF garbage. — [GlotLID README](https://github.com/cisnlp/GlotLID); [GlotLID languages-v3 table](https://github.com/cisnlp/GlotLID/blob/main/languages-v3.md)
- **CLD3** has Latin-script labels for `bg-Latn`, `el-Latn`, `hi-Latn`, `ja-Latn`, `ru-Latn` and `zh-Latn`. Punjabi is listed only as `pa` (Gurmukhi). — [google/cld3 README](https://github.com/google/cld3)
- **fastText lid.176** has 176 ISO codes including `pa`, `pnb`, `hi`, `ur` and `en`, with no script-suffixed or romanized labels. It was trained on Wikipedia, Tatoeba and SETimes and is licensed CC-BY-SA 3.0. The newer NLLB `lid218e.bin` uses `xxx_Script` codes, is 1.2 GB, and is licensed CC-BY-NC 4.0. — [fastText language-identification docs](https://github.com/facebookresearch/fastText/blob/main/docs/language-identification.md)
- **langid.py** is pretrained on 97 ISO 639-1 languages including `pa`. It has `set_languages()` to restrict the candidate set (for example to `['en','hi','pa']`). — [langid.py README](https://github.com/saffsd/langid.py)
- **lingua-py** lists Punjabi among its 75 languages. It uses rule-based plus Naive Bayes n-gram models with no word dictionaries, and is Apache-2.0. — [lingua-py README](https://github.com/pemistahl/lingua-py)
- **OpenLID** covers 201 languages, labels them as `lang_Script` (for example `wol_Latn`), and the model is GPL-3.0. — [OpenLID dataset README](https://github.com/laurieburchell/open-lid-dataset)

### Inferences
- Tools that list Punjabi only as `pa` (fastText lid.176, langid.py, lingua, CLD3) almost certainly trained on Gurmukhi text, so Gurmukhi input would be trivially detected by script. On romanized Punjabi they will tend to output English, Hindi-Latn (CLD3), or some unrelated Latin-script language. This is an inference from their label sets; I did not test it.
- GlotLID's `eng_Latn` has low precision (0.794) with near-perfect recall. That means many non-English Latin-script inputs get labelled English, which is exactly the failure mode that matters here.
- GlotLID's `pan_Latn` has only about 4.8k sentences, while `hin_Latn` has about 41k, so expect romanized Punjabi to be confused with `hin_Latn` and `urd_Latn`.
- Neither GlotLID nor IndicLID is usable in a dependency-free library: they need fastText or Transformers, and the model files are hundreds of MB to over 1 GB. They are useful as offline teachers. For example, either can label a corpus or produce evaluation data for distilling a small n-gram table.
- The Benton et al. result is directly relevant to a small-library design: a linear model on character n-grams, trained on synthetic romanizations with realistic spelling variation, beat a fine-tuned BERT.

### Gaps
- I did not verify whether NLLB `lid218e` or OpenLID have a `pan_Latn` label. From memory the NLLB-200 set has only `pan_Guru`, which would mean no romanized Punjabi; this is unverified.
- I found no published per-language confusion numbers for `pan_Latn` vs `hin_Latn` vs `eng_Latn` in IndicLID. The paper's per-language tables were blocked.
- I found no independent benchmark of any of these tools on romanized Gurbani.

## Q3. Very short inputs (1–5 words) and named entities

### Takeaway
Every general-purpose LID tool degrades sharply on 1–2 word inputs. For example, lingua on German scores 74.2% on single words, 93.9% on word pairs and 99.7% on sentences. The romanized-Indic benchmarks deliberately left out inputs under 5 words because those are dominated by named entities and English loanwords. The practical approach for short spans is:
- use a lexicon first;
- let neighbouring tokens and the document context decide;
- give named entities a "neutral" or "ambiguous" label instead of forcing a language.

### Cited Findings
- lingua's test data is single words of at least 5 characters, word pairs of at least 10 characters, and sentences, built from Leipzig Wortschatz corpora. For German (high-accuracy mode, all 75 languages) it reports 74.20% on single words (average 9 characters), 93.90% on word pairs (average 18 characters) and 99.70% on sentences. The README says trigrams are "not enough" for short phrases and that lingua uses n-grams up to 5. — [lingua-py README](https://github.com/pemistahl/lingua-py)
- lingua's own motivation: most other detectors only work on "quite lengthy text fragments" and lose accuracy as more languages are considered. — [lingua-py README](https://github.com/pemistahl/lingua-py)
- langid.py can be restricted to a small candidate set with `set_languages()`. This is the main lever for short-input accuracy in general-purpose tools. — [langid.py README](https://github.com/saffsd/langid.py)
- Bhasha-Abhijnaanam removed romanized test sentences shorter than 5 words because they were often only named entities and English loanwords. In other words, the benchmark's designers judged that short spans cannot be classified reliably. — [IndicLID / Bhasha-Abhijnaanam](https://arxiv.org/abs/2305.15814)
- The Punjabi-English CRF corpus treats Named Entity, Acronym, Universal and Mixed as their own tag classes, separate from English and Punjabi (snippet). The same convention is used in the FIRE and LinCE LID tag sets. — [ACL 2020.icon-demos.12](https://aclanthology.org/2020.icon-demos.12.pdf); [LinCE](https://aclanthology.org/2020.lrec-1.223/)

### Inferences
- **Treat named entities as their own class.** Words like "Guru Nanak", "Amritsar", "Waheguru", "Khalsa", "Sikh", "Sahib" and "Singh/Kaur" are in English dictionaries and corpora, yet they are Punjabi in origin. Following FIRE and LinCE practice, give them a neutral label (NE). A line or heading should then be labelled by its non-NE tokens. If every token is NE or neutral, fall back to the document or neighbouring-line majority, or to a configurable default.
- **Use a small gazetteer of Sikh and Punjabi proper names.** Gurus, banis, places, raags and common honorifics are enough. Matching it before the English lexicon stops "Guru Nanak Dev Ji" from being called English just because "guru" and "dev" are English words.
- **Use length-aware decision rules.** For 1–2 token spans:
  - require stronger evidence before switching away from the surrounding context, such as a strong English-lexicon hit vs a strong Gurbani-lexicon or orthographic hit;
  - otherwise return "unknown" and inherit the language from adjacent lines.
- **Restrict the label set.** Classify only English vs romanized Punjabi, optionally adding Hindi-Latn, never 100+ languages. This is the single biggest accuracy gain for short text, as lingua's and langid.py's documentation implies.
- **Handle capitalisation in headings.** Title Case does not mark a named entity in a heading. Capitalisation should be a weak signal in heading or all-caps contexts.

### Gaps
- I found no published accuracy figures specifically for 1–5 word romanized Punjabi vs English spans. Expected accuracy for that regime has to be measured on in-domain data.
- I found no published method specific to resolving Sikh/Punjabi named entities.

## Q4. Minimal embedded resources and expected accuracy

### Takeaway
A dependency-free design needs three small resources:
1. An English word list with frequencies, about 20k–50k words. It must have a clean licence: OpenSubtitles-derived FrequencyWords (MIT code; corpus needs attribution) or wordfreq data (CC BY-SA 4.0, which the author explicitly discourages exporting to CSV). Norvig/Google-derived lists carry non-commercial caveats.
2. A romanized-Punjabi/Gurbani lexicon generated from Gurmukhi text with the project's own transliterator, or taken from Dakshina's attested romanizations.
3. Character n-gram (1–5) log-probability tables for each class, plausibly a few hundred KB.

Expected accuracy based on the literature:
- about 88% token accuracy for dictionary plus n-grams on small data;
- 95–97% once context smoothing is added;
- line-level accuracy higher than token-level for lines of 5 or more words;
- noticeably lower for 1–2 word spans.

### Cited Findings
- **wordfreq**
  - Apache-licensed code. Its data is CC BY-SA 4.0 and includes SUBTLEX lists, which may be redistributed on the condition that SUBTLEX is credited.
  - The data is a snapshot through about 2021 and "unlikely to be updated again" (see the repo's SUNSET.md).
  - The 'small' lists cover words with frequency of at least 1 per million; the 'large' lists cover at least 1 per 100 million.
  - The author answers "No" to converting wordfreq data to CSV, because CSV cannot carry the CC BY-SA attribution.
  - Runtime dependencies are msgpack, langcodes and regex. — [rspeer/wordfreq README](https://github.com/rspeer/wordfreq)
- **google-10000-english** has the 10,000 most frequent English words, derived from Norvig's list from the Google Web Trillion Word Corpus. Its licence says personal and research use is fine but advises against commercial use without an LDC licence. The repo is marked "Not Maintained". — [first20hours/google-10000-english README](https://github.com/first20hours/google-10000-english) and [LICENSE.md](https://github.com/first20hours/google-10000-english/blob/master/LICENSE.md)
- **hermitdave/FrequencyWords** provides `en_50k.txt` and similar lists in `word count` format, generated from OpenSubtitles 2016/2018. The repo licence is MIT ("MIT License for code"); the data comes from OPUS OpenSubtitles. — [FrequencyWords README](https://github.com/hermitdave/FrequencyWords) and [LICENSE](https://github.com/hermitdave/FrequencyWords/blob/master/LICENSE)
- **Dakshina** (Google) includes Punjabi (`pa`). It provides a romanization lexicon of native-script words with attested Latin romanizations from several annotators; for example, a Punjabi word appears with `andaaja` attested once and `andaja` twice. It also has manually romanized full sentences. — [google-research-datasets/dakshina README](https://github.com/google-research-datasets/dakshina)
- IndicLID publishes its romanized training data and parallel native-roman pairs (GitHub releases, MIT). — [IndicLID README](https://github.com/AI4Bharat/IndicLID)
- Synthetic romanized training data with realistic spelling variation was enough for a linear model to reach 85.4% F1 on 20 romanized Indic languages, beating a fine-tuned BERT (74.7%). — [Benton et al., EMNLP 2025](https://research.google/pubs/improving-informally-romanized-language-identification/)
- For reference on size: lingua is a pure n-gram Naive Bayes design with no dictionaries. — [lingua-py README](https://github.com/pemistahl/lingua-py)
- Reported Punjabi-English token accuracies on social-media data are about 88% for dictionary plus n-gram LM with small data, and 96.8% / about 97% for a CRF (both snippets). — [ACL 2020.icon-demos.12](https://aclanthology.org/2020.icon-demos.12.pdf)

### Inferences
- **English list choice.** The cleanest licence for embedding in an MIT or Apache library is a list built yourself from a permissive corpus, or FrequencyWords `en_50k` with OpenSubtitles attribution. wordfreq is technically redistributable under CC BY-SA, but that would add a share-alike data file and goes against the author's stated wishes about export. A list of 20k–50k lowercase words with log-frequency, gzipped, is probably 100–400 KB (estimate, not measured).
- **Hindi fallback.** A Hindi-Latn class could be trained the same way from Dakshina `hi` romanizations. Romanized Punjabi and Hindi overlap heavily in function words, so a binary "Indic-Latn vs English" decision will be much more accurate than a three-way Punjabi/Hindi/English one, as the low romanized F1 in IndicLID and Bhasha-Abhijnaanam suggests.
- **Expected accuracy (my estimate, not a measured number).**
  - Lines from Gurbani PDFs with 5 or more tokens: plausibly over 97% line-level with lexicon plus n-gram plus smoothing, because English sentences and Gurbani lines differ a lot in function words and orthography.
  - Single-word headings: possibly 85–90% unless the gazetteer and document context are used.
  - These should be measured on a held-out set built from the project's own PDFs.

### Gaps
- I did not verify the SUBTLEX-US standalone licence or the licence of the OpenSubtitles-derived counts. FrequencyWords states MIT only "for code".
- I measured no n-gram table sizes. The sizes above are estimates.
- I found no published accuracy for a tiny pure-Python dictionary plus n-gram LID on romanized Punjabi vs English with short spans.

## Q5. What is specific to romanized Gurbani

### Takeaway
Romanized Gurbani differs from colloquial romanized Punjabi in ways that help detection:
- word-final grammatical vowels (aunkar `-u`, sihari `-i`), as in "sutu", "nanaku", "sachu", "hukami";
- archaic and Sanskritic/Braj vocabulary that is absent from English lexicons;
- systematic doubled vowels and aspirate digraphs (aa, ee, oo, kh, gh, bh, dh, th).

Whether the `-u`/`-i` endings appear depends on the transliteration scheme. Shabad OS, for example, keeps them in "LatinScholar" and drops them in the pronunciation-oriented "Latin" scheme.

### Cited Findings
- Shabad OS `gurmukhi-utils` shows the difference: `transcribe("ਸੁਤੁ", Script.LatinScholar)` gives `"sutu"`, while `Script.Latin` gives `"sut"`. The Latin scheme is described as pronunciation-aware: it "applies haha rules, drops grammatical vowels". LatinScholar is a "mechanical ISO/IAST-like mapping. Every orthographic distinction preserved." — [shabados/gurmukhi-utils README](https://github.com/shabados/gurmukhi-utils)
- Romanization standards for Punjabi in Gurmukhi exist: UN 1972/77, ALA-LC 1997 and ISO 15919. Each produces different surface strings, for example with or without diacritics. — [interscript UN pan-Guru-Latn map](https://interscript.org/maps/un-pan-Guru-Latn-1972); [interscript ALA-LC pan-Guru-Latn 1997](https://interscript.org/maps/alalc-pan-Guru-Latn-1997)

### Inferences
- **Useful Gurbani-specific features** for a hand-built scorer (these are hypotheses to validate on project data, not published results):
  - **Word-final vowel after a consonant.** Endings like `-u` or `-i` (as in "nanaku", "sachu", "mani", "hari", "naami") are rare in English, except words like "you", "menu", "taxi". English is dominated by final -e, -s, -ed, -ing, -ly, -tion.
  - **Doubled vowels** (`aa`, `ee`, `oo` in non-English positions) and **aspirate digraphs** after stops (`kh`, `gh`, `bh`, `dh`, `jh`, `th` before a vowel).
  - **Nasal markers** written as `n`/`N`/`ṅ`/`ñ`, and **ISO 15919 diacritics** (ā, ī, ū, ṇ, ṛ, ṭ, ḍ). Any of these is close to decisive for Indic-Latn.
  - **High-frequency Gurbani function words and particles**: "kai", "kee", "kaa", "naal", "hai", "ho", "jee", "mann/mani", "har/hari", "prabh", "naam", "sach", "gur", "jo", "so", "tu/too", "mai/mainn". Several of these ("so", "jo", "ho", "hai") are also English or English-looking, so they should only weakly contribute unless the neighbouring words support them.
- **Scheme variation.** The detector should be trained on, or synthesized from, several romanization schemes: BaniDB/STTM-style, Shabad OS Latin, LatinScholar or ISO-style with and without diacritics, and informal spellings. That way scheme variation does not look like "English". This matches the Benton et al. finding that sampling spelling variants is what drives accuracy.
- **Generating the Gurbani-side training data.** The project already transliterates Gurmukhi, so it can produce its own n-gram tables by running full Gurbani text (for example from BaniDB or the Shabad OS database) through each romanization scheme. This gives a large in-domain training set with no third-party licence concerns beyond the source text.
- **A dependency-free approach that fits the literature:**
  1. **Script and character gate.** Any Gurmukhi or Devanagari character means not English. Any ISO 15919 diacritic means Indic-Latn.
  2. **Per-token score.** Sum these into a log-likelihood ratio:
     - English-lexicon log-frequency (20–50k list);
     - romanized-Gurbani lexicon hit (generated);
     - character 1–5-gram Naive Bayes log-likelihood ratio, Indic-Latn vs English, trained on generated romanized Gurbani/Punjabi and an English corpus;
     - Gurbani orthographic cue bonuses (final -u/-i, aa/ee/oo, aspirate digraphs).
  3. **Named-entity / neutral class.** A gazetteer of Sikh proper nouns plus punctuation and numbers gets labelled neutral.
  4. **Context smoothing.** A two-state Viterbi or HMM over tokens with a switch penalty: the hand-rolled equivalent of the CRF's context features, which the literature credits with a few points of gain.
  5. **Line decision.** Majority of non-neutral tokens weighted by confidence. Abstain or inherit from neighbouring lines when the margin is small or the span is 1–2 tokens.
  6. **Evaluation and distillation.** Optionally use GlotLID or IndicLID offline, not shipped, as a teacher or for producing an evaluation set.

### Gaps
- I found no published LID work specifically on romanized Gurbani, and no corpus statistics comparing how often word-final -u/-i occurs in Gurbani romanizations vs English. That should be measured directly from project data, for example against an English word list.
- I did not verify the exact romanization conventions used by BaniDB or SikhiToTheMax (for example whether they keep aunkar/sihari endings) in this session.
