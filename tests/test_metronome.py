"""Unit tests for metronome timing and rhythm evaluation."""
import unittest
from audio.metronome import Metronome, evaluate_rhythm_accuracy


class TestMetronome(unittest.TestCase):

    def test_metronome_initialization_and_tempo_bounds(self):
        m = Metronome(bpm=120, beats_per_measure=4)
        self.assertEqual(m.bpm, 120)
        self.assertEqual(m.beats_per_measure, 4)
        self.assertFalse(m.is_running)

        m.set_bpm(300)
        self.assertEqual(m.bpm, 240)  # Clamped to max

        m.set_bpm(10)
        self.assertEqual(m.bpm, 40)   # Clamped to min

    def test_evaluate_rhythm_accuracy(self):
        expected_t = 100.0

        # Perfect timing (<= 95 ms)
        rating, delta_ms, pts = evaluate_rhythm_accuracy(expected_t, 100.05)
        self.assertIn("PERFEITO", rating)
        self.assertEqual(pts, 50)

        # Good timing (<= 220 ms)
        rating_good, delta_ms_good, pts_good = evaluate_rhythm_accuracy(expected_t, 100.15)
        self.assertIn("BOM", rating_good)
        self.assertEqual(pts_good, 25)

        # Off-beat timing (> 220 ms)
        rating_off, delta_ms_off, pts_off = evaluate_rhythm_accuracy(expected_t, 100.40)
        self.assertIn("FORA DE TEMPO", rating_off)
        self.assertEqual(pts_off, 10)


if __name__ == "__main__":
    unittest.main()
