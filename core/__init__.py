"""Core music theory logic and state management."""
from .notes import Note, NOTE_NAMES, NOTE_NAMES_PT, midi_to_freq, note_to_midi, midi_to_note
from .intervals import Interval, INTERVALS, INTERVAL_NAMES_PT, get_interval, transpose_note
from .scales import Scale, SCALE_TYPES, get_scale_notes
from .chords import Chord, CHORD_TYPES, get_chord_notes
from .quiz_engine import QuizEngine, QuizQuestion, QuestionType
from .score_tracker import ScoreTracker
from .user_manager import UserManager, UserProfile, LESSON_IDS, AVATAR_CHOICES
from .fingering import get_chord_piano_fingering
from .guitar import GuitarChordShape, GuitarFretboardModel, GUITAR_CHORD_LIBRARY
from .songs import Song, SongNote, SONG_LIBRARY, get_song_by_id

__all__ = [
    "Note",
    "NOTE_NAMES",
    "NOTE_NAMES_PT",
    "midi_to_freq",
    "note_to_midi",
    "midi_to_note",
    "Interval",
    "INTERVALS",
    "INTERVAL_NAMES_PT",
    "get_interval",
    "transpose_note",
    "Scale",
    "SCALE_TYPES",
    "get_scale_notes",
    "Chord",
    "CHORD_TYPES",
    "get_chord_notes",
    "QuizEngine",
    "QuizQuestion",
    "QuestionType",
    "ScoreTracker",
    "UserManager",
    "UserProfile",
    "LESSON_IDS",
    "AVATAR_CHOICES",
]
