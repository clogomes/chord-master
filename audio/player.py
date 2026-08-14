"""Asynchronous audio player engine with thread-safe playback and sound caching."""
import io
import os
import queue
import subprocess
import sys
import tempfile
import threading
import time
from typing import Any, Dict, List, Optional
from core.notes import Note
from .synthesizer import Synthesizer

try:
    import pygame
    HAS_PYGAME = True
except ImportError:
    HAS_PYGAME = False


class AudioPlayer:
    """Non-blocking audio engine for desktop music playback."""

    _instance: Optional["AudioPlayer"] = None

    def __init__(self):
        self._sound_cache: Dict[str, Any] = {}
        self._is_initialized = False
        self._playback_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._init_mixer()

    @classmethod
    def get_instance(cls) -> "AudioPlayer":
        if cls._instance is None:
            cls._instance = AudioPlayer()
        return cls._instance

    def _init_mixer(self):
        """Initializes the pygame audio mixer with low latency."""
        if HAS_PYGAME and not pygame.mixer.get_init():
            try:
                # Pre-init mixer settings
                pygame.mixer.pre_init(
                    frequency=Synthesizer.SAMPLE_RATE,
                    size=-16,
                    channels=2,
                    buffer=1024
                )
                pygame.mixer.init()
                pygame.mixer.set_num_channels(16)
                self._is_initialized = True
            except Exception as e:
                print(f"[AudioPlayer] Pygame mixer init error: {e}. Falling back to system playback.")
                self._is_initialized = False
        elif HAS_PYGAME and pygame.mixer.get_init():
            self._is_initialized = True

    def _get_or_create_sound(self, wav_bytes: bytes, cache_key: str):
        """Returns a cached pygame Sound object or creates a new one."""
        if cache_key in self._sound_cache:
            return self._sound_cache[cache_key]

        if self._is_initialized and HAS_PYGAME:
            try:
                sound_file = io.BytesIO(wav_bytes)
                sound = pygame.mixer.Sound(sound_file)
                self._sound_cache[cache_key] = sound
                return sound
            except Exception as e:
                print(f"[AudioPlayer] Error creating sound from bytes: {e}")
        return wav_bytes

    def play_note(self, note: Note, duration: float = 0.7, volume: float = 0.5):
        """Plays a single musical note asynchronously."""
        def _play_worker():
            cache_key = f"note_{note.midi}_{duration}_{volume}"
            if cache_key not in self._sound_cache:
                wav_bytes = Synthesizer.generate_single_frequency(note.frequency, duration, volume)
                sound_obj = self._get_or_create_sound(wav_bytes, cache_key)
            else:
                sound_obj = self._sound_cache[cache_key]

            self._play_sound_object(sound_obj, duration)

        threading.Thread(target=_play_worker, daemon=True).start()

    def play_chord(self, notes: List[Note], duration: float = 1.3, volume: float = 0.5):
        """Plays multiple notes simultaneously as a block chord or harmonic interval."""
        if not notes:
            return

        def _play_worker():
            midi_key = "_".join(str(n.midi) for n in sorted(notes, key=lambda x: x.midi))
            cache_key = f"chord_{midi_key}_{duration}_{volume}"

            if cache_key not in self._sound_cache:
                freqs = [n.frequency for n in notes]
                wav_bytes = Synthesizer.generate_polyphonic(freqs, duration, volume)
                sound_obj = self._get_or_create_sound(wav_bytes, cache_key)
            else:
                sound_obj = self._sound_cache[cache_key]

            self._play_sound_object(sound_obj, duration)

        threading.Thread(target=_play_worker, daemon=True).start()

    def play_sequence(
        self,
        notes: List[Note],
        delay_between: float = 0.35,
        note_duration: float = 0.6,
        volume: float = 0.5,
    ):
        """Plays a sequence of notes one after the other (scales, arpeggios, melodic intervals)."""
        self.stop_all()
        self._stop_event.clear()

        def _sequence_worker():
            for i, note in enumerate(notes):
                if self._stop_event.is_set():
                    break
                self.play_note(note, duration=note_duration, volume=volume)
                time.sleep(delay_between)

        self._playback_thread = threading.Thread(target=_sequence_worker, daemon=True)
        self._playback_thread.start()

    def play_question(self, question, slow_mode: bool = False):
        """Plays the audio corresponding to a QuizQuestion according to its play mode."""
        delay = 0.6 if slow_mode else 0.35
        note_dur = 0.9 if slow_mode else 0.6

        if question.play_mode == "harmonic" or question.play_mode == "chord":
            self.play_chord(question.notes_to_play, duration=1.5 if slow_mode else 1.2)
        else:
            self.play_sequence(question.notes_to_play, delay_between=delay, note_duration=note_dur)

    def _play_sound_object(self, sound_obj, duration: float):
        """Handles low-level playback with fallback."""
        if self._is_initialized and HAS_PYGAME and isinstance(sound_obj, pygame.mixer.Sound):
            sound_obj.play()
        else:
            # Fallback for systems without pygame audio or raw bytes
            wav_bytes = sound_obj if isinstance(sound_obj, bytes) else None
            if wav_bytes:
                self._system_audio_fallback(wav_bytes)

    def _system_audio_fallback(self, wav_bytes: bytes):
        """Plays WAV audio via OS-native players when pygame is unavailable."""
        try:
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                f.write(wav_bytes)
                temp_path = f.name

            if sys.platform == "darwin":  # macOS
                subprocess.Popen(["afplay", temp_path])
            elif sys.platform.startswith("linux"):  # Linux
                subprocess.Popen(["aplay", temp_path])
            elif sys.platform == "win32":  # Windows
                import winsound
                winsound.PlaySound(temp_path, winsound.SND_FILENAME | winsound.SND_ASYNC)

            # Schedule temp file deletion
            def _cleanup():
                time.sleep(3.0)
                if os.path.exists(temp_path):
                    try:
                        os.remove(temp_path)
                    except Exception:
                        pass

            threading.Thread(target=_cleanup, daemon=True).start()
        except Exception as e:
            print(f"[AudioPlayer] System audio playback failed: {e}")

    def stop_all(self):
        """Stops all currently playing audio sequences and sounds."""
        self._stop_event.set()
        if self._is_initialized and HAS_PYGAME:
            try:
                pygame.mixer.stop()
            except Exception:
                pass


def get_audio_player() -> AudioPlayer:
    """Convenience getter for the AudioPlayer singleton."""
    return AudioPlayer.get_instance()
