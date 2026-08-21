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
    """Returns a textual fingering pattern for the given scale family and hand.

    Accepts hand as 'right'/'direita' or 'left'/'esquerda'.
    """
    from .scales import SCALE_TYPES

    is_right = hand in ("right", "direita")
    hand_label = "Mão Direita" if is_right else "Mão Esquerda"

    if scale_name not in SCALE_TYPES:
        return f"{hand_label}: 1-2-3-1-2-3-4-5 (padrão genérico)"

    intervals = SCALE_TYPES[scale_name].intervals
    num_degrees = len(intervals) - 1

    if num_degrees == 7:
        if is_right:
            return "Mão Direita: 1-2-3-1-2-3-4-5 (o polegar passa por baixo do dedo 3)"
        else:
            return "Mão Esquerda: 5-4-3-2-1-3-2-1 (o dedo 3 passa por cima do polegar)"
    elif num_degrees == 5:
        if is_right:
            return "Mão Direita: 1-2-3-1-2 (o polegar passa por baixo do dedo 3)"
        else:
            return "Mão Esquerda: 5-4-3-2-1 (o dedo 3 passa por cima do polegar)"
    elif num_degrees == 6:
        if is_right:
            return "Mão Direita: 1-2-3-1-2-3 (o polegar passa por baixo do dedo 3)"
        else:
            return "Mão Esquerda: 5-4-3-2-1-3 (o dedo 3 passa por cima do polegar)"
    elif num_degrees == 12:
        if is_right:
            return "Mão Direita: 1-3-1-3-1-2-3-1-3-1-3-1-2 (polegar nas brancas, dedo 3 nas pretas)"
        else:
            return "Mão Esquerda: 5-3-5-3-5-4-3-5-3-5-3-5-4 (polegar nas brancas, dedo 3 nas pretas)"
    else:
        if is_right:
            return f"{hand_label}: 1-2-3-1-2-3-4-5 (dedilhação aproximada para {num_degrees} graus)"
        else:
            return f"{hand_label}: 5-4-3-2-1-3-2-1 (dedilhação aproximada para {num_degrees} graus)"


def assign_piano_fingerings(notes: List[Note]) -> List[int]:
    """Assigns standard 5-finger melodic heuristics for right hand."""
    if not notes:
        return []

    fingerings = []
    curr_finger = 1
    prev_midi = notes[0].midi

    for i, n in enumerate(notes):
        if i == 0:
            fingerings.append(curr_finger)
            continue

        delta = n.midi - prev_midi
        if delta > 0:
            curr_finger = min(5, curr_finger + min(delta, 2))
        elif delta < 0:
            curr_finger = max(1, curr_finger + max(delta, -2))
        fingerings.append(curr_finger)
        prev_midi = n.midi

    return fingerings
