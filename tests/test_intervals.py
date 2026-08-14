"""Unit tests for musical intervals and transpositions."""
import unittest
from core.notes import Note
from core.intervals import get_interval, transpose_note, get_interval_by_code, INTERVALS


class TestIntervals(unittest.TestCase):

    def test_perfect_fifth(self):
        c4 = Note("C4")
        g4 = Note("G4")
        interval = get_interval(c4, g4)
        self.assertEqual(interval.semitones, 7)
        self.assertEqual(interval.short_code, "P5")
        self.assertEqual(interval.name_pt, "Quinta Justa")

    def test_major_third(self):
        c4 = Note("C4")
        e4 = Note("E4")
        interval = get_interval(c4, e4)
        self.assertEqual(interval.semitones, 4)
        self.assertEqual(interval.short_code, "M3")
        self.assertEqual(interval.name_pt, "Terça Maior")

    def test_minor_third(self):
        a3 = Note("A3")
        c4 = Note("C4")
        interval = get_interval(a3, c4)
        self.assertEqual(interval.semitones, 3)
        self.assertEqual(interval.short_code, "m3")
        self.assertEqual(interval.name_pt, "Terça Menor")

    def test_tritone(self):
        c4 = Note("C4")
        f_sharp4 = Note("F#4")
        interval = get_interval(c4, f_sharp4)
        self.assertEqual(interval.semitones, 6)
        self.assertEqual(interval.short_code, "TT")

    def test_transpose_helper(self):
        d4 = Note("D4")
        transposed = transpose_note(d4, 7)  # +P5 -> A4
        self.assertEqual(transposed.pitch, "A")
        self.assertEqual(transposed.octave, 4)

    def test_get_by_code(self):
        p8 = get_interval_by_code("P8")
        self.assertIsNotNone(p8)
        self.assertEqual(p8.semitones, 12)
        self.assertEqual(p8.name_pt, "Oitava Justa")


if __name__ == "__main__":
    unittest.main()
