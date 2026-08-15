import unittest
import wave
import io
from audio.synthesizer import Synthesizer

class TestSynthesizerRealism(unittest.TestCase):
    def test_piano_synthesis_valid_wav(self):
        """Test piano synthesis produces valid WAV bytes for various notes with realism features."""
        # Test notes: A2 (110Hz), C4 (261.63Hz), G6 (1567.98Hz)
        test_cases = [
            (110.0, 1.0, 0.5),
            (261.63, 0.5, 0.8),
            (1567.98, 0.2, 0.3)
        ]
        
        for freq, duration, volume in test_cases:
            with self.subTest(freq=freq):
                wav_bytes = Synthesizer.generate_single_frequency(freq, duration=duration, volume=volume)
                
                self.assertIsInstance(wav_bytes, bytes)
                self.assertGreater(len(wav_bytes), 44)  # At least larger than WAV header
                
                # Check valid WAV header and duration
                with wave.open(io.BytesIO(wav_bytes), 'rb') as w:
                    self.assertEqual(w.getnchannels(), 1)
                    self.assertEqual(w.getsampwidth(), 2)
                    self.assertEqual(w.getframerate(), 44100)
                    
                    frames = w.getnframes()
                    actual_duration = frames / 44100.0
                    
                    # Within 5% tolerance
                    self.assertAlmostEqual(actual_duration, duration, delta=duration * 0.05)

    def test_guitar_synthesis_valid_wav(self):
        """Test guitar Karplus-Strong synthesis produces valid WAV bytes with body filter and vibrato."""
        # Test low string (E2 ~82.4Hz) soft pluck (warmer) and high string (E4 ~329.6Hz) hard pluck (brighter)
        test_cases = [
            (82.4, 1.5, 0.4),   # Warmer tone, longer duration
            (329.6, 0.8, 0.9)   # Brighter tone
        ]
        
        for freq, duration, volume in test_cases:
            with self.subTest(freq=freq):
                wav_bytes = Synthesizer.generate_plucked_string(freq, duration=duration, volume=volume)
                
                self.assertIsInstance(wav_bytes, bytes)
                self.assertGreater(len(wav_bytes), 44)
                
                # Check valid WAV header and duration
                with wave.open(io.BytesIO(wav_bytes), 'rb') as w:
                    self.assertEqual(w.getnchannels(), 1)
                    self.assertEqual(w.getsampwidth(), 2)
                    self.assertEqual(w.getframerate(), 44100)
                    
                    frames = w.getnframes()
                    actual_duration = frames / 44100.0
                    
                    # Within 5% tolerance
                    self.assertAlmostEqual(actual_duration, duration, delta=duration * 0.05)

if __name__ == '__main__':
    unittest.main()
