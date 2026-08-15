"""Pedagogy engine for step-by-step staff sight-reading (Guided Sight-Reading)."""
from typing import List, Dict, Tuple
from core.notes import Note

LEVELS_INFO = [
    {"level": 1, "name": "Notas nas Linhas", "desc": "(E4, G4, B4, D5, F5 / Mi, Sol, Si, Ré, Fá)"},
    {"level": 2, "name": "Notas nos Espaços", "desc": "(F4, A4, C5, E5 / Fá, Lá, Dó, Mi)"},
    {"level": 3, "name": "Linhas Suplementares", "desc": "(C4, D4, G5, A5)"},
    {"level": 4, "name": "Mistura Completa com Acidentes", "desc": "(♯ / ♭)"},
]

def get_note_explanation(note: Note, clef: str = "treble") -> str:
    """
    Returns a step-by-step explanation on how to read the given note in the specified clef.
    """
    step = note.diatonic_step
    
    if clef == "treble":
        base_line_step = 30  # E4 is the first line
        ref_note = "Sol (G4)"
        ref_line = "2ª linha a contar de baixo"
        is_ledger_below = step < 30
        is_ledger_above = step > 38
        if step == 32 and not note.accidental:
            return f"A Clave de Sol fixa a nota **{ref_note}** na {ref_line}."
    else:
        base_line_step = 18  # G2 is the first line
        ref_note = "Fá (F3)"
        ref_line = "4ª linha a contar de baixo"
        is_ledger_below = step < 18
        is_ledger_above = step > 26
        if step == 24 and not note.accidental:
            return f"A Clave de Fá fixa a nota **{ref_note}** na {ref_line}."

    if is_ledger_below or is_ledger_above:
        ext_type = "inferior" if is_ledger_below else "superior"
        if clef == "treble" and note.pitch == "C4":
            return "As linhas suplementares estendem a pauta. O Dó Central (C4) fica na 1ª linha suplementar inferior."
        elif clef == "bass" and note.pitch == "C4":
            return "As linhas suplementares estendem a pauta. O Dó Central (C4) fica na 1ª linha suplementar superior."
        return f"Esta é uma nota suplementar {ext_type}. Conta as linhas a partir da pauta principal para a encontrar."

    diff = step - base_line_step
    is_line = (diff % 2 == 0)
    pos_num = (diff // 2) + 1
    
    if is_line:
        pos_str = f"{pos_num}ª linha"
    else:
        pos_str = f"{pos_num}º espaço"

    return f"A nota **{note.pitch} ({note.name_pt})** encontra-se na/no {pos_str} a contar de baixo."

def generate_tutor_pool(level: int, clef: str = "treble", include_accidentals: bool = False) -> List[Note]:
    """
    Generates a pool of notes suitable for the given difficulty level.
    """
    notes = []
    
    if clef == "treble":
        lines = ["E4", "G4", "B4", "D5", "F5"]
        spaces = ["F4", "A4", "C5", "E5"]
        ledgers = ["C4", "D4", "G5", "A5"]
    else:
        lines = ["G2", "B2", "D3", "F3", "A3"]
        spaces = ["A2", "C3", "E3", "G3"]
        ledgers = ["E2", "F2", "B3", "C4"]

    pool_names = []
    if level >= 1:
        pool_names.extend(lines)
    if level >= 2:
        pool_names.extend(spaces)
    if level >= 3:
        pool_names.extend(ledgers)

    valid_notes = []
    for n in pool_names:
        valid_notes.append(Note(n))
        if include_accidentals and level == 4:
            if len(n) == 2:  # e.g., 'C4'
                valid_notes.append(Note(f"{n[0]}#{n[1]}"))
                valid_notes.append(Note(f"{n[0]}b{n[1]}"))
            
    return valid_notes
