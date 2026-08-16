"""Music theory representation of the guitar/viola fretboard, tunings, and chord shapes."""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from .notes import Note, NOTE_NAMES


# Standard 6-string Guitar / Viola tuning (from 6th/thickest string E2 to 1st/thinnest string E4)
STANDARD_TUNING = [
    Note("E2"),  # 6ª corda (Mi grave)
    Note("A2"),  # 5ª corda (Lá)
    Note("D3"),  # 4ª corda (Ré)
    Note("G3"),  # 3ª corda (Sol)
    Note("B3"),  # 2ª corda (Si)
    Note("E4"),  # 1ª corda (Mi agudo)
]

STRING_NAMES_PT = ["6ª (Mi grave)", "5ª (Lá)", "4ª (Ré)", "3ª (Sol)", "2ª (Si)", "1ª (Mi agudo)"]


@dataclass
class GuitarChordShape:
    """
    Represents how to play a chord on a 6-string guitar/viola.
    frets: list of 6 integers (one per string from 6th to 1st).
           -1 represents a muted string ('X'), 0 represents open string ('O'), >0 represents fret number.
    fingers: optional list of 6 values indicating finger (1=Index, 2=Middle, 3=Ring, 4=Pinky, 0=None).
    barre_fret: optional fret where a barre is placed.
    """
    name: str
    symbol: str
    chord_type: str
    root: str
    frets: List[int]
    fingers: Optional[List[int]] = None
    barre_fret: Optional[int] = None
    description: str = ""


# Essential chord shapes for guitar/viola (Open chords, CAGED movable forms, and Jazz/Bossa voicings)
GUITAR_CHORD_LIBRARY: Dict[str, List[GuitarChordShape]] = {
    # ACORDES MAIORES
    "C": [
        GuitarChordShape("Dó Maior", "C", "major", "C", [-1, 3, 2, 0, 1, 0], [0, 3, 2, 0, 1, 0], description="Forma aberta clássica (CAGED C)."),
        GuitarChordShape("Dó Maior (Pestana)", "C", "major", "C", [-1, 3, 5, 5, 5, 3], [0, 1, 2, 3, 4, 1], barre_fret=3, description="Forma de pestana no 3º traste (CAGED A)."),
        GuitarChordShape("Dó Maior (8º traste)", "C", "major", "C", [8, 10, 10, 9, 8, 8], [1, 3, 4, 2, 1, 1], barre_fret=8, description="Forma de pestana no 8º traste (CAGED E)."),
    ],
    "D": [
        GuitarChordShape("Ré Maior", "D", "major", "D", [-1, -1, 0, 2, 3, 2], [0, 0, 0, 1, 3, 2], description="Forma aberta clássica (CAGED D)."),
        GuitarChordShape("Ré Maior (5º traste)", "D", "major", "D", [-1, 5, 7, 7, 7, 5], [0, 1, 2, 3, 4, 1], barre_fret=5, description="Pestana no 5º traste (CAGED A)."),
    ],
    "E": [
        GuitarChordShape("Mi Maior", "E", "major", "E", [0, 2, 2, 1, 0, 0], [0, 2, 3, 1, 0, 0], description="Forma aberta básica com grande ressonância das cordas graves."),
        GuitarChordShape("Mi Maior (7º traste)", "E", "major", "E", [-1, 7, 9, 9, 9, 7], [0, 1, 2, 3, 4, 1], barre_fret=7, description="Pestana no 7º traste."),
    ],
    "F": [
        GuitarChordShape("Fá Maior (Pestana)", "F", "major", "F", [1, 3, 3, 2, 1, 1], [1, 3, 4, 2, 1, 1], barre_fret=1, description="A forma fundamental de pestana completa no 1º traste."),
        GuitarChordShape("Fá Maior (Simples)", "F", "major", "F", [-1, -1, 3, 2, 1, 1], [0, 0, 3, 2, 1, 1], description="Versão reduzida sem tocar os bordões."),
    ],
    "G": [
        GuitarChordShape("Sol Maior", "G", "major", "G", [3, 2, 0, 0, 0, 3], [2, 1, 0, 0, 0, 3], description="Forma aberta clássica com cordas soltas."),
        GuitarChordShape("Sol Maior (3º traste)", "G", "major", "G", [3, 5, 5, 4, 3, 3], [1, 3, 4, 2, 1, 1], barre_fret=3, description="Forma de pestana no 3º traste."),
    ],
    "A": [
        GuitarChordShape("Lá Maior", "A", "major", "A", [-1, 0, 2, 2, 2, 0], [0, 0, 1, 2, 3, 0], description="Forma aberta com as 3 cordas no 2º traste."),
        GuitarChordShape("Lá Maior (5º traste)", "A", "major", "A", [5, 7, 7, 6, 5, 5], [1, 3, 4, 2, 1, 1], barre_fret=5, description="Pestana no 5º traste (CAGED E)."),
    ],
    "B": [
        GuitarChordShape("Si Maior (Pestana)", "B", "major", "B", [-1, 2, 4, 4, 4, 2], [0, 1, 2, 3, 4, 1], barre_fret=2, description="Pestana no 2º traste a partir da 5ª corda."),
        GuitarChordShape("Si Maior (7º traste)", "B", "major", "B", [7, 9, 9, 8, 7, 7], [1, 3, 4, 2, 1, 1], barre_fret=7, description="Pestana no 7º traste a partir da 6ª corda."),
    ],

    # ACORDES MENORES
    "Am": [
        GuitarChordShape("Lá Menor", "Am", "minor", "A", [-1, 0, 2, 2, 1, 0], [0, 0, 2, 3, 1, 0], description="Forma aberta menor fundamental."),
        GuitarChordShape("Lá Menor (5º traste)", "Am", "minor", "A", [5, 7, 7, 5, 5, 5], [1, 3, 4, 1, 1, 1], barre_fret=5, description="Pestana menor no 5º traste."),
    ],
    "Em": [
        GuitarChordShape("Mi Menor", "Em", "minor", "E", [0, 2, 2, 0, 0, 0], [0, 2, 3, 0, 0, 0], description="O acorde menor mais fácil e encorpado na viola."),
        GuitarChordShape("Mi Menor (7º traste)", "Em", "minor", "E", [-1, 7, 9, 9, 8, 7], [0, 1, 3, 4, 2, 1], barre_fret=7, description="Pestana menor na 5ª corda."),
    ],
    "Dm": [
        GuitarChordShape("Ré Menor", "Dm", "minor", "D", [-1, -1, 0, 2, 3, 1], [0, 0, 0, 2, 3, 1], description="Forma aberta melancólica nas primeiras cordas."),
        GuitarChordShape("Ré Menor (5º traste)", "Dm", "minor", "D", [-1, 5, 7, 7, 6, 5], [0, 1, 3, 4, 2, 1], barre_fret=5, description="Pestana menor no 5º traste."),
    ],
    "Bm": [
        GuitarChordShape("Si Menor (Pestana)", "Bm", "minor", "B", [-1, 2, 4, 4, 3, 2], [0, 1, 3, 4, 2, 1], barre_fret=2, description="Pestana menor clássica no 2º traste."),
    ],
    "F#m": [
        GuitarChordShape("Fá# Menor", "F#m", "minor", "F#", [2, 4, 4, 2, 2, 2], [1, 3, 4, 1, 1, 1], barre_fret=2, description="Pestana menor no 2º traste."),
    ],
    "C#m": [
        GuitarChordShape("Dó# Menor", "C#m", "minor", "C#", [-1, 4, 6, 6, 5, 4], [0, 1, 3, 4, 2, 1], barre_fret=4, description="Pestana menor no 4º traste."),
    ],
    "Gm": [
        GuitarChordShape("Sol Menor", "Gm", "minor", "G", [3, 5, 5, 3, 3, 3], [1, 3, 4, 1, 1, 1], barre_fret=3, description="Pestana menor no 3º traste."),
    ],

    # ACORDES COM SÉTIMA (DOMINANTES)
    "C7": [GuitarChordShape("Dó com 7ª", "C7", "dom7", "C", [-1, 3, 2, 3, 1, 0], [0, 3, 2, 4, 1, 0], description="Dó com o Si♭ adicionado no 3º traste da 3ª corda.")],
    "D7": [GuitarChordShape("Ré com 7ª", "D7", "dom7", "D", [-1, -1, 0, 2, 1, 2], [0, 0, 0, 2, 1, 3], description="Forma triangular aberta de D7.")],
    "E7": [GuitarChordShape("Mi com 7ª", "E7", "dom7", "E", [0, 2, 0, 1, 0, 0], [0, 2, 0, 1, 0, 0], description="Mi maior retirando o dedo da 4ª corda para soar o Ré solto.")],
    "G7": [GuitarChordShape("Sol com 7ª", "G7", "dom7", "G", [3, 2, 0, 0, 0, 1], [3, 2, 0, 0, 0, 1], description="Sol maior com o Fá natural no 1º traste da 1ª corda.")],
    "A7": [GuitarChordShape("Lá com 7ª", "A7", "dom7", "A", [-1, 0, 2, 0, 2, 0], [0, 0, 1, 0, 2, 0], description="Lá maior com a 3ª corda solta (Sol natural).")],
    "B7": [GuitarChordShape("Si com 7ª", "B7", "dom7", "B", [-1, 2, 1, 2, 0, 2], [0, 2, 1, 3, 0, 4], description="Forma aberta clássica de B7 muito usada no fado e flamenco.")],

    # ACORDES MAJ7 & MIN7
    "Cmaj7": [GuitarChordShape("Dó com 7ª Maior", "Cmaj7", "maj7", "C", [-1, 3, 2, 0, 0, 0], [0, 3, 2, 0, 0, 0], description="Sonoridade aveludada de Bossa Nova.")],
    "Fmaj7": [GuitarChordShape("Fá com 7ª Maior", "Fmaj7", "maj7", "F", [-1, -1, 3, 2, 1, 0], [0, 0, 3, 2, 1, 0], description="Forma aberta sem pestana de grande beleza harmónica.")],
    "Am7": [GuitarChordShape("Lá Menor com 7ª", "Am7", "min7", "A", [-1, 0, 2, 0, 1, 0], [0, 0, 2, 0, 1, 0], description="Am com a 3ª corda solta.")],
    "Dm7": [GuitarChordShape("Ré Menor com 7ª", "Dm7", "min7", "D", [-1, -1, 0, 2, 1, 1], [0, 0, 0, 2, 1, 1], barre_fret=1, description="Mini-pestana no 1º traste das duas primeiras cordas.")],
    "Em7": [GuitarChordShape("Mi Menor com 7ª", "Em7", "min7", "E", [0, 2, 0, 0, 0, 0], [0, 1, 0, 0, 0, 0], description="Apenas 1 dedo no 2º traste da 5ª corda.")],
}


class GuitarFretboardModel:
    """Calculates fret positions, notes on the 6 strings, and matches chords/scales."""

    def __init__(self, tuning: Optional[List[Note]] = None, num_frets: int = 15):
        self.tuning = tuning if tuning is not None else STANDARD_TUNING
        self.num_frets = num_frets

    def get_note_at(self, string_idx: int, fret: int) -> Note:
        """
        Returns the Note produced at a given string (0=6th thickest, 5=1st thinnest) and fret.
        """
        if string_idx < 0 or string_idx >= len(self.tuning):
            raise ValueError(f"Índice de corda inválido: {string_idx}")
        open_note = self.tuning[string_idx]
        return open_note.transpose(fret)

    def find_note_positions(self, note: Note) -> List[Tuple[int, int]]:
        """
        Finds all (string_idx, fret) positions matching a specific note.
        Prefers exact MIDI pitch match. If out of range, falls back to the octave closest in MIDI pitch.
        """
        exact_positions = []
        octave_candidates = []

        for string_idx in range(len(self.tuning)):
            for fret in range(self.num_frets + 1):
                fret_note = self.get_note_at(string_idx, fret)
                if fret_note.midi == note.midi:
                    exact_positions.append((string_idx, fret))
                elif fret_note.normalized_pitch == note.normalized_pitch:
                    diff = abs(fret_note.midi - note.midi)
                    octave_candidates.append(((string_idx, fret), diff))

        if exact_positions:
            return exact_positions

        if octave_candidates:
            min_diff = min(c[1] for c in octave_candidates)
            return [c[0] for c in octave_candidates if c[1] == min_diff]

        return []

    def get_chord_shape(self, chord_symbol: str) -> Optional[GuitarChordShape]:
        """Retrieves a primary guitar chord shape for a chord symbol (e.g. 'C', 'Am', 'G7')."""
        clean_symbol = chord_symbol.strip()
        shapes = GUITAR_CHORD_LIBRARY.get(clean_symbol, [])
        return shapes[0] if shapes else None

    def get_all_chord_shapes(self, chord_symbol: str) -> List[GuitarChordShape]:
        """Retrieves all alternative guitar chord shapes for a chord symbol."""
        clean_symbol = chord_symbol.strip()
        return GUITAR_CHORD_LIBRARY.get(clean_symbol, [])

    def get_scale_positions_on_fretboard(self, scale_notes: List[Note]) -> List[Dict]:
        """
        Calculates all positions on the fretboard for a given list of scale notes.
        Returns a list of dicts with string_idx, fret, note, is_root, and degree index.
        """
        scale_pitches = [n.normalized_pitch for n in scale_notes]
        root_pitch = scale_notes[0].normalized_pitch if scale_notes else ""
        results = []

        for string_idx in range(len(self.tuning)):
            for fret in range(self.num_frets + 1):
                note = self.get_note_at(string_idx, fret)
                if note.normalized_pitch in scale_pitches:
                    degree_idx = scale_pitches.index(note.normalized_pitch)
                    results.append({
                        "string": string_idx,
                        "fret": fret,
                        "note": note,
                        "is_root": (note.normalized_pitch == root_pitch),
                        "degree_idx": degree_idx + 1,
                    })
        return results


def find_note_positions(note: Note, max_fret: int = 15) -> List[Tuple[int, int]]:
    """
    Finds all (string_idx, fret) positions matching a specific pitch or pitch-class on standard tuning.
    """
    model = GuitarFretboardModel(num_frets=max_fret)
    return model.find_note_positions(note)


def assign_guitar_coordinates(notes: List[Note], max_fret: int = 15) -> List[Tuple[int, int]]:
    """
    Calculates an ergonomic sequence of (string, fret) coordinates for a melody,
    minimizing sudden hand shifts across the fretboard.
    """
    if not notes:
        return []

    coords = []
    prev_str = 2  # Start around D string
    prev_fret = 5

    for n in notes:
        positions = find_note_positions(n, max_fret=max_fret)
        if not positions:
            coords.append((4, 1))
            continue

        # Pick position closest to previous string & fret
        best_pos = min(
            positions,
            key=lambda p: abs(p[0] - prev_str) * 2 + abs(p[1] - prev_fret)
        )
        coords.append(best_pos)
        prev_str, prev_fret = best_pos

    return coords
