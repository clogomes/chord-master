"""Static scan test ensuring that every 'theme.ATTRIBUTE' in the gui/ package exists in gui.theme."""
import os
import re
import unittest
from gui import theme


class TestThemeTokensStaticScan(unittest.TestCase):
    def test_all_theme_tokens_exist(self):
        """Scans all Python files in gui/ and asserts that all theme.* attribute references exist in gui.theme."""
        gui_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "gui")
        
        pattern = re.compile(r"\btheme\.([A-Za-z0-9_]+)\b")
        missing_tokens = []

        for root, _, files in os.walk(gui_dir):
            for file in files:
                if file.endswith(".py") and file != "theme.py":
                    filepath = os.path.join(root, file)
                    with open(filepath, "r", encoding="utf-8") as f:
                        for line_no, line in enumerate(f, start=1):
                            # Skip comments
                            stripped = line.strip()
                            if stripped.startswith("#"):
                                continue
                            
                            for match in pattern.finditer(line):
                                token_name = match.group(1)
                                if not hasattr(theme, token_name):
                                    rel_path = os.path.relpath(filepath, gui_dir)
                                    missing_tokens.append(f"{rel_path}:{line_no} -> theme.{token_name}")

        self.assertEqual(
            len(missing_tokens),
            0,
            f"Found {len(missing_tokens)} non-existent theme token references:\n" + "\n".join(missing_tokens)
        )


if __name__ == "__main__":
    unittest.main()
