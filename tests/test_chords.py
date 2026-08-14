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
        self.assertEqual(pitches, ["C", "D#", "F#"])  # Normalized sharp enharmonics

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


if __name__ == "__main__":
    unittest.main()
