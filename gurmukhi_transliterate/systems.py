"""
Romanization system definitions for Gurmukhi.

Data sourced from comparative spreadsheet covering:
  Dr. Sant Singh Khalsa, Dr. Kulbir S. Thind (SikhNet), SikhiToTheMax,
  Guru Fatha Singh, Sacred Nitnem, IAST, IPA.

Plus systems scraped from live sites/APIs (July 2026), word-aligned against
Gurmukhi source text:
  - sttm:        current BaniDB English scheme (api.banidb.com) powering
                 sikhitothemax.org — replaces the old scheme, kept as sttm_legacy
  - sttm_legacy: the old SikhiToTheMax scheme, still used verbatim by
                 igurbani.com (verified against its own database July 2026)
  - banidb_ipa:  BaniDB's IPA transliteration (differs from the academic ipa map)
  - gursevak:    Learn Shudh Gurbani app romanization (extracted from the
                 app's bundled SQLite database, v3.01)

Normalisation applied to the raw sheet data:
  - All values lowercased — EXCEPT the BaniDB-derived sttm map, where capital
    T/Th/R are meaningful (they distinguish retroflex from dental)
  - "N/A" → None  (character not supported by that system, or unattested in
    scraped data — see each system's notes)
  - Variants like "V or W" → primary form ('v')
  - Apostrophe markers like Ṭ´H → normalised to ṭh
  - Parenthesised prefixes like (n)g → primary form 'ng'
  - "doubles letter" for addak → handled by engine, not stored here
"""

from __future__ import annotations
from dataclasses import dataclass, field


@dataclass(frozen=True)
class SystemMap:
    id: str
    label: str
    # Gurmukhi char → romanization (None = not supported)
    consonants: dict[str, str | None]
    vowel_diacritics: dict[str, str | None]
    vowels: dict[str, str | None]   # independent vowel letters (ਅ ਆ ...)
    nasal_tippi: str | None         # ੰ romanization
    nasal_bindi: str | None         # ਂ romanization
    subjoined: dict[str, str | None]  # ੍ਰ ੍ਵ ੍ਹ ...
    notes: str = ''


# ---------------------------------------------------------------------------
# System definitions
# ---------------------------------------------------------------------------

DR_SANT_SINGH = SystemMap(
    id='dr_sant_singh',
    label='Dr. Sant Singh Khalsa',
    consonants={
        'ਸ': 's', 'ਹ': 'h',
        'ਕ': 'k', 'ਖ': 'kh', 'ਗ': 'g', 'ਘ': 'gh', 'ਙ': 'ng',
        'ਚ': 'ch', 'ਛ': 'chh', 'ਜ': 'j', 'ਝ': 'jh', 'ਞ': None,
        'ਟ': 'ṭ', 'ਠ': 'ṭh', 'ਡ': 'ḍ', 'ਢ': 'ḍh', 'ਣ': 'ṇ',
        'ਤ': 't', 'ਥ': 'th', 'ਦ': 'd', 'ਧ': 'dh', 'ਨ': 'n',
        'ਪ': 'p', 'ਫ': 'f',  # Sant Singh uses F for both ਫ and ਫ਼
        'ਬ': 'b', 'ਭ': 'bh', 'ਮ': 'm',
        'ਯ': 'y', 'ਰ': 'r', 'ਲ': 'l', 'ਵ': 'v', 'ੜ': 'ṛ',
        # Persian
        'ਸ਼': 'sh', 'ਜ਼': 'z', 'ਗ਼': 'g', 'ਖ਼': 'kh', 'ਫ਼': 'f', 'ਲ਼': None,
    },
    vowel_diacritics={
        'ਾ': 'aa', 'ਿ': 'i', 'ੀ': 'ee',
        'ੁ': 'u', 'ੂ': 'oo', 'ੇ': 'ay', 'ੈ': 'ai',
        'ੋ': 'o', 'ੌ': 'aau',
    },
    vowels={
        'ਅ': 'a', 'ਆ': 'aa', 'ਇ': 'i', 'ਈ': 'ee',
        'ਉ': 'u', 'ਊ': 'oo', 'ਏ': 'ay', 'ਐ': 'ai',
        'ਓ': 'o', 'ਔ': 'aau',
    },
    nasal_tippi='n',
    nasal_bindi='n',
    subjoined={'੍ਰ': 'r', '੍ਵ': 'v', '੍ਹ': None, '੍ਤ': None, '੍ਯ': None},
    notes=(
        'Dots on retroflex letters (ṭ ḍ ṇ ṛ). '
        'Apostrophe marker ´H used for aspiration (Ṭ´H = ṭh). '
        'Both ਫ and ਫ਼ romanized as F (collision).'
    ),
)

DR_THIND = SystemMap(
    id='dr_thind',
    label='Dr. Kulbir S. Thind (SikhNet)',
    consonants={
        'ਸ': 's', 'ਹ': 'h',
        'ਕ': 'k', 'ਖ': 'kh', 'ਗ': 'g', 'ਘ': 'gh', 'ਙ': 'ny',
        'ਚ': 'ch', 'ਛ': 'chh', 'ਜ': 'j', 'ਝ': 'jh', 'ਞ': None,
        # Retroflexes merged with dentals
        'ਟ': 't', 'ਠ': 'th', 'ਡ': 'd', 'ਢ': 'dh', 'ਣ': 'n',
        'ਤ': 't', 'ਥ': 'th', 'ਦ': 'd', 'ਧ': 'dh', 'ਨ': 'n',
        'ਪ': 'p', 'ਫ': 'f', 'ਬ': 'b', 'ਭ': 'bh', 'ਮ': 'm',
        'ਯ': 'y', 'ਰ': 'r', 'ਲ': 'l', 'ਵ': 'v', 'ੜ': 'rh',
        # Persian
        'ਸ਼': 'sh', 'ਜ਼': 'z', 'ਗ਼': 'g', 'ਖ਼': 'kh', 'ਫ਼': 'f', 'ਲ਼': 'l',
    },
    vowel_diacritics={
        'ਾ': 'aa', 'ਿ': 'i', 'ੀ': 'ee',
        'ੁ': 'u', 'ੂ': 'oo', 'ੇ': 'ay', 'ੈ': 'ai',
        'ੋ': 'o', 'ੌ': 'ou',
    },
    vowels={
        'ਅ': 'a', 'ਆ': 'aa', 'ਇ': 'i', 'ਈ': 'ee',
        'ਉ': 'u', 'ਊ': 'oo', 'ਏ': 'ay', 'ਐ': 'ai',
        'ਓ': 'o', 'ਔ': 'ou',
    },
    nasal_tippi='n',
    nasal_bindi='n',
    subjoined={'੍ਰ': 'r', '੍ਵ': 'v', '੍ਹ': None, '੍ਤ': None, '੍ਯ': None},
    notes=(
        'Used by SikhNet / fateh.sikhnet.com. '
        'Retroflex consonants not distinguished from dentals. '
        'ਙ romanized as ny.'
    ),
)

STTM = SystemMap(
    id='sttm',
    label='SikhiToTheMax (BaniDB)',
    consonants={
        'ਸ': 's', 'ਹ': 'h',
        'ਕ': 'k', 'ਖ': 'kh', 'ਗ': 'g', 'ਘ': 'gh', 'ਙ': 'n(g)',
        'ਚ': 'ch', 'ਛ': 'chh', 'ਜ': 'j', 'ਝ': 'jh', 'ਞ': 'n(j)',
        # Capitals distinguish retroflex stops; ਡ/ਢ merge as dd
        'ਟ': 'T', 'ਠ': 'Th', 'ਡ': 'dd', 'ਢ': 'dd', 'ਣ': 'n',
        # ਦ/ਧ merge as dh
        'ਤ': 't', 'ਥ': 'th', 'ਦ': 'dh', 'ਧ': 'dh', 'ਨ': 'n',
        'ਪ': 'p', 'ਫ': 'f', 'ਬ': 'b', 'ਭ': 'bh', 'ਮ': 'm',
        'ਯ': 'y', 'ਰ': 'r', 'ਲ': 'l', 'ਵ': 'v', 'ੜ': 'R',
        # Persian
        'ਸ਼': 'sh', 'ਜ਼': 'z', 'ਗ਼': 'g(h)', 'ਖ਼': 'khh', 'ਫ਼': 'ph', 'ਲ਼': None,
    },
    vowel_diacritics={
        'ਾ': 'aa', 'ਿ': 'i', 'ੀ': 'ee',
        'ੁ': 'u', 'ੂ': 'oo', 'ੇ': 'e', 'ੈ': 'ai',
        'ੋ': 'o', 'ੌ': 'au',
    },
    vowels={
        'ਅ': 'a', 'ਆ': 'aa', 'ਇ': 'i', 'ਈ': 'ee',
        'ਉ': 'u', 'ਊ': 'uoo', 'ਏ': 'e', 'ਐ': 'ai',
        'ਓ': 'o', 'ਔ': 'aau',
    },
    nasal_tippi='(n)',
    nasal_bindi='(n)',
    subjoined={'੍ਰ': 'r', '੍ਵ': 'v', '੍ਹ': 'h', '੍ਤ': 't', '੍ਯ': 'y'},
    notes=(
        'Current BaniDB English scheme powering sikhitothemax.org '
        '(scraped api.banidb.com July 2026, ~1100 word-aligned verses). '
        'Capitals T/Th/R mark retroflex; ਦ/ਧ both dh, ਡ/ਢ both dd. '
        'Nasals parenthesised: ਸੈਭੰ → saibha(n). '
        'Addak rendered as apostrophe (ਸਿੱਖੀ → si\'khee) — engine '
        'approximates by doubling. ੍ਰ often metathesised: ਅੰਮ੍ਰਿਤ → a(n)mirat. '
        'ਲ਼ unattested in the corpus. For the pre-2019 scheme see sttm_legacy.'
    ),
)

STTM_LEGACY = SystemMap(
    id='sttm_legacy',
    label='SikhiToTheMax (legacy) / iGurbani',
    consonants={
        'ਸ': 's', 'ਹ': 'h',
        'ਕ': 'k', 'ਖ': 'kh', 'ਗ': 'g', 'ਘ': 'gh', 'ਙ': 'n(g)',
        'ਚ': 'ch', 'ਛ': 'shh', 'ਜ': 'j', 'ਝ': 'jh', 'ਞ': 'n',
        # tt/dd for retroflex; th/dh for dental aspirates
        'ਟ': 'tt', 'ਠ': 'th', 'ਡ': 'dd', 'ਢ': 'dt', 'ਣ': 'n',
        'ਤ': 'th', 'ਥ': 'thh', 'ਦ': 'dh', 'ਧ': 'dhh', 'ਨ': 'n',
        'ਪ': 'p', 'ਫ': 'f', 'ਬ': 'b', 'ਭ': 'bh', 'ਮ': 'm',
        'ਯ': 'y', 'ਰ': 'r', 'ਲ': 'l', 'ਵ': 'v', 'ੜ': 'rr',
        # Persian
        'ਸ਼': 'sh', 'ਜ਼': 'z', 'ਗ਼': 'gh', 'ਖ਼': 'khh', 'ਫ਼': None, 'ਲ਼': None,
    },
    vowel_diacritics={
        'ਾ': 'aa', 'ਿ': 'i', 'ੀ': 'ee',
        'ੁ': 'u', 'ੂ': 'oo', 'ੇ': 'ae', 'ੈ': 'ai',
        'ੋ': 'o', 'ੌ': 'a',
    },
    vowels={
        'ਅ': 'a', 'ਆ': 'aa', 'ਇ': 'ei', 'ਈ': 'ee',
        'ਉ': 'ou', 'ਊ': 'oo', 'ਏ': 'eae', 'ਐ': 'ai',
        'ਓ': 'ou', 'ਔ': 'a',
    },
    nasal_tippi='n',
    nasal_bindi='n',
    subjoined={'੍ਰ': 'r', '੍ਵ': None, '੍ਹ': None, '੍ਤ': None, '੍ਯ': None},
    notes=(
        'The pre-BaniDB SikhiToTheMax scheme, still served verbatim by '
        'igurbani.com (verified against its database July 2026: ਸਤਿਨਾਮੁ → '
        'sathnaam, ਏਕ → eaek, ਕੌਣੁ → kaan). Heavy use of doubled letters; '
        'n and ṇ are the same. ਛ → shh (unusual), ੌ → a (simplified). '
        'Independent vowels get glides: ਇ → ei, ਉ/ਓ → ou, ਏ → eae. '
        'Also used by Gurbani Anywhere.'
    ),
)

GFS = SystemMap(
    id='gfs',
    label='Guru Fatha Singh',
    consonants={
        'ਸ': 's', 'ਹ': 'h',
        'ਕ': 'k', 'ਖ': 'kh', 'ਗ': 'g', 'ਘ': 'gh', 'ਙ': 'gn',
        'ਚ': 'ch', 'ਛ': 'chh', 'ਜ': 'j', 'ਝ': 'jh', 'ਞ': 'ny',
        # No diacritic distinction between retroflex and dental
        'ਟ': 't', 'ਠ': 'th', 'ਡ': 'd', 'ਢ': 'dh', 'ਣ': 'n',
        'ਤ': 't', 'ਥ': 'th', 'ਦ': 'd', 'ਧ': 'dh', 'ਨ': 'n',
        'ਪ': 'p', 'ਫ': 'ph', 'ਬ': 'b', 'ਭ': 'bh', 'ਮ': 'm',
        'ਯ': 'y', 'ਰ': 'r', 'ਲ': 'l', 'ਵ': 'v', 'ੜ': 'r',
        # Persian
        'ਸ਼': 'sh', 'ਜ਼': 'z', 'ਗ਼': 'ghh', 'ਖ਼': 'khh', 'ਫ਼': 'f', 'ਲ਼': None,
    },
    vowel_diacritics={
        'ਾ': 'aa', 'ਿ': 'i', 'ੀ': 'ee',
        'ੁ': 'u', 'ੂ': 'oo', 'ੇ': 'ay', 'ੈ': 'ai',
        'ੋ': 'o', 'ੌ': 'au',
    },
    vowels={
        'ਅ': 'a', 'ਆ': 'aa', 'ਇ': 'i', 'ਈ': 'ee',
        'ਉ': 'u', 'ਊ': 'oo', 'ਏ': 'ay', 'ਐ': 'ai',
        'ਓ': 'o', 'ਔ': 'au',
    },
    nasal_tippi='n',
    nasal_bindi=None,
    subjoined={'੍ਰ': 'r', '੍ਵ': 'v', '੍ਹ': None, '੍ਤ': None, '੍ਯ': None},
    notes=(
        'Similar to Dr. Sant Singh but: NG→GN, adds NY for ਞ, '
        'uses PH for ਫ, replaces diacritic dots with underlines, '
        'no aspiration apostrophes.'
    ),
)

SACRED_NITNEM = SystemMap(
    id='sacred_nitnem',
    label='Sacred Nitnem',
    consonants={
        'ਸ': 's', 'ਹ': 'h',
        'ਕ': 'k', 'ਖ': 'kh', 'ਗ': 'g', 'ਘ': 'gh', 'ਙ': None,
        'ਚ': 'ch', 'ਛ': 'chh', 'ਜ': 'j', 'ਝ': 'jh', 'ਞ': None,
        'ਟ': 'ṭ', 'ਠ': 'ṭh', 'ਡ': 'ḍ', 'ਢ': 'ḍh', 'ਣ': 'ṇ',
        'ਤ': 't', 'ਥ': 'th', 'ਦ': 'd', 'ਧ': 'dh', 'ਨ': 'n',
        'ਪ': 'p', 'ਫ': 'ph', 'ਬ': 'b', 'ਭ': 'bh', 'ਮ': 'm',
        'ਯ': 'y', 'ਰ': 'r', 'ਲ': 'l', 'ਵ': 'v', 'ੜ': 'ṛ',
        # Persian
        'ਸ਼': 'sh', 'ਜ਼': 'z', 'ਗ਼': 'g', 'ਖ਼': 'kh', 'ਫ਼': 'f', 'ਲ਼': None,
    },
    vowel_diacritics={
        'ਾ': 'ā', 'ਿ': 'i', 'ੀ': 'ī',
        'ੁ': 'u', 'ੂ': 'ū', 'ੇ': 'e', 'ੈ': 'ai',
        'ੋ': 'o', 'ੌ': 'au',
    },
    vowels={
        'ਅ': 'a', 'ਆ': 'ā', 'ਇ': 'i', 'ਈ': 'ī',
        'ਉ': 'u', 'ਊ': 'ū', 'ਏ': 'e', 'ਐ': 'ai',
        'ਓ': 'o', 'ਔ': 'au',
    },
    nasal_tippi='ṅ',
    nasal_bindi='ṅ',
    subjoined={'੍ਰ': 'r', '੍ਵ': 'v', '੍ਹ': None, '੍ਤ': None, '੍ਯ': None},
    notes=(
        'Similar to Dr. Sant Singh, but: PH for ਫ, macron for long vowels '
        '(ā ī ū), ṅ for both tippi and bindi, no aspiration apostrophes.'
    ),
)

IAST = SystemMap(
    id='iast',
    label='IAST (International Alphabet of Sanskrit Transliteration)',
    consonants={
        'ਸ': 's', 'ਹ': 'h',
        'ਕ': 'k', 'ਖ': 'kh', 'ਗ': 'g', 'ਘ': 'gh', 'ਙ': 'ṅ',
        'ਚ': 'c', 'ਛ': 'ch', 'ਜ': 'j', 'ਝ': 'jh', 'ਞ': 'ñ',
        'ਟ': 'ṭ', 'ਠ': 'ṭh', 'ਡ': 'ḍ', 'ਢ': 'ḍh', 'ਣ': 'ṇ',
        'ਤ': 't', 'ਥ': 'th', 'ਦ': 'd', 'ਧ': 'dh', 'ਨ': 'n',
        'ਪ': 'p', 'ਫ': 'ph', 'ਬ': 'b', 'ਭ': 'bh', 'ਮ': 'm',
        'ਯ': 'y', 'ਰ': 'r', 'ਲ': 'l', 'ਵ': 'v', 'ੜ': None,
        # Persian letters not in Sanskrit → None
        'ਸ਼': 'ś', 'ਜ਼': None, 'ਗ਼': None, 'ਖ਼': None, 'ਫ਼': None, 'ਲ਼': None,
    },
    vowel_diacritics={
        'ਾ': 'ā', 'ਿ': 'i', 'ੀ': 'ī',
        'ੁ': 'u', 'ੂ': 'ū', 'ੇ': 'e', 'ੈ': 'ai',
        'ੋ': 'o', 'ੌ': 'au',
    },
    vowels={
        'ਅ': 'a', 'ਆ': 'ā', 'ਇ': 'i', 'ਈ': 'ī',
        'ਉ': 'u', 'ਊ': 'ū', 'ਏ': 'e', 'ਐ': 'ai',
        'ਓ': 'o', 'ਔ': 'au',
    },
    nasal_tippi='ṃ',
    nasal_bindi='ṁ',
    subjoined={'੍ਰ': 'r', '੍ਵ': 'v', '੍ਹ': None, '੍ਤ': None, '੍ਯ': None},
    notes=(
        'Sanskrit-based system. Consistent diacritics. '
        'ੜ and Persian letters not included. '
        'Very close to ISO 15919 but without the Punjabi-specific extensions.'
    ),
)

IPA = SystemMap(
    id='ipa',
    label='IPA (International Phonetic Alphabet)',
    consonants={
        'ਸ': 's', 'ਹ': 'ɦ',
        'ਕ': 'k', 'ਖ': 'kʰ', 'ਗ': 'ɡ', 'ਘ': 'k˥', 'ਙ': 'ŋ',
        'ਚ': 'tʃ', 'ਛ': 'tʃʰ', 'ਜ': 'dʒ', 'ਝ': 'tʃ˥', 'ਞ': 'ɲ',
        'ਟ': 'ʈ', 'ਠ': 'ʈʰ', 'ਡ': 'ɖ', 'ਢ': 'ʈ˥', 'ਣ': 'ɳ',
        'ਤ': 't', 'ਥ': 'tʰ', 'ਦ': 'd', 'ਧ': 't˥', 'ਨ': 'n',
        'ਪ': 'p', 'ਫ': 'pʰ', 'ਬ': 'b', 'ਭ': 'p˥', 'ਮ': 'm',
        'ਯ': 'j', 'ਰ': 'r', 'ਲ': 'l', 'ਵ': 'ʋ', 'ੜ': 'ɽ',
        # Persian
        'ਸ਼': 'ʃ', 'ਜ਼': 'z', 'ਗ਼': 'ɣ', 'ਖ਼': 'x', 'ਫ਼': 'f', 'ਲ਼': 'ɭ',
    },
    vowel_diacritics={
        'ਾ': 'aː', 'ਿ': 'ɪ', 'ੀ': 'iː',
        'ੁ': 'ʊ', 'ੂ': 'uː', 'ੇ': 'eː', 'ੈ': 'ɛː',
        'ੋ': 'oː', 'ੌ': 'ɔː',
    },
    vowels={
        'ਅ': 'ə', 'ਆ': 'aː', 'ਇ': 'ɪ', 'ਈ': 'iː',
        'ਉ': 'ʊ', 'ਊ': 'uː', 'ਏ': 'eː', 'ਐ': 'ɛː',
        'ਓ': 'oː', 'ਔ': 'ɔː',
    },
    nasal_tippi='ŋ',
    nasal_bindi='̃',   # combining tilde (nasalisation of preceding vowel)
    subjoined={'੍ਰ': 'r', '੍ਵ': 'ʋ', '੍ਹ': 'h', '੍ਤ': None, '੍ਯ': None},
    notes=(
        'Scientific IPA transcription. Inherent vowel is ə (schwa). '
        'Voiced h → ɦ. Tone/murmur marks (˥) used for breathy consonants. '
        'Long vowels use ː.'
    ),
)

BANIDB_IPA = SystemMap(
    id='banidb_ipa',
    label='IPA (BaniDB/SikhiToTheMax)',
    consonants={
        'ਸ': 's', 'ਹ': 'h',
        'ਕ': 'k', 'ਖ': 'kʰ', 'ਗ': 'G', 'ਘ': 'Gʰ', 'ਙ': 'ŋ',
        'ਚ': 'tʃ', 'ਛ': 'ɕ', 'ਜ': 'dʒ', 'ਝ': 'ɖʐ', 'ਞ': 'ŋ',
        'ਟ': 'ʈ', 'ਠ': 'ʈʰ', 'ਡ': 'ɖ', 'ਢ': 'ʈ', 'ਣ': 'ɳ',
        # BaniDB writes dentals with combining bridge (t̪ d̪); stored plain
        # because U+032A renders as boxes in Noto Serif (see coverage tests)
        'ਤ': 't', 'ਥ': 'tʰ', 'ਦ': 'd', 'ਧ': 't', 'ਨ': 'n',
        'ਪ': 'p', 'ਫ': 'f', 'ਬ': 'b', 'ਭ': 'ɓ', 'ਮ': 'm',
        'ਯ': 'j', 'ਰ': 'r', 'ਲ': 'l', 'ਵ': 'ʋ', 'ੜ': 'ɽ',
        # Persian letters unattested in the sampled corpus
        'ਸ਼': None, 'ਜ਼': None, 'ਗ਼': None, 'ਖ਼': None, 'ਫ਼': None, 'ਲ਼': None,
    },
    vowel_diacritics={
        'ਾ': 'ɑ', 'ਿ': 'ɪ', 'ੀ': 'i',
        'ੁ': 'ʊ', 'ੂ': 'u', 'ੇ': 'e', 'ੈ': 'æ',
        'ੋ': 'ɔ', 'ੌ': 'ɒ',
    },
    vowels={
        'ਅ': 'ə', 'ਆ': 'əɑ', 'ਇ': 'eɪ', 'ਈ': 'ei',
        'ਉ': 'oʊ', 'ਊ': 'ou', 'ਏ': 'ee', 'ਐ': 'æ',
        'ਓ': 'oə', 'ਔ': None,
    },
    nasal_tippi='ŋ',
    nasal_bindi='ⁿ',
    subjoined={'੍ਰ': 'ɹ', '੍ਵ': 'ʋ', '੍ਹ': 'ʰ', '੍ਤ': None, '੍ਯ': None},
    notes=(
        'BaniDB\'s IPA transliteration as served on sikhitothemax.org '
        '(scraped July 2026). Differs from the academic ipa map: voiced '
        'aspirates lose voicing/aspiration and take a low-tone grave on the '
        'following vowel (ਭ → ɓ, ਧ → t̪ + ə̀, ਢ → ʈ + ə̀ — tone mark not '
        'reproduced here); no vowel length marks (ਾ → ɑ not aː); ਹ → h not ɦ; '
        'ਗ oddly capital G (attested consistently: ਗੁਰ → Gʊr). Affricates '
        'written with tie bars (t͡ʃ d͡ʒ) and dentals with bridge (t̪ d̪) in '
        'the source — stored without them for font-safe rendering. '
        'Diphthong-style independent vowels: ਇ → eɪ, ਉ → oʊ, ਓ → oə.'
    ),
)

GURSEVAK = SystemMap(
    id='gursevak',
    label='Gursevak / Learn Shudh Gurbani',
    consonants={
        'ਸ': 's', 'ਹ': 'h',
        'ਕ': 'k', 'ਖ': 'kh', 'ਗ': 'g', 'ਘ': 'gh', 'ਙ': 'ng',
        'ਚ': 'ch', 'ਛ': 'chh', 'ਜ': 'j', 'ਝ': 'jh', 'ਞ': 'nj',
        'ਟ': 'tt', 'ਠ': 'tth', 'ਡ': 'dd', 'ਢ': 'ddh', 'ਣ': 'nn',
        'ਤ': 't', 'ਥ': 'th', 'ਦ': 'd', 'ਧ': 'dh', 'ਨ': 'n',
        'ਪ': 'p', 'ਫ': 'ph', 'ਬ': 'b', 'ਭ': 'bh', 'ਮ': 'm',
        'ਯ': 'Y', 'ਰ': 'r', 'ਲ': 'l', 'ਵ': 'v', 'ੜ': 'rr',
        # Persian
        'ਸ਼': 'sh', 'ਜ਼': 'z', 'ਗ਼': 'gh', 'ਖ਼': 'khh', 'ਫ਼': 'ph', 'ਲ਼': None,
    },
    vowel_diacritics={
        'ਾ': 'aa', 'ਿ': 'e', 'ੀ': 'ee',
        'ੁ': 'u', 'ੂ': 'oo', 'ੇ': 'ay', 'ੈ': 'ai',
        'ੋ': 'o', 'ੌ': 'au',
    },
    vowels={
        # Independent ਅ is capital A in the source (ਅੰਦਰਿ → Aⁿdare); stored
        # lowercase because the engine reuses this value as the inherent vowel
        'ਅ': 'a', 'ਆ': 'aa', 'ਇ': 'e', 'ਈ': 'ee',
        'ਉ': 'u', 'ਊ': 'oo', 'ਏ': 'ay', 'ਐ': 'ai',
        'ਓ': 'o', 'ਔ': 'au',
    },
    nasal_tippi='ⁿ',
    nasal_bindi='ⁿ',
    subjoined={'੍ਰ': 'ᵣ', '੍ਵ': 'ᵤ', '੍ਹ': 'ₕ', '੍ਤ': 'ₜ', '੍ਯ': 'ₑ'},
    notes=(
        'Learn Shudh Gurbani app scheme, extracted from the bundled '
        'Gursevak.sqlite of app v3.01 (June 2026): ~143k verses across SGGS, '
        'Dasam Granth, Sarbloh, Bhai Gurdas, Bhai Nandlal, Rehatnamey, '
        'word-aligned. Pronunciation-first: sihari → e and laavaan → ay '
        '(ਜੇ → jay, ਏਕੁ → ayku), superscript ⁿ nasals, subjoined letters as '
        'Unicode subscripts (ਅੰਮ੍ਰਿਤ → Aⁿmᵣet, ਸ੍ਵਾਦ → sᵤaad, ਪੜ੍ਹਹਿ → '
        'parrₕahe), ਯ → capital Y (ਯਯਾ → YaYaa), addak capitalises the next '
        'consonant (ਚੱਕ੍ਰ → chaKᵣa) — engine doubles instead. The source '
        'wraps vowels in ‹› for the app\'s colour-coding (stripped here) and '
        'hyphenates adjacent vowels (ਚਲਾਏ → chalaa-ay). Silent final sihari '
        'is dropped in-data (ਮੂਰਤਿ → moorat). ਲ਼ absent from corpus.'
    ),
)

# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

SYSTEMS: dict[str, SystemMap] = {
    s.id: s for s in [
        DR_SANT_SINGH,
        DR_THIND,
        STTM,
        STTM_LEGACY,
        GURSEVAK,
        GFS,
        SACRED_NITNEM,
        IAST,
        IPA,
        BANIDB_IPA,
    ]
}

SYSTEM_ORDER = [
    'dr_sant_singh', 'dr_thind', 'sttm', 'sttm_legacy', 'gursevak',
    'gfs', 'sacred_nitnem', 'iast', 'ipa', 'banidb_ipa',
]
