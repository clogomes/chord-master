"""Tests for Phase 58: Bar loop playback and tail-folding rendering in Compose Studio."""
import unittest
import numpy as np

from core.composition import Composition, NoteEvent, ChordEvent, RhythmTrack
from audio.backing_tracks import BACKING_TRACK_LIBRARY
from audio.composition_renderer import CompositionRenderer


class TestCompositionLoopPlayback(unittest.TestCase):
    def setUp(self):
        self.renderer = CompositionRenderer(sample_rate=44100)
        # Create a 4-bar test composition
        rock_pattern = BACKING_TRACK_LIBRARY.get("rock_basic") or list(BACKING_TRACK_LIBRARY.values())[0]
        rhythm = RhythmTrack.from_pattern(rock_pattern, bars=4)
        chords = [
            ChordEvent(start_beat=0.0, duration_beats=4.0, root="C", chord_type="major", instrument="piano"),
            ChordEvent(start_beat=4.0, duration_beats=4.0, root="G", chord_type="major", instrument="piano"),
            ChordEvent(start_beat=8.0, duration_beats=4.0, root="A", chord_type="minor", instrument="piano"),
            ChordEvent(start_beat=12.0, duration_beats=4.0, root="F", chord_type="major", instrument="piano"),
        ]
        notes = [
            NoteEvent(midi=60, start_beat=0.0, duration_beats=1.0, velocity=0.8, instrument="piano"),
            NoteEvent(midi=64, start_beat=4.0, duration_beats=1.0, velocity=0.8, instrument="piano"),
            NoteEvent(midi=67, start_beat=8.0, duration_beats=1.0, velocity=0.8, instrument="piano"),
            NoteEvent(midi=72, start_beat=12.0, duration_beats=1.0, velocity=0.8, instrument="piano"),
        ]
        self.comp = Composition(
            id="test_loop_comp",
            title="Loop Test",
            bpm=120,
            time_signature="4/4",
            bars=4,
            rhythm=rhythm,
            chords=chords,
            notes=notes,
            master_volume=0.8,
        )

    def test_full_render_default_backward_compatible(self):
        full_audio = self.renderer.render(self.comp)
        self.assertIsInstance(full_audio, np.ndarray)
        self.assertEqual(full_audio.ndim, 2)
        self.assertEqual(full_audio.shape[1], 2)
        # 4 bars at 120 bpm = 16 beats = 8.0s core + 3.0s tail = 11.0s = 485100 samples
        expected_samples = int(11.0 * 44100)
        self.assertEqual(len(full_audio), expected_samples)

    def test_loop_region_render_duration_and_tail_folding(self):
        # Render bars 2 to 3 (2 bars = 8 beats at 120 bpm = 4.0s = 176400 samples)
        loop_audio = self.renderer.render(self.comp, start_bar=2, end_bar=3)
        self.assertIsInstance(loop_audio, np.ndarray)
        self.assertEqual(loop_audio.ndim, 2)
        self.assertEqual(loop_audio.shape[1], 2)
        expected_loop_samples = int(4.0 * 44100)
        self.assertEqual(len(loop_audio), expected_loop_samples)

        # Confirm non-silent audio and no clipping
        rms = np.sqrt(np.mean(loop_audio ** 2))
        self.assertGreater(rms, 0.01)
        self.assertLessEqual(np.max(np.abs(loop_audio)), 1.0)

    def test_loop_single_bar_render(self):
        # Render single bar 3 (1 bar = 4 beats at 120 bpm = 2.0s = 88200 samples)
        loop_audio = self.renderer.render(self.comp, start_bar=3, end_bar=3)
        expected_samples = int(2.0 * 44100)
        self.assertEqual(len(loop_audio), expected_samples)
        self.assertGreater(np.sqrt(np.mean(loop_audio ** 2)), 0.01)


if __name__ == "__main__":
    unittest.main()
