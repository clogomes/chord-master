"""Offline multi-track rendering engine for Composition Studio.

Renders complete compositions (rhythm tracks + piano & guitar chords) into a stereo
float32 numpy array (N, 2) without real-time jitter, with cached synthesis, proper tail
handling, and a soft-limiting saturation stage.
"""
from typing import Dict, List, Optional, Tuple
import numpy as np
from core.composition import Composition, ChordEvent, RhythmTrack
from core.chords import get_chord_notes
from core.notes import Note
from audio.synthesizer import Synthesizer
from audio.backing_tracks import (
    synthesize_kick,
    synthesize_snare,
    synthesize_hihat,
    synthesize_ride,
    synthesize_tom,
    synthesize_clap,
    synthesize_crash,
    synthesize_rimshot,
    synthesize_cowbell,
)

SAMPLE_RATE = 44100

# Cache for synthesized float32 audio arrays: (instrument, pitch_or_freq, duration_rounded, volume_rounded)
_SAMPLE_CACHE: Dict[Tuple, np.ndarray] = {}


def _get_synthesized_drum_sample(instrument: str, sample_rate: int = SAMPLE_RATE) -> np.ndarray:
    """Returns mono float32 drum sample array from cache or synthesizes it."""
    cache_key = ("drum", instrument, sample_rate)
    if cache_key in _SAMPLE_CACHE:
        return _SAMPLE_CACHE[cache_key]

    if instrument == "kick":
        sample = synthesize_kick(sample_rate=sample_rate, duration=0.25)
    elif instrument == "snare":
        sample = synthesize_snare(sample_rate=sample_rate, duration=0.20)
    elif instrument == "hihat_open":
        sample = synthesize_hihat(open=True, sample_rate=sample_rate)
    elif instrument == "hihat_closed" or instrument == "hihat":
        sample = synthesize_hihat(open=False, sample_rate=sample_rate)
    elif instrument == "ride":
        sample = synthesize_ride(sample_rate=sample_rate, duration=0.60)
    elif instrument == "tom_low":
        sample = synthesize_tom(pitch="low", sample_rate=sample_rate, duration=0.35)
    elif instrument == "tom_mid":
        sample = synthesize_tom(pitch="mid", sample_rate=sample_rate, duration=0.35)
    elif instrument == "tom_high":
        sample = synthesize_tom(pitch="high", sample_rate=sample_rate, duration=0.35)
    elif instrument == "clap":
        sample = synthesize_clap(sample_rate=sample_rate, duration=0.25)
    elif instrument == "crash":
        sample = synthesize_crash(sample_rate=sample_rate, duration=2.50)
    elif instrument == "rimshot":
        sample = synthesize_rimshot(sample_rate=sample_rate, duration=0.08)
    elif instrument == "cowbell":
        sample = synthesize_cowbell(sample_rate=sample_rate, duration=0.25)
    else:
        # Fallback to soft click
        sample = np.zeros(int(sample_rate * 0.05), dtype=np.float32)

    _SAMPLE_CACHE[cache_key] = sample
    return sample


def _synthesize_piano_chord_raw(frequencies: List[float], duration: float, volume: float, sample_rate: int = SAMPLE_RATE) -> np.ndarray:
    """Synthesizes mono float32 piano chord with multi-harmonic additive synthesis."""
    total_samples = int(sample_rate * duration)
    if not frequencies or total_samples <= 0:
        return np.zeros(total_samples, dtype=np.float32)

    t = np.linspace(0, duration, total_samples, endpoint=False)
    mixed = np.zeros(total_samples, dtype=np.float32)
    num_voices = len(frequencies)

    harmonics = [(1.0, 1.0), (2.0, 0.5), (3.0, 0.25), (4.0, 0.12), (5.0, 0.06), (6.0, 0.03)]

    for freq in frequencies:
        if freq <= 0:
            continue
        voice_wave = np.zeros(total_samples, dtype=np.float32)
        for h_mult, h_amp in harmonics:
            h_freq = freq * h_mult
            if h_freq < sample_rate / 2:
                voice_wave += h_amp * np.sin(2.0 * np.pi * h_freq * t).astype(np.float32)
        mixed += voice_wave

    if num_voices > 0:
        mixed /= np.sqrt(num_voices)

    peak = float(np.max(np.abs(mixed)))
    if peak > 0:
        mixed /= peak

    mixed = Synthesizer.apply_adsr(
        mixed,
        sample_rate,
        attack_ms=12.0,
        decay_ms=duration * 300.0,
        sustain_level=0.5,
        release_ms=45.0,
    )
    return (mixed * volume).astype(np.float32)


def _synthesize_guitar_note_raw(frequency: float, duration: float, volume: float, sample_rate: int = SAMPLE_RATE) -> np.ndarray:
    """Synthesizes single acoustic guitar plucked string in mono float32 with Karplus-Strong & body resonance."""
    total_samples = int(sample_rate * duration)
    if frequency <= 0 or total_samples <= 0:
        return np.zeros(total_samples, dtype=np.float32)

    decay_factor = 0.993
    n_delay = max(2, int(round(sample_rate / frequency)))

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
        final_out /= peak

    final_out = Synthesizer.apply_adsr(
        final_out,
        sample_rate,
        attack_ms=2.0,
        decay_ms=duration * 400.0,
        sustain_level=0.4,
        release_ms=35.0,
    )
    return (final_out * volume).astype(np.float32)


def _get_synthesized_chord_sample(
    instrument: str,
    root: str,
    chord_type: str,
    duration: float,
    volume: float,
    sample_rate: int = SAMPLE_RATE,
) -> np.ndarray:
    """Returns cached mono float32 chord waveform."""
    # Round duration and volume to prevent cache explosion
    dur_quant = round(duration, 3)
    vol_quant = round(volume, 2)
    cache_key = (instrument, root, chord_type, dur_quant, vol_quant, sample_rate)

    if cache_key in _SAMPLE_CACHE:
        return _SAMPLE_CACHE[cache_key]

    try:
        notes = get_chord_notes(root, chord_type)
    except Exception:
        notes = [Note("C", 4), Note("E", 4), Note("G", 4)]

    if instrument == "guitar":
        # Sum individual plucked strings
        total_samples = int(sample_rate * duration)
        combined = np.zeros(total_samples, dtype=np.float32)
        for note in notes:
            note_sample = _synthesize_guitar_note_raw(note.frequency, duration, volume, sample_rate)
            if len(note_sample) > len(combined):
                combined += note_sample[:len(combined)]
            else:
                combined[:len(note_sample)] += note_sample
        if len(notes) > 0:
            combined /= np.sqrt(len(notes))
        result = combined.astype(np.float32)
    else:
        # Piano synthesis
        freqs = [n.frequency for n in notes]
        result = _synthesize_piano_chord_raw(freqs, duration, volume, sample_rate)

    _SAMPLE_CACHE[cache_key] = result
    return result

def _get_synthesized_note_sample(
    instrument: str,
    midi: int,
    duration: float,
    volume: float,
    sample_rate: int = SAMPLE_RATE,
) -> np.ndarray:
    """Returns cached mono float32 note waveform for melodic notes."""
    dur_quant = round(duration, 3)
    vol_quant = round(volume, 2)
    cache_key = ("note", instrument, int(midi), dur_quant, vol_quant, sample_rate)

    if cache_key in _SAMPLE_CACHE:
        return _SAMPLE_CACHE[cache_key]

    freq = 440.0 * (2.0 ** ((midi - 69) / 12.0))

    if instrument == "guitar":
        result = _synthesize_guitar_note_raw(freq, duration, volume, sample_rate)
    else:
        # Piano note
        result = _synthesize_piano_chord_raw([freq], duration, volume, sample_rate)

    _SAMPLE_CACHE[cache_key] = result
    return result


class CompositionRenderer:
    """Offline renderer for compositions to 44.1kHz stereo float32 buffers."""

    def __init__(self, sample_rate: int = SAMPLE_RATE):
        self.sample_rate = sample_rate

    def render(
        self,
        composition: Composition,
        start_bar: Optional[int] = None,
        end_bar: Optional[int] = None,
    ) -> np.ndarray:
        """
        Renders a Composition (or a sub-region of bars [start_bar, end_bar], 1-indexed)
        to a stereo float32 array of shape (N, 2).
        Uses exact sample index placement, cached synthesis, acoustic tail room,
        tail-folding for seamless looping, and soft saturation limiting (np.tanh).
        """
        bpm = max(20, min(300, composition.bpm))
        beats_per_bar = 4
        if "/" in composition.time_signature:
            try:
                beats_per_bar = int(composition.time_signature.split("/")[0])
            except Exception:
                beats_per_bar = 4

        total_comp_bars = max(1, composition.bars)
        is_region_loop = (start_bar is not None and end_bar is not None)

        if is_region_loop:
            s_bar = max(1, min(total_comp_bars, int(start_bar)))
            e_bar = max(s_bar, min(total_comp_bars, int(end_bar)))
            region_bars = e_bar - s_bar + 1
            region_start_beat = (s_bar - 1) * beats_per_bar
            region_end_beat = e_bar * beats_per_bar
        else:
            s_bar = 1
            e_bar = total_comp_bars
            region_bars = total_comp_bars
            region_start_beat = 0.0
            region_end_beat = total_comp_bars * beats_per_bar

        total_beats = region_bars * beats_per_bar
        seconds_per_beat = 60.0 / bpm
        core_duration = total_beats * seconds_per_beat
        core_samples = int(core_duration * self.sample_rate)

        # Acoustic tail extension (3.0 seconds for natural crash cymbal ring and reverb decay)
        tail_duration = 3.0
        tail_samples = int(tail_duration * self.sample_rate)
        total_duration = core_duration + tail_duration
        total_samples = int(total_duration * self.sample_rate)

        # Stereo mix channels (float32)
        mix_left = np.zeros(total_samples, dtype=np.float32)
        mix_right = np.zeros(total_samples, dtype=np.float32)

        # 1. Render Rhythm Track
        if composition.rhythm and not composition.rhythm.muted and composition.rhythm.grid:
            steps_per_bar = composition.rhythm.steps_per_bar
            step_duration_sec = (60.0 / bpm) * (beats_per_bar / float(steps_per_bar))
            drum_vol = composition.rhythm.volume

            region_start_step = (s_bar - 1) * steps_per_bar
            region_end_step = e_bar * steps_per_bar
            total_region_steps = region_bars * steps_per_bar

            for region_step_idx in range(total_region_steps):
                abs_step_idx = region_start_step + region_step_idx
                step_start_sec = region_step_idx * step_duration_sec
                start_sample = int(step_start_sec * self.sample_rate)
                if start_sample >= total_samples:
                    continue

                pattern_idx = abs_step_idx % len(composition.rhythm.grid)
                active_drums = composition.rhythm.grid[pattern_idx]

                for drum_inst in active_drums:
                    drum_sample = _get_synthesized_drum_sample(drum_inst, self.sample_rate)
                    sample_len = len(drum_sample)
                    end_sample = min(total_samples, start_sample + sample_len)
                    actual_len = end_sample - start_sample

                    if actual_len > 0:
                        scaled_drum = drum_sample[:actual_len] * drum_vol

                        pan_left, pan_right = 1.0, 1.0
                        if "hihat" in drum_inst or "ride" in drum_inst or "clap" in drum_inst:
                            pan_left, pan_right = 0.9, 1.1
                        elif "tom_high" in drum_inst or "crash" in drum_inst:
                            pan_left, pan_right = 1.15, 0.85
                        elif "tom_low" in drum_inst:
                            pan_left, pan_right = 0.85, 1.15
                        elif "cowbell" in drum_inst:
                            pan_left, pan_right = 0.9, 1.1

                        mix_left[start_sample:end_sample] += scaled_drum * pan_left
                        mix_right[start_sample:end_sample] += scaled_drum * pan_right

        # 2. Render Chords Track
        if composition.chords:
            for ce in composition.chords:
                # Check if chord event overlaps the rendered region
                c_end_beat = ce.start_beat + ce.duration_beats
                if c_end_beat <= region_start_beat or ce.start_beat >= region_end_beat:
                    continue

                rel_start_beat = ce.start_beat - region_start_beat
                if rel_start_beat < 0:
                    # Chord started before loop region
                    chord_start_sec = 0.0
                    skip_sec = (-rel_start_beat) * seconds_per_beat
                    chord_dur_sec = (c_end_beat - region_start_beat) * seconds_per_beat
                    full_dur = ce.duration_beats * seconds_per_beat
                    chord_audio_full = _get_synthesized_chord_sample(
                        instrument=ce.instrument,
                        root=ce.root,
                        chord_type=ce.chord_type,
                        duration=full_dur,
                        volume=0.75,
                        sample_rate=self.sample_rate,
                    )
                    skip_samples = int(skip_sec * self.sample_rate)
                    chord_audio = chord_audio_full[skip_samples:] if skip_samples < len(chord_audio_full) else np.zeros(0, dtype=np.float32)
                else:
                    chord_start_sec = rel_start_beat * seconds_per_beat
                    chord_dur_sec = ce.duration_beats * seconds_per_beat
                    chord_audio = _get_synthesized_chord_sample(
                        instrument=ce.instrument,
                        root=ce.root,
                        chord_type=ce.chord_type,
                        duration=chord_dur_sec,
                        volume=0.75,
                        sample_rate=self.sample_rate,
                    )

                start_sample = int(chord_start_sec * self.sample_rate)
                if start_sample >= total_samples:
                    continue

                sample_len = len(chord_audio)
                end_sample = min(total_samples, start_sample + sample_len)
                actual_len = end_sample - start_sample

                if actual_len > 0:
                    scaled_chord = chord_audio[:actual_len]
                    pan_l, pan_r = (0.95, 1.05) if ce.instrument == "piano" else (1.05, 0.95)
                    mix_left[start_sample:end_sample] += scaled_chord * pan_l
                    mix_right[start_sample:end_sample] += scaled_chord * pan_r

        # 3. Render Melodic Notes Track
        if hasattr(composition, "notes") and composition.notes:
            for ne in composition.notes:
                n_end_beat = ne.start_beat + ne.duration_beats
                if n_end_beat <= region_start_beat or ne.start_beat >= region_end_beat:
                    continue

                rel_start_beat = ne.start_beat - region_start_beat
                if rel_start_beat < 0:
                    note_start_sec = 0.0
                    skip_sec = (-rel_start_beat) * seconds_per_beat
                    full_dur = ne.duration_beats * seconds_per_beat
                    note_vol = getattr(ne, "velocity", 0.8)
                    note_audio_full = _get_synthesized_note_sample(
                        instrument=ne.instrument,
                        midi=ne.midi,
                        duration=full_dur,
                        volume=note_vol,
                        sample_rate=self.sample_rate,
                    )
                    skip_samples = int(skip_sec * self.sample_rate)
                    note_audio = note_audio_full[skip_samples:] if skip_samples < len(note_audio_full) else np.zeros(0, dtype=np.float32)
                else:
                    note_start_sec = rel_start_beat * seconds_per_beat
                    note_dur_sec = ne.duration_beats * seconds_per_beat
                    note_vol = getattr(ne, "velocity", 0.8)
                    note_audio = _get_synthesized_note_sample(
                        instrument=ne.instrument,
                        midi=ne.midi,
                        duration=note_dur_sec,
                        volume=note_vol,
                        sample_rate=self.sample_rate,
                    )

                start_sample = int(note_start_sec * self.sample_rate)
                if start_sample >= total_samples:
                    continue

                sample_len = len(note_audio)
                end_sample = min(total_samples, start_sample + sample_len)
                actual_len = end_sample - start_sample

                if actual_len > 0:
                    scaled_note = note_audio[:actual_len]
                    pan_l, pan_r = (1.02, 0.98) if ne.instrument == "piano" else (0.98, 1.02)
                    mix_left[start_sample:end_sample] += scaled_note * pan_l
                    mix_right[start_sample:end_sample] += scaled_note * pan_r

        # 4. If region loop is active: Fold acoustic tail back into the beginning for seamless looping
        if is_region_loop and core_samples > 0:
            tail_left = mix_left[core_samples:]
            tail_right = mix_right[core_samples:]
            # Crop to exact core loop duration
            mix_left = mix_left[:core_samples]
            mix_right = mix_right[:core_samples]

            # Fold tail with wrap-around
            for i in range(len(tail_left)):
                mix_left[i % core_samples] += tail_left[i]
                mix_right[i % core_samples] += tail_right[i]

        # 5. Apply Master Volume
        master_vol = composition.master_volume
        mix_left *= master_vol
        mix_right *= master_vol

        # 6. Soft Saturation Limiter (np.tanh prevents hard clipping while keeping punch)
        mix_left = np.tanh(mix_left)
        mix_right = np.tanh(mix_right)

        # Stack into (N, 2) stereo float32 array
        stereo_mix = np.column_stack((mix_left, mix_right)).astype(np.float32)
        return stereo_mix

    def render_to_wav_bytes(self, composition: Composition) -> bytes:
        """Renders composition into a complete, standard 16-bit stereo WAV byte sequence."""
        stereo_float32 = self.render(composition)
        pcm_int16 = np.int16(np.clip(stereo_float32 * 32767.0, -32768, 32767))
        pcm_bytes = pcm_int16.tobytes()
        return Synthesizer._create_wav_header(pcm_bytes, self.sample_rate, num_channels=2)

    def export_to_wav_file(self, composition: Composition, output_filepath: str):
        """Renders composition and writes it directly to the specified WAV file."""
        wav_bytes = self.render_to_wav_bytes(composition)
        with open(output_filepath, "wb") as f:
            f.write(wav_bytes)
