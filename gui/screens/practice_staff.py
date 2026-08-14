"""Interactive Staff Reading practice screen for Treble and Bass clefs."""
from typing import Callable, List, Optional
import customtkinter as ctk
from core.quiz_engine import QuizEngine, QuizQuestion
from core.user_manager import UserManager
from audio.player import get_audio_player
from gui.components.staff_canvas import StaffCanvas
from gui.components.piano_keyboard import PianoKeyboard
from gui.components.score_card import ScoreCard


class PracticeStaffScreen(ctk.CTkFrame):
    """
    Sight-reading trainer on the musical staff with Treble (𝄞) and Bass (𝄢) clefs.
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
            text="🎼 Leitura de Pauta",
            font=ctk.CTkFont(family="Helvetica", size=24, weight="bold"),
            text_color=("#0F172A", "#F8FAFC"),
        )
        title_lbl.pack(side="left", padx=18)

        # Settings bar
        settings_frame = ctk.CTkFrame(
            self,
            corner_radius=10,
            fg_color=("#F8FAFC", "#1E293B"),
            border_width=1,
            border_color=("#E2E8F0", "#334155"),
        )
        settings_frame.pack(fill="x", padx=20, pady=(4, 12))

        ctk.CTkLabel(settings_frame, text="Clave:", font=ctk.CTkFont(family="Helvetica", size=12, weight="bold")).pack(side="left", padx=(14, 4), pady=10)

        self.clef_select = ctk.CTkSegmentedButton(
            settings_frame,
            values=["Clave de Sol (𝄞)", "Clave de Fá (𝄢)"],
            command=lambda v: self.load_new_question(),
            selected_color="#059669",
            selected_hover_color="#047857",
        )
        self.clef_select.set("Clave de Sol (𝄞)")
        self.clef_select.pack(side="left", padx=6, pady=10)

        self.accidentals_var = ctk.BooleanVar(value=False)
        self.accidentals_check = ctk.CTkCheckBox(
            settings_frame,
            text="Incluir Acidentes (♯/♭)",
            variable=self.accidentals_var,
            command=self.load_new_question,
            font=ctk.CTkFont(family="Helvetica", size=12),
        )
        self.accidentals_check.pack(side="left", padx=16, pady=10)

        # Main scroll container
        self.main_container = ctk.CTkScrollableFrame(self, fg_color=("#F8FAFC", "#0F172A"))
        self.main_container.pack(fill="both", expand=True, padx=20, pady=(0, 10))

        # Staff display container
        self.staff_card = ctk.CTkFrame(
            self.main_container,
            corner_radius=14,
            fg_color=("#F8FAFC", "#1E293B"),
            border_width=1,
            border_color=("#E2E8F0", "#334155"),
        )
        self.staff_card.pack(fill="x", pady=(0, 12))

        self.prompt_label = ctk.CTkLabel(
            self.staff_card,
            text="",
            font=ctk.CTkFont(family="Helvetica", size=16, weight="bold"),
            text_color=("#0F172A", "#F8FAFC"),
        )
        self.prompt_label.pack(pady=(12, 4))

        self.staff_view = StaffCanvas(self.staff_card, width=640, height=170, clef="treble", show_note_names=False)
        self.staff_view.pack(pady=4)

        play_btn = ctk.CTkButton(
            self.staff_card,
            text="🔊 Ouvir Som da Nota",
            font=ctk.CTkFont(family="Helvetica", size=12, weight="bold"),
            fg_color="#059669",
            hover_color="#047857",
            height=32,
            width=160,
            command=self._play_current_note,
        )
        play_btn.pack(pady=(4, 12))

        # Options Container (2x2 Grid)
        self.options_grid = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.options_grid.pack(fill="x", pady=6)
        self.options_grid.grid_columnconfigure((0, 1), weight=1, uniform="opts")

        for i in range(4):
            btn = ctk.CTkButton(
                self.options_grid,
                text="",
                font=ctk.CTkFont(family="Helvetica", size=15, weight="bold"),
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

        # Interactive reference piano keyboard
        self.piano_view = PianoKeyboard(
            self.main_container,
            start_octave=4,
            num_octaves=2,
            key_width=38,
            key_height=110,
            show_labels=True,
            on_key_click=self._on_piano_key_clicked,
        )
        self.piano_view.pack(pady=10)

        # Feedback ScoreCard
        self.feedback_card = ScoreCard(
            self.main_container,
            on_next=self.load_new_question,
            on_replay=self._play_current_note,
        )

    def load_new_question(self):
        """Generates and displays a new random staff reading question."""
        self.is_answered = False
        self.feedback_card.pack_forget()
        self.piano_view.clear_highlights()

        clef_pt = self.clef_select.get()
        clef_key = "treble" if "Sol" in clef_pt else "bass"
        include_acc = self.accidentals_var.get()

        # Update piano range according to clef
        if clef_key == "treble":
            self.piano_view.set_range(start_octave=4, num_octaves=2)
        else:
            self.piano_view.set_range(start_octave=2, num_octaves=2)

        self.current_question = QuizEngine.generate_staff_reading_question(
            clef=clef_key,
            include_accidentals=include_acc,
        )

        self.prompt_label.configure(text=self.current_question.prompt_text)
        self.staff_view.set_clef(clef_key)
        if self.current_question.staff_note:
            self.staff_view.set_single_note(self.current_question.staff_note, color="#38BDF8")

        for i, opt_text in enumerate(self.current_question.options):
            btn = self.option_buttons[i]
            btn.configure(
                text=opt_text,
                fg_color=("#E2E8F0", "#334155"),
                text_color=("#0F172A", "#F8FAFC"),
                hover_color=("#CBD5E1", "#475569"),
                state="normal",
            )

    def _play_current_note(self):
        if self.current_question and self.current_question.staff_note:
            self.audio_player.play_note(self.current_question.staff_note, duration=0.8)

    def _on_piano_key_clicked(self, note):
        """Allows answering or previewing by clicking the piano key."""
        if not self.is_answered and self.current_question:
            # Check if clicked key matches any option
            for idx, opt in enumerate(self.current_question.options):
                if note.pitch in opt or note.letter in opt:
                    self._handle_answer_selection(idx)
                    break

    def _handle_answer_selection(self, selected_index: int):
        if self.is_answered or not self.current_question:
            return

        self.is_answered = True
        correct_index = self.current_question.correct_index
        is_correct = selected_index == correct_index

        # Play note sound upon answering
        self._play_current_note()

        # Update button colors
        for i, btn in enumerate(self.option_buttons):
            if i == correct_index:
                btn.configure(fg_color="#059669", text_color="#FFFFFF")
            elif i == selected_index and not is_correct:
                btn.configure(fg_color="#DC2626", text_color="#FFFFFF")
            btn.configure(state="disabled")

        # Highlight on piano keyboard
        if self.current_question.staff_note:
            color = "#10B981" if is_correct else "#EF4444"
            self.piano_view.highlight_notes([self.current_question.staff_note], color=color)

        # Record in user manager
        stats = self.user_manager.record_attempt(
            category="leitura_pauta",
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
