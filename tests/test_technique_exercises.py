import unittest
from core.technique_exercises import TECHNIQUE_EXERCISES, get_exercises_by_instrument

class TestTechniqueExercises(unittest.TestCase):
    def test_exercise_count(self):
        self.assertGreaterEqual(len(TECHNIQUE_EXERCISES), 9, "Should have at least 9 technique exercises")

    def test_exercise_fields_validity(self):
        for ex in TECHNIQUE_EXERCISES:
            self.assertTrue(ex.id)
            self.assertTrue(ex.name_pt)
            self.assertTrue(ex.name_en)
            self.assertIn(ex.category, ["aquecimento", "destreza", "forca_agilidade"])
            self.assertIn(ex.instrument, ["piano", "guitar", "ambos"])
            self.assertGreater(len(ex.notes), 0, f"Exercise {ex.id} should have notes")
            self.assertEqual(len(ex.recommended_bpm_range), 2)
            self.assertLess(ex.recommended_bpm_range[0], ex.recommended_bpm_range[1])

    def test_get_exercises_by_instrument(self):
        piano_exs = get_exercises_by_instrument("piano")
        self.assertTrue(all(e.instrument in ["piano", "ambos"] for e in piano_exs))

        guitar_exs = get_exercises_by_instrument("guitar")
        self.assertTrue(all(e.instrument in ["guitar", "ambos"] for e in guitar_exs))

    def test_i18n_getters(self):
        ex = TECHNIQUE_EXERCISES[0]
        self.assertEqual(ex.get_name("pt"), ex.name_pt)
        self.assertEqual(ex.get_name("en"), ex.name_en)
        self.assertEqual(ex.get_description("pt"), ex.description_pt)
        self.assertEqual(ex.get_description("en"), ex.description_en)
