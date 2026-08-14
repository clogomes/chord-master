"""Unit tests for musical scales and modes."""
import unittest
from core.notes import Note
from core.scales import Scale, get_scale_notes, SCALE_TYPES


class TestScales(unittest.TestCase):

    def test_c_major_scale(self):
        c_maj = Scale(Note("C4"), "major")
        pitches = [n.pitch for n in c_maj.notes]
        expected = ["C", "D", "E", "F", "G", "A", "B", "C"]
        self.assertEqual(pitches, expected)
        self.assertEqual(len(c_maj.notes), 8)

    def test_a_natural_minor_scale(self):
        a_min = Scale(Note("A3"), "natural_minor")
        pitches = [n.pitch for n in a_min.notes]
        expected = ["A", "B", "C", "D", "E", "F", "G", "A"]
        self.assertEqual(pitches, expected)

    def test_a_harmonic_minor_scale(self):
        a_harm = Scale(Note("A3"), "harmonic_minor")
        pitches = [n.pitch for n in a_harm.notes]
        expected = ["A", "B", "C", "D", "E", "F", "G#", "A"]
        self.assertEqual(pitches, expected)

    def test_c_pentatonic_major(self):
        c_penta = Scale(Note("C4"), "major_pentatonic")
        pitches = [n.pitch for n in c_penta.notes]
        expected = ["C", "D", "E", "G", "A", "C"]
        self.assertEqual(pitches, expected)

    def test_a_pentatonic_minor(self):
        a_penta = Scale(Note("A3"), "minor_pentatonic")
        pitches = [n.pitch for n in a_penta.notes]
        expected = ["A", "C", "D", "E", "G", "A"]
        self.assertEqual(pitches, expected)

    def test_get_scale_notes_helper(self):
        notes = get_scale_notes("G", "major", octave=4)
        pitches = [n.pitch for n in notes]
        # G Major has F#
        self.assertIn("F#", pitches)
        self.assertEqual(pitches[0], "G")

    def test_all_scale_types_structure_and_intervals(self):
        self.assertGreaterEqual(len(SCALE_TYPES), 14)

        for key, scale_def in SCALE_TYPES.items():
            self.assertEqual(scale_def.key, key)
            self.assertTrue(len(scale_def.name_pt) > 0)
            self.assertTrue(len(scale_def.name_en) > 0)
            self.assertTrue(len(scale_def.formula_steps) > 0)
            self.assertTrue(len(scale_def.formula_degrees) > 0)
            self.assertTrue(len(scale_def.description) > 0)

            # Intervals rule: starts at 0, ends at 12, strictly increasing
            self.assertEqual(scale_def.intervals[0], 0, f"Escala {key} não começa em 0")
            self.assertEqual(scale_def.intervals[-1], 12, f"Escala {key} não termina em 12 (oitava)")
            for i in range(len(scale_def.intervals) - 1):
                self.assertLess(
                    scale_def.intervals[i],
                    scale_def.intervals[i + 1],
                    f"Intervalos não estritamente crescentes em {key}: {scale_def.intervals}"
                )

    def test_new_modes_and_exotic_scales(self):
        # 1. D Phrygian (D, Eb, F, G, A, Bb, C, D)
        d_phryg = Scale(Note("D4"), "phrygian")
        self.assertEqual([n.pitch for n in d_phryg.notes], ["D", "D#", "F", "G", "A", "A#", "C", "D"])

        # 2. F Lydian (F, G, A, B, C, D, E, F)
        f_lyd = Scale(Note("F4"), "lydian")
        self.assertEqual([n.pitch for n in f_lyd.notes], ["F", "G", "A", "B", "C", "D", "E", "F"])

        # 3. B Locrian (B, C, D, E, F, G, A, B)
        b_loc = Scale(Note("B3"), "locrian")
        self.assertEqual([n.pitch for n in b_loc.notes], ["B", "C", "D", "E", "F", "G", "A", "B"])

        # 4. Whole tone
        c_wt = Scale(Note("C4"), "whole_tone")
        self.assertEqual(len(c_wt.notes), 7)

        # 5. Chromatic
        c_chrom = Scale(Note("C4"), "chromatic")
        self.assertEqual(len(c_chrom.notes), 13)


if __name__ == "__main__":
    unittest.main()
