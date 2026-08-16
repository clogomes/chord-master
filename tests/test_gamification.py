"""Unit tests for gamification, XP progression, and achievements."""
import unittest
from core.gamification import (
    ACHIEVEMENT_LIBRARY,
    get_level_info,
    get_achievement_by_id,
    LEVEL_THRESHOLDS,
)
from core.user_manager import UserManager, UserProfile


class TestGamification(unittest.TestCase):

    def test_achievement_library_not_empty(self):
        self.assertGreaterEqual(len(ACHIEVEMENT_LIBRARY), 8)
        for ach in ACHIEVEMENT_LIBRARY:
            self.assertTrue(ach.id)
            self.assertTrue(ach.title)
            self.assertTrue(ach.description)
            self.assertGreater(ach.xp_reward, 0)

    def test_get_achievement_by_id(self):
        ach = get_achievement_by_id("first_step")
        self.assertIsNotNone(ach)
        self.assertEqual(ach.title, "Primeiro Passo")

        none_ach = get_achievement_by_id("non_existent_id")
        self.assertIsNone(none_ach)

    def test_level_progression(self):
        # Level 1 at 0 XP
        info1 = get_level_info(0)
        self.assertEqual(info1["level"], 1)
        self.assertEqual(info1["progress_pct"], 0.0)

        # Level 2 at 150 XP
        info2 = get_level_info(150)
        self.assertEqual(info2["level"], 2)

        # Level 3 at 400 XP
        info3 = get_level_info(400)
        self.assertEqual(info3["level"], 3)

    def test_user_manager_xp_and_achievements(self):
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tf:
            temp_path = tf.name

        try:
            um = UserManager(filepath=temp_path)
            user = um.current_user
            self.assertEqual(user.xp, 0)
            self.assertEqual(user.level, 1)

            # Award XP
            new_xp, leveled_up = um.add_xp(200)
            self.assertEqual(new_xp, 200)
            self.assertTrue(leveled_up)
            self.assertEqual(user.level, 2)

            # Complete lesson -> awards +100 XP and unlocks 'first_step' achievement
            um.mark_lesson_completed("chap1_fundamentals")
            self.assertIn("chap1_fundamentals", user.completed_lessons)
            self.assertIn("first_step", user.unlocked_achievements)
            self.assertGreaterEqual(user.xp, 400)  # 200 + 100 + 100 reward

        finally:
            import os
            if os.path.exists(temp_path):
                os.remove(temp_path)


if __name__ == "__main__":
    unittest.main()

    def test_new_context_achievements(self):
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tf:
            temp_path = tf.name

        try:
            um = UserManager(filepath=temp_path)
            user = um.current_user
            
            # test virtuoso_pianist
            unlocked = um.check_achievements({"song_id": "fur_elise", "accuracy": 95.0})
            self.assertTrue(any(a.id == "virtuoso_pianist" for a in unlocked))
            
            # test guitar_hero
            unlocked = um.check_achievements({"instrument": "guitar"})
            self.assertTrue(any(a.id == "guitar_hero" for a in unlocked))
            
            # test pitch_perfect
            unlocked = um.check_achievements({"min_cents": 2.0})
            self.assertTrue(any(a.id == "pitch_perfect" for a in unlocked))
            
            # test rhythm_master
            unlocked = um.check_achievements({"rhythm_score": 2500})
            self.assertTrue(any(a.id == "rhythm_master" for a in unlocked))
            
            # test that they are now in unlocked_achievements
            self.assertIn("virtuoso_pianist", user.unlocked_achievements)
            self.assertIn("guitar_hero", user.unlocked_achievements)
            self.assertIn("pitch_perfect", user.unlocked_achievements)
            self.assertIn("rhythm_master", user.unlocked_achievements)

        finally:
            import os
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def test_all_achievements_have_conditions(self):
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tf:
            temp_path = tf.name
        
        try:
            um = UserManager(filepath=temp_path)
            # simulate every possible condition
            um.current_user.completed_lessons = [str(i) for i in range(20)]
            um.current_user.categories["repertorio"].correct_count = 10
            um.current_user.categories["treino_auditivo"].best_streak = 10
            um.current_user.categories["leitura_pauta"].best_streak = 10
            um.current_user.best_streak = 20
            um.current_user.total_attempts = 100
            
            context = {
                "song_id": "fur_elise",
                "accuracy": 100.0,
                "instrument": "guitar",
                "min_cents": 0.0,
                "rhythm_score": 5000,
            }
            
            unlocked = um.check_achievements(context)
            unlocked_ids = set(user.unlocked_achievements)
            
            for ach in ACHIEVEMENT_LIBRARY:
                self.assertIn(ach.id, unlocked_ids, f"Achievement {ach.id} could not be unlocked")

        finally:
            import os
            if os.path.exists(temp_path):
                os.remove(temp_path)
