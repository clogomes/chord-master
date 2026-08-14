"""Application screen views for ChordMaster."""
from .main_menu import MainMenuScreen
from .theory_screen import TheoryScreen
from .practice_ear import PracticeEarScreen
from .practice_staff import PracticeStaffScreen
from .practice_song import PracticeSongScreen
from .practice_instrument import PracticeInstrumentScreen
from .stats_screen import StatsScreen

__all__ = [
    "MainMenuScreen",
    "TheoryScreen",
    "PracticeEarScreen",
    "PracticeStaffScreen",
    "PracticeSongScreen",
    "PracticeInstrumentScreen",
    "StatsScreen",
]
