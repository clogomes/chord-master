"""Biblioteca de padrões rítmicos para o Ecrã de Prática Rítmica (Fase 49).

Cada `RhythmPattern_Exercise` descreve um padrão de duração a bater ao
compasso do metrónomo. `durations` está expresso em *tempos* (1 = semínima):

    1.0  -> semínima        0.5  -> colcheia
    0.25 -> semicolcheia    1.5  -> semínima pontuada

A soma de `durations` deve igualar o nº de tempos da medida definida por
`time_signature` (ex.: "4/4" = 4 tempos, "3/4" = 3, "6/8" = 6 colcheias).
"""
from dataclasses import dataclass
from typing import List


@dataclass
class RhythmPattern_Exercise:
    id: str
    name_pt: str
    name_en: str
    level: int                      # 1..5
    time_signature: str             # "4/4", "3/4", "6/8"
    durations: List[float]          # em tempos
    description_pt: str
    description_en: str

    @property
    def total_beats(self) -> float:
        return round(sum(self.durations), 6)

    def get_name(self, lang: str) -> str:
        return self.name_pt if lang == "pt" else self.name_en

    def get_description(self, lang: str) -> str:
        return self.description_pt if lang == "pt" else self.description_en


RHYTHM_EXERCISES: List[RhythmPattern_Exercise] = [
    # ---- Nível 1 — Semínimas (1 por tempo) --------------------------------
    RhythmPattern_Exercise(
        id="q_44_quarters",
        name_pt="Semínimas (1 por tempo)",
        name_en="Quarter notes (1 per beat)",
        level=1,
        time_signature="4/4",
        durations=[1.0, 1.0, 1.0, 1.0],
        description_pt="Bate uma vez em cada tempo. Segue o pulso do metrónomo.",
        description_en="Tap once per beat. Follow the metronome pulse.",
    ),
    RhythmPattern_Exercise(
        id="q_34_quarters",
        name_pt="Semínimas em 3/4",
        name_en="Quarter notes in 3/4",
        level=1,
        time_signature="3/4",
        durations=[1.0, 1.0, 1.0],
        description_pt="Três tempos fortes por compasso. Mantém o pulso redondo.",
        description_en="Three beats per measure. Keep the round pulse steady.",
    ),
    # ---- Nível 2 — Colcheias (subdivisão em 2) -----------------------------
    RhythmPattern_Exercise(
        id="e_44_eighths",
        name_pt="Colcheias (subdivisão em 2)",
        name_en="Eighth notes (divide by 2)",
        level=2,
        time_signature="4/4",
        durations=[0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5],
        description_pt="Dois por tempo: 'e-e'. Divide cada tempo em duas partes iguais.",
        description_en="Two per beat: 'and'. Divide each beat into two equal parts.",
    ),
    RhythmPattern_Exercise(
        id="e_34_eighths",
        name_pt="Colcheias em 3/4",
        name_en="Eighth notes in 3/4",
        level=2,
        time_signature="3/4",
        durations=[0.5, 0.5, 0.5, 0.5, 0.5, 0.5],
        description_pt="Seis colcheias no compasso. Mantém a subdivisão uniforme.",
        description_en="Six eighths in the measure. Keep the subdivision even.",
    ),
    # ---- Nível 3 — Semínima pontuada + colcheia ----------------------------
    RhythmPattern_Exercise(
        id="dq_44_dotted",
        name_pt="Semínima pontuada + colcheia",
        name_en="Dotted quarter + eighth",
        level=3,
        time_signature="4/4",
        durations=[1.5, 0.5, 1.5, 0.5],
        description_pt="O padrão que mais faz tropeçar: 1.5 tempos + 0.5. Sente o '3 e 1'.",
        description_en="The classic stumbling block: 1.5 beats + 0.5. Feel the '3 and 1'.",
    ),
    RhythmPattern_Exercise(
        id="dq_68_dotted",
        name_pt="Pontuada em 6/8",
        name_en="Dotted rhythm in 6/8",
        level=3,
        time_signature="6/8",
        durations=[0.75, 0.25, 0.75, 0.25, 0.75, 0.25],
        description_pt="Colcheia pontuada + semicolcheia, 3 grupos. Sente o duplo pulso do 6/8.",
        description_en="Dotted eighth + sixteenth, 3 groups. Feel the compound pulse of 6/8.",
    ),
    # ---- Nível 4 — Semicolcheias (subdivisão em 4) -------------------------
    RhythmPattern_Exercise(
        id="x16_44_sixteenths",
        name_pt="Semicolcheias (subdivisão em 4)",
        name_en="Sixteenth notes (divide by 4)",
        level=4,
        time_signature="4/4",
        durations=[0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25,
                    0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25],
        description_pt="Quatro por tempo: muito rápido e uniforme. Começa devagar.",
        description_en="Four per beat: fast and even. Start slow.",
    ),
    RhythmPattern_Exercise(
        id="x16_44_mixed",
        name_pt="Misto: colcheia + 2 semicolcheias",
        name_en="Mixed: eighth + 2 sixteenths",
        level=4,
        time_signature="4/4",
        durations=[0.5, 0.25, 0.25, 0.5, 0.25, 0.25, 0.5, 0.25, 0.25, 0.5, 0.25, 0.25],
        description_pt="Combina colcheias com pares de semicolcheias. Mantém o pulso de fundo.",
        description_en="Mixes eighths with pairs of sixteenths. Keep the underlying pulse.",
    ),
    # ---- Nível 5 — Síncopa --------------------------------------------------
    RhythmPattern_Exercise(
        id="s_44_syncopation",
        name_pt="Síncopa (acentos fora do tempo forte)",
        name_en="Syncopation (accents off the beat)",
        level=5,
        time_signature="4/4",
        durations=[0.5, 0.5, 1.0, 0.5, 0.5, 1.0],
        description_pt="Colcheia + semínima em ligadura: o acento cai no meio do tempo. Resiste a acentar o tempo forte.",
        description_en="Tied eighth + quarter: the accent lands off the beat. Resist accenting the downbeat.",
    ),
    RhythmPattern_Exercise(
        id="s_34_syncopation",
        name_pt="Síncopa em 3/4",
        name_en="Syncopation in 3/4",
        level=5,
        time_signature="3/4",
        durations=[0.5, 0.5, 1.0, 0.5, 0.5],
        description_pt="Semínima em ligadura que atravessa o tempo: acenta o 'e' entre os tempos.",
        description_en="A tied quarter across the beat: accent the 'and' between beats.",
    ),
]


def get_exercises_by_level(level: int) -> List[RhythmPattern_Exercise]:
    return [e for e in RHYTHM_EXERCISES if e.level == level]


def get_exercise_by_id(exercise_id: str):
    for e in RHYTHM_EXERCISES:
        if e.id == exercise_id:
            return e
    return None
