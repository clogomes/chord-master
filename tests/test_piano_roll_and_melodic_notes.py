"""Tests for Phase 56: NoteEvent model, PianoRoll canvas component, and melodic note rendering."""
import os
import tempfile
import unittest
import numpy as np
import customtkinter as ctk

from core.composition import Composition, ChordEvent, NoteEvent, RhythmTrack
from core.compositions import get_template_composition
from audio.composition_renderer import CompositionRenderer
from gui.components.piano_roll import PianoRoll
from gui.screens.compose_studio import ComposeStudioScreen
from core.user_manager import UserManager


class TestPianoRollAndMelodicNotes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        ctk.set_appearance_mode("Dark")
        cls.root = ctk.CTk()
        cls.root.withdraw()
        cls.tmp_file = tempfile.NamedTemporaryFile(suffix=".json", delete=False)
        cls.tmp_file.close()
        cls.user_manager = UserManager(filepath=cls.tmp_file.name)
        cls.user_manager.create_user("MelodyTester", "🎼")

    @classmethod
    def tearDownClass(cls):
        try:
            cls.root.destroy()
        except Exception:
            pass
        if hasattr(cls, "tmp_file") and os.path.exists(cls.tmp_file.name):
            os.unlink(cls.tmp_file.name)

    def test_note_event_serialization_and_schema_version_2(self):
        note = NoteEvent(midi=64, start_beat=1.5, duration_beats=2.0, velocity=0.9, instrument="guitar")
        d = note.to_dict()
        self.assertEqual(d["midi"], 64)
        self.assertEqual(d["start_beat"], 1.5)
        self.assertEqual(d["duration_beats"], 2.0)
        self.assertEqual(d["velocity"], 0.9)
        self.assertEqual(d["instrument"], "guitar")

        restored = NoteEvent.from_dict(d)
        self.assertEqual(restored.midi, 64)
        self.assertEqual(restored.start_beat, 1.5)
        self.assertEqual(restored.duration_beats, 2.0)
        self.assertEqual(restored.instrument, "guitar")

        # Composition with notes
        comp = get_template_composition("pop")
        comp.notes = [note]
        comp_dict = comp.to_dict()
        self.assertEqual(comp_dict["schema_version"], 2)
        self.assertEqual(len(comp_dict["notes"]), 1)

        # Backwards compatibility: load from schema v1 without notes field
        legacy_data = {
            "id": "comp_legacy",
            "title": "Legacy Comp",
            "bpm": 120,
            "bars": 2,
            "schema_version": 1,
        }
        loaded = Composition.from_dict(legacy_data)
        self.assertEqual(loaded.schema_version, 1)
        self.assertEqual(loaded.notes, [])

    def test_composition_renderer_with_melodic_notes(self):
        renderer = CompositionRenderer(sample_rate=22050)
        comp = get_template_composition("rock_basic")
        comp.notes = [
            NoteEvent(midi=60, start_beat=0.0, duration_beats=1.0, instrument="piano"),
            NoteEvent(midi=62, start_beat=1.0, duration_beats=1.0, instrument="piano"),
            NoteEvent(midi=64, start_beat=2.0, duration_beats=1.0, instrument="guitar"),
            NoteEvent(midi=67, start_beat=3.0, duration_beats=1.0, instrument="guitar"),
        ]
        stereo = renderer.render(comp)
        self.assertIsInstance(stereo, np.ndarray)
        self.assertEqual(stereo.ndim, 2)
        self.assertEqual(stereo.shape[1], 2)
        self.assertGreater(np.max(np.abs(stereo)), 0.01)

    def test_piano_roll_canvas_interactions(self):
        notes = [
            NoteEvent(midi=60, start_beat=0.0, duration_beats=1.0, instrument="piano"),
            NoteEvent(midi=64, start_beat=2.0, duration_beats=2.0, instrument="guitar"),
        ]
        changed_notes = []
        selected_notes = []

        roll = PianoRoll(
            self.root,
            notes=notes,
            bars=4,
            steps_per_bar=16,
            on_notes_changed=lambda n: changed_notes.append(list(n)),
            on_note_selected=lambda n: selected_notes.append(n),
        )
        roll.pack()
        self.root.update_idletasks()

        self.assertEqual(len(roll.notes), 2)
        # Test selection & delete
        roll.selected_note_idx = 0
        roll.delete_selected_note()
        self.assertEqual(len(roll.notes), 1)
        self.assertEqual(roll.notes[0].midi, 64)

        # Test instrument change
        roll.selected_note_idx = 0
        roll.set_instrument("piano")
        self.assertEqual(roll.notes[0].instrument, "piano")

        roll.destroy()

    def test_compose_studio_screen_integration_with_piano_roll(self):
        screen = ComposeStudioScreen(self.root, self.user_manager, on_back=lambda: None)
        screen.pack()
        self.root.update_idletasks()

        self.assertTrue(hasattr(screen, "piano_roll"))
        self.assertTrue(hasattr(screen, "staff_widget"))

        # Add a note via callback
        screen._on_melody_notes_changed([
            NoteEvent(midi=60, start_beat=0.0, duration_beats=1.0, instrument="piano"),
        ])
        self.assertEqual(len(screen.composition.notes), 1)

        # Select note
        screen._on_melody_note_selected(screen.composition.notes[0])
        self.root.update_idletasks()

        screen.destroy()


if __name__ == "__main__":
    unittest.main()
