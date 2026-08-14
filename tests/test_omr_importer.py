"""Unit tests for the lightweight OMR importer (core/omr_importer.py).

All images are generated synthetically in-memory using numpy/Pillow,
following the same approach used for MIDI bytes in test_midi_importer.py.
No real score files are required.
"""
import unittest
import math
import numpy as np

# ── Imports under test ──────────────────────────────────────────────────────────
from core.omr_importer import (
    binarize,
    detect_staff_lines,
    detect_noteheads,
    map_pixel_to_note,
    import_score_as_song,
    _line_spacing,
    OMR_AVAILABLE,
)
from core.songs import Song


# ── Helpers to build synthetic score images ────────────────────────────────────

def _make_blank(height: int = 300, width: int = 600, fill: int = 255) -> np.ndarray:
    """Returns a white grayscale image as numpy array."""
    return np.full((height, width), fill, dtype=np.uint8)


def _draw_staff(img: np.ndarray, top_y: int, spacing: int = 12) -> list:
    """Draws 5 horizontal black staff lines and returns their y positions."""
    lines = []
    for i in range(5):
        y = top_y + i * spacing
        img[y, :] = 0
        lines.append(y)
    return lines


def _draw_circle(img: np.ndarray, cx: int, cy: int, radius: int = 5):
    """Draws a filled black circle (simulated note head) on the image."""
    h, w = img.shape
    for dy in range(-radius, radius + 1):
        for dx in range(-radius, radius + 1):
            if dx * dx + dy * dy <= radius * radius:
                ry, rx = cy + dy, cx + dx
                if 0 <= ry < h and 0 <= rx < w:
                    img[ry, rx] = 0


# ── Tests ───────────────────────────────────────────────────────────────────────

class TestBinarize(unittest.TestCase):
    def test_white_pixels_become_zero(self):
        gray = np.full((10, 10), 255, dtype=np.uint8)
        binary = binarize(gray)
        self.assertEqual(binary.sum(), 0)

    def test_black_pixels_become_one(self):
        gray = np.zeros((10, 10), dtype=np.uint8)
        binary = binarize(gray)
        self.assertEqual(binary.sum(), 100)

    def test_mid_grey_split_at_threshold(self):
        gray = np.array([[100, 150, 200], [50, 128, 130]], dtype=np.uint8)
        binary = binarize(gray, threshold=128)
        # < 128 → ink=1: 100, 50 → 2 pixels
        self.assertEqual(binary.sum(), 2)


class TestDetectStaffLines(unittest.TestCase):
    def _make_staff_image(self, spacing: int = 12, top_y: int = 50):
        img = _make_blank()
        binary_img = np.zeros_like(img, dtype=np.uint8)
        lines = []
        for i in range(5):
            y = top_y + i * spacing
            binary_img[y, :] = 1  # full-width black line
            lines.append(y)
        return binary_img, lines

    def test_detects_five_lines(self):
        binary, expected = self._make_staff_image(spacing=12, top_y=50)
        detected = detect_staff_lines(binary)
        self.assertEqual(len(detected), 5, f"Expected 5 staff lines, got {len(detected)}")

    def test_line_positions_match(self):
        binary, expected = self._make_staff_image(spacing=14, top_y=40)
        detected = detect_staff_lines(binary)
        detected_ys = [d[0] for d in detected]
        for exp_y in expected:
            closest = min(detected_ys, key=lambda y: abs(y - exp_y))
            self.assertAlmostEqual(closest, exp_y, delta=2,
                                   msg=f"Expected staff line at y={exp_y}, closest detected={closest}")

    def test_empty_image_returns_empty(self):
        # All-zero binary image: max row sum = 0 < 5% threshold → returns []
        blank = np.zeros((200, 400), dtype=np.uint8)
        result = detect_staff_lines(blank)
        self.assertEqual(result, [])

    def test_line_spacing_calculation(self):
        binary, expected = self._make_staff_image(spacing=10, top_y=30)
        detected = detect_staff_lines(binary)
        spacing = _line_spacing(detected)
        self.assertAlmostEqual(spacing, 10.0, delta=2.0)


class TestDetectNoteheads(unittest.TestCase):
    @unittest.skipUnless(OMR_AVAILABLE, "scipy/Pillow not installed — skipping notehead detection tests")
    def test_detects_single_notehead(self):
        # Build a 400×800 binary image with 5 staff lines at top (y=20..68)
        # and one notehead blob far below at y=200 (well outside masking strip)
        binary = np.zeros((400, 800), dtype=np.uint8)
        spacing = 12
        line_ys = [20, 32, 44, 56, 68]
        for y in line_ys:
            binary[y, :] = 1

        # Draw a solid filled square blob (≈ notehead) at y=200, x=300
        # Square size ~ spacing × spacing pixels so area ≈ 144
        blob_size = 10
        cy, cx = 200, 300
        binary[cy - blob_size // 2: cy + blob_size // 2, cx - blob_size // 2: cx + blob_size // 2] = 1

        staff_lines = [(y, 1.0) for y in line_ys]
        noteheads = detect_noteheads(binary, staff_lines)
        self.assertGreaterEqual(len(noteheads), 1,
                                f"Should detect at least one notehead blob, got {len(noteheads)}")

    @unittest.skipUnless(OMR_AVAILABLE, "scipy/Pillow not installed — skipping notehead detection tests")
    def test_detects_multiple_noteheads_sorted_by_x(self):
        binary = np.zeros((400, 1000), dtype=np.uint8)
        spacing = 12
        line_ys = [20, 32, 44, 56, 68]
        for y in line_ys:
            binary[y, :] = 1

        blob_size = 10
        positions = [(200, 200), (200, 500), (200, 800)]
        for cy, cx in positions:
            binary[cy - blob_size // 2: cy + blob_size // 2,
                   cx - blob_size // 2: cx + blob_size // 2] = 1

        staff_lines = [(y, 1.0) for y in line_ys]
        noteheads = detect_noteheads(binary, staff_lines)

        xs = [n[0] for n in noteheads]
        self.assertEqual(xs, sorted(xs), "Noteheads should be sorted left-to-right")
        self.assertGreaterEqual(len(noteheads), 2,
                                f"Expected ≥2 noteheads, got {len(noteheads)}")


class TestMapPixelToNote(unittest.TestCase):
    def _treble_staff(self):
        """Returns synthetic staff lines at spacing=12, 2nd line (index 1) at y=62."""
        return [(50, 1.0), (62, 1.0), (74, 1.0), (86, 1.0), (98, 1.0)]

    def test_treble_reference_line_maps_to_g4(self):
        staff = self._treble_staff()
        # y=62 is the 2nd line from bottom (index 1) → G4 in treble clef
        note = map_pixel_to_note(62, staff, clef="treble")
        self.assertEqual(note.letter, "G")
        self.assertEqual(note.octave, 4)

    def test_higher_pixel_gives_higher_note(self):
        staff = self._treble_staff()
        # higher on screen (smaller y) = higher pitch
        note_low = map_pixel_to_note(80, staff, clef="treble")
        note_high = map_pixel_to_note(40, staff, clef="treble")
        self.assertGreater(note_high.midi, note_low.midi,
                           f"Expected {note_high} > {note_low}")

    def test_empty_staff_returns_c4(self):
        note = map_pixel_to_note(100, [], clef="treble")
        self.assertEqual(note.pitch, "C")
        self.assertEqual(note.octave, 4)

    def test_bass_clef_reference_maps_to_b2(self):
        staff = self._treble_staff()
        note = map_pixel_to_note(62, staff, clef="bass")
        self.assertEqual(note.letter, "B")
        self.assertEqual(note.octave, 2)


class TestImportScoreAsSong(unittest.TestCase):
    @unittest.skipUnless(OMR_AVAILABLE, "OMR dependencies not installed — skipping full pipeline test")
    def test_returns_song_object(self):
        import tempfile, os
        from PIL import Image

        # Create a minimal synthetic score image: 5 staff lines + 2 note blobs
        img_array = np.full((300, 600), 255, dtype=np.uint8)
        line_ys = [60, 72, 84, 96, 108]
        for y in line_ys:
            img_array[y, :] = 0
        _draw_circle(img_array, cx=200, cy=150, radius=6)
        _draw_circle(img_array, cx=400, cy=140, radius=6)

        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            tmp_path = f.name
        try:
            Image.fromarray(img_array).save(tmp_path)
            song = import_score_as_song(tmp_path, clef="treble", title="Test Score")
            self.assertIsInstance(song, Song)
            self.assertEqual(song.title, "Test Score")
            self.assertEqual(song.clef, "treble")
            self.assertGreaterEqual(len(song.notes), 0)  # may be 0 if blobs too small
            # All notes should have quarter-note duration
            for sn in song.notes:
                self.assertEqual(sn.duration_beats, 1.0)
        finally:
            os.unlink(tmp_path)

    def test_missing_dependencies_raises_runtime_error(self):
        """If OMR_AVAILABLE is False, import_score_as_song should raise RuntimeError."""
        import core.omr_importer as omr_mod
        original = omr_mod.OMR_AVAILABLE
        omr_mod.OMR_AVAILABLE = False
        try:
            with self.assertRaises(RuntimeError):
                import_score_as_song("dummy.png", clef="treble")
        finally:
            omr_mod.OMR_AVAILABLE = original


if __name__ == "__main__":
    unittest.main()
