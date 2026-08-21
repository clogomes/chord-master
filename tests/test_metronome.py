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

    def test_evaluate_rhythm_accuracy_strict_thresholds(self):
        """Limiares estritos do ecrã de ritmo (45/110 ms): 30 ms é perfeito, 90 ms não.

        Regressão (Fase 49): os limiares por omissão (95/220) eram demasiado
        permissivos para o treino de ritmo — 90 ms de desvio não pode ser "PERFEITO".
        """
        expected_t = 100.0
        # 30 ms -> dentro de perfect_ms=45 -> PERFEITO
        rating, _, pts = evaluate_rhythm_accuracy(expected_t, 100.030, perfect_ms=45.0, good_ms=110.0)
        self.assertIn("PERFEITO", rating)
        self.assertEqual(pts, 50)
        # 90 ms -> fora de 45 mas dentro de 110 -> BOM (não é perfeito)
        rating90, _, pts90 = evaluate_rhythm_accuracy(expected_t, 100.090, perfect_ms=45.0, good_ms=110.0)
        self.assertNotIn("PERFEITO", rating90)
        self.assertIn("BOM", rating90)
        self.assertEqual(pts90, 25)

    def test_evaluate_rhythm_accuracy_defaults_preserve_legacy(self):
        """Os defaults (95/220) preservam o comportamento dos outros ecrãs."""
        expected_t = 100.0
        # 90 ms com defaults -> ainda PERFEITO (comportamento legado dos outros ecrãs)
        rating, _, _ = evaluate_rhythm_accuracy(expected_t, 100.090)
        self.assertIn("PERFEITO", rating)


if __name__ == "__main__":
    unittest.main()
