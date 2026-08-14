"""Audio synthesis and playback module for ChordMaster."""
from .synthesizer import Synthesizer
from .player import AudioPlayer, get_audio_player
from .pitch_listener import PitchListener, detect_pitch_from_samples
from .metronome import Metronome, evaluate_rhythm_accuracy
from .midi_manager import MidiManager, get_midi_manager

__all__ = [
    "Synthesizer",
    "AudioPlayer",
    "get_audio_player",
    "PitchListener",
    "detect_pitch_from_samples",
    "Metronome",
    "evaluate_rhythm_accuracy",
    "MidiManager",
    "get_midi_manager",
]
