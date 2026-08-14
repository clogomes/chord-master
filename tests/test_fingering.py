"""Unit tests for piano fingering recommendations."""
import unittest
from core.notes import Note
from core.chords import Chord
from core.fingering import get_chord_piano_fingering, RIGHT_HAND_TRIAD_FINGERINGS


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


if __name__ == "__main__":
    unittest.main()
