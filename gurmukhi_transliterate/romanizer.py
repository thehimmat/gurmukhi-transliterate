"""
GurmukhiRomanizer — a data-driven romanizer for the "Other" systems.

Usage:
    from gurmukhi_transliterate.romanizer import GurmukhiRomanizer

    r = GurmukhiRomanizer('dr_thind')
    print(r.romanize('ਸਤਿ ਨਾਮੁ'))   # → 'sati naamu'

    # Or pass a SystemMap directly
    from gurmukhi_transliterate.systems import DR_THIND
    r = GurmukhiRomanizer(DR_THIND)
"""

from __future__ import annotations
import logging
from .systems import SYSTEMS, SystemMap
from ._core import transliterate
from .banidb import GurmukhiBaniDB
from .shabados import GurmukhiShabadOS
from .legacy import ConversionResult

# Systems whose real-world output comes from a dedicated engine rather than the
# generic map-driven one. These apply their own vowel dropping, so
# delete_schwa has no effect on them.
_DEDICATED = {
    'sttm': GurmukhiBaniDB.to_english,
    'banidb_ipa': GurmukhiBaniDB.to_ipa,
    'shabados': GurmukhiShabadOS.to_english,
}

_logger = logging.getLogger('gurmukhi_transliterate._core')


class GurmukhiRomanizer:
    """Romanize Gurmukhi text using any registered system."""

    def __init__(self, system: str | SystemMap) -> None:
        if isinstance(system, str):
            if system not in SYSTEMS:
                raise ValueError(
                    f"Unknown system '{system}'. "
                    f"Available: {list(SYSTEMS.keys())}"
                )
            self._system = SYSTEMS[system]
        else:
            self._system = system

    @property
    def system(self) -> SystemMap:
        return self._system

    def romanize(self, text: str, delete_schwa: bool = False) -> str:
        """Convert Gurmukhi *text* to romanized form.

        Args:
            text:         Gurmukhi Unicode string.
            delete_schwa: Apply schwa deletion (word-final + pre-vocalic).

        Letters the system doesn't define fall back (see ``romanize_report``)
        and each fallback is logged as a warning.
        """
        result = self.romanize_report(text, delete_schwa=delete_schwa)
        for w in result.warnings:
            _logger.warning('%s at position %d (%r): %s', w.kind, w.position, w.char, w.message)
        return result.text

    def romanize_report(self, text: str, delete_schwa: bool = False) -> ConversionResult:
        """Romanize *text* and return the fallbacks used as warnings.

        Warning kinds: ``fallback_base`` (nukta letter → its base letter),
        ``fallback_iso`` (letter → its ISO 15919 value), ``fallback_nasal``
        (bindi → the system's tippi value). Positions index the NFC-normalised
        input.
        """
        engine = _DEDICATED.get(self._system.id)
        if engine is not None:
            return ConversionResult(engine(text), [])
        warnings: list = []
        out = transliterate(text, self._system, delete_schwa=delete_schwa, warnings=warnings)
        return ConversionResult(out, warnings)
