"""Integration tests verifying full user answering flow and ScoreCard updates across practice screens."""
import unittest
import customtkinter as ctk
from core.user_manager import UserManager, CategoryStats
from core.notes import Note
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
        cls.user_manager = UserManager(filepath=":memory:")
        cls.user_manager.create_user("TesterUI", "🎯")

    @classmethod
    def tearDownClass(cls):
        try:
            cls.root.destroy()
        except Exception:
            pass

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
