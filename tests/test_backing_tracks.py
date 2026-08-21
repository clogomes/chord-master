"""Unit tests for synthesized rhythm backing track engine and drum instruments."""
import unittest
import numpy as np
from audio.backing_tracks import (
    synthesize_kick,
    synthesize_snare,
    synthesize_hihat,
    synthesize_ride,
    BACKING_TRACK_LIBRARY,
    RhythmPattern,
    BackingTrackPlayer,
)


class TestBackingTracks(unittest.TestCase):

    def test_drum_synthesis_shapes_and_ranges(self):
        # 1. Kick
        kick = synthesize_kick()
        self.assertIsInstance(kick, np.ndarray)
        self.assertGreater(len(kick), 1000)
        self.assertTrue(np.all(kick >= -1.0) and np.all(kick <= 1.0))
        self.assertNotEqual(np.max(kick), 0.0)

        # 2. Snare
        snare = synthesize_snare()
        self.assertIsInstance(snare, np.ndarray)
        self.assertGreater(len(snare), 1000)
        self.assertTrue(np.all(snare >= -1.0) and np.all(snare <= 1.0))
        self.assertNotEqual(np.max(snare), 0.0)

        # 3. Closed & Open Hihat
        hihat_closed = synthesize_hihat(open=False)
        self.assertIsInstance(hihat_closed, np.ndarray)
        self.assertGreater(len(hihat_closed), 500)

        hihat_open = synthesize_hihat(open=True)
        self.assertIsInstance(hihat_open, np.ndarray)
        self.assertGreater(len(hihat_open), len(hihat_closed))

        # 4. Ride
        ride = synthesize_ride()
        self.assertIsInstance(ride, np.ndarray)
        self.assertGreater(len(ride), 2000)

    def test_backing_track_library_patterns(self):
        self.assertGreaterEqual(len(BACKING_TRACK_LIBRARY), 5)
        valid_instruments = {"kick", "snare", "hihat_closed", "hihat_open", "ride", "rimshot"}

        for pattern_id, pattern in BACKING_TRACK_LIBRARY.items():
            self.assertIsInstance(pattern, RhythmPattern)
            self.assertEqual(pattern.id, pattern_id)
            self.assertTrue(len(pattern.name_pt) > 0)
            self.assertIn(pattern.time_signature, ["4/4", "3/4", "6/8"])
            self.assertEqual(len(pattern.grid), pattern.steps_per_bar, f"Inconsistência de passos no padrão {pattern_id}")

            for step in pattern.grid:
                self.assertIsInstance(step, list)
                for inst in step:
                    self.assertIn(inst, valid_instruments, f"Instrumento inválido '{inst}' no padrão {pattern_id}")

    def test_no_duplicate_grids(self):
        """Asserts that no two patterns in the library share an identical grid."""
        seen = {}
        for pattern_id, pattern in BACKING_TRACK_LIBRARY.items():
            grid_key = tuple(tuple(sorted(step)) for step in pattern.grid)
            if grid_key in seen:
                self.fail(
                    f"Grelha duplicada: '{seen[grid_key]}' e '{pattern_id}' "
                    f"têm a mesma grelha de {len(pattern.grid)} passos."
                )
            seen[grid_key] = pattern_id

    def test_backing_track_player_lifecycle(self):
        player = BackingTrackPlayer(bpm=120, volume=0.5)
        self.assertEqual(player.bpm, 120)
        self.assertEqual(player.volume, 0.5)
        self.assertFalse(player.is_playing)

        # Tempo and volume bounds
        player.set_bpm(300)
        self.assertEqual(player.bpm, 240)
        player.set_bpm(20)
        self.assertEqual(player.bpm, 40)

        player.set_volume(1.5)
        self.assertEqual(player.volume, 1.0)
        player.set_volume(-0.5)
        self.assertEqual(player.volume, 0.0)

        # Start and Stop
        player.start(pattern_id="rock", bpm=110)
        self.assertTrue(player.is_playing)
        self.assertIsNotNone(player.current_pattern)
        self.assertEqual(player.current_pattern.id, "rock")

        player.stop()
        self.assertFalse(player.is_playing)


if __name__ == "__main__":
    unittest.main()
