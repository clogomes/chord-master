from dataclasses import dataclass
from typing import Dict, Optional
from core.notes import Note
from core.ear_mnemonics import EAR_MNEMONICS, get_mnemonic_by_semitones, get_mnemonic_by_code


@dataclass
class Interval:
    semitones: int
    name_pt: str
    name_en: str
    short_code: str
    mnemonic: str
    description: str


INTERVALS: Dict[int, Interval] = {}

# Build INTERVALS directly from consolidated EAR_MNEMONICS source of truth
for code, em in EAR_MNEMONICS.items():
    INTERVALS[em.semitones] = Interval(
        semitones=em.semitones,
        name_pt=em.name,
        name_en=em.name_en,
        short_code=em.interval_code,
        mnemonic=em.songs_ascending,
        description=em.description
    )

INTERVAL_NAMES_PT = {v.short_code: v.name_pt for v in INTERVALS.values()}


def get_interval(root: Note, target: Note) -> Interval:
    """Returns the Interval object between two notes."""
    raw_semitones = abs(target.midi - root.midi)
    if raw_semitones == 0:
        return INTERVALS[0]
    if raw_semitones in INTERVALS:
        return INTERVALS[raw_semitones]
    # For compound intervals (> 12 semitones), reduce to simple interval
    simple_semitones = raw_semitones % 12
    if simple_semitones == 0:
        return INTERVALS[12]
    return INTERVALS.get(simple_semitones, INTERVALS[12])


def get_interval_by_code(code: str) -> Optional[Interval]:
    """Returns the Interval object corresponding to a short code like 'm3' or 'P5'."""
    em = get_mnemonic_by_code(code)
    if em and em.semitones in INTERVALS:
        return INTERVALS[em.semitones]
    for interval in INTERVALS.values():
        if interval.short_code == code:
            return interval
    return None


def calculate_target_note(root: Note, semitones: int, direction: str = "up") -> Note:
    """Calculates the target note given a root note and semitone distance."""
    if direction == "down":
        target_midi = root.midi - semitones
    else:
        target_midi = root.midi + semitones
    return Note.from_midi(target_midi)


def transpose_note(note: Note, semitones: int) -> Note:
    """Transposes a note by a number of semitones."""
    return Note.from_midi(note.midi + semitones)
