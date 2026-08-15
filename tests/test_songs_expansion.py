import unittest
from core.songs import SONG_LIBRARY
from audio.backing_tracks import BackingTrackPlayer

class TestSongsExpansion(unittest.TestCase):
    def test_repertoire_songs_expanded(self):
        # Test REPERTOIRE_SONGS has 24 songs total
        self.assertEqual(len(SONG_LIBRARY), 24, "Should have 24 songs in the library")
        
    def test_new_songs_validity(self):
        new_ids = [
            "piano_fur_elise", "piano_moonlight", "piano_gymnopedie", "piano_canon_c",
            "guitar_malaguena", "guitar_house_rising_sun", "guitar_spanish_romance", "guitar_greensleeves_full"
        ]
        
        for song_id in new_ids:
            song = next((s for s in SONG_LIBRARY if s.id == song_id), None)
            self.assertIsNotNone(song, f"Song {song_id} should exist")
            self.assertGreater(len(song.notes), 0, f"Song {song_id} should have notes")
            self.assertGreater(song.bpm, 0, f"Song {song_id} should have valid BPM")
            
            # Check fingerings are assigned
            for note in song.notes:
                self.assertIsNotNone(note.piano_finger, f"Note in {song_id} should have piano_finger assigned")
                self.assertIsNotNone(note.guitar_string, f"Note in {song_id} should have guitar_string assigned")
                self.assertIsNotNone(note.guitar_fret, f"Note in {song_id} should have guitar_fret assigned")

    def test_backing_track_styles(self):
        # Test BackingTrackPlayer.get_available_styles() contains all 8 styles
        styles = BackingTrackPlayer.get_available_styles()
        expected = ["rock", "pop", "16beat", "disco", "bossa_nova", "jazz_swing", "waltz_34", "bolero"]
        for exp in expected:
            self.assertIn(exp, styles, f"Style {exp} should be in available styles")
