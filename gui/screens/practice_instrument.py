from gui.i18n import t
"""Live acoustic instrument practice screen with real-time microphone pitch listening and auto-advance."""
import time
from typing import Callable, Dict, List, Optional
import customtkinter as ctk
from core.notes import Note
from core.scales import Scale
from core.chords import Chord
from core.songs import Song, SONG_LIBRARY, get_song_by_id
from core.user_manager import UserManager
from audio.player import get_audio_player
from audio.pitch_listener import PitchListener
from audio.metronome import Metronome, evaluate_rhythm_accuracy
from gui.components.piano_keyboard import PianoKeyboard
from gui.components.staff_canvas import StaffCanvas
from gui.components.guitar_fretboard import GuitarFretboard
from gui.components.score_card import ScoreCard
from gui.scroll_utils import bind_mousewheel
from gui import theme


def calculate_pitch_directional_hint(target: Note, detected: Note) -> str:
    """Calculates diatonic/semitone distance and returns a directional hint string."""
    diff_semitones = target.midi - detected.midi
    if diff_semitones == 0:
        return f"Tocaste {detected.pitch_with_octave}, ajusta a afinação delicadamente"

    abs_semitones = abs(diff_semitones)
    direction = "sobe" if diff_semitones > 0 else "desce"

    if abs_semitones % 2 == 0 and abs_semitones >= 2:
        tones = abs_semitones // 2
        tone_str = f"{tones} tom" if tones == 1 else f"{tones} tons"
        return f"Tocaste {detected.pitch_with_octave}, o alvo é {target.pitch_with_octave} — {direction} {tone_str} ({abs_semitones} semitons)"
    else:
        st_str = "1 semitom" if abs_semitones == 1 else f"{abs_semitones} semitons"
        return f"Tocaste {detected.pitch_with_octave}, o alvo é {target.pitch_with_octave} — {direction} {st_str}"


class PracticeInstrumentScreen(ctk.CTkFrame):
    """
    Live acoustic instrument trainer. Listens to real physical piano or guitar
    through the microphone, evaluates intonation in cents, and advances when sustained.
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

        self.instrument_type: str = "piano"  # "Piano" ou "Viola"
        self.exercise_type: str = "Escalas"

        self.exercise_notes: List[Note] = []
        self.current_note_idx: int = 0
        self.exercise_title: str = ""

        # Note sustain tracking
        self._matched_start_time: Optional[float] = None
        self._sustain_threshold_sec: float = 0.30  # 300 ms required sustain
        self._is_advancing: bool = False
        self.exercise_completed: bool = False

        # Metronome, Rhythm & Auto Tempo Ramp
        self.target_bpm: int = 100
        self.current_ramp_bpm: int = 70
        self.tempo_ramp_var = ctk.BooleanVar(value=False)
        self.metronome = Metronome(bpm=100, on_beat=self._on_metronome_beat)
        self.current_combo: int = 0
        self.max_combo: int = 0
        self.rhythm_score: int = 0
        self._expected_note_timestamp: float = time.time()

        # GUI Throttling & safety guards
        self._is_gui_busy: bool = False
        self._last_gui_update: float = 0.0

        # Scoring
        self.correct_notes_count: int = 0
        self.total_notes_played: int = 0
        self.session_mistakes: int = 0

        self._build_ui()
        self._setup_default_exercise()

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
            text=f"🎯 Prática de Instrumento Real ({user.avatar} {user.username})",
            font=theme.get_font(theme.FONT_TITLE),
            text_color=theme.COLOR_TEXT_PRIMARY,
        )
        title_lbl.pack(side="left", padx=14)

        # Microphone Toggle Button on top right
        self.mic_btn = ctk.CTkButton(
            nav_bar,
            text=t("btn_start_mic", "🎙️ Ativar Microfone"),
            font=theme.get_font(theme.FONT_BODY_BOLD),
            fg_color=theme.COLOR_SUCCESS,
            hover_color=theme.COLOR_SUCCESS_HOVER,
            width=170,
            height=38,
            corner_radius=theme.RADIUS_MD,
            command=self._toggle_microphone,
        )
        self.mic_btn.pack(side="right")

        # 2. Main Scrollable Container
        self.container = ctk.CTkScrollableFrame(
            self,
            corner_radius=theme.RADIUS_LG,
            fg_color=theme.COLOR_BG,
            border_width=1,
            border_color=theme.COLOR_BORDER,
        )
        self.container.pack(fill="both", expand=True, padx=18, pady=(4, 14))
        bind_mousewheel(self.container)

        # 2.1 Configuration Controls Bar
        cfg_bar = ctk.CTkFrame(
            self.container,
            corner_radius=theme.RADIUS_LG,
            fg_color=theme.COLOR_SURFACE,
            border_width=1,
            border_color=theme.COLOR_BORDER,
        )
        cfg_bar.pack(fill="x", padx=6, pady=(0, 10))

        # Instrument Selector
        ctk.CTkLabel(cfg_bar, text=t("instrument_label", "Instrumento:"), font=theme.get_font(theme.FONT_BODY_BOLD), text_color=theme.COLOR_TEXT_PRIMARY).pack(side="left", padx=(14, 4), pady=12)
        self.inst_select = ctk.CTkOptionMenu(
            cfg_bar,
            values=[t("lbl_piano_acoustic", "🎹 Piano Acústico"), t("lbl_guitar", "🎸 Viola / Guitarra")],
            command=self._on_instrument_changed,
            font=theme.get_font(theme.FONT_BODY_BOLD),
            height=34,
            corner_radius=theme.RADIUS_SM,
            width=160,
        )
        self.inst_select.set("🎹 Piano Acústico")
        self.inst_select.pack(side="left", padx=4)

        # Exercise Type (Dynamic list with all repertoire songs)
        exercise_values = [
            "Escala Maior de Dó",
            "Escala Menor de Lá",
            "Arpejo Dó Maior (C)",
            "Arpejo Lá Menor (Am)",
        ]
        user_custom = getattr(self.user_manager.current_user, "custom_songs", []) if self.user_manager.current_user else []
        all_repertoire = SONG_LIBRARY + user_custom
        for s in all_repertoire:
            inst_icon = "🎸 " if getattr(s, "instrument", "piano") == "guitar" else "🎹 "
            exercise_values.append(f"Música: {inst_icon}{s.title}")

        ctk.CTkLabel(cfg_bar, text="Exercício:", font=theme.get_font(theme.FONT_BODY_BOLD), text_color=theme.COLOR_TEXT_PRIMARY).pack(side="left", padx=(10, 4))
        self.exercise_type_select = ctk.CTkOptionMenu(
            cfg_bar,
            values=exercise_values,
            command=self._on_exercise_changed,
            font=theme.get_font(theme.FONT_BODY),
            height=34,
            corner_radius=theme.RADIUS_SM,
            width=260,
        )
        self.exercise_type_select.set("Escala Maior de Dó")
        self.exercise_type_select.pack(side="left", padx=4)

        # Metronome Toggle
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

        # Restart exercise button
        restart_btn = ctk.CTkButton(
            cfg_bar,
            text=t("btn_restart", "↺ Reiniciar"),
            font=theme.get_font(theme.FONT_BODY_BOLD),
            fg_color="#475569",
            hover_color="#334155",
            width=90,
            height=34,
            corner_radius=theme.RADIUS_SM,
            command=self._restart_exercise,
        )
        restart_btn.pack(side="right", padx=10)

        # 2.2 Live Tuner Gauge / Pitch Display Card
        self.tuner_card = ctk.CTkFrame(
            self.container,
            corner_radius=theme.RADIUS_LG,
            fg_color=theme.COLOR_SURFACE,
            border_width=2,
            border_color=theme.COLOR_BORDER,
        )
        self.tuner_card.pack(fill="x", padx=6, pady=(0, 10))

        tuner_grid = ctk.CTkFrame(self.tuner_card, fg_color="transparent")
        tuner_grid.pack(fill="x", padx=16, pady=12)
        tuner_grid.grid_columnconfigure((0, 1), weight=1)

        # Left: Target Note Box
        target_box = ctk.CTkFrame(tuner_grid, corner_radius=theme.RADIUS_MD, fg_color=theme.COLOR_SURFACE_SECONDARY)
        target_box.grid(row=0, column=0, padx=(0, 8), sticky="nsew")

        ctk.CTkLabel(target_box, text="NOTA ALVO", font=theme.get_font(theme.FONT_BADGE), text_color=theme.COLOR_TEXT_MUTED).pack(pady=(8, 0))
        self.target_note_lbl = ctk.CTkLabel(target_box, text="C4 (Dó)", font=ctk.CTkFont(family=theme.FONT_FAMILY, size=26, weight="bold"), text_color=theme.COLOR_PRIMARY)
        self.target_note_lbl.pack(pady=(0, 8))

        # Right: Detected Note Box
        detected_box = ctk.CTkFrame(tuner_grid, corner_radius=theme.RADIUS_MD, fg_color=theme.COLOR_SURFACE_SECONDARY)
        detected_box.grid(row=0, column=1, padx=(8, 0), sticky="nsew")

        ctk.CTkLabel(detected_box, text="MICROFONE / NOTA DETETADA", font=theme.get_font(theme.FONT_BADGE), text_color=theme.COLOR_TEXT_MUTED).pack(pady=(8, 0))
        self.detected_note_lbl = ctk.CTkLabel(detected_box, text="Microfone desligado", font=ctk.CTkFont(family=theme.FONT_FAMILY, size=26, weight="bold"), text_color=theme.COLOR_TEXT_MUTED)
        self.detected_note_lbl.pack(pady=(0, 8))

        # Cents offset meter / needle
        meter_frame = ctk.CTkFrame(self.tuner_card, fg_color="transparent")
        meter_frame.pack(fill="x", padx=16, pady=(0, 10))

        self.cents_bar = ctk.CTkProgressBar(meter_frame, height=10, progress_color=theme.COLOR_SUCCESS)
        self.cents_bar.set(0.5)  # 0.5 = perfectly in tune
        self.cents_bar.pack(fill="x", pady=4)

        self.intonation_status_lbl = ctk.CTkLabel(
            meter_frame,
            text="Toca a nota no teu instrumento acústico após ligar o microfone!",
            font=theme.get_font(theme.FONT_BODY_BOLD),
            text_color=theme.COLOR_TEXT_MUTED,
        )
        self.intonation_status_lbl.pack()

        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(self.container, height=7, progress_color=theme.COLOR_PRIMARY)
        self.progress_bar.set(0.0)
        self.progress_bar.pack(fill="x", padx=6, pady=(0, 8))

        # 2.3 Visualizers
        vis_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        vis_frame.pack(fill="x", padx=6, pady=2)

        # 1. Staff Canvas
        self.staff_view = StaffCanvas(vis_frame, width=650, height=145, clef="treble", show_note_names=True)
        self.staff_view.pack(pady=4)

        # 2. Piano View
        self.piano_view = PianoKeyboard(vis_frame, start_octave=2, num_octaves=4, key_width=25, key_height=125)
        self.piano_view.pack(pady=4)

        # 3. Guitar View
        self.guitar_view = GuitarFretboard(vis_frame, width=650, height=155, num_frets=15)

        # Guidance hint
        hint_card = ctk.CTkFrame(
            self.container,
            corner_radius=theme.RADIUS_MD,
            fg_color=theme.COLOR_PRIMARY_BG,
            border_width=1,
            border_color=theme.COLOR_PRIMARY_BORDER,
        )
        hint_card.pack(fill="x", padx=6, pady=(8, 10))

        ctk.CTkLabel(
            hint_card,
            text="ℹ️ **Como Funciona**: Toca a nota pedida no teu instrumento acústico perto do microfone. Quando a nota estiver afinada (±25 cents) e sustentada por 0.3s, a aplicação avança automaticamente!",
            font=theme.get_font(theme.FONT_BODY),
            text_color=theme.COLOR_PRIMARY,
            justify="left",
            wraplength=660,
        ).pack(padx=16, pady=10)

        # Score Card for completion
        self.score_card = ScoreCard(self.container, on_next=self._restart_exercise)

    def _on_instrument_changed(self, choice: str):
        from gui.i18n import t
        if choice == t("lbl_guitar", "🎸 Viola / Guitarra"):
            self.instrument_type = "guitar"
            self.piano_view.pack_forget()
            self.guitar_view.pack(pady=4)
        else:
            self.instrument_type = "piano"
            self.piano_view.pack(pady=4)
            self.guitar_view.pack_forget()
        self._highlight_target_note()

    def _setup_default_exercise(self):
        self._on_exercise_changed(self.exercise_type_select.get())

    def _on_exercise_changed(self, choice: str):
        self.current_note_idx = 0
        self.correct_notes_count = 0
        self.total_notes_played = 0
        self.exercise_completed = False
        self._matched_start_time = None
        self.note_performance_history: Dict[str, List[dict]] = {}  # {pitch_with_octave: [{"detected": Note, "cents": float, "success": bool}]}
        self.score_card.pack_forget()

        if "Escala Maior de Dó" in choice:
            scale = Scale(Note("C4"), "major")
            self.exercise_notes = list(scale.notes)
            self.exercise_title = "Escala Maior de Dó"
        elif "Escala Menor de Lá" in choice:
            scale = Scale(Note("A3"), "natural_minor")
            self.exercise_notes = list(scale.notes)
            self.exercise_title = "Escala Menor de Lá"
        elif "Arpejo Dó Maior" in choice:
            chord = Chord(Note("C4"), "major")
            self.exercise_notes = [chord.root, chord.notes[1], chord.notes[2], Note("C5")]
            self.exercise_title = "Arpejo de Dó Maior"
        elif "Arpejo Lá Menor" in choice:
            chord = Chord(Note("A3"), "minor")
            self.exercise_notes = [chord.root, chord.notes[1], chord.notes[2], Note("A4")]
            self.exercise_title = "Arpejo de Lá Menor"
        else:
            # Search dynamically in repertoire
            user_custom = getattr(self.user_manager.current_user, "custom_songs", []) if self.user_manager.current_user else []
            all_songs = SONG_LIBRARY + user_custom
            found_song = None
            for s in all_songs:
                if s.title in choice:
                    found_song = s
                    break

            if found_song:
                self.exercise_notes = [sn.note for sn in found_song.notes]
                self.exercise_title = f"{found_song.title} ({found_song.composer})"
                # Auto switch active instrument to match song's primary instrument
                song_inst = getattr(found_song, "instrument", "piano")
                if song_inst == "guitar" and self.instrument_type != "guitar":
                    self.inst_select.set("🎸 Viola / Guitarra")
                    self._on_instrument_changed("🎸 Viola / Guitarra")
                elif song_inst == "piano" and self.instrument_type != "piano":
                    self.inst_select.set("🎹 Piano Acústico")
                    self._on_instrument_changed("🎹 Piano Acústico")
            else:
                self.exercise_notes = [Note("C4"), Note("D4"), Note("E4"), Note("F4"), Note("G4")]
                self.exercise_title = "Exercício Livre"

        self._highlight_target_note()

    def _highlight_target_note(self):
        if not self.exercise_notes:
            return

        total = len(self.exercise_notes)
        idx = min(self.current_note_idx, total - 1)
        target = self.exercise_notes[idx]

        self.progress_bar.set(idx / float(total) if total > 0 else 0.0)
        self.target_note_lbl.configure(text=f"{target.pitch}{target.octave} ({target.name_pt})")

        # 1. Staff
        self.staff_view.set_single_note(target, color="#3B82F6")

        # 2. Piano
        if self.instrument_type == "piano":
            self.piano_view.highlight_notes([target], color="#3B82F6")
            self.piano_view.set_fingering({target.midi: 1})

        # 3. Guitar
        if self.instrument_type == "guitar":
            self.guitar_view.highlight_scale([target])

    def _toggle_microphone(self):
        if self.pitch_listener.is_listening:
            self.pitch_listener.stop_listening()
            self.mic_btn.configure(
                text=t("btn_start_mic", "🎙️ Ativar Microfone"),
                fg_color=theme.COLOR_SUCCESS,
                hover_color=theme.COLOR_SUCCESS_HOVER,
            )
            self.detected_note_lbl.configure(text="Microfone desligado", text_color=theme.COLOR_TEXT_MUTED)
        else:
            started = self.pitch_listener.start_listening(self._on_live_audio_block)
            if started:
                self.mic_btn.configure(
                    text="⏹️ Desativar Microfone",
                    fg_color=theme.COLOR_ACCENT_CRIMSON,
                    hover_color=theme.COLOR_ACCENT_CRIMSON_HOVER,
                )
                self.detected_note_lbl.configure(text="A ouvir...", text_color="#38BDF8")
            else:
                self.detected_note_lbl.configure(text="Erro de microfone", text_color=theme.COLOR_ACCENT_CRIMSON)

    def _on_live_audio_block(
        self,
        detected_note: Optional[Note],
        cents: float,
        conf: float,
        f0: float,
    ):
        """Threaded callback from sounddevice audio stream with rate-limiting."""
        now = time.time()
        if now - self._last_gui_update < 0.075:
            return
        if self._is_gui_busy or not self.winfo_exists():
            return
        self._last_gui_update = now
        self._is_gui_busy = True
        try:
            self.after(0, lambda: self._safe_process_pitch(detected_note, cents, conf, f0))
        except Exception:
            self._is_gui_busy = False

    def _safe_process_pitch(self, detected_note, cents, conf, f0):
        try:
            self._process_pitch_on_gui(detected_note, cents, conf, f0)
        finally:
            self._is_gui_busy = False

    def _process_pitch_on_gui(
        self,
        detected_note: Optional[Note],
        cents: float,
        conf: float,
        f0: float,
    ):
        if not self.winfo_exists() or self.exercise_completed:
            return

        if detected_note is None:
            self._matched_start_time = None
            return

        # Display detected note text
        cents_str = f"{cents:+.0f}c" if abs(cents) >= 1.0 else "0c"
        self.detected_note_lbl.configure(
            text=f"{detected_note.pitch}{detected_note.octave} ({cents_str})",
            text_color=theme.COLOR_SUCCESS if abs(cents) <= 25 else theme.COLOR_ACCENT_AMBER,
        )

        # Update progress bar position (0.0 = -50 cents, 0.5 = 0 cents, 1.0 = +50 cents)
        normalized_cents = max(-50.0, min(50.0, cents))
        meter_val = (normalized_cents + 50.0) / 100.0
        self.cents_bar.set(meter_val)

        target_note = self.exercise_notes[self.current_note_idx]
        pitch_key = target_note.pitch_with_octave
        if pitch_key not in self.note_performance_history:
            self.note_performance_history[pitch_key] = []

        # Check if detected note matches target note pitch class
        if detected_note.normalized_pitch == target_note.normalized_pitch:
            if abs(cents) <= 25.0:
                self.intonation_status_lbl.configure(
                    text="✓ Excelente afinação! Sustenta a nota...",
                    text_color=theme.COLOR_SUCCESS,
                )
                self.tuner_card.configure(border_color=theme.COLOR_SUCCESS)

                self.note_performance_history[pitch_key].append({
                    "detected": detected_note,
                    "cents": cents,
                    "success": True,
                })

                now = time.time()
                if self._matched_start_time is None:
                    self._matched_start_time = now
                elif (now - self._matched_start_time) >= self._sustain_threshold_sec and not self._is_advancing:
                    self._advance_to_next_target_note()
            elif cents < -25.0:
                self.intonation_status_lbl.configure(
                    text="▲ Mesma nota — toca ligeiramente mais agudo",
                    text_color=theme.COLOR_ACCENT_AMBER,
                )
                self.tuner_card.configure(border_color=theme.COLOR_ACCENT_AMBER)
                self._matched_start_time = None
            else:
                self.intonation_status_lbl.configure(
                    text="▼ Mesma nota — toca ligeiramente mais grave",
                    text_color=theme.COLOR_ACCENT_AMBER,
                )
                self.tuner_card.configure(border_color=theme.COLOR_ACCENT_AMBER)
                self._matched_start_time = None
        else:
            hint = calculate_pitch_directional_hint(target_note, detected_note)
            self.intonation_status_lbl.configure(
                text=f"⚠️ {hint}",
                text_color=theme.COLOR_ACCENT_CRIMSON,
            )
            self.tuner_card.configure(border_color=theme.COLOR_ACCENT_CRIMSON)
            self._matched_start_time = None

            self.note_performance_history[pitch_key].append({
                "detected": detected_note,
                "cents": cents,
                "success": False,
            })

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

    def _advance_to_next_target_note(self):
        self._is_advancing = True
        self.correct_notes_count += 1
        self.total_notes_played += 1

        rhythm_feedback = ""
        if self.metronome.is_running:
            rating, delta_ms, pts = evaluate_rhythm_accuracy(self._expected_note_timestamp, time.time())
            self.rhythm_score += pts
            rhythm_feedback = f" • Ritmo: {rating} ({delta_ms:+.0f}ms)"
            self._expected_note_timestamp = time.time() + (60.0 / self.metronome.bpm)

        self.intonation_status_lbl.configure(
            text=f"✓ Nota correta afinada!{rhythm_feedback}",
            text_color=theme.COLOR_SUCCESS,
        )

        self.audio_player.play_note(self.exercise_notes[self.current_note_idx], duration=0.4)

        if self.current_note_idx < len(self.exercise_notes) - 1:
            self.current_note_idx += 1
            self._highlight_target_note()
            self._matched_start_time = None
            self._is_advancing = False
        else:
            self._finish_acoustic_exercise()

    def _finish_acoustic_exercise(self):
        self.exercise_completed = True
        self.progress_bar.set(1.0)
        self.pitch_listener.stop_listening()
        if self.metronome.is_running:
            self.metronome.stop()
            self.metronome_btn.configure(
                text=t("metronome", "⏱️ Metrónomo"),
                fg_color=theme.COLOR_SURFACE_SECONDARY,
                text_color=theme.COLOR_TEXT_PRIMARY,
            )
        self.mic_btn.configure(text=t("btn_start_mic", "🎙️ Ativar Microfone"), fg_color=theme.COLOR_SUCCESS)

        ramp_msg = ""
        if self.tempo_ramp_var.get() and self.session_mistakes == 0:
            if self.current_ramp_bpm < self.target_bpm:
                self.current_ramp_bpm = min(self.target_bpm, int(self.current_ramp_bpm + max(2, self.target_bpm * 0.05)))
                self.bpm_slider.set(self.current_ramp_bpm)
                self.bpm_lbl.configure(text=f"{self.current_ramp_bpm} (Rampa)")
                self.metronome.set_bpm(self.current_ramp_bpm)
                ramp_msg = f"\n🏎️ Rampa de Tempo avançou para {self.current_ramp_bpm} BPM!"
            else:
                ramp_msg = f"\n🏆 Atingiste a velocidade alvo completa ({self.target_bpm} BPM)!"

        # Compilar Relatório Detalhado de Afinação por Nota
        failed_notes_summary = []
        for pitch_key, attempts in self.note_performance_history.items():
            failures = [att for att in attempts if not att["success"]]
            if failures:
                avg_cents = sum(f["cents"] for f in failures) / float(len(failures))
                last_det = failures[-1]["detected"]
                failed_notes_summary.append(f"• **{pitch_key}**: {len(failures)} tentativa(s) fora do tom (detetado {last_det.pitch_with_octave}, desvio médio: {avg_cents:+.0f}c)")

        report_str = ""
        if failed_notes_summary:
            report_str = "\n\n📋 **Relatório da Aula (Notas para Reforçar)**:\n" + "\n".join(failed_notes_summary[:5])

        stats = self.user_manager.record_attempt(
            category="pratica_instrumento",
            question_type="acoustic_pitch",
            is_correct=True,
            prompt=f"Exercício: {self.exercise_title}",
            user_answer=f"{self.correct_notes_count}/{len(self.exercise_notes)} notas afinadas",
            correct_answer=self.exercise_title,
        )

        min_cents = min([abs(f["cents"]) for hist in self.note_performance_history.values() for f in hist if "cents" in f], default=100.0)
        unlocked = self.user_manager.check_achievements({"min_cents": min_cents})
        ach_msg = f"\n🏆 Desbloqueaste a medalha «{unlocked[0].title}» (+{unlocked[0].xp_reward} XP)!" if unlocked else ""
        ramp_msg += ach_msg

        self.intonation_status_lbl.configure(
            text=f"🎉 Parabéns! Completaste «{self.exercise_title}» com o teu instrumento real!{ramp_msg}",
            text_color=theme.COLOR_SUCCESS,
        )

        self.score_card.show_feedback(
            is_correct=True,
            explanation=f"Excelente desempenho acústico no {self.instrument_type}! Tocaste e afinaste todas as {len(self.exercise_notes)} notas com sucesso.{ramp_msg}{report_str}",
            stats=stats,
            can_replay=True,
        )
        self.score_card.pack(fill="x", padx=6, pady=(12, 10))

    def _restart_exercise(self):
        self.current_note_idx = 0
        self.correct_notes_count = 0
        self.total_notes_played = 0
        self.session_mistakes = 0
        self.exercise_completed = False
        self._matched_start_time = None
        self._is_advancing = False
        self.score_card.pack_forget()
        self.tuner_card.configure(border_color=theme.COLOR_BORDER)
        self.intonation_status_lbl.configure(
            text="Toca a nota no teu instrumento acústico após ligar o microfone!",
            text_color=theme.COLOR_TEXT_MUTED,
        )
        self._highlight_target_note()

    def _handle_back(self):
        self.pitch_listener.stop_listening()
        if self.metronome.is_running:
            self.metronome.stop()
        self.audio_player.stop_all()
        self.on_back()

    def destroy(self):
        self.pitch_listener.stop_listening()
        if self.metronome.is_running:
            self.metronome.stop()
        super().destroy()
