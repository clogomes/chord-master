"""Application screen views for ChordMaster."""
from .main_menu import MainMenuScreen
from .theory_screen import TheoryScreen
from .practice_ear import PracticeEarScreen
from .practice_staff import PracticeStaffScreen
from .practice_song import PracticeSongScreen
from .practice_scales import PracticeScalesScreen
from .practice_instrument import PracticeInstrumentScreen
from .tuner_screen import LamireScreen
from .stats_screen import StatsScreen

from .practice_technique import PracticeTechniqueScreen
from .compose_studio import ComposeStudioScreen

__all__ = [
    "MainMenuScreen",
    "TheoryScreen",
    "PracticeEarScreen",
    "PracticeStaffScreen",
    "PracticeSongScreen",
    "PracticeScalesScreen",
    "PracticeInstrumentScreen",
    "PracticeTechniqueScreen",
    "LamireScreen",
    "StatsScreen",
    "ComposeStudioScreen",
]
