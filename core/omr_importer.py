"""
Optical Music Recognition (OMR) — Lightweight score importer.

Supports PDF and common image formats (jpg, png, gif).
Limitation (deliberate, user-approved): works best with clean, printed,
single-melody lines. Polyphony, hand-written scores, and rhythm detection
are out of scope — all detected notes are assigned quarter-note duration (1.0 beat).
"""
from __future__ import annotations

import math
from typing import List, Optional, Tuple

import numpy as np

# ── Optional heavy dependencies (defensive pattern used throughout the project) ──
try:
    from PIL import Image
    HAS_PILLOW = True
except ImportError:
    HAS_PILLOW = False

try:
    import fitz  # PyMuPDF
    HAS_FITZ = True
except ImportError:
    HAS_FITZ = False

try:
    from scipy.ndimage import label as ndimage_label
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False

from core.notes import Note, DIATONIC_NAMES
from core.songs import Song, SongNote

OMR_AVAILABLE = HAS_PILLOW and HAS_FITZ and HAS_SCIPY

# ── Staff reference notes (pitch on line 2 from bottom of each clef) ──
# Treble clef: 2nd line from bottom = G4  (diatonic_step = 4*7+4 = 32)
# Bass clef:   2nd line from bottom = B2  (diatonic_step = 2*7+6 = 20)
_CLEF_REF: dict = {
    "treble": ("G4", 32),
    "bass":   ("B2", 20),
}

# How many pixels below the reference line position y=0 corresponds to diatonic_step 32/20.
# (actual y offsets are computed per-image from staff detection)

# ── Public interface ────────────────────────────────────────────────────────────


def load_image_from_file(filepath: str) -> "np.ndarray":
    """
    Loads a score image file as a grayscale numpy array.
    Accepts: .pdf (first page rendered at 200 DPI), .jpg/.jpeg/.png/.gif.
    Raises RuntimeError if required libraries are not installed.
    """
    if not HAS_PILLOW:
        raise RuntimeError("Pillow não está instalado. Execute: pip install Pillow")

    fp = filepath.lower()

    if fp.endswith(".pdf"):
        if not HAS_FITZ:
            raise RuntimeError("PyMuPDF não está instalado. Execute: pip install PyMuPDF")
        doc = fitz.open(filepath)
        page = doc[0]
        mat = fitz.Matrix(200 / 72, 200 / 72)  # 200 DPI
        pix = page.get_pixmap(matrix=mat, colorspace=fitz.csGRAY)
        arr = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width)
        doc.close()
        return arr

    img = Image.open(filepath).convert("L")
    return np.array(img, dtype=np.uint8)


def binarize(gray: "np.ndarray", threshold: int = 128) -> "np.ndarray":
    """
    Converts a grayscale image to binary (1=ink/black, 0=paper/white).
    Uses a simple fixed threshold (good for printed scores).
    """
    return (gray < threshold).astype(np.uint8)


def detect_staff_lines(
    binary: "np.ndarray",
) -> List[Tuple[int, float]]:
    """
    Finds the 5 staff lines by horizontal projection (row sum of black pixels).
    Returns a list of (row_index, confidence) for up to 5 strongest lines.
    Each entry represents the y-pixel of one staff line.
    """
    row_sums = binary.sum(axis=1).astype(float)
    width = binary.shape[1]

    # Normalise by image width so short lines don't dominate
    normalised = row_sums / (width + 1e-6)

    max_val = normalised.max()
    if max_val < 0.05:  # Less than 5% of pixels black in any row — no meaningful content
        return []

    # Simple peak detection: find rows that are local maxima above a threshold
    threshold = max_val * 0.35
    peaks: List[Tuple[int, float]] = []
    n = len(normalised)
    for i in range(1, n - 1):
        if (
            normalised[i] >= threshold
            and normalised[i] >= normalised[i - 1]
            and normalised[i] >= normalised[i + 1]
        ):
            peaks.append((i, float(normalised[i])))

    if not peaks:
        return []

    # Cluster nearby peaks (within 3 px) into groups and take the max per group
    merged: List[Tuple[int, float]] = []
    peaks_sorted = sorted(peaks, key=lambda p: p[0])
    group: List[Tuple[int, float]] = [peaks_sorted[0]]
    for p in peaks_sorted[1:]:
        if p[0] - group[-1][0] <= 3:
            group.append(p)
        else:
            best = max(group, key=lambda x: x[1])
            merged.append(best)
            group = [p]
    merged.append(max(group, key=lambda x: x[1]))

    # Return the 5 strongest
    merged.sort(key=lambda x: x[1], reverse=True)
    top5 = sorted(merged[:5], key=lambda x: x[0])
    return top5


def _line_spacing(staff_lines: List[Tuple[int, float]]) -> float:
    """Estimates the pixel distance between adjacent staff lines (half-space = note step)."""
    if len(staff_lines) < 2:
        return 10.0
    gaps = [staff_lines[i + 1][0] - staff_lines[i][0] for i in range(len(staff_lines) - 1)]
    return float(np.mean(gaps))


def detect_noteheads(
    binary: "np.ndarray",
    staff_lines: List[Tuple[int, float]],
    min_area_factor: float = 0.3,
    max_area_factor: float = 2.5,
) -> List[Tuple[int, int]]:
    """
    Detects note head blobs in a binary score image.
    Returns a list of (x, y) centre coordinates sorted left-to-right.

    Strategy:
    1. Mask out the staff lines (horizontal strips).
    2. Use scipy connected-components labelling.
    3. Filter blobs by size (≈ line_spacing²) and circularity.
    """
    if not HAS_SCIPY:
        raise RuntimeError("scipy não está instalado. Execute: pip install scipy")

    spacing = _line_spacing(staff_lines)
    masked = binary.copy()

    # Erase the staff lines (±2 px around each line row)
    for row_y, _ in staff_lines:
        y_lo = max(0, row_y - 2)
        y_hi = min(masked.shape[0], row_y + 3)
        masked[y_lo:y_hi, :] = 0

    labeled, num_features = ndimage_label(masked)

    noteheads: List[Tuple[int, int]] = []
    expected_area = spacing * spacing
    min_area = expected_area * min_area_factor
    max_area = expected_area * max_area_factor

    for lbl in range(1, num_features + 1):
        region = np.where(labeled == lbl)
        area = len(region[0])
        if area < min_area or area > max_area:
            continue

        rows, cols = region
        height = rows.max() - rows.min() + 1
        width = cols.max() - cols.min() + 1

        # Circularity heuristic: width and height should be comparable (not a stem/bar)
        if width == 0 or height == 0:
            continue
        ratio = max(width, height) / (min(width, height) + 1e-6)
        if ratio > 2.8:
            continue

        cy = int(np.mean(rows))
        cx = int(np.mean(cols))
        noteheads.append((cx, cy))

    noteheads.sort(key=lambda p: p[0])
    return noteheads


def map_pixel_to_note(
    y: int,
    staff_lines: List[Tuple[int, float]],
    clef: str = "treble",
) -> Note:
    """
    Converts a vertical pixel coordinate y to a musical Note by comparing it
    to the staff reference line (2nd line from bottom in the given clef).

    Each half-step in y corresponds to one diatonic step (line or space on the staff).
    """
    if not staff_lines:
        return Note("C4")

    spacing = _line_spacing(staff_lines)
    half_step = spacing / 2.0

    # 2nd line from bottom in a 5-line staff = index [1] (0-based)
    ref_idx = min(1, len(staff_lines) - 1)
    ref_y = staff_lines[ref_idx][0]

    ref_pitch_str, ref_diatonic = _CLEF_REF.get(clef, _CLEF_REF["treble"])

    # Higher on the page (smaller y) = higher pitch
    delta_steps = round((ref_y - y) / half_step)
    target_diatonic = ref_diatonic + delta_steps

    octave, step_in_oct = divmod(target_diatonic, 7)
    step_in_oct = max(0, min(6, step_in_oct))
    letter = DIATONIC_NAMES[step_in_oct]
    octave = max(0, min(8, octave))

    try:
        return Note(f"{letter}{octave}")
    except ValueError:
        return Note("C4")


def import_score_as_song(
    filepath: str,
    clef: str = "treble",
    title: Optional[str] = None,
) -> Song:
    """
    Full OMR pipeline: load → binarise → detect staff → detect noteheads → map to notes.
    Returns a Song with all detected notes at quarter-note duration (1.0 beat).
    Does NOT save to disk — the caller (Phase 19 review screen) handles persistence.

    Args:
        filepath: path to .pdf, .jpg, .jpeg, .png or .gif file.
        clef: \"treble\" (Clave de Sol) or \"bass\" (Clave de Fá).
        title: song title (defaults to filename stem).
    """
    if not OMR_AVAILABLE:
        missing = [
            lib for lib, avail in [("Pillow", HAS_PILLOW), ("PyMuPDF", HAS_FITZ), ("scipy", HAS_SCIPY)]
            if not avail
        ]
        raise RuntimeError(f"Dependências em falta para OMR: {', '.join(missing)}")

    import os
    song_title = title or os.path.splitext(os.path.basename(filepath))[0]

    gray = load_image_from_file(filepath)
    binary = binarize(gray)
    staff_lines = detect_staff_lines(binary)

    if not staff_lines:
        # Return empty song if no staff found
        return Song(
            id=f"omr_{hash(filepath) & 0xFFFFFF:06x}",
            title=song_title,
            composer="OMR Import",
            difficulty="Iniciante",
            bpm=80,
            clef=clef,
            notes=[],
        )

    noteheads = detect_noteheads(binary, staff_lines)

    song_notes: List[SongNote] = []
    for cx, cy in noteheads:
        note = map_pixel_to_note(cy, staff_lines, clef)
        song_notes.append(SongNote(note=note, duration_beats=1.0))

    return Song(
        id=f"omr_{hash(filepath) & 0xFFFFFF:06x}",
        title=song_title,
        composer="OMR Import",
        difficulty="Iniciante",
        bpm=80,
        clef=clef,
        notes=song_notes,
    )
