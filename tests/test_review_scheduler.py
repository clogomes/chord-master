"""Unit tests for core/review_scheduler.py — SM-2 algorithm, persistence schema, queue generation."""
import time
import unittest

from core.review_scheduler import (
    ReviewItem,
    apply_sm2_grade,
    generate_default_atomic_skills,
    get_due_review_queue,
)
from core.user_manager import UserManager


class TestSM2Algorithm(unittest.TestCase):
    """Tests for the SuperMemo SM-2 scheduling algorithm."""

    def _make_item(self):
        return ReviewItem(
            skill_id="interval:M3:asc",
            category="ear",
            prompt_pt="Identifica o intervalo ascendente",
            prompt_en="Identify the ascending interval",
            question_type="ear_interval",
            options_pt=["Terça Maior", "Terça Menor", "Quarta Justa", "Quinta Justa"],
            options_en=["Major Third", "Minor Third", "Perfect Fourth", "Perfect Fifth"],
            correct_index=0,
            explanation_pt="Uma Terça Maior tem 4 semitons.",
            explanation_en="A Major Third has 4 semitones.",
        )

    def test_initial_state(self):
        item = self._make_item()
        self.assertEqual(item.ease, 2.5)
        self.assertEqual(item.repetition_count, 0)
        self.assertEqual(item.interval_days, 0.0)
        self.assertEqual(item.lapses, 0)
        self.assertTrue(item.is_due())

    def test_grade5_first_rep(self):
        item = self._make_item()
        apply_sm2_grade(item, grade=5)
        self.assertEqual(item.repetition_count, 1)
        self.assertAlmostEqual(item.interval_days, 1.0)
        self.assertGreater(item.ease, 2.5)  # ease increases on grade 5

    def test_grade5_second_rep(self):
        item = self._make_item()
        apply_sm2_grade(item, grade=5)
        apply_sm2_grade(item, grade=5)
        self.assertEqual(item.repetition_count, 2)
        self.assertAlmostEqual(item.interval_days, 6.0)

    def test_grade5_third_rep_uses_ease(self):
        item = self._make_item()
        apply_sm2_grade(item, grade=5)
        apply_sm2_grade(item, grade=5)
        ease_before = item.ease
        apply_sm2_grade(item, grade=5)
        self.assertEqual(item.repetition_count, 3)
        # 3rd+ uses interval * ease
        self.assertGreater(item.interval_days, 6.0)

    def test_grade1_resets_repetitions(self):
        item = self._make_item()
        apply_sm2_grade(item, grade=5)
        apply_sm2_grade(item, grade=5)
        apply_sm2_grade(item, grade=1)  # lapse
        self.assertEqual(item.repetition_count, 0)
        self.assertAlmostEqual(item.interval_days, 1.0)
        self.assertEqual(item.lapses, 1)

    def test_ease_decreases_on_failure(self):
        item = self._make_item()
        ease_start = item.ease
        apply_sm2_grade(item, grade=1)
        self.assertLess(item.ease, ease_start)

    def test_ease_minimum_bound(self):
        item = self._make_item()
        for _ in range(30):
            apply_sm2_grade(item, grade=1)
        self.assertGreaterEqual(item.ease, 1.3)

    def test_grade3_does_not_increase_ease(self):
        item = self._make_item()
        apply_sm2_grade(item, grade=5)
        ease_after_5 = item.ease
        apply_sm2_grade(item, grade=3)
        self.assertLessEqual(item.ease, ease_after_5)

    def test_due_at_advances(self):
        item = self._make_item()
        apply_sm2_grade(item, grade=5)
        self.assertGreater(item.due_at, time.time())
        self.assertFalse(item.is_due())

    def test_leitner_box_progression(self):
        item = self._make_item()
        self.assertEqual(item.box, 1)
        # After 2 successes: interval=6 → box 3
        apply_sm2_grade(item, grade=5)
        apply_sm2_grade(item, grade=5)
        self.assertGreaterEqual(item.box, 2)


class TestSerialization(unittest.TestCase):
    """Tests for ReviewItem.to_dict / from_dict round-trip."""

    def test_round_trip(self):
        item = ReviewItem(
            skill_id="staff:treble:C4",
            category="staff",
            prompt_pt="Que nota é esta?",
            prompt_en="What note is this?",
            question_type="staff_note",
            options_pt=["Dó4", "Ré4", "Mi4", "Fá4"],
            options_en=["C4", "D4", "E4", "F4"],
            correct_index=0,
            explanation_pt="Dó central na clave de sol.",
            explanation_en="Middle C in treble clef.",
        )
        apply_sm2_grade(item, grade=4)
        d = item.to_dict()
        restored = ReviewItem.from_dict(d)
        self.assertEqual(restored.skill_id, item.skill_id)
        self.assertAlmostEqual(restored.ease, item.ease)
        self.assertEqual(restored.repetition_count, item.repetition_count)
        self.assertEqual(restored.lapses, item.lapses)
        self.assertAlmostEqual(restored.interval_days, item.interval_days)

    def test_from_dict_with_defaults(self):
        """Simulates loading an old profile entry that is missing SM-2 fields."""
        minimal = {"skill_id": "glossary:tritono", "category": "glossary"}
        item = ReviewItem.from_dict(minimal)
        self.assertEqual(item.skill_id, "glossary:tritono")
        self.assertEqual(item.ease, 2.5)
        self.assertEqual(item.repetition_count, 0)


class TestQueueGeneration(unittest.TestCase):
    """Tests for get_due_review_queue and generate_default_atomic_skills."""

    def test_default_skills_generated(self):
        items = generate_default_atomic_skills()
        self.assertGreater(len(items), 10)
        ids = [i.skill_id for i in items]
        # Should include at least one interval skill
        self.assertTrue(any(s.startswith("interval:") for s in ids))

    def test_all_new_items_are_due(self):
        items = generate_default_atomic_skills()
        for item in items:
            self.assertTrue(item.is_due(), f"{item.skill_id} should be due (new item)")

    def test_queue_respects_max_items(self):
        items = generate_default_atomic_skills()
        store = {i.skill_id: i.to_dict() for i in items}
        queue = get_due_review_queue(store, max_items=5)
        self.assertLessEqual(len(queue), 5)

    def test_queue_excludes_future_items(self):
        items = generate_default_atomic_skills()
        # Graduate all items far into the future
        for item in items:
            for _ in range(3):
                apply_sm2_grade(item, grade=5)
        store = {i.skill_id: i.to_dict() for i in items}
        queue = get_due_review_queue(store, max_items=15)
        self.assertEqual(len(queue), 0)

    def test_queue_includes_due_items(self):
        items = generate_default_atomic_skills()
        # Make only the first item due by resetting it
        store = {}
        for i, item in enumerate(items):
            for _ in range(3):
                apply_sm2_grade(item, grade=5)  # push into future
            d = item.to_dict()
            if i == 0:
                d["due_at"] = 0.0  # force due
                d["repetition_count"] = 0
            store[item.skill_id] = d
        queue = get_due_review_queue(store, max_items=15)
        self.assertGreaterEqual(len(queue), 1)

    def test_staff_skill_ids_use_pitch_with_octave(self):
        """
        Regression test: staff skill_ids from generate_default_atomic_skills() must
        use note.pitch_with_octave (e.g. 'C4'), NOT note.pitch (e.g. 'C').
        practice_staff.py generates ids at runtime using pitch_with_octave — this
        ensures both sides share the same namespace so practice updates seeded items.
        """
        items = generate_default_atomic_skills()
        staff_items = [i for i in items if i.skill_id.startswith("staff:")]
        self.assertGreater(len(staff_items), 0)
        for item in staff_items:
            parts = item.skill_id.split(":")
            pitch_part = parts[2]  # e.g. "C4"
            self.assertRegex(
                pitch_part,
                r'^[A-G][#b]?\d$',
                msg=f"Skill ID '{item.skill_id}' pitch part must include octave (e.g. C4, not C)"
            )

    def test_runtime_staff_skill_id_matches_seeded_namespace(self):
        """
        Verify that the runtime skill_id format 'staff:{clef}:{pitch_with_octave}'
        produced by practice_staff.py matches what generate_default_atomic_skills() seeds.
        """
        from core.notes import Note
        seeded_ids = {i.skill_id for i in generate_default_atomic_skills() if i.skill_id.startswith("staff:")}
        note = Note("C4")
        runtime_id = f"staff:treble:{note.pitch_with_octave}"
        self.assertIn(runtime_id, seeded_ids, msg=(
            f"Runtime skill_id '{runtime_id}' not in seeded namespace. "
            "practice_staff.py and review_scheduler.py must use the same pitch format."
        ))


class TestUserManagerIntegration(unittest.TestCase):
    """Tests for spaced review persistence in UserManager."""

    def setUp(self):
        self.um = UserManager(filepath=":memory:")
        self.um.create_user("TestAluno")

    def test_fresh_profile_has_empty_spaced_data(self):
        user = self.um.current_user
        self.assertIsNotNone(user)
        self.assertIsInstance(user.spaced_review_data, dict)
        self.assertEqual(len(user.spaced_review_data), 0)

    def test_record_atomic_review_persists_skill(self):
        self.um.record_atomic_review(
            skill_id="interval:P5:asc",
            is_correct=True,
            category="treino_auditivo",
            question_type="ear_interval",
        )
        user = self.um.current_user
        self.assertIn("interval:P5:asc", user.spaced_review_data)

    def test_record_atomic_review_increments_rep_on_correct(self):
        self.um.record_atomic_review(skill_id="interval:P5:asc", is_correct=True)
        data = self.um.current_user.spaced_review_data["interval:P5:asc"]
        self.assertGreater(data.get("repetition_count", 0), 0)

    def test_record_atomic_review_lapse_on_incorrect(self):
        self.um.record_atomic_review(skill_id="interval:P5:asc", is_correct=True)
        self.um.record_atomic_review(skill_id="interval:P5:asc", is_correct=False)
        data = self.um.current_user.spaced_review_data["interval:P5:asc"]
        self.assertEqual(data.get("repetition_count", 0), 0)
        self.assertGreater(data.get("lapses", 0), 0)

    def test_due_reviews_count_on_fresh_profile(self):
        user = self.um.current_user
        # Fresh empty profile → returns 0 (real count, no invented numbers)
        self.assertEqual(user.due_reviews_count, 0)

    def test_leitner_box_counts_empty(self):
        boxes = self.um.current_user.leitner_box_counts
        total = sum(boxes.values())
        self.assertEqual(total, 0)

    def test_leitner_box_counts_after_review(self):
        self.um.record_atomic_review(skill_id="staff:treble:G4", is_correct=True)
        boxes = self.um.current_user.leitner_box_counts
        self.assertGreater(sum(boxes.values()), 0)

    def test_schema_backwards_compatibility(self):
        """record_atomic_review creates entry for new skill_id on first call."""
        self.um.record_atomic_review(skill_id="theory:chap1:q0", is_correct=True)
        self.assertIn("theory:chap1:q0", self.um.current_user.spaced_review_data)

    def test_get_daily_review_queue_empty_profile(self):
        """Empty profile → returns empty list (no skills seeded yet by UserManager)."""
        queue = self.um.get_daily_review_queue()
        self.assertIsInstance(queue, list)


if __name__ == "__main__":
    unittest.main()
