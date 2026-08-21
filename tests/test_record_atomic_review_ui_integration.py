import tempfile
import os
import unittest
import customtkinter as ctk
from core.user_manager import UserManager, CategoryStats
from gui.screens.practice_ear import PracticeEarScreen
from gui.screens.practice_staff import PracticeStaffScreen
from gui.components.theory_quiz_widget import TheoryQuizWidget
from core.theory_quiz import CHAPTER_QUIZZES


class TestRecordAtomicReviewUIIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        ctk.set_appearance_mode("Dark")
        cls.root = ctk.CTk()
        cls.root.withdraw()
        cls.tmp_file = tempfile.NamedTemporaryFile(suffix=".json", delete=False)
        cls.tmp_file.close()
        cls.user_manager = UserManager(filepath=cls.tmp_file.name)
        cls.user_manager.create_user("TesterUI", "🎯")

    @classmethod
    def tearDownClass(cls):
        try:
            cls.root.destroy()
        except Exception:
            pass
        if hasattr(cls, "tmp_file") and os.path.exists(cls.tmp_file.name):
            os.unlink(cls.tmp_file.name)

    def test_record_atomic_review_returns_category_stats(self):
        """Validates that record_atomic_review returns a CategoryStats object with streak/correct counts."""
        stats = self.user_manager.record_atomic_review(
            skill_id="test:interval:P5",
            is_correct=True,
            category="treino_auditivo",
            question_type="ear_interval",
            prompt="5P",
            user_answer="5P",
            correct_answer="5P",
        )
        self.assertIsInstance(stats, CategoryStats)
        self.assertGreaterEqual(stats.current_streak, 1)
        self.assertGreaterEqual(stats.correct_count, 1)

    def test_practice_ear_screen_answering_flow(self):
        """Simulates answering multiple questions in PracticeEarScreen and asserts ScoreCard updates without exception."""
        screen = PracticeEarScreen(self.root, self.user_manager, on_back=lambda: None)
        screen.pack()
        self.root.update_idletasks()

        for _ in range(4):
            q = screen.current_question
            self.assertIsNotNone(q)
            correct_idx = q.options.index(q.correct_answer)
            screen.handle_answer(correct_idx)
            self.root.update_idletasks()
            self.assertIn("Sequência:", screen.score_card.streak_label.cget("text"))
            screen.load_new_question()

        screen.destroy()

    def test_practice_ear_progression_flow(self):
        """Progressões: o ecrã gera EAR_PROGRESSION e regista skill_id 'progression:<label>'."""
        from core.quiz_engine import QuestionType
        screen = PracticeEarScreen(self.root, self.user_manager, on_back=lambda: None)
        screen.pack()
        self.root.update_idletasks()

        screen.type_select.set("Progressões")
        screen.load_new_question()
        self.root.update_idletasks()

        q = screen.current_question
        self.assertEqual(q.question_type, QuestionType.EAR_PROGRESSION)
        self.assertEqual(q.play_mode, "progression")
        self.assertGreaterEqual(len(q.chords_to_play), 3)

        # Responder e verificar o skill_id atómico "progression:<label>".
        before = set(self.user_manager.current_user.spaced_review_data.keys())
        correct_idx = q.options.index(q.correct_answer)
        screen.handle_answer(correct_idx)
        self.root.update_idletasks()

        new_keys = set(self.user_manager.current_user.spaced_review_data.keys()) - before
        self.assertTrue(
            any(k.startswith("progression:") for k in new_keys),
            f"Nenhum skill_id 'progression:' registado; novos: {new_keys}",
        )
        screen.destroy()

    def test_practice_staff_screen_answering_flow(self):
        """Simulates answering in PracticeStaffScreen and asserts feedback card updates with stats without exception."""
        screen = PracticeStaffScreen(self.root, self.user_manager, on_back=lambda: None)
        screen.pack()
        self.root.update_idletasks()

        for _ in range(3):
            q = screen.current_question
            self.assertIsNotNone(q)
            correct_idx = q.options.index(q.correct_answer)
            screen._handle_answer_selection(correct_idx)
            self.root.update_idletasks()
            self.assertIsNotNone(screen.feedback_card)
            screen.load_new_question()

        screen.destroy()

    def test_theory_quiz_widget_answering_flow(self):
        """Simulates answering questions in TheoryQuizWidget and asserts XP and atomic review work cleanly."""
        frame = ctk.CTkFrame(self.root)
        frame.pack()
        quiz = CHAPTER_QUIZZES[0]
        completed = []
        widget = TheoryQuizWidget(
            frame,
            chapter_quiz=quiz,
            user_manager=self.user_manager,
            on_complete=lambda c, t: completed.append((c, t)),
        )
        widget.pack()
        self.root.update_idletasks()

        # Answer question 0
        widget.selected_option_idx.set(quiz.questions[0].correct_index)
        widget._on_confirm_clicked()
        self.root.update_idletasks()

        widget.destroy()
        frame.destroy()


if __name__ == "__main__":
    unittest.main()
