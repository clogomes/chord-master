"""Unit tests for progress export and student report generation."""
import os
import tempfile
import unittest
from core.user_manager import UserProfile, CategoryStats
from core.exporter import generate_student_report_markdown, export_student_report_file


class TestExporter(unittest.TestCase):

    def test_generate_student_report_markdown(self):
        user = UserProfile(
            username="Ana",
            avatar="🎹",
            xp=450,
            completed_lessons=["chap1_fundamentals", "chap2_intervals"],
            unlocked_achievements=["first_step"],
        )
        md = generate_student_report_markdown(user)
        self.assertIn("Ana", md)
        self.assertIn("450 XP", md)
        self.assertIn("Fundamentos da Música", md)
        self.assertIn("Primeiro Passo", md)

    def test_export_student_report_file(self):
        user = UserProfile(
            username="Beatriz",
            avatar="🎵",
            xp=150,
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            path = export_student_report_file(user, export_dir=tmpdir)
            self.assertTrue(os.path.exists(path))
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
                self.assertIn("Beatriz", content)


if __name__ == "__main__":
    unittest.main()
