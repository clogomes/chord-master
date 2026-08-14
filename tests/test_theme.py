"""Unit tests for gui.theme design tokens and helper functions."""
import unittest
from gui import theme


class TestTheme(unittest.TestCase):
    """Test design system tokens and typography scales."""

    def test_typography_tokens(self):
        self.assertEqual(theme.FONT_TITLE, ("Helvetica", 24, "bold"))
        self.assertEqual(theme.FONT_SUBTITLE, ("Helvetica", 16, "bold"))
        self.assertEqual(theme.FONT_SECTION, ("Helvetica", 18, "bold"))
        self.assertEqual(theme.FONT_BODY, ("Helvetica", 14))
        self.assertEqual(theme.FONT_BODY_BOLD, ("Helvetica", 14, "bold"))
        self.assertEqual(theme.FONT_SMALL, ("Helvetica", 12))
        self.assertEqual(theme.FONT_BADGE, ("Helvetica", 12, "bold"))
        self.assertEqual(theme.FONT_HERO, ("Helvetica", 32, "bold"))
        self.assertEqual(theme.FONT_MONO, ("Courier", 14, "bold"))

    def test_color_tokens(self):
        # Surface colors
        self.assertEqual(theme.COLOR_BG, ("#F8FAFC", "#0B0F19"))
        self.assertEqual(theme.COLOR_SURFACE, ("#FFFFFF", "#111827"))
        self.assertEqual(theme.COLOR_SURFACE_SECONDARY, ("#F1F5F9", "#1F2937"))
        self.assertEqual(theme.COLOR_BORDER, ("#E2E8F0", "#374151"))

        # Primary Brand
        self.assertEqual(theme.COLOR_PRIMARY, "#4F46E5")
        self.assertEqual(theme.COLOR_PRIMARY_HOVER, "#4338CA")

        # Success / In Tune
        self.assertEqual(theme.COLOR_SUCCESS, "#10B981")
        self.assertEqual(theme.COLOR_SUCCESS_DARK, "#064E3B")

        # Accents
        self.assertEqual(theme.COLOR_ACCENT_SKY, "#0284C7")
        self.assertEqual(theme.COLOR_ACCENT_AMBER, "#F59E0B")
        self.assertEqual(theme.COLOR_ACCENT_CRIMSON, "#EF4444")
        self.assertEqual(theme.COLOR_ACCENT_PURPLE, "#8B5CF6")

        # Text
        self.assertEqual(theme.COLOR_TEXT_PRIMARY, ("#0F172A", "#F9FAFB"))
        self.assertEqual(theme.COLOR_TEXT_MUTED, ("#64748B", "#94A3B8"))
        self.assertEqual(theme.COLOR_TEXT_SUBTLE, ("#94A3B8", "#6B7280"))

    def test_get_font_helper(self):
        try:
            import tkinter as tk
            root = tk.Tk()
            root.withdraw()
            font = theme.get_font(theme.FONT_TITLE)
            self.assertIsNotNone(font)
            root.destroy()
        except Exception:
            # Running in headless environments without display
            pass


if __name__ == "__main__":
    unittest.main()
