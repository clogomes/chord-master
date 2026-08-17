"""Unit tests for musical chords, triads, tetrads and inversions."""
import unittest
from core.notes import Note
from core.chords import Chord, get_chord_notes, CHORD_TYPES


class TestChords(unittest.TestCase):

    def test_c_major_triad(self):
        c_chord = Chord(Note("C4"), "major")
        pitches = [n.pitch for n in c_chord.notes]
        self.assertEqual(pitches, ["C", "E", "G"])
        self.assertEqual(c_chord.chord_symbol, "C")

    def test_a_minor_triad(self):
        a_chord = Chord(Note("A3"), "minor")
        pitches = [n.pitch for n in a_chord.notes]
        self.assertEqual(pitches, ["A", "C", "E"])
        self.assertEqual(a_chord.chord_symbol, "Am")

    def test_c_diminished_triad(self):
        c_dim = Chord(Note("C4"), "diminished")
        pitches = [n.pitch for n in c_dim.notes]
        self.assertEqual(pitches, ["C", "Eb", "Gb"])  # Correct harmonic spelling

    def test_g_dom7(self):
        g7 = Chord(Note("G3"), "dom7")
        pitches = [n.pitch for n in g7.notes]
        self.assertEqual(pitches, ["G", "B", "D", "F"])
        self.assertEqual(g7.chord_symbol, "G7")

    def test_c_maj7(self):
        c_maj7 = Chord(Note("C4"), "maj7")
        pitches = [n.pitch for n in c_maj7.notes]
        self.assertEqual(pitches, ["C", "E", "G", "B"])
        self.assertEqual(c_maj7.chord_symbol, "Cmaj7")

    def test_inversions(self):
        # C Major root: C4 (60), E4 (64), G4 (67)
        c_root = Chord(Note("C4"), "major", inversion=0)
        self.assertEqual([n.midi for n in c_root.notes], [60, 64, 67])

        # 1st inversion: E4 (64), G4 (67), C5 (72)
        c_inv1 = Chord(Note("C4"), "major", inversion=1)
        self.assertEqual([n.midi for n in c_inv1.notes], [64, 67, 72])

        # 2nd inversion: G4 (67), C5 (72), E5 (76)
        c_inv2 = Chord(Note("C4"), "major", inversion=2)
        self.assertEqual([n.midi for n in c_inv2.notes], [67, 72, 76])

    def test_power_chord(self):
        c5 = Chord(Note("C4"), "power")
        pitches = [n.pitch for n in c5.notes]
        self.assertEqual(pitches, ["C", "G"])
        self.assertEqual(c5.chord_symbol, "C5")

    def test_add9_chord(self):
        c_add9 = Chord(Note("C4"), "add9")
        pitches = [n.pitch for n in c_add9.notes]
        self.assertEqual(pitches, ["C", "E", "G", "D"])
        self.assertEqual(c_add9.chord_symbol, "Cadd9")

    def test_6_and_m6_chords(self):
        c6 = Chord(Note("C4"), "6")
        self.assertEqual([n.pitch for n in c6.notes], ["C", "E", "G", "A"])

        cm6 = Chord(Note("C4"), "m6")
        self.assertEqual([n.pitch for n in cm6.notes], ["C", "Eb", "G", "A"])

    def test_altered_dominants(self):
        g7b9 = Chord(Note("G3"), "7b9")
        self.assertEqual([n.pitch for n in g7b9.notes], ["G", "B", "D", "F", "Ab"])

        e7sharp9 = Chord(Note("E3"), "7#9")
        self.assertEqual(e7sharp9.chord_symbol, "E7(♯9)")


if __name__ == "__main__":
    unittest.main()
