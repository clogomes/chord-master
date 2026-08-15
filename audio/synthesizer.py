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
        Combines fundamental with 5 harmonics for a pleasant warm acoustic tone,
        with per-octave ADSR, hammer transient click, and subtle chorus (warmth).
        """
        sample_rate = cls.SAMPLE_RATE
        total_samples = int(sample_rate * duration)

        if HAS_NUMPY:
            t = np.linspace(0, duration, total_samples, endpoint=False)
            
            freqs = [frequency, frequency*2, frequency*3, frequency*4, frequency*5, frequency*6]
            amps = [1.0, 0.5, 0.25, 0.12, 0.06, 0.03]
            
            waveform = np.zeros(total_samples, dtype=np.float32)
            for f, a in zip(freqs, amps):
                waveform += a * np.sin(2 * np.pi * f * t)
                waveform += a * 0.4 * np.sin(2 * np.pi * (f + 0.15) * t)
                waveform += a * 0.4 * np.sin(2 * np.pi * (f - 0.15) * t)
                
            waveform = waveform / np.max(np.abs(waveform))
            
            octave_scale = max(0.2, 440.0 / max(50.0, frequency))
            waveform = cls.apply_adsr(
                waveform, 
                sample_rate,
                attack_ms=5.0,
                decay_ms=300.0 * octave_scale,
                sustain_level=0.3,
                release_ms=100.0 * octave_scale
            )
            
            click_len = int(sample_rate * 0.003)
            if click_len > 0:
                click = np.random.uniform(-1.0, 1.0, click_len) * np.linspace(1.0, 0.0, click_len)
                waveform[:click_len] += click * 0.15
                
            waveform = waveform * volume
            pcm_data = np.int16(np.clip(waveform * 32767, -32768, 32767)).tobytes()
        else:
            import random
            samples = []
            freqs = [frequency, frequency*2, frequency*3, frequency*4, frequency*5, frequency*6]
            amps = [1.0, 0.5, 0.25, 0.12, 0.06, 0.03]
            for i in range(total_samples):
                t = i / float(sample_rate)
                val = 0.0
                for f, a in zip(freqs, amps):
                    val += a * math.sin(2 * math.pi * f * t)
                    val += a * 0.4 * math.sin(2 * math.pi * (f + 0.15) * t)
                    val += a * 0.4 * math.sin(2 * math.pi * (f - 0.15) * t)
                if i < int(sample_rate * 0.003):
                    val += random.uniform(-1.0, 1.0) * (1.0 - i/(sample_rate*0.003)) * 0.5
                samples.append(val / 3.0)

            octave_scale = max(0.2, 440.0 / max(50.0, frequency))
            samples = cls.apply_adsr(
                samples, 
                sample_rate,
                attack_ms=5.0,
                decay_ms=300.0 * octave_scale,
                sustain_level=0.3,
                release_ms=100.0 * octave_scale
            )
            pcm_bytes = bytearray()
            for s in samples:
                val = int(max(-1.0, min(1.0, s * volume)) * 32767)
                pcm_bytes.extend(val.to_bytes(2, byteorder="little", signed=True))
            pcm_data = bytes(pcm_bytes)

        return cls._create_wav_header(pcm_data, sample_rate, num_channels=1)

    @classmethod
    def generate_plucked_string(
        cls,
        frequency: float,
        duration: float = 0.8,
        volume: float = 0.5,
        decay_factor: float = 0.994,
    ) -> bytes:
        """
        Synthesizes a realistic plucked string (acoustic guitar/viola) using the Karplus-Strong
        physical modeling algorithm (filtered delay line with noise excitation), 
        enhanced with natural vibrato and acoustic body resonance.
        """
        sample_rate = cls.SAMPLE_RATE
        total_samples = int(sample_rate * duration)
        if frequency <= 0 or total_samples <= 0:
            return cls._create_wav_header(b"", sample_rate)

        n_delay = max(2, int(round(sample_rate / frequency)))

        if HAS_NUMPY:
            rng = np.random.default_rng(seed=42)
            buffer = rng.uniform(-1.0, 1.0, n_delay).astype(np.float32)
            
            if volume < 0.7:
                smooth_factor = 1.0 - volume
                buffer[1:] = buffer[1:] * (1.0 - smooth_factor) + buffer[:-1] * smooth_factor
                
            samples = np.zeros(total_samples, dtype=np.float32)
            
            vibrato_rate = 4.5
            vibrato_depth = 0.004
            base_delay = sample_rate / frequency
            t_arr = np.linspace(0, duration, total_samples, endpoint=False)
            ramp = np.clip(t_arr / 0.2, 0.0, 1.0)
            delay_modulation = base_delay * (1.0 + ramp * vibrato_depth * np.sin(2 * np.pi * vibrato_rate * t_arr))
            
            write_ptr = 0
            max_delay = int(base_delay * 1.05) + 2
            delay_buffer = np.zeros(max_delay, dtype=np.float32)
            delay_buffer[:n_delay] = buffer
            
            fc = 150.0 / sample_rate
            r = 0.85
            a1 = -2.0 * r * np.cos(2.0 * np.pi * fc)
            a2 = r * r
            b0 = (1.0 - r) * np.sqrt(1.0 - r)
            body_out = np.zeros(total_samples, dtype=np.float32)

            for i in range(total_samples):
                curr_delay = delay_modulation[i]
                read_idx = write_ptr - curr_delay
                
                idx_int = int(np.floor(read_idx))
                frac = read_idx - idx_int
                
                idx_1 = idx_int % max_delay
                idx_2 = (idx_int + 1) % max_delay
                
                val = delay_buffer[idx_1] * (1.0 - frac) + delay_buffer[idx_2] * frac
                samples[i] = val
                
                filtered_val = 0.5 * (val + delay_buffer[(idx_int - 1) % max_delay]) * decay_factor
                delay_buffer[write_ptr] = filtered_val
                write_ptr = (write_ptr + 1) % max_delay
                
                if i >= 2:
                    body_out[i] = b0 * val - a1 * body_out[i-1] - a2 * body_out[i-2]

            final_out = samples * 0.7 + body_out * 0.3

            peak = float(np.max(np.abs(final_out)))
            if peak > 0:
                final_out = final_out / peak

            final_out = cls.apply_adsr(
                final_out,
                sample_rate,
                attack_ms=2.0,
                decay_ms=duration * 400.0,
                sustain_level=0.4,
                release_ms=35.0,
            )
            final_out = final_out * volume
            pcm_data = np.int16(np.clip(final_out * 32767, -32768, 32767)).tobytes()
        else:
            import random
            random.seed(42)
            buffer = [random.uniform(-1.0, 1.0) for _ in range(n_delay)]
            
            if volume < 0.7:
                smooth_factor = 1.0 - volume
                for i in range(1, n_delay):
                    buffer[i] = buffer[i] * (1.0 - smooth_factor) + buffer[i-1] * smooth_factor
                    
            samples = [0.0] * total_samples
            
            vibrato_rate = 4.5
            vibrato_depth = 0.004
            base_delay = sample_rate / frequency
            
            write_ptr = 0
            max_delay = int(base_delay * 1.05) + 2
            delay_buffer = [0.0] * max_delay
            for i in range(n_delay):
                delay_buffer[i] = buffer[i]
                
            fc = 150.0 / sample_rate
            r = 0.85
            a1 = -2.0 * r * math.cos(2.0 * math.pi * fc)
            a2 = r * r
            b0 = (1.0 - r) * math.sqrt(1.0 - r)
            body_out = [0.0] * total_samples
            
            for i in range(total_samples):
                t = i / float(sample_rate)
                ramp = min(1.0, t / 0.2)
                curr_delay = base_delay * (1.0 + ramp * vibrato_depth * math.sin(2 * math.pi * vibrato_rate * t))
                
                read_idx = write_ptr - curr_delay
                idx_int = int(math.floor(read_idx))
                frac = read_idx - idx_int
                
                idx_1 = idx_int % max_delay
                idx_2 = (idx_int + 1) % max_delay
                
                val = delay_buffer[idx_1] * (1.0 - frac) + delay_buffer[idx_2] * frac
                samples[i] = val
                
                filtered_val = 0.5 * (val + delay_buffer[(idx_int - 1) % max_delay]) * decay_factor
                delay_buffer[write_ptr] = filtered_val
                write_ptr = (write_ptr + 1) % max_delay
                
                if i >= 2:
                    body_out[i] = b0 * val - a1 * body_out[i-1] - a2 * body_out[i-2]
                    
            final_out = [samples[i] * 0.7 + body_out[i] * 0.3 for i in range(total_samples)]
            
            max_val = max(abs(s) for s in final_out) if final_out else 1.0
            if max_val > 0:
                final_out = [s / max_val for s in final_out]

            final_out = cls.apply_adsr(
                final_out,
                sample_rate,
                attack_ms=2.0,
                decay_ms=duration * 400.0,
                sustain_level=0.4,
                release_ms=35.0,
            )
            pcm_bytes = bytearray()
            for s in final_out:
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
