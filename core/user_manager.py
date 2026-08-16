"""Multi-user management, progress persistence, level XP, and achievement tracking."""
from dataclasses import dataclass, field, asdict
import json
import os
import time
from typing import Dict, List, Optional, Tuple
from core.gamification import (
    Achievement,
    ACHIEVEMENT_LIBRARY,
    get_level_info,
    get_achievement_by_id,
)

from core.theory_content import THEORY_CHAPTERS
LESSON_IDS = [(c.id, c.title) for c in THEORY_CHAPTERS]

AVATAR_CHOICES = [
    "🎵", "🎹", "🎸", "🎼", "🎻", "🎺", "🎷", "🥁", "🎧", "🌟", "⚡", "🔥"
]


@dataclass
class CategoryStats:
    total_attempts: int = 0
    correct_count: int = 0
    current_streak: int = 0
    best_streak: int = 0


@dataclass
class ExerciseRecord:
    timestamp: float
    category: str
    question_type: str
    is_correct: bool
    prompt: str
    user_answer: str
    correct_answer: str


@dataclass
class UserProfile:
    """Represents a single student profile with independent stats, XP, level, and achievements."""
    username: str
    avatar: str = "🎵"
    created_at: float = field(default_factory=time.time)
    xp: int = 0
    unlocked_achievements: List[str] = field(default_factory=list)
    categories: Dict[str, CategoryStats] = field(default_factory=lambda: {
        "treino_auditivo": CategoryStats(),
        "leitura_pauta": CategoryStats(),
        "teoria": CategoryStats(),
        "repertorio": CategoryStats(),
        "pratica_instrumento": CategoryStats(),
        "escalas_modos": CategoryStats(),
        "tecnica": CategoryStats(),
    })
    completed_lessons: List[str] = field(default_factory=list)
    history: List[ExerciseRecord] = field(default_factory=list)

    @property
    def level_info(self) -> Dict:
        return get_level_info(self.xp)

    @property
    def level(self) -> int:
        return self.level_info["level"]

    @property
    def level_title(self) -> str:
        return self.level_info["title"]

    @property
    def level_icon(self) -> str:
        return self.level_info["icon"]

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
        return (self.total_correct / float(self.total_attempts)) * 100.0

    @property
    def best_streak(self) -> int:
        return max((c.best_streak for c in self.categories.values()), default=0)

    @property
    def lessons_progress_percent(self) -> float:
        total_lessons = len(LESSON_IDS)
        if total_lessons == 0:
            return 0.0
        return (len(self.completed_lessons) / float(total_lessons)) * 100.0


class UserManager:
    """
    Manages multi-student profiles, gamification XP, level unlocks,
    and persistent storage in user_profiles.json.
    """

    def __init__(self, filepath: Optional[str] = None):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if filepath is None:
            self.filepath = os.path.join(base_dir, "user_profiles.json")
            self.legacy_filepath = os.path.join(base_dir, "user_scores.json")
        else:
            self.filepath = filepath
            self.legacy_filepath = ""

        self.profiles: Dict[str, UserProfile] = {}
        self.active_username: str = "Utilizador 1"
        self.load()

        if not self.profiles:
            self.create_user("Utilizador 1", avatar="🎵")
            self.active_username = "Utilizador 1"

    @property
    def current_user(self) -> UserProfile:
        if self.active_username not in self.profiles:
            if self.profiles:
                self.active_username = next(iter(self.profiles.keys()))
            else:
                self.create_user("Utilizador 1")
                self.active_username = "Utilizador 1"
        return self.profiles[self.active_username]

    def get_all_users(self) -> List[UserProfile]:
        return list(self.profiles.values())

    def create_user(self, username: str, avatar: str = "🎵") -> UserProfile:
        clean_name = username.strip()
        if not clean_name:
            clean_name = f"Utilizador {len(self.profiles) + 1}"

        base_name = clean_name
        counter = 2
        while clean_name in self.profiles:
            clean_name = f"{base_name} ({counter})"
            counter += 1

        profile = UserProfile(
            username=clean_name,
            avatar=avatar,
            created_at=time.time(),
            xp=0,
            unlocked_achievements=[],
        )
        self.profiles[clean_name] = profile
        self.active_username = clean_name
        self.save()
        return profile

    def switch_user(self, username: str) -> bool:
        if username in self.profiles:
            self.active_username = username
            self.save()
            return True
        return False

    def delete_user(self, username: str) -> bool:
        if username in self.profiles and len(self.profiles) > 1:
            del self.profiles[username]
            if self.active_username == username:
                self.active_username = next(iter(self.profiles.keys()))
            self.save()
            return True
        return False

    def add_xp(self, amount: int) -> Tuple[int, bool]:
        """Awards XP to current active user. Returns (new_xp, did_level_up)."""
        user = self.current_user
        old_level = user.level
        user.xp += max(0, amount)
        new_level = user.level
        self.check_achievements()
        self.save()
        return user.xp, (new_level > old_level)

    def check_achievements(self) -> List[Achievement]:
        """Evaluates achievement requirements for active user and unlocks any newly earned."""
        user = self.current_user
        newly_unlocked = []

        for ach in ACHIEVEMENT_LIBRARY:
            if ach.id in user.unlocked_achievements:
                continue

            unlocked = False

            if ach.id == "first_step" and len(user.completed_lessons) >= 1:
                unlocked = True
            elif ach.id == "theory_scholar" and len(user.completed_lessons) >= 4:
                unlocked = True
            elif ach.id == "theory_master" and len(user.completed_lessons) >= len(LESSON_IDS):
                unlocked = True
            elif ach.id == "first_melody" and user.categories.get("repertorio", CategoryStats()).correct_count >= 1:
                unlocked = True
            elif ach.id == "perfect_ear" and user.categories.get("treino_auditivo", CategoryStats()).best_streak >= 5:
                unlocked = True
            elif ach.id == "sight_reader" and user.categories.get("leitura_pauta", CategoryStats()).best_streak >= 10:
                unlocked = True
            elif ach.id == "streak_fire" and user.best_streak >= 10:
                unlocked = True
            elif ach.id == "diligent_student" and user.total_attempts >= 50:
                unlocked = True

            if unlocked:
                user.unlocked_achievements.append(ach.id)
                user.xp += ach.xp_reward
                newly_unlocked.append(ach)

        if newly_unlocked:
            self.save()

        return newly_unlocked

    def mark_lesson_completed(self, lesson_id: str) -> bool:
        user = self.current_user
        if lesson_id not in user.completed_lessons:
            user.completed_lessons.append(lesson_id)
            user.xp += 100  # +100 XP per completed lesson
            self.check_achievements()
            self.save()
            return True
        return False

    def is_lesson_completed(self, lesson_id: str) -> bool:
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
            # Award XP for correct answer (+15 XP + streak bonus)
            streak_bonus = min(20, stats.current_streak * 2)
            user.xp += (15 + streak_bonus)
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

        self.check_achievements()
        self.save()
        return stats

    def reset_current_user_scores(self):
        """Resets scores, XP, achievements and lesson progress for the active user."""
        user = self.current_user
        for cat in user.categories.keys():
            user.categories[cat] = CategoryStats()
        user.history.clear()
        user.completed_lessons.clear()
        user.xp = 0
        user.unlocked_achievements.clear()
        self.save()

    def save(self):
        data = {
            "active_user": self.active_username,
            "users": {}
        }
        for name, profile in self.profiles.items():
            data["users"][name] = {
                "username": profile.username,
                "avatar": profile.avatar,
                "created_at": profile.created_at,
                "xp": profile.xp,
                "unlocked_achievements": profile.unlocked_achievements,
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
        if os.path.exists(self.filepath) and os.path.getsize(self.filepath) > 0:
            try:
                with open(self.filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)

                self.active_username = data.get("active_user", "Utilizador 1")
                self.profiles.clear()

                for name, udata in data.get("users", {}).items():
                    categories = {
                        "treino_auditivo": CategoryStats(),
                        "leitura_pauta": CategoryStats(),
                        "teoria": CategoryStats(),
                        "repertorio": CategoryStats(),
                        "pratica_instrumento": CategoryStats(),
                        "escalas_modos": CategoryStats(),
                        "tecnica": CategoryStats(),
                    }
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
                        xp=udata.get("xp", 0),
                        unlocked_achievements=udata.get("unlocked_achievements", []),
                        categories=categories,
                        completed_lessons=udata.get("completed_lessons", []),
                        history=history,
                    )
                    self.profiles[profile.username] = profile
                return
            except Exception as e:
                print(f"[UserManager] Erro ao carregar {self.filepath}: {e}")
