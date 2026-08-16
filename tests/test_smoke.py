import unittest
import customtkinter as ctk
from gui.app import ChordMasterApp

class TestSmoke(unittest.TestCase):
    def test_app_instantiates_without_crash(self):
        # Should not raise any exceptions
        app = ChordMasterApp()
        app._on_close()
