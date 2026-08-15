import unittest
from core.theory_quiz import CHAPTER_QUIZZES
from core.theory_content import THEORY_CHAPTERS

class TestTheoryQuiz(unittest.TestCase):
    def test_quizzes_count(self):
        """Test that CHAPTER_QUIZZES has exactly the same number of entries as THEORY_CHAPTERS."""
        self.assertEqual(len(CHAPTER_QUIZZES), len(THEORY_CHAPTERS), "Number of quizzes must match number of chapters")

    def test_all_chapters_have_quiz(self):
        """Test that all 12 chapter ids have a corresponding quiz."""
        chapter_ids = {c.id for c in THEORY_CHAPTERS}
        quiz_ids = {q.chapter_id for q in CHAPTER_QUIZZES}
        self.assertEqual(chapter_ids, quiz_ids, "Every chapter must have a corresponding quiz")

    def test_five_questions_per_quiz(self):
        """Test each quiz has exactly 5 questions."""
        for quiz in CHAPTER_QUIZZES:
            self.assertEqual(len(quiz.questions), 5, f"Quiz for {quiz.chapter_id} must have exactly 5 questions")

    def test_four_options_per_question(self):
        """Test each question has exactly 4 options."""
        for quiz in CHAPTER_QUIZZES:
            for i, q in enumerate(quiz.questions):
                self.assertEqual(len(q.options), 4, f"Question {i} in {quiz.chapter_id} must have exactly 4 options")

    def test_correct_index_in_bounds(self):
        """Test correct_index is always between 0 and 3."""
        for quiz in CHAPTER_QUIZZES:
            for i, q in enumerate(quiz.questions):
                self.assertIn(q.correct_index, [0, 1, 2, 3], f"correct_index for Question {i} in {quiz.chapter_id} out of bounds")

    def test_question_not_empty(self):
        """Test that the question string is not empty."""
        for quiz in CHAPTER_QUIZZES:
            for q in quiz.questions:
                self.assertTrue(len(q.question.strip()) > 0, "Question string cannot be empty")

    def test_options_not_empty(self):
        """Test that no option string is empty."""
        for quiz in CHAPTER_QUIZZES:
            for q in quiz.questions:
                for opt in q.options:
                    self.assertTrue(len(opt.strip()) > 0, "Option string cannot be empty")

    def test_explanation_not_empty(self):
        """Test that explanation string is not empty."""
        for quiz in CHAPTER_QUIZZES:
            for q in quiz.questions:
                self.assertTrue(len(q.explanation.strip()) > 0, "Explanation string cannot be empty")

    def test_unique_options(self):
        """Test that the 4 options in each question are unique."""
        for quiz in CHAPTER_QUIZZES:
            for i, q in enumerate(quiz.questions):
                self.assertEqual(len(set(q.options)), len(q.options), f"Options must be unique in {quiz.chapter_id} question {i}")

    def test_correct_index_matches_option(self):
        """Test that correct_index actually points to a valid option string."""
        for quiz in CHAPTER_QUIZZES:
            for q in quiz.questions:
                self.assertIsInstance(q.options[q.correct_index], str)

if __name__ == '__main__':
    unittest.main()
