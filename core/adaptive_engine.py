"""Adaptive Practice Engine analyzing student performance history and identifying weak areas."""
import random
import time
from typing import Any, Dict, List, Optional, Tuple
from core.user_manager import UserProfile, ExerciseRecord
from core.quiz_engine import QuizEngine, QuizQuestion, QuestionType
from core.categories import CATEGORY_NAMES_PT, CATEGORY_NAMES_EN, CATEGORY_ROUTES, CATEGORY_TIPS, CATEGORY_TIPS_EN

def get_weak_areas(user: UserProfile, max_recent: int = 50) -> List[Tuple[str, float]]:
    """
    Analyzes the user's recent exercise history and returns categories sorted
    from weakest (lowest weighted accuracy) to strongest.
    Uses exponential recency weighting so recent mistakes have higher impact.

    Returns:
        List of (category_id, weighted_accuracy_percent)
    """
    if not user.history:
        # Default baseline if no history exists
        return [
            ("leitura_pauta", 50.0),
            ("treino_auditivo", 50.0),
            ("teoria", 50.0),
            ("repertorio", 50.0),
            ("pratica_instrumento", 50.0),
        ]

    recent_records = user.history[-max_recent:]
    # Group weighted scores by category
    category_weights: Dict[str, float] = {}
    category_correct_weights: Dict[str, float] = {}

    total_count = len(recent_records)
    for idx, rec in enumerate(recent_records):
        # Recency decay: most recent record has weight 1.0, oldest has ~0.35
        weight = 0.35 + 0.65 * (float(idx) / float(total_count - 1 if total_count > 1 else 1))

        cat = rec.category or "teoria"
        category_weights[cat] = category_weights.get(cat, 0.0) + weight
        if rec.is_correct:
            category_correct_weights[cat] = category_correct_weights.get(cat, 0.0) + weight

    results = []
    # Ensure all standard categories are considered
    all_standard_cats = list(CATEGORY_NAMES_PT.keys())
    for cat in all_standard_cats:
        total_w = category_weights.get(cat, 0.0)
        if total_w > 0:
            corr_w = category_correct_weights.get(cat, 0.0)
            acc = (corr_w / total_w) * 100.0
        else:
            # If category has no attempts yet, prioritize it with neutral score
            acc = 45.0
        results.append((cat, round(acc, 1)))

    # Sort ascending by accuracy (weakest first)
    results.sort(key=lambda x: x[1])
    return results


def get_recommendation(user: UserProfile, lang: str = "pt") -> Dict[str, Any]:
    """
    Returns personalized practice recommendation metadata for the main dashboard.
    """
    weak_areas = get_weak_areas(user)
    primary_cat, acc = weak_areas[0]

    names = CATEGORY_NAMES_PT if lang == "pt" else CATEGORY_NAMES_EN
    tips = CATEGORY_TIPS if lang == "pt" else CATEGORY_TIPS_EN

    cat_name = names.get(primary_cat, "Música Geral" if lang == "pt" else "General Music")
    route = CATEGORY_ROUTES.get(primary_cat, "practice_ear")
    tip = tips.get(primary_cat, "Continua a praticar diariamente para evoluir!" if lang == "pt" else "Keep practicing daily to improve!")

    if not user.history:
        title = "Começa o teu Treino Musical" if lang == "pt" else "Start Your Musical Training"
        reason = "Ainda não realizaste exercícios hoje. Recomendamos iniciar com leitura de pauta e intervalos!" if lang == "pt" else "You haven't done any exercises today. We recommend starting with sight reading and intervals!"
    elif acc < 60.0:
        title = f"Reforço Recomendado: {cat_name}" if lang == "pt" else f"Recommended Practice: {cat_name}"
        reason = f"Identificámos que a tua precisão recente em {cat_name} é de {acc:.0f}%. Um treino focado vai acelerar o teu progresso!" if lang == "pt" else f"We noticed your recent accuracy in {cat_name} is {acc:.0f}%. Focused practice will accelerate your progress!"
    else:
        title = f"Excelente Desempenho em {cat_name}" if lang == "pt" else f"Excellent Performance in {cat_name}"
        reason = f"Estás com {acc:.0f}% de precisão! Continua a consolidar o teu domínio nesta área." if lang == "pt" else f"You have {acc:.0f}% accuracy! Keep consolidating your mastery in this area."

    return {
        "category": primary_cat,
        "category_name": cat_name,
        "accuracy": acc,
        "title": title,
        "reason": reason,
        "tip": tip,
        "route": route,
    }


def generate_adaptive_question(user: UserProfile, difficulty: str = "intermediate") -> QuizQuestion:
    """
    Generates a quiz question with 60% bias towards the student's weakest area,
    and 40% balanced general exploration.
    """
    weak_areas = get_weak_areas(user)
    weakest_cat = weak_areas[0][0] if weak_areas else "treino_auditivo"

    # 60% probability of targeting the weakest area
    if random.random() < 0.60:
        chosen_cat = weakest_cat
    else:
        chosen_cat = random.choice(["treino_auditivo", "leitura_pauta", "teoria"])

    if chosen_cat == "leitura_pauta":
        clef = random.choice(["treble", "bass"])
        return QuizEngine.generate_staff_question(clef=clef, difficulty=difficulty)
    elif chosen_cat == "teoria":
        return QuizEngine.generate_theory_question()
    elif chosen_cat == "pratica_instrumento":
        return QuizEngine.generate_solfege_sing_question(difficulty=difficulty)
    else:
        if random.random() < 0.5:
            return QuizEngine.generate_ear_interval_question(difficulty=difficulty)
        else:
            return QuizEngine.generate_ear_chord_question(difficulty=difficulty)
