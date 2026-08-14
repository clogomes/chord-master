"""Unit tests for QuizEngine and ScoreTracker."""
import os
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
