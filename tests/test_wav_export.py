"""Tests for Phase 55: Exporting Composition to standard WAV files."""
import io
import os
import tempfile
import unittest
import wave
import numpy as np

from core.composition import Composition, ChordEvent, RhythmTrack
from core.compositions import get_template_composition
from audio.composition_renderer import CompositionRenderer
from audio.backing_tracks import BACKING_TRACK_LIBRARY


class TestWavExport(unittest.TestCase):
    def setUp(self):
        self.renderer = CompositionRenderer(sample_rate=44100)
        self.tmp_dir = tempfile.mkdtemp()

    def tearDown(self):
        import shutil
        if os.path.exists(self.tmp_dir):
            shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_render_to_wav_bytes_creates_valid_wave_header(self):
        comp = get_template_composition("rock_basic")
        # Add a couple of chord events
        comp.chords = [
            ChordEvent(root="C", chord_type="major", start_beat=0.0, duration_beats=2.0, instrument="piano"),
            ChordEvent(root="G", chord_type="major", start_beat=2.0, duration_beats=2.0, instrument="guitar"),
        ]
        wav_bytes = self.renderer.render_to_wav_bytes(comp)
        self.assertIsInstance(wav_bytes, bytes)
        self.assertGreater(len(wav_bytes), 44)  # Greater than standard 44-byte WAV header

        # Read back using wave standard library
        with wave.open(io.BytesIO(wav_bytes), "rb") as wf:
            self.assertEqual(wf.getnchannels(), 2, "Must be stereo (2 channels)")
            self.assertEqual(wf.getsampwidth(), 2, "Must be 16-bit (2 bytes per sample)")
            self.assertEqual(wf.getframerate(), 44100, "Must be 44100 Hz sample rate")
            
            # Expected duration ≈ (4 bars * 4 beats/bar * 60 / 100 bpm) + 3.0s tail
            # 4 * 4 * 0.6 = 9.6s + 3.0s = 12.6s
            expected_frames = int(12.6 * 44100)
            actual_frames = wf.getnframes()
            self.assertAlmostEqual(actual_frames, expected_frames, delta=4410)  # Within 100ms tolerance

    def test_export_to_wav_file_writes_file_correctly(self):
        comp = get_template_composition("pop")
        out_path = os.path.join(self.tmp_dir, "test_output.wav")
        self.renderer.export_to_wav_file(comp, out_path)

        self.assertTrue(os.path.exists(out_path))
        self.assertGreater(os.path.getsize(out_path), 1000)

        with wave.open(out_path, "rb") as wf:
            self.assertEqual(wf.getnchannels(), 2)
            self.assertEqual(wf.getsampwidth(), 2)
            self.assertEqual(wf.getframerate(), 44100)
            frames = wf.readframes(wf.getnframes())
            self.assertGreater(len(frames), 0)


if __name__ == "__main__":
    unittest.main()
