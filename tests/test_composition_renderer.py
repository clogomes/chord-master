"""Comprehensive unit tests for offline composition renderer (Phase 41)."""
import unittest
import numpy as np
from core.composition import Composition, ChordEvent, RhythmTrack
from audio.composition_renderer import CompositionRenderer, SAMPLE_RATE
from audio.backing_tracks import BACKING_TRACK_LIBRARY


class TestCompositionRenderer(unittest.TestCase):
    def setUp(self):
        self.renderer = CompositionRenderer(sample_rate=44100)

    def test_empty_composition_renders_valid_stereo_array(self):
        comp = Composition(id="empty", title="Empty", bpm=120, bars=2)
        audio = self.renderer.render(comp)
        self.assertIsInstance(audio, np.ndarray)
        self.assertEqual(audio.dtype, np.float32)
        self.assertEqual(audio.ndim, 2)
        self.assertEqual(audio.shape[1], 2)
        # 2 bars * 4 beats * (60 / 120) = 4.0s + 3.0s tail = 7.0s * 44100 = 308700 samples
        expected_samples = int(7.0 * 44100)
        self.assertEqual(audio.shape[0], expected_samples)
        # Should be silence
        self.assertAlmostEqual(float(np.max(np.abs(audio))), 0.0, places=5)

    def test_kick_on_beat_2_at_120_bpm_exact_sample_index(self):
        """Asserção forte: um bombo no tempo 2 a 120 BPM inicia energia exatamente no índice 44100."""
        # 120 BPM -> 1 beat = 0.5s = 22050 samples. Beat 2 starts at beat index 2 (1.0 second = 44100 samples)
        # Grid with 16 steps per bar (4 steps per beat). Beat 2 (0-indexed beat 2 = step 8).
        grid = [[] for _ in range(16)]
        grid[8] = ["kick"]  # Step 8 is beat 2.0 (1.0s into the bar)
        
        comp = Composition(
            id="kick_test",
            title="Kick Test",
            bpm=120,
            bars=1,
            rhythm=RhythmTrack(steps_per_bar=16, grid=grid, volume=1.0),
        )
        audio = self.renderer.render(comp)
        
        # Beat 2 starts at 1.0s -> sample 44100.
        # Check that energy before 44100 is silence, and energy immediately at 44100 rises.
        expected_kick_sample = 44100
        self.assertEqual(float(np.max(np.abs(audio[:expected_kick_sample, 0]))), 0.0)
        self.assertGreater(float(np.max(np.abs(audio[expected_kick_sample : expected_kick_sample + 64, 0]))), 0.05)

    def test_piano_and_guitar_chords_mixed_rendering(self):
        chords = [
            ChordEvent("C", "major", start_beat=0.0, duration_beats=2.0, instrument="piano"),
            ChordEvent("G", "dom7", start_beat=2.0, duration_beats=2.0, instrument="guitar"),
        ]
        rhythm = RhythmTrack.from_pattern(BACKING_TRACK_LIBRARY["rock_basic"])
        comp = Composition(
            id="mix_test",
            title="Mixed Test",
            bpm=100,
            bars=2,
            rhythm=rhythm,
            chords=chords,
            master_volume=0.9,
        )
        audio = self.renderer.render(comp)
        self.assertGreater(float(np.max(np.abs(audio))), 0.1)
        self.assertLessEqual(float(np.max(np.abs(audio))), 1.0)
        # Check stereo differentiation (panning)
        left_energy = float(np.sum(audio[:, 0] ** 2))
        right_energy = float(np.sum(audio[:, 1] ** 2))
        self.assertGreater(left_energy, 0)
        self.assertGreater(right_energy, 0)

    def test_all_new_percussion_synthesizers(self):
        new_drums = ["tom_high", "tom_mid", "tom_low", "clap", "crash", "rimshot", "cowbell"]
        for d in new_drums:
            grid = [[] for _ in range(16)]
            grid[0] = [d]
            comp = Composition(
                id=f"test_{d}",
                title=f"Test {d}",
                bpm=120,
                bars=1,
                rhythm=RhythmTrack(steps_per_bar=16, grid=grid, volume=1.0),
            )
            audio = self.renderer.render(comp)
            self.assertGreater(float(np.max(np.abs(audio))), 0.05, f"Drum {d} produced near-silence")

    def test_crash_cymbal_on_last_step_full_decay_no_truncation(self):
        """Test crash on last step: verify full 2.5s decay fits in buffer without hard cutoff."""
        grid = [[] for _ in range(16)]
        grid[15] = ["crash"]  # Last step
        comp = Composition(
            id="crash_tail_test",
            title="Crash Tail Test",
            bpm=120,
            bars=1,
            rhythm=RhythmTrack(steps_per_bar=16, grid=grid, volume=1.0),
        )
        audio = self.renderer.render(comp)
        # End of buffer should decay to near-zero without clipping or sudden stop
        end_samples = audio[-100:, :]
        self.assertLess(float(np.max(np.abs(end_samples))), 0.05)


if __name__ == "__main__":
    unittest.main()
