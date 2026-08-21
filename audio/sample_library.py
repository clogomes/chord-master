"""Real Instrument & Drum Sample Management System with graceful synthesis fallback (Phase 59).

Features:
- Sample manifest parsing (instrument.json): note->file mappings, velocity layers, round-robin.
- Sample loading via soundfile (WAV/FLAC/OGG/MP3) with wave standard library fallback for WAV.
- High-quality sample pitch transposition (resample_poly using scipy when available, or linear np.interp).
- Deterministic round-robin counters per instrument/note for repeatable rendering.
- 100% graceful fallback to built-in synthesis if samples are missing or unreadable.
"""
import json
import math
import os
from fractions import Fraction
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
import numpy as np

# Optional soundfile import
try:
    import soundfile as sf
    HAS_SOUNDFILE = True
except Exception:
    HAS_SOUNDFILE = False

# Optional scipy resample_poly import
try:
    from scipy.signal import resample_poly
    HAS_SCIPY = True
except Exception:
    HAS_SCIPY = False

import wave


SAMPLE_RATE = 44100


def get_samples_root_directory() -> Path:
    """
    Finds the root directory for external audio samples in order of precedence:
    1. CHORDMASTER_SAMPLES_DIR environment variable
    2. data/local_settings.json (samples_dir field)
    3. ~/Documents/ChordMaster/Samples
    """
    env_dir = os.environ.get("CHORDMASTER_SAMPLES_DIR")
    if env_dir and os.path.isdir(env_dir):
        return Path(env_dir)

    # Local settings (gitignored)
    local_settings_file = Path(__file__).resolve().parent.parent / "data" / "local_settings.json"
    if local_settings_file.exists():
        try:
            with open(local_settings_file, "r", encoding="utf-8") as f:
                cfg = json.load(f)
                custom_dir = cfg.get("samples_dir")
                if custom_dir and os.path.isdir(custom_dir):
                    return Path(custom_dir)
        except Exception:
            pass

    # Default fallback path
    return Path.home() / "Documents" / "ChordMaster" / "Samples"


def load_audio_file_raw(filepath: Union[str, Path], target_sr: int = SAMPLE_RATE) -> Optional[np.ndarray]:
    """
    Loads an audio file (mono/stereo) into a float32 1D or 2D numpy array normalized to [-1.0, 1.0].
    Uses soundfile if available, otherwise falls back to the standard library wave module for WAV files.
    """
    path_obj = Path(filepath)
    if not path_obj.exists() or not path_obj.is_file():
        return None

    # 1. Try soundfile
    if HAS_SOUNDFILE:
        try:
            data, sr = sf.read(str(path_obj), dtype="float32", always_2d=False)
            if sr != target_sr:
                data = resample_audio(data, sr, target_sr)
            return data.astype(np.float32)
        except Exception:
            pass

    # 2. Fallback: wave standard library for .wav files
    if path_obj.suffix.lower() == ".wav":
        try:
            with wave.open(str(path_obj), "rb") as wf:
                num_channels = wf.getnchannels()
                sample_width = wf.getsampwidth()
                sr = wf.getframerate()
                num_frames = wf.getnframes()
                raw_bytes = wf.readframes(num_frames)

                if sample_width == 2:
                    # 16-bit PCM
                    pcm_data = np.frombuffer(raw_bytes, dtype=np.int16).astype(np.float32) / 32768.0
                elif sample_width == 1:
                    # 8-bit unsigned
                    pcm_data = (np.frombuffer(raw_bytes, dtype=np.uint8).astype(np.float32) - 128.0) / 128.0
                elif sample_width == 3:
                    # 24-bit PCM
                    a8 = np.frombuffer(raw_bytes, dtype=np.uint8)
                    a32 = np.zeros(len(a8) // 3, dtype=np.int32)
                    a32 = (a8[0::3].astype(np.int32) << 8) | (a8[1::3].astype(np.int32) << 16) | (a8[2::3].astype(np.int32) << 24)
                    pcm_data = a32.astype(np.float32) / 2147483648.0
                else:
                    return None

                if num_channels == 2:
                    pcm_data = pcm_data.reshape(-1, 2)

                if sr != target_sr:
                    pcm_data = resample_audio(pcm_data, sr, target_sr)

                return pcm_data.astype(np.float32)
        except Exception:
            return None

    return None


def resample_audio(data: np.ndarray, orig_sr: int, target_sr: int) -> np.ndarray:
    """Resamples 1D or 2D audio array from orig_sr to target_sr."""
    if orig_sr == target_sr or len(data) == 0:
        return data

    ratio = target_sr / float(orig_sr)
    if HAS_SCIPY:
        frac = Fraction(ratio).limit_denominator(512)
        up, down = frac.numerator, frac.denominator
        if data.ndim == 1:
            return resample_poly(data, up, down).astype(np.float32)
        else:
            chans = [resample_poly(data[:, ch], up, down) for ch in range(data.shape[1])]
            return np.column_stack(chans).astype(np.float32)
    else:
        orig_len = len(data)
        target_len = int(orig_len * ratio)
        x_orig = np.linspace(0, 1, orig_len)
        x_target = np.linspace(0, 1, target_len)
        if data.ndim == 1:
            return np.interp(x_target, x_orig, data).astype(np.float32)
        else:
            chans = [np.interp(x_target, x_orig, data[:, ch]) for ch in range(data.shape[1])]
            return np.column_stack(chans).astype(np.float32)


def pitch_shift_sample(sample_data: np.ndarray, semitones: float) -> np.ndarray:
    """
    Shifts sample pitch by semitones using resample_poly with fraction denominator limiting.
    Positive semitones = higher pitch, shorter duration.
    """
    if abs(semitones) < 1e-4 or len(sample_data) == 0:
        return sample_data

    speed_ratio = math.pow(2.0, semitones / 12.0)
    
    if HAS_SCIPY:
        ratio = 1.0 / speed_ratio
        frac = Fraction(ratio).limit_denominator(512)
        up, down = frac.numerator, frac.denominator
        if sample_data.ndim == 1:
            return resample_poly(sample_data, up, down).astype(np.float32)
        else:
            chans = [resample_poly(sample_data[:, ch], up, down) for ch in range(sample_data.shape[1])]
            return np.column_stack(chans).astype(np.float32)
    else:
        orig_len = len(sample_data)
        target_len = max(1, int(orig_len / speed_ratio))
        x_orig = np.linspace(0, 1, orig_len)
        x_target = np.linspace(0, 1, target_len)
        if sample_data.ndim == 1:
            return np.interp(x_target, x_orig, sample_data).astype(np.float32)
        else:
            chans = [np.interp(x_target, x_orig, sample_data[:, ch]) for ch in range(sample_data.shape[1])]
            return np.column_stack(chans).astype(np.float32)


class SampleLibrary:
    """
    Manages external instrument and drum sample libraries.
    Provides deterministic round-robin playback and pitch shifting with caching.
    """
    _instance: Optional["SampleLibrary"] = None

    def __init__(self, samples_root: Optional[Union[str, Path]] = None):
        self.root_dir = Path(samples_root) if samples_root else get_samples_root_directory()
        self._manifests: Dict[str, dict] = {}
        self._audio_cache: Dict[str, np.ndarray] = {}
        self._shifted_cache: Dict[str, np.ndarray] = {}
        self._rr_counters: Dict[str, int] = {}
        self._scanned = False
        self.scan_library()

    @classmethod
    def get_instance(cls) -> "SampleLibrary":
        if cls._instance is None:
            cls._instance = SampleLibrary()
        return cls._instance

    def scan_library(self):
        """Scans the samples root directory for subdirectories containing instrument.json manifests."""
        self._manifests.clear()
        self._audio_cache.clear()
        self._shifted_cache.clear()
        self._rr_counters.clear()
        self._scanned = True

        if not self.root_dir.exists() or not self.root_dir.is_dir():
            return

        for item in self.root_dir.iterdir():
            if item.is_dir():
                manifest_file = item / "instrument.json"
                if manifest_file.exists() and manifest_file.is_file():
                    try:
                        with open(manifest_file, "r", encoding="utf-8") as f:
                            data = json.load(f)
                            inst_name = data.get("name", item.name).lower()
                            data["_dir"] = str(item)
                            self._manifests[inst_name] = data
                    except Exception:
                        pass

    def register_instrument_manifest(self, name: str, manifest_data: dict, base_dir: Union[str, Path]):
        """Directly registers an instrument manifest (useful for testing or custom paths)."""
        manifest_copy = dict(manifest_data)
        manifest_copy["_dir"] = str(base_dir)
        self._manifests[name.lower()] = manifest_copy

    def has_instrument(self, instrument_name: str) -> bool:
        return instrument_name.lower() in self._manifests

    def _get_next_rr_index(self, key: str, count: int) -> int:
        """Deterministic round-robin counter for repeatable audio rendering."""
        if count <= 1:
            return 0
        curr = self._rr_counters.get(key, 0)
        self._rr_counters[key] = (curr + 1) % count
        return curr

    def get_drum_sample(self, drum_instrument: str, velocity: float = 0.8) -> Optional[np.ndarray]:
        """
        Retrieves a drum sample for a specific drum instrument (e.g., 'kick', 'snare', 'hihat_closed').
        Selects velocity layer (switching, no crossfade) and deterministic round-robin variant.
        Returns 1D float32 audio or None if not available (graceful fallback).
        """
        manifest = self._manifests.get("drums") or self._manifests.get("drum_kit")
        if not manifest:
            return None

        drum_map = manifest.get("samples", {})
        inst_entry = drum_map.get(drum_instrument)
        if not inst_entry:
            return None

        base_dir = Path(manifest["_dir"])
        filename = None
        gain = float(inst_entry.get("gain", 1.0))

        if "layers" in inst_entry:
            layers = sorted(inst_entry["layers"], key=lambda l: l.get("min_velocity", 0.0))
            matched_layer = layers[0]
            for l in layers:
                if velocity >= l.get("min_velocity", 0.0):
                    matched_layer = l
            
            variants = matched_layer.get("files", [])
            if variants:
                rr_key = f"drum_{drum_instrument}_{matched_layer.get('min_velocity', 0)}"
                rr_idx = self._get_next_rr_index(rr_key, len(variants))
                filename = variants[rr_idx]
        elif "files" in inst_entry:
            variants = inst_entry["files"]
            if variants:
                rr_key = f"drum_{drum_instrument}"
                rr_idx = self._get_next_rr_index(rr_key, len(variants))
                filename = variants[rr_idx]
        elif "file" in inst_entry:
            filename = inst_entry["file"]

        if not filename:
            return None

        file_path = base_dir / filename
        cache_key = str(file_path)
        if cache_key not in self._audio_cache:
            loaded = load_audio_file_raw(file_path)
            if loaded is None:
                return None
            if loaded.ndim == 2:
                loaded = np.mean(loaded, axis=1)
            self._audio_cache[cache_key] = loaded

        raw_sample = self._audio_cache[cache_key]
        if gain != 1.0:
            return raw_sample * gain
        return raw_sample

    def get_note_sample(
        self,
        instrument: str,
        midi_note: int,
        duration_sec: float = 1.0,
        velocity: float = 0.8,
    ) -> Optional[np.ndarray]:
        """
        Retrieves an instrument note sample (e.g. 'piano', 'guitar', 'bass').
        Finds the nearest sample in the manifest (spacing <= 3-7 semitones), applies
        high-quality pitch transposition (scipy resample_poly / np.interp), and returns float32 audio.
        Returns None if instrument or sample is unavailable.
        """
        manifest = self._manifests.get(instrument.lower())
        if not manifest:
            return None

        samples_map = manifest.get("samples", {})
        if not samples_map:
            return None

        base_dir = Path(manifest["_dir"])

        available_midis = []
        for key_str in samples_map.keys():
            try:
                available_midis.append(int(key_str))
            except ValueError:
                pass

        if not available_midis:
            return None

        closest_midi = min(available_midis, key=lambda m: abs(m - midi_note))
        semitone_diff = midi_note - closest_midi

        if abs(semitone_diff) > 7:
            return None

        entry = samples_map[str(closest_midi)]
        gain = float(entry.get("gain", 1.0))
        filename = None

        if "layers" in entry:
            layers = sorted(entry["layers"], key=lambda l: l.get("min_velocity", 0.0))
            matched_layer = layers[0]
            for l in layers:
                if velocity >= l.get("min_velocity", 0.0):
                    matched_layer = l
            variants = matched_layer.get("files", [])
            if variants:
                rr_key = f"{instrument}_{closest_midi}_{matched_layer.get('min_velocity', 0)}"
                rr_idx = self._get_next_rr_index(rr_key, len(variants))
                filename = variants[rr_idx]
        elif "files" in entry:
            variants = entry["files"]
            if variants:
                rr_key = f"{instrument}_{closest_midi}"
                rr_idx = self._get_next_rr_index(rr_key, len(variants))
                filename = variants[rr_idx]
        elif "file" in entry:
            filename = entry["file"]

        if not filename:
            return None

        file_path = base_dir / filename
        cache_key = str(file_path)

        if cache_key not in self._audio_cache:
            loaded = load_audio_file_raw(file_path)
            if loaded is None:
                return None
            if loaded.ndim == 2:
                loaded = np.mean(loaded, axis=1)
            self._audio_cache[cache_key] = loaded

        base_audio = self._audio_cache[cache_key]

        shifted_key = f"{cache_key}__st_{semitone_diff}"
        if abs(semitone_diff) < 1e-4:
            shifted_audio = base_audio
        else:
            if shifted_key not in self._shifted_cache:
                self._shifted_cache[shifted_key] = pitch_shift_sample(base_audio, semitone_diff)
            shifted_audio = self._shifted_cache[shifted_key]

        target_samples = int(duration_sec * SAMPLE_RATE)
        if len(shifted_audio) > target_samples:
            fade_samples = min(int(0.01 * SAMPLE_RATE), target_samples)
            result = shifted_audio[:target_samples].copy()
            if fade_samples > 0:
                fade_out = np.linspace(1.0, 0.0, fade_samples, dtype=np.float32)
                result[-fade_samples:] *= fade_out
        else:
            result = shifted_audio.copy()

        if gain != 1.0:
            result *= gain

        return result
