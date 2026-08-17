"""Comprehensive unit tests for the Musical Glossary module and search engine."""
import unittest
from core.glossary import (
    GLOSSARY_DATABASE,
    GLOSSARY_BY_ID,
    GlossaryTerm,
    get_all_terms,
    get_term_by_id,
    search_terms,
)
from core.notes import Note
from gui.markdown_renderer import get_glossary_keywords_map


class TestGlossary(unittest.TestCase):
    def test_glossary_database_size(self):
        """Verifies that the glossary contains at least 120 terms covering all core topics."""
        self.assertGreaterEqual(len(GLOSSARY_DATABASE), 120)
        self.assertEqual(len(GLOSSARY_DATABASE), len(GLOSSARY_BY_ID))

    def test_unique_term_ids(self):
        ids = [t.id for t in GLOSSARY_DATABASE]
        self.assertEqual(len(ids), len(set(ids)), "Found duplicate glossary term IDs")

    def test_all_terms_have_valid_fields(self):
        valid_categories = {
            "harmonia", "ritmo", "notacao", "modos", "tecnica", "acustica", "forma", "jazz"
        }
        for t in GLOSSARY_DATABASE:
            self.assertTrue(t.id, "Term missing id")
            self.assertTrue(t.term_pt.strip(), f"Term {t.id} missing term_pt")
            self.assertTrue(t.term_en.strip(), f"Term {t.id} missing term_en")
            self.assertIn(t.category.lower(), valid_categories, f"Term {t.id} has invalid category '{t.category}'")
            self.assertTrue(t.short_def_pt.strip(), f"Term {t.id} missing short_def_pt")
            self.assertTrue(t.short_def_en.strip(), f"Term {t.id} missing short_def_en")
            self.assertTrue(t.long_def_pt.strip(), f"Term {t.id} missing long_def_pt")
            self.assertTrue(t.long_def_en.strip(), f"Term {t.id} missing long_def_en")

    def test_hear_it_notes_valid(self):
        """All pitches defined in hear_it must be valid parseable Note strings."""
        for t in GLOSSARY_DATABASE:
            for pitch_str in t.hear_it:
                try:
                    n = Note(pitch_str)
                    self.assertGreater(n.midi, 0)
                except Exception as e:
                    self.fail(f"Term '{t.id}' has invalid pitch string '{pitch_str}' in hear_it: {e}")

    def test_see_also_references_exist(self):
        """Cross-references in see_also must refer to existing glossary term IDs."""
        for t in GLOSSARY_DATABASE:
            for ref_id in t.see_also:
                self.assertIn(
                    ref_id,
                    GLOSSARY_BY_ID,
                    f"Term '{t.id}' references non-existent see_also term ID '{ref_id}'"
                )

    def test_get_term_by_id(self):
        term = get_term_by_id("tritono")
        self.assertIsNotNone(term)
        self.assertIn("Trítono", term.term_pt)
        self.assertEqual(term.category, "harmonia")

        none_term = get_term_by_id("non_existent_term_id_xyz")
        self.assertIsNone(none_term)

    def test_getters_respect_language(self):
        term = get_term_by_id("tritono")
        self.assertIsNotNone(term)
        self.assertIn("Trítono", term.get_term("pt"))
        self.assertIn("Tritone", term.get_term("en"))
        self.assertIn("3 tons", term.get_short_def("pt"))
        self.assertIn("three whole tones", term.get_short_def("en"))

    def test_search_by_query(self):
        # Search Portuguese keyword
        results_pt = search_terms("síncopa", lang="pt")
        self.assertTrue(any(t.id == "sincope" for t in results_pt))

        # Search English keyword
        results_en = search_terms("syncopation", lang="en")
        self.assertTrue(any(t.id == "sincope" for t in results_en))

        # Search by formula
        results_form = search_terms("V → I", lang="pt")
        self.assertTrue(any(t.id == "cadencia" for t in results_form))

    def test_search_by_category(self):
        jazz_terms = search_terms(category="jazz")
        self.assertGreater(len(jazz_terms), 0)
        for t in jazz_terms:
            self.assertEqual(t.category, "jazz")

    def test_search_by_chapter(self):
        chap1_terms = search_terms(chapter="chap1_fundamentals")
        self.assertGreater(len(chap1_terms), 0)
        for t in chap1_terms:
            self.assertIn("chap1_fundamentals", t.chapters)

    def test_keywords_map_generation(self):
        kw_map = get_glossary_keywords_map()
        self.assertGreater(len(kw_map), 50)
        self.assertIn("trítono", kw_map)
        self.assertEqual(kw_map["trítono"], "tritono")

    def test_accent_insensitive_search(self):
        """Verifies that searching with or without accents returns the exact same number of results."""
        pairs = [
            ("tónica", "tonica"),
            ("trítono", "tritono"),
            ("cadência", "cadencia"),
            ("harmónico", "harmonico"),
            ("sensível", "sensivel"),
            ("Dó", "do"),
            ("inversão", "inversao"),
        ]
        for with_acc, without_acc in pairs:
            r_acc = search_terms(with_acc, lang="pt")
            r_noacc = search_terms(without_acc, lang="pt")
            self.assertGreater(len(r_acc), 0, f"Query '{with_acc}' returned 0 results")
            self.assertEqual(
                len(r_acc),
                len(r_noacc),
                f"Accent mismatch: '{with_acc}' ({len(r_acc)}) vs '{without_acc}' ({len(r_noacc)})"
            )

    def test_all_hear_it_notes_playable_and_constructible(self):
        """Verifies that all hear_it pitch strings across all terms construct valid Note instances and work in play_note."""
        from audio.player import get_audio_player
        player = get_audio_player()
        for t in GLOSSARY_DATABASE:
            for pitch_str in t.hear_it:
                note = Note(pitch_str)
                self.assertIsNotNone(note.frequency)
                # Verify that play_note accepts Note and string without raising exception
                try:
                    # Test with Note object and str parameter
                    player.play_note(note, duration=0.1, volume=0.0)
                    player.play_note(pitch_str, duration=0.1, volume=0.0)
                except Exception as e:
                    self.fail(f"AudioPlayer.play_note failed for term {t.id} note {pitch_str}: {e}")


if __name__ == "__main__":
    unittest.main()
