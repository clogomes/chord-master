"""Unit tests for QuizEngine and ScoreTracker."""
import os
import random
import tempfile
import unittest
from core.quiz_engine import QuizEngine, QuestionType
from core.score_tracker import ScoreTracker


class TestQuizAndScore(unittest.TestCase):

    def test_generate_ear_interval_question(self):
        q = QuizEngine.generate_ear_interval_question(difficulty="beginner")
        self.assertEqual(q.question_type, QuestionType.EAR_INTERVAL)
        self.assertEqual(len(q.options), 4)
        self.assertTrue(0 <= q.correct_index < 4)
        self.assertEqual(len(q.notes_to_play), 2)
        self.assertIn(q.correct_answer, q.options)

    def test_generate_ear_chord_question(self):
        q = QuizEngine.generate_ear_chord_question(difficulty="beginner")
        self.assertEqual(q.question_type, QuestionType.EAR_CHORD)
        self.assertEqual(len(q.options), 4)
        self.assertTrue(0 <= q.correct_index < 4)
        self.assertGreaterEqual(len(q.notes_to_play), 3)

    def test_generate_ear_progression_question(self):
        for diff in ("beginner", "intermediate", "advanced"):
            q = QuizEngine.generate_ear_progression_question(difficulty=diff)
            self.assertEqual(q.question_type, QuestionType.EAR_PROGRESSION)
            self.assertEqual(q.play_mode, "progression")
            self.assertEqual(q.category, "treino_auditivo")
            self.assertEqual(len(q.options), 4)
            self.assertEqual(len(set(q.options)), 4)
            self.assertTrue(0 <= q.correct_index < 4)
            self.assertEqual(q.options[q.correct_index], q.correct_answer)
            # Cada progressão tem >= 3 acordes, cada acorde >= 3 notas (tríades).
            self.assertGreaterEqual(len(q.chords_to_play), 3)
            for chord in q.chords_to_play:
                self.assertGreaterEqual(len(chord), 3)
                for note in chord:
                    self.assertTrue(24 <= note.midi <= 96)

    def test_progression_chords_are_diatonic(self):
        """I-V-vi-IV em Dó Maior (C4=60) produz as tríades esperadas."""
        from core.quiz_engine import _build_progression_chords
        chords = _build_progression_chords(
            "major", [(1, "major"), (5, "major"), (6, "minor"), (4, "major")], 60,
        )
        # I=C (C-E-G), V=G (G-B-D), vi=Am (A-C-E), IV=F (F-A-C)
        self.assertEqual([n.midi for n in chords[0]], [60, 64, 67])   # C major
        self.assertEqual([n.midi for n in chords[1]], [67, 71, 74])   # G major
        self.assertEqual([n.midi for n in chords[2]], [69, 72, 76])   # A minor
        self.assertEqual([n.midi for n in chords[3]], [65, 69, 72])   # F major

    def test_progression_minor_v_is_major(self):
        """Em Lá menor, o V (i-♭VII-♭VI-V) é Mi Maior (5ª elevada, harmónica)."""
        from core.quiz_engine import _build_progression_chords
        chords = _build_progression_chords(
            "minor", [(1, "minor"), (7, "major"), (6, "major"), (5, "major")], 57,
        )
        # V = Mi Maior: E4(64) G#4(68) B4(71) — o G# confirma a 5ª elevada.
        self.assertEqual([n.midi for n in chords[3]], [64, 68, 71])

    def test_progression_random_key_forces_relative_recognition(self):
        """Gerar várias perguntas deve produzir tonalidades (raízes) diferentes."""
        roots = set()
        for _ in range(30):
            q = QuizEngine.generate_ear_progression_question(difficulty="beginner")
            roots.add(q.chords_to_play[0][0].midi)
        self.assertGreater(len(roots), 1)

    def test_progression_explanation_references_library(self):
        """As progressões ligadas a uma música do repertório referem-na na explicação.

        Nem todas as progressões têm uma música na biblioteca (ex.: doo-wop
        referencia o género); mas as que têm (Cânone, Greensleeves, Ode to Joy,
        House of the Rising Sun, Malagueña) devem referi-lo. Gerar várias
        perguntas garante que pelo menos uma dessas é sorteada.
        """
        referenced = False
        for _ in range(40):
            q = QuizEngine.generate_ear_progression_question(
                difficulty=random.choice(["beginner", "intermediate", "advanced"]),
            )
            if "repertório" in q.explanation or "repertoire" in q.explanation:
                referenced = True
                break
        self.assertTrue(
            referenced,
            "Nenhuma progressão sorteada referiu uma música do repertório",
        )

    def test_progression_data_has_repertoire_references(self):
        """O conjunto de progressões inclui referências a músicas do repertório."""
        from core.quiz_engine import _PROGRESSIONS
        all_refs = [
            p["ref_pt"] for level in _PROGRESSIONS.values() for p in level
        ]
        self.assertTrue(any("repertório" in r for r in all_refs))

    def test_play_progression_runs_without_error(self):
        """play_progression reproduz os acordes (silenciosamente) sem erro."""
        from audio.player import get_audio_player
        q = QuizEngine.generate_ear_progression_question(difficulty="beginner")
        player = get_audio_player()
        try:
            player.play_progression(q.chords_to_play, chord_duration=0.1, gap=0.05, volume=0.0)
        except Exception as e:
            self.fail(f"play_progression falhou: {e}")
        finally:
            player.stop_all()

    def test_generate_staff_question(self):
        q_treble = QuizEngine.generate_staff_reading_question(clef="treble", include_accidentals=False)
        self.assertEqual(q_treble.clef, "treble")
        self.assertIsNotNone(q_treble.staff_note)
        self.assertEqual(len(q_treble.options), 4)

        q_bass = QuizEngine.generate_staff_reading_question(clef="bass", include_accidentals=True)
        self.assertEqual(q_bass.clef, "bass")
        self.assertIsNotNone(q_bass.staff_note)

    def test_generate_solfege_sing_question(self):
        q = QuizEngine.generate_solfege_sing_question(difficulty="beginner")
        self.assertEqual(q.question_type, QuestionType.SOLFEGE_SING)
        self.assertIsNotNone(q.target_note)
        self.assertIsNotNone(q.reference_note)
        self.assertEqual(len(q.options), 4)
        self.assertTrue(0 <= q.correct_index < 4)
        self.assertIn(q.correct_answer, q.options)

    def test_generate_theory_question(self):
        q = QuizEngine.generate_theory_question()
        self.assertEqual(len(q.options), 4)
        self.assertTrue(0 <= q.correct_index < 4)

    def test_score_tracker_streaks_and_persistence(self):
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            tracker = ScoreTracker(filepath=tmp_path)
            self.assertEqual(tracker.total_attempts, 0)
            self.assertEqual(tracker.global_accuracy, 0.0)

            # Record correct answer
            tracker.record_attempt(
                category="treino_auditivo",
                question_type="ear_interval",
                is_correct=True,
                prompt="Intervalo?",
                user_answer="Quinta Justa",
                correct_answer="Quinta Justa",
            )
            cat_stats = tracker.get_category_stats("treino_auditivo")
            self.assertEqual(cat_stats.total_attempts, 1)
            self.assertEqual(cat_stats.correct_count, 1)
            self.assertEqual(cat_stats.current_streak, 1)
            self.assertEqual(cat_stats.best_streak, 1)
            self.assertEqual(cat_stats.accuracy_rate, 100.0)

            # Record incorrect answer
            tracker.record_attempt(
                category="treino_auditivo",
                question_type="ear_interval",
                is_correct=False,
                prompt="Intervalo?",
                user_answer="Segunda Maior",
                correct_answer="Terça Menor",
            )
            self.assertEqual(cat_stats.total_attempts, 2)
            self.assertEqual(cat_stats.correct_count, 1)
            self.assertEqual(cat_stats.current_streak, 0)
            self.assertEqual(cat_stats.best_streak, 1)
            self.assertEqual(cat_stats.accuracy_rate, 50.0)

            # Verify reloading from disk
            tracker2 = ScoreTracker(filepath=tmp_path)
            self.assertEqual(tracker2.total_attempts, 2)
            self.assertEqual(tracker2.get_category_stats("treino_auditivo").accuracy_rate, 50.0)

            # Test reset
            tracker2.reset_all()
            self.assertEqual(tracker2.total_attempts, 0)
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)


if __name__ == "__main__":
    unittest.main()
