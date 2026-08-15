import unittest
from core.theory_content import THEORY_CHAPTERS

class TestTheoryI18n(unittest.TestCase):
    def test_all_chapters_have_en_fields(self):
        self.assertEqual(len(THEORY_CHAPTERS), 12, "Should have 12 chapters")
        for chap in THEORY_CHAPTERS:
            self.assertTrue(chap.title_en, f"Chapter {chap.id} missing title_en")
            self.assertTrue(chap.subtitle_en, f"Chapter {chap.id} missing subtitle_en")
            self.assertTrue(chap.summary_en, f"Chapter {chap.id} missing summary_en")
            self.assertTrue(chap.content_markdown_en, f"Chapter {chap.id} missing content_markdown_en")
            self.assertTrue(chap.piano_focus_en, f"Chapter {chap.id} missing piano_focus_en")
            self.assertTrue(chap.guitar_focus_en, f"Chapter {chap.id} missing guitar_focus_en")

    def test_getters_return_correct_language(self):
        chap1 = THEORY_CHAPTERS[0]
        # PT getters
        self.assertEqual(chap1.get_title("pt"), chap1.title)
        self.assertEqual(chap1.get_summary("pt"), chap1.summary)
        
        # EN getters
        self.assertEqual(chap1.get_title("en"), chap1.title_en)
        self.assertEqual(chap1.get_summary("en"), chap1.summary_en)
        self.assertIn("Western Music", chap1.get_content_markdown("en"))
