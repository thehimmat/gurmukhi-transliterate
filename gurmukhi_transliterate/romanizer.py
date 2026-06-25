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
from .systems import SYSTEMS, SystemMap
from ._core import transliterate


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
        """
        return transliterate(text, self._system, delete_schwa=delete_schwa)
