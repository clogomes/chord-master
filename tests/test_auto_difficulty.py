"""Unit tests for the AutoDifficultyTracker."""
import unittest
from core.auto_difficulty import (
    AutoDifficultyTracker,
    DIFFICULTIES,
    MIN_ATTEMPTS_FOR_UP,
    UP_THRESHOLD,
    MIN_ATTEMPTS_FOR_DOWN,
    DOWN_THRESHOLD,
)


class TestAutoDifficultyTracker(unittest.TestCase):

    def test_initial_state(self):
        tracker = AutoDifficultyTracker()
        self.assertEqual(tracker.attempts, 0)
        self.assertEqual(tracker.correct, 0)
        self.assertEqual(tracker.accuracy, 0.0)
        self.assertFalse(tracker.should_level_up())
        self.assertFalse(tracker.should_level_down())

    def test_progress_text_initial(self):
        tracker = AutoDifficultyTracker()
        text = tracker.progress_text()
        self.assertIn("0/15", text)
        self.assertIn("85%", text)

    def test_record_correct(self):
        tracker = AutoDifficultyTracker()
        tracker.record(True)
        self.assertEqual(tracker.attempts, 1)
        self.assertEqual(tracker.correct, 1)
        self.assertEqual(tracker.accuracy, 1.0)

    def test_record_incorrect(self):
        tracker = AutoDifficultyTracker()
        tracker.record(False)
        self.assertEqual(tracker.attempts, 1)
        self.assertEqual(tracker.correct, 0)
        self.assertEqual(tracker.accuracy, 0.0)

    def test_no_level_up_before_min_attempts(self):
        tracker = AutoDifficultyTracker()
        for _ in range(MIN_ATTEMPTS_FOR_UP - 1):
            tracker.record(True)
        self.assertFalse(tracker.should_level_up())

    def test_level_up_at_threshold(self):
        tracker = AutoDifficultyTracker()
        for _ in range(MIN_ATTEMPTS_FOR_UP):
            tracker.record(True)
        self.assertTrue(tracker.should_level_up())

    def test_no_level_up_below_threshold(self):
        tracker = AutoDifficultyTracker()
        for _ in range(12):
            tracker.record(True)
        for _ in range(3):
            tracker.record(False)
        self.assertAlmostEqual(tracker.accuracy, 12 / 15)
        self.assertFalse(tracker.should_level_up())

    def test_level_up_with_one_miss(self):
        tracker = AutoDifficultyTracker()
        for _ in range(MIN_ATTEMPTS_FOR_UP - 1):
            tracker.record(True)
        tracker.record(False)
        acc = tracker.accuracy
        self.assertAlmostEqual(acc, (MIN_ATTEMPTS_FOR_UP - 1) / MIN_ATTEMPTS_FOR_UP)
        self.assertTrue(tracker.should_level_up())

    def test_no_level_down_before_min_attempts(self):
        tracker = AutoDifficultyTracker()
        for _ in range(MIN_ATTEMPTS_FOR_DOWN - 1):
            tracker.record(False)
        self.assertFalse(tracker.should_level_down())

    def test_level_down_below_threshold(self):
        tracker = AutoDifficultyTracker()
        for _ in range(MIN_ATTEMPTS_FOR_DOWN):
            tracker.record(False)
        self.assertTrue(tracker.should_level_down())

    def test_no_level_down_above_threshold(self):
        tracker = AutoDifficultyTracker()
        for _ in range(3):
            tracker.record(False)
        for _ in range(3):
            tracker.record(True)
        self.assertAlmostEqual(tracker.accuracy, 0.5)
        self.assertFalse(tracker.should_level_down())

    def test_level_down_at_exactly_50_percent(self):
        tracker = AutoDifficultyTracker()
        for _ in range(3):
            tracker.record(False)
        for _ in range(3):
            tracker.record(True)
        self.assertAlmostEqual(tracker.accuracy, 0.5)
        self.assertFalse(tracker.should_level_down())

    def test_level_down_below_50_percent(self):
        tracker = AutoDifficultyTracker()
        for _ in range(4):
            tracker.record(False)
        for _ in range(2):
            tracker.record(True)
        self.assertAlmostEqual(tracker.accuracy, 2 / 6)
        self.assertTrue(tracker.should_level_down())

    def test_reset(self):
        tracker = AutoDifficultyTracker()
        for _ in range(10):
            tracker.record(True)
        tracker.reset()
        self.assertEqual(tracker.attempts, 0)
        self.assertEqual(tracker.correct, 0)

    def test_next_difficulty_stays_same(self):
        tracker = AutoDifficultyTracker()
        for _ in range(5):
            tracker.record(True)
        self.assertEqual(tracker.next_difficulty("beginner"), "beginner")

    def test_next_difficulty_levels_up(self):
        tracker = AutoDifficultyTracker()
        for _ in range(MIN_ATTEMPTS_FOR_UP):
            tracker.record(True)
        self.assertEqual(tracker.next_difficulty("beginner"), "intermediate")
        self.assertEqual(tracker.next_difficulty("intermediate"), "advanced")

    def test_next_difficulty_stays_at_advanced(self):
        tracker = AutoDifficultyTracker()
        for _ in range(MIN_ATTEMPTS_FOR_UP):
            tracker.record(True)
        self.assertEqual(tracker.next_difficulty("advanced"), "advanced")

    def test_next_difficulty_levels_down(self):
        tracker = AutoDifficultyTracker()
        for _ in range(MIN_ATTEMPTS_FOR_DOWN):
            tracker.record(False)
        self.assertEqual(tracker.next_difficulty("advanced"), "intermediate")
        self.assertEqual(tracker.next_difficulty("intermediate"), "beginner")

    def test_next_difficulty_stays_at_beginner(self):
        tracker = AutoDifficultyTracker()
        for _ in range(MIN_ATTEMPTS_FOR_DOWN):
            tracker.record(False)
        self.assertEqual(tracker.next_difficulty("beginner"), "beginner")

    def test_progress_text_midway(self):
        tracker = AutoDifficultyTracker()
        for _ in range(12):
            tracker.record(True)
        for _ in range(3):
            tracker.record(False)
        text = tracker.progress_text()
        self.assertIn("15/15", text)
        self.assertIn("80%", text)

    def test_progress_text_ready_to_up(self):
        tracker = AutoDifficultyTracker()
        for _ in range(MIN_ATTEMPTS_FOR_UP):
            tracker.record(True)
        text = tracker.progress_text()
        self.assertIn("pronto para subir", text)

    def test_difficulties_list(self):
        self.assertEqual(DIFFICULTIES, ["beginner", "intermediate", "advanced"])

    def test_constants(self):
        self.assertEqual(MIN_ATTEMPTS_FOR_UP, 15)
        self.assertAlmostEqual(UP_THRESHOLD, 0.85)
        self.assertEqual(MIN_ATTEMPTS_FOR_DOWN, 5)
        self.assertAlmostEqual(DOWN_THRESHOLD, 0.50)


if __name__ == "__main__":
    unittest.main()
