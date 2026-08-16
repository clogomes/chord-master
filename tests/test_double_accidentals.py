import unittest
from core.notes import Note
from core.chords import get_chord_notes, CHORD_TYPES
from core.scales import get_scale_notes, SCALE_TYPES

class TestDoubleAccidentals(unittest.TestCase):
    def test_double_accidentals_parsing(self):
        # Should parse without exception
        n1 = Note("C##")
        self.assertEqual(n1.midi, 62) # D4
        self.assertEqual(n1.name_pt, "Dó dobrado sustenido")
        
        n2 = Note("Bbb")
        self.assertEqual(n2.midi, 69) # A4
        self.assertEqual(n2.name_pt, "Si dobrado bemol")
        
        n3 = Note("F##")
        self.assertEqual(n3.midi, 67) # G4
        
        n4 = Note("Ebb")
        self.assertEqual(n4.midi, 62) # D4
        
    def test_all_chords_cartesian_product(self):
        """Test all root notes * all chord types to ensure no spelling exceptions."""
        roots = ["C", "C#", "Db", "D", "D#", "Eb", "E", "F", "F#", "Gb", "G", "G#", "Ab", "A", "A#", "Bb", "B"]
        for root_str in roots:
            for chord_type in CHORD_TYPES:
                try:
                    notes = get_chord_notes(root_str, chord_type)
                    self.assertTrue(len(notes) >= 3)
                except Exception as e:
                    self.fail(f"Chord combination {root_str} {chord_type} raised an exception: {e}")

    def test_all_scales_cartesian_product(self):
        """Test all root notes * all scale types to ensure no spelling exceptions."""
        roots = ["C", "C#", "Db", "D", "D#", "Eb", "E", "F", "F#", "Gb", "G", "G#", "Ab", "A", "A#", "Bb", "B"]
        for root_str in roots:
            for scale_type in SCALE_TYPES:
                try:
                    notes = get_scale_notes(root_str, scale_type)
                    self.assertTrue(len(notes) >= 5)
                except Exception as e:
                    self.fail(f"Scale combination {root_str} {scale_type} raised an exception: {e}")

if __name__ == '__main__':
    unittest.main()
