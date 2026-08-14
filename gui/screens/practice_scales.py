"""Interactive Scale Practice Studio with Piano, Guitar, Backing Tracks, Metronome, and USB MIDI."""
import time
from typing import Callable, Dict, List, Optional, Tuple
import customtkinter as ctk
from core.notes import Note
from core.scales import Scale, SCALE_TYPES, ScaleDefinition
from core.fingering import assign_piano_fingerings, get_scale_piano_fingering_description
from core.guitar import assign_guitar_coordinates, GuitarFretboardModel
from core.user_manager import UserManager
from audio.player import get_audio_player
from audio.metronome import Metronome, evaluate_rhythm_accuracy
from audio.backing_tracks import BackingTrackPlayer, BACKING_TRACK_LIBRARY
from audio.midi_manager import get_midi_manager
from gui.components.piano_keyboard import PianoKeyboard
from gui.components.staff_canvas import StaffCanvas
from gui.components.guitar_fretboard import GuitarFretboard
from gui.components.score_card import ScoreCard
from gui.scroll_utils import bind_mousewheel
from gui import theme


# QWERTY Key mapping for physical PC keyboard piano input
PIANO_KEY_MAPPINGS = {
    "a": "C4", "s": "D4", "d": "E4", "f": "F4", "g": "G4", "h": "A4", "j": "B4",
    "k": "C5", "l": "D5", "ç": "E5", ";": "E5",
    "w": "C#4", "e": "D#4", "t": "F#4", "y": "G#4", "z": "G#4", "u": "A#4",
    "o": "C#5", "p": "D#5",
}

GUITAR_KEY_MAPPINGS = {
    "6": 0, "5": 1, "4": 2, "3": 3, "2": 4, "1": 5,
}


class PracticeScalesScreen(ctk.CTkFrame):
    """
    Dedicated Scale & Mode Practice Studio.
    Supports all 16 scale types across all root notes, with bidirectional execution,
    piano fingering, guitar CAGED positions, backing tracks, metronome, and auto tempo ramp.
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

        # Scale Configuration
        self.current_root = "C"
        self.current_scale_key = "major"
        self.direction_mode = "Ascendente & Descendente"
        self.instrument_mode = "Piano"  # "Piano", "Viola", "Ambos"

        # Note sequence & performance tracking
        self.scale_notes: List[Note] = []
        self.piano_fingers: List[int] = []
        self.guitar_coords: List[Tuple[int, int]] = []
        self.current_note_idx: int = 0

        # Rhythm, Metronome & Backing Tracks
        self.target_bpm: int = 100
        self.current_ramp_bpm: int = 70
        self.tempo_ramp_var = ctk.BooleanVar(value=False)
        self.metronome = Metronome(bpm=100, on_beat=self._on_metronome_beat)
        self.backing_player = BackingTrackPlayer(bpm=100, volume=0.65)
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
        self._generate_and_load_scale()

    def _on_metronome_beat(self, beat_num: int):
        pass

    def _bind_keyboard_events(self):
        self._unbind_keyboard_events()
        try:
            self.winfo_toplevel().bind("<KeyPress>", self._on_physical_key_press)
        except Exception:
            pass

    def _unbind_keyboard_events(self):
        try:
            self.winfo_toplevel().unbind("<KeyPress>")
        except Exception:
            pass

    def _start_midi_listener(self):
        self.midi_manager.start_listening(
            on_note_on=self._on_midi_note_on,
            on_note_off=self._on_midi_note_off,
        )

    def _build_ui(self):
        # 1. Top Navigation Bar
        nav_bar = ctk.CTkFrame(self, fg_color="transparent")
        nav_bar.pack(fill="x", padx=18, pady=(14, 6))

        back_btn = ctk.CTkButton(
            nav_bar,
            text="← Voltar ao Menu",
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
            text=f"🎼 Estúdio de Prática de Escalas ({user.avatar} {user.username})",
            font=theme.get_font(theme.FONT_TITLE),
            text_color=theme.COLOR_TEXT_PRIMARY,
        )
        title_lbl.pack(side="left", padx=14)

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

        # 2.1 Configuration Selector Bar
        cfg_card = ctk.CTkFrame(
            self.container,
            corner_radius=theme.RADIUS_LG,
            fg_color=theme.COLOR_SURFACE,
            border_width=1,
            border_color=theme.COLOR_BORDER,
        )
        cfg_card.pack(fill="x", padx=6, pady=(0, 10))

        # Row 1: Root & Scale Selectors
        row1 = ctk.CTkFrame(cfg_card, fg_color="transparent")
        row1.pack(fill="x", padx=12, pady=(10, 6))

        ctk.CTkLabel(row1, text="Tónica:", font=theme.get_font(theme.FONT_BODY_BOLD), text_color=theme.COLOR_TEXT_PRIMARY).pack(side="left", padx=(0, 4))
        self.root_select = ctk.CTkOptionMenu(
            row1,
            values=["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"],
            command=self._on_config_changed,
            width=80,
            height=34,
            corner_radius=theme.RADIUS_SM,
        )
        self.root_select.set("C")
        self.root_select.pack(side="left", padx=(0, 12))

        ctk.CTkLabel(row1, text="Escala / Modo:", font=theme.get_font(theme.FONT_BODY_BOLD), text_color=theme.COLOR_TEXT_PRIMARY).pack(side="left", padx=(0, 4))
        scale_names = [f"{s.name_pt} ({s.key})" for s in SCALE_TYPES.values()]
        self.scale_select = ctk.CTkOptionMenu(
            row1,
            values=scale_names,
            command=self._on_config_changed,
            width=260,
            height=34,
            corner_radius=theme.RADIUS_SM,
        )
        self.scale_select.set(scale_names[0])
        self.scale_select.pack(side="left", padx=(0, 12))

        ctk.CTkLabel(row1, text="Sentido:", font=theme.get_font(theme.FONT_BODY_BOLD), text_color=theme.COLOR_TEXT_PRIMARY).pack(side="left", padx=(0, 4))
        self.dir_select = ctk.CTkOptionMenu(
            row1,
            values=["Ascendente & Descendente", "Apenas Ascendente", "Apenas Descendente"],
            command=self._on_config_changed,
            width=200,
            height=34,
            corner_radius=theme.RADIUS_SM,
        )
        self.dir_select.set("Ascendente & Descendente")
        self.dir_select.pack(side="left", padx=(0, 4))

        # Row 2: Instrument Mode, Metronome, Backing Track, BPM & Tempo Ramp
        row2 = ctk.CTkFrame(cfg_card, fg_color="transparent")
        row2.pack(fill="x", padx=12, pady=(4, 10))

        ctk.CTkLabel(row2, text="Instrumento:", font=theme.get_font(theme.FONT_BODY_BOLD), text_color=theme.COLOR_TEXT_PRIMARY).pack(side="left", padx=(0, 4))
        self.inst_select = ctk.CTkSegmentedButton(
            row2,
            values=["🎹 Piano", "🎸 Viola", "🎹 & 🎸 Ambos"],
            command=self._on_instrument_changed,
            height=34,
            selected_color=theme.COLOR_PRIMARY,
        )
        self.inst_select.set("🎹 Piano")
        self.inst_select.pack(side="left", padx=(0, 10))

        # Metronome Button
        self.metronome_btn = ctk.CTkButton(
            row2,
            text="⏱️ Metrónomo",
            font=theme.get_font(theme.FONT_BODY_BOLD),
            fg_color=theme.COLOR_SURFACE_SECONDARY,
            hover_color=theme.COLOR_SURFACE_HOVER,
            text_color=theme.COLOR_TEXT_PRIMARY,
            height=34,
            width=110,
            corner_radius=theme.RADIUS_SM,
            command=self._toggle_metronome,
        )
        self.metronome_btn.pack(side="left", padx=4)

        # Backing Track Selector
        backing_styles = ["🥁 Sem Ritmo"] + [f"🥁 {p.name_pt}" for p in BACKING_TRACK_LIBRARY.values()]
        self.backing_select = ctk.CTkOptionMenu(
            row2,
            values=backing_styles,
            command=self._on_backing_style_changed,
            font=theme.get_font(theme.FONT_SMALL_BOLD),
            height=34,
            width=165,
            corner_radius=theme.RADIUS_SM,
        )
        self.backing_select.set("🥁 Sem Ritmo")
        self.backing_select.pack(side="left", padx=4)

        # BPM Slider & Label
        ctk.CTkLabel(row2, text="BPM:", font=theme.get_font(theme.FONT_SMALL_BOLD), text_color=theme.COLOR_TEXT_MUTED).pack(side="left", padx=(6, 2))
        self.bpm_slider = ctk.CTkSlider(
            row2,
            from_=40,
            to=180,
            number_of_steps=140,
            width=85,
            command=self._on_bpm_changed,
        )
        self.bpm_slider.set(self.target_bpm)
        self.bpm_slider.pack(side="left", padx=2)

        self.bpm_lbl = ctk.CTkLabel(
            row2,
            text=f"{self.target_bpm}",
            font=theme.get_font(theme.FONT_BODY_BOLD),
            text_color=theme.COLOR_PRIMARY,
            width=30,
        )
        self.bpm_lbl.pack(side="left", padx=2)

        # Auto Tempo Ramp Checkbox
        self.ramp_checkbox = ctk.CTkCheckBox(
            row2,
            text="🏎️ Rampa (70%➔100%)",
            variable=self.tempo_ramp_var,
            command=self._on_tempo_ramp_toggled,
            font=theme.get_font(theme.FONT_SMALL_BOLD),
        )
        self.ramp_checkbox.pack(side="left", padx=6)

        # Play Demo / Restart
        self.demo_btn = ctk.CTkButton(
            row2,
            text="▶ Demonstrar",
            font=theme.get_font(theme.FONT_BODY_BOLD),
            fg_color=theme.COLOR_SUCCESS,
            hover_color=theme.COLOR_SUCCESS_HOVER,
            width=110,
            height=34,
            corner_radius=theme.RADIUS_SM,
            command=self._toggle_demo_playback,
        )
        self.demo_btn.pack(side="right", padx=4)

        self.restart_btn = ctk.CTkButton(
            row2,
            text="↺ Reiniciar",
            font=theme.get_font(theme.FONT_BODY_BOLD),
            fg_color="#475569",
            hover_color="#334155",
            width=90,
            height=34,
            corner_radius=theme.RADIUS_SM,
            command=self._restart_practice,
        )
        self.restart_btn.pack(side="right", padx=4)

        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(self.container, height=7, progress_color=theme.COLOR_PRIMARY)
        self.progress_bar.set(0.0)
        self.progress_bar.pack(fill="x", padx=6, pady=(0, 6))

        # Active Note Instruction Banner
        self.instruction_banner = ctk.CTkFrame(
            self.container,
            corner_radius=theme.RADIUS_MD,
            fg_color=theme.COLOR_SUCCESS_BG,
            border_width=1,
            border_color=theme.COLOR_SUCCESS,
        )
        self.instruction_banner.pack(fill="x", padx=6, pady=(0, 8))

        self.note_guide_lbl = ctk.CTkLabel(
            self.instruction_banner,
            text="",
            font=theme.get_font(theme.FONT_SECTION),
            text_color=theme.COLOR_SUCCESS if "#10B981" else "#065F46",
        )
        self.note_guide_lbl.pack(padx=16, pady=12)

        # 2.2 Visualizers
        self.vis_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        self.vis_frame.pack(fill="x", padx=6, pady=2)

        # Staff Canvas
        self.staff_view = StaffCanvas(self.vis_frame, width=720, height=140, clef="treble", show_note_names=True)
        self.staff_view.pack(pady=4)

        # Piano Keyboard
        self.piano_view = PianoKeyboard(
            self.vis_frame,
            start_octave=2,
            num_octaves=4,
            key_width=25,
            key_height=125,
            on_key_click=self._on_piano_key_clicked,
        )
        self.piano_view.pack(pady=4)

        # Guitar Fretboard
        self.guitar_view = GuitarFretboard(
            self.vis_frame,
            width=720,
            height=150,
            num_frets=15,
            on_position_clicked=self._on_guitar_fret_clicked,
        )

        # Description / Formula Card
        self.desc_card = ctk.CTkFrame(
            self.container,
            corner_radius=theme.RADIUS_MD,
            fg_color=theme.COLOR_SURFACE,
            border_width=1,
            border_color=theme.COLOR_BORDER,
        )
        self.desc_card.pack(fill="x", padx=6, pady=(6, 10))

        self.scale_desc_lbl = ctk.CTkLabel(
            self.desc_card,
            text="",
            font=theme.get_font(theme.FONT_BODY),
            text_color=theme.COLOR_TEXT_PRIMARY,
            justify="left",
            wraplength=700,
        )
        self.scale_desc_lbl.pack(padx=16, pady=10)

        # Score Card for completion
        self.score_card = ScoreCard(self.container, on_next=self._restart_practice)

    def _on_instrument_changed(self, mode: str):
        if "Piano" in mode and "Viola" not in mode:
            self.instrument_mode = "Piano"
            self.piano_view.pack(pady=4)
            self.guitar_view.pack_forget()
        elif "Viola" in mode and "Piano" not in mode:
            self.instrument_mode = "Viola"
            self.piano_view.pack_forget()
            self.guitar_view.pack(pady=4)
        else:
            self.instrument_mode = "Ambos"
            self.piano_view.pack(pady=4)
            self.guitar_view.pack(pady=4)
        self._highlight_active_note()

    def _on_config_changed(self, _=None):
        self.current_root = self.root_select.get()
        scale_choice = self.scale_select.get()
        for k in SCALE_TYPES.keys():
            if f"({k})" in scale_choice:
                self.current_scale_key = k
                break
        self.direction_mode = self.dir_select.get()
        self._generate_and_load_scale()

    def _generate_and_load_scale(self):
        self._stop_demo_playback()
        self.current_note_idx = 0
        self.session_correct = 0
        self.session_mistakes = 0
        self.current_combo = 0
        self.max_combo = 0
        self.rhythm_score = 0
        self.is_completed = False
        self.score_card.pack_forget()

        # Build scale
        root_note = Note(self.current_root, octave=4)
        scale_obj = Scale(root_note, self.current_scale_key)
        asc_notes = list(scale_obj.notes)

        if self.direction_mode == "Apenas Ascendente":
            self.scale_notes = asc_notes
        elif self.direction_mode == "Apenas Descendente":
            self.scale_notes = list(reversed(asc_notes))
        else:  # Ascendente & Descendente
            desc_notes = list(reversed(asc_notes[:-1]))
            self.scale_notes = asc_notes + desc_notes

        # Assign ergonomics
        self.piano_fingers = assign_piano_fingerings(self.scale_notes)
        self.guitar_coords = assign_guitar_coordinates(self.scale_notes)

        # Update description card
        def_obj = scale_obj.definition
        desc_text = (
            f"📖 **{scale_obj.name_pt}** ({def_obj.name_en})\n"
            f"• Fórmula de Graus: {def_obj.formula_degrees}\n"
            f"• Fórmula de Passos: {def_obj.formula_steps}\n"
            f"• Carácter e Aplicação: {def_obj.description}"
        )
        self.scale_desc_lbl.configure(text=desc_text)

        # Highlight scale on guitar
        self.guitar_view.highlight_scale(asc_notes)

        self._highlight_active_note()

    def _highlight_active_note(self):
        if not self.scale_notes:
            return

        total_notes = len(self.scale_notes)
        idx = min(self.current_note_idx, total_notes - 1)
        active_note = self.scale_notes[idx]
        piano_finger = self.piano_fingers[idx] if idx < len(self.piano_fingers) else 1
        g_str, g_fret = self.guitar_coords[idx] if idx < len(self.guitar_coords) else (0, 0)

        # Progress bar
        self.progress_bar.set(idx / float(total_notes) if total_notes > 0 else 0.0)

        # 1. Staff Display (4-note sliding window)
        window_size = 4
        start_w = max(0, min(idx, total_notes - window_size))
        end_w = min(total_notes, start_w + window_size)
        sub_notes = self.scale_notes[start_w:end_w]
        sub_cols = []
        for k in range(start_w, end_w):
            if k < idx:
                sub_cols.append("#64748B")
            elif k == idx:
                sub_cols.append(theme.COLOR_SUCCESS)
            else:
                sub_cols.append("#38BDF8")
        self.staff_view.set_notes(sub_notes, sub_cols)

        # 2. Piano View
        self.piano_view.highlight_notes([active_note], color=theme.COLOR_SUCCESS)
        self.piano_view.set_fingering({active_note.midi: piano_finger})

        # 3. Guitar View
        self.guitar_view.highlighted_positions.clear()
        self.guitar_view.highlight_scale(self.scale_notes)
        self.guitar_view.highlighted_positions[(g_str, g_fret)] = {
            "color": theme.COLOR_SUCCESS,
            "label": active_note.pitch,
            "is_root": (active_note.pitch == self.current_root),
            "note": active_note,
        }
        self.guitar_view.redraw()

        # 4. Banner Text
        combo_str = f" | 🔥 Combo {self.current_combo}x" if self.current_combo > 1 else ""
        finger_desc = f"Dedo {piano_finger} (Mão Direita)"
        guitar_pos_str = f"{g_str + 1}ª Corda, Traste {g_fret}"

        banner_text = (
            f"Nota {idx + 1}/{total_notes}: {active_note.pitch}{active_note.octave} ({active_note.name_pt})  |  "
            f"🎹 Piano: {finger_desc}  |  🎸 Viola: {guitar_pos_str}{combo_str}"
        )
        self.note_guide_lbl.configure(text=banner_text)

    def _toggle_metronome(self):
        if self.metronome.is_running:
            self.metronome.stop()
            self.metronome_btn.configure(
                text="⏱️ Metrónomo",
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

    def _on_backing_style_changed(self, choice: str):
        if "Sem Ritmo" in choice:
            self.backing_player.stop()
        else:
            bpm = int(self.bpm_slider.get())
            for p_id, p in BACKING_TRACK_LIBRARY.items():
                if p.name_pt in choice:
                    self.backing_player.start(p_id, bpm=bpm)
                    break

    def _on_bpm_changed(self, value):
        val = int(value)
        self.bpm_lbl.configure(text=str(val))
        self.metronome.set_bpm(val)
        self.backing_player.set_bpm(val)
        self.target_bpm = val

    def _on_tempo_ramp_toggled(self):
        if self.tempo_ramp_var.get():
            self.current_ramp_bpm = max(40, int(self.target_bpm * 0.70))
            self.bpm_slider.set(self.current_ramp_bpm)
            self.bpm_lbl.configure(text=f"{self.current_ramp_bpm} (Rampa)")
            self.metronome.set_bpm(self.current_ramp_bpm)
            self.backing_player.set_bpm(self.current_ramp_bpm)
        else:
            self.bpm_slider.set(self.target_bpm)
            self.bpm_lbl.configure(text=str(self.target_bpm))
            self.metronome.set_bpm(self.target_bpm)
            self.backing_player.set_bpm(self.target_bpm)

    def _on_physical_key_press(self, event):
        if self.is_playing_demo or self.is_completed:
            return

        char = event.char.lower()
        if char in PIANO_KEY_MAPPINGS:
            note_name = PIANO_KEY_MAPPINGS[char]
            self._process_played_note(Note(note_name))
        elif char in GUITAR_KEY_MAPPINGS:
            str_idx = GUITAR_KEY_MAPPINGS[char]
            target_str, target_fret = self.guitar_coords[self.current_note_idx]
            if str_idx == target_str:
                self._process_played_note(self.scale_notes[self.current_note_idx])
            else:
                self._handle_incorrect_note()

    def _on_piano_key_clicked(self, note: Note):
        if self.is_playing_demo or self.is_completed:
            return
        self._process_played_note(note)

    def _on_guitar_fret_clicked(self, string_idx: int, fret: int):
        if self.is_playing_demo or self.is_completed:
            return
        model = GuitarFretboardModel()
        note = model.get_note_at(string_idx, fret)
        self._process_played_note(note)

    def _on_midi_note_on(self, midi_num: int, velocity: int):
        if self.is_playing_demo or self.is_completed or velocity == 0:
            return
        note = Note.from_midi(midi_num)
        self.after(0, lambda: self._process_played_note(note))

    def _on_midi_note_off(self, midi_num: int):
        pass

    def _process_played_note(self, note: Note):
        if self.is_completed or not self.scale_notes:
            return

        target_note = self.scale_notes[self.current_note_idx]
        if note.normalized_pitch == target_note.normalized_pitch:
            self._handle_correct_note()
        else:
            self._handle_incorrect_note()

    def _handle_correct_note(self):
        self.session_correct += 1
        self.current_combo += 1
        if self.current_combo > self.max_combo:
            self.max_combo = self.current_combo

        rhythm_str = ""
        if self.metronome.is_running:
            rating, delta_ms, pts = evaluate_rhythm_accuracy(self._expected_note_timestamp, time.time())
            self.rhythm_score += pts
            rhythm_str = f" • Ritmo: {rating}"
            self._expected_note_timestamp = time.time() + (60.0 / self.metronome.bpm)

        target_note = self.scale_notes[self.current_note_idx]
        self.audio_player.play_note(target_note, duration=0.45)

        if self.current_note_idx < len(self.scale_notes) - 1:
            self.current_note_idx += 1
            self._highlight_active_note()
        else:
            self._finish_scale_practice()

    def _handle_incorrect_note(self):
        self.session_mistakes += 1
        self.current_combo = 0
        self.instruction_banner.configure(fg_color=theme.COLOR_CRIMSON_BG, border_color=theme.COLOR_ACCENT_CRIMSON)
        self.after(200, self._restore_banner_color)

    def _restore_banner_color(self):
        if self.winfo_exists():
            self.instruction_banner.configure(fg_color=theme.COLOR_SUCCESS_BG, border_color=theme.COLOR_SUCCESS)

    def _finish_scale_practice(self):
        self.is_completed = True
        self.progress_bar.set(1.0)
        if self.metronome.is_running:
            self.metronome.stop()
            self.metronome_btn.configure(text="⏱️ Metrónomo", fg_color=theme.COLOR_SURFACE_SECONDARY)
        self.backing_player.stop()

        total_attempts = self.session_correct + self.session_mistakes
        accuracy = (self.session_correct / float(total_attempts) * 100.0) if total_attempts > 0 else 100.0
        is_passed = accuracy >= 70.0

        ramp_msg = ""
        if self.tempo_ramp_var.get() and self.session_mistakes == 0:
            if self.current_ramp_bpm < self.target_bpm:
                self.current_ramp_bpm = min(self.target_bpm, int(self.current_ramp_bpm + max(2, self.target_bpm * 0.05)))
                self.bpm_slider.set(self.current_ramp_bpm)
                self.bpm_lbl.configure(text=f"{self.current_ramp_bpm} (Rampa)")
                self.metronome.set_bpm(self.current_ramp_bpm)
                self.backing_player.set_bpm(self.current_ramp_bpm)
                ramp_msg = f"\n🏎️ Rampa de Tempo acelerou para {self.current_ramp_bpm} BPM!"
            else:
                ramp_msg = f"\n🏆 Atingiste o andamento alvo completo ({self.target_bpm} BPM)!"

        scale_title = f"{self.current_root} {SCALE_TYPES[self.current_scale_key].name_pt}"

        stats = self.user_manager.record_attempt(
            category="escalas_modos",
            question_type="scale_performance",
            is_correct=is_passed,
            prompt=f"Escala: {scale_title}",
            user_answer=f"{self.session_correct}/{len(self.scale_notes)} notas ({accuracy:.0f}%)",
            correct_answer=scale_title,
        )

        unlocked = self.user_manager.check_achievements()
        ach_msg = f"\n🏆 Desbloqueaste a medalha «{unlocked[0].title}» (+{unlocked[0].xp_reward} XP)!" if unlocked else ""

        self.note_guide_lbl.configure(
            text=f"🎉 Escala Concluída! Precisão: {accuracy:.0f}% • Maior Combo: 🔥 {self.max_combo}x{ramp_msg}{ach_msg}"
        )

        self.score_card.show_feedback(
            is_correct=is_passed,
            explanation=f"Praticaste a escala **{scale_title}** com {accuracy:.0f}% de precisão e combo de {self.max_combo}x!{ramp_msg}",
            stats=stats,
            can_replay=True,
        )
        self.score_card.pack(fill="x", padx=6, pady=(10, 10))

    def _toggle_demo_playback(self):
        if self.is_playing_demo:
            self._stop_demo_playback()
        else:
            self._start_demo_playback()

    def _start_demo_playback(self):
        self.is_playing_demo = True
        self.demo_btn.configure(
            text="⏸ Pausar",
            fg_color=theme.COLOR_ACCENT_CRIMSON,
            hover_color=theme.COLOR_ACCENT_CRIMSON_HOVER,
        )
        self.current_note_idx = 0
        self._highlight_active_note()
        self._schedule_next_demo_note()

    def _stop_demo_playback(self):
        self.is_playing_demo = False
        if self._demo_timer_id is not None:
            self.after_cancel(self._demo_timer_id)
            self._demo_timer_id = None
        self.demo_btn.configure(
            text="▶ Demonstrar",
            fg_color=theme.COLOR_SUCCESS,
            hover_color=theme.COLOR_SUCCESS_HOVER,
        )

    def _schedule_next_demo_note(self):
        if not self.is_playing_demo or not self.winfo_exists() or not self.scale_notes:
            return

        if self.current_note_idx >= len(self.scale_notes):
            self._stop_demo_playback()
            return

        note = self.scale_notes[self.current_note_idx]
        bpm = int(self.bpm_slider.get())
        note_dur_sec = 60.0 / bpm

        self._highlight_active_note()
        self.audio_player.play_note(note, duration=note_dur_sec * 0.85)

        self.current_note_idx += 1
        delay_ms = int(note_dur_sec * 1000)
        self._demo_timer_id = self.after(delay_ms, self._schedule_next_demo_note)

    def _restart_practice(self):
        self._generate_and_load_scale()

    def _handle_back(self):
        self._unbind_keyboard_events()
        self._stop_demo_playback()
        self.metronome.stop()
        self.backing_player.stop()
        self.midi_manager.stop_listening()
        self.audio_player.stop_all()
        self.on_back()

    def destroy(self):
        self._unbind_keyboard_events()
        self._stop_demo_playback()
        self.metronome.stop()
        self.backing_player.stop()
        self.midi_manager.stop_listening()
        super().destroy()
