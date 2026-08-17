"""Comprehensive UI Smoke Test: Instantiates ChordMasterApp and EVERY screen and modal to prevent runtime constructor crashes."""
import os
import unittest
import customtkinter as ctk
from core.user_manager import UserManager
from core.songs import Song, SongNote
from gui.app import ChordMasterApp
from gui.screens.main_menu import MainMenuScreen
from gui.screens.theory_screen import TheoryScreen
from gui.screens.practice_song import PracticeSongScreen
from gui.screens.practice_scales import PracticeScalesScreen
from gui.screens.tuner_screen import LamireScreen
from gui.screens.practice_instrument import PracticeInstrumentScreen
from gui.screens.practice_technique import PracticeTechniqueScreen
from gui.screens.practice_ear import PracticeEarScreen
from gui.screens.practice_staff import PracticeStaffScreen
from gui.screens.stats_screen import StatsScreen
from gui.screens.glossary_screen import GlossaryScreen
from gui.screens.compose_studio import ComposeStudioScreen
from gui.screens.omr_review import OMRReviewScreen
from gui.components.user_modal import UserManagementModal
from gui.components.glossary_modal import GlossaryTermModal


class TestSmoke(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        ctk.set_appearance_mode("Dark")
        cls.root = ctk.CTk()
        cls.root.withdraw()
        cls.user_manager = UserManager()
        if not cls.user_manager.current_user:
            cls.user_manager.create_user("SmokeTestUser", "🎹")

    @classmethod
    def tearDownClass(cls):
        try:
            cls.root.destroy()
        except Exception:
            pass

    def test_app_instantiates_without_crash(self):
        """Validates ChordMasterApp shell startup and clean shutdown."""
        app = ChordMasterApp()
        app.update_idletasks()
        app.destroy()

    def test_all_screens_instantiate_cleanly(self):
        """Constructs every individual screen and confirms zero AttributeError / runtime crashes."""
        container = ctk.CTkFrame(self.root)
        container.pack()

        screens = [
            ("MainMenuScreen", lambda: MainMenuScreen(container, self.user_manager, lambda s: None)),
            ("TheoryScreen", lambda: TheoryScreen(container, self.user_manager, lambda: None)),
            ("PracticeSongScreen", lambda: PracticeSongScreen(container, self.user_manager, lambda: None)),
            ("PracticeScalesScreen", lambda: PracticeScalesScreen(container, self.user_manager, lambda: None)),
            ("LamireScreen", lambda: LamireScreen(container, lambda: None)),
            ("PracticeInstrumentScreen", lambda: PracticeInstrumentScreen(container, self.user_manager, lambda: None)),
            ("PracticeTechniqueScreen", lambda: PracticeTechniqueScreen(container, self.user_manager, lambda: None)),
            ("PracticeEarScreen", lambda: PracticeEarScreen(container, self.user_manager, lambda: None)),
            ("PracticeStaffScreen", lambda: PracticeStaffScreen(container, self.user_manager, lambda: None)),
            ("StatsScreen", lambda: StatsScreen(container, self.user_manager, lambda: None)),
            ("GlossaryScreen", lambda: GlossaryScreen(container, self.user_manager, lambda: None)),
            ("ComposeStudioScreen", lambda: ComposeStudioScreen(container, self.user_manager, lambda: None)),
        ]

        for screen_name, factory in screens:
            try:
                screen = factory()
                self.assertIsNotNone(screen, f"Screen {screen_name} returned None")
                screen.destroy()
            except Exception as e:
                self.fail(f"Screen {screen_name} failed during constructor initialization: {e}")

        # Test OMRReviewScreen with dummy draft song
        from core.notes import Note
        dummy_song = Song(
            id="draft_test",
            title="Partitura Teste",
            composer="Teste",
            difficulty="Iniciante",
            bpm=100,
            notes=[SongNote(note=Note("C4"), duration_beats=1.0)],
        )
        try:
            omr_screen = OMRReviewScreen(
                container,
                draft_song=dummy_song,
                original_filepath="",
                user_manager=self.user_manager,
                on_save=lambda s: None,
                on_cancel=lambda: None,
            )
            self.assertIsNotNone(omr_screen)
            omr_screen.destroy()
        except Exception as e:
            self.fail(f"OMRReviewScreen failed during initialization: {e}")

        container.destroy()

    def test_modals_instantiate_cleanly(self):
        """Constructs modal popups and ensures clean initialization."""
        try:
            user_modal = UserManagementModal(self.root, user_manager=self.user_manager)
            user_modal.destroy()
        except Exception as e:
            self.fail(f"UserManagementModal failed: {e}")

        try:
            gloss_modal = GlossaryTermModal(self.root, term_id="tritono")
            gloss_modal.destroy()
        except Exception as e:
            self.fail(f"GlossaryTermModal failed: {e}")


if __name__ == "__main__":
    unittest.main()
