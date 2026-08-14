"""Unit tests for multi-user profiles and lesson progress management."""
import os
import tempfile
import unittest
from core.user_manager import UserManager, UserProfile


class TestUserManager(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(suffix=".json", delete=False)
        self.tmp_path = self.tmp.name
        self.tmp.close()

    def tearDown(self):
        if os.path.exists(self.tmp_path):
            os.remove(self.tmp_path)

    def test_default_user_creation(self):
        manager = UserManager(filepath=self.tmp_path)
        self.assertEqual(len(manager.get_all_users()), 1)
        self.assertEqual(manager.current_user.username, "Utilizador 1")
        self.assertEqual(manager.current_user.avatar, "🎵")

    def test_create_and_switch_user(self):
        manager = UserManager(filepath=self.tmp_path)
        u2 = manager.create_user("Maria", avatar="🎹")
        self.assertEqual(manager.active_username, "Maria")
        self.assertEqual(manager.current_user.avatar, "🎹")

        # Record attempt for Maria
        manager.record_attempt("treino_auditivo", "ear_interval", True)
        self.assertEqual(manager.current_user.total_correct, 1)

        # Switch back to Utilizador 1
        manager.switch_user("Utilizador 1")
        self.assertEqual(manager.current_user.username, "Utilizador 1")
        self.assertEqual(manager.current_user.total_correct, 0)

    def test_lesson_completion_tracking(self):
        manager = UserManager(filepath=self.tmp_path)
        self.assertFalse(manager.is_lesson_completed("chap1_fundamentals"))

        manager.mark_lesson_completed("chap1_fundamentals")
        self.assertTrue(manager.is_lesson_completed("chap1_fundamentals"))
        self.assertEqual(manager.current_user.lessons_progress_percent, 12.5)

        # Switch to another user and check lesson is not completed for them
        manager.create_user("João", avatar="🎸")
        self.assertFalse(manager.is_lesson_completed("chap1_fundamentals"))
        self.assertEqual(manager.current_user.lessons_progress_percent, 0.0)

    def test_delete_user(self):
        manager = UserManager(filepath=self.tmp_path)
        manager.create_user("Ana")
        self.assertEqual(len(manager.get_all_users()), 2)

        deleted = manager.delete_user("Ana")
        self.assertTrue(deleted)
        self.assertEqual(len(manager.get_all_users()), 1)

        # Cannot delete the only remaining user
        deleted_last = manager.delete_user("Utilizador 1")
        self.assertFalse(deleted_last)

    def test_persistence_reload(self):
        manager1 = UserManager(filepath=self.tmp_path)
        manager1.create_user("Sofia", avatar="🌟")
        manager1.mark_lesson_completed("chap2_intervals")
        manager1.record_attempt("leitura_pauta", "staff_note", True)

        # Reload in new instance
        manager2 = UserManager(filepath=self.tmp_path)
        self.assertEqual(manager2.active_username, "Sofia")
        self.assertTrue(manager2.is_lesson_completed("chap2_intervals"))
        self.assertEqual(manager2.current_user.total_correct, 1)


if __name__ == "__main__":
    unittest.main()
