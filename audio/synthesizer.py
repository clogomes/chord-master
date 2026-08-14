"""Mathematical sound synthesizer with harmonic richness and click-free ADSR envelopes."""
import io
import math
import wave
from typing import List, Union

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False


class Synthesizer:
    """Synthesizes instrument-like tones in memory using additive harmonic synthesis."""

    SAMPLE_RATE = 44100

    @classmethod
    def apply_adsr(
        cls,
        samples: Union[List[float], "np.ndarray"],
        sample_rate: int,
        attack_ms: float = 15.0,
        decay_ms: float = 40.0,
        sustain_level: float = 0.75,
        release_ms: float = 60.0,
    ):
        """Applies an Attack-Decay-Sustain-Release envelope to eliminate audio pops and clicks."""
        n_samples = len(samples)
        attack_samples = int((attack_ms / 1000.0) * sample_rate)
        decay_samples = int((decay_ms / 1000.0) * sample_rate)
        release_samples = int((release_ms / 1000.0) * sample_rate)

        # Ensure bounds
        if attack_samples + decay_samples + release_samples > n_samples:
            scale = n_samples / (attack_samples + decay_samples + release_samples)
            attack_samples = int(attack_samples * scale)
            decay_samples = int(decay_samples * scale)
            release_samples = int(release_samples * scale)

        sustain_samples = max(0, n_samples - attack_samples - decay_samples - release_samples)

        if HAS_NUMPY and isinstance(samples, np.ndarray):
            env = np.ones(n_samples, dtype=np.float32)

            # Attack (0 -> 1)
            if attack_samples > 0:
                env[:attack_samples] = np.linspace(0.0, 1.0, attack_samples)

            # Decay (1 -> sustain_level)
            d_start = attack_samples
            d_end = attack_samples + decay_samples
            if decay_samples > 0:
                env[d_start:d_end] = np.linspace(1.0, sustain_level, decay_samples)

            # Sustain
            s_end = d_end + sustain_samples
            env[d_end:s_end] = sustain_level

            # Release (sustain_level -> 0)
            if release_samples > 0:
                env[s_end:] = np.linspace(sustain_level, 0.0, release_samples)

            return samples * env
        else:
            # Pure Python fallback
            result = list(samples)
            for i in range(n_samples):
                if i < attack_samples:
                    factor = i / float(attack_samples)
                elif i < attack_samples + decay_samples:
                    progress = (i - attack_samples) / float(decay_samples)
                    factor = 1.0 - (1.0 - sustain_level) * progress
                elif i < attack_samples + decay_samples + sustain_samples:
                    factor = sustain_level
                else:
                    progress = (i - attack_samples - decay_samples - sustain_samples) / float(release_samples)
                    factor = max(0.0, sustain_level * (1.0 - progress))
                result[i] *= factor
            return result

    @classmethod
    def generate_single_frequency(
        cls,
        frequency: float,
        duration: float = 0.7,
        volume: float = 0.45,
    ) -> bytes:
        """
        Generates 16-bit PCM WAV bytes for a single musical note.
        Combines fundamental with 3 harmonics for a pleasant warm acoustic tone.
        """
        sample_rate = cls.SAMPLE_RATE
        total_samples = int(sample_rate * duration)

        if HAS_NUMPY:
            t = np.linspace(0, duration, total_samples, endpoint=False)
            # Additive synthesis with harmonics
            waveform = (
                1.00 * np.sin(2 * np.pi * frequency * t) +
                0.30 * np.sin(2 * np.pi * frequency * 2 * t) +
                0.12 * np.sin(2 * np.pi * frequency * 3 * t) +
                0.05 * np.sin(2 * np.pi * frequency * 4 * t)
            )
            # Normalize peak amplitude
            waveform = waveform / 1.47
            waveform = cls.apply_adsr(waveform, sample_rate)
            waveform = waveform * volume

            # Convert to 16-bit signed PCM
            pcm_data = np.int16(np.clip(waveform * 32767, -32768, 32767)).tobytes()
        else:
            samples = []
            for i in range(total_samples):
                t = i / float(sample_rate)
                val = (
                    1.00 * math.sin(2 * math.pi * frequency * t) +
                    0.30 * math.sin(2 * math.pi * frequency * 2 * t) +
                    0.12 * math.sin(2 * math.pi * frequency * 3 * t) +
                    0.05 * math.sin(2 * math.pi * frequency * 4 * t)
                ) / 1.47
                samples.append(val)

            samples = cls.apply_adsr(samples, sample_rate)
            pcm_bytes = bytearray()
            for s in samples:
                val = int(max(-1.0, min(1.0, s * volume)) * 32767)
                pcm_bytes.extend(val.to_bytes(2, byteorder="little", signed=True))
            pcm_data = bytes(pcm_bytes)

        return cls._create_wav_header(pcm_data, sample_rate, num_channels=1)

    @classmethod
    def generate_polyphonic(
        cls,
        frequencies: List[float],
        duration: float = 1.2,
        volume: float = 0.5,
    ) -> bytes:
        """
        Generates 16-bit PCM WAV bytes for multiple simultaneous frequencies (harmonic intervals & chords).
        """
        if not frequencies:
            return cls.generate_single_frequency(440.0, duration=0.1, volume=0.0)

        sample_rate = cls.SAMPLE_RATE
        total_samples = int(sample_rate * duration)
        num_voices = len(frequencies)

        if HAS_NUMPY:
            t = np.linspace(0, duration, total_samples, endpoint=False)
            mixed = np.zeros(total_samples, dtype=np.float32)

            for freq in frequencies:
                voice = (
                    1.00 * np.sin(2 * np.pi * freq * t) +
                    0.28 * np.sin(2 * np.pi * freq * 2 * t) +
                    0.10 * np.sin(2 * np.pi * freq * 3 * t)
                ) / 1.38
                mixed += voice

            mixed = mixed / math.sqrt(num_voices)
            mixed = cls.apply_adsr(mixed, sample_rate, attack_ms=25.0, release_ms=120.0)
            mixed = mixed * volume
            pcm_data = np.int16(np.clip(mixed * 32767, -32768, 32767)).tobytes()
        else:
            samples = [0.0] * total_samples
            for freq in frequencies:
                for i in range(total_samples):
                    t = i / float(sample_rate)
                    val = (
                        1.00 * math.sin(2 * math.pi * freq * t) +
                        0.28 * math.sin(2 * math.pi * freq * 2 * t) +
                        0.10 * math.sin(2 * math.pi * freq * 3 * t)
                    ) / 1.38
                    samples[i] += val

            norm = math.sqrt(num_voices)
            for i in range(total_samples):
                samples[i] /= norm

            samples = cls.apply_adsr(samples, sample_rate, attack_ms=25.0, release_ms=120.0)
            pcm_bytes = bytearray()
            for s in samples:
                val = int(max(-1.0, min(1.0, s * volume)) * 32767)
                pcm_bytes.extend(val.to_bytes(2, byteorder="little", signed=True))
            pcm_data = bytes(pcm_bytes)

        return cls._create_wav_header(pcm_data, sample_rate, num_channels=1)

    @staticmethod
    def _create_wav_header(pcm_data: bytes, sample_rate: int, num_channels: int = 1) -> bytes:
        """Wraps raw 16-bit PCM bytes with a standard RIFF/WAVE header."""
        out = io.BytesIO()
        with wave.open(out, "wb") as wav_file:
            wav_file.setnchannels(num_channels)
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(pcm_data)
        return out.getvalue()
