"""
Cross-system comparison and system identification for Gurmukhi romanization.

comparison_table(text) → {system_id: romanized_text}
identify_system(romanized) → [{system, label, confidence, equivalent}, ...]
"""

from __future__ import annotations
import math
from collections import defaultdict
from .systems import SYSTEMS, SYSTEM_ORDER
from .romanizer import GurmukhiRomanizer
from .iso15919 import GurmukhiISO15919
from .practical import GurmukhiPractical


# ---------------------------------------------------------------------------
# Comparison
# ---------------------------------------------------------------------------

def comparison_table(
    text: str,
    systems: list[str] | None = None,
    delete_schwa: bool = False,
) -> dict[str, str]:
    """Romanize *text* with every known system.

    Args:
        text:         Gurmukhi Unicode input.
        systems:      Optional list of system IDs to include. Defaults to all.
        delete_schwa: Pass through to each romanizer.

    Returns:
        Ordered dict {system_id: romanized_string} including 'iso15919' and
        'practical' as the first two entries.
    """
    order = ['iso15919', 'practical'] + SYSTEM_ORDER
    if systems is not None:
        order = [s for s in order if s in systems]

    result: dict[str, str] = {}
    for sid in order:
        if sid == 'iso15919':
            result[sid] = GurmukhiISO15919.to_phonetic(
                text, delete_schwa=delete_schwa
            )
        elif sid == 'practical':
            result[sid] = GurmukhiPractical.to_practical(
                text, delete_schwa=delete_schwa
            )
        elif sid in SYSTEMS:
            result[sid] = GurmukhiRomanizer(sid).romanize(
                text, delete_schwa=delete_schwa
            )
    return result


# ---------------------------------------------------------------------------
# System identification
# ---------------------------------------------------------------------------

# Each system has a character-trigram model trained on its own romanization of
# the Gurbani lexicon, and English has one trained on SCOWL (language.py). A
# text's score under a model is the sum of its words' log-likelihoods.

# systems whose per-word log-likelihood is this close to the best are flagged
# `equivalent`: the text can't tell them apart (e.g. IAST and ISO 15919 write
# most words identically)
_EQUIVALENT_NATS = 0.25

_LABELS_EXTRA = {
    'iso15919': 'ISO 15919',
    'practical': 'Practical',
    'informal': 'Informal / common spellings',
    'english': 'English (not Gurmukhi)',
}


def identify_system(
    romanized: str,
    top_n: int = 5,
    include_english: bool = False,
) -> list[dict]:
    """Rank the romanization systems that could have written *romanized*.

    Each word is scored under every system's character-trigram model and the
    English model. A system's confidence compares its mean per-word
    log-likelihood with the best system's and with English's, so English
    prose gets low confidence everywhere and a system scores near 1 only
    when it explains the text about as well as the best one does.

    Systems the text can't tell apart from the best one are marked
    ``equivalent``. When every word is a known informal spelling (Waheguru,
    Sat Sri Akal, …), ``'informal'`` is ranked first. With
    ``include_english=True``, ``'english'`` is ranked alongside the systems.

    Returns:
        List of dicts ``{system, label, confidence, equivalent}``, sorted by
        confidence descending.
    """
    from .informal import reverse_informal
    from .language import latin_words, word_scores

    words = latin_words(romanized)
    if not words:
        return []
    totals: dict[str, float] = defaultdict(float)
    for w in words:
        for name, lp in word_scores(w).items():
            totals[name] += lp
    mean = {name: t / len(words) for name, t in totals.items()}
    english = mean.pop('english')
    best = max(mean.values())

    def confidence(m: float) -> float:
        # m relative to the best explanation (best system or English)
        top = max(best, english)
        return math.exp(m - top) / (math.exp(best - top) + math.exp(english - top))

    labels = {**{s.id: s.label for s in SYSTEMS.values()}, **_LABELS_EXTRA}
    ranked = [
        {'system': sid, 'label': labels.get(sid, sid), 'confidence': confidence(m),
         'equivalent': m >= best - _EQUIVALENT_NATS}
        for sid, m in mean.items()
    ]
    if include_english:
        ranked.append({'system': 'english', 'label': labels['english'],
                       'confidence': confidence(english), 'equivalent': False})
    ranked.sort(key=lambda d: d['confidence'], reverse=True)
    if romanized.isascii() and reverse_informal(romanized)[0] is not None:
        ranked.insert(0, {'system': 'informal', 'label': labels['informal'],
                          'confidence': 1.0, 'equivalent': False})
    for d in ranked:
        d['confidence'] = round(d['confidence'], 3)
    return ranked[:top_n]
