from gui.i18n import t
"""Interactive Staff Reading practice screen for Treble and Bass clefs."""
from typing import Callable, List, Optional
import customtkinter as ctk
from core.quiz_engine import QuizEngine, QuizQuestion, QuestionType
from core.staff_tutor import get_note_explanation, generate_tutor_pool, LEVELS_INFO
from core.user_manager import UserManager
from audio.player import get_audio_player
from gui.components.staff_canvas import StaffCanvas
from gui.components.piano_keyboard import PianoKeyboard
from gui.components.score_card import ScoreCard
from gui.scroll_utils import bind_mousewheel
from gui import theme
import random


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
        self.current_level = 1
        self.show_hint_var = ctk.BooleanVar(value=False)
        self.weak_notes = {}


        self._build_ui()
        self.load_new_question()

    def _build_ui(self):
        # Top Navigation Bar
        nav_bar = ctk.CTkFrame(self, fg_color="transparent")
        nav_bar.pack(fill="x", padx=20, pady=(16, 8))

        back_btn = ctk.CTkButton(
            nav_bar,
            text=t("btn_back", "← Voltar ao Menu"),
            font=ctk.CTkFont(family="Helvetica", size=13, weight="bold"),
            fg_color="#475569",
            hover_color="#334155",
            width=130,
            command=self.on_back,
        )
        back_btn.pack(side="left")

        title_lbl = ctk.CTkLabel(
            nav_bar,
            text=t("staff_reading_title", "🎼 Leitura de Pauta"),
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

        ctk.CTkLabel(settings_frame, text=t("clef_label", "Clave:"), font=ctk.CTkFont(family="Helvetica", size=12, weight="bold")).pack(side="left", padx=(14, 4), pady=10)

        self.clef_select = ctk.CTkSegmentedButton(
            settings_frame,
            values=[t("clef_treble", "Clave de Sol (𝄞)"), t("clef_bass", "Clave de Fá (𝄢)")],
            command=lambda v: self.load_new_question(),
            selected_color="#059669",
            selected_hover_color="#047857",
        )
        self.clef_select.set(t("clef_treble", "Clave de Sol (𝄞)"))
        self.clef_select.pack(side="left", padx=6, pady=10)

        self.level_select = ctk.CTkOptionMenu(
            settings_frame,
            values=[f"Nível {info['level']}: {info['name']}" for info in LEVELS_INFO],
            command=self._on_level_changed,
            font=ctk.CTkFont(family="Helvetica", size=12),
        )
        self.level_select.set("Nível 1: Notas nas Linhas")
        self.level_select.pack(side="left", padx=16, pady=10)

        self.hint_check = ctk.CTkCheckBox(
            settings_frame,
            text="👁️ Mostrar Dica de Posição",
            variable=self.show_hint_var,
            command=self._on_hint_toggled,
            font=ctk.CTkFont(family="Helvetica", size=12),
        )
        self.hint_check.pack(side="left", padx=16, pady=10)

        # Main scroll container
        self.main_container = ctk.CTkScrollableFrame(self, fg_color=("#F8FAFC", "#0F172A"))
        self.main_container.pack(fill="both", expand=True, padx=20, pady=(0, 10))
        bind_mousewheel(self.main_container)

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
        
        # 💡 Guia Passo-a-Passo
        self.tutor_frame = ctk.CTkFrame(self.staff_card, fg_color=theme.COLOR_SUCCESS_BG, corner_radius=8)
        self.tutor_frame.pack(fill="x", padx=20, pady=8)
        self.tutor_lbl = ctk.CTkLabel(
            self.tutor_frame, 
            text="💡 Guia Passo-a-Passo", 
            font=ctk.CTkFont(family="Helvetica", size=13, weight="bold"),
            text_color=theme.COLOR_SUCCESS
        )
        self.tutor_lbl.pack(anchor="w", padx=10, pady=(6,0))
        self.tutor_desc = ctk.CTkLabel(
            self.tutor_frame, 
            text="", 
            font=ctk.CTkFont(family="Helvetica", size=13),
            text_color=theme.COLOR_TEXT_PRIMARY,
            wraplength=600,
            justify="left"
        )
        self.tutor_desc.pack(anchor="w", padx=10, pady=(0,6))

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

    def _on_level_changed(self, choice: str):
        # Nível X: ... -> extrai o X
        import re
        m = re.search(r"Nível (\d+)", choice)
        if m:
            self.current_level = int(m.group(1))
        self.load_new_question()
        
    def _on_hint_toggled(self):
        if self.current_question and self.current_question.staff_note:
            if self.show_hint_var.get():
                self.staff_view.set_position_hint(self.current_question.staff_note, "#34D399")
            else:
                self.staff_view.set_position_hint(None)
        
    def load_new_question(self):
        """Generates and displays a new random staff reading question based on the selected level."""
        self.is_answered = False
        self.feedback_card.pack_forget()
        self.piano_view.clear_highlights()
        self.staff_view.set_position_hint(None)

        clef_pt = self.clef_select.get()
        clef_key = "treble" if "Sol" in clef_pt else "bass"
        
        # Update piano range according to clef
        if clef_key == "treble":
            self.piano_view.set_range(start_octave=4, num_octaves=2)
        else:
            self.piano_view.set_range(start_octave=2, num_octaves=2)

        pool = generate_tutor_pool(self.current_level, clef_key, include_accidentals=(self.current_level == 4))
        if not pool:
            return
            
        # Weak-spot focus logic
        weighted_pool = list(pool)
        for n in pool:
            if n.pitch in self.weak_notes:
                weighted_pool.extend([n] * self.weak_notes[n.pitch])
                
        target_note = random.choice(weighted_pool)
        
        from core.quiz_engine import QuizQuestion, QuestionType
        from core.notes import NOTE_NAMES, NOTE_NAMES_PT
        all_possible_pitches = list(NOTE_NAMES)
        distractors_pitches = [p for p in all_possible_pitches if p != target_note.pitch]
        random.shuffle(distractors_pitches)

        correct_label = f"{target_note.name_pt} ({target_note.pitch})"
        distractor_labels = [f"{NOTE_NAMES_PT[p]} ({p})" for p in distractors_pitches[:3]]

        options = distractor_labels + [correct_label]
        random.shuffle(options)
        correct_index = options.index(correct_label)

        clef_name = "Clave de Sol" if clef_key == "treble" else "Clave de Fá"
        prompt = f"Identifica a nota desenhada na pauta na **{clef_name}**:"
        explanation = (
            f"Correto! A nota na pauta é **{target_note.name_pt}** ({target_note.pitch}{target_note.octave}), "
            f"com frequência de **{target_note.frequency:.1f} Hz** (MIDI {target_note.midi})."
        )
        
        self.current_question = QuizQuestion(
            question_type=QuestionType.STAFF_NOTE,
            prompt_text=prompt,
            category="leitura_pauta",
            options=options,
            correct_index=correct_index,
            explanation=explanation,
            notes_to_play=[target_note],
            play_mode="melodic_asc",
            staff_note=target_note,
            clef=clef_key,
        )

        self.prompt_label.configure(text=self.current_question.prompt_text)
        self.staff_view.set_clef(clef_key)
        self.staff_view.set_single_note(self.current_question.staff_note, color="#38BDF8")
        
        # Update Tutor Info
        tutor_text = get_note_explanation(self.current_question.staff_note, clef_key)
        self.tutor_desc.configure(text=tutor_text)
        
        if self.show_hint_var.get():
            self.staff_view.set_position_hint(self.current_question.staff_note, "#34D399")

        for i, opt_text in enumerate(self.current_question.options):
            btn = self.option_buttons[i]
            btn.configure(
                text=opt_text,
                fg_color=theme.COLOR_SURFACE_SECONDARY,
                text_color=theme.COLOR_TEXT_PRIMARY,
                hover_color=theme.COLOR_SURFACE_HOVER,
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

        target_pitch = self.current_question.staff_note.pitch
        if not is_correct:
            self.weak_notes[target_pitch] = self.weak_notes.get(target_pitch, 0) + 1
        else:
            if target_pitch in self.weak_notes and self.weak_notes[target_pitch] > 0:
                self.weak_notes[target_pitch] -= 1

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

        # Record atomic spaced review
        note = self.current_question.staff_note
        clef = getattr(self.current_question, "clef", "treble")
        skill_id = f"staff:{clef}:{note.pitch_with_octave}" if note else "staff:treble:unknown"
        stats = self.user_manager.record_atomic_review(
            skill_id=skill_id,
            is_correct=is_correct,
            category="leitura_pauta",
            question_type=self.current_question.question_type.value,
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
