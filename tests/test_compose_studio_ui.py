"""Unit tests for Compose Studio screen and StepGrid canvas component (Phase 42)."""
import unittest
import customtkinter as ctk
from core.user_manager import UserManager
from core.composition import Composition, RhythmTrack
from gui.components.step_grid import StepGrid, DRUM_ROWS
from gui.screens.compose_studio import ComposeStudioScreen


class TestComposeStudioUI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        ctk.set_appearance_mode("Dark")
        cls.root = ctk.CTk()
        cls.root.withdraw()
        cls.user_manager = UserManager(filepath=":memory:")
        cls.user_manager.create_user("ComposeTester", "🎛️")

    @classmethod
    def tearDownClass(cls):
        try:
            cls.root.destroy()
        except Exception:
            pass

    def test_step_grid_toggle_and_clear(self):
        frame = ctk.CTkFrame(self.root)
        frame.pack()

        changes = []
        grid_widget = StepGrid(
            frame,
            steps_per_bar=16,
            bars=4,
            on_grid_change=lambda g: changes.append(list(g)),
        )
        self.assertEqual(grid_widget.steps_per_bar, 16)
        self.assertEqual(grid_widget.bars, 4)
        self.assertEqual(len(grid_widget.grid_data), 64)

        # Set custom grid across 4 bars
        custom_grid = [["kick"], ["hihat_closed"], ["snare"], []]
        grid_widget.set_grid(custom_grid, steps_per_bar=16, bars=4)
        self.assertEqual(len(grid_widget.grid_data), 64)
        self.assertEqual(grid_widget.grid_data[0], ["kick"])
        self.assertEqual(grid_widget.grid_data[2], ["snare"])

        # Test clear
        grid_widget.clear()
        self.assertTrue(all(len(step) == 0 for step in grid_widget.grid_data))
        self.assertTrue(len(changes) > 0)

        grid_widget.destroy()
        frame.destroy()

    def test_legacy_1_bar_composition_auto_expansion_compatibility(self):
        """Validates that a legacy 16-step composition expands across all bars without data loss."""
        legacy_data = {
            "id": "legacy_rock",
            "title": "Legacy Rock",
            "bars": 4,
            "rhythm": {
                "steps_per_bar": 16,
                "grid": [["kick", "hihat_closed"]] + [[] for _ in range(15)],
            },
        }
        comp = Composition.from_dict(legacy_data)
        self.assertEqual(comp.bars, 4)
        # Should be expanded to 4 * 16 = 64 steps
        self.assertEqual(len(comp.rhythm.grid), 64)
        # Should have kick on steps 0, 16, 32, 48
        for bar_idx in range(4):
            step_idx = bar_idx * 16
            self.assertIn("kick", comp.rhythm.grid[step_idx])
            self.assertIn("hihat_closed", comp.rhythm.grid[step_idx])

    def test_compose_studio_screen_instantiation_and_controls(self):
        screen = ComposeStudioScreen(
            self.root,
            user_manager=self.user_manager,
            on_back=lambda: None,
        )
        screen.pack()
        self.root.update_idletasks()

        self.assertIsNotNone(screen.step_grid)
        self.assertIsNotNone(screen.bpm_slider)
        self.assertEqual(screen.composition.bpm, 100)

        # Change BPM
        screen._on_bpm_slider_changed(135)
        self.assertEqual(screen.composition.bpm, 135)
        self.assertEqual(screen.bpm_val_lbl.cget("text"), "135")

        # Change Bars
        screen._on_bars_changed("8")
        self.assertEqual(screen.composition.bars, 8)
        self.assertEqual(len(screen.composition.rhythm.grid), 8 * 16)

        # Test Playhead Cursor
        screen.step_grid.update_playback_cursor(0.5, bpm=120)
        self.assertIsNotNone(screen.step_grid.cursor_line_id)
        screen.step_grid.hide_playback_cursor()

        # Test Mousewheel Scroll
        class FakeEvent:
            def __init__(self, delta):
                self.delta = delta
        screen.step_grid._on_mousewheel(FakeEvent(-120))

        screen.destroy()


if __name__ == "__main__":
    unittest.main()
