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


def spell_note_with_letter(target_midi: int, expected_letter: str) -> "Note":
    """
    Spells a note with a specified expected base letter (A-G) and appropriate accidental
    (#, b, ##, bb, or natural) so that its pitch matches target_midi.
    """
    letter = expected_letter.upper()
    octave = (target_midi // 12) - 1
    base_midi_in_octave4 = {"C": 60, "D": 62, "E": 64, "F": 65, "G": 67, "A": 69, "B": 71}[letter]
    natural_midi = (octave + 1) * 12 + (base_midi_in_octave4 % 12)
    diff = target_midi - natural_midi

    while diff > 6:
        diff -= 12
    while diff < -6:
        diff += 12

    if diff == 0:
        acc = ""
    elif diff == 1:
        acc = "#"
    elif diff == -1:
        acc = "b"
    elif diff == 2:
        acc = "##"
    elif diff == -2:
        acc = "bb"
    else:
        acc = ""

    pitch = f"{letter}{acc}"
    return Note(pitch, octave=octave)


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
        match = re.match(r"^([A-G])([#b]{0,2})$", self.raw_name)
        if not match:
            raise ValueError(f"Formato de nota inválido: '{name}'")

        self.letter = match.group(1).upper()
        self.accidental = match.group(2)
        self.pitch = f"{self.letter}{self.accidental}"

        # Calculate MIDI based on natural letter + accidental offset
        base_midi_oct4 = {"C": 60, "D": 62, "E": 64, "F": 65, "G": 67, "A": 69, "B": 71}[self.letter]
        acc_offset = 0
        if self.accidental == "#": acc_offset = 1
        elif self.accidental == "##": acc_offset = 2
        elif self.accidental == "b": acc_offset = -1
        elif self.accidental == "bb": acc_offset = -2

        natural_midi = (self.octave + 1) * 12 + (base_midi_oct4 % 12)
        self.midi = natural_midi + acc_offset
        self.frequency = midi_to_freq(self.midi)
        
        # Standardized pitch (sharp-based)
        self.normalized_pitch, _ = midi_to_note(self.midi)

    @classmethod
    def from_midi(cls, midi_number: int, display_name: Optional[str] = None) -> "Note":
        """Creates a Note instance directly from a MIDI number."""
        pitch, octave = midi_to_note(midi_number)
        return cls(pitch, octave, display_name=display_name)

    @staticmethod
    def _parse_string(name: str, default_octave: int) -> Tuple[str, int]:
        name = name.strip()
        match = re.match(r"^([A-Ga-g])([#b♯♭]{1,2})?(-?\d+)?$", name)
        if not match:
            raise ValueError(f"Não foi possível interpretar a nota: '{name}'")
            
        pitch_letter = match.group(1).upper()
        acc = match.group(2) or ""
        acc = acc.replace("♯", "#").replace("♭", "b")
        pitch = pitch_letter + acc

        octave = int(match.group(3)) if match.group(3) is not None else default_octave
        return pitch, octave

    @property
    def name_pt(self) -> str:
        """Returns the Portuguese solfège name (e.g. 'Dó#', 'Lá')."""
        if self.raw_name in NOTE_NAMES_PT:
            return NOTE_NAMES_PT[self.raw_name]
            
        base_name_pt = NOTE_NAMES_PT.get(self.letter, self.letter)
        if self.accidental == "##":
            return f"{base_name_pt} dobrado sustenido"
        elif self.accidental == "bb":
            return f"{base_name_pt} dobrado bemol"
            
        return NOTE_NAMES_PT.get(self.normalized_pitch, self.raw_name)

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
