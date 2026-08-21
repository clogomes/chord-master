"""Automated static analysis test to ensure zero undefined names (F821) across all python modules."""
import os
import unittest

try:
    import pyflakes.api
    import pyflakes.messages
    import pyflakes.reporter
    HAS_PYFLAKES = True
except ImportError:
    HAS_PYFLAKES = False


class PyflakesErrorCollector(pyflakes.reporter.Reporter):
    def __init__(self):
        self.errors = []

    def unexpectedError(self, filename, msg):
        self.errors.append((filename, 0, f"Unexpected error: {msg}"))

    def syntaxError(self, filename, msg, lineno, offset, text):
        self.errors.append((filename, lineno, f"Syntax error: {msg}"))

    def flake(self, message):
        # We specifically target undefined names (F821 / UndefinedName)
        if isinstance(message, pyflakes.messages.UndefinedName):
            self.errors.append((message.filename, message.lineno, str(message)))


class TestNoUndefinedNames(unittest.TestCase):
    @unittest.skipUnless(HAS_PYFLAKES, "pyflakes is required for undefined name static verification")
    def test_no_undefined_names_across_codebase(self):
        """Scans audio, core, gui, tests, and main.py for any undefined variable/import names."""
        repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        targets = ["audio", "core", "gui", "tests", "main.py"]
        
        collector = PyflakesErrorCollector()
        py_files_checked = 0

        for target in targets:
            full_path = os.path.join(repo_root, target)
            if os.path.isfile(full_path) and full_path.endswith(".py"):
                pyflakes.api.checkPath(full_path, reporter=collector)
                py_files_checked += 1
            elif os.path.isdir(full_path):
                for root_dir, _, files in os.walk(full_path):
                    for file in files:
                        if file.endswith(".py"):
                            file_path = os.path.join(root_dir, file)
                            pyflakes.api.checkPath(file_path, reporter=collector)
                            py_files_checked += 1

        self.assertGreater(py_files_checked, 20, "Should have scanned at least 20 python files")

        if collector.errors:
            error_details = "\n".join(f"  {fn}:{ln}: {msg}" for fn, ln, msg in collector.errors)
            self.fail(f"Found {len(collector.errors)} undefined name(s) in codebase:\n{error_details}")


if __name__ == "__main__":
    unittest.main()
