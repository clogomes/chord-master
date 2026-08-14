"""Unit tests for Internationalization (i18n) module and localization helpers."""
import unittest
from gui.i18n import UI_STRINGS, get_language, set_language, t, toggle_language
from core.i18n_helpers import (
    localized_note_name,
    localized_chord_name,
    localized_scale_name,
    localized_interval_name,
)
from core.notes import Note
from core.chords import CHORD_TYPES
from core.scales import SCALE_TYPES
from core.intervals import INTERVALS


class TestI18n(unittest.TestCase):
    """Validates language dictionary symmetry, state toggling, and music theory localization helpers."""

    def setUp(self):
        self._initial_lang = get_language()

    def tearDown(self):
        set_language(self._initial_lang)

    def test_ui_strings_dictionary_symmetry(self):
        """Validates that PT and EN translation dictionaries have exact same set of keys without missing translations."""
        pt_keys = set(UI_STRINGS["pt"].keys())
        en_keys = set(UI_STRINGS["en"].keys())

        missing_in_en = pt_keys - en_keys
        missing_in_pt = en_keys - pt_keys

        self.assertEqual(missing_in_en, set(), f"Keys in PT missing in EN: {missing_in_en}")
        self.assertEqual(missing_in_pt, set(), f"Keys in EN missing in PT: {missing_in_pt}")
        self.assertGreater(len(pt_keys), 20)

    def test_language_getter_setter_toggle(self):
        """Validates get_language, set_language, and toggle_language behavior."""
        set_language("pt")
        self.assertEqual(get_language(), "pt")
        self.assertEqual(t("btn_play"), "▶ Ouvir")

        set_language("en")
        self.assertEqual(get_language(), "en")
        self.assertEqual(t("btn_play"), "▶ Play")

        toggled = toggle_language()
        self.assertEqual(toggled, "pt")
        self.assertEqual(get_language(), "pt")

    def test_localized_note_name(self):
        """Validates solfege name in PT and scientific note pitch in EN."""
        c4 = Note("C4")
        f_sharp = Note("F#3")

        set_language("pt")
        self.assertEqual(localized_note_name(c4), "Dó")
        self.assertEqual(localized_note_name(f_sharp), "Fá#")

        set_language("en")
        self.assertEqual(localized_note_name(c4), "C")
        self.assertEqual(localized_note_name(f_sharp), "F#")

    def test_localized_chord_name(self):
        """Validates chord definition localization."""
        major_chord = CHORD_TYPES["major"]
        minor_chord = CHORD_TYPES["minor"]

        set_language("pt")
        self.assertEqual(localized_chord_name(major_chord), "Tríade Maior")
        self.assertEqual(localized_chord_name(minor_chord), "Tríade Menor")

        set_language("en")
        self.assertEqual(localized_chord_name(major_chord), "Major Triad")
        self.assertEqual(localized_chord_name(minor_chord), "Minor Triad")

    def test_localized_scale_name(self):
        """Validates scale definition localization."""
        major_scale = SCALE_TYPES["major"]

        set_language("pt")
        self.assertEqual(localized_scale_name(major_scale), "Escala Maior (Jónio)")

        set_language("en")
        self.assertEqual(localized_scale_name(major_scale), "Major Scale")

    def test_localized_interval_name(self):
        """Validates interval definition localization."""
        major_third = INTERVALS[4]

        set_language("pt")
        self.assertEqual(localized_interval_name(major_third), "Terça Maior")

        set_language("en")
        self.assertEqual(localized_interval_name(major_third), "Major 3rd")


if __name__ == "__main__":
    unittest.main()
