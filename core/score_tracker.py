"""Score tracking, accuracy statistics, streak calculations, and JSON persistence."""
import json
import os
import time
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class CategoryStats:
    """Statistics for a specific practice or theory category."""
    total_attempts: int = 0
    correct_count: int = 0
    current_streak: int = 0
    best_streak: int = 0

    @property
    def accuracy_rate(self) -> float:
        if self.total_attempts == 0:
            return 0.0
        return (self.correct_count / self.total_attempts) * 100.0


@dataclass
class ExerciseRecord:
    """Historical log of an answered question."""
    timestamp: float
    category: str
    question_type: str
    is_correct: bool
    prompt: str
    user_answer: str
    correct_answer: str


class ScoreTracker:
    """Manages player scores, accuracy metrics, and persistence across sessions."""

    def __init__(self, filepath: Optional[str] = None):
        if filepath is None:
            # Default to chord-master directory user_scores.json
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.filepath = os.path.join(base_dir, "user_scores.json")
        else:
            self.filepath = filepath

        self.categories: Dict[str, CategoryStats] = {
            "treino_auditivo": CategoryStats(),
            "leitura_pauta": CategoryStats(),
            "teoria": CategoryStats(),
        }
        self.history: List[ExerciseRecord] = []
        self.load()

    def record_attempt(
        self,
        category: str,
        question_type: str,
        is_correct: bool,
        prompt: str = "",
        user_answer: str = "",
        correct_answer: str = "",
    ) -> CategoryStats:
        """Records an answer attempt, updates streaks and saves data."""
        if category not in self.categories:
            self.categories[category] = CategoryStats()

        stats = self.categories[category]
        stats.total_attempts += 1

        if is_correct:
            stats.correct_count += 1
            stats.current_streak += 1
            if stats.current_streak > stats.best_streak:
                stats.best_streak = stats.current_streak
        else:
            stats.current_streak = 0

        # Add to history log (keep last 100 entries)
        record = ExerciseRecord(
            timestamp=time.time(),
            category=category,
            question_type=question_type,
            is_correct=is_correct,
            prompt=prompt,
            user_answer=user_answer,
            correct_answer=correct_answer,
        )
        self.history.append(record)
        if len(self.history) > 100:
            self.history = self.history[-100:]

        self.save()
        return stats

    @property
    def total_attempts(self) -> int:
        return sum(c.total_attempts for c in self.categories.values())

    @property
    def total_correct(self) -> int:
        return sum(c.correct_count for c in self.categories.values())

    @property
    def global_accuracy(self) -> float:
        if self.total_attempts == 0:
            return 0.0
        return (self.total_correct / self.total_attempts) * 100.0

    @property
    def global_best_streak(self) -> int:
        return max((c.best_streak for c in self.categories.values()), default=0)

    def get_category_stats(self, category: str) -> CategoryStats:
        return self.categories.get(category, CategoryStats())

    def reset_all(self):
        """Resets all recorded scores and clears historical entries."""
        for cat in self.categories.keys():
            self.categories[cat] = CategoryStats()
        self.history.clear()
        self.save()

    def save(self):
        """Persists current statistics and history to JSON."""
        data = {
            "categories": {
                k: {
                    "total_attempts": v.total_attempts,
                    "correct_count": v.correct_count,
                    "current_streak": v.current_streak,
                    "best_streak": v.best_streak,
                }
                for k, v in self.categories.items()
            },
            "history": [asdict(r) for r in self.history],
        }
        try:
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Erro ao salvar progresso em {self.filepath}: {e}")

    def load(self):
        """Loads statistics and history from JSON if file exists."""
        if not os.path.exists(self.filepath) or os.path.getsize(self.filepath) == 0:
            return

        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                data = json.load(f)

            if "categories" in data:
                for k, v in data["categories"].items():
                    self.categories[k] = CategoryStats(
                        total_attempts=v.get("total_attempts", 0),
                        correct_count=v.get("correct_count", 0),
                        current_streak=v.get("current_streak", 0),
                        best_streak=v.get("best_streak", 0),
                    )

            if "history" in data:
                self.history = [
                    ExerciseRecord(
                        timestamp=h.get("timestamp", 0.0),
                        category=h.get("category", "treino_auditivo"),
                        question_type=h.get("question_type", "unknown"),
                        is_correct=h.get("is_correct", False),
                        prompt=h.get("prompt", ""),
                        user_answer=h.get("user_answer", ""),
                        correct_answer=h.get("correct_answer", ""),
                    )
                    for h in data["history"]
                ]
        except Exception as e:
            print(f"Erro ao carregar progresso de {self.filepath}: {e}")
