import unittest
import time
from core.notes import Note
from core.user_manager import UserManager
from audio.metronome import Metronome

class TestDeadFeaturesPhase32(unittest.TestCase):
    def test_metronome_callback_signature_and_invocation(self):
        beat_calls = []

        def sample_callback(beat_num: int, timestamp: float = 0.0):
            beat_calls.append((beat_num, timestamp))

        metro = Metronome(bpm=120, beats_per_measure=4, on_beat=sample_callback)
        metro.start()
        time.sleep(0.6)  # Should trigger at least 1-2 beats
        metro.stop()

        self.assertGreater(len(beat_calls), 0, "Metronome callback failed to trigger")
        self.assertEqual(len(beat_calls[0]), 2, "Callback did not receive 2 arguments (beat_num, timestamp)")

    def test_practice_technique_play_note_objects(self):
        from gui.screens.practice_technique import PracticeTechniqueScreen
        import customtkinter as ctk

        root = ctk.CTk()
        um = UserManager()
        if not um.current_user:
            um.create_user("TestUserPhase32")

        screen = PracticeTechniqueScreen(root, um, lambda: None)
        
        # Test playing demo note without crashing
        try:
            screen._schedule_next_demo_note()
            # Test playing user note with integer MIDI without crashing
            screen._on_midi_note_on(60, 100)
        except Exception as exc:
            self.fail(f"PracticeTechniqueScreen failed on audio/MIDI calls: {exc}")
        finally:
            root.destroy()
