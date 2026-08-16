from gui.i18n import t
"""Interactive Technique Exercises Studio for Piano & Guitar Warmup, Dexterity, and Strength."""
import time
from typing import Callable, Dict, List, Optional, Tuple
import customtkinter as ctk
from core.notes import Note
from core.technique_exercises import TECHNIQUE_EXERCISES, TechniqueExercise, get_exercises_by_instrument
from core.user_manager import UserManager
from audio.player import get_audio_player
from audio.metronome import Metronome, evaluate_rhythm_accuracy
from audio.midi_manager import get_midi_manager
from gui.components.piano_keyboard import PianoKeyboard
from gui.components.staff_canvas import StaffCanvas
from gui.components.guitar_fretboard import GuitarFretboard
from gui.components.score_card import ScoreCard
from gui.scroll_utils import bind_mousewheel
from gui.i18n import get_language, t
from gui import theme

PIANO_KEY_MAPPINGS = {
    "a": "C4", "s": "D4", "d": "E4", "f": "F4", "g": "G4", "h": "A4", "j": "B4",
    "k": "C5", "l": "D5", "ç": "E5", ";": "E5",
    "w": "C#4", "e": "D#4", "t": "F#4", "y": "G#4", "z": "G#4", "u": "A#4",
    "o": "C#5", "p": "D#5",
}


class PracticeTechniqueScreen(ctk.CTkFrame):
    """
    Dedicated Technical Exercises Studio for Piano & Guitar.
    Includes finger independence drills (Hanon), chromatic spider walks, 5-finger warmups,
    alternate picking drills, metronome with tempo ramping, and MIDI/keyboard support.
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
        self.midi_manager = get_midi_manager()

        self.current_exercise: TechniqueExercise = TECHNIQUE_EXERCISES[0]
        self.current_note_idx: int = 0

        # Metronome & Auto Tempo Ramp
        self.target_bpm: int = 100
        self.current_ramp_bpm: int = 70
        self.tempo_ramp_var = ctk.BooleanVar(value=False)
        self.metronome = Metronome(bpm=100, on_beat=self._on_metronome_beat)

        self.current_combo: int = 0
        self.max_combo: int = 0
        self.rhythm_score: int = 0
        self._expected_note_timestamp: float = time.time()

        # Session scoring
        self.session_correct: int = 0
        self.session_mistakes: int = 0
        self.is_completed: bool = False
        self.is_playing_demo: bool = False
        self._demo_timer_id: Optional[str] = None

        self._build_ui()
        self._bind_keyboard_events()
        self._start_midi_listener()
        self._load_exercise(self.current_exercise)

    def _on_metronome_beat(self, beat_num: int, timestamp: float = 0.0):
        pass

    def _build_ui(self):
        # 1. Top Navigation Bar
        nav_bar = ctk.CTkFrame(self, fg_color="transparent")
        nav_bar.pack(fill="x", padx=18, pady=(14, 6))

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
            text=f"💪 Exercícios Técnicos & Aquecimento ({user.avatar} {user.username})",
            font=theme.get_font(theme.FONT_TITLE),
            text_color=theme.COLOR_TEXT_PRIMARY,
        )
        title_lbl.pack(side="left", padx=14)

        # 2. Main Scrollable Container
        self.stage_scroll = ctk.CTkScrollableFrame(
            self,
            corner_radius=theme.RADIUS_LG,
            fg_color=theme.COLOR_BG,
            border_width=1,
            border_color=theme.COLOR_BORDER,
        )
        self.stage_scroll.pack(fill="both", expand=True, padx=18, pady=(4, 14))
        bind_mousewheel(self.stage_scroll)

        # 2.1 Configuration Controls Bar
        cfg_bar = ctk.CTkFrame(
            self.stage_scroll,
            corner_radius=theme.RADIUS_LG,
            fg_color=theme.COLOR_SURFACE,
            border_width=1,
            border_color=theme.COLOR_BORDER,
        )
        cfg_bar.pack(fill="x", padx=6, pady=(0, 10))

        # Category / Instrument Selector
        ctk.CTkLabel(cfg_bar, text=t("instrument_label", "Instrumento:"), font=theme.get_font(theme.FONT_BODY_BOLD), text_color=theme.COLOR_TEXT_PRIMARY).pack(side="left", padx=(14, 4), pady=12)
        self.inst_segmented = ctk.CTkSegmentedButton(
            cfg_bar,
            values=["🎹 Piano", "🎸 Viola", "Todos"],
            command=self._on_instrument_filter_changed,
            font=theme.get_font(theme.FONT_BODY),
            height=32,
        )
        self.inst_segmented.set("Todos")
        self.inst_segmented.pack(side="left", padx=4)

        # Exercise Dropdown
        ctk.CTkLabel(cfg_bar, text="Exercício:", font=theme.get_font(theme.FONT_BODY_BOLD), text_color=theme.COLOR_TEXT_PRIMARY).pack(side="left", padx=(10, 4))
        lang = get_language()
        ex_names = [e.get_name(lang) for e in TECHNIQUE_EXERCISES]
        self.ex_option_menu = ctk.CTkOptionMenu(
            cfg_bar,
            values=ex_names,
            command=self._on_exercise_option_selected,
            font=theme.get_font(theme.FONT_BODY),
            height=34,
            corner_radius=theme.RADIUS_SM,
            width=280,
        )
        self.ex_option_menu.pack(side="left", padx=4)

        # Metronome Toggle Button
        self.metronome_btn = ctk.CTkButton(
            cfg_bar,
            text=t("metronome", "⏱️ Metrónomo"),
            font=theme.get_font(theme.FONT_BODY_BOLD),
            fg_color=theme.COLOR_SURFACE_SECONDARY,
            hover_color=theme.COLOR_SURFACE_HOVER,
            height=34,
            width=115,
            corner_radius=theme.RADIUS_SM,
            command=self._toggle_metronome,
        )
        self.metronome_btn.pack(side="left", padx=6)

        # BPM Slider
        self.bpm_slider = ctk.CTkSlider(
            cfg_bar,
            from_=40,
            to=180,
            number_of_steps=140,
            width=90,
            command=self._on_bpm_changed,
        )
        self.bpm_slider.set(self.target_bpm)
        self.bpm_slider.pack(side="left", padx=2)

        self.bpm_lbl = ctk.CTkLabel(
            cfg_bar,
            text=f"{self.target_bpm}",
            font=theme.get_font(theme.FONT_BODY_BOLD),
            text_color=theme.COLOR_PRIMARY,
            width=32,
        )
        self.bpm_lbl.pack(side="left", padx=2)

        # Tempo Ramp Checkbox
        self.ramp_checkbox = ctk.CTkCheckBox(
            cfg_bar,
            text="🏎️ Rampa (70%➔100%)",
            variable=self.tempo_ramp_var,
            command=self._on_tempo_ramp_toggled,
            font=theme.get_font(theme.FONT_SMALL_BOLD),
        )
        self.ramp_checkbox.pack(side="left", padx=8)

        # Play Demo Button
        self.play_demo_btn = ctk.CTkButton(
            cfg_bar,
            text="🔊 Ouvir Exemplo",
            font=theme.get_font(theme.FONT_BODY_BOLD),
            fg_color=theme.COLOR_PRIMARY,
            hover_color=theme.COLOR_PRIMARY_HOVER,
            text_color="#FFFFFF",
            height=34,
            corner_radius=theme.RADIUS_SM,
            command=self._toggle_demo_playback,
        )
        self.play_demo_btn.pack(side="right", padx=10)

        # 2.2 Info Header Card
        self.info_card = ctk.CTkFrame(
            self.stage_scroll,
            corner_radius=theme.RADIUS_LG,
            fg_color=theme.COLOR_SURFACE,
            border_width=1,
            border_color=theme.COLOR_BORDER,
        )
        self.info_card.pack(fill="x", padx=6, pady=(0, 10))

        info_header = ctk.CTkFrame(self.info_card, fg_color="transparent")
        info_header.pack(fill="x", padx=16, pady=(12, 4))

        self.ex_title_lbl = ctk.CTkLabel(
            info_header,
            text="",
            font=theme.get_font(theme.FONT_TITLE),
            text_color=theme.COLOR_TEXT_PRIMARY,
        )
        self.ex_title_lbl.pack(side="left")

        self.ex_meta_lbl = ctk.CTkLabel(
            info_header,
            text="",
            font=theme.get_font(theme.FONT_BODY_BOLD),
            text_color=theme.COLOR_TEXT_MUTED,
        )
        self.ex_meta_lbl.pack(side="right")

        self.ex_desc_lbl = ctk.CTkLabel(
            self.info_card,
            text="",
            font=theme.get_font(theme.FONT_BODY),
            text_color=theme.COLOR_TEXT_MUTED,
            wraplength=720,
            justify="left",
        )
        self.ex_desc_lbl.pack(anchor="w", padx=16, pady=(0, 12))

        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(
            self.info_card,
            height=8,
            fg_color=theme.COLOR_SURFACE_SECONDARY,
            progress_color=theme.COLOR_PRIMARY,
        )
        self.progress_bar.pack(fill="x", padx=16, pady=(0, 12))

        # 2.3 Visualizers (Staff + Piano + Guitar)
        visualizers_frame = ctk.CTkFrame(self.stage_scroll, fg_color="transparent")
        visualizers_frame.pack(fill="x", padx=6, pady=(0, 10))

        # Staff Canvas
        self.staff_view = StaffCanvas(visualizers_frame, width=700, height=140)
        self.staff_view.pack(pady=4)

        # Piano Keyboard
        self.piano_view = PianoKeyboard(visualizers_frame, start_octave=3, num_octaves=2, key_width=32, key_height=130)
        self.piano_view.pack(pady=4)

        # Guitar Fretboard
        self.guitar_view = GuitarFretboard(visualizers_frame, width=720, height=150, num_frets=15)
        self.guitar_view.pack_forget()

        # Feedback & Score Card
        self.feedback_lbl = ctk.CTkLabel(
            self.stage_scroll,
            text="Prime no teclado ou usa o teu piano/viola para tocar as notas do exercício!",
            font=theme.get_font(theme.FONT_SUBTITLE),
            text_color=theme.COLOR_TEXT_PRIMARY,
        )
        self.feedback_lbl.pack(pady=8)

        self.score_card = ScoreCard(self.stage_scroll, on_next=self._restart_exercise)

    def _on_instrument_filter_changed(self, filter_choice: str):
        inst_map = {"🎹 Piano": "piano", "🎸 Viola": "guitar", "Todos": "ambos"}
        sel = inst_map.get(filter_choice, "ambos")
        filtered = get_exercises_by_instrument(sel)
        lang = get_language()
        ex_names = [e.get_name(lang) for e in filtered]
        self.ex_option_menu.configure(values=ex_names)
        if ex_names:
            self.ex_option_menu.set(ex_names[0])
            self._on_exercise_option_selected(ex_names[0])

    def _on_exercise_option_selected(self, option_name: str):
        lang = get_language()
        for e in TECHNIQUE_EXERCISES:
            if e.get_name(lang) == option_name:
                self._load_exercise(e)
                break

    def _load_exercise(self, exercise: TechniqueExercise):
        self._stop_demo_playback()
        self.current_exercise = exercise
        self.current_note_idx = 0
        self.session_correct = 0
        self.session_mistakes = 0
        self.current_combo = 0
        self.rhythm_score = 0
        self.is_completed = False
        self.score_card.pack_forget()

        lang = get_language()
        self.ex_title_lbl.configure(text=exercise.get_name(lang))
        self.ex_meta_lbl.configure(text=f"Categoria: {exercise.category.capitalize()} • Dificuldade: {exercise.difficulty} • {len(exercise.notes)} Notas")
        self.ex_desc_lbl.configure(text=exercise.get_description(lang))

        # Update BPM slider from recommended_bpm_range
        if hasattr(exercise, "recommended_bpm_range") and exercise.recommended_bpm_range:
            min_bpm, max_bpm = exercise.recommended_bpm_range
            default_bpm = int((min_bpm + max_bpm) / 2)
            self.bpm_slider.configure(from_=min_bpm, to=max_bpm, number_of_steps=max(1, max_bpm - min_bpm))
            self.bpm_slider.set(default_bpm)
            self.bpm_lbl.configure(text=str(default_bpm))
            self.target_bpm = default_bpm
            self.metronome.set_bpm(default_bpm)

        # Adjust visualizer visibility
        if exercise.instrument == "guitar":
            self.piano_view.pack_forget()
            self.guitar_view.pack(pady=4)
        else:
            self.piano_view.pack(pady=4)
            self.guitar_view.pack_forget()

        self._highlight_active_note()

    def _highlight_active_note(self):
        if not self.current_exercise.notes:
            return

        total = len(self.current_exercise.notes)
        idx = min(self.current_note_idx, total - 1)
        active_note = self.current_exercise.notes[idx]

        self.progress_bar.set(idx / float(total) if total > 0 else 0.0)

        # 1. Staff
        self.staff_view.set_single_note(active_note, color="#3B82F6")

        # 2. Piano
        if self.current_exercise.instrument != "guitar":
            self.piano_view.highlight_notes([active_note], color="#3B82F6")

        # 3. Guitar
        if self.current_exercise.instrument == "guitar":
            self.guitar_view.highlight_scale([active_note])

    def _toggle_metronome(self):
        if self.metronome.is_running:
            self.metronome.stop()
            self.metronome_btn.configure(
                text=t("metronome", "⏱️ Metrónomo"),
                fg_color=theme.COLOR_SURFACE_SECONDARY,
                text_color=theme.COLOR_TEXT_PRIMARY,
            )
        else:
            self.metronome.start()
            self._expected_note_timestamp = time.time() + (60.0 / self.metronome.bpm)
            self.metronome_btn.configure(
                text="⏱️ A Tocar...",
                fg_color=theme.COLOR_PRIMARY,
                text_color="#FFFFFF",
            )

    def _on_bpm_changed(self, val):
        bpm = int(float(val))
        self.bpm_lbl.configure(text=str(bpm))
        self.metronome.set_bpm(bpm)
        self.target_bpm = bpm

    def _on_tempo_ramp_toggled(self):
        if self.tempo_ramp_var.get():
            self.current_ramp_bpm = max(40, int(self.target_bpm * 0.70))
            self.bpm_slider.set(self.current_ramp_bpm)
            self.bpm_lbl.configure(text=f"{self.current_ramp_bpm} (Rampa)")
            self.metronome.set_bpm(self.current_ramp_bpm)
        else:
            self.bpm_slider.set(self.target_bpm)
            self.bpm_lbl.configure(text=str(self.target_bpm))
            self.metronome.set_bpm(self.target_bpm)

    def _toggle_demo_playback(self):
        if self.is_playing_demo:
            self._stop_demo_playback()
        else:
            self.is_playing_demo = True
            self.play_demo_btn.configure(text="⏹️ Parar Exemplo", fg_color=theme.COLOR_ACCENT_CRIMSON)
            self.current_note_idx = 0
            self._schedule_next_demo_note()

    def _stop_demo_playback(self):
        if self._demo_timer_id:
            self.after_cancel(self._demo_timer_id)
            self._demo_timer_id = None
        self.is_playing_demo = False
        self.play_demo_btn.configure(text="🔊 Ouvir Exemplo", fg_color=theme.COLOR_PRIMARY)

    def _schedule_next_demo_note(self):
        if not self.is_playing_demo or self.current_note_idx >= len(self.current_exercise.notes):
            self._stop_demo_playback()
            return

        note = self.current_exercise.notes[self.current_note_idx]
        self._highlight_active_note()
        self.audio_player.play_note(note, duration=0.45, instrument=self.current_exercise.instrument)

        self.current_note_idx += 1
        self._demo_timer_id = self.after(500, self._schedule_next_demo_note)

    def _on_user_played_note(self, played_pitch: str):
        if self.is_completed or self.is_playing_demo:
            return

        active_note = self.current_exercise.notes[self.current_note_idx]
        if Note(played_pitch).normalized_pitch == active_note.normalized_pitch:
            self.session_correct += 1
            self.current_combo += 1
            if self.current_combo > self.max_combo:
                self.max_combo = self.current_combo

            rhythm_feedback = ""
            if self.metronome.is_running:
                rating, delta_ms, pts = evaluate_rhythm_accuracy(self._expected_note_timestamp, time.time())
                self.rhythm_score += pts
                rhythm_feedback = f" • Ritmo: {rating} ({delta_ms:+.0f}ms)"
                self._expected_note_timestamp = time.time() + (60.0 / self.metronome.bpm)

            self.feedback_lbl.configure(
                text=f"✓ Nota {active_note.pitch_with_octave} correta! (Combo {self.current_combo}x){rhythm_feedback}",
                text_color=theme.COLOR_SUCCESS,
            )
            self.audio_player.play_note(active_note, duration=0.45, instrument=self.current_exercise.instrument)

            if self.current_note_idx < len(self.current_exercise.notes) - 1:
                self.current_note_idx += 1
                self._highlight_active_note()
            else:
                self._finish_exercise()
        else:
            self.session_mistakes += 1
            self.current_combo = 0
            self.feedback_lbl.configure(
                text=f"❌ Nota errada! Esperado: {active_note.pitch_with_octave}",
                text_color=theme.COLOR_ACCENT_CRIMSON,
            )

    def _finish_exercise(self):
        self.is_completed = True
        self.progress_bar.set(1.0)
        if self.metronome.is_running:
            self.metronome.stop()

        ramp_msg = ""
        if self.tempo_ramp_var.get() and self.session_mistakes == 0:
            if self.current_ramp_bpm < self.target_bpm:
                self.current_ramp_bpm = min(self.target_bpm, int(self.current_ramp_bpm + max(2, self.target_bpm * 0.05)))
                self.bpm_slider.set(self.current_ramp_bpm)
                self.bpm_lbl.configure(text=f"{self.current_ramp_bpm} (Rampa)")
                self.metronome.set_bpm(self.current_ramp_bpm)
                ramp_msg = f"\n🏎️ Rampa de Tempo avançou para {self.current_ramp_bpm} BPM!"

        stats = self.user_manager.record_attempt(
            category="tecnica",
            question_type="technique_drill",
            is_correct=True,
            prompt=f"Exercício Técnico: {self.current_exercise.name_pt}",
            user_answer=f"Combo Máx: {self.max_combo}x",
            correct_answer=self.current_exercise.name_pt,
        )

        lang = get_language()
        self.score_card.show_feedback(
            is_correct=True,
            explanation=f"Completaste «{self.current_exercise.get_name(lang)}» com sucesso! Maior sequência consecutiva: {self.max_combo}x.{ramp_msg}",
            stats=stats,
            can_replay=True,
        )
        self.score_card.pack(fill="x", padx=6, pady=(12, 10))

    def _restart_exercise(self):
        self._load_exercise(self.current_exercise)

    def _bind_keyboard_events(self):
        top = self.winfo_toplevel()
        top.bind("<Key>", self._on_key_press)

    def _unbind_keyboard_events(self):
        top = self.winfo_toplevel()
        top.unbind("<Key>")

    def _on_key_press(self, event):
        char = (event.char or "").lower()
        if char in PIANO_KEY_MAPPINGS:
            self._on_user_played_note(PIANO_KEY_MAPPINGS[char])

    def _start_midi_listener(self):
        self.midi_manager.start_listening(self._on_midi_note_on)

    def _on_midi_note_on(self, note_midi: int, velocity: int):
        note = Note.from_midi(note_midi)
        self.after(0, lambda: self._on_user_played_note(note.pitch_with_octave))

    def _handle_back(self):
        self._unbind_keyboard_events()
        self._stop_demo_playback()
        self.metronome.stop()
        self.midi_manager.stop_listening()
        self.audio_player.stop_all()
        self.on_back()

    def destroy(self):
        self._unbind_keyboard_events()
        self._stop_demo_playback()
        self.metronome.stop()
        self.midi_manager.stop_listening()
        super().destroy()
