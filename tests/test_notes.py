"""Unit tests for Note class, MIDI, frequencies and conversions."""
import unittest
from core.notes import Note, midi_to_freq, note_to_midi, midi_to_note


class TestNotes(unittest.TestCase):

    def test_a4_frequency_and_midi(self):
        a4 = Note("A4")
        self.assertEqual(a4.midi, 69)
        self.assertAlmostEqual(a4.frequency, 440.0, places=2)
        self.assertEqual(a4.pitch, "A")
        self.assertEqual(a4.octave, 4)
        self.assertEqual(a4.name_pt, "Lá")

    def test_middle_c(self):
        c4 = Note("C4")
        self.assertEqual(c4.midi, 60)
        self.assertAlmostEqual(c4.frequency, 261.63, places=2)
        self.assertEqual(c4.name_pt, "Dó")

    def test_enharmonics(self):
        c_sharp = Note("C#4")
        d_flat = Note("Db4")
        self.assertEqual(c_sharp.midi, d_flat.midi)
        self.assertAlmostEqual(c_sharp.frequency, d_flat.frequency, places=4)
        self.assertEqual(c_sharp, d_flat)

    def test_transposition(self):
        c4 = Note("C4")
        g4 = c4.transpose(7)
        self.assertEqual(g4.pitch, "G")
        self.assertEqual(g4.octave, 4)
        self.assertEqual(g4.midi, 67)

        c5 = c4.transpose(12)
        self.assertEqual(c5.pitch, "C")
        self.assertEqual(c5.octave, 5)
        self.assertEqual(c5.midi, 72)

    def test_from_midi(self):
        note = Note.from_midi(60)
        self.assertEqual(note.pitch, "C")
        self.assertEqual(note.octave, 4)

    def test_invalid_note_raises(self):
        with self.assertRaises(ValueError):
            Note("H4")


if __name__ == "__main__":
    unittest.main()
