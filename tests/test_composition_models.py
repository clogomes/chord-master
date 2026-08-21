"""Comprehensive unit tests for Composition Studio data models and persistence (Phase 40)."""
import os
import tempfile
import unittest
from core.composition import ChordEvent, RhythmTrack, Composition
from core.compositions import (
    get_template_composition,
    save_user_composition,
    load_user_compositions,
    delete_user_composition,
)
from audio.backing_tracks import BACKING_TRACK_LIBRARY


class TestCompositionModels(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_json = os.path.join(self.temp_dir.name, "test_compositions.json")

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_chord_event_roundtrip(self):
        ce = ChordEvent(
            root="Bb",
            chord_type="dom7",
            start_beat=2.5,
            duration_beats=1.5,
            instrument="guitar",
        )
        d = ce.to_dict()
        self.assertEqual(d["root"], "Bb")
        self.assertEqual(d["chord_type"], "dom7")
        self.assertEqual(d["start_beat"], 2.5)
        self.assertEqual(d["duration_beats"], 1.5)
        self.assertEqual(d["instrument"], "guitar")

        reconstructed = ChordEvent.from_dict(d)
        self.assertEqual(reconstructed.root, "Bb")
        self.assertEqual(reconstructed.chord_type, "dom7")
        self.assertEqual(reconstructed.start_beat, 2.5)
        self.assertEqual(reconstructed.duration_beats, 1.5)
        self.assertEqual(reconstructed.instrument, "guitar")

    def test_rhythm_track_roundtrip(self):
        grid = [["kick", "hihat_closed"], [], ["snare"], ["hihat_open"]]
        rt = RhythmTrack(steps_per_bar=16, grid=grid, volume=0.75, muted=False)
        d = rt.to_dict()
        self.assertEqual(d["steps_per_bar"], 16)
        self.assertEqual(d["grid"], grid)
        self.assertEqual(d["volume"], 0.75)
        self.assertFalse(d["muted"])

        reconstructed = RhythmTrack.from_dict(d)
        self.assertEqual(reconstructed.steps_per_bar, 16)
        self.assertEqual(reconstructed.grid, grid)
        self.assertEqual(reconstructed.volume, 0.75)
        self.assertFalse(reconstructed.muted)

    def test_rhythm_pattern_adapter_all_12_library_patterns(self):
        for pattern_id, pattern in BACKING_TRACK_LIBRARY.items():
            # Test 1-bar expansion
            rt1 = RhythmTrack.from_pattern(pattern, bars=1, volume=0.85)
            self.assertEqual(rt1.steps_per_bar, pattern.steps_per_bar)
            self.assertEqual(len(rt1.grid), len(pattern.grid))
            self.assertEqual(rt1.volume, 0.85)
            self.assertFalse(rt1.muted)
            self.assertEqual(rt1.grid, pattern.grid)

            # Test 4-bar expansion
            rt4 = RhythmTrack.from_pattern(pattern, bars=4, volume=0.85)
            self.assertEqual(len(rt4.grid), 4 * pattern.steps_per_bar)

    def test_composition_roundtrip(self):
        chords = [
            ChordEvent("C", "major", 0.0, 2.0, "piano"),
            ChordEvent("G", "dom7", 2.0, 2.0, "piano"),
            ChordEvent("Am", "minor", 4.0, 2.0, "guitar"),
            ChordEvent("F", "major", 6.0, 2.0, "guitar"),
        ]
        rhythm = RhythmTrack.from_pattern(BACKING_TRACK_LIBRARY["rock_basic"])
        comp = Composition(
            id="my_first_song",
            title="Minha Primeira Canção",
            bpm=125,
            time_signature="4/4",
            bars=8,
            rhythm=rhythm,
            chords=chords,
            master_volume=0.9,
            schema_version=1,
        )

        d = comp.to_dict()
        self.assertEqual(d["id"], "my_first_song")
        self.assertEqual(d["title"], "Minha Primeira Canção")
        self.assertEqual(d["bpm"], 125)
        self.assertEqual(d["bars"], 8)
        self.assertEqual(len(d["chords"]), 4)
        self.assertEqual(d["schema_version"], 1)

        loaded = Composition.from_dict(d)
        self.assertEqual(loaded.id, comp.id)
        self.assertEqual(loaded.title, comp.title)
        self.assertEqual(loaded.bpm, 125)
        self.assertEqual(loaded.bars, 8)
        self.assertEqual(len(loaded.chords), 4)
        self.assertEqual(loaded.chords[2].root, "Am")
        self.assertEqual(loaded.chords[2].instrument, "guitar")
        self.assertEqual(loaded.rhythm.steps_per_bar, 16)

    def test_persistence_save_load_delete(self):
        comp1 = get_template_composition("rock_basic")
        comp1.id = "comp_1"
        comp1.title = "Rock Jam"

        comp2 = get_template_composition("bossa_nova")
        comp2.id = "comp_2"
        comp2.title = "Bossa Session"

        # Save comp1 and comp2
        save_user_composition(comp1, filepath=self.test_json)
        save_user_composition(comp2, filepath=self.test_json)

        loaded = load_user_compositions(filepath=self.test_json)
        self.assertEqual(len(loaded), 2)
        ids = [c.id for c in loaded]
        self.assertIn("comp_1", ids)
        self.assertIn("comp_2", ids)

        # Update comp1
        comp1.bpm = 140
        save_user_composition(comp1, filepath=self.test_json)
        loaded_after_update = load_user_compositions(filepath=self.test_json)
        self.assertEqual(len(loaded_after_update), 2)
        c1_loaded = next(c for c in loaded_after_update if c.id == "comp_1")
        self.assertEqual(c1_loaded.bpm, 140)

        # Delete comp2
        deleted = delete_user_composition("comp_2", filepath=self.test_json)
        self.assertTrue(deleted)
        loaded_after_del = load_user_compositions(filepath=self.test_json)
        self.assertEqual(len(loaded_after_del), 1)
        self.assertEqual(loaded_after_del[0].id, "comp_1")

    def test_schema_backward_compatibility_with_missing_fields(self):
        sparse_data = {
            "id": "legacy_comp",
            "title": "Antiga Composição",
            # Missing bpm, time_signature, bars, rhythm, chords, notes, schema_version, etc.
        }
        comp = Composition.from_dict(sparse_data)
        self.assertEqual(comp.id, "legacy_comp")
        self.assertEqual(comp.title, "Antiga Composição")
        self.assertEqual(comp.bpm, 100)
        self.assertEqual(comp.time_signature, "4/4")
        self.assertEqual(comp.bars, 4)
        self.assertEqual(comp.chords, [])
        self.assertEqual(comp.notes, [])
        self.assertEqual(comp.rhythm.steps_per_bar, 16)
        self.assertEqual(comp.schema_version, 2)


if __name__ == "__main__":
    unittest.main()
