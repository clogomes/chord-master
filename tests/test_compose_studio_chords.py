import tempfile
import os
import unittest
import customtkinter as ctk
from core.user_manager import UserManager
from core.composition import Composition, ChordEvent, RhythmTrack
from core.chords import CHORD_TYPES, get_chord_notes
from gui.screens.compose_studio import ComposeStudioScreen, ROOT_OPTIONS


class TestComposeStudioChords(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        ctk.set_appearance_mode("Dark")
        cls.root = ctk.CTk()
        cls.root.withdraw()
        cls.tmp_file = tempfile.NamedTemporaryFile(suffix=".json", delete=False)
        cls.tmp_file.close()
        cls.user_manager = UserManager(filepath=cls.tmp_file.name)
        cls.user_manager.create_user("ChordStudioTester", "🎹")

    @classmethod
    def tearDownClass(cls):
        try:
            cls.root.destroy()
        except Exception:
            pass
        if hasattr(cls, "tmp_file") and os.path.exists(cls.tmp_file.name):
            os.unlink(cls.tmp_file.name)

    def test_root_options_and_chord_types_coverage(self):
        # 17 roots including all flats and sharps
        self.assertEqual(len(ROOT_OPTIONS), 17)
        for r in ["C", "Db", "D#", "Eb", "F#", "Gb", "Ab", "Bb"]:
            self.assertIn(r, ROOT_OPTIONS)

        # 22 chord types in CHORD_TYPES
        self.assertEqual(len(CHORD_TYPES), 22)
        for ctype in ["major", "minor", "dom7", "diminished", "augmented", "mMaj7", "7b9", "7#9", "sus4", "power"]:
            self.assertIn(ctype, CHORD_TYPES)

    def test_add_select_and_delete_chord_events(self):
        screen = ComposeStudioScreen(
            self.root,
            user_manager=self.user_manager,
            on_back=lambda: None,
        )
        screen.pack()
        self.root.update_idletasks()

        # Add 3 chords: C major (piano), G dom7 (piano), Am minor (guitar)
        screen.root_menu.set("C")
        screen.chord_type_menu.set("major (Tríade Maior)")
        screen.inst_menu.set("🎹 Piano")
        screen.start_beat_menu.set("0.0")
        screen.dur_menu.set("4.0")
        screen._add_chord_event()

        screen.root_menu.set("G")
        screen.chord_type_menu.set("dom7 (Sétima da Dominante)")
        screen.inst_menu.set("🎹 Piano")
        screen.start_beat_menu.set("4.0")
        screen.dur_menu.set("4.0")
        screen._add_chord_event()

        screen.root_menu.set("A")
        screen.chord_type_menu.set("minor (Tríade Menor)")
        screen.inst_menu.set("🎸 Viola")
        screen.start_beat_menu.set("8.0")
        screen.dur_menu.set("4.0")
        screen._add_chord_event()

        self.assertEqual(len(screen.composition.chords), 3)
        self.assertEqual(screen.composition.chords[0].root, "C")
        self.assertEqual(screen.composition.chords[1].root, "G")
        self.assertEqual(screen.composition.chords[2].root, "A")
        self.assertEqual(screen.composition.chords[2].instrument, "guitar")

        # Select chord index 0 (C major) and check visualizer sync
        screen._select_chord(0)
        c_notes = get_chord_notes("C", "major")
        self.assertTrue(len(screen.piano_widget.highlighted_midis) >= len(c_notes))

        # Select chord index 2 (Am minor guitar) and check fretboard sync
        screen._select_chord(2)
        self.assertIsNotNone(screen.guitar_widget.current_chord_shape)
        self.assertEqual(screen.guitar_widget.current_chord_shape.root, "A")

        # Delete chord index 1 (G dom7)
        screen._delete_chord(1)
        self.assertEqual(len(screen.composition.chords), 2)
        self.assertEqual(screen.composition.chords[1].root, "A")
        self.assertEqual(len(screen.step_grid.chords_data), 2)

        # Test clicking directly on a chord lane to insert a chord at beat 6.0
        screen._on_chord_lane_clicked("piano", 6.0)
        self.assertEqual(len(screen.composition.chords), 3)
        # Because chords are sorted [beat 0.0, beat 6.0, beat 8.0], index 1 has start_beat 6.0
        inserted_chord = next(c for c in screen.composition.chords if c.start_beat == 6.0)
        self.assertEqual(inserted_chord.instrument, "piano")
        self.assertEqual(screen.composition.chords[1].start_beat, 6.0)

        # Test moving a chord via drag-and-drop: move chord index 1 to beat 2.0 and switch instrument to guitar
        screen._on_chord_moved(1, new_start_beat=2.0, new_instrument="guitar")
        moved_chord = next(c for c in screen.composition.chords if c.start_beat == 2.0)
        self.assertEqual(moved_chord.instrument, "guitar")
        self.assertEqual(moved_chord.start_beat, 2.0)
        self.assertEqual(screen.step_grid.chords_data[1].instrument, "guitar")

        # Toggle visualizer modes
        screen._on_vis_mode_changed("🎹 Piano")
        screen._on_vis_mode_changed("🎸 Viola")
        screen._on_vis_mode_changed("👥 Ambos")

        screen.destroy()


if __name__ == "__main__":
    unittest.main()
