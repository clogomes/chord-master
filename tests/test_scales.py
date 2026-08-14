"""Unit tests for musical scales and modes."""
import unittest
from core.notes import Note
from core.scales import Scale, get_scale_notes, SCALE_TYPES


class TestScales(unittest.TestCase):

    def test_c_major_scale(self):
        c_maj = Scale(Note("C4"), "major")
        pitches = [n.pitch for n in c_maj.notes]
        expected = ["C", "D", "E", "F", "G", "A", "B", "C"]
        self.assertEqual(pitches, expected)
        self.assertEqual(len(c_maj.notes), 8)

    def test_a_natural_minor_scale(self):
        a_min = Scale(Note("A3"), "natural_minor")
        pitches = [n.pitch for n in a_min.notes]
        expected = ["A", "B", "C", "D", "E", "F", "G", "A"]
        self.assertEqual(pitches, expected)

    def test_a_harmonic_minor_scale(self):
        a_harm = Scale(Note("A3"), "harmonic_minor")
        pitches = [n.pitch for n in a_harm.notes]
        expected = ["A", "B", "C", "D", "E", "F", "G#", "A"]
        self.assertEqual(pitches, expected)

    def test_c_pentatonic_major(self):
        c_penta = Scale(Note("C4"), "major_pentatonic")
        pitches = [n.pitch for n in c_penta.notes]
        expected = ["C", "D", "E", "G", "A", "C"]
        self.assertEqual(pitches, expected)

    def test_a_pentatonic_minor(self):
        a_penta = Scale(Note("A3"), "minor_pentatonic")
        pitches = [n.pitch for n in a_penta.notes]
        expected = ["A", "C", "D", "E", "G", "A"]
        self.assertEqual(pitches, expected)

    def test_get_scale_notes_helper(self):
        notes = get_scale_notes("G", "major", octave=4)
        pitches = [n.pitch for n in notes]
        # G Major has F#
        self.assertIn("F#", pitches)
        self.assertEqual(pitches[0], "G")


if __name__ == "__main__":
    unittest.main()
