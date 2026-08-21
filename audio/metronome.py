"""Thread-safe audio metronome with synthesized acoustic woodblock clicks and rhythm timing evaluator."""
import threading
import time
from typing import Callable, Optional, Tuple, Any
import numpy as np
from audio.player import HAS_PYGAME

try:
    import pygame
except ImportError:
    pass


class Metronome:
    """
    Precision auditory and visual metronome supporting time signatures (2/4, 3/4, 4/4, 6/8)
    and adjustable tempo (40 - 220 BPM).
    """

    def __init__(
        self,
        bpm: int = 100,
        beats_per_measure: int = 4,
        on_beat: Optional[Callable[[int, float], None]] = None,
    ):
        self.bpm = max(40, min(240, bpm))
        self.beats_per_measure = beats_per_measure
        self.on_beat = on_beat

        self._is_running = False
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._lock = threading.Lock()

        self._click_high: Optional[Any] = None
        self._click_low: Optional[Any] = None
        self._generate_click_sounds()

    def _generate_click_sounds(self):
        """Synthesizes high and low woodblock clicks for the metronome."""
        if not HAS_PYGAME or not pygame.mixer.get_init():
            return

        sr = 44100
        dur = 0.035  # 35 ms short click
        t = np.linspace(0, dur, int(sr * dur), endpoint=False)
        envelope = np.exp(-t * 90.0)

        # High click (1200 Hz downbeat)
        high_wave = (0.75 * np.sin(2.0 * np.pi * 1200.0 * t) * envelope).astype(np.float32)
        high_stereo = np.column_stack((high_wave, high_wave))
        high_int16 = (high_stereo * 32767).astype(np.int16)

        # Low click (800 Hz offbeats)
        low_wave = (0.60 * np.sin(2.0 * np.pi * 800.0 * t) * envelope).astype(np.float32)
        low_stereo = np.column_stack((low_wave, low_wave))
        low_int16 = (low_stereo * 32767).astype(np.int16)

        try:
            self._click_high = pygame.sndarray.make_sound(high_int16)
            self._click_low = pygame.sndarray.make_sound(low_int16)
        except Exception:
            pass

    @property
    def is_running(self) -> bool:
        return self._is_running

    def set_bpm(self, bpm: int):
        with self._lock:
            self.bpm = max(40, min(240, bpm))

    def set_beats_per_measure(self, beats: int):
        with self._lock:
            self.beats_per_measure = max(1, min(12, beats))

    def start(self):
        with self._lock:
            if self._is_running:
                return
            self._is_running = True
            self._stop_event.clear()
            self._thread = threading.Thread(target=self._run_loop, daemon=True)
            self._thread.start()

    def stop(self):
        with self._lock:
            if not self._is_running:
                return
            self._is_running = False
            self._stop_event.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=0.2)
        self._thread = None

    def _run_loop(self):
        current_beat = 1
        while not self._stop_event.is_set():
            beat_start = time.time()

            # Play click sound
            is_downbeat = (current_beat == 1)
            sound = self._click_high if is_downbeat else self._click_low
            if sound is not None:
                try:
                    sound.play()
                except Exception:
                    pass

            # Invoke callback
            if self.on_beat is not None:
                try:
                    self.on_beat(current_beat, beat_start)
                except Exception as exc:
                    import logging
                    logging.warning(f"Erro no callback do metrónomo: {exc}")

            # Advance beat
            current_beat = (current_beat % self.beats_per_measure) + 1

            # Sleep accurately until next beat
            beat_interval = 60.0 / float(self.bpm)
            elapsed = time.time() - beat_start
            sleep_time = max(0.001, beat_interval - elapsed)

            if self._stop_event.wait(timeout=sleep_time):
                break


def evaluate_rhythm_accuracy(
    expected_timestamp: float,
    actual_timestamp: float,
    perfect_ms: float = 95.0,
    good_ms: float = 220.0,
) -> Tuple[str, float, int]:
    """
    Evaluates timing accuracy of a musical note press relative to expected beat.

    Args:
        expected_timestamp: momento esperado (referência time.time()).
        actual_timestamp: momento em que a batida/nota aconteceu.
        perfect_ms: |desvio| máximo (ms) para "PERFEITO" (omissão 95).
        good_ms: |desvio| máximo (ms) para "BOM" (omissão 220).

    Returns:
        (rating_label, delta_ms, points)
        Ratings: "PERFEITO ⭐", "BOM 👍", "FORA DE TEMPO ⚠️"

    Nota: os valores por omissão (95/220) preservam o comportamento dos ecrãs
    onde a batida é ao tocar uma nota (repertório, escalas, instrumento), onde
    alguma tolerância faz sentido. O ecrã de prática rítmica passa limiares
    estritos (ver practice_rhythm.py).
    """
    delta_sec = abs(actual_timestamp - expected_timestamp)
    delta_ms = delta_sec * 1000.0

    if delta_ms <= perfect_ms:
        return "PERFEITO ⭐", delta_ms, 50
    elif delta_ms <= good_ms:
        return "BOM 👍", delta_ms, 25
    else:
        return "FORA DE TEMPO ⚠️", delta_ms, 10
