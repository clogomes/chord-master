import unittest
from core.notes import Note
from core.staff_tutor import get_note_explanation, generate_tutor_pool

class TestStaffPedagogy(unittest.TestCase):
    def test_note_explanation_treble(self):
        note_e4 = Note("E4")
        explanation = get_note_explanation(note_e4, "treble")
        self.assertIn("1ª linha", explanation)

        note_f4 = Note("F4")
        explanation_f = get_note_explanation(note_f4, "treble")
        self.assertIn("1º espaço", explanation_f)

        note_g4 = Note("G4")
        explanation_g = get_note_explanation(note_g4, "treble")
        self.assertIn("Clave de Sol fixa a nota", explanation_g)

    def test_note_explanation_bass(self):
        note_f3 = Note("F3")
        explanation_f = get_note_explanation(note_f3, "bass")
        self.assertIn("Clave de Fá fixa a nota", explanation_f)

        note_b2 = Note("B2")
        explanation_b = get_note_explanation(note_b2, "bass")
        self.assertIn("2ª linha", explanation_b)

    def test_level_filters(self):
        level_1_treble = generate_tutor_pool(1, "treble", False)
        # E4, G4, B4, D5, F5 -> 5 notes
        self.assertEqual(len(level_1_treble), 5)
        self.assertTrue(all(n.pitch_with_octave in ["E4", "G4", "B4", "D5", "F5"] for n in level_1_treble))

        level_2_treble = generate_tutor_pool(2, "treble", False)
        # 5 lines + 4 spaces -> 9 notes
        self.assertEqual(len(level_2_treble), 9)

        level_4_treble = generate_tutor_pool(4, "treble", True)
        self.assertTrue(len(level_4_treble) > 13) # including accidentals
        # Check if C#4 is in it
        self.assertTrue(any(n.accidental == "#" for n in level_4_treble))

if __name__ == '__main__':
    unittest.main()
