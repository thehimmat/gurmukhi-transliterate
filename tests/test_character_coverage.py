"""Character coverage tests.

Every character that any system can output must fall within Unicode ranges
reliably covered by Noto Serif (the display font). If a character lands
outside the safe ranges the test fails with the offending system, input
glyph, and codepoint — so the fix is obvious.

Safe ranges (Noto Serif confirmed coverage):
  U+0021–U+007E  Basic Latin (printable ASCII)
  U+00C0–U+024F  Latin Extended-A/B  (ā ī ū ṭ ḍ ś ġ etc.)
  U+0250–U+02AF  IPA Extensions      (ə ɪ ʊ ɦ ʋ ɽ ɳ ɲ ŋ etc.)
  U+02B0–U+02FF  Spacing Modifiers   (ʰ ː ˥ etc.)
  U+0300–U+030F  Common combining    (̃ grave acute circumflex tilde macron)
  U+1D00–U+1D7F  Phonetic Extensions
  U+1E00–U+1EFF  Latin Extended Additional (ṃ ṁ ṅ ś ġ etc.)

Explicitly excluded (renders as boxes in Noto Serif):
  U+0310–U+036F  Uncommon combining marks (e.g. U+032A combining bridge below)
"""

import pytest
from gurmukhi_transliterate import SYSTEMS

# ---------------------------------------------------------------------------
# Safe ranges
# ---------------------------------------------------------------------------

SAFE_RANGES = [
    (0x0021, 0x007E),   # Basic Latin printable
    (0x00C0, 0x024F),   # Latin Extended A/B
    (0x0250, 0x02FF),   # IPA Extensions + Spacing Modifiers
    (0x0300, 0x030F),   # Common combining diacritics (tilde, macron, etc.)
    (0x1D00, 0x1D7F),   # Phonetic Extensions
    (0x1E00, 0x1EFF),   # Latin Extended Additional
]


def is_safe(ch: str) -> bool:
    cp = ord(ch)
    return any(lo <= cp <= hi for lo, hi in SAFE_RANGES)


def collect_all_mappings():
    """Yield (system_id, gurmukhi_key, roman_value) for every non-None map entry."""
    for sys_id, system in SYSTEMS.items():
        for gurmukhi, roman in {
            **system.consonants,
            **system.vowel_diacritics,
            **system.vowels,
        }.items():
            if roman is not None:
                yield sys_id, gurmukhi, roman
        for label, roman in [
            ('nasal_tippi', system.nasal_tippi),
            ('nasal_bindi', system.nasal_bindi),
        ]:
            if roman is not None:
                yield sys_id, label, roman
        for gurmukhi, roman in system.subjoined.items():
            if roman is not None:
                yield sys_id, gurmukhi, roman


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestCharacterCoverage:
    def test_all_mapped_chars_in_safe_range(self):
        """Every character in every system map must be in the Noto Serif safe range."""
        failures = []
        for sys_id, key, roman in collect_all_mappings():
            for ch in roman:
                if not is_safe(ch):
                    failures.append(
                        f"  {sys_id}[{key!r}] = {roman!r} — "
                        f"char {ch!r} U+{ord(ch):04X} outside safe range"
                    )
        if failures:
            pytest.fail(
                f"{len(failures)} unsafe character(s) found:\n" + "\n".join(failures)
            )

    def test_no_solo_combining_mark_values(self):
        """No map value should be ONLY an *unsafe* combining character.

        Safe combining marks (U+0300-U+030F: tilde, macron, etc.) are allowed
        as solo values — the engine always appends them to the preceding vowel,
        so they combine correctly (e.g. IPA nasal_bindi = U+0303 combining tilde).
        Unsafe combining marks outside that range would also render as boxes.
        """
        UNSAFE_COMBINING_START = 0x0310
        UNSAFE_COMBINING_END   = 0x036F
        failures = []
        for sys_id, key, roman in collect_all_mappings():
            if len(roman) == 1:
                cp = ord(roman)
                if UNSAFE_COMBINING_START <= cp <= UNSAFE_COMBINING_END:
                    failures.append(
                        f"  {sys_id}[{key!r}] = {roman!r} U+{cp:04X} "
                        f"is a bare unsafe combining character"
                    )
        if failures:
            pytest.fail(
                "Bare unsafe combining characters found:\n"
                + "\n".join(failures)
            )

    def test_unique_output_chars_inventory(self):
        """Snapshot of every unique output character across all systems.
        Fails if a new character is added outside the safe range, acting as
        a canary for future unsafe additions."""
        all_chars = set()
        for _, _, roman in collect_all_mappings():
            all_chars.update(roman)
        unsafe = {ch for ch in all_chars if not is_safe(ch)}
        assert unsafe == set(), (
            f"Unsafe characters in system maps: "
            + ", ".join(f"{ch!r} U+{ord(ch):04X}" for ch in sorted(unsafe, key=ord))
        )
