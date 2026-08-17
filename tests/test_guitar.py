"""Unit tests for guitar/viola fretboard model, tunings, and chord shapes."""
import unittest
from core.notes import Note
from core.guitar import GuitarFretboardModel, GuitarChordShape, GUITAR_CHORD_LIBRARY, STANDARD_TUNING


class TestGuitar(unittest.TestCase):

    def setUp(self):
        self.model = GuitarFretboardModel()

    def test_open_string_tunings(self):
        # 6th string: E2 (MIDI 40)
        e2 = self.model.get_note_at(string_idx=0, fret=0)
        self.assertEqual(e2.pitch, "E")
        self.assertEqual(e2.octave, 2)
        self.assertEqual(e2.midi, 40)

        # 5th string: A2 (MIDI 45)
        a2 = self.model.get_note_at(string_idx=1, fret=0)
        self.assertEqual(a2.pitch, "A")
        self.assertEqual(a2.octave, 2)

        # 1st string: E4 (MIDI 64)
        e4 = self.model.get_note_at(string_idx=5, fret=0)
        self.assertEqual(e4.pitch, "E")
        self.assertEqual(e4.octave, 4)
        self.assertEqual(e4.midi, 64)

    def test_fret_transposition(self):
        # 6th string, fret 3 = G2
        g2 = self.model.get_note_at(string_idx=0, fret=3)
        self.assertEqual(g2.pitch, "G")
        self.assertEqual(g2.octave, 2)

        # 5th string, fret 3 = C3
        c3 = self.model.get_note_at(string_idx=1, fret=3)
        self.assertEqual(c3.pitch, "C")
        self.assertEqual(c3.octave, 3)

        # 2nd string, fret 1 = C4 (Middle C)
        c4 = self.model.get_note_at(string_idx=4, fret=1)
        self.assertEqual(c4.pitch, "C")
        self.assertEqual(c4.octave, 4)
        self.assertEqual(c4.midi, 60)

    def test_chord_library_shapes(self):
        # C Major open chord: [-1, 3, 2, 0, 1, 0]
        c_shape = self.model.get_chord_shape("C")
        self.assertIsNotNone(c_shape)
        self.assertEqual(c_shape.frets, [-1, 3, 2, 0, 1, 0])
        self.assertEqual(c_shape.root, "C")

        # F Major barre chord: [1, 3, 3, 2, 1, 1]
        f_shape = self.model.get_chord_shape("F")
        self.assertIsNotNone(f_shape)
        self.assertEqual(f_shape.frets, [1, 3, 3, 2, 1, 1])
        self.assertEqual(f_shape.barre_fret, 1)

        # Am open chord: [-1, 0, 2, 2, 1, 0]
        am_shape = self.model.get_chord_shape("Am")
        self.assertIsNotNone(am_shape)
        self.assertEqual(am_shape.frets, [-1, 0, 2, 2, 1, 0])

    def test_scale_positions_on_fretboard(self):
        c_major_notes = [Note("C4"), Note("D4"), Note("E4"), Note("F4"), Note("G4"), Note("A4"), Note("B4"), Note("C5")]
        positions = self.model.get_scale_positions_on_fretboard(c_major_notes)
        self.assertGreater(len(positions), 20)

        # Check root notes identification
        root_positions = [p for p in positions if p["is_root"]]
        self.assertTrue(any(p["string"] == 1 and p["fret"] == 3 for p in root_positions))  # 5th string 3rd fret is C

    def test_assign_guitar_coordinates(self):
        from core.guitar import assign_guitar_coordinates
        notes = [Note("C4"), Note("D4"), Note("E4"), Note("F4"), Note("G4")]
        coords = assign_guitar_coordinates(notes)
        self.assertEqual(len(coords), 5)
        for s, f in coords:
            self.assertTrue(0 <= s <= 5)
            self.assertTrue(0 <= f <= 15)

        # Empty test
        self.assertEqual(assign_guitar_coordinates([]), [])

    def test_expanded_guitar_chord_library(self):
        # Test Cadd9, Dsus4, Asus2
        cadd9 = self.model.get_chord_shape("Cadd9")
        self.assertIsNotNone(cadd9)
        self.assertEqual(cadd9.frets, [-1, 3, 2, 0, 3, 3])

        dsus4 = self.model.get_chord_shape("Dsus4")
        self.assertIsNotNone(dsus4)
        self.assertEqual(dsus4.frets, [-1, -1, 0, 2, 3, 3])

        # Test Power Chords
        e5 = self.model.get_chord_shape("E5")
        self.assertIsNotNone(e5)
        self.assertEqual(e5.frets[:3], [0, 2, 2])

        # Test Flat / Sharp root shapes
        bb = self.model.get_chord_shape("Bb")
        self.assertIsNotNone(bb)
        self.assertEqual(bb.frets, [-1, 1, 3, 3, 3, 1])


if __name__ == "__main__":
    unittest.main()
