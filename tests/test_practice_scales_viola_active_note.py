"""Tests for Phase 57: Viola timbre on scale practice and distinguishable active note on guitar fretboard."""
import os
import tempfile
import unittest
from unittest.mock import MagicMock
import customtkinter as ctk

from core.notes import Note
from core.scales import get_scale_notes
from core.user_manager import UserManager
from gui.screens.practice_scales import PracticeScalesScreen
from gui.components.guitar_fretboard import GuitarFretboard


class TestPracticeScalesViolaAndActiveNote(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        ctk.set_appearance_mode("Dark")
        cls.root = ctk.CTk()
        cls.root.withdraw()
        cls.tmp_file = tempfile.NamedTemporaryFile(suffix=".json", delete=False)
        cls.tmp_file.close()
        cls.user_manager = UserManager(filepath=cls.tmp_file.name)
        cls.user_manager.create_user("ScalesTester", "🎸")

    @classmethod
    def tearDownClass(cls):
        try:
            cls.root.destroy()
        except Exception:
            pass
        if hasattr(cls, "tmp_file") and os.path.exists(cls.tmp_file.name):
            os.unlink(cls.tmp_file.name)

    def test_guitar_fretboard_has_distinguishable_active_note(self):
        fretboard = GuitarFretboard(self.root, width=600, height=140)
        scale_notes = get_scale_notes("C", "major", octave=4)

        # Highlight entire scale
        fretboard.highlight_scale(scale_notes)

        # Mark exactly one position as active
        active_pos = (3, 10)  # G string, 10th fret (F) or similar
        fretboard.highlighted_positions[active_pos] = {
            "color": "#10B981",
            "label": "F",
            "is_root": False,
            "is_active": True,
            "note": Note("F", 4),
        }
        fretboard.redraw()
        self.root.update_idletasks()

        # Count active positions
        active_items = [
            pos for pos, data in fretboard.highlighted_positions.items()
            if data.get("is_active") is True
        ]
        self.assertEqual(len(active_items), 1)
        self.assertEqual(active_items[0], active_pos)

        fretboard.destroy()

    def test_practice_scales_screen_plays_guitar_audio_and_sets_active_note(self):
        screen = PracticeScalesScreen(self.root, self.user_manager, on_back=lambda: None)
        screen.pack()
        self.root.update_idletasks()

        # Mock audio player
        screen.audio_player.play_note = MagicMock()

        # Switch to guitar mode
        screen._on_instrument_changed("🎸 Viola")
        self.assertEqual(screen.instrument_mode, "guitar")

        # Advance scale note
        idx_before = screen.current_note_idx
        screen._handle_correct_note()
        self.root.update_idletasks()

        # Check play_note was called with instrument='guitar'
        self.assertTrue(screen.audio_player.play_note.called)
        call_kwargs = screen.audio_player.play_note.call_args[1]
        self.assertEqual(call_kwargs.get("instrument"), "guitar")

        # Verify active note on guitar_view has is_active == True and is unique
        active_items = [
            pos for pos, data in screen.guitar_view.highlighted_positions.items()
            if data.get("is_active") is True
        ]
        self.assertEqual(len(active_items), 1)

        screen.destroy()


if __name__ == "__main__":
    unittest.main()
