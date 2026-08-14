"""Unit tests for microphone pitch detection algorithms and frequency mapping."""
import math
import unittest
import numpy as np
from core.notes import Note
from audio.pitch_listener import detect_pitch_from_samples, PitchListener


class TestPitchDetection(unittest.TestCase):

    def _generate_sine_wave(self, freq: float, sample_rate: int = 44100, num_samples: int = 2048) -> np.ndarray:
        t = np.arange(num_samples) / float(sample_rate)
        return (0.7 * np.sin(2.0 * np.pi * freq * t)).astype(np.float32)

    def test_detect_a4_440hz(self):
        # A4 = 440 Hz (MIDI 69)
        samples = self._generate_sine_wave(440.0)
        note, cents, conf, f0 = detect_pitch_from_samples(samples, sample_rate=44100)

        self.assertIsNotNone(note)
        self.assertEqual(note.pitch, "A")
        self.assertEqual(note.octave, 4)
        self.assertEqual(note.midi, 69)
        self.assertAlmostEqual(f0, 440.0, delta=2.0)
        self.assertLess(abs(cents), 10.0)
        self.assertGreater(conf, 0.8)

    def test_detect_c4_middle_c(self):
        # C4 = 261.63 Hz (MIDI 60)
        samples = self._generate_sine_wave(261.63)
        note, cents, conf, f0 = detect_pitch_from_samples(samples, sample_rate=44100)

        self.assertIsNotNone(note)
        self.assertEqual(note.pitch, "C")
        self.assertEqual(note.octave, 4)
        self.assertEqual(note.midi, 60)
        self.assertAlmostEqual(f0, 261.63, delta=2.0)

    def test_detect_e2_guitar_low_e(self):
        # E2 = 82.41 Hz (MIDI 40, lowest string on standard guitar)
        samples = self._generate_sine_wave(82.41)
        note, cents, conf, f0 = detect_pitch_from_samples(samples, sample_rate=44100)

        self.assertIsNotNone(note)
        self.assertEqual(note.pitch, "E")
        self.assertEqual(note.octave, 2)
        self.assertEqual(note.midi, 40)

    def test_silence_and_noise_rejection(self):
        # Zero silence
        silence = np.zeros(2048, dtype=np.float32)
        note, cents, conf, f0 = detect_pitch_from_samples(silence, sample_rate=44100)
        self.assertIsNone(note)

        # White noise without periodic pitch
        np.random.seed(42)
        noise = (0.005 * np.random.randn(2048)).astype(np.float32)
        note, cents, conf, f0 = detect_pitch_from_samples(noise, sample_rate=44100)
        self.assertIsNone(note)

    def test_pitch_listener_instance(self):
        listener = PitchListener()
        self.assertFalse(listener.is_listening)
        self.assertEqual(listener.sample_rate, 44100)
        self.assertEqual(listener.block_size, 2048)


if __name__ == "__main__":
    unittest.main()
