# Reversibility of the repo's romanization systems, and a baseline for `identify_system`

Scope: an analysis of the code in `thehimmat/gurmukhi-transliterate` at commit `70468d9` (branch `claude/jolly-ritchie-26cpkc`, identical to `origin/main`). No tracked repo files were changed. All numbers below come from Python experiments that call the repo's own forward transliterators (`GurmukhiISO15919.to_phonetic`, `GurmukhiPractical.to_practical`, `GurmukhiRomanizer(sid).romanize`), so they measure what the code actually emits, not just what the maps say. `pytest` passes (397 tests) on this commit.

**Reproduction.** Scratch scripts are in `docs/research/16-romanized-gurmukhi/scripts/` (that directory is session scratch and may not persist, so the method is also written out below):
- `common.py`: a wrapper `fwd(sid, text, delete_schwa)` around the 13 forward systems, plus the sample loader
- `matrix.py`: static collision matrix built from the map dicts
- `matrix_engine.py`, `probes.py`: minimal-pair matrix and behaviour probes run through the real engines
- `invert.py`, `experiment_candidates.py`: brute-force inverse, giving candidate spellings per word
- `experiment_identify.py`: the `identify_system` baseline
- `experiment_reverse.py`: the Shackle round-trip

Raw outputs are in `out_*.txt`, `out_*.md` and `cands_*.json` in the same directory.

**Sample.** Unless stated otherwise:
- **Sample** = `tests/fixtures/legacy/japji.unicode.txt`, NFC-normalised. Its 10 non-empty lines are the Mul Mantar plus Japji pauri 1.
- **Words** = whitespace tokens with `॥ । ੦-੯ ੴ` stripped: 71 running words, **57 unique**.
- **Profile of the sample:** 0 words with addak, 2 with tippi (ਸੈਭੰ, ਬੰਨਾ), 0 with bindi, 0 nukta letters, 1 conjunct (ਪ੍ਰਸਾਦਿ), 4 with retroflex letters, 15 with word-final aunkar/sihari, and 10 with a non-initial independent vowel (ਭਉ, ਹੋਵਈ, ਲਾਇ…).
- **Supplement:** because the sample has no addak, bindi or nukta letters, I added a hand-picked list of 20 words, labelled *supplement*. It is **not** a random sample: ਸਿੱਖ ਪੱਕਾ ਇੱਕ ਅੰਮ੍ਰਿਤ ਸਿੰਘ ਮਾਂ ਸੰਤ ਗੁਰੂ ਵਾਹਿਗੁਰੂ ਖ਼ਾਲਸਾ ਜ਼ਮੀਨ ਸ਼ਬਦ ਪੰਥ ਠਾਕੁਰ ਡਰ ਢਾਡੀ ਪ੍ਰੀਤਮ ਨ੍ਹਾਵਣ ਕਿਉਂ ਆਂਖ.
- **Word rendering:** words are romanized as `fwd(word + ' ')` with the trailing space stripped, so they get mid-sentence treatment. This matters for `practical`, which drops a final schwa only before a space, and for ISO, which crashes on a string-final addak cluster (see Q1).

---

## Q1. Which Gurmukhi letters and signs collapse to the same Latin output, per system and by kind?

### Takeaway
Map-level collisions are what the hand-entered `SystemMap`s show. On top of those, the shared generic engine (`_core.py`) silently drops three things for *every* SystemMap-driven system: addak after a vowel sign, tippi/bindi after an independent vowel, and any letter whose map value is `None`. `practical.py` also collapses every nukta letter onto its base letter. ISO 15919 is the only system that keeps every distinction tested; IPA comes next. Thind and GFS are the lossiest.

### Cited Findings

**Method A: static collision matrix (from the maps alone).**
- Inventory (`matrix.py`):
  - 35 base consonants plus 7 nukta letters (ਸ਼ ਖ਼ ਗ਼ ਜ਼ ਫ਼ ਲ਼ ਕ਼)
  - 10 vowel slots (inherent ∅ plus 9 matras)
  - 10 independent vowels
  - 2 nasal signs
- ISO and practical are read from their class dicts (`CONSONANTS`, `VOWEL_DIACRITICS`, `VOWELS`, with ISO tippi→ṃ and bindi→ṁ hard-coded in `to_phonetic`). The other 11 systems are read from `SystemMap.consonants/vowel_diacritics/vowels/nasal_tippi/nasal_bindi`.
- A pair is **collapsed** if both outputs are identical (case-insensitive; differences only in case are flagged). It is **lost** if either side is `None` (unsupported).
- Each pair is classified as retroflex/dental, ṇ/n, ṛ/r, aspiration, nukta, retroflex+aspiration, short/long, other — [systems.py](https://github.com/thehimmat/gurmukhi-transliterate/blob/70468d9/gurmukhi_transliterate/systems.py), [iso15919.py](https://github.com/thehimmat/gurmukhi-transliterate/blob/70468d9/gurmukhi_transliterate/iso15919.py), [practical.py](https://github.com/thehimmat/gurmukhi-transliterate/blob/70468d9/gurmukhi_transliterate/practical.py)

Static map collisions per system (from `matrix.py` output) — [systems.py](https://github.com/thehimmat/gurmukhi-transliterate/blob/70468d9/gurmukhi_transliterate/systems.py):

| system | collisions in the map (Gurmukhi → shared Latin) | unsupported (`None`/absent) |
|---|---|---|
| iso15919 | none | — |
| practical | tippi = bindi (both n/m by context) | — |
| dr_sant_singh | nukta: ਖ/ਖ਼=kh, ਗ/ਗ਼=g, ਫ/ਫ਼=f; tippi=bindi=n | ਞ ਲ਼ ਕ਼ |
| dr_thind | retroflex/dental: ਟ/ਤ=t, ਠ/ਥ=th, ਡ/ਦ=d, ਢ/ਧ=dh; ਣ/ਨ=n; nukta ਖ/ਖ਼, ਗ/ਗ਼, ਫ/ਫ਼, ਲ/ਲ਼; tippi=bindi=n | ਞ ਕ਼ |
| sttm (BaniDB) | aspiration: ਡ/ਢ=dd, ਦ/ਧ=dh; ਣ/ਨ=n; tippi=bindi=(n); ਟ/ਤ, ਠ/ਥ, ੜ/ਰ differ **only by case** (T/t, Th/th, R/r) | ਲ਼ ਕ਼ |
| sttm_legacy | ਣ/ਨ/ਞ=n; ਠ/ਤ=th (retroflex+aspiration crossed); ਘ/ਗ਼=gh; ੌ = inherent = a; ਔ/ਅ=a; ਉ/ਓ=ou; tippi=bindi=n | ਫ਼ ਲ਼ ਕ਼ |
| gursevak | ਫ/ਫ਼=ph; ਘ/ਗ਼=gh; tippi=bindi=ⁿ | ਲ਼ ਕ਼ |
| gfs | retroflex/dental (all 4); ਣ/ਨ=n; ੜ/ਰ=r; bindi=`None` (dropped) | ਲ਼ ਕ਼ ਂ |
| sacred_nitnem | nukta ਖ/ਖ਼, ਗ/ਗ਼; tippi=bindi=ṅ | ਙ ਞ ਲ਼ ਕ਼ |
| iast | none among supported letters | ੜ ਖ਼ ਗ਼ ਜ਼ ਫ਼ ਲ਼ ਕ਼ |
| shackle | ਖ/ਖ਼=kh (deliberately degraded, see map comment); tippi=bindi=ṁ | ਲ਼ |
| ipa | none | ਕ਼ |
| banidb_ipa | ਙ/ਞ=ŋ; ਟ/ਢ=ʈ; ਤ/ਧ=t (voicing+aspiration lost, tone mark not stored) | ਸ਼ ਖ਼ ਗ਼ ਜ਼ ਫ਼ ਲ਼ ਕ਼ ਔ |

**Method B: minimal pairs run through the real forward code.** `matrix_engine.py` romanizes minimal pairs of Gurmukhi strings with each system and records **LOST** when both romanize identically, or when one side's output is empty. These engine-level losses are invisible in the maps — [_core.py](https://github.com/thehimmat/gurmukhi-transliterate/blob/70468d9/gurmukhi_transliterate/_core.py), [practical.py](https://github.com/thehimmat/gurmukhi-transliterate/blob/70468d9/gurmukhi_transliterate/practical.py), [iso15919.py](https://github.com/thehimmat/gurmukhi-transliterate/blob/70468d9/gurmukhi_transliterate/iso15919.py):

| kind (minimal pair) | iso | prac | sant | thind | sttm | sttm_leg | gursevak | gfs | s_nitnem | iast | shackle | ipa | bdb_ipa |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| retroflex/dental ਟ/ਤ ਠ/ਥ ਡ/ਦ ਢ/ਧ | kept | kept | kept | LOST | kept (case) | kept | kept | LOST | kept | kept | kept | kept | kept |
| ਣ/ਨ | kept | kept | kept | LOST | LOST | LOST | kept | LOST | kept | kept | kept | kept | kept |
| ੜ/ਰ | kept | kept | kept | kept | kept (case) | kept | kept | LOST | kept | ੜ dropped | kept | kept | kept |
| aspiration (10 pairs) | kept | kept | kept | kept | LOST ਡ/ਢ, ਦ/ਧ | kept | kept | kept | kept | kept | kept | kept | kept* |
| ਸ਼/ਸ | kept | **LOST (s)** | kept | kept | kept | kept | kept | kept | kept | kept | kept | kept | ਸ਼ dropped |
| other nukta ਖ਼ ਗ਼ ਜ਼ ਫ਼ ਲ਼ | kept | **LOST all 5** | LOST ਖ਼ ਗ਼ ਫ਼; ਲ਼ dropped | LOST all 4 + ਲ਼ | ਲ਼ dropped | ਫ਼ ਲ਼ dropped | LOST ਫ਼; ਲ਼ dropped | ਲ਼ dropped | LOST ਖ਼ ਗ਼; ਲ਼ dropped | all 5 dropped | LOST ਖ਼; ਲ਼ dropped | kept | all 5 dropped |
| tippi vs bindi | kept | LOST | LOST | LOST | LOST | LOST | LOST | (bindi silent) | LOST | kept | LOST | kept | kept |
| nasal present vs absent after a matra | kept | kept | kept | kept | kept | kept | kept | **LOST ਕਾਂ=ਕਾ** | kept | kept | kept | kept | kept |
| nasal after an **independent vowel** (ਆਂ/ਆ, ਅੰਗ/ਅਗ) | kept | kept | LOST | LOST | LOST | LOST | LOST | LOST | LOST | LOST | LOST | LOST | LOST |
| addak after a consonant (ਪੱਕਾ/ਪਕਾ) | kept | kept (but `pkkaa`) | kept | kept | kept | kept | kept | kept | kept | kept | kept | kept | kept |
| addak after a **vowel sign** (ਸਿੱਖ/ਸਿਖ, ਇੱਕ/ਇਕ) | kept | LOST | LOST | LOST | LOST | LOST | LOST | LOST | LOST | LOST | LOST | LOST | LOST |
| short/long (∅/ਾ, ਿ/ੀ, ੁ/ੂ, ਇ/ਈ, ਉ/ਊ, ਅ/ਆ) | kept | kept | kept | kept | kept | kept | kept | kept | kept | kept | kept | kept | kept |
| ੇ/ੈ, ੋ/ੌ | kept | kept | kept | kept | kept | kept | kept | kept | kept | kept | kept | kept | kept |
| vowel sign vs hiatus: ੈ/ਇ after a (ਕੈ/ਕਇ), ੌ/ਉ (ਕੌ/ਕਉ) | kept (apostrophe `ka'u`) | LOST both | LOST ੈ | LOST ੈ | LOST both | kept | LOST ੌ | LOST both | LOST both | LOST both | LOST both | kept | kept |
| ੌ vs inherent (ਕੌ/ਕ) | kept | kept | kept | kept | kept | **LOST (`ka`)** | kept | kept | kept | kept | kept | kept | kept |
| final aunkar/sihari vs none (ਕਰੁ/ਕਰ, ਕਰਿ/ਕਰ) | kept | kept | kept | kept | kept | kept | kept | kept | kept | kept | kept | kept | kept |
| schwa with `delete_schwa=False`: C+a vs conjunct (ਕਰਤਾਰ/ਕਰ੍ਤਾਰ) | kept | kept | kept | kept | kept | kept | kept | kept | kept | kept | kept | kept | kept |
| schwa with `delete_schwa=True` (same pair) | LOST | LOST | LOST | LOST | LOST | LOST | LOST | LOST | LOST | LOST | LOST | LOST | LOST |
| minimal pairs collapsed (of 46) | **0** | 13 | 12 | **17** | 13 | 11 | 10 | 14 | 12 | 12 | 11 | **4** | 10 |

\* banidb_ipa keeps the 10 aspiration pairs, but crosses ਟ/ਢ (ʈ) and ਤ/ਧ (t) — [systems.py](https://github.com/thehimmat/gurmukhi-transliterate/blob/70468d9/gurmukhi_transliterate/systems.py)

**Engine behaviours behind the LOST cells.** Verified with `probes.py`; a full output table is in `out_probes.md`.

Generic engine (`_core.py`):
- **Addak after a vowel sign is dropped.** `_core.transliterate` handles addak only as the character right after a consonant (or consonant+nukta). The addak in ਸਿੱਖ (ਸ ਿ ੱ ਖ) is unmapped and skipped, so ਸਿੱਖ → `sikha` in all 11 SystemMap systems. ਪੱਕਾ (addak right after a consonant) → `pakkaa` works — [_core.py](https://github.com/thehimmat/gurmukhi-transliterate/blob/70468d9/gurmukhi_transliterate/_core.py)
- **Tippi/bindi after an independent vowel is dropped.** Step 7 emits the vowel, and the following ੰ/ਂ is not in any table, so it is skipped: ਅੰਗ → `aga`, ਆਂਖ → `aakha`/`ākha` — [_core.py](https://github.com/thehimmat/gurmukhi-transliterate/blob/70468d9/gurmukhi_transliterate/_core.py)
- **`None` letters vanish.** A consonant mapped to `None` is skipped with no output (two-char nukta forms `i += 2`), e.g. IAST ਗ਼ → ``, ੜ → ``. A nukta letter absent from the map (e.g. ਕ਼ in Sant Singh) falls back to its base letter, because the `਼` is then skipped — [_core.py](https://github.com/thehimmat/gurmukhi-transliterate/blob/70468d9/gurmukhi_transliterate/_core.py)
- **Fixed nasal values.** The engine uses one value for each nasal sign with no homorganic/labial switching. Shackle's forward output for ਸੰਤ is therefore `saṁta`, not Shackle's real `santa` (the map notes admit this) — [systems.py](https://github.com/thehimmat/gurmukhi-transliterate/blob/70468d9/gurmukhi_transliterate/systems.py)
- **`SystemMap.subjoined` is never read by the engine.** The engine's own comment says it is used only for the server's comparison table. So Gursevak's documented subscripts (`ᵣ ₕ ᵤ`) are never emitted: ਪ੍ਰੀਤਮ → `preetama`, not `pᵣeetam` — [_core.py](https://github.com/thehimmat/gurmukhi-transliterate/blob/70468d9/gurmukhi_transliterate/_core.py), [systems.py](https://github.com/thehimmat/gurmukhi-transliterate/blob/70468d9/gurmukhi_transliterate/systems.py)
- **Real-scheme features the engine does not reproduce.** The map notes document STTM addak as an apostrophe and ੍ਰ metathesis, Gursevak capitalising after addak and dropping silent final sihari, and Shackle's etymological doubling. The engine reproduces none of these, so engine output ≠ real-world text for those systems — [systems.py](https://github.com/thehimmat/gurmukhi-transliterate/blob/70468d9/gurmukhi_transliterate/systems.py)

`practical.py`:
- **Nukta letters collapse onto their base.** `to_practical` looks up the single base character before any two-character nukta form, and then treats `਼` as a modifier that also suppresses the inherent vowel. Results: ਸ਼ਸ → `ss`, ਖ਼ਖ → `khkh`, ਗ਼ਮ → `gm`, ਜ਼ਮੀਨ → `jmeen`. The `'ਸ਼': 'sh'` entries in its own map are therefore unreachable — [practical.py](https://github.com/thehimmat/gurmukhi-transliterate/blob/70468d9/gurmukhi_transliterate/practical.py)
- **Addak right after a consonant drops that consonant's inherent vowel.** The addak branch appends only the doubled consonant: ਪੱਕਾ → `pkkaa`, ਮੱਥਾ → `mththaa` — [practical.py](https://github.com/thehimmat/gurmukhi-transliterate/blob/70468d9/gurmukhi_transliterate/practical.py)
- **Final schwa is deleted before a space or danda even when `delete_schwa=False`, but kept at end of string.** ਸਿੰਘ alone → `singha` (shown in `comparison_table`), while inside a sentence it is `singh` — [practical.py](https://github.com/thehimmat/gurmukhi-transliterate/blob/70468d9/gurmukhi_transliterate/practical.py)

`iso15919.py`:
- **Crash on a string-final addak cluster.** `to_phonetic('ਸਿੱਖ')` raises `IndexError: string index out of range` (line 126: `text[i]` after `i += 3`). `comparison_table('ਸਿੱਖ')` crashes too; `'ਸਿੱਖ ਕ'` works (`sikkha ka`) — [iso15919.py](https://github.com/thehimmat/gurmukhi-transliterate/blob/70468d9/gurmukhi_transliterate/iso15919.py)
- **Smaller drops found by the inverse search:**
  - addak and tippi right after a nukta letter are dropped: ਜ਼ੱਮੀਨ = ਜ਼ੰਮੀਨ = ਜ਼ਮੀਨ → `zamīna`
  - a bindi after an addak cluster is swallowed: ਸਿੱਖਂ → `sikkha`
  - a bindi directly on a consonant suppresses the inherent vowel: ਕਂ → `kṁ`, but ਕੰ → `kaṃ`

  — [iso15919.py](https://github.com/thehimmat/gurmukhi-transliterate/blob/70468d9/gurmukhi_transliterate/iso15919.py)

`schwa.py`:
- **R1 treats the last consonant as word-final even when an independent vowel follows.** With `delete_schwa=True`: ਹੋਵਈ → `hovī`, which is identical to ਹੋਵੀ's output (a new collision); ਨਿਰਭਉ → `nirabhu`. This affects all 13 systems because they all call `compute_deletions` — [schwa.py](https://github.com/thehimmat/gurmukhi-transliterate/blob/70468d9/gurmukhi_transliterate/schwa.py)

Shared by every system:
- **Word-final aunkar/sihari is never dropped by any forward engine.** It is always written (`nāmu`, `sati`; Gursevak writes `sate`). Final short vowels therefore survive in generated text, but the map notes say real Gursevak data drops silent final sihari — [systems.py](https://github.com/thehimmat/gurmukhi-transliterate/blob/70468d9/gurmukhi_transliterate/systems.py)
- **Segmentation collisions** appear only when the output is parsed, not as identical map values:
  - aspirate digraph vs consonant + subjoined ਹ: `bh` = ਭ or ਬ੍ਹ; `kh` = ਖ or ਕ੍ਹ in every system using h-digraphs
  - `ai`/`au` = ੈ/ੌ or inherent a + ਇ/ਉ in most systems (Japji: ਨਿਰਭਉ `nirabhau`, ਸੋਚੈ `socai`)
  - nasal `n` vs ਨ: ਸੰਤ = ਸਨ੍ਤ in Thind/practical
  - IPA tippi `ŋ` = ਙ (ਸੰਤ ≈ ਸਙ੍ਤ)
  - Gursevak/sttm_legacy geminate vs retroflex digraph: `tt` = ਟ or ਤੱਤ/ਤ੍ਤ; `rr` = ੜ or ਰ੍ਰ

  Source: `invert.py` candidate lists in `cands_nods_*.json`, using [_core.py](https://github.com/thehimmat/gurmukhi-transliterate/blob/70468d9/gurmukhi_transliterate/_core.py)

### Inferences
- **Two kinds of loss.** A reverse design has to separate (a) losses the *scheme* imposes (retroflex/dental in Thind/GFS, ṇ/n in four systems, tippi=bindi in nine, nukta merges) from (b) losses the *repo's forward engine* introduces (addak after a matra, nasal after an independent vowel, practical's nukta bug, ISO's crash). Kind (b) should be fixed in the forward code, or at least kept out of test fixtures. Otherwise a reverse trained or tested on engine output learns phantom ambiguities, and misses ones real text has (STTM apostrophe-addak, Gursevak dropped sihari).
- **Ambiguity kinds a SystemMap-driven reverse must emit, beyond Shackle's four** (nasalization, aspirate_sonorant, gemination, persian_collision):
  - `retroflex_dental`, `nasal_class` (ṇ/n/ñ), `flap` (ṛ/r), `aspiration` (STTM ਡ/ਢ, ਦ/ਧ), `nukta` (Shackle's persian_collision generalised)
  - `vowel_hiatus` (ੈ vs a+ਇ, ੌ vs a+ਉ), `vowel_merge` (sttm_legacy ੌ=a, ਉ=ਓ)
  - `nasal_presence` (GFS bindi silent; any system where nasal after a vowel letter was dropped)
  - `schwa`/conjunct boundary (after schwa deletion), and `case_lost` (STTM capitals lowercased)
- **Short/long vowels are kept by every map** (aa/ee/oo or macrons) as long as the writer is consistent. The real-world aa/a and ee/i inconsistency described in #16 is a property of ad-hoc text, not of any implemented system.

### Gaps
- None of the 13 maps was checked against its real source here (that is #4). The matrix reflects the maps as entered.
- No real-world romanized corpus is in the repo, so the losses that real STTM/Gursevak/iGurbani text shows (apostrophe addak, metathesis, dropped final sihari) could not be measured. They are known only from the map notes.

---

## Q2. How reversible is each system? (distinctions preserved; candidate spellings per word)

### Takeaway
On the 57 unique Japji words, inverting the repo's own forward output gives:
- **ISO 15919:** one Gurmukhi spelling for every word.
- **IPA, IAST, Shackle, Sacred Nitnem, Sant Singh, Gursevak, BaniDB-IPA:** about 1.1–1.4 spellings per word (geometric mean) once the two `_core` engine artifacts are discounted, or 2–3.4 with them.
- **Thind and STTM:** about 1.6–2.2 (artifact-free).
- **sttm_legacy and GFS** are the least reversible: about 4–8 artifact-free, up to 1,056 spellings for one word.

### Cited Findings

**Score 1: fraction of pairwise distinctions kept, static maps.** Computed over 832 same-category pairs; a pair touching a `None` value counts as lost. The table also gives Score 2: the fraction of the 46 minimal pairs kept through the real engines (Q1 Method B). Source: `matrix.py`, `matrix_engine.py`, using [systems.py](https://github.com/thehimmat/gurmukhi-transliterate/blob/70468d9/gurmukhi_transliterate/systems.py)

| system | static pairs kept (of 832) | engine minimal pairs kept (of 46) |
|---|---|---|
| iso15919 | 1.000 | 1.00 |
| practical | 0.999 | 0.72 (nukta + engine bugs invisible to the map) |
| dr_sant_singh | 0.862 | 0.74 |
| dr_thind | 0.898 | 0.63 |
| sttm | 0.901 | 0.72 |
| sttm_legacy | 0.856 | 0.76 |
| gursevak | 0.906 | 0.78 |
| gfs | 0.901 | 0.70 |
| sacred_nitnem | 0.821 | 0.74 |
| iast | 0.706 (7 unsupported letters) | 0.74 |
| shackle | 0.952 | 0.76 |
| ipa | 0.954 | 0.91 |
| banidb_ipa | 0.691 (8 unsupported) | 0.78 |

**Score 3: candidate Gurmukhi spellings per word**, measured by a brute-force inverse (`invert.py`). Method:
- For each word W and system S, compute the target T = S(W).
- Enumerate every Gurmukhi string G built from a restricted akshara grammar. Each G is one or more aksharas of the form `[ੱ] C [੍S] [M] [N]`, or an independent vowel `V [N]`. Here:
  - C is any consonant S maps to a non-`None` value, nukta forms included
  - the subjoined consonant is one of ਰ ਵ ਤ ਯ, or ਹ (ਹ only under the sonorants ਨ ਮ ਰ ਲ ੜ ਣ ਵ, mirroring reverse.py's aspirate-sonorant rule)
  - M is any vowel sign, and N is ੰ or ਂ
  - ਅ is allowed only word-initially, and addak never word-initially or right after a nasal
- Keep every G with S(G) == T exactly; the real forward function is the judge. Search is depth-first with exact prefix pruning, plus small allowances for practical's context rules.
- A 30-second limit per search applied to ISO only, and was hit for 7 words; ISO counts are therefore lower bounds, but all 57 true words were found.
- "Artifact-free" drops candidates that differ only through the two `_core` drops (addak after a vowel sign or vowel letter; nasal after a vowel letter). Applied to the 11 SystemMap systems only.
- "tb-rule" also drops candidates that break the modern tippi/bindi distribution (tippi with ∅ ਿ ੁ ੂ ਅ ਇ ਉ, bindi elsewhere).

Results, `delete_schwa=False`, 57 unique Japji words (`out_nods_japji.txt`, `cands_nods_japji_all.json`) — [_core.py](https://github.com/thehimmat/gurmukhi-transliterate/blob/70468d9/gurmukhi_transliterate/_core.py):

| system | truth found | words with 1 candidate (raw) | median (raw) | geo-mean (raw) | max (raw) | geo-mean, tb-rule | geo-mean, artifact-free | 1-candidate words, artifact-free |
|---|---|---|---|---|---|---|---|---|
| iso15919 | 57 | 57 | 1 | 1.00 | 1 | 1.00 | 1.00 | 57 |
| practical | 57 | 8 | 4 | 4.13 | 96 | 4.03 | 4.13 (n/a) | 8 |
| dr_sant_singh | 57 | 11 | 3 | 3.40 | 48 | 2.80 | 1.41 | 38 |
| dr_thind | 57 | 6 | 6 | 5.38 | 72 | 4.29 | 2.23 | 21 |
| sttm | 57 | 9 | 4 | 4.28 | 192 | 3.46 | 1.59 | 27 |
| sttm_legacy | 57 | 3 | 10 | 13.23 | 1008 | 10.28 | 3.85 | 10 |
| gursevak | 57 | 12 | 2 | 3.11 | 96 | 2.60 | 1.26 | 41 |
| gfs | 57 | 0 | 12 | 16.19 | 1056 | 5.75 | 7.86 | 0 |
| sacred_nitnem | 57 | 11 | 2 | 3.10 | 24 | 2.59 | 1.32 | 40 |
| iast | 56 (ਕੂੜੈ: ੜ is `None`) | 13 | 2 | 2.60 | 12 | 2.27 | 1.10 | 49 |
| shackle | 57 | 11 | 2 | 2.98 | 24 | 2.51 | 1.26 | 42 |
| ipa | 57 | 15 | 2 | 2.18 | 9 | 1.98 | 1.00 | 57 |
| banidb_ipa | 57 | 12 | 2 | 2.41 | 9 | 2.18 | 1.10 | 50 |

The same run on the 20-word supplement (`out_nods_supp.txt`):

| system | truth found | geo-mean (raw) | geo-mean, artifact-free | 1-candidate words, artifact-free |
|---|---|---|---|---|
| iso15919 | 20 (3 searches hit the time limit) | 1.30 (ISO's own addak/nukta drops) | 1.30 (filter not applied to ISO) | 16 |
| iast | 18 (ਖ਼, ਜ਼ are `None`) | 2.23 | 1.26 | 14 |
| ipa | 20 | 2.31 | 1.37 | 12 |
| banidb_ipa | 17 (Persian letters are `None`) | 2.48 | 1.47 | 10 |
| shackle | 20 | 2.80 | 1.61 | 9 |
| sacred_nitnem | 20 | 3.13 | 1.85 | 7 |
| dr_sant_singh | 20 | 3.67 | 2.02 | 7 |
| gursevak | 20 | 3.91 | 2.01 | 3 |
| sttm | 20 | 4.49 | 2.31 | 1 |
| dr_thind | 20 | 5.76 | 3.13 | 0 |
| practical | 19 (ਪੱਕਾ → `pkkaa` not invertible) | 5.98 | 5.98 (filter not applied) | 1 |
| gfs | 20 | 14.81 | 8.88 | 0 |
| sttm_legacy | 20 | 21.81 | 7.73 | 1 |

**With `delete_schwa=True`.** Candidates were generated by re-inserting the inherent vowel at consonant–consonant and word-final positions of T, inverting each variant without schwa deletion, then keeping G only if S(G, delete_schwa=True) == T. ISO used a 5-second limit and hit it 24 times (`out_ds_japji_a.txt`, `out_ds_japji_b.txt`). Results — [schwa.py](https://github.com/thehimmat/gurmukhi-transliterate/blob/70468d9/gurmukhi_transliterate/schwa.py):
- Artifact-free geometric means were about the same as or slightly below the no-deletion run:
  - iso 1.06, sant_singh 1.35, thind 2.15, sttm 1.51, sttm_legacy 2.76, gursevak 1.31, gfs 6.22
  - sacred_nitnem 1.25, iast 1.08, shackle 1.19, ipa 1.20, banidb_ipa 1.18
- The truth was found for only 55/57 words in every system. The two misses are the R1 bug: ਨਿਰਭਉ → `nirabhu` and ਹੋਵਈ → `hovee`/`hovī`, where the dropped `a` sits before a vowel letter.

**Which collision kinds actually occur in real words.** Counted as the number of Japji words (of 57) where at least one wrong candidate differs from the truth in that way, using `difflib` on the Gurmukhi strings (`cands_nods_japji_all.json`):
- Every SystemMap system: "addak presence" in 39 words. This is entirely the `_core` addak-after-vowel-sign drop.
- Most systems: tippi/bindi or nasal presence in 15–24 words.
- Thind: retroflex/dental in 10 words and ṇ/n in 10.
- STTM: ṇ/n in 10 and aspiration in 3.
- GFS: nasal in all 57, ṛ/r in 15, retroflex in 10.
- sttm_legacy: "other vowel" (ੌ=a=inherent, ਉ=ਓ) in 45.
- practical: nukta in 28.
- Shackle: nukta (ਖ/ਖ਼) in 5.

— [systems.py](https://github.com/thehimmat/gurmukhi-transliterate/blob/70468d9/gurmukhi_transliterate/systems.py)

Example candidate sets (raw):

| system | word → output | candidates |
|---|---|---|
| dr_thind | ਤੁਟੈ → `tutai` | 32 (8 artifact-free): ਟੁਟੈ, ਟੁਤੈ, ਤੁਟਇ, … |
| sttm_legacy | ਸਿਆਣਪਾ → `siaanapaa` | 1,008 (36 artifact-free) |
| gfs | ਕਰਤਾ → `karataa` | 32, because bindi is silent and can be inserted anywhere |
| shackle | ਨਿਰਭਉ → `nirabhau` | 16, including ਨਿਰਭੌ and ਨਿਰਬ੍ਹਉ |
| iso | ਨਿਰਭਉ → `nirabha'u` | 1 (the apostrophe resolves the hiatus) |

### Inferences
- **Rough tiers for a reverse design**, using artifact-free geometric means:
  - Near-deterministic (≈1.0–1.3 spellings per word): ISO 15919, IPA, IAST, BaniDB-IPA, Shackle, Gursevak, Sacred Nitnem, Sant Singh.
  - Needs a lexicon (≈1.5–2.5): STTM, Thind.
  - Needs a lexicon plus context (≈4–9, long tails into hundreds): sttm_legacy, GFS.
- **Practical** cannot be scored fairly until its nukta and addak bugs are fixed.
- **Fixing the two `_core` drops** (addak after a vowel sign; nasal after an independent vowel) would cut raw candidate counts by roughly 2–3× for every SystemMap system. That is the biggest single reversibility win available in this repo.
- **The modern tippi/bindi rule** prunes 0–65% of candidates (ISO 0%, Sant Singh 3.40 to 2.80, GFS 16.2 to 5.8). A reverse should apply it as a prior, not a hard rule: Shackle's own primary for `sāṁ` is ਸਾੰ, tippi after kanna, which breaks the modern rule.
- **Schwa deletion hides little in this setting.** Gurmukhi writes no half-letters except ੍ਰ ੍ਵ ੍ਹ, so a deleted schwa between consonants usually maps back to the same unmarked consonant sequence. Its real cost is in ad-hoc text, where deletion is inconsistent and segmentation (`gurprasad`) is unknown. The R1 bug before vowel letters also needs fixing.

### Gaps
- The candidate counts are an upper bound on what a lexicon-backed reverse would face, because no lexicon is in the repo. `sgfreq.json` in the shared scratchpad belongs to another researcher and was not used. A measured "candidates attested in an SGGS word index" figure is the needed next step.
- The 57-word sample has no addak, bindi or nukta letters. The 20-word supplement is hand-picked, not random. Neither is a stratified estimate for SGGS as a whole.
- Candidate counts depend on the grammar restrictions above, which are my assumptions: subjoined set, ਹ only under sonorants, ਅ only initial. A looser grammar gives more candidates.

---

## Q3. How accurate is `compare.identify_system` today?

### Takeaway
On the Japji sample, the true system is uniquely ranked first for only **33% of lines** and **15% of single words**. In 50% of lines and 68% of words it ties with other systems for top score; ties are broken by registry order, which favours `dr_sant_singh`. ISO 15919 and practical are never identified (0/10 lines), because the token index holds only 14 and 3 signature tokens for them. An English pangram scores 0.756.

### Cited Findings

**How the scorer works.** `_build_token_index`:
- The index holds every non-`None` consonant, vowel-sign, vowel and nasal value of each SystemMap, lowercased.
- For ISO it holds only 14 hand-picked signature characters (ś ṭ ḍ ṛ ṅ ṇ ñ ā ī ū ē ō ṃ ṁ); for practical only `aa ee oo`.
- `identify_system` tokenises greedily longest-first and scores each system as `(tokens in its set) / total tokens`, spaces and `|` included.
- It sorts with Python's stable `sorted`, so tied systems come out in `_ALL_SYSTEMS` order: iso15919, practical, dr_sant_singh, dr_thind, sttm, …
- There is no "not Gurmukhi" output.

— [compare.py](https://github.com/thehimmat/gurmukhi-transliterate/blob/70468d9/gurmukhi_transliterate/compare.py)

**Token index statistics** (`experiment_identify.py`) — [compare.py](https://github.com/thehimmat/gurmukhi-transliterate/blob/70468d9/gurmukhi_transliterate/compare.py):
- 133 distinct tokens; 55 belong to exactly one system, 16 to 9 systems, and 9 to all 11 SystemMap systems.
- Exclusive tokens per system:

| system | exclusive tokens |
|---|---|
| iso15919 | 2 (ē ō) |
| practical | 0 |
| dr_sant_singh | 0 |
| dr_thind | 1 (rh) |
| sttm | 4 (`(n)` `g(h)` `n(j)` `uoo`) |
| sttm_legacy | 6 |
| gursevak | 4 |
| gfs | 2 |
| sacred_nitnem | 0 |
| iast | 0 |
| shackle | 2 (q ġ) |
| ipa | 22 |
| banidb_ipa | 12 |

- Lowercasing erases STTM's meaningful capitals (T Th R).
- `w` appears in no map, so "waheguru"-style input is out of vocabulary.

**Measured accuracy.** Method:
- Romanize each unit with each of the 13 systems via `fwd`, then call `identify_system(rom, top_n=99)`.
- "top1" = the true system is in position 1 as returned (ties broken by order). "unique-top1" = the true system's score is strictly greater than every other. "tied" = the true system shares the top score.
- Units: the 10 sample lines (130 trials) and the 57 unique words (741 trials).

Results (`out_identify.txt`) — [compare.py](https://github.com/thehimmat/gurmukhi-transliterate/blob/70468d9/gurmukhi_transliterate/compare.py):

| unit | delete_schwa | top1 | top3 | unique-top1 | tied at top |
|---|---|---|---|---|---|
| lines (130) | False | 50.8% (66) | 71.5% (93) | 33.1% (43) | 50.0% (65) |
| words (741) | False | 29.8% (221) | 58.6% (434) | 15.1% (112) | 68.4% (507) |
| lines (130) | True | 50.8% (66) | 73.1% (95) | 32.3% (42) | 52.3% (68) |
| words (741) | True | 29.6% (219) | 58.0% (430) | 15.0% (111) | 69.2% (513) |

Per-system top1 (lines, no schwa deletion, out of 10):

| system | top1 | system | top1 |
|---|---|---|---|
| iso15919 | 0 (mean rank 11.8) | gfs | 1 |
| practical | 0 (mean rank 12.1) | sacred_nitnem | 9 |
| dr_sant_singh | 9 | iast | 9 |
| dr_thind | 1 | shackle | 1 |
| sttm | 4 | ipa | 10 |
| sttm_legacy | 5 | banidb_ipa | 9 |
| gursevak | 8 | | |

Words, no schwa deletion, top1 out of 57:

| system | top1 | system | top1 |
|---|---|---|---|
| dr_sant_singh | 54 | sttm | 5 |
| ipa | 57 | sttm_legacy | 5 |
| banidb_ipa | 47 | dr_thind | 1 |
| sacred_nitnem | 32 | iso15919 | 1 |
| iast | 11 | practical | 0 |
| gursevak | 8 | gfs | 0 |
| | | shackle | 0 |

Main confusions (true → predicted top1), lines, no schwa deletion:

| true | predicted | count (of 10) |
|---|---|---|
| gfs | dr_sant_singh | 9 |
| iso15919 | iast | 8 |
| dr_thind | dr_sant_singh | 8 |
| shackle | iast | 8 |
| practical | dr_sant_singh | 6 |
| sttm | dr_sant_singh | 6 |
| sttm_legacy | dr_sant_singh | 4 |
| practical | sttm | 3 |

On words: gfs, practical, dr_thind, sttm and sttm_legacy each go to dr_sant_singh in 48–54 of 57 cases; iso15919, iast and shackle go to sacred_nitnem in 27 of 57.

**Worked example** (sample line 3, ਆਦਿ ਸਚੁ ਜੁਗਾਦਿ ਸਚੁ ॥) — [compare.py](https://github.com/thehimmat/gurmukhi-transliterate/blob/70468d9/gurmukhi_transliterate/compare.py):
- ISO output `ādi sacu jugādi sacu ||` scores iast 0.739 = shackle 0.739, sacred_nitnem 0.652, … and ISO itself 0.087 (rank 12). Only the two `ā` tokens count for ISO.
- The same string is Shackle's output, so ISO, IAST and Shackle are indistinguishable on this line in any scheme.
- STTM `aadhi sachu jugaadhi sachu ||` ties five systems at 0.739.

**Out-of-domain input** — [compare.py](https://github.com/thehimmat/gurmukhi-transliterate/blob/70468d9/gurmukhi_transliterate/compare.py):

| input | top results |
|---|---|
| "The quick brown fox jumps over the lazy dog" | shackle 0.756, sacred_nitnem 0.707 |
| "Satnam Waheguru" | 4-way tie at 0.867 |
| "sat naam kartaa purakh" | 4-way tie at 0.842 |

**Existing tests** only assert loose properties: some practical-family system in the top 4 for `vaahiguroo`, a scholarly system in the top 3 for `vahigurū`, IPA first for IPA text. None checks the true system is first — [tests/test_compare.py](https://github.com/thehimmat/gurmukhi-transliterate/blob/70468d9/tests/test_compare.py)

### Inferences
- **Failure modes, in order of impact:**
  1. **Coverage, not likelihood.** The score rewards systems whose inventory is a superset. Common tokens (s, h, k, a, i, u, n, r…) are shared by 9–11 systems, so most systems score alike, and nothing penalises a system for not producing an observed pattern (e.g. Thind never emits `ṭ`).
  2. **Ties resolved by list order.** About half of line trials and two thirds of word trials tie at the top, and `dr_sant_singh` wins them by position.
  3. **ISO/practical under-indexed.** They are structurally unidentifiable.
  4. **Systems that truly coincide.** ISO, IAST and Shackle on text without ē/ō, ṛ, nukta or nasal produce identical strings. Thind and GFS share the same retroflex/dental and ṇ/n mergers and differ only in a few letters: ੜ (rh vs r), ੌ (ou vs au), ਫ (f vs ph), ਙ/ਞ, the nukta letters, and bindi (n vs silent). No scorer can separate these without discriminating evidence, so the output should be a *set* of equivalent systems.
  5. **Lowercasing** throws away STTM's T/Th/R evidence.
  6. **No reject option**, so English scores as high as real romanization.
- **A likelihood scorer would fix 1, 2 and 6.** Use log P(tokens | system) from each system's forward output distribution (or from token presence/absence with smoothing), add a background/English model, and report ties as equivalence classes. The forward engines plus a Gurmukhi corpus can generate training text cheaply, but see the Q1 caveat about engine output ≠ real text.

### Gaps
- Accuracy on real romanized text, which is inconsistent and mixes schemes, was not measured; there is no such fixture in the repo (#16 Q1).
- Line-level numbers rest on 10 lines; they show the failure modes clearly but carry wide uncertainty: about ±9 percentage points at 95% for n=130 trials by binomial approximation, and more in practice because the trials cluster (13 systems × 10 lines).

---

## Q4. How does `reverse.py` do on Shackle output, and what generalises?

### Takeaway
- **Round-trip accuracy on Shackle output** (Gurmukhi → `GurmukhiRomanizer('shackle')` → `reverse_transliterate`): 70/71 running Japji words (98.6%) and 56/57 unique words. The one miss is the ਉ hiatus (ਨਿਰਭਉ → ਨਿਰਭੌ).
- **On the 20-word supplement:** 12/20 exact and 15/20 with candidates. Most failures come from the forward engine dropping addak and nasals, not from `reverse.py`.
- **Design parts that generalise:** the `Ambiguity` record, `candidate_spellings` and `CorpusMatcher`.
- **Design parts that do not:** the hard-coded Shackle token table, greedy tokenisation, and the inherent-`a` conjunct rule.

### Cited Findings

**Round-trip method.** `rom = GurmukhiRomanizer('shackle').romanize(w + ' ').rstrip()`, then `reverse_transliterate(rom)`. Exact = primary equals the original word (NFC). Candidates = `matcher.candidate_spellings(result)`. Results (`out_reverse.txt`) — [reverse.py](https://github.com/thehimmat/gurmukhi-transliterate/blob/70468d9/gurmukhi_transliterate/reverse.py), [matcher.py](https://github.com/thehimmat/gurmukhi-transliterate/blob/70468d9/gurmukhi_transliterate/matcher.py):

| set | exact | truth in candidates | mean candidates (max) | ambiguity flags |
|---|---|---|---|---|
| Japji running words (71) | 70 (98.6%) | 70 | 1.14 (3) | 6 persian_collision, 2 nasalization |
| Japji unique words (57) | 56 (98.2%) | 56 | 1.16 | — |
| supplement (20) | 12 (60%) | 15 (75%) | 1.70 (3) | — |

- The only Japji failure: ਨਿਰਭਉ → `nirabhau` → ਨਿਰਭੌ. Genuine Shackle writes the hiatus as `nirabhaü`, which `reverse.py` maps correctly to ਨਿਰਭਉ; the generic forward engine never emits `ü`.
- `CorpusMatcher` with an oracle lexicon (the sample's own words, frequency = count) picks the truth for 56/57; the failure is the same word, which has no alternative to rank.

Supplement failures and their causes:

| word | Shackle output | reverse primary | cause |
|---|---|---|---|
| ਸਿੱਖ | `sikha` | ਸਿਖ | forward engine dropped the addak |
| ਇੱਕ | `ika` | ਇਕ | forward engine dropped the addak |
| ਆਂਖ | `ākha` | ਆਖ | forward engine dropped the nasal |
| ਕਿਉਂ | `kiu` | ਕਿਉ | forward engine dropped the nasal |
| ਪੱਕਾ | `pakkā` | ਪਕਾ | ਪੱਕਾ is in the candidates (gemination flag) |
| ਮਾਂ | `māṁ` | ਮਾੰ | bindi is in the candidates; primary is tippi |
| ਖ਼ਾਲਸਾ | `khālasā` | ਖਾਲਸਾ | ਖ਼ is in the candidates (persian_collision) |
| ਅੰਮ੍ਰਿਤ | `amrita` | ਅੰਰਿਤ | real reverse bug (below) |

**Real `reverse.py` bugs found:**
- **`mr` read as a nasal group.** `amritu` → ਅੰਰਿਤੁ. The homorganic-nasal-group rule (§5) fires for a nasal before *any* consonant, including the non-homorganic `r`, so ਮ੍ਰ is lost.
- **Issue #13 artifacts still reproduce:** `ammritu` → ਅੰੰਰਿਤੁ (doubled tippi) and `daïā` → ਦïਆ (Latin ï leaks into the output).
- **Other #13 items now map correctly**, apparently since commit `55af6b7`: `jūṭhā` → ਜੂਠਾ, `kaṅkaṇu` → ਕੰਕਣੁ, `putru` → ਪੁਤ੍ਰੁ.

— [reverse.py](https://github.com/thehimmat/gurmukhi-transliterate/blob/70468d9/gurmukhi_transliterate/reverse.py), [issue #13](https://github.com/thehimmat/gurmukhi-transliterate/issues/13)

**Applying the Shackle reverse to other systems' output** (Japji unique words, exact) — [reverse.py](https://github.com/thehimmat/gurmukhi-transliterate/blob/70468d9/gurmukhi_transliterate/reverse.py):

| system output reversed | exact |
|---|---|
| IAST | 93.0% |
| ISO 15919 | 80.7% |
| Sacred Nitnem | 80.7% |
| practical | 31.6% |
| Sant Singh | 29.8% |
| Shackle with `delete_schwa=True` | 82.5% |

Shackle convention writes every inherent `a`, so the last row shows how sensitive the conjunct rule is to schwa.

**Design elements and how far they generalise** — [reverse.py](https://github.com/thehimmat/gurmukhi-transliterate/blob/70468d9/gurmukhi_transliterate/reverse.py), [matcher.py](https://github.com/thehimmat/gurmukhi-transliterate/blob/70468d9/gurmukhi_transliterate/matcher.py):
- **Tokeniser:** a greedy longest-match over a hard-coded list of `(roman, _Cons)` and `(roman, _Vowel)` pairs, with Shackle-specific flags (`is_nasal`, `aspirate_sonorant`, `persian_collision`).
- **Engine logic relies on two Shackle properties:**
  - the inherent `a` is always written, so two adjacent consonant tokens always form a conjunct
  - nasal + consonant = ੰ (homorganic group)
- **`Ambiguity`** = `(kind, source, chosen, alternatives, start offset, note)`.
- **`candidate_spellings`** takes the cartesian product of chosen + alternatives at those offsets, capped at `_MAX_CANDIDATES = 256`.
- **`CorpusMatcher`** keeps candidates attested in an injected `{word: freq}` lexicon and ranks them by frequency, then primary-first, then length; it falls back to the primary when nothing matches.

### Inferences

**Generalises well:**
- **`Ambiguity` + `candidate_spellings` + `CorpusMatcher`** are system-agnostic. A SystemMap-driven reverse can emit the same records with new `kind` values (see Q1 Inferences) and reuse the matcher unchanged.
- **Inverted SystemMap as a substitution table.** The per-token alternatives can be built automatically by inverting each SystemMap: roman token → list of Gurmukhi letters. A list longer than one *is* the collision class. For example, Thind `t` → [ਟ, ਤ] is `kind='retroflex_dental'`.

**Needs redesign:**
1. **Greedy tokenisation** must become a lattice/DP over all segmentations, because of real segmentation collisions: `kh` = ਖ or ਕ+ਹ; `ai` = ੈ or a+ਇ; `au` = ੌ or a+ਉ; sttm_legacy `a` = inherent or ੌ; `tt`/`rr` digraph vs geminate. `Ambiguity` records that replace a fixed-length span cannot express alternative segmentations cleanly.
2. **The inherent-`a` conjunct rule** fails once the schwa is deleted. That is the default for most real romanized text and the behaviour of `practical` before spaces.
3. **The 256 cap** in `candidate_spellings` is too low for lossy systems: sttm_legacy reaches 1,008 raw candidates for one 9-character word, GFS 1,056. Enumerate-then-filter should become lexicon-guided search (walk a trie of the SGGS word index while expanding the lattice), or noisy-channel scoring.
4. **Case and markup handling** in the tokeniser: STTM capitals, parenthesised `(n)`/`n(g)`/`g(h)`, superscript `ⁿ`, Gursevak subscripts and `‹›` colour markup, and IPA combining characters (e.g. banidb tone marks stripped).

**Test data.** Evaluate on real romanized text, not on engine output. The forward engines' artifacts (Q1) would otherwise inflate round-trip scores for the wrong reasons, or invent failures (ਸਿੱਖ → `sikha`).

### Gaps
- The README's "92% exact, 97% with candidates on 5,959 glossary head-words" could not be re-run: the glossary data is not in the repo — [README.md](https://github.com/thehimmat/gurmukhi-transliterate/blob/70468d9/README.md)
- No real lexicon was available to measure `CorpusMatcher` on non-oracle data.

---

## Q5. Context from open issues #13, #10, #4, #16

### Takeaway
- #16 is the parent research issue and asks for exactly this matrix plus an approach.
- #13 and #10 list gaps in the Shackle reverse. Some #13 items are already fixed and the two artifact bugs still reproduce; #10's hiatus case is the one Japji failure.
- #4 notes that the maps were hand-entered; several collisions above trace to map choices, so #4 bears directly on detection and reversal accuracy.

### Cited Findings

**#16** (open), "Detect romanized Gurmukhi and reverse-transliterate it from any system (research first)" — [issue #16](https://github.com/thehimmat/gurmukhi-transliterate/issues/16):
- Calls `identify_system` "greedy token overlap… common tokens make most systems score alike… no 'not Gurmukhi' outcome". This is confirmed quantitatively in Q3.
- Lists reverse challenges: retroflex/dental, aspiration, ਣ/ਨ, ਸ/ਸ਼, schwa deletion, tippi/bindi, addak, final short vowels, inconsistent aa/a, OCR diacritic loss, mixed English.
- Proposes phases: (1) a SystemMap-driven reverse with Shackle as the first case; (2) a detector with a "not Gurmukhi" outcome and real confidence; (3) corpus ranking plus verse alignment.

**#13** (open), "Reverse engine: systematic gaps found via Shackle OCR cross-check" — [issue #13](https://github.com/thehimmat/gurmukhi-transliterate/issues/13):
- Reports ṭh → ਥ (`jūṭhā`), ṇ → ਨ (`kaṅkaṇu`, `bālaṇu`), dropped ੍ਰ (`putru`), and the artifacts `ï` and doubled ੰੰ.
- On the current code, the first three produce the correct Gurmukhi; `ammritu` → ਅੰੰਰਿਤੁ and `daïā` → ਦïਆ still reproduce (Q4).

**#10** (open), "bearer-vowel hiatus (saü/aï) and underlined Perso-Arabic source signs" — [issue #10](https://github.com/thehimmat/gurmukhi-transliterate/issues/10):
- Hiatus forms and underlined Perso-Arabic signs (s̲ s̲h̲ z̲ ż ẓ k͟h ʿ) are not handled.
- The repo's Shackle map degrades ਖ਼ to `kh` because the combining underline renders badly ([systems.py](https://github.com/thehimmat/gurmukhi-transliterate/blob/70468d9/gurmukhi_transliterate/systems.py)). That collision causes 5–6 of the `persian_collision` flags measured on Japji.

**#4** (open), "Audit hand-entered other-system maps for transcription errors" — [issue #4](https://github.com/thehimmat/gurmukhi-transliterate/issues/4):
- Covers BaniDB STTM, legacy STTM/iGurbani and BaniDB IPA (commit `8c3d611`); Gursevak is tracked separately in #1.
- Map entries behind collisions or drops above, documented in the map notes as intentional or source-attested — [systems.py](https://github.com/thehimmat/gurmukhi-transliterate/blob/70468d9/gurmukhi_transliterate/systems.py):
  - STTM ਦ=ਧ=`dh`, ਡ=ਢ=`dd`
  - sttm_legacy ੌ=`a`, ਔ=`a`, ਉ=ਓ=`ou`, ਛ=`shh`
  - banidb_ipa ਢ=ਟ=`ʈ`, ਧ=ਤ=`t` (tone mark not stored), ਗ=`G`, ਔ=`None`
  - Gursevak ਯ=`Y`
- Practical's `MODIFIERS` maps ੰ→ṁ and ਂ→ṃ, the reverse of ISO's ੰ→ṃ, ਂ→ṁ. The table is unused by `to_practical`, but it is a latent inconsistency — [practical.py](https://github.com/thehimmat/gurmukhi-transliterate/blob/70468d9/gurmukhi_transliterate/practical.py)

**User stories:**
- US-005 ("Identify the transliteration/encoding of unknown input") is marked `status: delivered` with no linked tests.
- US-004 (compare systems) is delivered and links #4.

— [user-stories/US-005-identify-unknown-input.md](https://github.com/thehimmat/gurmukhi-transliterate/blob/70468d9/user-stories/US-005-identify-unknown-input.md), [user-stories/US-004-compare-systems.md](https://github.com/thehimmat/gurmukhi-transliterate/blob/70468d9/user-stories/US-004-compare-systems.md)

### Inferences
- **US-005 is "delivered" in name only.** Given Q3 (15% unique-correct on words, English scored as romanized Gurmukhi), the story should be reopened or narrowed.
- **Before building on the forward engines, fix:**
  - the `_core` addak/nasal drops
  - practical's nukta/addak bugs
  - ISO's crash
  - the `schwa.py` R1-before-vowel bug

  Every reverse fixture generated from the engines, and any likelihood model trained on engine output, inherits these.
- **Order of #4's audit.** It changes the reverse candidate classes directly (e.g. if STTM really distinguishes ਦ/ਧ in some contexts). It should come before freezing the ambiguity kinds for a SystemMap-driven reverse.

### Gaps
- Issue comments were not read beyond the bodies; #10 had one comment, "Sub-task of #7", and #7 itself was not reviewed.
- The kosh cross-check data mentioned in #13 is not in this repo, so its 3% divergence breakdown could not be checked.
