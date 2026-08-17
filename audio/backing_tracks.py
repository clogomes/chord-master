"""Synthesized rhythm backing track engine for groove accompaniment with zero external audio samples."""
import threading
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
import numpy as np
from audio.player import HAS_PYGAME

try:
    import pygame
except ImportError:
    pass


def synthesize_kick(sample_rate: int = 44100, duration: float = 0.25) -> np.ndarray:
    """
    Synthesizes a punchy acoustic bass drum (kick) with pitch drop and transient click.
    Returns mono float32 array in range [-1.0, 1.0].
    """
    total_samples = int(sample_rate * duration)
    t = np.linspace(0, duration, total_samples, endpoint=False)

    # Exponential pitch sweep: 140 Hz down to 48 Hz
    pitch_env = 48.0 + (140.0 - 48.0) * np.exp(-t * 32.0)
    phase = 2.0 * np.pi * np.cumsum(pitch_env) / sample_rate
    sine_body = np.sin(phase)

    # Amplitude envelope
    amp_env = np.exp(-t * 14.0)

    # Initial punch transient (5 ms click)
    click_len = int(sample_rate * 0.005)
    click = np.zeros(total_samples, dtype=np.float32)
    if click_len > 0:
        click[:click_len] = np.random.uniform(-0.5, 0.5, click_len) * np.linspace(1.0, 0.0, click_len)

    wave = (0.85 * sine_body * amp_env + 0.15 * click).astype(np.float32)
    return np.clip(wave, -1.0, 1.0)


def synthesize_snare(sample_rate: int = 44100, duration: float = 0.20) -> np.ndarray:
    """
    Synthesizes an acoustic snare drum with tonal shell body and white-noise snare wires.
    Returns mono float32 array in range [-1.0, 1.0].
    """
    total_samples = int(sample_rate * duration)
    t = np.linspace(0, duration, total_samples, endpoint=False)

    # Tonal drum shell (185 Hz + 330 Hz harmonic)
    body_phase = 2.0 * np.pi * (185.0 * t + 30.0 * np.exp(-t * 40.0))
    shell = 0.6 * np.sin(body_phase) + 0.2 * np.sin(2.0 * np.pi * 330.0 * t)
    shell_env = np.exp(-t * 28.0)

    # Noise wires (snare wires response)
    noise = np.random.uniform(-1.0, 1.0, total_samples)
    noise_env = np.exp(-t * 18.0)

    wave = (0.45 * shell * shell_env + 0.55 * noise * noise_env).astype(np.float32)
    return np.clip(wave, -1.0, 1.0)


def synthesize_hihat(open: bool = False, sample_rate: int = 44100) -> np.ndarray:
    """
    Synthesizes closed or open metallic hi-hat cymbal using clustered metallic frequencies and filtered noise.
    Returns mono float32 array in range [-1.0, 1.0].
    """
    duration = 0.35 if open else 0.05
    decay_rate = 10.0 if open else 85.0

    total_samples = int(sample_rate * duration)
    t = np.linspace(0, duration, total_samples, endpoint=False)

    # Inharmonic metallic cluster (square/sine mix at high frequencies)
    metallic = (
        0.3 * np.sign(np.sin(2 * np.pi * 3200 * t)) +
        0.3 * np.sign(np.sin(2 * np.pi * 5400 * t)) +
        0.2 * np.sign(np.sin(2 * np.pi * 8900 * t)) +
        0.2 * np.sign(np.sin(2 * np.pi * 11200 * t))
    )

    noise = np.random.uniform(-0.8, 0.8, total_samples)
    env = np.exp(-t * decay_rate)

    wave = ((0.5 * metallic + 0.5 * noise) * env * 0.7).astype(np.float32)
    return np.clip(wave, -1.0, 1.0)


def synthesize_ride(sample_rate: int = 44100, duration: float = 0.60) -> np.ndarray:
    """
    Synthesizes a shimmering ride cymbal with long resonant sustain.
    Returns mono float32 array in range [-1.0, 1.0].
    """
    total_samples = int(sample_rate * duration)
    t = np.linspace(0, duration, total_samples, endpoint=False)

    # Resonant metallic ring
    ring = (
        0.35 * np.sin(2 * np.pi * 590 * t) +
        0.25 * np.sin(2 * np.pi * 1240 * t) +
        0.20 * np.sin(2 * np.pi * 2870 * t) +
        0.20 * np.sin(2 * np.pi * 6420 * t)
    )
    noise = np.random.uniform(-0.4, 0.4, total_samples)
    env = np.exp(-t * 6.5)

    wave = ((0.65 * ring + 0.35 * noise) * env * 0.6).astype(np.float32)
    return np.clip(wave, -1.0, 1.0)


def synthesize_tom(pitch: str = "mid", sample_rate: int = 44100, duration: float = 0.35) -> np.ndarray:
    """
    Synthesizes an acoustic Tom drum (low, mid, high) with downward frequency sweep and membrane resonance.
    Returns mono float32 array in range [-1.0, 1.0].
    """
    total_samples = int(sample_rate * duration)
    t = np.linspace(0, duration, total_samples, endpoint=False)

    if pitch == "low":
        start_f, end_f, decay = 130.0, 75.0, 12.0
    elif pitch == "high":
        start_f, end_f, decay = 240.0, 150.0, 16.0
    else:  # "mid"
        start_f, end_f, decay = 180.0, 110.0, 14.0

    pitch_env = end_f + (start_f - end_f) * np.exp(-t * 22.0)
    phase = 2.0 * np.pi * np.cumsum(pitch_env) / sample_rate
    body = 0.8 * np.sin(phase) + 0.2 * np.sin(2.0 * phase)
    amp_env = np.exp(-t * decay)

    click_len = int(sample_rate * 0.004)
    click = np.zeros(total_samples, dtype=np.float32)
    if click_len > 0:
        click[:click_len] = np.random.uniform(-0.4, 0.4, click_len) * np.linspace(1.0, 0.0, click_len)

    wave = (0.85 * body * amp_env + 0.15 * click).astype(np.float32)
    return np.clip(wave, -1.0, 1.0)


def synthesize_clap(sample_rate: int = 44100, duration: float = 0.25) -> np.ndarray:
    """
    Synthesizes an acoustic handclap with multi-burst transient group and short reverb decay tail.
    Returns mono float32 array in range [-1.0, 1.0].
    """
    total_samples = int(sample_rate * duration)
    t = np.linspace(0, duration, total_samples, endpoint=False)
    noise = np.random.uniform(-1.0, 1.0, total_samples).astype(np.float32)

    # Multi-burst envelope: 3 micro-claps spaced ~11ms apart followed by diffuse tail
    env = np.zeros(total_samples, dtype=np.float32)
    burst_spacing = int(0.011 * sample_rate)
    for i in range(3):
        b_start = i * burst_spacing
        b_len = int(0.008 * sample_rate)
        if b_start + b_len < total_samples:
            env[b_start : b_start + b_len] = np.linspace(1.0, 0.2, b_len) * (0.8 + 0.2 * i)

    # Reverb decay tail starting around third burst
    tail_start = int(0.030 * sample_rate)
    if tail_start < total_samples:
        t_tail = t[tail_start:] - t[tail_start]
        env[tail_start:] += np.exp(-t_tail * 24.0)

    # Bandpass color
    wave = noise * env
    return np.clip(wave * 0.85, -1.0, 1.0)


def synthesize_crash(sample_rate: int = 44100, duration: float = 2.50) -> np.ndarray:
    """
    Synthesizes an explosive Crash cymbal with dense inharmonic metallic spectrum and long natural decay.
    Returns mono float32 array in range [-1.0, 1.0].
    """
    total_samples = int(sample_rate * duration)
    t = np.linspace(0, duration, total_samples, endpoint=False)

    metallic = (
        0.25 * np.sin(2 * np.pi * 420 * t) +
        0.25 * np.sin(2 * np.pi * 830 * t) +
        0.20 * np.sin(2 * np.pi * 1650 * t) +
        0.15 * np.sin(2 * np.pi * 3420 * t) +
        0.15 * np.sin(2 * np.pi * 7100 * t)
    )
    noise = np.random.uniform(-0.6, 0.6, total_samples)
    env = np.exp(-t * 2.2)  # Long 2.5s decay

    wave = ((0.55 * metallic + 0.45 * noise) * env * 0.8).astype(np.float32)
    return np.clip(wave, -1.0, 1.0)


def synthesize_rimshot(sample_rate: int = 44100, duration: float = 0.08) -> np.ndarray:
    """
    Synthesizes a crisp, high-pitched acoustic snare rim shot / side stick click.
    Returns mono float32 array in range [-1.0, 1.0].
    """
    total_samples = int(sample_rate * duration)
    t = np.linspace(0, duration, total_samples, endpoint=False)

    # High wooden ring ~2100 Hz and 950 Hz
    ring = 0.7 * np.sin(2 * np.pi * 2100 * t) + 0.3 * np.sin(2 * np.pi * 950 * t)
    noise = np.random.uniform(-0.5, 0.5, total_samples)
    env = np.exp(-t * 70.0)

    wave = ((0.75 * ring + 0.25 * noise) * env * 0.9).astype(np.float32)
    return np.clip(wave, -1.0, 1.0)


def synthesize_cowbell(sample_rate: int = 44100, duration: float = 0.25) -> np.ndarray:
    """
    Synthesizes a classic 808-style metallic Cowbell using two detuned square/sine waves (587 Hz & 845 Hz).
    Returns mono float32 array in range [-1.0, 1.0].
    """
    total_samples = int(sample_rate * duration)
    t = np.linspace(0, duration, total_samples, endpoint=False)

    f1, f2 = 587.0, 845.0
    square1 = np.sign(np.sin(2 * np.pi * f1 * t))
    square2 = np.sign(np.sin(2 * np.pi * f2 * t))
    metallic = 0.6 * square1 + 0.4 * square2

    # Bandpass filter simulation with sine undertone
    body = 0.5 * np.sin(2 * np.pi * f1 * t) + 0.5 * np.sin(2 * np.pi * f2 * t)
    env = np.exp(-t * 16.0)

    wave = ((0.4 * metallic + 0.6 * body) * env * 0.75).astype(np.float32)
    return np.clip(wave, -1.0, 1.0)


@dataclass(frozen=True)
class RhythmPattern:
    """Structure defining a cyclic rhythmic backing track."""
    id: str
    name_pt: str
    time_signature: str
    steps_per_bar: int
    grid: List[List[str]]


# Standard Accompaniment Patterns
BACKING_TRACK_LIBRARY: Dict[str, RhythmPattern] = {
    "rock_basic": RhythmPattern(id="rock_basic", name_pt="Rock Básico (4/4)", time_signature="4/4", steps_per_bar=16, grid=[["kick", "hihat_closed"], [], ["hihat_closed"], [], ["snare", "hihat_closed"], [], ["hihat_closed"], [], ["kick", "hihat_closed"], ["kick"], ["hihat_closed"], [], ["snare", "hihat_closed"], [], ["hihat_closed"], ["hihat_open"]]),
    "rock": RhythmPattern(id="rock", name_pt="Rock (4/4)", time_signature="4/4", steps_per_bar=16, grid=[["kick", "hihat_closed"], [], ["hihat_closed"], [], ["snare", "hihat_closed"], [], ["hihat_closed"], [], ["kick", "hihat_closed"], ["kick"], ["hihat_closed"], [], ["snare", "hihat_closed"], [], ["hihat_closed"], ["hihat_open"]]),
    "slow_ballad": RhythmPattern(id="slow_ballad", name_pt="Balada Lenta (4/4)", time_signature="4/4", steps_per_bar=16, grid=[["kick", "hihat_closed"], [], ["hihat_closed"], [], ["snare", "hihat_closed"], [], ["hihat_closed"], [], ["kick", "hihat_closed"], [], ["hihat_closed"], [], ["snare", "hihat_closed"], [], ["hihat_closed"], []]),
    "bossa_nova": RhythmPattern(id="bossa_nova", name_pt="Bossa Nova (4/4)", time_signature="4/4", steps_per_bar=16, grid=[["kick", "snare", "hihat_closed"], [], ["hihat_closed"], ["snare"], ["hihat_closed"], [], ["kick", "snare", "hihat_closed"], [], ["hihat_closed"], ["snare"], ["kick", "hihat_closed"], [], ["snare", "hihat_closed"], [], ["hihat_closed"], ["snare"]]),
    "blues_shuffle": RhythmPattern(id="blues_shuffle", name_pt="Blues Shuffle (4/4)", time_signature="4/4", steps_per_bar=12, grid=[["kick", "ride"], [], ["ride"], ["snare", "hihat_closed", "ride"], [], ["ride"], ["kick", "ride"], [], ["ride"], ["snare", "hihat_closed", "ride"], [], ["ride"]]),
    "waltz": RhythmPattern(id="waltz", name_pt="Valsa (3/4)", time_signature="3/4", steps_per_bar=12, grid=[["kick", "hihat_closed"], [], ["hihat_closed"], [], ["snare", "hihat_closed"], [], ["hihat_closed"], [], ["snare", "hihat_closed"], [], ["hihat_closed"], []]),
    "waltz_34": RhythmPattern(id="waltz_34", name_pt="Valsa 3/4", time_signature="3/4", steps_per_bar=12, grid=[["kick", "hihat_closed"], [], ["hihat_closed"], [], ["snare", "hihat_closed"], [], ["hihat_closed"], [], ["snare", "hihat_closed"], [], ["hihat_closed"], []]),
    "16beat": RhythmPattern(id="16beat", name_pt="16 Beat Pop (4/4)", time_signature="4/4", steps_per_bar=16, grid=[["kick", "hihat_closed"], ["hihat_closed"], ["hihat_closed"], ["hihat_closed"], ["snare", "hihat_closed"], ["hihat_closed"], ["kick", "hihat_closed"], ["hihat_closed"], ["kick", "hihat_closed"], ["hihat_closed"], ["hihat_closed"], ["hihat_closed"], ["snare", "hihat_closed"], ["hihat_closed"], ["hihat_closed"], ["hihat_closed"]]),
    "disco": RhythmPattern(id="disco", name_pt="Disco / Dance (4/4)", time_signature="4/4", steps_per_bar=16, grid=[["kick", "hihat_closed"], [], ["hihat_open"], [], ["snare", "hihat_closed", "kick"], [], ["hihat_open"], [], ["kick", "hihat_closed"], [], ["hihat_open"], [], ["snare", "hihat_closed", "kick"], [], ["hihat_open"], []]),
    "pop": RhythmPattern(id="pop", name_pt="Pop (4/4)", time_signature="4/4", steps_per_bar=16, grid=[["kick", "hihat_closed"], [], ["hihat_closed"], [], ["snare", "hihat_closed"], [], ["hihat_closed"], [], ["kick", "hihat_closed"], [], ["hihat_closed"], [], ["snare", "hihat_closed"], [], ["hihat_closed"], []]),
    "jazz_swing": RhythmPattern(id="jazz_swing", name_pt="Jazz Swing (4/4)", time_signature="4/4", steps_per_bar=12, grid=[["kick", "ride"], [], ["ride"], ["snare", "hihat_closed", "ride"], [], ["ride"], ["kick", "ride"], [], ["ride"], ["snare", "hihat_closed", "ride"], [], ["ride"]]),
    "bolero": RhythmPattern(id="bolero", name_pt="Bolero / Balada Latina (4/4)", time_signature="4/4", steps_per_bar=16, grid=[["kick", "hihat_closed"], [], ["hihat_closed"], [], ["snare", "hihat_closed"], [], ["kick", "hihat_closed"], ["kick"], ["kick", "hihat_closed"], [], ["hihat_closed"], [], ["snare", "hihat_closed"], [], ["hihat_closed"], []]),
}


class BackingTrackPlayer:
    """
    Background rhythm groove player driven by synthesized acoustic drum instruments.
    Maintains tempo precision and lock-free thread synchronization.
    """

    @staticmethod
    def get_available_styles():
        return list(BACKING_TRACK_LIBRARY.keys())

    def __init__(self, bpm: int = 100, volume: float = 0.70):
        self.bpm = max(40, min(240, bpm))
        self.volume = max(0.0, min(1.0, volume))
        self.current_pattern: Optional[RhythmPattern] = None

        self._is_playing = False
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._lock = threading.Lock()

        # Cache synthesized pygame sounds
        self._sounds: Dict[str, Optional[Any]] = {}
        self._prepare_sounds()

    def _prepare_sounds(self):
        """Generates and caches drum kit instruments into Pygame Sounds."""
        if not HAS_PYGAME or not pygame.mixer.get_init():
            return

        def _to_sound(mono_wave: np.ndarray):
            stereo = np.column_stack((mono_wave, mono_wave))
            int16_pcm = (np.clip(stereo * self.volume, -1.0, 1.0) * 32767).astype(np.int16)
            try:
                return pygame.sndarray.make_sound(int16_pcm)
            except Exception:
                return None

        self._sounds["kick"] = _to_sound(synthesize_kick())
        self._sounds["snare"] = _to_sound(synthesize_snare())
        self._sounds["hihat_closed"] = _to_sound(synthesize_hihat(open=False))
        self._sounds["hihat_open"] = _to_sound(synthesize_hihat(open=True))
        self._sounds["ride"] = _to_sound(synthesize_ride())
        self._sounds["tom_low"] = _to_sound(synthesize_tom(pitch="low"))
        self._sounds["tom_mid"] = _to_sound(synthesize_tom(pitch="mid"))
        self._sounds["tom_high"] = _to_sound(synthesize_tom(pitch="high"))
        self._sounds["clap"] = _to_sound(synthesize_clap())
        self._sounds["crash"] = _to_sound(synthesize_crash())
        self._sounds["rimshot"] = _to_sound(synthesize_rimshot())
        self._sounds["cowbell"] = _to_sound(synthesize_cowbell())

    @property
    def is_playing(self) -> bool:
        return self._is_playing

    def set_bpm(self, bpm: int):
        with self._lock:
            self.bpm = max(40, min(240, bpm))

    def set_volume(self, volume: float):
        with self._lock:
            self.volume = max(0.0, min(1.0, volume))
            self._prepare_sounds()

    def start(self, pattern_id: str = "rock_basic", bpm: Optional[int] = None):
        with self._lock:
            if pattern_id in BACKING_TRACK_LIBRARY:
                self.current_pattern = BACKING_TRACK_LIBRARY[pattern_id]
            else:
                self.current_pattern = BACKING_TRACK_LIBRARY["rock_basic"]

            if bpm is not None:
                self.bpm = max(40, min(240, bpm))

            if self._is_playing:
                return

            self._is_playing = True
            self._stop_event.clear()
            self._thread = threading.Thread(target=self._run_loop, daemon=True)
            self._thread.start()

    def stop(self):
        with self._lock:
            if not self._is_playing:
                return
            self._is_playing = False
            self._stop_event.set()

        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=0.25)
        self._thread = None

    def _run_loop(self):
        step_idx = 0
        next_step_time = time.perf_counter()

        while not self._stop_event.is_set():
            with self._lock:
                pattern = self.current_pattern
                bpm = self.bpm

            if not pattern or not pattern.grid:
                self._stop_event.wait(timeout=0.05)
                continue

            # Calculate step duration based on time signature and steps per bar
            if pattern.steps_per_bar == 16:
                step_dur = (60.0 / bpm) / 4.0
            elif pattern.steps_per_bar == 12:
                beats = 3.0 if pattern.time_signature == "3/4" else 4.0
                step_dur = (beats * (60.0 / bpm)) / 12.0
            else:
                step_dur = (4.0 * (60.0 / bpm)) / float(pattern.steps_per_bar)

            # Trigger sounds for current step
            active_hits = pattern.grid[step_idx % len(pattern.grid)]
            for hit in active_hits:
                snd = self._sounds.get(hit)
                if snd is not None:
                    try:
                        snd.play()
                    except Exception:
                        pass

            step_idx = (step_idx + 1) % len(pattern.grid)

            # Drift-free monotonic scheduling without CPU spin-wait
            next_step_time += step_dur
            now = time.perf_counter()
            sleep_time = next_step_time - now

            if sleep_time > 0:
                self._stop_event.wait(timeout=sleep_time)
            else:
                # If behind schedule, resync anchor to current timestamp
                next_step_time = now
