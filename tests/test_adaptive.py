"""Unit tests for the Adaptive Practice Engine and weak area identification."""
import time
import unittest
from core.user_manager import UserProfile, ExerciseRecord, CategoryStats
from core.adaptive_engine import (
    get_weak_areas,
    get_recommendation,
    generate_adaptive_question,
)
from core.quiz_engine import QuizQuestion


class TestAdaptiveEngine(unittest.TestCase):

    def test_empty_history_returns_baseline(self):
        user = UserProfile(username="Iniciante", avatar="🌱")
        weak_areas = get_weak_areas(user)
        self.assertGreaterEqual(len(weak_areas), 4)

        rec = get_recommendation(user)
        self.assertIn("Começa", rec["title"])
        self.assertTrue(rec["route"])

    def test_synthetic_history_identifies_weakest_area(self):
        # Create a user profile with high performance in theory & ear, but poor performance in sight reading
        now = time.time()
        user = UserProfile(username="Estudante", avatar="🎼")

        # 10 correct attempts in ear training
        for i in range(10):
            user.history.append(
                ExerciseRecord(
                    timestamp=now - 500 + i * 10,
                    category="treino_auditivo",
                    question_type="ear_interval",
                    is_correct=True,
                    prompt="Intervalo?",
                    user_answer="5ª Justa",
                    correct_answer="5ª Justa",
                )
            )

        # 10 correct attempts in theory
        for i in range(10):
            user.history.append(
                ExerciseRecord(
                    timestamp=now - 400 + i * 10,
                    category="teoria",
                    question_type="theory_chord",
                    is_correct=True,
                    prompt="Acorde?",
                    user_answer="Maior",
                    correct_answer="Maior",
                )
            )

        # 10 attempts in sheet music reading with 8 mistakes (poor accuracy ~20%)
        for i in range(10):
            user.history.append(
                ExerciseRecord(
                    timestamp=now - 200 + i * 10,
                    category="leitura_pauta",
                    question_type="staff_note",
                    is_correct=(i < 2),  # only 2 correct
                    prompt="Nota na pauta?",
                    user_answer="Ré",
                    correct_answer="Sol",
                )
            )

        weak_areas = get_weak_areas(user)
        # Weakest area MUST be leitura_pauta
        weakest_cat, acc = weak_areas[0]
        self.assertEqual(weakest_cat, "leitura_pauta")
        self.assertLess(acc, 50.0)

        # Recommendation should point directly to sheet music reading
        rec = get_recommendation(user)
        self.assertEqual(rec["category"], "leitura_pauta")
        self.assertEqual(rec["route"], "practice_staff")
        self.assertIn("Leitura de Pauta", rec["category_name"])

    def test_recency_decay_weighting(self):
        # User had 5 mistakes in theory long ago, but 5 recent successes
        # vs 5 successes in ear training long ago, but 5 recent mistakes
        now = time.time()
        user = UserProfile(username="Dinamico", avatar="🎧")

        # Old theory mistakes, recent theory correct
        for i in range(5):
            user.history.append(
                ExerciseRecord(
                    timestamp=now - 1000 + i * 10,
                    category="teoria",
                    question_type="theory_scale",
                    is_correct=False,
                    prompt="q",
                    user_answer="a",
                    correct_answer="b",
                )
            )
        for i in range(5):
            user.history.append(
                ExerciseRecord(
                    timestamp=now - 100 + i * 10,
                    category="teoria",
                    question_type="theory_scale",
                    is_correct=True,
                    prompt="q",
                    user_answer="b",
                    correct_answer="b",
                )
            )

        # Old ear correct, recent ear mistakes
        for i in range(5):
            user.history.append(
                ExerciseRecord(
                    timestamp=now - 1000 + i * 10,
                    category="treino_auditivo",
                    question_type="ear_interval",
                    is_correct=True,
                    prompt="q",
                    user_answer="b",
                    correct_answer="b",
                )
            )
        for i in range(5):
            user.history.append(
                ExerciseRecord(
                    timestamp=now - 100 + i * 10,
                    category="treino_auditivo",
                    question_type="ear_interval",
                    is_correct=False,
                    prompt="q",
                    user_answer="a",
                    correct_answer="b",
                )
            )

        weak_areas = get_weak_areas(user)
        dict_acc = dict(weak_areas)
        # Because ear training mistakes are more recent, its weighted accuracy must be lower than theory
        self.assertLess(dict_acc["treino_auditivo"], dict_acc["teoria"])

    def test_generate_adaptive_question(self):
        user = UserProfile(username="Praticante", avatar="🌟")
        q = generate_adaptive_question(user, difficulty="intermediate")
        self.assertIsInstance(q, QuizQuestion)
        self.assertTrue(len(q.options) >= 2)

    def test_adaptive_question_distribution_tends_to_weak_area(self):
        # Create a user with heavy mistakes in sight reading (leitura_pauta)
        now = time.time()
        user = UserProfile(username="Aluno", avatar="🎹")
        for i in range(15):
            user.history.append(
                ExerciseRecord(
                    timestamp=now - 200 + i * 5,
                    category="leitura_pauta",
                    question_type="staff_note",
                    is_correct=False,
                    prompt="Nota?",
                    user_answer="Dó",
                    correct_answer="Sol",
                )
            )
        for i in range(15):
            user.history.append(
                ExerciseRecord(
                    timestamp=now - 200 + i * 5,
                    category="treino_auditivo",
                    question_type="ear_interval",
                    is_correct=True,
                    prompt="Intervalo?",
                    user_answer="5ª",
                    correct_answer="5ª",
                )
            )

        # Generate 40 questions and count category occurrences
        cat_counts = {}
        for _ in range(40):
            q = generate_adaptive_question(user, difficulty="intermediate")
            cat_counts[q.category] = cat_counts.get(q.category, 0) + 1

        # The weakest area (leitura_pauta) should be generated significantly more often (around 60% of times)
        self.assertGreater(cat_counts.get("leitura_pauta", 0), cat_counts.get("teoria", 0))
        self.assertGreaterEqual(cat_counts.get("leitura_pauta", 0), 15)


if __name__ == "__main__":
    unittest.main()
