# Tippi (ੰ) and bindi (ਂ) before each consonant class: what each system actually writes

Researched 2026-10-07 for #22. The scripts, downloads and raw outputs were session scratch and are not committed; the strings quoted below are verbatim from them.

Classes: velar ਕ ਖ ਗ ਘ · palatal ਚ ਛ ਜ ਝ · retroflex ਟ ਠ ਡ ਢ · dental ਤ ਥ ਦ ਧ ਨ · labial ਪ ਫ ਬ ਭ ਮ.

Confidence labels:
- **run**: I ran the system's own code (anvaad-js 1.5.1, gurmukhi-utils 3.2.2).
- **primary**: I read the system's real published output (BaniDB API, the igurbani.com API, page scans of the printed book, or a verbatim copy of srigranth text).
- **secondary**: second-hand (the repo's own notes, or translation prose rather than transliteration).
- **convention**: a published standard or phonetics, not one specific corpus.
- **snippet**: a web-search snippet only.
- **none**: no evidence found.

## 1. Table

| system | sign | velar | palatal | retroflex | dental | labial | evidence (verbatim; source) | confidence |
|---|---|---|---|---|---|---|---|---|
| **sttm** (BaniDB `english`) | ੰ | (n) | (n) | (n) | (n) | **(n)** | ਅਸੰਖ→asa(n)kh, ਨਿਰੰਜਨੁ→nira(n)jan, ਖੰਡਾ→kha(n)ddaa, ਅੰਦਰਿ→a(n)dhar, ਕੰਮ→ka(n)m, ਕੁਟੰਬੁ→kuTa(n)b, ਸੰਪੈ→sa(n)pai, ਗੰਭੀਰੁ→ga(n)bheer, ਅੰਮ੍ਰਿਤ→a(n)mirat (Japji, ang 2); api.banidb.com angs 1–200 and anvaad-js | run + primary |
| sttm | ਂ | (n) | (n) | (n) | (n) | **(n)** | ਮਾਂਗ→maa(n)g, ਮਾਂਝ→maa(n)jh, ਭਾਂਡਾ→bhaa(n)ddaa, ਸਾਂਤਿ→saa(n)t, ਕਾਂਮ→kaa(n)m (ang 202), ਆਂਬੁ→aa(n)b (ang 972), ਜਾਂਮੈ→jaa(n)mai (ang 1205) | run + primary |
| **sttm_legacy** (igurbani.com, SGGS) | ੰ | n | n | n | n | **n** | ਅਸੰਖ→asankh, ਨਿਰੰਜਨੁ→niranjan, ਖੰਡ→khandd, ਅੰਤੁ→anth, ਅੰਮ੍ਰਿਤ→anmrith (ang 2), ਕੰਮ→kanm (ang 78), ਕੁਟੰਬੁ→kuttanb, ਸੰਪੈ→sanpai, ਗੰਭੀਰੁ→ganbheer, ਅਪਰੰਪਰੁ→aparanpar; 250 shabads (angs 1–89) + search API | primary |
| sttm_legacy | ਂ | n | n | n | n | **n** | ਮਾਂਗ→maang, ਮਾਂਜੀਐ→maanjeeai, ਭਾਂਡਾ→bhaanddaa, ਸਾਂਤਿ→saanth, ਕਾਂਮ→kaanm (ang 202), ਆਂਬੁ→aaanb (ang 972), ਜਾਂਮੈ→jaanmai (ang 1205) | primary |
| **banidb_ipa** (BaniDB `ipa`) | ੰ | ŋ | ŋ | ŋ | ŋ | **ŋ** | ਅਸੰਖ→əsəŋkʰ, ਪੰਜ→pəŋd͡ʒ, ਖੰਡ→kʰəŋɖ, ਅੰਤੁ→əŋt̪, ਕੰਮ→kəŋm, ਕੁਟੰਬੁ→kʊʈəŋb, ਸੰਪੈ→səŋpæ, ਗੰਭੀਰ→Gəŋɓir, ਅੰਮ੍ਰਿਤ→əŋmɪɹət̪ | run + primary |
| banidb_ipa | ਂ | ⁿ | ⁿ | ⁿ | ⁿ | **ⁿ** | ਮਾਂਗ→mɑⁿəG, ਮਾਂਝ→mɑⁿəɖ͡ʐ, ਭਾਂਡਾ→ɓɑⁿəɖɑ, ਸਾਂਤਿ→sɑⁿət̪, ਕਾਂਮ→kɑⁿəm, ਆਂਬੁ→əɑⁿəb, ਕਾਂਪੈ→kɑⁿəpæ | run + primary |
| **dr_thind** (srigranth text, via verbatim copies on GitHub) | ੰ | n (sometimes N) | n | n | n | **m** | ਅਸੰਖ→asaNkh, ਨਿਰੰਕਾਰ→nirankaar, ਨਿਰੰਜਨੁ→niranjan, ਖੰਡ→khand, ਅੰਤੁ→ant; **ਕੁਟੰਬੁ→kutamb, ਸੰਬਤਿ→sambat, ਕੰਮੁ→kamm, ਅਗੰਮ→agamm, ਜੰਮਿਆ→jammi-aa**, ਅੰਮ੍ਰਿਤ→amrit (nasal merges into the m) | primary (third-party copies) |
| dr_thind | ਂ | – | – | N | N | – | ਭਾਂਡਾ→bhaaNdaa, ਸਾਂਤਿ→saaNt; no velar, palatal or labial case in the corpus | primary (thin) |
| **sacred_nitnem** (H. S. Doabia, *Sacred Nitnem*, Singh Brothers 2005) | ੰ | ṅ | ṅ | ṅ | ṅ | **ṅ** | Asaṅkh, Niraṅkār, maṅgeh, niraṅjan(u), aṅdh, niṅdak, Maṅnai, aṅt(u); **kuṭaṅb(u), kaṅm(u), agaṅm(u), aṅmrit(u)** (Anand Sahib, p.174); but Japji p.24 has "Amrit velā" (nasal not written) | primary (page scans) |
| sacred_nitnem | ਂ | – | – | – | – | – | Key to Pronunciation: ਆਂ = **āṅ** ("ān … as in 'can't'"). I found no bindi-before-consonant word in the running text | primary (key only) |
| **dr_sant_singh** | ੰ | n | n | n | n | **m** | Translation prose only: Sangat, Panch, Pandit, Gobind; **Ambreek, Gambheer, Kumbha**, Simritees, Amrit | secondary (translation prose, not transliteration) |
| dr_sant_singh | ਂ | – | – | – | – | – | none | none |
| **gursevak** | ੰ | – | – | – | ⁿ | **ⁿ** | ਅੰਦਰਿ→Aⁿdare, ਅੰਮ੍ਰਿਤ→Aⁿmᵣet (repo notes from the app's SQLite, v3.01) | secondary (repo notes; no access to the app/APK) |
| gursevak | ਂ | – | – | – | – | – | none beyond the repo's "superscript ⁿ nasals" | secondary |
| **gfs** | ੰ / ਂ | – | – | – | – | – | no reachable samples | none |
| **iast** | ੰ | ṃ (or ṅ) | ṃ (or ñ) | ṃ (or ṇ) | ṃ (or n) | **ṃ (or m)** | Anusvāra is ṃ letter for letter. Writing the homorganic nasal is a spelling choice: "clusters of nasal plus plosive were written using the nasal consonant in Europe but using anusvara in India" (Wikipedia, *Anusvara*) | convention (snippet) |
| iast | ਂ | ṁ | ṁ | ṁ | ṁ | ṁ | Bindu/nasal vowel; no homorganic convention | convention |
| **shackle** | ੰ | ṅ | ñ | ṇ | n | **m** | §5: ਸੰਕ saṅka, ਸੰਚ sañca, ਸੰਟ saṇṭa, ਸੰਤ santa, ਸੰਪ sampa (*A Guru Nanak Glossary*, as cited in the brief and `systems.py`) | primary (cited, not re-read by me) |
| shackle | ਂ | ṁ | ṁ | ṁ | ṁ | ṁ | §6 pure nasalization ṁ (repo notes) | secondary |
| **ipa** (academic) | ੰ | ŋ | ɲ | ɳ | n | **m** | Phonetic: "in front of a labial plosive like p, the bilabial nasal m is pronounced; in front of a dental plosive like t the dental nasal n …; in front of a guttural plosive like k, the guttural nasal ṅ" (Wikipedia, *Anusvara*); Shackle §5 says the same for Gurbani | convention (snippet) |
| ipa | ਂ | ◌̃ (± homorganic) | ◌̃ | ◌̃ | ◌̃ | ◌̃ | Vowel nasalization. A short homorganic nasal stop often follows before a stop, but transcriptions vary | convention |
| *Shabad OS `toEnglish`* (reference) | ੰ | n | n | n | n | **n**, but ੰ+ਮ → m | ਅੰਗ→ang, ਪੰਜ→panj, ਕੰਡਾ→kanddaa, ਸੰਤ→sant, ਲੰਬਾ→lanbaa, ਸੰਪੂਰਨ→sanpooran, ਕੁਟੰਬੁ→kuttanb, ਸੰਭਾਲ→sanbhaal; but ਕੰਮ→kam, ਅੰਮ੍ਰਿਤ→amrit, ਅਗੰਮ→agam (and ਮੰਨੈ→manai) | run |
| *Shabad OS* | ਂ | n | n | n | n | **n**, but ਂ+ਮ → m | ਸਾਂਝ→saanjh, ਭਾਂਡਾ→bhaanddaa, ਨਾਂਵ→naanv, ਆਂਬੁ→aanb, ਕਾਂਪੈ→kaanpai; but ਕਾਂਮ→kaam | run |

## 2. Recommendations, and where "labial → m" fails

**The idea that labials take m "for all in that family" is wrong for most systems.** Only Thind, Shackle, academic IPA and (weakly) Sant Singh write m before labials. The data-driven systems all keep their fixed nasal.

| system | recommendation | labial → m? |
|---|---|---|
| sttm | **Keep fixed `(n)`** for both signs. | **CONTRADICTED.** ka(n)m, kuTa(n)b, sa(n)pai, ga(n)bheer, kaa(n)m, aa(n)b |
| sttm_legacy | **Keep fixed `n`.** | **CONTRADICTED.** kanm, anmrith, kuttanb, sanpai, ganbheer, kaanm, aaanb |
| banidb_ipa | **Keep fixed `ŋ` / `ⁿ`.** BaniDB's IPA does no assimilation at all, not even before ਮ. | **CONTRADICTED.** kəŋm, kʊʈəŋb, səŋpæ, Gəŋɓir, kɑⁿəm |
| sacred_nitnem | **Keep fixed `ṅ`.** | **CONTRADICTED.** kuṭaṅb(u), kaṅm(u), agaṅm(u), aṅmrit(u). One inconsistency: Japji "Amrit velā" drops the nasal |
| gursevak | **Keep fixed `ⁿ`.** The evidence is only the repo's own notes. | **Likely contradicted** (Aⁿmᵣet), not independently verified |
| dr_thind | **Labial-only `m` for tippi**; keep `n` elsewhere. Thind writes bindi as `N` (bhaaNdaa, saaNt), and sometimes tippi too (asaNkh, ahaNkaar). That is a separate fix if wanted. | **Confirmed** for tippi: kutamb, sambat, kamm, agamm, jammi-aa. No bindi+labial example |
| dr_sant_singh | **Labial-only `m` (tentative)**; keep `n` elsewhere. The only evidence is his English translation prose (Ambreek, Gambheer, Kumbha against Sangat, Panch, Pandit). Per a search snippet, the transliteration in the SikhNet/srigranth SGGS PDF beside his translation is by Thind ("the phonetic transliteration was done by Kulbir Singh Thind, MD, while the English translation was by Dr. Sant Singh Khalsa" — sikhnet.com node/46279, snippet). iGurbani shows the legacy STTM transliteration beside his translation, not one of his own. So the provenance of the repo's `dr_sant_singh` map is unclear. | Weakly confirmed (prose only) |
| gfs | **Keep fixed `n`.** I could not reach any source. | No evidence |
| iast | **Keep fixed `ṃ`/`ṁ`** (strict letter-for-letter). Optionally offer full homorganic as a variant. A labial-only rule matches neither convention. | Not a rule: strict IAST gives ṃ |
| shackle | **Full homorganic table for tippi** (already in `nasal_by_class`). Bindi stays ṁ. | Confirmed (§5 sampa) |
| ipa | **Full homorganic table for tippi**: ŋ ɲ ɳ n m. Keep ◌̃ for bindi. | Confirmed (phonetics) |
| Shabad OS (reference) | Not a repo system. Its only special case is nasal + identical nasal letter collapsing (ੰਮ/ਂਮ → m, ੰਨ → n). Before ਪ ਫ ਬ ਭ it writes n. | **Contradicted** for ਪ ਫ ਬ ਭ |

Side findings:
- BaniDB metathesises inconsistently: ਅੰਮ੍ਰਿਤ → a(n)mirat, but ਅੰਮ੍ਰਿਤੁ → a(n)mrit.
- BaniDB IPA puts an extra ə after kanna + bindi (ਸਾਂਝ → sɑⁿəɖ͡ʐ, ਆਂਬੁ → əɑⁿəb). The repo's `banidb_ipa` gives sɑⁿɖʐ.
- igurbani.com is not uniform. SGGS and Bhai Gurdas use the legacy scheme (ਨਾਂਵ → naanv). Its Dasam Granth (SDGS) lines use the BaniDB-style `(n)` (ਸੰਪੂਰਨ → sa(n)pooran, ਕਾਂਪੈ → kaa(n)pai).
- igurbani legacy has a few oddities: ਦੇਂਦਾ → dhaenadhaa, ਆਂਬੁ → aaanb.

## 3. Exact strings observed

### anvaad-js 1.5.1 `translit()` (English and `'ipa'`), input converted with its own `unicode(w, true)` — run
```
ਅੰਮ੍ਰਿਤ AMimRq  a(n)mirat    əŋmɪɹət̪
ਕੰਮ     kMm     ka(n)m       kəŋm
ਬੰਦਾ    bMdw    ba(n)dhaa    bəŋd̪ɑ
ਸੰਤ     sMq     sa(n)t       səŋt̪
ਅੰਗ     AMg     a(n)g        əŋG
ਸਿੰਘ    isMG    si(n)gh      sɪŋGʰə̀
ਪੰਜ     pMj     pa(n)j       pəŋd͡ʒ
ਕੰਡਾ    kMfw    ka(n)ddaa    kəŋɖɑ
ਸੰਪੂਰਨ  sMpUrn  sa(n)pooran  səŋpurən
ਲੰਬਾ    lMbw    la(n)baa     ləŋbɑ
ਸਾਂਝ    sWJ     saa(n)jh     sɑⁿəɖ͡ʐ
ਭਾਂਡਾ   BWfw    bhaa(n)ddaa  ɓɑⁿəɖɑ
ਨਾਂਵ    nWv     naa(n)v      nɑⁿəʋ
ਸੰਕ sa(n)k səŋk | ਸੰਚ sa(n)ch səŋt͡ʃ | ਸੰਟ sa(n)T səŋʈ | ਸੰਪ sa(n)p səŋp
ਥੰਮ tha(n)m t̪ʰəŋm | ਸੰਭਾਲ sa(n)bhaal səŋɓɑl | ਅੰਬ a(n)b əŋb | ਕੁੰਭ ku(n)bh kʊŋɓ
ਜਾਂਪ jaa(n)p d͡ʒɑⁿəp | ਸਾਂਬ saa(n)b sɑⁿəb | ਕੀਂਮ kee(n)m kiⁿm | ਭੀਂਬ bhee(n)b ɓiⁿb
```
(full list: `out/anvaad.tsv`)

### api.banidb.com real verses (`english` | `ipa`) — primary
```
ang 2    ਅੰਮ੍ਰਿਤ ਵੇਲਾ ਸਚੁ ਨਾਉ ਵਡਿਆਈ ਵੀਚਾਰੁ ॥ | a(n)mirat velaa sach naau vaddiaaiee veechaar || | əŋmɪɹət̪ ʋelɑ sət͡ʃ nɑo ʋəɖɪəɑei ʋit͡ʃɑr.
ang 2    ਆਪੇ ਆਪਿ ਨਿਰੰਜਨੁ ਸੋਇ ॥ | aape aap nira(n)jan soi || | əɑpe əɑp nɪrəŋd͡ʒən sɔeɪ.
ang 2    ਨਵਾ ਖੰਡਾ ਵਿਚਿ ਜਾਣੀਐ ... | navaa kha(n)ddaa vich ... | nəʋɑ kʰəŋɖɑ ʋɪt͡ʃ ...
ang 2    ਆਖਹਿ ਮੰਗਹਿ ਦੇਹਿ ਦੇਹਿ ... | aakheh ma(n)geh dheh dheh ... | əɑkʰəh məŋGəh ...
ang 3    ਸੁਣਿਐ ਸਤੁ ਸੰਤੋਖੁ ਗਿਆਨੁ ॥ | suniaai sat sa(n)tokh giaan || | sʊɳɪæ sət̪ səŋt̪ɔkʰ Gɪəɑn.
ang 8    ਭਾਂਡਾ ਭਾਉ ਅੰਮ੍ਰਿਤੁ ਤਿਤੁ ਢਾਲਿ ॥ | bhaa(n)ddaa bhaau a(n)mrit tit ddaal || | ɓɑⁿəɖɑ ɓɑo əŋmɪɹət̪ t̪ɪt̪ ʈɑl.
ang 13   ... ਤਿਨ ਅੰਤਰਿ ਹਉਮੈ ਕੰਡਾ ਹੇ ॥ | ... tin a(n)tar haumai ka(n)ddaa he || | ... t̪ɪn əŋt̪ər hoʊmæ kəŋɖɑ he.
ang 24   ਤੀਹ ਕਰਿ ਰਖੇ ਪੰਜ ਕਰਿ ਸਾਥੀ ... | teeh kar rakhe pa(n)j kar saathee ... | t̪ih kər rəkʰe pəŋd͡ʒ ...
ang 78   ਸਾਹੁਰੜੈ ਕੰਮ ਸਿਖੈ ... | saahuraRai ka(n)m sikhai ... | sɑhʊrəɽæ kəŋm sɪkʰæ ...
ang 84   ਵਖਤੁ ਵੀਚਾਰੇ ਸੁ ਬੰਦਾ ਹੋਇ ॥ | vakhat veechaare su ba(n)dhaa hoi || | ʋəkʰət̪ ʋit͡ʃɑre s bəŋd̪ɑ hɔeɪ.
ang 198  ਗਊ ਚਰਿ ਸਿੰਘ ਪਾਛੈ ਪਾਵੈ ॥੨॥ | guoo char si(n)gh paachhai paavai ||2|| | Gou t͡ʃər sɪŋGʰə̀ ...
ang 202  ਤਾ ਤੇ ਸਿਧਿ ਭਏ ਸਗਲ ਕਾਂਮ ॥੨॥ | taa te sidh bhe sagal kaa(n)m ||2|| | ... səGəl kɑⁿəm.2.
ang 562  ... ਕਰਿ ਸਾਂਝੀ ਹਰਿ ਗੁਣ ਗਾਵਾਂ ॥ | ... kar saa(n)jhee har gun gaavaa(n) || | ... kər sɑⁿəɖ͡ʐi ...
ang 821  ਏਕੁ ਬਿਸਥੀਰਨੁ ਏਕੁ ਸੰਪੂਰਨੁ ... | ek bisatheeran ek sa(n)pooran ... | ... eek səŋpurən ...
ang 972  ਨੰੀਬੁ ਭਇਓ ਆਂਬੁ ਆਂਬੁ ਭਇਓ ਨੰੀਬਾ ... | na(n)eeb bhio aa(n)b aa(n)b bhio ... | nəⁿib ɓeɪo əɑⁿəb əɑⁿəb ...
ang 1205 ... ਬਿਨੁ ਬੀਜੈ ਨਹੀ ਜਾਂਮੈ ॥ | ... bin beejai nahee jaa(n)mai || | ... nəhi d͡ʒɑⁿəmæ.
word-aligned, angs 1–200: ਕੁਟੰਬੁ→kuTa(n)b/kʊʈəŋb, ਸੰਪੈ→sa(n)pai/səŋpæ, ਗੰਭੀਰੁ→ga(n)bheer/Gəŋɓir,
  ਅਪਰੰਪਰੁ→apara(n)par/əpərəŋpər, ਸੰਬਾਹੇ→sa(n)baahe, ਅਗੰਮ→aga(n)m/əGəŋm, ਮਾਂਗ→maa(n)g/mɑⁿəG,
  ਮਾਂਝ→maa(n)jh/mɑⁿəɖ͡ʐ, ਸਾਂਤਿ→saa(n)t/sɑⁿət̪, ਬਾਂਛਤ→baa(n)chhat/bɑⁿəɕət̪
```
(full: `out/banidb_align.json`, `out/search_words.json`)

### igurbani.com (legacy STTM), SGGS verses — primary
```
ang 2    ਅੰਮ੍ਰਿਤ ਵੇਲਾ ਸਚੁ ਨਾਉ; ਵਡਿਆਈ ਵੀਚਾਰੁ ॥ | anmrith vaelaa sach naao vaddiaaee veechaar ||
ang 8    ਭਾਂਡਾ ਭਾਉ; ਅੰਮ੍ਰਿਤੁ ਤਿਤੁ ਢਾਲਿ ॥ | bhaanddaa bhaao anmrith thith dtaal ||
ang 13   ਕਰਉ ਬੇਨੰਤੀ, ... ਸੰਤ ਟਹਲ ਕੀ ਬੇਲਾ ॥ | karo baenanthee ... santh ttehal kee baelaa ||
ang 13   ... ਤਿਨ ਅੰਤਰਿ ਹਉਮੈ ਕੰਡਾ ਹੇ ॥ | ... thin anthar houmai kanddaa hae ||
ang 24   ਤੀਹ ਕਰਿ ਰਖੇ, ਪੰਜ ਕਰਿ ਸਾਥੀ; ... | theeh kar rakhae panj kar saathhee ...
ang 78   ... ਗੁਰਮੁਖਿ ਸਾਹੁਰੜੈ ਕੰਮ ਸਿਖੈ ॥ | ... guramukh saahurarrai kanm sikhai ||
ang 84   ਵਖਤੁ ਵੀਚਾਰੇ; ਸੁ ਬੰਦਾ ਹੋਇ ॥ | vakhath veechaarae s bandhaa hoe ||
ang 198  ਗਊ ਚਰਿ; ਸਿੰਘ ਪਾਛੈ ਪਾਵੈ ॥੨॥ | goo char singh paashhai paavai ||2||
ang 202  ਤਾ ਤੇ ਸਿਧਿ ਭਏ; ਸਗਲ ਕਾਂਮ ॥੨॥ | thaa thae sidhh bheae sagal kaanm ||2||
ang 345  ਕਹਿ ਕਬੀਰ; ਤਬ ਨਿਰਮਲ ਅੰਗ ॥੮॥੧॥ | kehi kabeer thab niramal ang ||8||1||
ang 562  ... ਕਰਿ ਸਾਂਝੀ, ਹਰਿ ਗੁਣ ਗਾਵਾਂ ॥ | ... kar saanjhee har gun gaavaan ||
ang 972  ਨੰੀਬੁ ਭਇਓ ਆਂਬੁ, ਆਂਬੁ ਭਇਓ ਨੰੀਬਾ; ... | naneeb bhaeiou aaanb aaanb bhaeiou naneebaa ...
ang 1205 ... ਬਿਨੁ ਬੀਜੈ ਨਹੀ ਜਾਂਮੈ ॥ | ... bin beejai nehee jaanmai ||
word-aligned: ਅਸੰਖ→asankh, ਨਿਰੰਜਨੁ→niranjan, ਖੰਡ→khandd, ਕੁਟੰਬੁ→kuttanb (ang 32), ਸੰਪੈ→sanpai (ang 32),
  ਗੰਭੀਰੁ→ganbheer (ang 22), ਅਪਰੰਪਰੁ→aparanpar (ang 11), ਡੰਫੁ→ddanf (ang 50), ਅਗੰਮ→aganm (ang 4),
  ਮਾਂਗ→maang (ang 19), ਮਾਂਜੀਐ→maanjeeai (ang 56), ਸਾਂਤਿ→saanth, ਦੇਂਦਾ→dhaenadhaa (ang 85)
Dasam Granth on igurbani: ਸੰਪੂਰਨ→sa(n)pooran (SDGS 46), ਕਾਂਪੈ→kaa(n)pai (SDGS 1037), ਨਾਂਵ→naa(n)v (SDGS 897)
Bhai Gurdas on igurbani: ਨਾਂਵ→naanv, ਕਾਂਪੈ→kaanpai
```
(full: `out/igurbani_align.json`)

### Dr. Thind (srigranth text, as copied verbatim in GitHub repos `suhailsinghbains/Gurbani-Prayers-AngularJS` (Japji, Anand, Sohila) and `03-KOMALPREET-KAUR/AUTOMATIC-GURBANI-RECOGNITION-AND-MAPPING-SYSTEM`) — primary via third-party copies
```
"Ik-oNkaar sat naam kartaa purakh Nirbha-o nirvair / Akaal moorat ajoonee saibhaN Gur parsaad."
"Amrit vaylaa sach naa-o vadi-aa-ee veechaar."
"ayhu kutamb too je daykh-daa chalai naahee tayrai naalay."      (eyhu kutMbu qU ij dyKdw clY nwhI qyrY nwly)
"Aisaa kamm moolay na keechai jit ant pachhotaa-ee-ai."
"Kahai naanak too sadaa agamm hai tayraa ant na paa-i-aa."
word-aligned: ਅਸੰਖ→asaNkh, ਅਹੰਕਾਰੁ→ahaNkaar, ਨਿਰੰਕਾਰ→nirankaar, ਮੰਗਹਿ→mangahi, ਨਿਰੰਜਨੁ→niranjan,
  ਪੰਚ→panch, ਚੰਚਲ→chanchal, ਖੰਡ→khand, ਪੰਡਿਤ→pandit, ਕੰਟਕੁ→kantak, ਅੰਤੁ→ant, ਮੰਨੈ→mannai,
  ਕੁਟੰਬੁ→kutamb, ਸੰਬਤਿ→sambat, ਕੰਮੁ→kamm, ਅਗੰਮ→agamm, ਜੰਮਿਆ→jammi-aa, ਅੰਮ੍ਰਿਤੁ→amrit,
  ਭਾਂਡਾ→bhaaNdaa, ਸਾਂਤਿ→saaNt
```
(full: `out/thind_align_sggs.json`. The same repo's Jaap Sahib uses a different, non-Thind scheme (besvunbhr, aghumai), so I excluded it.)

### Sacred Nitnem (Harbans Singh Doabia, Singh Brothers, Amritsar 2005; archive.org item `sacred-nitnem-divine-hymns-of-daily-prayers-by-sikhs-by-harbans-singh-doabia-pun`, page scans n5/n25/n33/n39/n175 read directly) — primary
```
Key to Pronunciation: ਅੰ ṅ "n (as in 'sing')";  ਆਂ āṅ "an (as in 'can't')"
p.24  Ākheh maṅgeh deh(i) deh(i) dāt(i) kare dātār(u).
p.24  Amrit velā sach(u) nāo vaḍiāī vīchār(u).          [ਅੰਮ੍ਰਿਤ — nasal not written here]
p.24  Āpe āp(i) niraṅjan(u) soe.
p.32  Maṅnai mag(u) na chalai paṅth(u). / Maṅnai dharam setī sanbaṅdh(u).
p.38  Asaṅkh mūrakh aṅdh ghor. ... Asaṅkh niṅdak sir(i) karah(i) bhār(u).
p.38  Jo tudh(u) bhāvai sāī bhalī kār. Tū sadā salāmat(i) Niraṅkār.
p.38  Asaṅkh nāv asaṅkh thāv. Agaṅm agaṅm asaṅkh loa.
p.174 Eh(u) kuṭaṅb(u) tū je dekhdā, chalai nāhī terai nāle.
p.174 Aisā kaṅm(u) mūle na kīchai, jit(u) aṅt(i) pachhotāīai.
p.174 Kahai Nānak(u) tū sadā agaṅm(u) hai, terā aṅt(u) na pāiā.
p.174 Sur(i) nar mun(i) jan aṅmrit(u) khojde, su aṅmrit(u) gur te pāiā.
```

### Sant Singh Khalsa, English translation of SGGS (archive.org `AadGuruGranthSahibEnglish`, OCR text) — secondary (translation prose)
```
"The Lord blessed Ambreek with fearless dignity"
"Saaloo, Saarang, Saagaraa, Gond and Gambheer"
"Someone may go to the Ganges or the Godaavari, or to the Kumbha"
"the Panch Shabad, the Five Primal Sounds"   "The Pandit — the religious scholar"
"So chant Gobind, Gobind"   "joining the Sangat"   "the Shaastras, the Simritees"
```
Snippet (sikhnet.com/node/46279): "the phonetic transliteration was done by Kulbir Singh Thind, MD, while the English translation was by Dr. Sant Singh Khalsa".

### Shabad OS gurmukhi-utils 3.2.2 `toEnglish()` — run (read and run only; GPL code not copied)
```
ਅੰਮ੍ਰਿਤ amrit | ਕੰਮ kam | ਬੰਦਾ bandaa | ਸੰਤ sant | ਅੰਗ ang | ਸਿੰਘ singh | ਪੰਜ panj | ਕੰਡਾ kanddaa
ਸੰਪੂਰਨ sanpooran | ਲੰਬਾ lanbaa | ਸਾਂਝ saanjh | ਭਾਂਡਾ bhaanddaa | ਨਾਂਵ naanv
ਸੰਕ sank | ਸੰਚ sanch | ਸੰਟ santt | ਸੰਪ sanp | ਕੁਟੰਬੁ kuttanb | ਕੰਬ kanb | ਸੰਭਾਲ sanbhaal | ਸੰਫ sanf
ਜੰਮੈ jamai | ਅਗੰਮ agam | ਸੰਮਤ samat | ਸਿੰਮ੍ਰਿਤਿ sinmrit | ਮੰਨੈ manai | ਜਗੰਨਾਥ jaganaath
ਮਾਂਗ maang | ਮਾਂਝ maanjh | ਸਾਂਤਿ saant | ਆਂਬੁ aanb | ਕਾਂਮ kaam | ਕਾਂਪੈ kaanpai | ਵਰਸਾਂਨੇ varasaane
```
(`out/shabados.tsv`)

### Sources not reachable (blocked by the egress proxy)
srigranth.org, searchgurbani.com, sikhitothemax.org, sikhnet.com, sikhs.org, wikipedia.org, unicode.org, icann.org, Play Store and APK mirrors, web.archive.org. Reachable: api.banidb.com, igurbani.com (and its `/api/search`), archive.org, GitHub, npm. I found no samples for GFS, and none for Sant Singh's own transliteration or for Gursevak beyond the repo's notes.
