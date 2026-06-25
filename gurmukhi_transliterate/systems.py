"""
Romanization system definitions for Gurmukhi.

Data sourced from comparative spreadsheet covering:
  Dr. Sant Singh Khalsa, Dr. Kulbir S. Thind (SikhNet), SikhiToTheMax,
  Guru Fatha Singh, Sacred Nitnem, IAST, IPA.

Normalisation applied to the raw sheet data:
  - All values lowercased
  - "N/A" → None  (character not supported by that system)
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
    label='SikhiToTheMax',
    consonants={
        'ਸ': 's', 'ਹ': 'h',
        'ਕ': 'k', 'ਖ': 'kh', 'ਗ': 'g', 'ਘ': 'gh', 'ਙ': 'ng',
        'ਚ': 'ch', 'ਛ': 'shh', 'ਜ': 'j', 'ਝ': 'jh', 'ਞ': 'n',
        # STTM uses tt/dd for retroflex; th/dh for dental aspirates
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
        'ਅ': 'a', 'ਆ': 'aa', 'ਇ': 'i', 'ਈ': 'ee',
        'ਉ': 'u', 'ਊ': 'oo', 'ਏ': 'ae', 'ਐ': 'ai',
        'ਓ': 'o', 'ਔ': 'a',
    },
    nasal_tippi='n',
    nasal_bindi='n',
    subjoined={'੍ਰ': 'r', '੍ਵ': None, '੍ਹ': None, '੍ਤ': None, '੍ਯ': None},
    notes=(
        'Used by iGurbani and Gurbani Anywhere. '
        'Heavy use of doubled letters; n and ṇ are the same. '
        'ਛ → shh (unusual), ੌ → a (simplified).'
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
        'ਤ': 't̪', 'ਥ': 't̪ʰ', 'ਦ': 'd̪', 'ਧ': 't̪˥', 'ਨ': 'n',
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

# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

SYSTEMS: dict[str, SystemMap] = {
    s.id: s for s in [
        DR_SANT_SINGH,
        DR_THIND,
        STTM,
        GFS,
        SACRED_NITNEM,
        IAST,
        IPA,
    ]
}

SYSTEM_ORDER = [
    'dr_sant_singh', 'dr_thind', 'sttm', 'gfs',
    'sacred_nitnem', 'iast', 'ipa',
]
