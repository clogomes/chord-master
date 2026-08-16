from gui.i18n import t
from typing import Callable, Optional
import customtkinter as ctk
from core.theory_quiz import ChapterQuiz, QuizQuestion
from core.user_manager import UserManager
from gui import theme
from gui.components.score_card import ScoreCard


class TheoryQuizWidget(ctk.CTkFrame):
    """
    An interactive multiple-choice quiz widget for theory chapters.
    Presents 5 questions one by one, shows instant feedback, and computes the final score.
    """

    def __init__(
        self,
        master,
        chapter_quiz: ChapterQuiz,
        on_complete: Callable[[int, int], None],
        user_manager: Optional[UserManager] = None,
        **kwargs,
    ):
        super().__init__(
            master,
            corner_radius=theme.RADIUS_LG,
            fg_color=theme.COLOR_SURFACE,
            border_width=1,
            border_color=theme.COLOR_BORDER,
            **kwargs,
        )
        self.chapter_quiz = chapter_quiz
        self.on_complete = on_complete
        self.user_manager = user_manager
        
        self.current_q_idx = 0
        self.correct_count = 0
        self.selected_option_idx = ctk.IntVar(value=-1)
        self.is_answered = False

        self._build_ui()
        self._load_question(self.current_q_idx)

    def _build_ui(self):
        # Header
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(fill="x", padx=20, pady=(20, 10))

        self.title_lbl = ctk.CTkLabel(
            self.header_frame,
            text=f"📝 Quiz — {self.chapter_quiz.chapter_id}",
            font=theme.get_font(theme.FONT_SECTION),
            text_color=theme.COLOR_TEXT_PRIMARY,
        )
        self.title_lbl.pack(side="left")

        self.counter_lbl = ctk.CTkLabel(
            self.header_frame,
            text="Pergunta 1/5",
            font=theme.get_font(theme.FONT_BODY_BOLD),
            text_color=theme.COLOR_PRIMARY,
        )
        self.counter_lbl.pack(side="right")

        # Question Text
        self.question_lbl = ctk.CTkLabel(
            self,
            text="",
            font=theme.get_font(theme.FONT_TITLE),
            text_color=theme.COLOR_TEXT_PRIMARY,
            wraplength=600,
            justify="left",
        )
        self.question_lbl.pack(fill="x", padx=20, pady=(10, 20))

        # Options Frame
        self.options_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.options_frame.pack(fill="x", padx=20, pady=(0, 20))

        self.option_radios = []
        for i in range(4):
            rb = ctk.CTkRadioButton(
                self.options_frame,
                text=f"Opção {i+1}",
                variable=self.selected_option_idx,
                value=i,
                font=theme.get_font(theme.FONT_BODY),
                text_color=theme.COLOR_TEXT_PRIMARY,
                hover_color=theme.COLOR_PRIMARY,
                fg_color=theme.COLOR_PRIMARY,
                command=self._on_option_selected,
            )
            rb.pack(fill="x", pady=8, padx=10)
            self.option_radios.append(rb)

        # Feedback/Score Card
        self.score_card = ScoreCard(
            self,
            on_next=self._on_next_clicked,
            on_replay=None
        )

        # Actions
        self.actions_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.actions_frame.pack(fill="x", padx=20, pady=(0, 20))

        self.confirm_btn = ctk.CTkButton(
            self.actions_frame,
            text="Confirmar",
            font=theme.get_font(theme.FONT_BODY_BOLD),
            fg_color=theme.COLOR_PRIMARY,
            hover_color=theme.COLOR_PRIMARY_HOVER,
            command=self._on_confirm_clicked,
            state="disabled"
        )
        self.confirm_btn.pack(side="right", padx=10)

        # Results Screen
        self.results_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.results_score_lbl = ctk.CTkLabel(
            self.results_frame,
            text="",
            font=theme.get_font(theme.FONT_TITLE),
            text_color=theme.COLOR_TEXT_PRIMARY,
        )
        self.results_score_lbl.pack(pady=20)
        
        self.results_xp_lbl = ctk.CTkLabel(
            self.results_frame,
            text="",
            font=theme.get_font(theme.FONT_BODY_BOLD),
            text_color=theme.COLOR_SUCCESS,
        )
        self.results_xp_lbl.pack(pady=10)

        self.finish_btn = ctk.CTkButton(
            self.results_frame,
            text="Terminar Quiz",
            font=theme.get_font(theme.FONT_BODY_BOLD),
            fg_color=theme.COLOR_SUCCESS,
            hover_color=theme.COLOR_SUCCESS_HOVER,
            command=self._on_finish_clicked,
        )
        self.finish_btn.pack(pady=20)

    def _load_question(self, idx: int):
        self.is_answered = False
        self.selected_option_idx.set(-1)
        self.score_card.pack_forget()
        self.confirm_btn.configure(state="disabled")
        
        for rb in self.option_radios:
            rb.configure(state="normal", text_color=theme.COLOR_TEXT_PRIMARY)

        q = self.chapter_quiz.questions[idx]
        total = len(self.chapter_quiz.questions)
        lang = get_language()

        self.title_lbl.configure(text=f"📝 {t('quiz_title', 'Quiz — Capítulo')} {idx + 1}/{total}")
        self.question_lbl.configure(text=q.get_question(lang) if hasattr(q, "get_question") else (q.question_en if lang == "en" and getattr(q, "question_en", None) else q.question))

        self.confirm_btn.configure(text=t("quiz_confirm", "Confirmar"))
        
        for i, rb in enumerate(self.option_radios):
            opt_text = q.options_en[i] if lang == "en" and getattr(q, "options_en", None) else q.options[i]
            rb.configure(text=opt_text)

    def _on_option_selected(self):
        if not self.is_answered:
            self.confirm_btn.configure(state="normal")

    def _on_confirm_clicked(self):
        if self.is_answered:
            return

        self.is_answered = True
        self.confirm_btn.configure(state="disabled")

        selected = self.selected_option_idx.get()
        q = self.chapter_quiz.questions[self.current_q_idx]
        is_correct = (selected == q.correct_index)
        lang = get_language()

        if is_correct:
            self.correct_count += 1
            if self.user_manager and self.user_manager.current_user:
                self.user_manager.current_user.xp += 10
                self.user_manager._save_users()

        for i, rb in enumerate(self.option_radios):
            rb.configure(state="disabled")
            if i == q.correct_index:
                rb.configure(text_color=theme.COLOR_SUCCESS)
            elif i == selected and not is_correct:
                rb.configure(text_color=theme.COLOR_ACCENT_CRIMSON)

        expl = q.get_explanation(lang) if hasattr(q, "get_explanation") else (q.explanation_en if lang == "en" and getattr(q, "explanation_en", None) else q.explanation)

        self.score_card.show_feedback(
            is_correct=is_correct,
            explanation=expl,
            can_replay=False
        )
        self.score_card.pack(fill="x", padx=20, pady=(10, 20), before=self.actions_frame)

    def _on_next_clicked(self):
        self.current_q_idx += 1
        if self.current_q_idx < len(self.chapter_quiz.questions):
            self._load_question(self.current_q_idx)
        else:
            self._show_results()

    def _show_results(self):
        self.header_frame.pack_forget()
        self.question_lbl.pack_forget()
        self.options_frame.pack_forget()
        self.actions_frame.pack_forget()
        self.score_card.pack_forget()

        total = len(self.chapter_quiz.questions)
        self.results_score_lbl.configure(text=f"Resultado: {self.correct_count} / {total}")
        
        xp_earned = self.correct_count * 10
        if self.user_manager and self.user_manager.current_user:
            self.results_xp_lbl.configure(text=f"+{xp_earned} XP Ganhos!")
            # Also check for achievements here maybe, but simple is fine.
        
        self.results_frame.pack(fill="both", expand=True, padx=20, pady=20)

    def _on_finish_clicked(self):
        if self.on_complete:
            self.on_complete(self.correct_count, len(self.chapter_quiz.questions))
