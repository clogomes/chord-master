"""Unit tests for public domain song repertoire and note coordinates."""
import unittest
from core.songs import Song, SongNote, SONG_LIBRARY, get_song_by_id
from core.guitar import GuitarFretboardModel


class TestSongs(unittest.TestCase):

    def setUp(self):
        self.fretboard_model = GuitarFretboardModel()

    def test_song_library_not_empty(self):
        self.assertGreaterEqual(len(SONG_LIBRARY), 6)

    def test_song_attributes_and_unique_ids(self):
        seen_ids = set()
        for song in SONG_LIBRARY:
            self.assertNotIn(song.id, seen_ids, f"ID de música duplicado: {song.id}")
            seen_ids.add(song.id)

            self.assertTrue(len(song.title) > 0)
            self.assertTrue(len(song.composer) > 0)
            self.assertIn(song.difficulty, ["Iniciante", "Intermédio", "Avançado"])
            self.assertGreater(song.bpm, 40)
            self.assertIn(song.clef, ["treble", "bass"])
            self.assertGreater(song.note_count, 0)
            self.assertGreater(song.total_beats, 0)

    def test_notes_validity_and_durations(self):
        for song in SONG_LIBRARY:
            for i, sn in enumerate(song.notes):
                # Note duration must be positive
                self.assertGreater(sn.duration_beats, 0, f"Duração inválida em {song.id} nota #{i}")

                # Note MIDI in playable piano range (21 to 108)
                self.assertTrue(21 <= sn.note.midi <= 108, f"Nota fora do alcance do piano: {sn.note}")

                # Piano finger must be 1-5 if specified
                if sn.piano_finger is not None:
                    self.assertIn(sn.piano_finger, [1, 2, 3, 4, 5])
                self.assertIn(sn.piano_hand, ["right", "left", "direita", "esquerda"])

                # Guitar coordinates must match note pitch if specified
                if sn.guitar_string is not None and sn.guitar_fret is not None:
                    self.assertTrue(0 <= sn.guitar_string <= 5)
                    self.assertTrue(0 <= sn.guitar_fret <= 24)

                    actual_fret_note = self.fretboard_model.get_note_at(sn.guitar_string, sn.guitar_fret)
                    self.assertEqual(
                        actual_fret_note.normalized_pitch,
                        sn.note.normalized_pitch,
                        f"Inconsistência de traste na viola para {song.id} nota #{i}: esperado {sn.note.pitch}, obtido {actual_fret_note.pitch}"
                    )

    def test_get_song_by_id(self):
        song = get_song_by_id("ode_to_joy")
        self.assertIsNotNone(song)
        self.assertEqual(song.title, "Hino à Alegria (9ª Sinfonia)")

        none_song = get_song_by_id("non_existent_id")
        self.assertIsNone(none_song)


if __name__ == "__main__":
    unittest.main()
