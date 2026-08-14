"""Unit tests for the sound synthesizer and Karplus-Strong physical modeling synthesis."""
import unittest
import wave
import io
from audio.synthesizer import Synthesizer


class TestSynthesizer(unittest.TestCase):
    """Validates the generation of sound waves and physical modeling audio."""

    def test_generate_single_frequency(self):
        """Validates additive synthesis output for a single frequency note (A4 440 Hz)."""
        wav_bytes = Synthesizer.generate_single_frequency(440.0, duration=0.5, volume=0.5)
        self.assertIsInstance(wav_bytes, bytes)
        self.assertGreater(len(wav_bytes), 44)  # RIFF header is 44 bytes

        # Check wave file validity
        with wave.open(io.BytesIO(wav_bytes), "rb") as wf:
            self.assertEqual(wf.getnchannels(), 1)
            self.assertEqual(wf.getsampwidth(), 2)
            self.assertEqual(wf.getframerate(), Synthesizer.SAMPLE_RATE)
            self.assertGreater(wf.getnframes(), 0)

    def test_generate_plucked_string_karplus_strong(self):
        """Validates Karplus-Strong physical modeling for various string guitar frequencies."""
        test_frequencies = [82.4, 110.0, 146.8, 196.0, 246.9, 329.6, 440.0]
        for freq in test_frequencies:
            wav_bytes = Synthesizer.generate_plucked_string(freq, duration=0.6, volume=0.5)
            self.assertIsInstance(wav_bytes, bytes)
            self.assertGreater(len(wav_bytes), 44)

            with wave.open(io.BytesIO(wav_bytes), "rb") as wf:
                self.assertEqual(wf.getnchannels(), 1)
                self.assertEqual(wf.getsampwidth(), 2)
                self.assertEqual(wf.getframerate(), Synthesizer.SAMPLE_RATE)
                self.assertGreater(wf.getnframes(), 0)

    def test_generate_polyphonic_chords(self):
        """Validates polyphonic chord wave generation."""
        c_major_freqs = [261.63, 329.63, 392.00]
        wav_bytes = Synthesizer.generate_polyphonic(c_major_freqs, duration=0.8, volume=0.5)
        self.assertIsInstance(wav_bytes, bytes)
        self.assertGreater(len(wav_bytes), 44)

        with wave.open(io.BytesIO(wav_bytes), "rb") as wf:
            self.assertEqual(wf.getnchannels(), 1)
            self.assertEqual(wf.getsampwidth(), 2)
            self.assertEqual(wf.getframerate(), Synthesizer.SAMPLE_RATE)
            self.assertGreater(wf.getnframes(), 0)

    def test_edge_cases_zero_and_empty(self):
        """Validates graceful handling of zero frequencies or zero duration."""
        wav_empty = Synthesizer.generate_plucked_string(0.0, duration=0.5)
        self.assertIsInstance(wav_empty, bytes)

        wav_poly_empty = Synthesizer.generate_polyphonic([])
        self.assertIsInstance(wav_poly_empty, bytes)


if __name__ == "__main__":
    unittest.main()
