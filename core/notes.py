"""Music theory representation for notes, pitches, frequencies, and staff coordinates."""
import re
from typing import Optional, Tuple, Union

# Chromatic scale definitions
NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

ENHARMONIC_FLATS = {
    "Db": "C#",
    "Eb": "D#",
    "Fb": "E",
    "Gb": "F#",
    "Ab": "G#",
    "Bb": "A#",
    "Cb": "B",
}

ENHARMONIC_SHARPS = {
    "B#": "C",
    "E#": "F",
}

# Portuguese Solfège mapping
NOTE_NAMES_PT = {
    "C": "Dó",
    "C#": "Dó#",
    "Db": "Réb",
    "D": "Ré",
    "D#": "Ré#",
    "Eb": "Mib",
    "E": "Mi",
    "F": "Fá",
    "F#": "Fá#",
    "Gb": "Solb",
    "G": "Sol",
    "G#": "Sol#",
    "Ab": "Láb",
    "A": "Lá",
    "A#": "Lá#",
    "Bb": "Sib",
    "B": "Si",
}

DIATONIC_STEPS = {"C": 0, "D": 1, "E": 2, "F": 3, "G": 4, "A": 5, "B": 6}
DIATONIC_NAMES = ["C", "D", "E", "F", "G", "A", "B"]


def midi_to_freq(midi_number: int) -> float:
    """Converts a MIDI note number to its corresponding frequency in Hz (A4 = 440 Hz)."""
    return 440.0 * (2.0 ** ((midi_number - 69) / 12.0))


def note_to_midi(pitch: str, octave: int = 4) -> int:
    """Converts a note pitch name and octave to its MIDI number (C4 = 60)."""
    clean_pitch = pitch.strip()
    # Normalize flats and special sharps
    if clean_pitch in ENHARMONIC_FLATS:
        base_pitch = ENHARMONIC_FLATS[clean_pitch]
    elif clean_pitch in ENHARMONIC_SHARPS:
        base_pitch = ENHARMONIC_SHARPS[clean_pitch]
    else:
        base_pitch = clean_pitch

    if base_pitch not in NOTE_NAMES:
        raise ValueError(f"Pitch desconhecido: '{pitch}'")

    semitone = NOTE_NAMES.index(base_pitch)
    return (octave + 1) * 12 + semitone


def midi_to_note(midi_number: int, use_sharps: bool = True) -> Tuple[str, int]:
    """Converts a MIDI number to (pitch_name, octave)."""
    octave = (midi_number // 12) - 1
    semitone = midi_number % 12
    pitch = NOTE_NAMES[semitone]
    return pitch, octave


class Note:
    """Represents a specific musical note with pitch and octave."""

    def __init__(self, name: str, octave: int = 4, display_name: Optional[str] = None):
        """
        Creates a Note.
        Args:
            name: e.g. 'C', 'C#', 'Db', 'A4', 'F#3'
            octave: integer octave (default 4, ignored if octave is specified in name)
            display_name: optional custom display (e.g. 'Db' instead of 'C#')
        """
        parsed_name, parsed_octave = self._parse_string(name, octave)
        self.raw_name = parsed_name
        self.display_name = display_name if display_name else parsed_name
        self.octave = parsed_octave

        # Extract base letter and accidental
        match = re.match(r"^([A-Ga-g])([#b]?)$", self.raw_name)
        if not match:
            raise ValueError(f"Formato de nota inválido: '{name}'")

        self.letter = match.group(1).upper()
        self.accidental = match.group(2)
        self.pitch = f"{self.letter}{self.accidental}"

        # Standardized pitch (sharp-based)
        if self.pitch in ENHARMONIC_FLATS:
            self.normalized_pitch = ENHARMONIC_FLATS[self.pitch]
        elif self.pitch in ENHARMONIC_SHARPS:
            self.normalized_pitch = ENHARMONIC_SHARPS[self.pitch]
        else:
            self.normalized_pitch = self.pitch

        self.midi: int = note_to_midi(self.normalized_pitch, self.octave)
        self.frequency: float = midi_to_freq(self.midi)

    @classmethod
    def from_midi(cls, midi_number: int, display_name: Optional[str] = None) -> "Note":
        """Creates a Note instance directly from a MIDI number."""
        pitch, octave = midi_to_note(midi_number)
        return cls(pitch, octave, display_name=display_name)

    @staticmethod
    def _parse_string(name: str, default_octave: int) -> Tuple[str, int]:
        name = name.strip()
        match = re.match(r"^([A-Ga-g][#b]?)(-?\d+)?$", name)
        if not match:
            raise ValueError(f"Não foi possível interpretar a nota: '{name}'")
        pitch = match.group(1).capitalize()
        if len(pitch) > 1 and pitch[1] in ["#", "b"]:
            pitch = pitch[0].upper() + pitch[1]
        else:
            pitch = pitch.upper()

        octave = int(match.group(2)) if match.group(2) is not None else default_octave
        return pitch, octave

    @property
    def name_pt(self) -> str:
        """Returns the Portuguese solfège name (e.g. 'Dó#', 'Lá')."""
        return NOTE_NAMES_PT.get(self.raw_name, NOTE_NAMES_PT.get(self.normalized_pitch, self.raw_name))

    @property
    def pitch_with_octave(self) -> str:
        """Returns standardized pitch with octave (e.g. 'C4', 'F#3')."""
        return f"{self.pitch}{self.octave}"

    @property
    def full_name(self) -> str:
        """Returns the full scientific pitch notation (e.g. 'C#4')."""
        return f"{self.raw_name}{self.octave}"

    @property
    def full_name_pt(self) -> str:
        """Returns the full Portuguese solfège with octave (e.g. 'Dó#4')."""
        return f"{self.name_pt}{self.octave}"

    @property
    def diatonic_step(self) -> int:
        """
        Calculates the absolute diatonic step for musical staff rendering.
        Each step corresponds to one line or space on the staff.
        C4 is 4 * 7 + 0 = 28.
        """
        return self.octave * 7 + DIATONIC_STEPS[self.letter]

    def transpose(self, semitones: int) -> "Note":
        """Returns a new Note transposed by a number of semitones."""
        new_midi = self.midi + semitones
        return Note.from_midi(new_midi)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Note):
            return self.midi == other.midi
        return False

    def __lt__(self, other: "Note") -> bool:
        return self.midi < other.midi

    def __hash__(self) -> int:
        return hash(self.midi)

    def __repr__(self) -> str:
        return f"Note('{self.full_name}', freq={self.frequency:.1f}Hz, midi={self.midi})"

    def __str__(self) -> str:
        return self.full_name
