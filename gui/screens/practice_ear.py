"""Interactive Ear Training practice screen for musical intervals and chord qualities."""
from typing import Callable, List, Optional
import customtkinter as ctk
from core.quiz_engine import QuizEngine, QuizQuestion, QuestionType
from core.user_manager import UserManager
from audio.player import get_audio_player
from gui.components.score_card import ScoreCard


class PracticeEarScreen(ctk.CTkFrame):
    """
    Ear training workout room. Synthesizes intervals or chords and evaluates user guesses
    with instant acoustic feedback, mnemonics, and streak tracking.
    """

    def __init__(
        self,
        master,
        user_manager: UserManager,
        on_back: Callable[[], None],
        **kwargs,
    ):
        super().__init__(master, fg_color=("#F8FAFC", "#0F172A"), **kwargs)
        self.user_manager = user_manager
        self.on_back = on_back
        self.audio_player = get_audio_player()

        self.current_question: Optional[QuizQuestion] = None
        self.option_buttons: List[ctk.CTkButton] = []
        self.is_answered = False

        self._build_ui()
        self.load_new_question()

    def _build_ui(self):
        # Top Navigation Bar
        nav_bar = ctk.CTkFrame(self, fg_color="transparent")
        nav_bar.pack(fill="x", padx=20, pady=(16, 8))

        back_btn = ctk.CTkButton(
            nav_bar,
            text="← Voltar ao Menu",
            font=ctk.CTkFont(family="Helvetica", size=13, weight="bold"),
            fg_color="#475569",
            hover_color="#334155",
            width=130,
            command=self.on_back,
        )
        back_btn.pack(side="left")

        title_lbl = ctk.CTkLabel(
            nav_bar,
            text="🎧 Treino Auditivo",
            font=ctk.CTkFont(family="Helvetica", size=24, weight="bold"),
            text_color=("#0F172A", "#F8FAFC"),
        )
        title_lbl.pack(side="left", padx=18)

        # Settings & Filter Header
        settings_frame = ctk.CTkFrame(
            self,
            corner_radius=10,
            fg_color=("#F8FAFC", "#1E293B"),
            border_width=1,
            border_color=("#E2E8F0", "#334155"),
        )
        settings_frame.pack(fill="x", padx=20, pady=(4, 12))

        ctk.CTkLabel(settings_frame, text="Tipo de Exercício:", font=ctk.CTkFont(family="Helvetica", size=12, weight="bold")).pack(side="left", padx=(14, 4), pady=10)

        self.type_select = ctk.CTkSegmentedButton(
            settings_frame,
            values=["Intervalos", "Acordes"],
            command=lambda v: self.load_new_question(),
            selected_color="#7C3AED",
            selected_hover_color="#6D28D9",
        )
        self.type_select.set("Intervalos")
        self.type_select.pack(side="left", padx=6, pady=10)

        ctk.CTkLabel(settings_frame, text="Dificuldade:", font=ctk.CTkFont(family="Helvetica", size=12, weight="bold")).pack(side="left", padx=(16, 4), pady=10)

        self.diff_select = ctk.CTkSegmentedButton(
            settings_frame,
            values=["Iniciante", "Intermédio", "Avançado"],
            command=lambda v: self.load_new_question(),
            selected_color="#2563EB",
            selected_hover_color="#1D4ED8",
        )
        self.diff_select.set("Iniciante")
        self.diff_select.pack(side="left", padx=6, pady=10)

        # Exercise Main Area
        self.main_container = ctk.CTkScrollableFrame(self, fg_color=("#F8FAFC", "#0F172A"))
        self.main_container.pack(fill="both", expand=True, padx=20, pady=(0, 10))

        # Audio playback controls card
        self.play_card = ctk.CTkFrame(
            self.main_container,
            corner_radius=14,
            fg_color=("#F8FAFC", "#1E293B"),
            border_width=1,
            border_color=("#E2E8F0", "#334155"),
        )
        self.play_card.pack(fill="x", pady=(0, 12))

        self.prompt_label = ctk.CTkLabel(
            self.play_card,
            text="",
            font=ctk.CTkFont(family="Helvetica", size=17, weight="bold"),
            text_color=("#0F172A", "#F8FAFC"),
            wraplength=600,
        )
        self.prompt_label.pack(pady=(16, 12))

        # Audio Action Buttons
        audio_btn_box = ctk.CTkFrame(self.play_card, fg_color="transparent")
        audio_btn_box.pack(pady=(0, 16))

        self.play_btn = ctk.CTkButton(
            audio_btn_box,
            text="🔊 Tocar Áudio",
            font=ctk.CTkFont(family="Helvetica", size=14, weight="bold"),
            fg_color="#7C3AED",
            hover_color="#6D28D9",
            height=40,
            width=150,
            command=self._play_audio_normal,
        )
        self.play_btn.pack(side="left", padx=8)

        self.play_slow_btn = ctk.CTkButton(
            audio_btn_box,
            text="🐢 Tocar Lento",
            font=ctk.CTkFont(family="Helvetica", size=14, weight="bold"),
            fg_color="#475569",
            hover_color="#334155",
            height=40,
            width=140,
            command=self._play_audio_slow,
        )
        self.play_slow_btn.pack(side="left", padx=8)

        # Options Container (2x2 Grid)
        self.options_grid = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.options_grid.pack(fill="x", pady=6)
        self.options_grid.grid_columnconfigure((0, 1), weight=1, uniform="opts")

        for i in range(4):
            btn = ctk.CTkButton(
                self.options_grid,
                text="",
                font=ctk.CTkFont(family="Helvetica", size=14, weight="bold"),
                height=48,
                corner_radius=10,
                fg_color=("#E2E8F0", "#334155"),
                text_color=("#0F172A", "#F8FAFC"),
                hover_color=("#CBD5E1", "#475569"),
                command=lambda idx=i: self._handle_answer_selection(idx),
            )
            r, c = i // 2, i % 2
            btn.grid(row=r, column=c, padx=8, pady=8, sticky="nsew")
            self.option_buttons.append(btn)

        # Feedback ScoreCard
        self.feedback_card = ScoreCard(
            self.main_container,
            on_next=self.load_new_question,
            on_replay=self._play_audio_normal,
        )
        # Initially hidden

    def load_new_question(self):
        """Generates a fresh exercise based on the selected mode and difficulty."""
        self.is_answered = False
        self.feedback_card.pack_forget()

        # Map difficulty
        diff_pt = self.diff_select.get()
        diff_key = "beginner" if diff_pt == "Iniciante" else ("intermediate" if diff_pt == "Intermédio" else "advanced")

        # Generate question
        if self.type_select.get() == "Intervalos":
            self.current_question = QuizEngine.generate_ear_interval_question(difficulty=diff_key)
        else:
            self.current_question = QuizEngine.generate_ear_chord_question(difficulty=diff_key)

        self.prompt_label.configure(text=self.current_question.prompt_text)

        for i, opt_text in enumerate(self.current_question.options):
            btn = self.option_buttons[i]
            btn.configure(
                text=opt_text,
                fg_color=("#E2E8F0", "#334155"),
                text_color=("#0F172A", "#F8FAFC"),
                hover_color=("#CBD5E1", "#475569"),
                state="normal",
            )

        # Auto-play audio when loading question
        self.after(200, self._play_audio_normal)

    def _play_audio_normal(self):
        if not self.winfo_exists():
            return
        if self.current_question:
            self.audio_player.play_question(self.current_question, slow_mode=False)

    def _play_audio_slow(self):
        if not self.winfo_exists():
            return
        if self.current_question:
            self.audio_player.play_question(self.current_question, slow_mode=True)

    def _handle_answer_selection(self, selected_index: int):
        if self.is_answered or not self.current_question:
            return

        self.is_answered = True
        correct_index = self.current_question.correct_index
        is_correct = selected_index == correct_index

        # Update button colors
        for i, btn in enumerate(self.option_buttons):
            if i == correct_index:
                btn.configure(fg_color="#059669", text_color="#FFFFFF")  # Green for correct
            elif i == selected_index and not is_correct:
                btn.configure(fg_color="#DC2626", text_color="#FFFFFF")  # Red for incorrect
            btn.configure(state="disabled")

        # Record in user manager
        stats = self.user_manager.record_attempt(
            category="treino_auditivo",
            question_type=self.current_question.question_type.value,
            is_correct=is_correct,
            prompt=self.current_question.prompt_text,
            user_answer=self.current_question.options[selected_index],
            correct_answer=self.current_question.correct_answer,
        )

        # Show feedback card
        self.feedback_card.show_feedback(
            is_correct=is_correct,
            explanation=self.current_question.explanation,
            stats=stats,
            can_replay=True,
        )
        self.feedback_card.pack(fill="x", pady=(12, 10))
