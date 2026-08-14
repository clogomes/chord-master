"""Multi-user profile manager, progress tracking, and persistence."""
import json
import os
import time
from dataclasses import asdict, dataclass, field
from typing import Dict, List, Optional
from .score_tracker import CategoryStats, ExerciseRecord

AVATAR_CHOICES = ["🎵", "🎹", "🎸", "🎻", "🎧", "🎷", "🎺", "🥁", "🎼", "🌟"]

LESSON_IDS = [
    ("chap1_fundamentals", "1. Fundamentos & Notação"),
    ("chap2_intervals", "2. Intervalos & Acústica"),
    ("chap3_scales_modes", "3. Escalas & Modos"),
    ("chap4_chords_triads", "4. Tríades & Inversões"),
    ("chap5_harmonic_field_tetrads", "5. Campo Harmónico & Tétrades"),
    ("chap6_advanced_harmony", "6. Harmonia Avançada"),
    ("chap7_piano_guide", "7. Guia Prático de Piano"),
    ("chap8_guitar_guide", "8. Guia Prático de Viola (CAGED)"),
]


@dataclass
class UserProfile:
    """Represents a single student profile with independent stats and lesson progress."""
    username: str
    avatar: str = "🎵"
    created_at: float = field(default_factory=time.time)
    categories: Dict[str, CategoryStats] = field(default_factory=lambda: {
        "treino_auditivo": CategoryStats(),
        "leitura_pauta": CategoryStats(),
        "teoria": CategoryStats(),
        "repertorio": CategoryStats(),
        "pratica_instrumento": CategoryStats(),
    })
    completed_lessons: List[str] = field(default_factory=list)
    history: List[ExerciseRecord] = field(default_factory=list)

    @property
    def total_attempts(self) -> int:
        return sum(c.total_attempts for c in self.categories.values())

    @property
    def total_correct(self) -> int:
        return sum(c.correct_count for c in self.categories.values())

    @property
    def accuracy_rate(self) -> float:
        if self.total_attempts == 0:
            return 0.0
        return (self.total_correct / self.total_attempts) * 100.0

    @property
    def best_streak(self) -> int:
        return max((c.best_streak for c in self.categories.values()), default=0)

    @property
    def lessons_progress_percent(self) -> float:
        total_lessons = len(LESSON_IDS)
        if total_lessons == 0:
            return 0.0
        return (len(self.completed_lessons) / total_lessons) * 100.0


class UserManager:
    """Manages multiple local user profiles with switching, progress saving, and leaderboards."""

    def __init__(self, filepath: Optional[str] = None):
        if filepath is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.filepath = os.path.join(base_dir, "user_profiles.json")
            self.legacy_filepath = os.path.join(base_dir, "user_scores.json")
        else:
            self.filepath = filepath
            self.legacy_filepath = ""

        self.profiles: Dict[str, UserProfile] = {}
        self.active_username: str = "Utilizador 1"
        self.load()

        if not self.profiles:
            # Create default profile
            self.create_user("Utilizador 1", avatar="🎵")
            self.active_username = "Utilizador 1"

    @property
    def current_user(self) -> UserProfile:
        if self.active_username not in self.profiles:
            # Pick first available or create default
            if self.profiles:
                self.active_username = next(iter(self.profiles.keys()))
            else:
                self.create_user("Utilizador 1")
                self.active_username = "Utilizador 1"
        return self.profiles[self.active_username]

    def get_all_users(self) -> List[UserProfile]:
        """Returns all registered user profiles sorted by creation date."""
        return list(self.profiles.values())

    def create_user(self, username: str, avatar: str = "🎵") -> UserProfile:
        """Creates and activates a new user profile."""
        clean_name = username.strip()
        if not clean_name:
            clean_name = f"Utilizador {len(self.profiles) + 1}"

        # If name exists, add suffix
        base_name = clean_name
        counter = 2
        while clean_name in self.profiles:
            clean_name = f"{base_name} ({counter})"
            counter += 1

        profile = UserProfile(
            username=clean_name,
            avatar=avatar,
            created_at=time.time(),
        )
        self.profiles[clean_name] = profile
        self.active_username = clean_name
        self.save()
        return profile

    def switch_user(self, username: str) -> bool:
        """Switches the active user profile."""
        if username in self.profiles:
            self.active_username = username
            self.save()
            return True
        return False

    def delete_user(self, username: str) -> bool:
        """Deletes a user profile (cannot delete if it's the only one)."""
        if len(self.profiles) <= 1:
            return False

        if username in self.profiles:
            del self.profiles[username]
            if self.active_username == username:
                self.active_username = next(iter(self.profiles.keys()))
            self.save()
            return True
        return False

    def mark_lesson_completed(self, lesson_id: str) -> bool:
        """Marks a theory lesson as completed for the current user."""
        user = self.current_user
        if lesson_id not in user.completed_lessons:
            user.completed_lessons.append(lesson_id)
            self.save()
            return True
        return False

    def is_lesson_completed(self, lesson_id: str) -> bool:
        """Checks if a theory lesson is completed for the current user."""
        return lesson_id in self.current_user.completed_lessons

    def record_attempt(
        self,
        category: str,
        question_type: str,
        is_correct: bool,
        prompt: str = "",
        user_answer: str = "",
        correct_answer: str = "",
    ) -> CategoryStats:
        """Records an exercise attempt for the active user."""
        user = self.current_user
        if category not in user.categories:
            user.categories[category] = CategoryStats()

        stats = user.categories[category]
        stats.total_attempts += 1

        if is_correct:
            stats.correct_count += 1
            stats.current_streak += 1
            if stats.current_streak > stats.best_streak:
                stats.best_streak = stats.current_streak
        else:
            stats.current_streak = 0

        # Add to history
        record = ExerciseRecord(
            timestamp=time.time(),
            category=category,
            question_type=question_type,
            is_correct=is_correct,
            prompt=prompt,
            user_answer=user_answer,
            correct_answer=correct_answer,
        )
        user.history.append(record)
        if len(user.history) > 100:
            user.history = user.history[-100:]

        self.save()
        return stats

    def reset_current_user_scores(self):
        """Resets scores and progress for the active user only."""
        user = self.current_user
        for cat in user.categories.keys():
            user.categories[cat] = CategoryStats()
        user.history.clear()
        user.completed_lessons.clear()
        self.save()

    def save(self):
        """Persists all profiles and the active user to JSON."""
        data = {
            "active_user": self.active_username,
            "users": {}
        }
        for name, profile in self.profiles.items():
            data["users"][name] = {
                "username": profile.username,
                "avatar": profile.avatar,
                "created_at": profile.created_at,
                "completed_lessons": profile.completed_lessons,
                "categories": {
                    k: {
                        "total_attempts": v.total_attempts,
                        "correct_count": v.correct_count,
                        "current_streak": v.current_streak,
                        "best_streak": v.best_streak,
                    }
                    for k, v in profile.categories.items()
                },
                "history": [asdict(r) for r in profile.history],
            }

        try:
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[UserManager] Erro ao salvar utilizadores em {self.filepath}: {e}")

    def load(self):
        """Loads profiles from JSON, with migration from legacy user_scores.json."""
        if os.path.exists(self.filepath) and os.path.getsize(self.filepath) > 0:
            try:
                with open(self.filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)

                self.active_username = data.get("active_user", "Utilizador 1")
                self.profiles.clear()

                for name, udata in data.get("users", {}).items():
                    categories = {}
                    for ck, cv in udata.get("categories", {}).items():
                        categories[ck] = CategoryStats(
                            total_attempts=cv.get("total_attempts", 0),
                            correct_count=cv.get("correct_count", 0),
                            current_streak=cv.get("current_streak", 0),
                            best_streak=cv.get("best_streak", 0),
                        )
                    history = [
                        ExerciseRecord(
                            timestamp=h.get("timestamp", 0.0),
                            category=h.get("category", "treino_auditivo"),
                            question_type=h.get("question_type", "unknown"),
                            is_correct=h.get("is_correct", False),
                            prompt=h.get("prompt", ""),
                            user_answer=h.get("user_answer", ""),
                            correct_answer=h.get("correct_answer", ""),
                        )
                        for h in udata.get("history", [])
                    ]
                    profile = UserProfile(
                        username=udata.get("username", name),
                        avatar=udata.get("avatar", "🎵"),
                        created_at=udata.get("created_at", time.time()),
                        categories=categories,
                        completed_lessons=udata.get("completed_lessons", []),
                        history=history,
                    )
                    self.profiles[profile.username] = profile
                return
            except Exception as e:
                print(f"[UserManager] Erro ao carregar {self.filepath}: {e}")

        # Migration from legacy user_scores.json if present
        if self.legacy_filepath and os.path.exists(self.legacy_filepath) and os.path.getsize(self.legacy_filepath) > 0:
            try:
                with open(self.legacy_filepath, "r", encoding="utf-8") as f:
                    legacy_data = json.load(f)

                categories = {}
                for ck, cv in legacy_data.get("categories", {}).items():
                    categories[ck] = CategoryStats(
                        total_attempts=cv.get("total_attempts", 0),
                        correct_count=cv.get("correct_count", 0),
                        current_streak=cv.get("current_streak", 0),
                        best_streak=cv.get("best_streak", 0),
                    )
                history = [
                    ExerciseRecord(
                        timestamp=h.get("timestamp", 0.0),
                        category=h.get("category", "treino_auditivo"),
                        question_type=h.get("question_type", "unknown"),
                        is_correct=h.get("is_correct", False),
                        prompt=h.get("prompt", ""),
                        user_answer=h.get("user_answer", ""),
                        correct_answer=h.get("correct_answer", ""),
                    )
                    for h in legacy_data.get("history", [])
                ]
                default_profile = UserProfile(
                    username="Utilizador 1",
                    avatar="🎵",
                    categories=categories,
                    completed_lessons=[],
                    history=history,
                )
                self.profiles["Utilizador 1"] = default_profile
                self.active_username = "Utilizador 1"
                self.save()
            except Exception as e:
                print(f"[UserManager] Erro na migração legacy: {e}")
