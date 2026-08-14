"""Piano fingering algorithms and standard hand fingering recommendations for chords, scales, and melodies."""
from typing import Dict, List, Optional
from .notes import Note
from .chords import Chord


# Standard right-hand fingering patterns for chords (inversions 0, 1, 2, 3)
RIGHT_HAND_TRIAD_FINGERINGS = {
    0: [1, 3, 5],  # Root position: Thumb (1), Middle (3), Pinky (5)
    1: [1, 2, 5],  # 1st inversion: Thumb (1), Index (2), Pinky (5)
    2: [1, 3, 5],  # 2nd inversion: Thumb (1), Middle (3), Pinky (5)
}

LEFT_HAND_TRIAD_FINGERINGS = {
    0: [5, 3, 1],  # Root position: Pinky (5), Middle (3), Thumb (1)
    1: [5, 3, 1],  # 1st inversion
    2: [5, 2, 1],  # 2nd inversion: Pinky (5), Index (2), Thumb (1)
}

RIGHT_HAND_TETRAD_FINGERINGS = {
    0: [1, 2, 3, 5],  # Root position: 1, 2, 3, 5
    1: [1, 2, 3, 5],  # 1st inversion
    2: [1, 2, 4, 5],  # 2nd inversion
    3: [1, 2, 3, 5],  # 3rd inversion
}

LEFT_HAND_TETRAD_FINGERINGS = {
    0: [5, 3, 2, 1],
    1: [5, 3, 2, 1],
    2: [5, 4, 2, 1],
    3: [5, 3, 2, 1],
}


def get_chord_piano_fingering(
    notes: List[Note],
    inversion: int = 0,
    hand: str = "right",
) -> Dict[int, int]:
    """
    Returns a mapping of Note MIDI numbers to recommended finger numbers (1=Thumb..5=Pinky).
    Hand can be 'right' or 'left'.
    """
    if not notes:
        return {}

    num_notes = len(notes)
    fingers = []

    if hand == "right":
        if num_notes == 3:
            fingers = RIGHT_HAND_TRIAD_FINGERINGS.get(inversion, [1, 3, 5])
        elif num_notes == 4:
            fingers = RIGHT_HAND_TETRAD_FINGERINGS.get(inversion, [1, 2, 3, 5])
        elif num_notes == 2:
            fingers = [1, 5]
        else:
            fingers = [1, 2, 3, 4, 5][:num_notes]
    else:  # Left hand
        if num_notes == 3:
            fingers = LEFT_HAND_TRIAD_FINGERINGS.get(inversion, [5, 3, 1])
        elif num_notes == 4:
            fingers = LEFT_HAND_TETRAD_FINGERINGS.get(inversion, [5, 3, 2, 1])
        elif num_notes == 2:
            fingers = [5, 1]
        else:
            fingers = [5, 4, 3, 2, 1][-num_notes:]

    # Map each note's MIDI to its assigned finger
    result = {}
    for i, note in enumerate(notes):
        if i < len(fingers):
            result[note.midi] = fingers[i]

    return result


def get_scale_piano_fingering_description(scale_name: str, hand: str = "right") -> str:
    """Returns a textual explanation of the thumb under/finger over pattern for standard scales."""
    if hand == "right":
        return "Mão Direita: 1-2-3-1-2-3-4-5 (o polegar passa por baixo do dedo 3)"
    else:
        return "Mão Esquerda: 5-4-3-2-1-3-2-1 (o dedo 3 passa por cima do polegar)"
