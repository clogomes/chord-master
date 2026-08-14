"""Microphone audio capture and real-time autocorrelation pitch detection engine."""
import math
import threading
import time
from typing import Callable, Optional, Tuple
import numpy as np
from core.notes import Note, midi_to_note

try:
    import sounddevice as sd
    HAS_SOUNDDEVICE = True
except ImportError:
    HAS_SOUNDDEVICE = False


def detect_pitch_from_samples(
    samples: np.ndarray,
    sample_rate: int = 44100,
    min_freq: float = 60.0,      # ~B1 (Lowest notes of cello/viola/piano)
    max_freq: float = 1200.0,    # ~D6 (High treble notes)
    silence_threshold: float = 0.010,
) -> Tuple[Optional[Note], float, float, float]:
    """
    Detects the fundamental frequency (f0), musical Note, cents offset, and confidence
    using FFT autocorrelation with first-major-peak selection and parabolic interpolation.

    Returns:
        (detected_note, cents_offset, confidence, frequency_hz)
    """
    if len(samples) < 512:
        return None, 0.0, 0.0, 0.0

    # 1. Check signal RMS energy level
    rms = float(np.sqrt(np.mean(samples**2)))
    if rms < silence_threshold:
        return None, 0.0, 0.0, 0.0

    # 2. DC offset removal
    x = samples - np.mean(samples)
    N = len(x)

    # 3. FFT-accelerated Autocorrelation
    n_fft = 2 * N
    f = np.fft.rfft(x, n=n_fft)
    acf = np.fft.irfft(f * np.conj(f))[:N]

    if acf[0] <= 1e-12:
        return None, 0.0, 0.0, 0.0

    # 4. Search range in lags
    abs_min_lag = max(2, int(sample_rate / max_freq))
    abs_max_lag = min(N - 2, int(sample_rate / min_freq))

    if abs_min_lag >= abs_max_lag:
        return None, 0.0, 0.0, 0.0

    # 5. Find zero crossing to avoid main lag-0 peak
    zero_crossings = np.where((acf[:-1] > 0) & (acf[1:] <= 0))[0]
    start_lag = zero_crossings[0] if len(zero_crossings) > 0 and zero_crossings[0] > abs_min_lag else abs_min_lag

    # 6. Find all positive local maxima peaks
    peaks = []
    for i in range(start_lag, abs_max_lag):
        if acf[i] > acf[i-1] and acf[i] > acf[i+1] and acf[i] > 0:
            peaks.append((i, acf[i]))

    if not peaks:
        return None, 0.0, 0.0, 0.0

    # Pick the FIRST major peak whose amplitude is at least 75% of the global peak
    max_val = max(p[1] for p in peaks)
    threshold = 0.75 * max_val
    chosen_peak = next((p for p in peaks if p[1] >= threshold), peaks[0])
    peak_idx = chosen_peak[0]

    # 7. Parabolic peak interpolation for sub-sample fractional accuracy
    alpha = acf[peak_idx - 1]
    beta = acf[peak_idx]
    gamma = acf[peak_idx + 1]
    denom = 2.0 * (alpha - 2.0 * beta + gamma)
    delta = (alpha - gamma) / denom if abs(denom) > 1e-12 else 0.0
    refined_lag = float(peak_idx) + delta

    if refined_lag <= 0:
        return None, 0.0, 0.0, 0.0

    f0 = float(sample_rate) / refined_lag
    confidence = float(acf[peak_idx] / acf[0])

    # 8. Quality thresholding
    if confidence < 0.25 or f0 < min_freq or f0 > max_freq:
        return None, 0.0, confidence, f0

    # 9. Convert frequency to exact fractional MIDI note number
    exact_midi = 69.0 + 12.0 * math.log2(max(1e-6, f0 / 440.0))
    rounded_midi = int(round(exact_midi))
    cents_offset = (exact_midi - rounded_midi) * 100.0

    if 21 <= rounded_midi <= 108:
        try:
            pitch_str, octave = midi_to_note(rounded_midi)
            detected_note = Note(pitch_str, octave)
            return detected_note, cents_offset, confidence, f0
        except Exception:
            return None, 0.0, 0.0, 0.0

    return None, 0.0, confidence, f0


class PitchListener:
    """
    Manages live microphone audio stream capture in a background daemon thread,
    periodically triggering pitch detection callbacks with intelligent rate-limiting.
    """

    def __init__(self, sample_rate: int = 44100, block_size: int = 2048, max_fps: float = 16.0):
        self.sample_rate = sample_rate
        self.block_size = block_size
        self.min_callback_interval = 1.0 / max_fps
        self._last_callback_time = 0.0
        self._is_listening = False
        self._stream = None
        self._callback: Optional[Callable[[Optional[Note], float, float, float], None]] = None
        self._lock = threading.Lock()

    @property
    def is_listening(self) -> bool:
        return self._is_listening

    @property
    def has_sounddevice(self) -> bool:
        return HAS_SOUNDDEVICE

    def start_listening(
        self,
        callback: Callable[[Optional[Note], float, float, float], None],
    ) -> bool:
        """
        Starts audio stream capture from default microphone.
        Returns True if started successfully, False otherwise.
        """
        if not HAS_SOUNDDEVICE:
            print("[PitchListener] sounddevice não está disponível no sistema.")
            return False

        with self._lock:
            if self._is_listening:
                self._callback = callback
                return True

            self._callback = callback
            self._last_callback_time = 0.0
            try:
                self._stream = sd.InputStream(
                    samplerate=self.sample_rate,
                    blocksize=self.block_size,
                    channels=1,
                    dtype="float32",
                    callback=self._audio_stream_callback,
                )
                self._stream.start()
                self._is_listening = True
                return True
            except Exception as e:
                print(f"[PitchListener] Erro ao abrir stream de microfone: {e}")
                self._is_listening = False
                self._stream = None
                return False

    def stop_listening(self):
        """Stops and cleans up the microphone audio stream."""
        with self._lock:
            self._is_listening = False
            if self._stream is not None:
                try:
                    self._stream.stop()
                    self._stream.close()
                except Exception:
                    pass
                self._stream = None
            self._callback = None

    def _audio_stream_callback(self, indata, frames, time_info, status):
        """Internal callback invoked by sounddevice with rate-limiting."""
        if not self._is_listening or self._callback is None:
            return

        now = time.time()
        if now - self._last_callback_time < self.min_callback_interval:
            return
        self._last_callback_time = now

        samples = indata[:, 0]
        detected_note, cents, conf, freq = detect_pitch_from_samples(
            samples,
            sample_rate=self.sample_rate,
        )

        cb = self._callback
        if cb is not None and self._is_listening:
            try:
                cb(detected_note, cents, conf, freq)
            except Exception:
                pass
