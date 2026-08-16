"""
Daily Spaced Repetition Review Screen — "🔄 Revisão de Hoje"

Serves atomic musical skills that are due today using the SM-2 / Leitner
system. Supports ear interval audio, staff note images and theory/glossary
multiple-choice questions with instant feedback grading.
"""
from __future__ import annotations

import time
from typing import List, Optional, Callable

import customtkinter as ctk

from core.review_scheduler import (
    ReviewItem,
    apply_sm2_grade,
    generate_default_atomic_skills,
    get_due_review_queue,
)
from core.user_manager import UserManager
from gui import theme
from gui.i18n import t

_XP_PER_ITEM = 15


class LeitnerBoxWidget(ctk.CTkFrame):
    """Small horizontal bar showing item distribution across Leitner boxes."""

    BOX_LABELS = ["1\nNovo", "2\nAprender", "3\nConsol.", "4\nRetido", "5\nDom."]
    BOX_COLORS = ["#EF4444", "#F59E0B", "#3B82F6", "#10B981", "#8B5CF6"]

    def __init__(self, master, box_counts: dict, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.columnconfigure(list(range(5)), weight=1, uniform="box")
        for i in range(5):
            count = box_counts.get(i + 1, 0)
            col_frame = ctk.CTkFrame(self, fg_color=self.BOX_COLORS[i], corner_radius=theme.RADIUS_SM)
            col_frame.grid(row=0, column=i, padx=3, sticky="ew")
            ctk.CTkLabel(
                col_frame,
                text=f"{count}",
                font=theme.get_font(theme.FONT_BADGE),
                text_color="#FFFFFF",
            ).pack(pady=(6, 2))
            ctk.CTkLabel(
                col_frame,
                text=self.BOX_LABELS[i],
                font=theme.get_font(theme.FONT_SMALL),
                text_color="#FFFFFF",
                justify="center",
            ).pack(pady=(0, 6))


class DailyReviewScreen(ctk.CTkScrollableFrame):
    """
    Full-page spaced repetition review session.

    Loads up to 15 due atomic skills and presents them one at a time.
    After grading, the result is saved to UserProfile.spaced_review_data
    and the user earns +15 XP per correct-graded item (grade >= 4).
    """

    def __init__(
        self,
        master,
        user_manager: UserManager,
        on_back: Callable[[], None],
        **kwargs,
    ):
        super().__init__(
            master,
            fg_color=theme.COLOR_BG,
            scrollbar_button_color=theme.COLOR_SURFACE_SECONDARY,
            scrollbar_button_hover_color=theme.COLOR_PRIMARY,
            **kwargs,
        )
        self.user_manager = user_manager
        self.on_back = on_back

        self._queue: List[ReviewItem] = []
        self._current_idx: int = 0
        self._session_correct: int = 0
        self._session_total: int = 0
        self._item_answered: bool = False

        self._build_header()
        self._build_leitner_bar()
        self._build_question_card()
        self._build_grade_buttons()
        self._build_next_btn()
        self._build_completion_card()

        self._start_session()

    # ─── Build UI ────────────────────────────────────────────────────────────

    def _build_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(20, 8))
        header.columnconfigure(1, weight=1)

        back_btn = ctk.CTkButton(
            header,
            text="← Voltar",
            font=theme.get_font(theme.FONT_BODY),
            fg_color=theme.COLOR_SURFACE_SECONDARY,
            hover_color=theme.COLOR_SURFACE_HOVER,
            text_color=theme.COLOR_TEXT_MUTED,
            width=90,
            height=34,
            corner_radius=theme.RADIUS_MD,
            command=self.on_back,
        )
        back_btn.grid(row=0, column=0, sticky="w")

        self.title_lbl = ctk.CTkLabel(
            header,
            text="🔄 Revisão de Hoje",
            font=theme.get_font(theme.FONT_TITLE),
            text_color=theme.COLOR_TEXT_PRIMARY,
        )
        self.title_lbl.grid(row=0, column=1, sticky="ew")

        self.progress_lbl = ctk.CTkLabel(
            header,
            text="",
            font=theme.get_font(theme.FONT_SMALL),
            text_color=theme.COLOR_TEXT_MUTED,
        )
        self.progress_lbl.grid(row=1, column=0, columnspan=3, sticky="w", pady=(4, 0))

    def _build_leitner_bar(self):
        self.leitner_container = ctk.CTkFrame(
            self,
            fg_color=theme.COLOR_SURFACE,
            corner_radius=theme.RADIUS_LG,
            border_width=1,
            border_color=theme.COLOR_BORDER,
        )
        self.leitner_container.pack(fill="x", padx=20, pady=(0, 12))
        ctk.CTkLabel(
            self.leitner_container,
            text="Distribuição de Caixas Leitner",
            font=theme.get_font(theme.FONT_SMALL),
            text_color=theme.COLOR_TEXT_MUTED,
        ).pack(pady=(10, 6), padx=14, anchor="w")
        self.leitner_widget_holder = ctk.CTkFrame(self.leitner_container, fg_color="transparent")
        self.leitner_widget_holder.pack(fill="x", padx=14, pady=(0, 10))

    def _build_question_card(self):
        self.question_card = ctk.CTkFrame(
            self,
            fg_color=theme.COLOR_SURFACE,
            corner_radius=theme.RADIUS_LG,
            border_width=1,
            border_color=theme.COLOR_BORDER,
        )
        self.question_card.pack(fill="x", padx=20, pady=(0, 12))

        self.category_lbl = ctk.CTkLabel(
            self.question_card,
            text="",
            font=theme.get_font(theme.FONT_SMALL),
            text_color=theme.COLOR_TEXT_MUTED,
        )
        self.category_lbl.pack(pady=(14, 4), padx=20, anchor="w")

        self.prompt_lbl = ctk.CTkLabel(
            self.question_card,
            text="",
            font=theme.get_font(theme.FONT_SECTION),
            text_color=theme.COLOR_TEXT_PRIMARY,
            wraplength=620,
            justify="center",
        )
        self.prompt_lbl.pack(pady=(4, 12), padx=20)

        # Audio play button (shown for ear intervals)
        self.play_btn = ctk.CTkButton(
            self.question_card,
            text="🔊 Ouvir",
            font=theme.get_font(theme.FONT_BODY_BOLD),
            fg_color=theme.COLOR_PRIMARY,
            hover_color=theme.COLOR_PRIMARY_HOVER,
            corner_radius=theme.RADIUS_MD,
            height=38,
            command=self._play_audio,
        )

        # MCQ Options area (shown for theory/glossary)
        self.options_frame = ctk.CTkFrame(self.question_card, fg_color="transparent")
        self.option_buttons: list = []

        # Explanation area (revealed after grading)
        self.explanation_lbl = ctk.CTkLabel(
            self.question_card,
            text="",
            font=theme.get_font(theme.FONT_BODY),
            text_color=theme.COLOR_TEXT_MUTED,
            wraplength=620,
            justify="left",
        )

    def _build_grade_buttons(self):
        self.grade_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.grade_frame.pack(fill="x", padx=20, pady=(0, 10))
        self.grade_frame.columnconfigure([0, 1, 2, 3], weight=1, uniform="grade")

        grade_specs = [
            ("❌ Errei", 1, theme.COLOR_ACCENT_CRIMSON, theme.COLOR_ACCENT_CRIMSON_HOVER),
            ("🟡 Difícil", 3, theme.COLOR_ACCENT_AMBER, "#D97706"),
            ("🟢 Bom", 4, theme.COLOR_SUCCESS, theme.COLOR_SUCCESS_HOVER),
            ("🌟 Fácil", 5, theme.COLOR_PRIMARY, theme.COLOR_PRIMARY_HOVER),
        ]

        self.grade_buttons: list = []
        for col, (label, grade, fg, hover) in enumerate(grade_specs):
            btn = ctk.CTkButton(
                self.grade_frame,
                text=label,
                font=theme.get_font(theme.FONT_BODY_BOLD),
                fg_color=fg,
                hover_color=hover,
                corner_radius=theme.RADIUS_MD,
                height=44,
                state="disabled",
                command=lambda g=grade: self._on_grade(g),
            )
            btn.grid(row=0, column=col, padx=4, sticky="ew")
            self.grade_buttons.append(btn)

    def _build_next_btn(self):
        self.next_btn = ctk.CTkButton(
            self,
            text="Próxima →",
            font=theme.get_font(theme.FONT_BODY_BOLD),
            fg_color=theme.COLOR_SURFACE_SECONDARY,
            hover_color=theme.COLOR_SURFACE_HOVER,
            text_color=theme.COLOR_TEXT_PRIMARY,
            corner_radius=theme.RADIUS_MD,
            height=42,
            state="disabled",
            command=self._advance,
        )
        self.next_btn.pack(fill="x", padx=20, pady=(0, 20))

    def _build_completion_card(self):
        self.completion_card = ctk.CTkFrame(
            self,
            fg_color=theme.COLOR_SURFACE,
            corner_radius=theme.RADIUS_LG,
            border_width=1,
            border_color=theme.COLOR_BORDER,
        )
        ctk.CTkLabel(
            self.completion_card,
            text="✅ Sessão Completa!",
            font=theme.get_font(theme.FONT_TITLE),
            text_color=theme.COLOR_SUCCESS,
        ).pack(pady=(20, 8))
        self.summary_lbl = ctk.CTkLabel(
            self.completion_card,
            text="",
            font=theme.get_font(theme.FONT_BODY),
            text_color=theme.COLOR_TEXT_PRIMARY,
        )
        self.summary_lbl.pack(pady=(0, 8))
        self.xp_lbl = ctk.CTkLabel(
            self.completion_card,
            text="",
            font=theme.get_font(theme.FONT_SUBTITLE),
            text_color=theme.COLOR_ACCENT_AMBER,
        )
        self.xp_lbl.pack(pady=(0, 20))
        ctk.CTkButton(
            self.completion_card,
            text="← Voltar ao Menu",
            font=theme.get_font(theme.FONT_BODY_BOLD),
            fg_color=theme.COLOR_PRIMARY,
            hover_color=theme.COLOR_PRIMARY_HOVER,
            corner_radius=theme.RADIUS_MD,
            height=40,
            command=self.on_back,
        ).pack(pady=(0, 20))

    # ─── Session Logic ────────────────────────────────────────────────────────

    def _start_session(self):
        user = self.user_manager.current_user
        if not user:
            self._show_empty("Nenhum utilizador ativo.")
            return

        # Seed default skills if profile is fresh
        if not user.spaced_review_data:
            defaults = generate_default_atomic_skills()
            for item in defaults:
                user.spaced_review_data[item.skill_id] = item.to_dict()
            self.user_manager.save()

        self._queue = self.user_manager.get_daily_review_queue(max_items=15)

        if not self._queue:
            self._show_empty("Nenhum item por rever hoje! Volta amanhã 🎉")
            return

        self._session_total = len(self._queue)
        self._update_leitner_bar()
        self._load_item(0)

    def _update_leitner_bar(self):
        for w in self.leitner_widget_holder.winfo_children():
            w.destroy()
        user = self.user_manager.current_user
        if user:
            lw = LeitnerBoxWidget(self.leitner_widget_holder, user.leitner_box_counts)
            lw.pack(fill="x")

    def _load_item(self, idx: int):
        if idx >= len(self._queue):
            self._show_completion()
            return

        self._current_idx = idx
        self._item_answered = False
        item = self._queue[idx]

        # Progress
        self.progress_lbl.configure(
            text=f"Item {idx + 1} de {self._session_total}  •  Caixa Leitner {item.box}"
        )

        # Category chip
        cat_map = {
            "ear": "🎧 Treino Auditivo",
            "staff": "📖 Leitura de Pauta",
            "theory": "📝 Teoria",
            "glossary": "📚 Glossário",
        }
        cat_prefix = cat_map.get(item.category, item.category)
        self.category_lbl.configure(text=cat_prefix)

        # Prompt
        self.prompt_lbl.configure(text=item.prompt_pt)

        # Clear explanation
        self.explanation_lbl.pack_forget()
        self.explanation_lbl.configure(text="")

        # Show/hide audio button
        if item.audio_notes:
            self.play_btn.pack(pady=(0, 14))
        else:
            self.play_btn.pack_forget()

        # Build MCQ options
        for b in self.option_buttons:
            b.destroy()
        self.option_buttons.clear()
        self.options_frame.pack_forget()

        if item.options_pt:
            self.options_frame.pack(fill="x", padx=20, pady=(0, 12))
            self.options_frame.columnconfigure([0, 1], weight=1, uniform="opt")
            for i, opt_text in enumerate(item.options_pt):
                r = i // 2
                c = i % 2
                btn = ctk.CTkButton(
                    self.options_frame,
                    text=opt_text,
                    font=theme.get_font(theme.FONT_BODY),
                    fg_color=theme.COLOR_SURFACE_SECONDARY,
                    hover_color=theme.COLOR_SURFACE_HOVER,
                    text_color=theme.COLOR_TEXT_PRIMARY,
                    corner_radius=theme.RADIUS_MD,
                    height=44,
                    command=lambda ix=i: self._select_mcq_option(ix),
                )
                btn.grid(row=r, column=c, padx=4, pady=4, sticky="ew")
                self.option_buttons.append(btn)

        # Disable grade & next until answered
        for gb in self.grade_buttons:
            gb.configure(state="disabled")
        self.next_btn.configure(state="disabled")

        # For ear items without MCQ — show grade buttons immediately after audio
        if not item.options_pt and not item.audio_notes:
            self._reveal_grade_buttons()

    def _select_mcq_option(self, chosen_idx: int):
        if self._item_answered:
            return
        item = self._queue[self._current_idx]
        is_correct = (chosen_idx == item.correct_index)

        for i, btn in enumerate(self.option_buttons):
            btn.configure(state="disabled")
            if i == item.correct_index:
                btn.configure(fg_color=theme.COLOR_SUCCESS, text_color="#FFFFFF")
            elif i == chosen_idx and not is_correct:
                btn.configure(fg_color=theme.COLOR_ACCENT_CRIMSON, text_color="#FFFFFF")

        self._show_explanation(item)
        self._reveal_grade_buttons(auto_grade=5 if is_correct else 1)

    def _reveal_grade_buttons(self, auto_grade: Optional[int] = None):
        if auto_grade is not None:
            self._on_grade(auto_grade)
        else:
            for gb in self.grade_buttons:
                gb.configure(state="normal")

    def _show_explanation(self, item: ReviewItem):
        if item.explanation_pt:
            self.explanation_lbl.configure(text=f"💡 {item.explanation_pt}")
            self.explanation_lbl.pack(pady=(0, 14), padx=20, anchor="w")

    def _play_audio(self):
        item = self._queue[self._current_idx]
        if not item.audio_notes:
            return
        try:
            from core.audio_player import AudioPlayer
            from core.notes import Note
            player = AudioPlayer()
            notes = [Note.from_pitch(p) for p in item.audio_notes if p]
            player.play_notes_melodic(notes, duration=0.5)
        except Exception as e:
            print(f"[DailyReview] Audio error: {e}")

        # After playing, reveal grade buttons for ear items
        if not self.option_buttons and not self._item_answered:
            self._show_explanation(self._queue[self._current_idx])
            self._reveal_grade_buttons()

    def _on_grade(self, grade: int):
        if self._item_answered:
            return
        self._item_answered = True

        item = self._queue[self._current_idx]
        apply_sm2_grade(item, grade=grade)

        user = self.user_manager.current_user
        if user:
            user.spaced_review_data[item.skill_id] = item.to_dict()
            if grade >= 4:
                self._session_correct += 1
                user.xp += _XP_PER_ITEM
            self.user_manager.save()

        # Disable grade buttons
        for gb in self.grade_buttons:
            gb.configure(state="disabled")

        self.next_btn.configure(state="normal")
        self._update_leitner_bar()

    def _advance(self):
        self._load_item(self._current_idx + 1)

    def _show_completion(self):
        self.question_card.pack_forget()
        self.grade_frame.pack_forget()
        self.next_btn.pack_forget()
        self.leitner_container.pack_forget()

        xp_earned = self._session_correct * _XP_PER_ITEM
        self.summary_lbl.configure(
            text=f"Itens bem dominados: {self._session_correct} / {self._session_total}"
        )
        self.xp_lbl.configure(text=f"+{xp_earned} XP ganhos! 🎉")
        self.completion_card.pack(fill="x", padx=20, pady=20)

    def _show_empty(self, message: str):
        self.question_card.pack_forget()
        self.grade_frame.pack_forget()
        self.next_btn.pack_forget()

        ctk.CTkLabel(
            self,
            text=message,
            font=theme.get_font(theme.FONT_SUBTITLE),
            text_color=theme.COLOR_TEXT_MUTED,
        ).pack(pady=40)

        ctk.CTkButton(
            self,
            text="← Voltar",
            font=theme.get_font(theme.FONT_BODY_BOLD),
            fg_color=theme.COLOR_PRIMARY,
            hover_color=theme.COLOR_PRIMARY_HOVER,
            corner_radius=theme.RADIUS_MD,
            height=40,
            command=self.on_back,
        ).pack()
