# Back-transliteration of romanized Indic text (Punjabi/Gurmukhi): methods and tools

Research date: 2026-10-06. Network note: arxiv.org, aclanthology.org, huggingface.co, direct.mit.edu, research.google, indicnlp.ai4bharat.org and learnpunjabi.org were blocked by this session's egress proxy. Facts from those papers come from search-engine snippets of them, and are marked "(via search snippet)". GitHub READMEs (raw.githubusercontent.com), PyPI metadata and package source code could be read directly. Those facts are primary.

## 1. What do IndicXlit/Aksharantar, Dakshina, indic-trans, Aksharamukha, Google Input Tools and libindic offer for romanized Punjabi to Gurmukhi?

### Takeaway
IndicXlit (an MIT-licensed transformer trained on Aksharantar) is the only maintained, open, trained model with published romanized-to-Gurmukhi numbers. Even it gets only about 40-47% top-1 word accuracy on Punjabi, the second-lowest of its languages. It is also heavy: fairseq/PyTorch, a ~127 MB model zip and an ~850 MB word-frequency zip. Dakshina (CC BY-SA 4.0) is the standard Punjabi benchmark and gives human, ad hoc romanizations. The other tools are either deterministic scheme converters (Aksharamukha, sanscript-style), unmaintained (indic-trans, libindic), or an undocumented deprecated Google endpoint.

### Cited Findings

**AI4Bharat IndicXlit + Aksharantar**
- IndicXlit is "a transformer-based multilingual transliteration model (~11M)" for 21 Indic languages, Punjabi (`pan`) among them. It handles both Roman→native and native→Roman. It is trained on Aksharantar, described as "26 million word pairs spanning 20 Indic languages" (as of 5 May 2022). — [IndicXlit README](https://github.com/AI4Bharat/IndicXlit)
- Architecture: 6 encoder and 6 decoder layers, embedding size 256, 4 attention heads, feed-forward dimension 1024, "a total of 11M parameters". — [IndicXlit README](https://github.com/AI4Bharat/IndicXlit)
- **Punjabi Roman→Gurmukhi top-1 accuracy, as reported in the README results table:**
  - Dakshina test set: **47.24**
  - Aksharantar test, native words: **40.27**
  - Aksharantar test, named entities: **36.08**

  For comparison on the same rows: Hindi 60.56 (Dakshina) and 55.59 (Aksharantar native); Telugu 84.69 (Aksharantar native). — [IndicXlit README](https://github.com/AI4Bharat/IndicXlit)
  - Caveat: in the README's Dakshina row, 20 values sit under 19 language columns. Read by position, `pan` = 47.24 and a trailing unlabeled 61.45 is left over, probably an average. The Hindi value at that position (60.56) matches the IndicXlit Hindi Dakshina figure that a third party cites as 0.6056 ([indic-suggest README](https://github.com/AshayK003/indic-suggest)), which supports reading the row by position.
  - On Aksharantar native words, Punjabi (40.27) is the second-lowest language; only Kashmiri (28.76) is lower. On Dakshina, Punjabi (47.24) is second-lowest after Urdu (42.12). — [IndicXlit README](https://github.com/AI4Bharat/IndicXlit)
- Punjabi Gurmukhi→Roman (the reverse direction) top-1: 29.05 on Aksharantar native words, 48.00 on named entities. — [IndicXlit README](https://github.com/AI4Bharat/IndicXlit)
- Paper-level aggregates (via search snippet of arXiv 2205.03018 / Findings of EMNLP 2023):
  - Micro-averaged accuracy on the Aksharantar test set: 56.31%
  - Frequent words: 69.70%; foreign named entities: 38.34%
  - Accuracy improvement on Dakshina: 15%
  - Error analysis: vowel errors are the most common error type (45%), followed by confusion between similar consonants (25%)

  — [Aksharantar paper (arXiv)](https://arxiv.org/abs/2205.03018); [ACL Anthology 2023.findings-emnlp.4](https://aclanthology.org/2023.findings-emnlp.4/)
- License: "The IndicXlit code (and models) are released under the MIT License." — [IndicXlit README](https://github.com/AI4Bharat/IndicXlit)
- Aksharantar data license: manually collected data is CC-BY. Mined data (from Samanantar and IndicCorp) and existing sources are CC0 (via search snippet). — [Aksharantar paper](https://arxiv.org/abs/2205.03018v2); [AI4Bharat datasets page](https://datasets.ai4bharat.org/aksharantar)
- **Packaging:** PyPI package `ai4bharat-transliteration`, latest version 1.1.3, last upload **2022-09-14**, license MIT, `requires_python >=3.6`. It declares these dependencies: pydload, flask, flask-cors, gevent, sacremoses, pandas, tqdm, ujson, mock, tensorboardX, pyarrow, **fairseq**, urduhack, indic-nlp-library. — [PyPI JSON for ai4bharat-transliteration](https://pypi.org/project/ai4bharat-transliteration/)
  - The README also has users install fairseq from source (`git clone https://github.com/pytorch/fairseq.git; pip install --editable ./`). — [IndicXlit README](https://github.com/AI4Bharat/IndicXlit)
- **Download size, measured by an HTTP HEAD request against the release URLs hard-coded in the package source** ([`transformer/en2indic.py` in the 1.1.3 sdist](https://pypi.org/project/ai4bharat-transliteration/)):
  - `indicxlit-en-indic-v1.0.zip`: 126,832,968 bytes (~127 MB)
  - `word_prob_dicts.zip`: 850,493,322 bytes (~850 MB; covers all languages)

  — [IndicXlit release v1.0](https://github.com/AI4Bharat/IndicXlit/releases/tag/v1.0)
- **Default inference behaviour, from package source:**
  - `XlitEngine(lang2use="all", beam_width=4, rescore=True, ...)` is the default.
  - Rescoring takes the top-k beam outputs, normalises the model scores and the word-unigram probabilities over the candidate set, and ranks by `alpha*model_score + (1-alpha)*word_prob` with `alpha = 0.9`.
  - The bundled web server uses `rescore=True` for en→indic and `rescore=False` for indic→en.

  — [ai4bharat-transliteration 1.1.3 sdist, `transformer/base_engine.py`, `xlit_src.py`, `xlit_server.py`](https://pypi.org/project/ai4bharat-transliteration/)
- Maintenance: the PyPI package has not been released since September 2022, and its fairseq dependency is itself largely unmaintained upstream. The GitHub API was blocked, so the last commit date could not be checked. — [PyPI](https://pypi.org/project/ai4bharat-transliteration/)

**Google Dakshina dataset**
- Covers 12 South Asian languages, including Punjabi (`pa`) written in Gurmukhi. It contains three parts:
  - native-script Wikipedia text
  - a romanization lexicon
  - full sentences in both the native script and the Latin alphabet

  — [Dakshina README](https://github.com/google-research-datasets/dakshina)
- Lexicon details:
  - Words are sampled from words that occur more than once in the Wikipedia training sets. Each has human-annotated romanizations, usually from more than one annotator, with a count of attestations.
  - Punjabi example: `ਅਂਦਾਜਾ andaaja 1` / `ਅਂਦਾਜਾ andaja 2`.
  - Train, dev and test are split by native word, and lemmata in dev/test do not appear in train.
  - Sizes: 25,000 native word types in train, 2,500 each in dev and test.

  — [Dakshina README](https://github.com/google-research-datasets/dakshina)
- Romanized sentences: 10,000 strings per language were randomly chosen and romanized by native speakers. — [Dakshina README](https://github.com/google-research-datasets/dakshina)
- License: CC BY-SA 4.0. — [Dakshina README](https://github.com/google-research-datasets/dakshina)
- Baselines in Roark et al. (2020) use pair n-gram / joint multigram WFSTs: "pair 6-gram models are trained with Witten-Bell smoothing using the OpenGrm library, yielding models in the OpenFst format" (via search snippet of Kirov et al. 2024). — [Kirov et al. 2024, Computational Linguistics](https://aclanthology.org/2024.cl-2.2.pdf); [Roark et al. 2020, LREC](https://aclanthology.org/2020.lrec-1.294/)

**indic-trans (LTRC / libindic, Irshad Bhat)**
- Supports `pan` along with 15 other languages. It has two mutually exclusive modes: `-m` (an ML system) and `-r` (rule-based), with rule-based as the default. A `build_lookup` option caches repeated words. It requires Cython and SciPy and is installed by cloning the repo. — [indic-trans README](https://github.com/libindic/indic-trans)
- License: GNU AGPL v3. — [indic-trans LICENSE](https://github.com/libindic/indic-trans/blob/master/LICENSE)
- Not on PyPI as `indic-trans` (the PyPI JSON endpoint returned "Not Found"). An unrelated-looking `indictrans` 0.2.0 exists there with no license field. — [PyPI](https://pypi.org/project/indictrans/)
- **Likely unmaintained.** The README points to travis-ci.org badges and an IRC channel on freenode, both defunct services. — [indic-trans README](https://github.com/libindic/indic-trans)
- No Punjabi accuracy figures appear in the README.

**Aksharamukha**
- Converts between 120 scripts, including "Punjabi (Gurmukhi)" and Shahmukhi. It supports these romanization formats: Harvard-Kyoto, ITRANS, Velthuis, IAST, ISO, Titus, SLP1, WX, "Roman (Readable)", "Roman (Colloquial)". It also implements script-specific orthographic conventions such as vowel length, gemination and nasalization. — [aksharamukha-python README](https://github.com/virtualvinodh/aksharamukha-python)
- PyPI `aksharamukha` 2.3, last upload 2024-10-14, license **GNU AGPL 3.0**. Dependencies: requests, pykakasi, pyyaml, langcodes, language-data, regex, fonttools, lxml. — [PyPI aksharamukha](https://pypi.org/project/aksharamukha/)

**indic-transliteration (sanscript port)**: actively released (2.3.82, 2026-04-06) under the MIT license. Dependencies: regex, typer, toml, roman, tqdm. — [PyPI indic-transliteration](https://pypi.org/project/indic-transliteration/)

**Google Transliterate API / Input Tools**
- "The Google Transliterate API has been officially deprecated as of May 26, 2011." — [Google Developers: Transliterate](https://developers.google.com/transliterate)
- Unofficial wrappers call the Input Tools backend. Punjabi is reached through the input-tool code `pu-t-i0-und` (via search snippet of these wrappers). — [zaini/google-transliterator-api](https://github.com/zaini/google-transliterator-api); [KSubedi/transliteration-input-tools](https://github.com/KSubedi/transliteration-input-tools); [narVidhai/Google-Transliterate-API](https://github.com/narVidhai/Google-Transliterate-API)
- A user report in the Google Translate community is titled "Tool to Write in Punjab is not working". — [Google Translate Community thread](https://support.google.com/translate/thread/308064752/tool-to-write-in-punjab-is-not-working?hl=en)
- PyPI `google-transliteration-api` 1.0.3 was last uploaded 2021-03-03. Its license metadata is inconsistent: the license field says "MIT" but the classifier says Apache. — [PyPI](https://pypi.org/project/google-transliteration-api/)
- The original API's terms of use apply. — [Google Transliterate API Terms](https://developers.google.com/transliterate/terms?hl=en)

**libindic Transliteration**
- README: "transliterate from English to any Indian Language or from any Indian Language other Indian Language". It uses Travis CI badges and Python 2 `print` syntax in its example. — [libindic/Transliteration README](https://github.com/libindic/Transliteration)
- Not on PyPI under `libindic-transliteration` (Not Found). — [PyPI](https://pypi.org/project/libindic-transliteration/)

### Inferences
- With roughly 40-47% top-1 on Punjabi, even the best open model gets more than half of words wrong at rank 1 on ad hoc romanizations. Top-k output plus re-ranking is a practical necessity for Punjabi, not an optional extra.
- Punjabi scores below Hindi with the same architecture, which suggests Punjabi romanization is more ambiguous. Likely causes are the tippi/bindi/addak marks, the lack of consistent tone marking and the ਣ/ਨ and ੜ/ਰ distinctions, which romanizers rarely mark. The single-language results support this, though no source states the cause directly.
- Aksharamukha and sanscript-style converters only invert a *known, standard* scheme. They do not handle chat-style romanization. Aksharamukha's AGPL license also makes it a poor fit as a vendored dependency of a permissively licensed library.
- indic-trans, libindic and the Google API wrappers should be treated as unmaintained or unreliable for new work as of 2026.

### Gaps
- **CPU inference speed for IndicXlit:** no published per-word CPU latency was found, and the paper could not be fetched. It was not benchmarked locally either, because installing fairseq is heavy.
- **Punjabi row counts in Aksharantar (train/valid/test):** the dataset card and the paper were blocked.
- **Punjabi WER/CER for the Roark et al. 2020 Dakshina baselines (pair n-gram vs. neural):** the paper PDF was blocked.
- **Last commit dates on GitHub:** the GitHub API was blocked for these repos.
- **libindic's Punjabi method and accuracy:** not documented in the README.
- **Accuracy of the Google Input Tools endpoint:** not published.

## 2. Classical approaches (noisy-channel/WFST, joint-sequence, char seq2seq/transformers): pros and cons for low-resource Gurmukhi

### Takeaway
Pair n-gram (joint multigram) WFSTs, as built with OpenGrm/Pynini or Sequitur, are the long-standing strong baselines. Google used them for Dakshina, and they combine well with neural models. They are small, CPU-fast and interpretable, but they need either an FST toolkit or a re-implementation. Neural character transformers are more accurate given lots of data, but they are heavy. A few Punjabi-specific classical systems exist, built on n-gram databases and dictionary-plus-rules, and they report high accuracy, but on proper nouns or on script-to-script tasks rather than ad hoc romanization.

### Cited Findings
- Dakshina baselines use pair n-gram transducers: pair 6-gram, Witten-Bell smoothing, OpenGrm, OpenFst format (via search snippet). — [Kirov et al. 2024](https://aclanthology.org/2024.cl-2.2.pdf)
- Kirov et al. (2024) is a context-aware full-sentence transliteration paper that uses non-parallel monolingual native-script text.
  - It reports "an overall 3.3% absolute (18.6% relative) mean word-error rate reduction" over previous results across all 12 Dakshina languages (via search snippet).
  - One snippet also claimed a "12.7% absolute F1" improvement for Punjabi. This could not be verified against the paper and should be treated as unconfirmed.

  — [Kirov et al. 2024, CL 50(2):475–534](https://direct.mit.edu/coli/article/50/2/475/119145/Context-aware-Transliteration-of-Romanized-South); [Google Research page](https://research.google/pubs/context-aware-transliteration-of-romanized-south-asian-languages/)
- SEQUITUR "is a joint n-gram-based string transduction system which directly trains a joint n-gram model from unaligned data." In the NEWS 2018 comparison, a linear combination of DirecTL+, SEQUITUR and RL-NMT was best, meaning the models capture complementary information (via search snippet). — [Comparison of Assorted Models for Transliteration, W18-2412](https://aclanthology.org/W18-2412.pdf)
- `sequitur-g2p` on PyPI: version 1.0.1668.30, last upload 2024-07-03, GPL-2.0, dependencies numpy>=2.0 and six. — [PyPI sequitur-g2p](https://pypi.org/project/sequitur-g2p/)
- `pynini` on PyPI: version 2.1.7, last upload 2025-09-04, Apache 2.0. It ships compiled wheels wrapping OpenFst. — [PyPI pynini](https://pypi.org/project/pynini/)
- Punjabi forward/backward n-gram transliteration (ACM TALLIP 22(2)), tested on 13,999 parallel Punjabi-English *names*:
  - Trained on over one million parallel entities, with n-gram databases from bigrams up to 30-grams and a rule-based fallback for sparse cases.
  - English→Punjabi: 96% accuracy against the gold standard, 99.14% "using minimum edit distance".
  - Punjabi→English: 96.85% and 99.35% on the same two measures.

  (via search snippet) — [Forward-backward Transliteration of Punjabi Gurmukhi Script Using N-gram Language Model, ACM TALLIP](https://dl.acm.org/doi/10.1145/3542924)
- IndicXlit is a fairseq transformer of about 11M parameters trained on about 26M pairs. — [IndicXlit README](https://github.com/AI4Bharat/IndicXlit)
- A single-author, low-authority repo reports a negative result for a lexicon-only classical pipeline (frequent-word lexicon, phonetic hashing and weighted edit distance) on held-out Aksharantar Hindi:
  - Top-1: **0.000**, at 3.88 MB and 0.22 ms per query.
  - The dhvani rule-based system scored 0.113.
  - The test vocabulary had 0/10,112 overlap with train on both sides. The repo's conclusion: "lookup architectures score at most their independent-lexicon coverage on held-out-vocab benchmarks".

  — [AshayK003/indic-suggest README](https://github.com/AshayK003/indic-suggest)

### Inferences
- **Pair n-gram WFST / joint-sequence models.**
  - Pros: trainable on Dakshina-sized data (25k words); model files of a few MB; fast CPU decoding; N-best output that composes naturally with a word-level LM or lexicon (the noisy-channel setup); interpretable alignments.
  - Cons: needs OpenFst/Pynini (C++ wheels) or Sequitur (GPL-2.0, numpy), or a pure-Python re-implementation of joint-multigram training and decoding. Weaker than neural models on long-range vowel context.
- **Character seq2seq/transformers.**
  - Pros: best published accuracy.
  - Cons: need PyTorch-class runtimes; hard to ship dependency-free; opaque; Punjabi data is limited relative to Hindi.
- The Punjabi n-gram paper's 96-99% figures are on names, and its "minimum edit distance" accuracy is a lenient measure. They are not comparable to Dakshina/Aksharantar top-1 numbers and should not be used to set expectations for ad hoc romanized text.
- The indic-suggest result is a useful warning. A pure lookup approach without a generative fallback scores near zero on out-of-lexicon words. Any lexicon-ranking design needs a character-level candidate generator (rules, pair n-gram, or similar) for unseen words.

### Gaps
- No published Punjabi-specific comparison of a pair n-gram model against a transformer was found in readable form. The Kirov 2024 and Roark 2020 per-language tables were blocked.
- No published pure-Python joint-multigram implementation with Punjabi results was found.

## 3. Handling ad hoc romanization (inconsistent vowels, missing diacritics) vs. standard schemes

### Takeaway
Ad hoc romanization is the main source of error. Vowel errors dominate (45% of IndicXlit errors), and Dakshina explicitly records multiple human romanizations per word. Systems built on standard schemes (Aksharamukha, ISO 15919/ITRANS inverters) assume a deterministic, invertible mapping and do not cover this case. Data-driven models trained on attested romanizations, combined with a word-frequency LM, are the published answer.

### Cited Findings
- Dakshina records multiple attested romanizations per native word with counts, for example `andaaja` (1) and `andaja` (2) for ਅਂਦਾਜਾ. — [Dakshina README](https://github.com/google-research-datasets/dakshina)
- In IndicXlit's error analysis, vowel-related errors are the most common type (45%), followed by similar-consonant confusion (25%) (via search snippet). — [Aksharantar paper](https://arxiv.org/abs/2205.03018)
- Aksharamukha supports fixed schemes (HK, ITRANS, IAST, ISO, Velthuis, SLP1, WX, "Roman (Readable)", "Roman (Colloquial)"). — [aksharamukha-python README](https://github.com/virtualvinodh/aksharamukha-python)
- Kirov et al. frame informal South Asian romanization as needing full-sentence transliteration with context from non-parallel monolingual text (via search snippet). — [Kirov et al. 2024](https://direct.mit.edu/coli/article/50/2/475/119145/Context-aware-Transliteration-of-Romanized-South)
- An LREC 2026 paper studies sentence-level back-transliteration for 13 Indian languages. It is motivated by the "lack of standardized orthography and the presence of contextual ambiguities" in social-media romanization (via search snippet). — [Kumar et al., LREC 2026](https://aclanthology.org/2026.lrec-1.61/)
- The IndoNLP 2025 shared task on real-time reverse transliteration covered Sinhala, Hindi, Bengali, Gujarati and Malayalam, not Punjabi. — [IndoNLP 2025 shared task](https://arxiv.org/abs/2501.05816)
- LLMs:
  - "Beyond Specialization" benchmarks GPT-4o, GPT-4.5, GPT-4.1, Gemma-3-27B-it and Mistral-Large against IndicXlit on 10 languages, Panjabi included, using Dakshina and the Aksharantar subsets. It reports that GPT-family models "generally outperform" IndicXlit (via search snippet). — [arXiv 2505.19851](https://arxiv.org/pdf/2505.19851)
  - VarDial 2025 reports that LoRA-tuning an open LLM on about 10,000 parallel examples gives results comparable to closed LLMs on Dakshina (via search snippet). — [Large Language Models as a Normalizer for Transliteration and Dialectal Translation](https://aclanthology.org/2025.vardial-1.5/)

### Inferences
- A useful library design is a two-tier detector and reverser:
  1. **Scheme-aware exact inversion** when the input matches a known standard scheme (ISO 15919, the library's own practical scheme, BaniDB-style Gurbani romanization). This is cheap and near-lossless.
  2. **Ambiguity-tolerant candidate generation plus ranking** for ad hoc input. It expands vowel-length variants (a/aa, i/ee, u/oo), nasal variants (n/ṇ → ਂ/ੰ/ਨ/ਣ), gemination (doubling → addak ੱ), aspiration (bh/b, etc.), and the r/ṛ (ਰ/ੜ) distinction, then ranks the candidates against a Gurmukhi word list.
- Because vowels cause 45% of neural errors, vowel-variant expansion constrained by a lexicon should address the largest error class directly.
- Sentence context matters (Kirov 2024; LREC 2026). A word-bigram LM over Gurbani or Punjabi text could resolve homographs, but it adds data size.

### Gaps
- Punjabi-specific numbers comparing standard-scheme input with ad hoc input were not found.
- Punjabi rows from the LLM benchmark ("Beyond Specialization") and the LREC 2026 sentence-level paper could not be retrieved (blocked).

## 4. Work specific to Gurbani/SGGS, Sant Bhasha/Old Punjabi, or Shahmukhi↔Gurmukhi that transfers

### Takeaway
No published romanized-to-Gurmukhi back-transliteration study targets Gurbani or Sant Bhasha specifically. The Gurbani ecosystem (BaniDB, anvaad, gurmukhi-utils) provides *forward* Gurmukhi→Roman transliteration, plus line-aligned Roman transliterations of the whole canon, which could serve as training and lexicon data. Shahmukhi↔Gurmukhi work by Lehal and Saini, and the newer SLPG corpus, shows that dictionary lookup plus rules plus corpus-based post-processing handles missing-vowel input well. That is directly analogous to restoring vowels in romanized text.

### Cited Findings
- BaniDB: 142,405 lines across seven sources, 820,549 translations, and "4 transliteration schemes (Roman, Devanagari, IPA, Shahmukhi)". First-letter search (for example `jkrvmm` → ਜਿਨ ਕੈ ਰਾਮੁ ਵਸੈ ਮਨ ਮਾਹਿ) is a signature feature of Gurbani apps (via search snippet of the offline gurbani-search repo). — [singhgursahib0007/gurbani-search](https://github.com/singhgursahib0007/gurbani-search)
- anvaad-js (Khalis Foundation) provides `unicode()` (Gurbani Akhar ASCII ↔ Unicode), `translit()` (Gurmukhi → transliteration), `firstLetters()`, `mainLetters()` and `pauses()`. There is no Roman→Gurmukhi function in its API list. — [KhalisFoundation/anvaad-js README](https://github.com/KhalisFoundation/anvaad-js); Python port: [0xharkirat/anvaad-py](https://github.com/0xharkirat/anvaad-py)
- gurmukhi-utils generates first letters for Unicode Gurmukhi, Hindi transliteration or English transliteration strings. — [gurmukhi-utils (npm)](https://www.npmjs.com/package/gurmukhi-utils)
- Gurmukhi→Shahmukhi (Lehal): more than 98.6% word-level accuracy. Font-independent, supporting about 225 Gurmukhi font encodings (via search snippet). — [A Gurmukhi to Shahmukhi Transliteration System](https://learnpunjabi.org/pdf/GurmukhiToShahmukhiTransliteration.pdf); [Omni-font version, COLING 2012 demo](https://aclanthology.org/C12-3039.pdf)
- Shahmukhi→Gurmukhi (Saini and Lehal), corpus-based:
  - 91.37% average accuracy on a test set of poetry, articles and stories.
  - Uses a "multi-phase approach involving dictionary lookups, rule-based transliteration, and sophisticated post-processing" that copes with Shahmukhi lacking diacritics.
  - Addresses "multiple/zero character mappings, missing vowels, word segmentation, variations in pronunciations and orthography and transliterations of proper nouns" (via search snippet).

  — [Shahmukhi to Gurmukhi Transliteration System: A Corpus based Approach](https://learnpunjabi.org/pdf/gslehal-pap24.pdf); [Conversion between Scripts of Punjabi: Beyond Simple Transliteration, COLING 2012](https://aclanthology.org/C12-2062.pdf)
- SLPG Punjabi Transliteration Corpus:
  - 6.3 million parallel Gurmukhi–Shahmukhi sentences; models updated July 2024.
  - Gurmukhi→Shahmukhi: BLEU 98.1 and word accuracy 99.5%.
  - Shahmukhi→Gurmukhi: BLEU 87.7.
  - The same snippet lists "CER of 99.1%", which cannot be a real character error rate and is probably mislabelled. Treat it as suspect.

  (via search snippet; Hugging Face was blocked) — [SLPG/Punjabi_Transliteration_Corpus](https://huggingface.co/datasets/SLPG/Punjabi_Transliteration_Corpus); [SLPG Shahmukhi→Gurmukhi model](https://huggingface.co/SLPG/Punjabi_Shahmukhi_to_Gurmukhi_Transliteration)
- Related Punjabi transliteration work: "Punjabi to ISO 15919 and Roman Transliteration with Phonetic Rectification" (forward direction) — [ACM TALLIP](https://dl.acm.org/doi/10.1145/3359991). "GRT: Gurmukhi to Roman Transliteration System" (forward, rule-based) — [ResearchGate](https://www.researchgate.net/publication/334442972_GRT_Gurmukhi_to_Roman_Transliteration_System_using_Character_Mapping_and_Handcrafted_Rules).
- The user's own repo has an open issue scoping this work: "Detect romanized Gurmukhi and reverse-transliterate it from any system (research first)". — [thehimmat/gurmukhi-transliterate#16](https://github.com/thehimmat/gurmukhi-transliterate/issues/16)

### Inferences
- **The best Gurbani-specific resource is BaniDB's line-aligned Gurmukhi and Roman text.** It gives (a) a closed lexicon of the SGGS and other canonical vocabulary, including Sant Bhasha forms with word-final ੁ/ਿ case markers (ਰਾਮੁ, ਮਨਿ) that modern-Punjabi models trained on Wikipedia or Aksharantar will not predict, and (b) word-aligned (Gurmukhi, Roman) pairs for fitting a character-mapping or pair-n-gram model. This needs a check of BaniDB's data license (see Gaps).
- Gurbani is a **closed corpus**: about 142k lines with a finite vocabulary. That makes lexicon-constrained decoding much stronger than in open-domain Punjabi. Out-of-vocabulary rates for Gurbani input should be near zero, so the indic-suggest-style coverage ceiling does not bind for Gurbani.
- First-letter search shows that Gurbani users already accept a heavily lossy query form. A reverse-transliterator can likewise use the lexicon to recover the full form from partial or loose romanization, and can cross-check candidates against a line index.
- The Lehal/Saini Shahmukhi→Gurmukhi pipeline (dictionary, then rules, then corpus-frequency disambiguation) is architecturally the same as the recommended romanized→Gurmukhi pipeline. Both restore short vowels lost in the source script, which supports the design.

### Gaps
- No paper or tool was found for romanized→Gurmukhi back-transliteration evaluated on Gurbani or SGGS text, nor any Sant Bhasha-specific transliteration lexicon study.
- **BaniDB data license and terms:** not verified (BaniDB/Khalis pages were not fetched).
- **SLPG model license and size:** Hugging Face was blocked.

## 5. Lexicon-constrained decoding and top-k re-ranking with a word frequency list vs. unconstrained models

### Takeaway
Re-ranking a model's top-k candidates with a word-unigram frequency list is a large, documented gain. AI4Bharat reports about a 12% additional improvement on Dakshina from rescoring the top-4 candidates with a unigram LM, and their shipped engine does this by default (alpha = 0.9). Pure lexicon lookup without a generator fails on out-of-vocabulary words. The best design generates candidates without constraints, then constrains or re-ranks them with a lexicon, keeping a fallback for unseen words.

### Cited Findings
- IndicXlit uses beam size 4 and re-ranks the top-4 candidates by interpolating a word-level unigram LM score with the transliteration score. This "contributes an additional 12% improvement on the Dakshina test set" and helps frequent words most (via search snippet of the Aksharantar paper). — [Aksharantar paper](https://arxiv.org/abs/2205.03018)
- In the shipped code, normalised model scores and normalised word probabilities are combined over the candidate set with `alpha = 0.9` (90% model, 10% frequency); `rescore=True` is the default for Roman→Indic. — [ai4bharat-transliteration 1.1.3 source, `transformer/base_engine.py`](https://pypi.org/project/ai4bharat-transliteration/)
- The word-probability dictionaries for that rescoring ship as an ~850 MB zip covering all languages (measured by HTTP HEAD). — [IndicXlit release v1.0](https://github.com/AI4Bharat/IndicXlit/releases/tag/v1.0)
- Frequent words score highest: 69.70% on AK-Freq versus 38.34% on foreign named entities (via search snippet). — [Aksharantar paper](https://arxiv.org/abs/2205.03018)
- Lexicon-only systems score at most their lexicon's coverage on held-out vocabulary: 0.000 top-1 for one such system on Aksharantar-hi (low-authority source). — [AshayK003/indic-suggest](https://github.com/AshayK003/indic-suggest)
- Saini and Lehal's Shahmukhi→Gurmukhi system combines dictionary lookup with rules and corpus-based post-processing for 91.37% accuracy (via search snippet). — [Saini & Lehal, corpus-based approach](https://learnpunjabi.org/pdf/gslehal-pap24.pdf)

### Inferences
- Using a frequency list as a *re-ranker* over generated candidates, with a soft interpolation, is safer than *hard* lexicon constraint. A hard constraint makes every out-of-lexicon word wrong. A soft re-ranker can still return the generator's best guess when no candidate is in the lexicon.
- For Gurbani, the lexicon is nearly closed, so a hard constraint (prefer any in-lexicon candidate) is reasonable, with a soft fallback for modern Punjabi words, names and loanwords.
- A per-language Punjabi frequency list is much smaller than AI4Bharat's all-language 850 MB bundle. A Gurbani-only word list (tens of thousands of types) would plausibly compress to a few MB or less, small enough to ship inside a pure-Python wheel. This is an estimate; it was not measured.

### Gaps
- No Punjabi-specific number isolating the rescoring gain was found; the 12% figure is for Dakshina overall.
- No study was found comparing hard lexicon-constrained decoding (an FST composed with a lexicon acceptor) against soft re-ranking specifically for Punjabi.

## 6. Should the zero-dependency library integrate a model, call one optionally, or build its own candidate-generation + corpus-ranking approach?

### Takeaway
Build the library's own lightweight candidate generator plus corpus ranker as the default, dependency-free path. Optionally, behind an extra such as `pip install gurmukhi-transliterate[xlit]`, delegate open-domain modern Punjabi to IndicXlit or an LLM. Do not integrate a neural model as a hard dependency.

### Cited Findings
- The library currently declares `dependencies = []` and `requires-python = ">=3.10"`, and already contains `reverse.py`, `matcher.py`, `practical.py` and `iso15919.py` modules. — local repo `pyproject.toml` and `gurmukhi_transliterate/`
- IndicXlit runtime requirements: fairseq plus PyTorch, about 14 declared dependencies, a ~127 MB model and ~850 MB of rescoring dictionaries, and no PyPI release since 2022. — [PyPI](https://pypi.org/project/ai4bharat-transliteration/); [IndicXlit README](https://github.com/AI4Bharat/IndicXlit)
- IndicXlit's Punjabi top-1 is only 40.27 (Aksharantar native words) and 47.24 (Dakshina). — [IndicXlit README](https://github.com/AI4Bharat/IndicXlit)
- Aksharamukha and indic-trans are AGPL-3.0; Sequitur is GPL-2.0; Pynini is Apache-2.0 but needs native wheels. — [PyPI aksharamukha](https://pypi.org/project/aksharamukha/); [indic-trans LICENSE](https://github.com/libindic/indic-trans/blob/master/LICENSE); [PyPI sequitur-g2p](https://pypi.org/project/sequitur-g2p/); [PyPI pynini](https://pypi.org/project/pynini/)
- Dakshina is CC BY-SA 4.0, a share-alike license. Aksharantar is CC-BY for manual data and CC0 for mined data. — [Dakshina README](https://github.com/google-research-datasets/dakshina); [Aksharantar](https://arxiv.org/abs/2205.03018v2)

### Inferences
- **Option A: integrate a model as a hard dependency.** Reject. It breaks the zero-dependency property, adds hundreds of MB, ties the library to an unmaintained fairseq stack, and gains little on Punjabi (about 40-47% top-1). It is also trained on modern-Punjabi data that will miss Gurbani morphology.
- **Option B: optional call-out.** Reasonable as an *extra*. Import IndicXlit (or an LLM/HTTP endpoint the user configures) lazily, only when installed. Use it as an additional candidate source fed into the library's own ranker, which mirrors how IndicXlit itself rescores its beam with a word-frequency lexicon. Avoid the deprecated Google endpoint: there is no SLA, the terms are unclear, and reports say it is unreliable for Punjabi.
- **Option C: own candidate generation plus corpus ranking.** Recommended default.
  1. Detect the scheme. If the input matches a known standard (ISO 15919, the library's practical scheme, BaniDB-style Gurbani romanization), invert it deterministically using the existing forward tables.
  2. For ad hoc input, use a weighted rule lattice or beam search. Weights are hand-set or fitted on Dakshina/Aksharantar Punjabi pairs, or on BaniDB-aligned pairs. Expand vowel length, nasalization (ਂ/ੰ/ਨ/ਣ), addak gemination, aspiration, ਰ/ੜ, ਸ/ਸ਼ and the Gurbani-specific final ੁ/ਿ.
  3. Rank candidates by `alpha * channel_score + (1 - alpha) * log P_lexicon(word)`, using a bundled Gurmukhi frequency list (Gurbani-first, optionally modern Punjabi). Optionally add a word-bigram LM, or match against the line index for Gurbani.
  4. Fall back to the best channel candidate when nothing is in the lexicon (the lesson from indic-suggest).
- A pure-Python pair-n-gram trainer and decoder is feasible but substantial work. A rules-plus-learned-weights lattice gets most of the benefit at lower cost, because the dominant errors are vowels and similar consonants, which hand-written variant rules cover.
- **Data licensing for bundled assets.** A word list derived from Dakshina would carry CC BY-SA 4.0 share-alike obligations. Aksharantar's CC0 mined portion is the most permissive source of Punjabi pairs. BaniDB terms must be checked before bundling Gurbani-derived lists.
- **Evaluation.** Report top-1 and top-5 on (a) the Dakshina `pa` test lexicon (2,500 words; directly comparable to IndicXlit's 47.24), (b) the Aksharantar `pan` test set (comparable to 40.27), and (c) a held-out Gurbani set built from BaniDB Roman/Gurmukhi line pairs. Gurbani is the domain where a closed lexicon should let a small classical system beat IndicXlit.

### Gaps
- No measured head-to-head result exists yet for a lexicon-ranked rules system against IndicXlit on Punjabi or Gurbani. It would need to be built and benchmarked.
- The size of a compressed Gurbani or modern Punjabi frequency list was estimated, not measured.
- The impact of CC BY-SA share-alike terms on a library that bundles Dakshina-derived data needs a licensing check.
