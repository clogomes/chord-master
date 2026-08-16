from gui.i18n import t
"""Interactive Ear Training & Vocal Solfège Practice Screen with PitchListener real-time validation."""
import time
from typing import Callable, List, Optional
import customtkinter as ctk
from core.quiz_engine import QuizEngine, QuizQuestion, QuestionType
from core.adaptive_engine import generate_adaptive_question
from core.user_manager import UserManager
from core.notes import Note
from audio.player import get_audio_player
from audio.pitch_listener import PitchListener
from gui.components.score_card import ScoreCard
from gui.scroll_utils import bind_mousewheel
from gui import theme


class PracticeEarScreen(ctk.CTkFrame):
    """
    Ear training workout room & vocal solfège studio. Synthesizes intervals or chords,
    and supports real-time microphone vocal pitch validation for solfège singing dictation.
    """

    def __init__(
        self,
        master,
        user_manager: UserManager,
        on_back: Callable[[], None],
        **kwargs,
    ):
        super().__init__(master, fg_color=theme.COLOR_BG, **kwargs)
        self.user_manager = user_manager
        self.on_back = on_back
        self.audio_player = get_audio_player()
        self.pitch_listener = PitchListener(max_fps=15.0)

        self.current_question: Optional[QuizQuestion] = None
        self.option_buttons: List[ctk.CTkButton] = []
        self.is_answered = False

        # Solfège vocal singing tracking
        self._sustain_start_time: Optional[float] = None
        self._sustain_threshold_sec: float = 0.35
        self._is_evaluating_singing: bool = False
        self._is_gui_busy: bool = False
        self._last_gui_update: float = 0.0

        self._build_ui()
        self.load_new_question()

    def _build_ui(self):
        # Top Navigation Bar
        nav_bar = ctk.CTkFrame(self, fg_color="transparent")
        nav_bar.pack(fill="x", padx=20, pady=(16, 6))

        back_btn = ctk.CTkButton(
            nav_bar,
            text=t("btn_back", "← Voltar ao Menu"),
            font=theme.get_font(theme.FONT_BODY_BOLD),
            fg_color="#475569",
            hover_color="#334155",
            width=140,
            height=38,
            corner_radius=theme.RADIUS_MD,
            command=self._handle_back,
        )
        back_btn.pack(side="left")

        user = self.user_manager.current_user
        title_lbl = ctk.CTkLabel(
            nav_bar,
            text=f"🎧 Treino Auditivo & Solfejo ({user.avatar} {user.username})",
            font=theme.get_font(theme.FONT_TITLE),
            text_color=theme.COLOR_TEXT_PRIMARY,
        )
        title_lbl.pack(side="left", padx=16)

        # Settings & Filter Header
        settings_frame = ctk.CTkFrame(
            self,
            corner_radius=theme.RADIUS_LG,
            fg_color=theme.COLOR_SURFACE,
            border_width=1,
            border_color=theme.COLOR_BORDER,
        )
        settings_frame.pack(fill="x", padx=20, pady=(4, 10))

        ctk.CTkLabel(
            settings_frame,
            text="Tipo de Exercício:",
            font=theme.get_font(theme.FONT_BODY_BOLD),
            text_color=theme.COLOR_TEXT_PRIMARY,
        ).pack(side="left", padx=(16, 4), pady=12)

        self.type_select = ctk.CTkSegmentedButton(
            settings_frame,
            values=["Intervalos", "Acordes", "🎤 Ditado de Solfejo (Cantar)"],
            command=lambda v: self.load_new_question(),
            selected_color=theme.COLOR_PRIMARY,
            selected_hover_color=theme.COLOR_PRIMARY_HOVER,
            font=theme.get_font(theme.FONT_BODY_BOLD),
            height=36,
        )
        self.type_select.set("Intervalos")
        self.type_select.pack(side="left", padx=6, pady=10)

        ctk.CTkLabel(
            settings_frame,
            text=t("difficulty", "Dificuldade:"),
            font=theme.get_font(theme.FONT_BODY_BOLD),
            text_color=theme.COLOR_TEXT_PRIMARY,
        ).pack(side="left", padx=(16, 4), pady=12)

        self.diff_select = ctk.CTkSegmentedButton(
            settings_frame,
            values=[t("diff_beginner", "Iniciante"), t("diff_intermediate", "Intermédio"), t("diff_advanced", "Avançado")],
            command=lambda v: self.load_new_question(),
            selected_color="#2563EB",
            selected_hover_color="#1D4ED8",
            font=theme.get_font(theme.FONT_BODY_BOLD),
            height=36,
        )
        self.diff_select.set(t("diff_beginner", "Iniciante"))
        self.diff_select.pack(side="left", padx=6, pady=10)

        # Adaptive Mode Toggle Switch
        self.adaptive_var = ctk.BooleanVar(value=False)
        self.adaptive_switch = ctk.CTkSwitch(
            settings_frame,
            text="🧠 Modo Adaptativo",
            variable=self.adaptive_var,
            command=self.load_new_question,
            font=theme.get_font(theme.FONT_BODY_BOLD),
            progress_color=theme.COLOR_PRIMARY,
        )
        self.adaptive_switch.pack(side="right", padx=16, pady=10)

        # Mode Toggle (Learn / Test)
        mode_frame = ctk.CTkFrame(self, fg_color="transparent")
        mode_frame.pack(fill="x", padx=20, pady=(0, 6))
        
        self.mode_select = ctk.CTkSegmentedButton(
            mode_frame,
            values=["🎓 Modo Aprender (Guiado)", "🎯 Modo Testar (Desafio)"],
            command=lambda v: self._on_mode_changed(),
            selected_color=theme.COLOR_PRIMARY,
            selected_hover_color=theme.COLOR_PRIMARY_HOVER,
            font=theme.get_font(theme.FONT_BODY_BOLD),
            height=36,
        )
        self.mode_select.set("🎯 Modo Testar (Desafio)")
        self.mode_select.pack(fill="x", padx=0, pady=0)

        # Exercise Main Scrollable Container
        self.main_container = ctk.CTkScrollableFrame(
            self,
            corner_radius=theme.RADIUS_LG,
            fg_color=theme.COLOR_BG,
            border_width=1,
            border_color=theme.COLOR_BORDER,
        )
        self.main_container.pack(fill="both", expand=True, padx=20, pady=(0, 14))
        bind_mousewheel(self.main_container)

        # Guided Learning Card
        self.learning_card = ctk.CTkFrame(
            self.main_container,
            corner_radius=theme.RADIUS_LG,
            fg_color=theme.COLOR_SURFACE,
            border_width=1,
            border_color=theme.COLOR_BORDER,
        )
        # Will be packed dynamically when in Learn Mode
        
        self.learning_title_lbl = ctk.CTkLabel(
            self.learning_card,
            text="Mnemónica Musical",
            font=theme.get_font(theme.FONT_TITLE),
            text_color=theme.COLOR_TEXT_PRIMARY,
        )
        self.learning_title_lbl.pack(pady=(16, 4))
        
        from gui.components.staff_canvas import StaffCanvas
        from gui.components.piano_keyboard import PianoKeyboard
        
        self.learning_vis_frame = ctk.CTkFrame(self.learning_card, fg_color="transparent")
        self.learning_vis_frame.pack(fill="x", pady=4, padx=16)
        
        self.learning_staff = StaffCanvas(self.learning_vis_frame, width=400, height=120, clef="treble")
        self.learning_staff.pack(pady=4)
        
        self.learning_piano = PianoKeyboard(
            self.learning_vis_frame,
            start_octave=3,
            num_octaves=2,
            key_width=25,
            key_height=100,
        )
        self.learning_piano.pack(pady=4)

        self.learning_songs_lbl = ctk.CTkLabel(
            self.learning_card,
            text="",
            font=theme.get_font(theme.FONT_BODY_BOLD),
            text_color=theme.COLOR_PRIMARY,
            wraplength=600,
        )
        self.learning_songs_lbl.pack(pady=(8, 4))

        self.learning_desc_lbl = ctk.CTkLabel(
            self.learning_card,
            text="",
            font=theme.get_font(theme.FONT_BODY),
            text_color=theme.COLOR_TEXT_PRIMARY,
            wraplength=600,
        )
        self.learning_desc_lbl.pack(pady=(4, 12), padx=20)

        self.learning_play_btn = ctk.CTkButton(
            self.learning_card,
            text="🔊 Ouvir Exemplo Guiado",
            font=theme.get_font(theme.FONT_BODY_BOLD),
            fg_color=theme.COLOR_SUCCESS,
            hover_color=theme.COLOR_SUCCESS_HOVER,
            corner_radius=theme.RADIUS_MD,
            height=40,
            command=self._play_guided_example,
        )
        self.learning_play_btn.pack(pady=(0, 16))

        # Audio playback & question card
        self.play_card = ctk.CTkFrame(
            self.main_container,
            corner_radius=theme.RADIUS_LG,
            fg_color=theme.COLOR_SURFACE,
            border_width=1,
            border_color=theme.COLOR_BORDER,
        )
        self.play_card.pack(fill="x", pady=(4, 12))

        self.prompt_label = ctk.CTkLabel(
            self.play_card,
            text="",
            font=theme.get_font(theme.FONT_SECTION),
            text_color=theme.COLOR_TEXT_PRIMARY,
            wraplength=640,
            justify="center",
        )
        self.prompt_label.pack(pady=(16, 12), padx=20)

        # Audio control buttons row
        self.btn_row = ctk.CTkFrame(self.play_card, fg_color="transparent")
        self.btn_row.pack(pady=(0, 16))

        self.play_btn = ctk.CTkButton(
            self.btn_row,
            text="🔊 Ouvir Áudio",
            font=theme.get_font(theme.FONT_BODY_BOLD),
            fg_color=theme.COLOR_PRIMARY,
            hover_color=theme.COLOR_PRIMARY_HOVER,
            corner_radius=theme.RADIUS_MD,
            height=40,
            width=160,
            command=self.play_question_audio,
        )
        self.play_btn.pack(side="left", padx=6)

        self.play_slow_btn = ctk.CTkButton(
            self.btn_row,
            text="🐢 Tocar Lento",
            font=theme.get_font(theme.FONT_BODY_BOLD),
            fg_color=theme.COLOR_SURFACE_SECONDARY,
            hover_color=theme.COLOR_SURFACE_HOVER,
            text_color=theme.COLOR_TEXT_PRIMARY,
            corner_radius=theme.RADIUS_MD,
            height=40,
            width=140,
            command=self.play_question_audio_slow,
        )
        self.play_slow_btn.pack(side="left", padx=6)

        # Vocal Pitch Detection Card (Visible in Solfège Singing mode)
        self.vocal_mic_card = ctk.CTkFrame(
            self.main_container,
            corner_radius=theme.RADIUS_LG,
            fg_color=theme.COLOR_SURFACE,
            border_width=2,
            border_color=theme.COLOR_BORDER,
        )

        vocal_top = ctk.CTkFrame(self.vocal_mic_card, fg_color="transparent")
        vocal_top.pack(fill="x", padx=16, pady=(12, 4))

        ctk.CTkLabel(
            vocal_top,
            text="🎙️ Deteção Vocal de Afinação em Tempo Real",
            font=theme.get_font(theme.FONT_SECTION),
            text_color=theme.COLOR_TEXT_PRIMARY,
        ).pack(side="left")

        self.mic_toggle_btn = ctk.CTkButton(
            vocal_top,
            text="🎙️ Ativar Microfone & Cantar",
            font=theme.get_font(theme.FONT_BODY_BOLD),
            fg_color=theme.COLOR_SUCCESS,
            hover_color=theme.COLOR_SUCCESS_HOVER,
            corner_radius=theme.RADIUS_MD,
            height=34,
            command=self._toggle_microphone,
        )
        self.mic_toggle_btn.pack(side="right")

        # Detected vocal feedback
        self.vocal_detected_lbl = ctk.CTkLabel(
            self.vocal_mic_card,
            text="Clica em «Ativar Microfone» e canta a nota pedida...",
            font=theme.get_font(theme.FONT_TITLE, size=24),
            text_color=theme.COLOR_TEXT_MUTED,
        )
        self.vocal_detected_lbl.pack(pady=(8, 2))

        self.vocal_cents_bar = ctk.CTkProgressBar(self.vocal_mic_card, height=9, progress_color=theme.COLOR_SUCCESS)
        self.vocal_cents_bar.set(0.5)
        self.vocal_cents_bar.pack(fill="x", padx=24, pady=(4, 6))

        self.vocal_hint_lbl = ctk.CTkLabel(
            self.vocal_mic_card,
            text="Dica: Entoa o nome da nota com voz firme e clara (ex: «Dóóó», «Miii»)",
            font=theme.get_font(theme.FONT_BODY),
            text_color=theme.COLOR_TEXT_MUTED,
        )
        self.vocal_hint_lbl.pack(pady=(0, 14))

        # Options Container (2x2 Grid for multiple-choice buttons)
        self.options_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.options_frame.pack(fill="x", pady=(0, 10))
        self.options_frame.grid_columnconfigure((0, 1), weight=1)

        # Feedback & Score Card Component
        self.score_card = ScoreCard(
            self.main_container,
            on_next=self.load_new_question,
        )

    def _on_mode_changed(self):
        self.load_new_question()

    def _play_guided_example(self):
        if not self.current_question:
            return
        # Play notes
        self.play_question_audio_slow()
        
        # Display notes on staff and piano
        notes = self.current_question.notes_to_play
        if notes:
            self.learning_staff.set_notes(notes)
            self.learning_piano.highlight_notes(notes, color=theme.COLOR_SUCCESS)
            
        # Enable test options now that the user listened
        for btn in self.option_buttons:
            btn.configure(state="normal")
        self.learning_play_btn.configure(text="🔊 Ouvir Novamente")

    def load_new_question(self):
        self._stop_listening()
        self.is_answered = False
        self._sustain_start_time = None
        self._is_evaluating_singing = False
        self.score_card.pack_forget()
        self.learning_card.pack_forget()
        self.learning_staff.set_notes([])
        self.learning_piano.clear_highlights()
        self.learning_play_btn.configure(text="🔊 Ouvir Exemplo Guiado")

        ex_type = self.type_select.get()
        diff_map = {t("diff_beginner", "Iniciante"): "beginner", t("diff_intermediate", "Intermédio"): "intermediate", t("diff_advanced", "Avançado"): "advanced"}
        difficulty = diff_map.get(self.diff_select.get(), "beginner")

        if hasattr(self, "adaptive_var") and self.adaptive_var.get():
            self.current_question = generate_adaptive_question(
                self.user_manager.current_user,
                difficulty=difficulty,
            )
            if self.current_question.question_type == QuestionType.SOLFEGE_SING:
                self.vocal_mic_card.pack(fill="x", pady=(0, 12))
                self.play_btn.configure(text="🔊 Ouvir Tom de Referência")
                self.play_slow_btn.pack_forget()
                self.vocal_detected_lbl.configure(text="Clica em «Ativar Microfone» e canta...", text_color=theme.COLOR_TEXT_MUTED)
                self.vocal_cents_bar.set(0.5)
            elif self.current_question.play_mode == "chord":
                self.vocal_mic_card.pack_forget()
                self.play_btn.configure(text="🔊 Ouvir Acorde")
                self.play_slow_btn.pack(side="left", padx=6)
            else:
                self.vocal_mic_card.pack_forget()
                self.play_btn.configure(text="🔊 Ouvir Pergunta")
                self.play_slow_btn.pack(side="left", padx=6)
        elif "Solfejo" in ex_type or "Cantar" in ex_type:
            self.current_question = QuizEngine.generate_solfege_sing_question(difficulty)
            self.vocal_mic_card.pack(fill="x", pady=(0, 12))
            self.play_btn.configure(text="🔊 Ouvir Tom de Referência")
            self.play_slow_btn.pack_forget()
            self.vocal_detected_lbl.configure(text="Clica em «Ativar Microfone» e canta...", text_color=theme.COLOR_TEXT_MUTED)
            self.vocal_cents_bar.set(0.5)
        elif ex_type == "Acordes":
            self.current_question = QuizEngine.generate_ear_chord_question(difficulty)
            self.vocal_mic_card.pack_forget()
            self.play_btn.configure(text="🔊 Ouvir Acorde")
            self.play_slow_btn.pack(side="left", padx=6)
        else:
            self.current_question = QuizEngine.generate_ear_interval_question(difficulty)
            self.vocal_mic_card.pack_forget()
            self.play_btn.configure(text="🔊 Ouvir Intervalo")
            self.play_slow_btn.pack(side="left", padx=6)

        is_learn_mode = ("Aprender" in self.mode_select.get())
        if is_learn_mode and self.current_question.question_type == QuestionType.EAR_INTERVAL:
            # Only show learning card for intervals
            from core.ear_mnemonics import get_mnemonic_by_code
            import re
            
            # Extract short code from correct answer (e.g. "Terça Maior (M3)")
            match = re.search(r'\((.*?)\)', self.current_question.correct_answer)
            if match:
                code = match.group(1)
                mnemonic = get_mnemonic_by_code(code)
                if mnemonic:
                    self.learning_title_lbl.configure(text=f"Mnemónica: {mnemonic.name} ({code})")
                    self.learning_songs_lbl.configure(text=f"🎵 {mnemonic.songs}")
                    self.learning_desc_lbl.configure(text=f"📋 {mnemonic.description}")
                    self.learning_card.pack(fill="x", pady=(4, 12))
                    self.play_card.pack_forget()
                else:
                    self.learning_card.pack_forget()
                    self.play_card.pack(fill="x", pady=(4, 12))
            else:
                self.learning_card.pack_forget()
                self.play_card.pack(fill="x", pady=(4, 12))
        else:
            self.learning_card.pack_forget()
            self.play_card.pack(fill="x", pady=(4, 12))

        self.prompt_label.configure(text=self.current_question.prompt_text)
        self._render_options()

        if not is_learn_mode:
            # Automatically play prompt audio on new question
            self.after(250, self.play_question_audio)

    def _render_options(self):
        for btn in self.option_buttons:
            btn.destroy()
        self.option_buttons.clear()

        is_learn_mode = ("Aprender" in self.mode_select.get())

        for idx, opt_text in enumerate(self.current_question.options):
            r = idx // 2
            c = idx % 2
            btn = ctk.CTkButton(
                self.options_frame,
                text=opt_text,
                font=theme.get_font(theme.FONT_BODY_BOLD),
                height=48,
                corner_radius=theme.RADIUS_MD,
                fg_color=theme.COLOR_SURFACE_SECONDARY,
                hover_color=theme.COLOR_SURFACE_HOVER,
                text_color=theme.COLOR_TEXT_PRIMARY,
                state="disabled" if (is_learn_mode and self.current_question.question_type == QuestionType.EAR_INTERVAL) else "normal",
                command=lambda i=idx: self.handle_answer(i),
            )
            btn.grid(row=r, column=c, padx=6, pady=6, sticky="nsew")
            self.option_buttons.append(btn)

    def play_question_audio(self):
        if not self.current_question:
            return
        self.audio_player.play_question(self.current_question, slow_mode=False)

    def play_question_audio_slow(self):
        if not self.current_question:
            return
        self.audio_player.play_question(self.current_question, slow_mode=True)

    def _toggle_microphone(self):
        if self.pitch_listener.is_listening:
            self._stop_listening()
        else:
            self._start_listening()

    def _start_listening(self):
        started = self.pitch_listener.start_listening(self._on_live_vocal_audio)
        if started:
            self.mic_toggle_btn.configure(
                text="⏹️ Desativar Microfone",
                fg_color=theme.COLOR_ACCENT_CRIMSON,
                hover_color=theme.COLOR_ACCENT_CRIMSON_HOVER,
            )
            self.vocal_detected_lbl.configure(text="🎙️ A ouvir a tua voz... Canta a nota!", text_color="#38BDF8")
        else:
            self.vocal_detected_lbl.configure(text="Erro ao aceder ao microfone", text_color=theme.COLOR_ACCENT_CRIMSON)

    def _stop_listening(self):
        self.pitch_listener.stop_listening()
        self.mic_toggle_btn.configure(
            text="🎙️ Ativar Microfone & Cantar",
            fg_color=theme.COLOR_SUCCESS,
            hover_color=theme.COLOR_SUCCESS_HOVER,
        )

    def _on_live_vocal_audio(
        self,
        detected_note: Optional[Note],
        cents: float,
        conf: float,
        freq: float,
    ):
        """Thread-safe callback from microphone pitch listener."""
        now = time.time()
        if now - self._last_gui_update < 0.075:
            return
        if self._is_gui_busy or not self.winfo_exists() or self.is_answered:
            return
        self._last_gui_update = now
        self._is_gui_busy = True
        try:
            self.after(0, lambda: self._safe_process_vocal_pitch(detected_note, cents, conf, freq))
        except Exception:
            self._is_gui_busy = False

    def _safe_process_vocal_pitch(self, detected_note, cents, conf, freq):
        try:
            self._process_vocal_pitch(detected_note, cents, conf, freq)
        finally:
            self._is_gui_busy = False

    def _process_vocal_pitch(
        self,
        detected_note: Optional[Note],
        cents: float,
        conf: float,
        freq: float,
    ):
        if not self.winfo_exists() or self.is_answered or not self.current_question:
            return

        target_note = self.current_question.target_note
        if not target_note:
            return

        if detected_note is None:
            self._sustain_start_time = None
            return

        # Display detected note
        cents_str = f"{cents:+.0f}c" if abs(cents) >= 1.0 else "0c"
        self.vocal_detected_lbl.configure(
            text=f"A tua voz: {detected_note.pitch}{detected_note.octave} ({detected_note.name_pt}, {cents_str})",
            text_color=theme.COLOR_SUCCESS if abs(cents) <= 25 else theme.COLOR_ACCENT_AMBER,
        )

        norm_cents = max(-50.0, min(50.0, cents))
        self.vocal_cents_bar.set((norm_cents + 50.0) / 100.0)

        # Check if sung note matches target pitch class
        if detected_note.normalized_pitch == target_note.normalized_pitch:
            if abs(cents) <= 40.0:
                self.vocal_hint_lbl.configure(
                    text="✓ Excelente afinação vocal! Mantém a nota...",
                    text_color=theme.COLOR_SUCCESS,
                )
                self.vocal_mic_card.configure(border_color=theme.COLOR_SUCCESS)

                now = time.time()
                if self._sustain_start_time is None:
                    self._sustain_start_time = now
                elif (now - self._sustain_start_time) >= self._sustain_threshold_sec and not self._is_evaluating_singing:
                    self._is_evaluating_singing = True
                    self._handle_vocal_success(detected_note)
            else:
                self.vocal_hint_lbl.configure(
                    text="Ajusta a altura: quase afinado!",
                    text_color=theme.COLOR_ACCENT_AMBER,
                )
                self._sustain_start_time = None
        else:
            self.vocal_hint_lbl.configure(
                text=f"Detetado {detected_note.pitch} — Tenta cantar {target_note.pitch} ({target_note.name_pt})",
                text_color=theme.COLOR_TEXT_MUTED,
            )
            self._sustain_start_time = None

    def _handle_vocal_success(self, sung_note: Note):
        self._stop_listening()
        self.is_answered = True
        self.audio_player.play_note(sung_note, duration=0.6)

        correct_idx = self.current_question.correct_index
        self.handle_answer(correct_idx, from_voice=True)

    def handle_answer(self, chosen_index: int, from_voice: bool = False):
        if self.is_answered and not from_voice:
            return

        self._stop_listening()
        self.is_answered = True
        is_correct = (chosen_index == self.current_question.correct_index)

        # Color the buttons
        for idx, btn in enumerate(self.option_buttons):
            if idx == self.current_question.correct_index:
                btn.configure(fg_color=theme.COLOR_SUCCESS, hover_color=theme.COLOR_SUCCESS_HOVER, text_color="#FFFFFF")
            elif idx == chosen_index and not is_correct:
                btn.configure(fg_color=theme.COLOR_ACCENT_CRIMSON, hover_color=theme.COLOR_ACCENT_CRIMSON_HOVER, text_color="#FFFFFF")

        # Record attempt in UserManager
        stats = self.user_manager.record_attempt(
            category=self.current_question.category,
            question_type=self.current_question.question_type.value,
            is_correct=is_correct,
            prompt=self.current_question.prompt_text,
            user_answer="Voz Afinada" if from_voice else self.current_question.options[chosen_index],
            correct_answer=self.current_question.correct_answer,
        )

        prefix = "🎤 Cantaste com afinação perfeita! " if from_voice else ""
        explanation_full = f"{prefix}{self.current_question.explanation}"

        # Show feedback score card
        self.score_card.show_feedback(
            is_correct=is_correct,
            explanation=explanation_full,
            stats=stats,
            can_replay=True,
        )
        self.score_card.pack(fill="x", pady=(10, 10))

    def _handle_back(self):
        self._stop_listening()
        self.audio_player.stop_all()
        self.on_back()

    def destroy(self):
        self._stop_listening()
        super().destroy()
