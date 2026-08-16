import unittest
from core.notes import Note, spell_note_with_letter
from core.scales import Scale
from core.chords import Chord
from core.songs import SONG_LIBRARY
from core.guitar import GuitarFretboardModel

class TestEngineCorrectionsPhase31(unittest.TestCase):
    def test_harmonic_spelling_flat_keys(self):
        # F Major scale spelling: F G A Bb C D E F
        f_scale = Scale(Note("F4"), "major")
        f_pitches = [n.pitch for n in f_scale.notes]
        self.assertEqual(f_pitches, ["F", "G", "A", "Bb", "C", "D", "E", "F"])

        # Bb Major scale spelling: Bb C D Eb F G A Bb
        bb_scale = Scale(Note("Bb4"), "major")
        bb_pitches = [n.pitch for n in bb_scale.notes]
        self.assertEqual(bb_pitches, ["Bb", "C", "D", "Eb", "F", "G", "A", "Bb"])

        # C Minor scale spelling: C D Eb F G Ab Bb C
        cm_scale = Scale(Note("C4"), "natural_minor")
        cm_pitches = [n.pitch for n in cm_scale.notes]
        self.assertEqual(cm_pitches, ["C", "D", "Eb", "F", "G", "Ab", "Bb", "C"])

        # C Diminished triad: C Eb Gb
        cdim = Chord(Note("C4"), "diminished")
        cdim_pitches = [n.pitch for n in cdim.notes]
        self.assertEqual(cdim_pitches, ["C", "Eb", "Gb"])

    def test_guitar_pitch_matching_with_octaves(self):
        model = GuitarFretboardModel(num_frets=15)
        
        # E4 should match 1st string open (string 5, fret 0)
        e4_pos = model.find_note_positions(Note("E4"))
        self.assertIn((5, 0), e4_pos)

        # E2 should match 6th string open (string 0, fret 0)
        e2_pos = model.find_note_positions(Note("E2"))
        self.assertIn((0, 0), e2_pos)

        # E3 should match 4th string 2nd fret (string 2, fret 2)
        e3_pos = model.find_note_positions(Note("E3"))
        self.assertIn((2, 2), e3_pos)

        # Verify all songs in library have valid matching notes on assigned string/fret
        for song in SONG_LIBRARY:
            for sn in song.notes:
                if sn.guitar_string is not None and sn.guitar_fret is not None:
                    fret_note = model.get_note_at(sn.guitar_string, sn.guitar_fret)
                    self.assertEqual(
                        fret_note.normalized_pitch,
                        sn.note.normalized_pitch,
                        f"Mismatch in {song.id}: written {sn.note.pitch_with_octave} vs fret {fret_note.pitch_with_octave}"
                    )
