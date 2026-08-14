"""Music theory representation of scales and modes."""
from dataclasses import dataclass
from typing import Dict, List, Optional
from .notes import Note


@dataclass(frozen=True)
class ScaleDefinition:
    """Defines the structure of a scale pattern."""
    key: str
    name_pt: str
    name_en: str
    intervals: List[int]  # Semitones from root
    formula_steps: str   # e.g., "T - T - ST - T - T - T - ST"
    formula_degrees: str # e.g., "1 - 2 - 3 - 4 - 5 - 6 - 7"
    description: str


SCALE_TYPES: Dict[str, ScaleDefinition] = {
    "major": ScaleDefinition(
        key="major",
        name_pt="Escala Maior (Jónio)",
        name_en="Major Scale",
        intervals=[0, 2, 4, 5, 7, 9, 11, 12],
        formula_steps="Tom - Tom - Semitom - Tom - Tom - Tom - Semitom",
        formula_degrees="1 - 2 - 3 - 4 - 5 - 6 - 7",
        description="A base do sistema tonal ocidental. Soa alegre, brilhante e resoluta."
    ),
    "natural_minor": ScaleDefinition(
        key="natural_minor",
        name_pt="Escala Menor Natural (Eólio)",
        name_en="Natural Minor Scale",
        intervals=[0, 2, 3, 5, 7, 8, 10, 12],
        formula_steps="Tom - Semitom - Tom - Tom - Semitom - Tom - Tom",
        formula_degrees="1 - 2 - ♭3 - 4 - 5 - ♭6 - ♭7",
        description="O modo menor básico. Possui terça, sexta e sétima menores, conferindo um caráter melancólico."
    ),
    "harmonic_minor": ScaleDefinition(
        key="harmonic_minor",
        name_pt="Escala Menor Harmónica",
        name_en="Harmonic Minor Scale",
        intervals=[0, 2, 3, 5, 7, 8, 11, 12],
        formula_steps="Tom - Semitom - Tom - Tom - Semitom - Tom e meio - Semitom",
        formula_degrees="1 - 2 - ♭3 - 4 - 5 - ♭6 - 7",
        description="Destaca-se pelo intervalo de 1 tom e meio entre o 6º e 7º grau (sensível elevada), com sonoridade exótica e clássica."
    ),
    "melodic_minor": ScaleDefinition(
        key="melodic_minor",
        name_pt="Escala Menor Melódica",
        name_en="Melodic Minor Scale",
        intervals=[0, 2, 3, 5, 7, 9, 11, 12],
        formula_steps="Tom - Semitom - Tom - Tom - Tom - Tom - Semitom",
        formula_degrees="1 - 2 - ♭3 - 4 - 5 - 6 - 7",
        description="Eleva tanto o 6º como o 7º grau para suavizar o salto melódico da menor harmónica. Muito utilizada no Jazz."
    ),
    "major_pentatonic": ScaleDefinition(
        key="major_pentatonic",
        name_pt="Pentatónica Maior",
        name_en="Major Pentatonic",
        intervals=[0, 2, 4, 7, 9, 12],
        formula_steps="Tom - Tom - Tom e meio - Tom - Tom e meio",
        formula_degrees="1 - 2 - 3 - 5 - 6",
        description="Escala de 5 notas sem semitons nem trítonos. Soa aberta, melódica e é extremamente versátil no Pop e Rock."
    ),
    "minor_pentatonic": ScaleDefinition(
        key="minor_pentatonic",
        name_pt="Pentatónica Menor",
        name_en="Minor Pentatonic",
        intervals=[0, 3, 5, 7, 10, 12],
        formula_steps="Tom e meio - Tom - Tom - Tom e meio - Tom",
        formula_degrees="1 - ♭3 - 4 - 5 - ♭7",
        description="A escala mais famosa do Blues e Rock. É construída a partir da tónica, 3ª menor, 4ª, 5ª e 7ª menor."
    ),
    "blues": ScaleDefinition(
        key="blues",
        name_pt="Escala Blues",
        name_en="Blues Scale",
        intervals=[0, 3, 5, 6, 7, 10, 12],
        formula_steps="Tom e meio - Tom - Semitom - Semitom - Tom e meio - Tom",
        formula_degrees="1 - ♭3 - 4 - ♭5 (Blue Note) - 5 - ♭7",
        description="Pentatónica menor adicionada da famosa 'Blue Note' (5ª diminuta/4ª aumentada), dando a assinatura do Blues."
    ),
    "dorian": ScaleDefinition(
        key="dorian",
        name_pt="Modo Dórico",
        name_en="Dorian Mode",
        intervals=[0, 2, 3, 5, 7, 9, 10, 12],
        formula_steps="Tom - Semitom - Tom - Tom - Tom - Semitom - Tom",
        formula_degrees="1 - 2 - ♭3 - 4 - 5 - 6 - ♭7",
        description="Escala menor com 6ª Maior característica. Soa elegante, misteriosa e ligeiramente mais brilhante que a menor natural."
    ),
    "mixolydian": ScaleDefinition(
        key="mixolydian",
        name_pt="Modo Mixolídio",
        name_en="Mixolydian Mode",
        intervals=[0, 2, 4, 5, 7, 9, 10, 12],
        formula_steps="Tom - Tom - Semitom - Tom - Tom - Semitom - Tom",
        formula_degrees="1 - 2 - 3 - 4 - 5 - 6 - ♭7",
        description="Escala maior com 7ª Menor. Típica do Rock clássico, Blues e música tradicional celta."
    ),
    "phrygian": ScaleDefinition(
        key="phrygian",
        name_pt="Modo Frígio",
        name_en="Phrygian Mode",
        intervals=[0, 1, 3, 5, 7, 8, 10, 12],
        formula_steps="Semitom - Tom - Tom - Tom - Semitom - Tom - Tom",
        formula_degrees="1 - ♭2 - ♭3 - 4 - 5 - ♭6 - ♭7",
        description="Modo menor com 2ª menor marcante. Soa sombrio, tenso e com forte sonoridade flamenca e espanhola."
    ),
    "lydian": ScaleDefinition(
        key="lydian",
        name_pt="Modo Lídio",
        name_en="Lydian Mode",
        intervals=[0, 2, 4, 6, 7, 9, 11, 12],
        formula_steps="Tom - Tom - Tom - Semitom - Tom - Tom - Semitom",
        formula_degrees="1 - 2 - 3 - ♯4 - 5 - 6 - 7",
        description="Modo maior com 4ª aumentada (trítono). Soa etéreo, sonhador, místico e muito utilizado em trilhas sonoras de cinema."
    ),
    "locrian": ScaleDefinition(
        key="locrian",
        name_pt="Modo Lócrio",
        name_en="Locrian Mode",
        intervals=[0, 1, 3, 5, 6, 8, 10, 12],
        formula_steps="Semitom - Tom - Tom - Semitom - Tom - Tom - Tom",
        formula_degrees="1 - ♭2 - ♭3 - 4 - ♭5 - ♭6 - ♭7",
        description="O modo mais instável e tenso, com tónica diminuta (♭5). Muito usado no Metal extremo e Jazz moderno."
    ),
    "whole_tone": ScaleDefinition(
        key="whole_tone",
        name_pt="Escala de Tons Inteiros",
        name_en="Whole Tone Scale",
        intervals=[0, 2, 4, 6, 8, 10, 12],
        formula_steps="Tom - Tom - Tom - Tom - Tom - Tom",
        formula_degrees="1 - 2 - 3 - ♯4 - ♯5 - ♭7",
        description="Escala simétrica composta unicamente por intervalos de 1 tom. Cria um ambiente onírico, flutuante e impressionista."
    ),
    "chromatic": ScaleDefinition(
        key="chromatic",
        name_pt="Escala Cromática",
        name_en="Chromatic Scale",
        intervals=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
        formula_steps="Semitom x 12",
        formula_degrees="1 - ♭2 - 2 - ♭3 - 3 - 4 - ♭5 - 5 - ♭6 - 6 - ♭7 - 7",
        description="Contém todas as 12 notas do sistema temperado ocidental em semitons sucessivos."
    ),
    "bebop_dominant": ScaleDefinition(
        key="bebop_dominant",
        name_pt="Escala Bebop Dominante",
        name_en="Bebop Dominant Scale",
        intervals=[0, 2, 4, 5, 7, 9, 10, 11, 12],
        formula_steps="Tom - Tom - Semitom - Tom - Tom - Semitom - Semitom - Semitom",
        formula_degrees="1 - 2 - 3 - 4 - 5 - 6 - ♭7 - 7",
        description="Escala mixolídia com nota de passagem cromática entre a 7ª menor e a tónica. Essencial no fraseado Jazz e Bebop."
    ),
    "hungarian_minor": ScaleDefinition(
        key="hungarian_minor",
        name_pt="Escala Menor Húngara",
        name_en="Hungarian Minor Scale",
        intervals=[0, 2, 3, 6, 7, 8, 11, 12],
        formula_steps="Tom - Semitom - Tom e meio - Semitom - Semitom - Tom e meio - Semitom",
        formula_degrees="1 - 2 - ♭3 - ♯4 - 5 - ♭6 - 7",
        description="Possui dois intervalos aumentados de 1 tom e meio (graus 3-4 e 6-7), com sonoridade profundamente dramática e exótica."
    )
}


class Scale:
    """Represents a concrete Scale built on a root note."""

    def __init__(self, root: Note, scale_type: str = "major"):
        if scale_type not in SCALE_TYPES:
            raise ValueError(f"Tipo de escala inválido: '{scale_type}'")

        self.root = root
        self.scale_type = scale_type
        self.definition = SCALE_TYPES[scale_type]
        self.notes = self._generate_notes()

    def _generate_notes(self) -> List[Note]:
        """Generates all Note objects in the scale."""
        return [self.root.transpose(st) for st in self.definition.intervals]

    @property
    def name_pt(self) -> str:
        return f"{self.root.name_pt} {self.definition.name_pt}"

    @property
    def full_name(self) -> str:
        return f"{self.root.pitch} {self.definition.name_en}"

    @property
    def note_names(self) -> List[str]:
        return [n.pitch for n in self.notes]

    @property
    def note_names_pt(self) -> List[str]:
        return [n.name_pt for n in self.notes]

    def __repr__(self) -> str:
        notes_str = ", ".join(self.note_names)
        return f"Scale({self.full_name}: [{notes_str}])"


def get_scale_notes(root_name: str, scale_type: str = "major", octave: int = 4) -> List[Note]:
    """Helper function to quickly generate notes for a scale."""
    root = Note(root_name, octave=octave)
    scale = Scale(root, scale_type)
    return scale.notes
