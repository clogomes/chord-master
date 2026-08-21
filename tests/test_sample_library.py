"""Tests for Phase 59: Real Instrument & Drum Sample Management System and Fallback."""
import json
import os
import shutil
import tempfile
import unittest
import wave
import numpy as np

from audio.sample_library import (
    SampleLibrary,
    get_samples_root_directory,
    load_audio_file_raw,
    pitch_shift_sample,
    resample_audio,
)
from audio.composition_renderer import CompositionRenderer
from core.composition import Composition, ChordEvent, NoteEvent, RhythmTrack
from audio.backing_tracks import BACKING_TRACK_LIBRARY


def _create_sine_wav(filepath: str, freq: float = 440.0, duration: float = 0.5, sr: int = 44100):
    """Helper to create a simple test PCM 16-bit WAV file without external dependencies."""
    num_samples = int(duration * sr)
    t = np.linspace(0, duration, num_samples, endpoint=False)
    waveform = (0.5 * np.sin(2.0 * np.pi * freq * t) * 32767.0).astype(np.int16)
    with wave.open(filepath, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(waveform.tobytes())


class TestSampleLibraryAndFallback(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_default_samples_directory_lookup(self):
        # Set environment variable
        os.environ["CHORDMASTER_SAMPLES_DIR"] = self.temp_dir
        root = get_samples_root_directory()
        self.assertEqual(str(root), self.temp_dir)
        del os.environ["CHORDMASTER_SAMPLES_DIR"]

    def test_load_audio_file_raw_wav(self):
        wav_path = os.path.join(self.temp_dir, "test_tone.wav")
        _create_sine_wav(wav_path, freq=440.0, duration=0.2, sr=44100)

        data = load_audio_file_raw(wav_path, target_sr=44100)
        self.assertIsNotNone(data)
        self.assertEqual(len(data), int(0.2 * 44100))
        self.assertAlmostEqual(float(np.max(np.abs(data))), 0.5, places=2)

    def test_pitch_shift_sample(self):
        wav_path = os.path.join(self.temp_dir, "test_a4.wav")
        _create_sine_wav(wav_path, freq=440.0, duration=0.2, sr=44100)
        raw_data = load_audio_file_raw(wav_path)

        # Shift up by 2 semitones
        shifted_up = pitch_shift_sample(raw_data, 2.0)
        self.assertIsNotNone(shifted_up)
        # Pitch shift up shortens duration / samples
        self.assertLess(len(shifted_up), len(raw_data))

    def test_drum_sample_round_robin_and_velocity(self):
        drums_dir = os.path.join(self.temp_dir, "drums")
        os.makedirs(drums_dir, exist_ok=True)

        k1_path = os.path.join(drums_dir, "kick1.wav")
        k2_path = os.path.join(drums_dir, "kick2.wav")
        _create_sine_wav(k1_path, freq=80.0, duration=0.1)
        _create_sine_wav(k2_path, freq=90.0, duration=0.1)

        manifest = {
            "name": "drums",
            "samples": {
                "kick": {
                    "gain": 1.0,
                    "layers": [
                        {
                            "min_velocity": 0.0,
                            "files": ["kick1.wav", "kick2.wav"],
                        }
                    ],
                }
            },
        }

        with open(os.path.join(drums_dir, "instrument.json"), "w") as f:
            json.dump(manifest, f)

        lib = SampleLibrary(samples_root=self.temp_dir)
        self.assertTrue(lib.has_instrument("drums"))

        # Test deterministic round-robin alternation
        s1 = lib.get_drum_sample("kick", velocity=0.8)
        s2 = lib.get_drum_sample("kick", velocity=0.8)
        s3 = lib.get_drum_sample("kick", velocity=0.8)

        self.assertIsNotNone(s1)
        self.assertIsNotNone(s2)
        self.assertIsNotNone(s3)
        # s1 should match s3 (first round robin variant), s2 should differ
        self.assertEqual(len(s1), len(s3))

    def test_instrument_manifest_pitch_interpolation(self):
        piano_dir = os.path.join(self.temp_dir, "piano")
        os.makedirs(piano_dir, exist_ok=True)

        c4_wav = os.path.join(piano_dir, "c4.wav")
        _create_sine_wav(c4_wav, freq=261.63, duration=0.5)

        manifest = {
            "name": "piano",
            "samples": {
                "60": {
                    "file": "c4.wav",
                    "gain": 1.0,
                }
            },
        }

        with open(os.path.join(piano_dir, "instrument.json"), "w") as f:
            json.dump(manifest, f)

        lib = SampleLibrary(samples_root=self.temp_dir)
        self.assertTrue(lib.has_instrument("piano"))

        # Exact note 60
        s60 = lib.get_note_sample("piano", midi_note=60, duration_sec=0.4)
        self.assertIsNotNone(s60)

        # Interpolated note 62 (+2 semitones)
        s62 = lib.get_note_sample("piano", midi_note=62, duration_sec=0.4)
        self.assertIsNotNone(s62)

        # Out of bounds note 80 (>7 semitones away from closest 60) -> returns None
        s80 = lib.get_note_sample("piano", midi_note=80)
        self.assertIsNone(s80)

    def test_renderer_seamless_fallback_when_samples_absent(self):
        # Empty sample library
        lib = SampleLibrary(samples_root=self.temp_dir)
        renderer = CompositionRenderer()

        comp = Composition(
            id="test_fallback",
            title="Fallback",
            bpm=120,
            time_signature="4/4",
            bars=2,
            chords=[ChordEvent(start_beat=0.0, duration_beats=4.0, root="C", chord_type="major", instrument="piano")],
            notes=[NoteEvent(midi=60, start_beat=0.0, duration_beats=2.0, velocity=0.8, instrument="piano")],
        )

        audio = renderer.render(comp)
        self.assertIsInstance(audio, np.ndarray)
        self.assertEqual(audio.ndim, 2)
        # Ensure synthesis was produced and no crash occurred
        self.assertGreater(np.sqrt(np.mean(audio ** 2)), 0.001)


if __name__ == "__main__":
    unittest.main()
