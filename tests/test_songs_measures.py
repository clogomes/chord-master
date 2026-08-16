"""Tests verifying that all repertoire songs close measures and have valid harmonic analyses."""
import unittest
from core.songs import SONG_LIBRARY, get_song_by_id


class TestSongsMeasuresAndAnalysis(unittest.TestCase):
    def test_all_24_songs_present(self):
        self.assertEqual(len(SONG_LIBRARY), 24)

    def test_all_songs_have_integer_measures(self):
        """Every song in SONG_LIBRARY must have a total beat duration that is an integer multiple of its measure length."""
        for s in SONG_LIBRARY:
            total = s.total_beats
            bpm = s.beats_per_measure
            remainder = total % bpm
            is_exact = abs(remainder) < 1e-4 or abs(remainder - bpm) < 1e-4
            self.assertTrue(
                is_exact,
                f"Song '{s.id}' ({s.title}) has total_beats={total} with beats_per_measure={bpm} ({s.time_signature}), "
                f"resulting in fractional measures ({total / bpm:.2f})"
            )

    def test_greensleeves_mode_in_aeolian(self):
        """Greensleeves analysis must accurately state A minor (Aeolian) because the notes contain F natural and not F#."""
        for sid in ["greensleeves", "guitar_greensleeves_full"]:
            s = get_song_by_id(sid)
            self.assertIsNotNone(s)
            analysis = s.get_theory_analysis("pt")
            if analysis:
                self.assertIn("Eólio", analysis)
                self.assertNotIn("Modo Dórico", analysis)

    def test_piano_fur_elise_harmonic_minor(self):
        """Für Elise analysis must specify Harmonic Minor due to G# leading tone."""
        s = get_song_by_id("piano_fur_elise")
        self.assertIsNotNone(s)
        analysis = s.get_theory_analysis("pt")
        self.assertIn("Menor Harmónica", analysis)

    def test_piano_gymnopedie_ionian(self):
        """Gymnopedie analysis must specify D Major / Ionian since G natural is used."""
        s = get_song_by_id("piano_gymnopedie")
        self.assertIsNotNone(s)
        analysis = s.get_theory_analysis("pt")
        self.assertIn("Jónico", analysis)
        self.assertNotIn("Modo Lídio", analysis)

    def test_guitar_malaguena_phrygian_dominant(self):
        """Malaguena analysis must specify Phrygian Dominant (major I with G#)."""
        s = get_song_by_id("guitar_malaguena")
        self.assertIsNotNone(s)
        analysis = s.get_theory_analysis("pt")
        self.assertIn("Frígio Dominante", analysis)

    def test_song_notes_not_empty(self):
        for s in SONG_LIBRARY:
            self.assertGreater(len(s.notes), 0, f"Song {s.id} has empty notes list")
            self.assertGreater(s.bpm, 0, f"Song {s.id} has invalid BPM")


if __name__ == "__main__":
    unittest.main()
