"""Gamification system with XP progression, levels, badges, and achievements."""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass
class Achievement:
    """Represents an unlockable accomplishment in the music learning journey."""
    id: str
    title: str
    description: str
    icon: str
    xp_reward: int
    category: str  # "teoria", "repertorio", "auditivo", "pauta", "geral"


ACHIEVEMENT_LIBRARY: List[Achievement] = [
    Achievement(
        id="first_step",
        title="Primeiro Passo",
        description="Conclui a tua primeira lição teórica.",
        icon="🌱",
        xp_reward=100,
        category="teoria",
    ),
    Achievement(
        id="theory_scholar",
        title="Académico da Teoria",
        description="Conclui 4 capítulos da Academia de Teoria Musical.",
        icon="📖",
        xp_reward=250,
        category="teoria",
    ),
    Achievement(
        id="theory_master",
        title="Mestre da Teoria",
        description="Conclui todas as lições da Academia de Teoria Musical.",
        icon="🎓",
        xp_reward=500,
        category="teoria",
    ),
    Achievement(
        id="first_melody",
        title="Primeira Canção",
        description="Toca a tua primeira música completa no repertório.",
        icon="🎵",
        xp_reward=100,
        category="repertorio",
    ),

    Achievement(
        id="perfect_ear",
        title="Ouvido Apurado",
        description="Atinge uma sequência de 5 acertos seguidos no Treino Auditivo.",
        icon="🎧",
        xp_reward=150,
        category="auditivo",
    ),
    Achievement(
        id="sight_reader",
        title="Leitor de Pauta Ágil",
        description="Acerta 10 notas seguidas no exercício de Leitura de Pauta.",
        icon="🎼",
        xp_reward=200,
        category="pauta",
    ),

    Achievement(
        id="streak_fire",
        title="Em Chamas!",
        description="Atinge uma sequência global de 10 acertos consecutivos.",
        icon="🔥",
        xp_reward=200,
        category="geral",
    ),
    Achievement(
        id="diligent_student",
        title="Estudante Dedicado",
        description="Realiza mais de 50 exercícios práticos no total.",
        icon="⭐",
        xp_reward=300,
        category="geral",
    ),

]


LEVEL_THRESHOLDS: List[Tuple[int, str, str]] = [
    # (min_xp, level_title, icon)
    (0, "Iniciante Curioso", "🌱"),
    (150, "Aprendiz de Pauta", "🎼"),
    (400, "Mestre dos Intervalos", "🎹"),
    (800, "Harmonista Prático", "🎸"),
    (1400, "Virtuoso em Palco", "🌟"),
    (2200, "Mestre Compositor", "👑"),
    (3200, "Lenda da Música", "🏆"),
]


def get_level_info(xp: int) -> Dict:
    """Calculates level number, title, badge icon, and progress towards next level."""
    current_level = 1
    current_title = LEVEL_THRESHOLDS[0][1]
    current_icon = LEVEL_THRESHOLDS[0][2]
    current_threshold = 0
    next_threshold = LEVEL_THRESHOLDS[1][0]

    for idx, (thresh, title, icon) in enumerate(LEVEL_THRESHOLDS):
        if xp >= thresh:
            current_level = idx + 1
            current_title = title
            current_icon = icon
            current_threshold = thresh
            if idx + 1 < len(LEVEL_THRESHOLDS):
                next_threshold = LEVEL_THRESHOLDS[idx + 1][0]
            else:
                next_threshold = thresh  # Max level reached

    if current_level >= len(LEVEL_THRESHOLDS):
        progress_pct = 100.0
        xp_needed = 0
    else:
        span = next_threshold - current_threshold
        progress_pct = min(100.0, max(0.0, ((xp - current_threshold) / float(span)) * 100.0))
        xp_needed = max(0, next_threshold - xp)

    return {
        "level": current_level,
        "title": current_title,
        "icon": current_icon,
        "current_xp": xp,
        "current_threshold": current_threshold,
        "next_threshold": next_threshold,
        "xp_needed": xp_needed,
        "progress_pct": progress_pct,
    }


def get_achievement_by_id(ach_id: str) -> Optional[Achievement]:
    """Returns achievement definition matching the given id."""
    for ach in ACHIEVEMENT_LIBRARY:
        if ach.id == ach_id:
            return ach
    return None
