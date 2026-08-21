from gui.i18n import t
"""Modern visual feedback card for quiz answers, streaks, and explanations."""
from typing import Callable, Optional
import customtkinter as ctk
from core.user_manager import CategoryStats


class ScoreCard(ctk.CTkFrame):
    """
    Feedback card shown after a user submits an answer.
    Displays success/error badges, streak indicators, and detailed explanation text.
    """

    def __init__(
        self,
        master,
        on_next: Optional[Callable[[], None]] = None,
        on_replay: Optional[Callable[[], None]] = None,
        **kwargs,
    ):
        super().__init__(
            master,
            corner_radius=12,
            fg_color=("#F1F5F9", "#1E293B"),
            border_width=1,
            border_color=("#CBD5E1", "#334155"),
            **kwargs,
        )
        self.on_next = on_next
        self.on_replay = on_replay

        # Badge container
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(fill="x", padx=16, pady=(14, 6))

        self.badge_label = ctk.CTkLabel(
            self.header_frame,
            text="",
            font=ctk.CTkFont(family="Helvetica", size=18, weight="bold"),
        )
        self.badge_label.pack(side="left")

        self.streak_label = ctk.CTkLabel(
            self.header_frame,
            text="",
            font=ctk.CTkFont(family="Helvetica", size=14, weight="bold"),
            text_color="#F59E0B",  # Amber flame color
        )
        self.streak_label.pack(side="right")

        # Explanation box
        self.explanation_box = ctk.CTkTextbox(
            self,
            height=90,
            corner_radius=8,
            fg_color=("#E2E8F0", "#0F172A"),
            text_color=("#0F172A", "#F8FAFC"),
            font=ctk.CTkFont(family="Helvetica", size=13),
            wrap="word",
        )
        self.explanation_box.pack(fill="x", padx=16, pady=(4, 12))

        # Action buttons
        self.btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.btn_frame.pack(fill="x", padx=16, pady=(0, 14))

        self.replay_btn = ctk.CTkButton(
            self.btn_frame,
            text="🔊 Ouvir Novamente",
            font=ctk.CTkFont(family="Helvetica", size=13, weight="bold"),
            fg_color="#475569",
            hover_color="#334155",
            command=self._handle_replay,
        )
        self.replay_btn.pack(side="left", expand=True, fill="x", padx=(0, 6))

        self.next_btn = ctk.CTkButton(
            self.btn_frame,
            text="Próximo Exercício →",
            font=ctk.CTkFont(family="Helvetica", size=13, weight="bold"),
            fg_color="#2563EB",
            hover_color="#1D4ED8",
            command=self._handle_next,
        )
        self.next_btn.pack(side="right", expand=True, fill="x", padx=(6, 0))

    def show_feedback(
        self,
        is_correct: bool,
        explanation: str,
        stats: Optional[CategoryStats] = None,
        can_replay: bool = True,
    ):
        """Updates and formats the card according to the user's answer result."""
        if is_correct:
            self.badge_label.configure(
                text="✨ Excelente! Resposta Correta",
                text_color="#10B981",  # Emerald
            )
            self.configure(border_color="#059669")
        else:
            self.badge_label.configure(
                text="❌ Resposta Incorreta",
                text_color="#EF4444",  # Rose/Red
            )
            self.configure(border_color="#DC2626")

        if stats:
            streak_text = f"🔥 Sequência: {stats.current_streak} (Recorde: {stats.best_streak})"
            self.streak_label.configure(text=streak_text)
        else:
            self.streak_label.configure(text="")

        self.explanation_box.configure(state="normal")
        self.explanation_box.delete("0.0", "end")
        self.explanation_box.insert("0.0", explanation)
        self.explanation_box.configure(state="disabled")

        if can_replay:
            self.replay_btn.pack(side="left", expand=True, fill="x", padx=(0, 6))
        else:
            self.replay_btn.pack_forget()

    def _handle_replay(self):
        if self.on_replay:
            self.on_replay()

    def _handle_next(self):
        if self.on_next:
            self.on_next()
