"""Music theory representation of musical intervals and transposition."""
from dataclasses import dataclass
from typing import Dict, List, Optional, Union
from .notes import Note


@dataclass(frozen=True)
class Interval:
    """Represents a musical interval defined by semitones and quality."""
    semitones: int
    name_pt: str
    name_en: str
    short_code: str
    mnemonic: str
    description: str


INTERVALS: Dict[int, Interval] = {
    0: Interval(
        semitones=0,
        name_pt="Uníssono Perfeito",
        name_en="Perfect Unison",
        short_code="P1",
        mnemonic="Mesma nota",
        description="A mesma frequência/nota tocada sem variação de altura."
    ),
    1: Interval(
        semitones=1,
        name_pt="Segunda Menor",
        name_en="Minor 2nd",
        short_code="m2",
        mnemonic="Tema de 'Tubarão' (Jaws)",
        description="Distância de 1 semitom (meio-tom). Altamente dissonante e tenso."
    ),
    2: Interval(
        semitones=2,
        name_pt="Segunda Maior",
        name_en="Major 2nd",
        short_code="M2",
        mnemonic="'Parabéns a Você' (1º salto)",
        description="Distância de 2 semitons (1 tom inteiro). Passo natural da escala maior."
    ),
    3: Interval(
        semitones=3,
        name_pt="Terça Menor",
        name_en="Minor 3rd",
        short_code="m3",
        mnemonic="'Greensleeves' / 'Smoke on the Water'",
        description="Distância de 3 semitons (1 tom e meio). Define a sonoridade de acordes menores (melancólico)."
    ),
    4: Interval(
        semitones=4,
        name_pt="Terça Maior",
        name_en="Major 3rd",
        short_code="M3",
        mnemonic="'Oh When the Saints' / 'Kumbaya'",
        description="Distância de 4 semitons (2 tons inteiros). Define a sonoridade de acordes maiores (brilhante/alegre)."
    ),
    5: Interval(
        semitones=5,
        name_pt="Quarta Justa",
        name_en="Perfect 4th",
        short_code="P4",
        mnemonic="'Hino da Champions League' / Marcha Nupcial",
        description="Distância de 5 semitons (2 tons e meio). Intervalo de grande estabilidade harmónica."
    ),
    6: Interval(
        semitones=6,
        name_pt="Trítono (4ª Aumentada / 5ª Diminuta)",
        name_en="Tritone",
        short_code="TT",
        mnemonic="Tema dos 'Simpsons' / 'Maria' (West Side Story)",
        description="Distância de 6 semitons (3 tons inteiros). Historicamente conhecido como 'Diabolus in Musica', muito tenso."
    ),
    7: Interval(
        semitones=7,
        name_pt="Quinta Justa",
        name_en="Perfect 5th",
        short_code="P5",
        mnemonic="Tema de 'Star Wars' / 'Twinkle Twinkle'",
        description="Distância de 7 semitons (3 tons e meio). A base das quintas e dos acordes fundamentais (power chords)."
    ),
    8: Interval(
        semitones=8,
        name_pt="Sexta Menor",
        name_en="Minor 6th",
        short_code="m6",
        mnemonic="'Love Story' / 'In My Life' (Beatles)",
        description="Distância de 8 semitons (4 tons inteiros). Sonoridade emotiva e profunda."
    ),
    9: Interval(
        semitones=9,
        name_pt="Sexta Maior",
        name_en="Major 6th",
        short_code="M6",
        mnemonic="'My Bonnie Lies over the Ocean' / 'Aquarela do Brasil'",
        description="Distância de 9 semitons (4 tons e meio). Intervalo aberto, doce e consonante."
    ),
    10: Interval(
        semitones=10,
        name_pt="Sétima Menor",
        name_en="Minor 7th",
        short_code="m7",
        mnemonic="'The Winner Takes It All' (ABBA) / 'Somewhere' (West Side Story)",
        description="Distância de 10 semitons (5 tons). Essencial em acordes de dominante e blues/jazz."
    ),
    11: Interval(
        semitones=11,
        name_pt="Sétima Maior",
        name_en="Major 7th",
        short_code="M7",
        mnemonic="'Take On Me' (refrão) / 'Superman' tema",
        description="Distância de 11 semitons (5 tons e meio). Forte atração para a tónica superior, usado em bossa nova e jazz."
    ),
    12: Interval(
        semitones=12,
        name_pt="Oitava Justa",
        name_en="Perfect Octave",
        short_code="P8",
        mnemonic="'Somewhere Over the Rainbow'",
        description="Distância de 12 semitons (6 tons). A mesma nota, mas com o dobro da frequência sonora."
    )
}

INTERVAL_NAMES_PT = {v.short_code: v.name_pt for v in INTERVALS.values()}


def get_interval(root: Note, target: Note) -> Interval:
    """Returns the Interval object between two notes."""
    semitones = abs(target.midi - root.midi) % 13
    if semitones in INTERVALS:
        return INTERVALS[semitones]
    # For intervals > 12 (compound intervals), reduce to simple interval
    simple_semitones = semitones % 12
    return INTERVALS.get(simple_semitones, INTERVALS[12])


def transpose_note(root: Note, semitones: int) -> Note:
    """Transposes a note by a given number of semitones."""
    return root.transpose(semitones)


def get_interval_by_code(code: str) -> Optional[Interval]:
    """Retrieves an interval by its short code (e.g. 'm3', 'P5', 'M7')."""
    for interval in INTERVALS.values():
        if interval.short_code == code:
            return interval
    return None
