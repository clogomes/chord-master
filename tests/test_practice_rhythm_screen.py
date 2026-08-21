"""Testes de integração do Ecrã de Prática Rítmica (Fase 49).

Verificam, sem dependência de tempo real preciso, que:
- o ecrã se constrói sem exceções;
- o fluxo de batidas regista cada batida e termina a sessão;
- a categoria "ritmo" fica registada nas estatísticas do utilizador.
"""
import time
import unittest
import customtkinter as ctk
from core.user_manager import UserManager
from core.rhythm_exercises import RHYTHM_EXERCISES
from gui.screens.practice_rhythm import PracticeRhythmScreen


class TestPracticeRhythmScreen(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        ctk.set_appearance_mode("Dark")
        cls.root = ctk.CTk()
        cls.root.withdraw()
        cls.user_manager = UserManager(filepath=":memory:")
        cls.user_manager.create_user("TesterRhythm", "🥁")

    @classmethod
    def tearDownClass(cls):
        try:
            cls.root.destroy()
        except Exception:
            pass

    def test_screen_construction(self):
        screen = PracticeRhythmScreen(self.root, self.user_manager, on_back=lambda: None)
        screen.pack()
        self.root.update_idletasks()
        # Componentes-chave presentes.
        self.assertIsNotNone(screen.staff_view)
        self.assertIsNotNone(screen.tap_btn)
        self.assertIsNotNone(screen.score_card)
        self.assertEqual(screen.current_exercise, RHYTHM_EXERCISES[0])
        screen.destroy()

    def test_tap_flow_registers_rhythm_category(self):
        ex = RHYTHM_EXERCISES[0]  # 4/4, 4 batidas
        screen = PracticeRhythmScreen(self.root, self.user_manager, on_back=lambda: None)
        screen.pack()
        self.root.update_idletasks()
        screen._load_exercise(ex)

        # Sessão controlada: tempos esperados ≈ agora -> desvios pequenos (certos).
        screen.session_active = True
        screen.is_finished = False
        screen.current_note_idx = 0
        screen.taps = []
        now = time.time()
        screen._expected_timestamps = [now + 0.002] * len(ex.durations)

        for _ in range(len(ex.durations)):
            screen._on_tap()
            self.root.update_idletasks()

        # Terminou a sessão e registou todas as batidas.
        self.assertTrue(screen.is_finished)
        self.assertEqual(len(screen.taps), len(ex.durations))
        self.assertEqual(screen.current_note_idx, len(ex.durations))

        # Categoria "ritmo" registada nas estatísticas do utilizador.
        stats = self.user_manager.current_user.categories.get("ritmo")
        self.assertIsNotNone(stats, "A categoria 'ritmo' deve existir após a prática")
        self.assertGreaterEqual(stats.total_attempts, 1)

        # Competência atómica entrou na revisão espaçada (skill_id ritmo:<id>).
        self.assertIn(f"rhythm:{ex.id}", self.user_manager.current_user.spaced_review_data)
        screen.destroy()

    def test_late_taps_flagged(self):
        """Batidas deliberadamente atrasadas produzem desvio assinado positivo."""
        ex = RHYTHM_EXERCISES[0]
        screen = PracticeRhythmScreen(self.root, self.user_manager, on_back=lambda: None)
        screen.pack()
        self.root.update_idletasks()
        screen._load_exercise(ex)

        screen.session_active = True
        screen.is_finished = False
        screen.current_note_idx = 0
        screen.taps = []
        # Expectativas no passado -> o utilizador "bate" atrasado (~300 ms).
        past = time.time() - 0.3
        screen._expected_timestamps = [past] * len(ex.durations)

        for _ in range(len(ex.durations)):
            screen._on_tap()
        self.root.update_idletasks()

        # Todas as batidas ficaram atrasadas (desvio assinado > 0).
        self.assertTrue(all(s > 0 for (_, _, s, _) in screen.taps),
                        "Desvio assinado deve ser positivo quando se bate atrasado")
        screen.destroy()

    def test_strict_thresholds_90ms_is_not_perfect(self):
        """Regressão (Fase 49): com os limiares estritos do ecrã, 90 ms não é PERFEITO."""
        from audio.metronome import evaluate_rhythm_accuracy
        from gui.screens.practice_rhythm import PERFECT_MS, GOOD_MS
        # O ecrã usa limiares estritos (muito mais apertados que o default 95/220).
        self.assertLess(PERFECT_MS, 95.0)
        self.assertLess(GOOD_MS, 220.0)

        expected = 100.0
        # 90 ms de desvio -> BOM, não PERFEITO, com os limiares do ecrã.
        label, _, _ = evaluate_rhythm_accuracy(
            expected, expected + 0.090, perfect_ms=PERFECT_MS, good_ms=GOOD_MS,
        )
        self.assertNotIn("PERFEITO", label)
        self.assertIn("BOM", label)
        # E 30 ms -> PERFEITO.
        label30, _, _ = evaluate_rhythm_accuracy(
            expected, expected + 0.030, perfect_ms=PERFECT_MS, good_ms=GOOD_MS,
        )
        self.assertIn("PERFEITO", label30)


if __name__ == "__main__":
    unittest.main()
