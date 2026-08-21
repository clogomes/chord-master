"""Automatic difficulty progression tracker for ear training."""
from typing import List


DIFFICULTIES = ["beginner", "intermediate", "advanced"]

MIN_ATTEMPTS_FOR_UP = 15
UP_THRESHOLD = 0.85
MIN_ATTEMPTS_FOR_DOWN = 5
DOWN_THRESHOLD = 0.50


class AutoDifficultyTracker:
    """Tracks attempts at the current difficulty and decides when to level up or down."""

    def __init__(self):
        self._results: List[bool] = []

    @property
    def attempts(self) -> int:
        return len(self._results)

    @property
    def correct(self) -> int:
        return sum(self._results)

    @property
    def accuracy(self) -> float:
        if not self._results:
            return 0.0
        return self.correct / self.attempts

    def record(self, correct: bool) -> None:
        self._results.append(correct)

    def should_level_up(self) -> bool:
        if self.attempts < MIN_ATTEMPTS_FOR_UP:
            return False
        return self.accuracy >= UP_THRESHOLD

    def should_level_down(self) -> bool:
        if self.attempts < MIN_ATTEMPTS_FOR_DOWN:
            return False
        return self.accuracy < DOWN_THRESHOLD

    def progress_text(self) -> str:
        if self.attempts == 0:
            return "0/15 · 0% — precisas de 85% em 15 para subir"
        acc_pct = int(self.accuracy * 100)
        if self.attempts >= MIN_ATTEMPTS_FOR_UP:
            if self.accuracy >= UP_THRESHOLD:
                return f"{self.attempts}/15 · {acc_pct}% — pronto para subir!"
            return f"{self.attempts}/15 · {acc_pct}% — precisas de 85% para subir"
        return f"{self.attempts}/15 · {acc_pct}% — precisas de 85% em 15 para subir"

    def reset(self) -> None:
        self._results.clear()

    def next_difficulty(self, current: str) -> str:
        if self.should_level_up() and current != DIFFICULTIES[-1]:
            idx = DIFFICULTIES.index(current)
            return DIFFICULTIES[idx + 1]
        if self.should_level_down() and current != DIFFICULTIES[0]:
            idx = DIFFICULTIES.index(current)
            return DIFFICULTIES[idx - 1]
        return current
