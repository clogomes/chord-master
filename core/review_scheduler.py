"""Spaced Repetition System (SRS) using the SuperMemo SM-2 & Leitner Box algorithm for atomic musical skills."""
from dataclasses import dataclass, field, asdict
import random
import time
from typing import Any, Dict, List, Optional, Tuple
from core.notes import Note, NOTE_NAMES, NOTE_NAMES_PT
from core.intervals import INTERVALS, Interval, get_interval_by_code
from core.ear_mnemonics import get_mnemonic_by_code as get_mnemonic
from core.theory_quiz import CHAPTER_QUIZZES
from core.glossary import GLOSSARY_DATABASE, get_term_by_id


@dataclass
class ReviewItem:
    """Represents a single atomic musical skill tracked by the SM-2 algorithm."""
    skill_id: str
    category: str  # "ear", "staff", "theory", "chord", "glossary"
    prompt_pt: str
    prompt_en: str
    question_type: str  # "ear_interval", "ear_chord", "staff_note", "theory_mcq", "glossary_term"
    options_pt: List[str]
    options_en: List[str]
    correct_index: int
    explanation_pt: str
    explanation_en: str
    audio_notes: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    # SM-2 Spaced Repetition state
    ease: float = 2.5
    interval_days: float = 0.0
    repetition_count: int = 0
    lapses: int = 0
    due_at: float = 0.0
    last_reviewed_at: Optional[float] = None
    last_grade: Optional[int] = None

    def is_due(self, now: Optional[float] = None) -> bool:
        if now is None:
            now = time.time()
        return self.due_at <= now or self.repetition_count == 0

    @property
    def box(self) -> int:
        """Leitner 5-box tier (1: Novo/Revisar, 2: Aprendizagem, 3: Consolidação, 4: Retido, 5: Dominado)."""
        if self.repetition_count == 0 or self.interval_days < 1.0:
            return 1
        elif self.interval_days < 3.0:
            return 2
        elif self.interval_days < 7.0:
            return 3
        elif self.interval_days < 21.0:
            return 4
        else:
            return 5

    def to_dict(self) -> Dict[str, Any]:
        return {
            "skill_id": self.skill_id,
            "category": self.category,
            "prompt_pt": self.prompt_pt,
            "prompt_en": self.prompt_en,
            "question_type": self.question_type,
            "options_pt": self.options_pt,
            "options_en": self.options_en,
            "correct_index": self.correct_index,
            "explanation_pt": self.explanation_pt,
            "explanation_en": self.explanation_en,
            "audio_notes": self.audio_notes,
            "metadata": self.metadata,
            "ease": self.ease,
            "interval_days": self.interval_days,
            "repetition_count": self.repetition_count,
            "lapses": self.lapses,
            "due_at": self.due_at,
            "last_reviewed_at": self.last_reviewed_at,
            "last_grade": self.last_grade,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ReviewItem":
        return cls(
            skill_id=data.get("skill_id", ""),
            category=data.get("category", "theory"),
            prompt_pt=data.get("prompt_pt", ""),
            prompt_en=data.get("prompt_en", ""),
            question_type=data.get("question_type", "theory_mcq"),
            options_pt=data.get("options_pt", []),
            options_en=data.get("options_en", []),
            correct_index=data.get("correct_index", 0),
            explanation_pt=data.get("explanation_pt", ""),
            explanation_en=data.get("explanation_en", ""),
            audio_notes=data.get("audio_notes", []),
            metadata=data.get("metadata", {}),
            ease=data.get("ease", 2.5),
            interval_days=data.get("interval_days", 0.0),
            repetition_count=data.get("repetition_count", 0),
            lapses=data.get("lapses", 0),
            due_at=data.get("due_at", 0.0),
            last_reviewed_at=data.get("last_reviewed_at", None),
            last_grade=data.get("last_grade", None),
        )


def apply_sm2_grade(item: ReviewItem, grade: int, now: Optional[float] = None) -> ReviewItem:
    """
    Applies the SuperMemo SM-2 spaced repetition calculation to a ReviewItem.
    Grades:
      5: Perfect / Easy (sem hesitação)
      4: Good / Correct (após breve reflexão)
      3: Hard / Correct (com bastante esforço)
      2: Incorrect (quase acertou / lembrou ao ver resposta)
      1: Incorrect / Failed (errou)
      0: Complete blackout
    """
    if now is None:
        now = time.time()

    grade = max(0, min(5, grade))
    item.last_grade = grade
    item.last_reviewed_at = now

    if grade >= 3:
        # Success
        if item.repetition_count == 0:
            item.interval_days = 1.0
        elif item.repetition_count == 1:
            item.interval_days = 6.0
        else:
            item.interval_days = round(item.interval_days * item.ease, 1)

        item.repetition_count += 1
        # SM-2 Ease adjustment formula
        delta_ease = 0.1 - (5 - grade) * (0.08 + (5 - grade) * 0.02)
        item.ease = max(1.3, round(item.ease + delta_ease, 2))
    else:
        # Lapse / Failure
        item.repetition_count = 0
        item.interval_days = 1.0
        item.lapses += 1
        item.ease = max(1.3, round(item.ease - 0.2, 2))

    item.due_at = now + (item.interval_days * 86400.0)
    return item


# ── ATOMIC SKILL FACTORIES ───────────────────────────────────────────────────

def build_interval_review_item(interval_code: str, direction: str = "asc") -> Optional[ReviewItem]:
    """Generates an atomic ear training ReviewItem for a specific interval and direction."""
    interval = get_interval_by_code(interval_code)
    if not interval:
        return None

    dir_str_pt = "ascendente" if direction == "asc" else ("descendente" if direction == "desc" else "harmónico")
    dir_str_en = "ascending" if direction == "asc" else ("descending" if direction == "desc" else "harmonic")

    root_note = Note("C4")
    target_note = root_note.transpose(interval.semitones if direction != "desc" else -interval.semitones)

    if direction == "desc":
        audio_notes = [target_note.pitch_with_octave, root_note.pitch_with_octave]
    else:
        audio_notes = [root_note.pitch_with_octave, target_note.pitch_with_octave]

    prompt_pt = f"Identifica o intervalo {dir_str_pt} tocado pelo áudio:"
    prompt_en = f"Identify the {dir_str_en} interval played in the audio:"

    # Options pool
    correct_name_pt = interval.name_pt
    correct_name_en = interval.name_en

    # Choose 3 distractor intervals
    other_intervals = [i for i in INTERVALS.values() if i.short_code != interval_code]
    random.seed(f"{interval_code}_{direction}")
    distractors = random.sample(other_intervals, min(3, len(other_intervals)))
    all_choices = [interval] + distractors
    random.shuffle(all_choices)
    correct_idx = all_choices.index(interval)

    options_pt = [f"{i.short_code} — {i.name_pt}" for i in all_choices]
    options_en = [f"{i.short_code} — {i.name_en}" for i in all_choices]

    mnemonic = get_mnemonic(interval_code)
    mnem_str = f" Mnemónica: «{mnemonic.songs_ascending}»." if mnemonic else ""

    explanation_pt = f"O intervalo {interval.short_code} ({interval.name_pt}) tem {interval.semitones} semitons.{mnem_str}"
    explanation_en = f"The interval {interval.short_code} ({interval.name_en}) has {interval.semitones} semitones.{mnem_str}"

    return ReviewItem(
        skill_id=f"interval:{interval_code}:{direction}",
        category="ear",
        prompt_pt=prompt_pt,
        prompt_en=prompt_en,
        question_type="ear_interval",
        options_pt=options_pt,
        options_en=options_en,
        correct_index=correct_idx,
        explanation_pt=explanation_pt,
        explanation_en=explanation_en,
        audio_notes=audio_notes,
        metadata={"interval_code": interval_code, "direction": direction, "semitones": interval.semitones},
    )


def build_staff_review_item(clef: str, note_pitch: str) -> ReviewItem:
    """Generates an atomic sight-reading ReviewItem for a specific staff note."""
    note = Note(note_pitch)
    clef_name_pt = "Clave de Sol (𝄞)" if clef == "treble" else "Clave de Fá (𝄢)"
    clef_name_en = "Treble Clef (𝄞)" if clef == "treble" else "Bass Clef (𝄢)"

    prompt_pt = f"Na {clef_name_pt}, que nota está representada na pauta?"
    prompt_en = f"In {clef_name_en}, which note is shown on the staff?"

    correct_name_pt = NOTE_NAMES_PT.get(note.pitch, note.pitch)
    correct_name_en = note.letter

    # Generate 4 options
    all_notes_pt = ["Dó", "Ré", "Mi", "Fá", "Sol", "Lá", "Si"]
    all_notes_en = ["C", "D", "E", "F", "G", "A", "B"]

    distractors_pt = [n for n in all_notes_pt if n != correct_name_pt]
    random.seed(f"staff_{clef}_{note_pitch}")
    picked_pt = random.sample(distractors_pt, 3)
    choices_pt = [correct_name_pt] + picked_pt
    random.shuffle(choices_pt)
    correct_idx = choices_pt.index(correct_name_pt)

    # Align English options
    pt_to_en = dict(zip(all_notes_pt, all_notes_en))
    choices_en = [pt_to_en.get(p, p) for p in choices_pt]

    explanation_pt = f"A nota é {correct_name_pt} ({note.pitch_with_octave}) na {clef_name_pt}."
    explanation_en = f"The note is {correct_name_en} ({note.pitch_with_octave}) in {clef_name_en}."

    return ReviewItem(
        skill_id=f"staff:{clef}:{note_pitch}",
        category="staff",
        prompt_pt=prompt_pt,
        prompt_en=prompt_en,
        question_type="staff_note",
        options_pt=choices_pt,
        options_en=choices_en,
        correct_index=correct_idx,
        explanation_pt=explanation_pt,
        explanation_en=explanation_en,
        audio_notes=[note.pitch_with_octave],
        metadata={"clef": clef, "pitch": note.pitch_with_octave},
    )


def build_theory_quiz_review_item(chapter_id: str, question_idx: int) -> Optional[ReviewItem]:
    """Generates an atomic theory ReviewItem from the Chapter Quiz bank."""
    for quiz in CHAPTER_QUIZZES:
        if quiz.chapter_id == chapter_id and 0 <= question_idx < len(quiz.questions):
            q = quiz.questions[question_idx]
            return ReviewItem(
                skill_id=f"theory:{chapter_id}:q{question_idx+1}",
                category="theory",
                prompt_pt=q.question,
                prompt_en=getattr(q, "question_en", q.question),
                question_type="theory_mcq",
                options_pt=q.options,
                options_en=getattr(q, "options_en", q.options),
                correct_index=q.correct_index,
                explanation_pt=q.explanation,
                explanation_en=getattr(q, "explanation_en", q.explanation),
                metadata={"chapter_id": chapter_id, "question_index": question_idx},
            )
    return None


def build_glossary_review_item(term_id: str) -> Optional[ReviewItem]:
    """Generates an atomic glossary flashcard ReviewItem."""
    term = get_term_by_id(term_id)
    if not term:
        return None

    prompt_pt = f"Qual é o significado musical do termo «{term.term_pt}»?"
    prompt_en = f"What is the musical definition of the term '{term.term_en or term.term_pt}'?"

    correct_def_pt = term.short_def_pt
    correct_def_en = term.short_def_en

    # Pick 3 distractors from other terms
    other_terms = [t for t in GLOSSARY_DATABASE if t.id != term_id and t.category == term.category]
    if len(other_terms) < 3:
        other_terms = [t for t in GLOSSARY_DATABASE if t.id != term_id]

    random.seed(f"gloss_{term_id}")
    distractors = random.sample(other_terms, min(3, len(other_terms)))
    all_terms = [term] + distractors
    random.shuffle(all_terms)
    correct_idx = all_terms.index(term)

    options_pt = [t.short_def_pt for t in all_terms]
    options_en = [t.short_def_en for t in all_terms]

    return ReviewItem(
        skill_id=f"glossary:{term_id}",
        category="glossary",
        prompt_pt=prompt_pt,
        prompt_en=prompt_en,
        question_type="glossary_term",
        options_pt=options_pt,
        options_en=options_en,
        correct_index=correct_idx,
        explanation_pt=f"{term.term_pt}: {term.long_def_pt}",
        explanation_en=f"{term.term_en}: {term.long_def_en}",
        audio_notes=term.hear_it,
        metadata={"term_id": term_id, "category": term.category},
    )


# ── COMPREHENSIVE DEFAULT SKILL LIBRARY ───────────────────────────────────────

def generate_default_atomic_skills() -> List[ReviewItem]:
    """Builds a diverse initial pool of atomic musical skills spanning all disciplines."""
    items = []

    # 1. Ear Training Intervals (Ascending & Descending)
    interval_codes = ["2m", "2M", "3m", "3M", "4P", "TT", "5P", "6m", "6M", "7m", "7M", "8P"]
    for code in interval_codes:
        asc_item = build_interval_review_item(code, "asc")
        if asc_item:
            items.append(asc_item)
        desc_item = build_interval_review_item(code, "desc")
        if desc_item:
            items.append(desc_item)

    # 2. Staff Sight Reading (Treble & Bass clefs)
    treble_notes = ["C4", "E4", "G4", "B4", "D5", "F5", "A4", "C5", "E5"]
    for pitch in treble_notes:
        items.append(build_staff_review_item("treble", pitch))

    bass_notes = ["C3", "G2", "B2", "D3", "F3", "A3", "C4"]
    for pitch in bass_notes:
        items.append(build_staff_review_item("bass", pitch))

    # 3. Core Theory Concepts from first 8 chapters
    for chap_idx in range(1, 9):
        chap_id = f"chap{chap_idx}_fundamentals" if chap_idx == 1 else f"chap{chap_idx}"
        for q_idx in range(3):
            t_item = build_theory_quiz_review_item(chap_id, q_idx)
            if t_item:
                items.append(t_item)

    # 4. Essential Glossary Concepts
    key_glossary = [
        "tritono", "sincope", "cadencia", "sensivel", "enarmonia",
        "campo_harmonico", "serie_harmonica", "guide_tones", "walking_bass", "turnaround"
    ]
    for gid in key_glossary:
        g_item = build_glossary_review_item(gid)
        if g_item:
            items.append(g_item)

    return items


def get_due_review_queue(
    user_review_data: Dict[str, Dict[str, Any]],
    max_items: int = 15,
    now: Optional[float] = None
) -> List[ReviewItem]:
    """
    Constructs the daily review queue for a user:
    1. Fetches all existing items that are due (due_at <= now).
    2. Sorts by urgency (failed lapses first, then earliest due date).
    3. If fewer than max_items are due, draws new unpracticed skills from the default pool.
    """
    if now is None:
        now = time.time()

    user_items: List[ReviewItem] = []
    for s_dict in user_review_data.values():
        try:
            item = ReviewItem.from_dict(s_dict)
            user_items.append(item)
        except Exception:
            pass

    # Collect due items
    due_items = [item for item in user_items if item.is_due(now)]
    # Sort: lower repetition count (new/failed) first, then lowest due_at
    due_items.sort(key=lambda item: (item.repetition_count, item.due_at))

    if len(due_items) >= max_items:
        return due_items[:max_items]

    # Fill remaining capacity with new skills
    existing_skill_ids = {item.skill_id for item in user_items}
    default_pool = generate_default_atomic_skills()
    fresh_items = [it for it in default_pool if it.skill_id not in existing_skill_ids]
    random.shuffle(fresh_items)

    needed = max_items - len(due_items)
    selected = due_items + fresh_items[:needed]
    return selected
