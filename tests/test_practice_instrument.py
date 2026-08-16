import unittest
from core.notes import Note
from core.songs import SONG_LIBRARY
from gui.screens.practice_instrument import calculate_pitch_directional_hint

class TestPracticeInstrumentPedagogy(unittest.TestCase):
    def test_directional_hints(self):
        target = Note("E4")  # MIDI 64
        detected_lower = Note("D4")  # MIDI 62 (2 semitones lower = 1 tone)
        detected_higher = Note("F4")  # MIDI 65 (1 semitone higher)
        detected_same = Note("E4")

        hint_lower = calculate_pitch_directional_hint(target, detected_lower)
        self.assertIn("sobe 1 tom", hint_lower)
        self.assertIn("2 semitons", hint_lower)

        hint_higher = calculate_pitch_directional_hint(target, detected_higher)
        self.assertIn("desce 1 semitom", hint_higher)

        hint_same = calculate_pitch_directional_hint(target, detected_same)
        self.assertIn("ajusta a afinação", hint_same)

    def test_repertoire_songs_available(self):
        self.assertGreater(len(SONG_LIBRARY), 0, "Song library should not be empty")
        for song in SONG_LIBRARY:
            self.assertTrue(song.title)
            self.assertGreater(len(song.notes), 0)
