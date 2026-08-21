"""Unit tests for piano fingering recommendations."""
import unittest
from core.notes import Note
from core.chords import Chord
from core.fingering import get_chord_piano_fingering, get_scale_piano_fingering_description, RIGHT_HAND_TRIAD_FINGERINGS
from core.scales import SCALE_TYPES


class TestFingering(unittest.TestCase):

    def test_triad_root_fingering_right_hand(self):
        # C Major: C4 (60), E4 (64), G4 (67)
        c_major = Chord(Note("C4"), "major")
        fingering = get_chord_piano_fingering(c_major.notes, inversion=0, hand="right")
        self.assertEqual(len(fingering), 3)
        self.assertEqual(fingering[60], 1)  # Thumb
        self.assertEqual(fingering[64], 3)  # Middle
        self.assertEqual(fingering[67], 5)  # Pinky

    def test_triad_first_inversion_fingering_right_hand(self):
        # C/E: E4 (64), G4 (67), C5 (72)
        c_inv1 = Chord(Note("C4"), "major", inversion=1)
        fingering = get_chord_piano_fingering(c_inv1.notes, inversion=1, hand="right")
        self.assertEqual(len(fingering), 3)
        self.assertEqual(fingering[64], 1)  # Thumb on E4
        self.assertEqual(fingering[67], 2)  # Index on G4
        self.assertEqual(fingering[72], 5)  # Pinky on C5

    def test_triad_second_inversion_fingering_right_hand(self):
        # C/G: G4 (67), C5 (72), E5 (76)
        c_inv2 = Chord(Note("C4"), "major", inversion=2)
        fingering = get_chord_piano_fingering(c_inv2.notes, inversion=2, hand="right")
        self.assertEqual(fingering[67], 1)  # Thumb on G4
        self.assertEqual(fingering[72], 3)  # Middle on C5
        self.assertEqual(fingering[76], 5)  # Pinky on E5

    def test_tetrad_fingering_right_hand(self):
        # C7: C4 (60), E4 (64), G4 (67), A#4/Bb4 (70)
        c7 = Chord(Note("C4"), "dom7")
        fingering = get_chord_piano_fingering(c7.notes, inversion=0, hand="right")
        self.assertEqual(len(fingering), 4)
        self.assertEqual(fingering[60], 1)
        self.assertEqual(fingering[64], 2)
        self.assertEqual(fingering[67], 3)
        self.assertEqual(fingering[70], 5)

    def test_left_hand_fingering(self):
        c_major = Chord(Note("C3"), "major")
        fingering = get_chord_piano_fingering(c_major.notes, inversion=0, hand="left")
        self.assertEqual(fingering[48], 5)  # Pinky on C3
        self.assertEqual(fingering[52], 3)  # Middle on E3
        self.assertEqual(fingering[55], 1)  # Thumb on G3

    def test_assign_piano_fingerings_melodic(self):
        from core.fingering import assign_piano_fingerings
        notes = [Note("C4"), Note("D4"), Note("E4"), Note("F4"), Note("G4")]
        fingers = assign_piano_fingerings(notes)
        self.assertEqual(len(fingers), 5)
        self.assertEqual(fingers[0], 1)
        # ascending scale fingers should increase up to 5
        self.assertTrue(all(1 <= f <= 5 for f in fingers))
        self.assertEqual(fingers[-1], 5)

        # Empty list test
        self.assertEqual(assign_piano_fingerings([]), [])


class TestScaleFingeringDescription(unittest.TestCase):
    """Tests for get_scale_piano_fingering_description (Fase 53)."""

    def test_different_families_return_different_text(self):
        from core.fingering import get_scale_piano_fingering_description
        from core.scales import SCALE_TYPES

        seven = get_scale_piano_fingering_description("major", "right")
        five = get_scale_piano_fingering_description("major_pentatonic", "right")
        twelve = get_scale_piano_fingering_description("chromatic", "right")
        six = get_scale_piano_fingering_description("blues", "right")

        self.assertNotEqual(seven, five)
        self.assertNotEqual(seven, twelve)
        self.assertNotEqual(five, twelve)
        self.assertNotEqual(seven, six)

    def test_all_scale_types_return_nonempty(self):
        from core.fingering import get_scale_piano_fingering_description
        from core.scales import SCALE_TYPES

        for scale_key in SCALE_TYPES:
            for hand in ("right", "left"):
                result = get_scale_piano_fingering_description(scale_key, hand)
                self.assertTrue(len(result) > 0, f"Empty result for {scale_key}/{hand}")

    def test_hand_variants(self):
        from core.fingering import get_scale_piano_fingering_description

        right = get_scale_piano_fingering_description("major", "right")
        direita = get_scale_piano_fingering_description("major", "direita")
        self.assertEqual(right, direita)

        left = get_scale_piano_fingering_description("major", "left")
        esquerda = get_scale_piano_fingering_description("major", "esquerda")
        self.assertEqual(left, esquerda)

    def test_right_and_left_differ(self):
        from core.fingering import get_scale_piano_fingering_description

        right = get_scale_piano_fingering_description("major", "right")
        left = get_scale_piano_fingering_description("major", "left")
        self.assertNotEqual(right, left)

    def test_unknown_scale_returns_generic(self):
        from core.fingering import get_scale_piano_fingering_description

        result = get_scale_piano_fingering_description("nonexistent_scale", "right")
        self.assertIn("padrão genérico", result)


if __name__ == "__main__":
    unittest.main()
