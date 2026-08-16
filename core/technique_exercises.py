"""Technique exercises module for piano and guitar warmup, dexterity, and strength drills."""
from dataclasses import dataclass, field
from typing import List, Tuple
from core.notes import Note


@dataclass
class TechniqueExercise:
    """Dataclass defining a technical exercise drill."""
    id: str
    name_pt: str
    name_en: str
    category: str  # "aquecimento", "destreza", "forca_agilidade"
    instrument: str  # "piano", "guitar", "ambos"
    difficulty: str  # "Iniciante", "Intermédio", "Avançado"
    description_pt: str
    description_en: str
    notes: List[Note] = field(default_factory=list)
    recommended_bpm_range: Tuple[int, int] = (60, 120)

    def get_name(self, lang: str = "pt") -> str:
        return self.name_en if lang == "en" and self.name_en else self.name_pt

    def get_description(self, lang: str = "pt") -> str:
        return self.description_en if lang == "en" and self.description_en else self.description_pt


TECHNIQUE_EXERCISES: List[TechniqueExercise] = [
    # ----------------------------------------------------
    # PIANO EXERCISES
    # ----------------------------------------------------
    TechniqueExercise(
        id="piano_warmup_5fingers",
        name_pt="Aquecimento de 5 Dedos (Dó Maior)",
        name_en="5-Finger Warmup (C Major)",
        category="aquecimento",
        instrument="piano",
        difficulty="Iniciante",
        description_pt="Exercício de aquecimento fundamental para articulação individual dos dedos 1 a 5.",
        description_en="Essential warmup drill for independent articulation of fingers 1 through 5.",
        notes=[
            Note("C4"), Note("D4"), Note("E4"), Note("F4"), Note("G4"),
            Note("F4"), Note("E4"), Note("D4"), Note("C4"),
        ],
        recommended_bpm_range=(60, 100),
    ),
    TechniqueExercise(
        id="piano_hanon_1",
        name_pt="Hanon No. 1 — Independência de Dedos",
        name_en="Hanon No. 1 — Finger Independence",
        category="destreza",
        instrument="piano",
        difficulty="Intermédio",
        description_pt="Padrão clássico de Hanon No. 1 para independência e articulação dos dedos 4 e 5.",
        description_en="Classic Hanon No. 1 pattern for 4th and 5th finger independence across the octave.",
        notes=[
            Note("C4"), Note("E4"), Note("F4"), Note("G4"), Note("A4"), Note("G4"), Note("F4"), Note("E4"),
            Note("D4"), Note("F4"), Note("G4"), Note("A4"), Note("B4"), Note("A4"), Note("G4"), Note("F4"),
            Note("E4"), Note("G4"), Note("A4"), Note("B4"), Note("C5"), Note("B4"), Note("A4"), Note("G4"),
            Note("F4"), Note("A4"), Note("B4"), Note("C5"), Note("D5"), Note("C5"), Note("B4"), Note("A4"),
            Note("G4"), Note("B4"), Note("C5"), Note("D5"), Note("E5"), Note("D5"), Note("C5"), Note("B4"),
            Note("C5"),
        ],
        recommended_bpm_range=(60, 115),
    ),
    TechniqueExercise(
        id="piano_chromatic_2octaves",
        name_pt="Escala Cromática de Passagem",
        name_en="Chromatic Scale Drill",
        category="destreza",
        instrument="piano",
        difficulty="Intermédio",
        description_pt="Desenvolve velocidade na passagem rápida de dedos em todas as 12 notas semitonais.",
        description_en="Builds speed and thumb-under agility across all 12 semitones.",
        notes=[
            Note("C4"), Note("C#4"), Note("D4"), Note("D#4"), Note("E4"), Note("F4"),
            Note("F#4"), Note("G4"), Note("G#4"), Note("A4"), Note("A#4"), Note("B4"), Note("C5"),
        ],
        recommended_bpm_range=(70, 130),
    ),
    TechniqueExercise(
        id="piano_arpeggios_c",
        name_pt="Arpejos Triádicos Ascendentes/Descendentes",
        name_en="Triadic Arpeggio Drill (C Major)",
        category="forca_agilidade",
        instrument="piano",
        difficulty="Avançado",
        description_pt="Fortalece a abertura da mão e a transição suave de oitavas em arpejos de C Maior.",
        description_en="Strengthens hand stretch and fluid octave transitions in C Major arpeggios.",
        notes=[
            Note("C3"), Note("E3"), Note("G3"), Note("C4"), Note("E4"), Note("G4"), Note("C5"),
            Note("G4"), Note("E4"), Note("C4"), Note("G3"), Note("E3"), Note("C3"),
        ],
        recommended_bpm_range=(60, 120),
    ),
    TechniqueExercise(
        id="piano_contrary_motion",
        name_pt="Escala Diatónica Ascendente e Descendente",
        name_en="Diatonic Scale Drill (Ascending & Descending)",
        category="forca_agilidade",
        instrument="piano",
        difficulty="Avançado",
        description_pt="Desenvolve fluidez, passagem rápida do polegar e articulação uniforme na escala de Dó Maior.",
        description_en="Builds speed, smooth thumb-under passing, and even articulation across C Major.",
        notes=[
            Note("C4"), Note("D4"), Note("E4"), Note("F4"), Note("G4"), Note("A4"), Note("B4"), Note("C5"),
            Note("B4"), Note("A4"), Note("G4"), Note("F4"), Note("E4"), Note("D4"), Note("C4"),
        ],
        recommended_bpm_range=(60, 110),
    ),

    # ----------------------------------------------------
    # GUITAR / VIOLA EXERCISES
    # ----------------------------------------------------
    TechniqueExercise(
        id="guitar_spider_walk",
        name_pt="Spider Walk Cromático (1-2-3-4)",
        name_en="Chromatic Spider Walk (1-2-3-4)",
        category="aquecimento",
        instrument="guitar",
        difficulty="Iniciante",
        description_pt="O exercício de aquecimento clássico para violão/guitarra usando os trastes 1-2-3-4 em cada corda.",
        description_en="The quintessential guitar warmup drill using frets 1-2-3-4 across strings.",
        notes=[
            Note("F2"), Note("F#2"), Note("G2"), Note("G#2"),
            Note("A#2"), Note("B2"), Note("C3"), Note("C#3"),
            Note("D#3"), Note("E3"), Note("F3"), Note("F#3"),
            Note("G#3"), Note("A3"), Note("A#3"), Note("B3"),
        ],
        recommended_bpm_range=(60, 110),
    ),
    TechniqueExercise(
        id="guitar_string_skipping",
        name_pt="Salto de Cordas (String Skipping)",
        name_en="String Skipping Drill",
        category="destreza",
        instrument="guitar",
        difficulty="Intermédio",
        description_pt="Exercício de destreza para precisão da mão direita na alternância de cordas não adjacentes.",
        description_en="Dexterity exercise for right-hand picking precision across non-adjacent strings.",
        notes=[
            Note("E2"), Note("D3"), Note("A2"), Note("G3"),
            Note("D3"), Note("B3"), Note("G3"), Note("E4"),
            Note("D3"), Note("E2"),
        ],
        recommended_bpm_range=(60, 105),
    ),
    TechniqueExercise(
        id="guitar_alternate_picking",
        name_pt="Palhetada Alternada Rápida (Down-Up)",
        name_en="Alternate Picking Speed Drill",
        category="forca_agilidade",
        instrument="guitar",
        difficulty="Intermédio",
        description_pt="Treino de velocidade e sincronismo estrito entre palhetada descendente e ascendente.",
        description_en="Speed and strict synchronization drill for alternate down-up picking.",
        notes=[
            Note("A3"), Note("B3"), Note("C4"), Note("B3"), Note("A3"), Note("G3"), Note("F3"), Note("E3"),
            Note("A3"), Note("C4"), Note("E4"), Note("C4"), Note("A3"),
        ],
        recommended_bpm_range=(70, 130),
    ),
    TechniqueExercise(
        id="guitar_finger_stretch",
        name_pt="Alongamento de Dedos (Trastes 1-3-5)",
        name_en="Finger Stretching Drill (Frets 1-3-5)",
        category="forca_agilidade",
        instrument="guitar",
        difficulty="Avançado",
        description_pt="Desenvolve flexibilidade muscular e abertura da mão esquerda usando os trastes 1-3-5 nas cordas graves.",
        description_en="Develops left-hand muscular flexibility and finger span using frets 1-3-5 across low strings.",
        notes=[
            Note("F2"), Note("G2"), Note("A2"),
            Note("A#2"), Note("C3"), Note("D3"),
            Note("D#3"), Note("F3"), Note("G3"),
        ],
        recommended_bpm_range=(50, 95),
    ),
]


def get_exercises_by_instrument(instrument: str = "ambos") -> List[TechniqueExercise]:
    if instrument == "ambos":
        return TECHNIQUE_EXERCISES
    return [e for e in TECHNIQUE_EXERCISES if e.instrument in (instrument, "ambos")]
