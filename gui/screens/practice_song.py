"""Interactive Song Performance & Play-Along Studio for Piano and Viola/Guitar with physical keyboard, metronome challenge, and USB MIDI."""
import time
from tkinter import filedialog, messagebox
from typing import Callable, Dict, List, Optional
import customtkinter as ctk
from core.notes import Note
from core.songs import Song, SongNote, SONG_LIBRARY, get_song_by_id
from core.midi_importer import import_midi_as_song, save_user_song, load_user_songs
from core.user_manager import UserManager
from audio.player import get_audio_player
from audio.metronome import Metronome, evaluate_rhythm_accuracy
from audio.midi_manager import get_midi_manager
from gui.components.piano_keyboard import PianoKeyboard
from gui.components.staff_canvas import StaffCanvas
from gui.components.guitar_fretboard import GuitarFretboard
from gui.components.score_card import ScoreCard
from gui import theme


# QWERTY / Portuguese physical keyboard mappings for Piano notes
PIANO_KEY_MAPPINGS = {
    # White keys
    "a": "C4",
    "s": "D4",
    "d": "E4",
    "f": "F4",
    "g": "G4",
    "h": "A4",
    "j": "B4",
    "k": "C5",
    "l": "D5",
    "ç": "E5",
    ";": "E5",
    # Black keys
    "w": "C#4",
    "e": "D#4",
    "t": "F#4",
    "y": "G#4",
    "z": "G#4",
    "u": "A#4",
    "o": "C#5",
    "p": "D#5",
}

# Number keys 1-6 for Viola/Guitar strings (6=6th thickest string idx 0, 1=1st thinnest string idx 5)
GUITAR_KEY_MAPPINGS = {
    "6": 0,  # 6ª corda (E2)
    "5": 1,  # 5ª corda (A2)
    "4": 2,  # 4ª corda (D3)
    "3": 3,  # 3ª corda (G3)
    "2": 4,  # 2ª corda (B3)
    "1": 5,  # 1ª corda (E4)
}


class PracticeSongScreen(ctk.CTkFrame):
    """
    Interactive play-along performance studio with metronome rhythm challenge,
    USB MIDI hardware support, and computer keyboard mapping.
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

        self.user_songs: List[Song] = load_user_songs()
        self.current_song: Song = (self.user_songs[0] if self.user_songs else SONG_LIBRARY[0])
        self.current_note_idx: int = 0
        self.is_playing_demo: bool = False
        self.instrument_mode: str = "Piano"  # "Piano", "Viola", "Ambos"
        self._demo_timer_id: Optional[str] = None

        # Rhythm & Metronome Challenge Mode
        self.is_challenge_mode: bool = False
        self.metronome = Metronome(bpm=self.current_song.bpm, on_beat=self._on_metronome_beat)
        self.current_combo: int = 0
        self.max_combo: int = 0
        self.rhythm_score: int = 0
        self._expected_note_timestamp: float = time.time()

        # Scoring & Performance metrics
        self.session_correct: int = 0
        self.session_mistakes: int = 0
        self.song_completed: bool = False
        self.song_buttons: List[ctk.CTkButton] = []

        self._build_ui()
        self._bind_keyboard_events()
        self._start_midi_listener()
        self._load_song(self.current_song)

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

    def _on_midi_note_on(self, midi_note: int, velocity: int):
        if not self.winfo_exists() or self.is_playing_demo or self.song_completed or not self.current_song:
            return

        # Safely schedule on main GUI thread
        self.after(0, lambda: self._process_midi_note(midi_note))

    def _on_midi_note_off(self, midi_note: int):
        pass

    def _process_midi_note(self, midi_note: int):
        if not self.current_song or self.current_note_idx >= len(self.current_song.notes):
            return

        expected_sn = self.current_song.notes[self.current_note_idx]
        if expected_sn.note.midi == midi_note or (midi_note % 12 == expected_sn.note.midi % 12):
            self._handle_correct_note()
        else:
            self._handle_incorrect_note()

    def _build_ui(self):
        # 1. Top Navigation Bar
        nav_bar = ctk.CTkFrame(self, fg_color="transparent")
        nav_bar.pack(fill="x", padx=20, pady=(16, 6))

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
            text=f"🎶 Repertório & Estúdio ({user.avatar} {user.username})",
            font=theme.get_font(theme.FONT_TITLE),
            text_color=theme.COLOR_TEXT_PRIMARY,
        )
        title_lbl.pack(side="left", padx=16)

        # Instrument Selector on right
        inst_box = ctk.CTkFrame(nav_bar, fg_color="transparent")
        inst_box.pack(side="right")

        ctk.CTkLabel(
            inst_box,
            text="Modo:",
            font=theme.get_font(theme.FONT_BODY_BOLD),
            text_color=theme.COLOR_TEXT_MUTED,
        ).pack(side="left", padx=(0, 6))

        self.inst_segmented = ctk.CTkSegmentedButton(
            inst_box,
            values=["🎹 Piano", "🎸 Viola", "🎹 + 🎸 Ambos"],
            command=self._on_instrument_mode_changed,
            selected_color=theme.COLOR_PRIMARY,
            selected_hover_color=theme.COLOR_PRIMARY_HOVER,
            font=theme.get_font(theme.FONT_BODY_BOLD),
            height=36,
        )
        self.inst_segmented.set("🎹 Piano")
        self.inst_segmented.pack(side="left")

        # 2. Main Layout (Sidebar with song selection + Main Stage)
        main_layout = ctk.CTkFrame(self, fg_color="transparent")
        main_layout.pack(fill="both", expand=True, padx=20, pady=(4, 14))
        main_layout.grid_columnconfigure(0, weight=0)
        main_layout.grid_columnconfigure(1, weight=1)
        main_layout.grid_rowconfigure(0, weight=1)

        # 2.1 Song Selection Sidebar
        self.song_sidebar = ctk.CTkScrollableFrame(
            main_layout,
            width=260,
            corner_radius=theme.RADIUS_LG,
            fg_color=theme.COLOR_SURFACE,
            border_width=1,
            border_color=theme.COLOR_BORDER,
        )
        self.song_sidebar.grid(row=0, column=0, sticky="nsew", padx=(0, 12))

        # Import MIDI button
        import_btn = ctk.CTkButton(
            self.song_sidebar,
            text="📂 Importar Música (.mid)",
            font=theme.get_font(theme.FONT_BODY_BOLD),
            fg_color=theme.COLOR_PRIMARY,
            hover_color=theme.COLOR_PRIMARY_HOVER,
            height=36,
            corner_radius=theme.RADIUS_MD,
            command=self._handle_import_midi,
        )
        import_btn.pack(fill="x", padx=6, pady=(10, 8))

        self.sidebar_title_lbl = ctk.CTkLabel(
            self.song_sidebar,
            text="Biblioteca de Peças",
            font=theme.get_font(theme.FONT_SECTION),
            text_color=theme.COLOR_TEXT_PRIMARY,
        )
        self.sidebar_title_lbl.pack(anchor="w", padx=12, pady=(4, 6))

        self.songs_btn_container = ctk.CTkFrame(self.song_sidebar, fg_color="transparent")
        self.songs_btn_container.pack(fill="x")

        self._populate_song_sidebar()

        # 2.2 Active Song Studio Stage
        self.stage_scroll = ctk.CTkScrollableFrame(
            main_layout,
            corner_radius=theme.RADIUS_LG,
            fg_color=theme.COLOR_BG,
            border_width=1,
            border_color=theme.COLOR_BORDER,
        )
        self.stage_scroll.grid(row=0, column=1, sticky="nsew")

        self._build_stage_ui()

    def _populate_song_sidebar(self):
        for btn in self.song_buttons:
            btn.destroy()
        self.song_buttons.clear()

        all_songs = SONG_LIBRARY + self.user_songs
        self.sidebar_title_lbl.configure(text=f"Biblioteca de Peças ({len(all_songs)})")

        for s in all_songs:
            is_active = (self.current_song and self.current_song.id == s.id)
            btn = ctk.CTkButton(
                self.songs_btn_container,
                text=f"{s.title}\n{s.composer} ({s.difficulty})",
                font=theme.get_font(theme.FONT_BODY),
                anchor="w",
                height=52,
                corner_radius=theme.RADIUS_MD,
                fg_color=theme.COLOR_PRIMARY if is_active else theme.COLOR_SURFACE_SECONDARY,
                text_color="#FFFFFF" if is_active else theme.COLOR_TEXT_PRIMARY,
                hover_color=theme.COLOR_PRIMARY_HOVER if is_active else theme.COLOR_SURFACE_HOVER,
                command=lambda chosen=s: self._load_song(chosen),
            )
            btn.pack(fill="x", padx=6, pady=3)
            self.song_buttons.append(btn)

    def _handle_import_midi(self):
        filepath = filedialog.askopenfilename(
            title="Selecionar Ficheiro MIDI (.mid / .midi)",
            filetypes=[("Ficheiros MIDI", "*.mid *.midi"), ("Todos os Ficheiros", "*.*")],
        )
        if not filepath:
            return

        try:
            new_song = import_midi_as_song(filepath)
            save_user_song(new_song)
            if not any(s.id == new_song.id for s in self.user_songs):
                self.user_songs.append(new_song)
            self._populate_song_sidebar()
            self._load_song(new_song)
            messagebox.showinfo(
                "Partitura Importada com Sucesso",
                f"A música «{new_song.title}» foi importada com sucesso!\n\n"
                f"• Total de notas: {len(new_song.notes)}\n"
                f"• Andamento detetado: {new_song.bpm} BPM\n"
                f"• Dedilhações e posições no instrumento geradas automaticamente.",
            )
        except Exception as e:
            messagebox.showerror("Erro ao Importar MIDI", f"Não foi possível importar o ficheiro MIDI:\n{e}")

    def _build_stage_ui(self):
        # Header Info Card
        self.info_card = ctk.CTkFrame(
            self.stage_scroll,
            corner_radius=theme.RADIUS_LG,
            fg_color=theme.COLOR_SURFACE,
            border_width=1,
            border_color=theme.COLOR_BORDER,
        )
        self.info_card.pack(fill="x", padx=6, pady=(0, 8))

        top_info = ctk.CTkFrame(self.info_card, fg_color="transparent")
        top_info.pack(fill="x", padx=16, pady=(12, 2))

        self.song_title_lbl = ctk.CTkLabel(
            top_info,
            text="",
            font=theme.get_font(theme.FONT_TITLE, size=22),
            text_color=theme.COLOR_TEXT_PRIMARY,
        )
        self.song_title_lbl.pack(side="left")

        self.song_meta_lbl = ctk.CTkLabel(
            top_info,
            text="",
            font=theme.get_font(theme.FONT_BODY_BOLD),
            text_color=theme.COLOR_TEXT_MUTED,
        )
        self.song_meta_lbl.pack(side="right")

        self.song_desc_lbl = ctk.CTkLabel(
            self.info_card,
            text="",
            font=theme.get_font(theme.FONT_BODY),
            text_color=theme.COLOR_TEXT_MUTED,
            wraplength=640,
            justify="left",
        )
        self.song_desc_lbl.pack(anchor="w", padx=16, pady=(0, 12))

        # Playback Controls & Metronome Bar
        ctrl_bar = ctk.CTkFrame(
            self.stage_scroll,
            corner_radius=theme.RADIUS_LG,
            fg_color=theme.COLOR_SURFACE,
            border_width=1,
            border_color=theme.COLOR_BORDER,
        )
        ctrl_bar.pack(fill="x", padx=6, pady=(0, 8))

        self.play_demo_btn = ctk.CTkButton(
            ctrl_bar,
            text="▶ Ouvir Demonstração",
            font=theme.get_font(theme.FONT_BODY_BOLD),
            fg_color=theme.COLOR_SUCCESS,
            hover_color=theme.COLOR_SUCCESS_HOVER,
            corner_radius=theme.RADIUS_MD,
            width=170,
            height=36,
            command=self._toggle_demo_playback,
        )
        self.play_demo_btn.pack(side="left", padx=10, pady=10)

        self.restart_btn = ctk.CTkButton(
            ctrl_bar,
            text="↺ Reiniciar",
            font=theme.get_font(theme.FONT_BODY_BOLD),
            fg_color="#475569",
            hover_color="#334155",
            corner_radius=theme.RADIUS_MD,
            width=110,
            height=36,
            command=self._restart_practice,
        )
        self.restart_btn.pack(side="left", padx=4)

        # Metronome Toggle Button
        self.metronome_btn = ctk.CTkButton(
            ctrl_bar,
            text="⏱️ Metrónomo: Desligado",
            font=theme.get_font(theme.FONT_BODY_BOLD),
            fg_color=theme.COLOR_SURFACE_SECONDARY,
            hover_color=theme.COLOR_SURFACE_HOVER,
            text_color=theme.COLOR_TEXT_PRIMARY,
            corner_radius=theme.RADIUS_MD,
            height=36,
            command=self._toggle_metronome,
        )
        self.metronome_btn.pack(side="left", padx=6)

        # Tempo BPM Slider
        ctk.CTkLabel(
            ctrl_bar,
            text="BPM:",
            font=theme.get_font(theme.FONT_SMALL_BOLD),
            text_color=theme.COLOR_TEXT_MUTED,
        ).pack(side="left", padx=(10, 4))

        self.bpm_slider = ctk.CTkSlider(
            ctrl_bar,
            from_=40,
            to=180,
            number_of_steps=140,
            width=110,
            command=self._on_bpm_changed,
        )
        self.bpm_slider.set(self.current_song.bpm)
        self.bpm_slider.pack(side="left", padx=2)

        self.bpm_lbl = ctk.CTkLabel(
            ctrl_bar,
            text=f"{self.current_song.bpm}",
            font=theme.get_font(theme.FONT_BODY_BOLD),
            text_color=theme.COLOR_PRIMARY,
            width=35,
        )
        self.bpm_lbl.pack(side="left", padx=4)

        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(self.stage_scroll, height=7, progress_color=theme.COLOR_PRIMARY)
        self.progress_bar.set(0.0)
        self.progress_bar.pack(fill="x", padx=6, pady=(0, 6))

        # Active Note Instruction & Rhythm Feedback Banner
        self.instruction_banner = ctk.CTkFrame(
            self.stage_scroll,
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

        # Visualizers Container
        self.vis_container = ctk.CTkFrame(self.stage_scroll, fg_color="transparent")
        self.vis_container.pack(fill="x", padx=6, pady=2)

        # 1. Staff Canvas
        self.staff_view = StaffCanvas(self.vis_container, width=650, height=145, clef="treble", show_note_names=True)
        self.staff_view.pack(pady=4)

        # 2. Piano Keyboard
        self.piano_view = PianoKeyboard(
            self.vis_container,
            start_octave=3,
            num_octaves=2,
            key_width=42,
            key_height=125,
            on_key_click=self._on_user_piano_click,
        )
        self.piano_view.pack(pady=4)

        # 3. Guitar / Viola Fretboard
        self.guitar_view = GuitarFretboard(
            self.vis_container,
            width=650,
            height=155,
            num_frets=15,
            on_note_clicked=self._on_user_guitar_click,
        )

        # Keyboard Helper Legend
        self.legend_card = ctk.CTkFrame(
            self.stage_scroll,
            corner_radius=theme.RADIUS_MD,
            fg_color=theme.COLOR_SURFACE,
            border_width=1,
            border_color=theme.COLOR_BORDER,
        )
        self.legend_card.pack(fill="x", padx=6, pady=(8, 10))

        self.legend_lbl = ctk.CTkLabel(
            self.legend_card,
            text="",
            font=theme.get_font(theme.FONT_SMALL),
            text_color=theme.COLOR_TEXT_MUTED,
            justify="left",
        )
        self.legend_lbl.pack(padx=14, pady=10)

        # Score Card for completion
        self.score_card = ScoreCard(self.stage_scroll, on_next=self._restart_practice)

    def _on_metronome_beat(self, beat_num: int, timestamp: float):
        self._expected_note_timestamp = timestamp

    def _toggle_metronome(self):
        if self.metronome.is_running:
            self.metronome.stop()
            self.metronome_btn.configure(
                text="⏱️ Metrónomo: Desligado",
                fg_color=theme.COLOR_SURFACE_SECONDARY,
            )
        else:
            self.metronome.set_bpm(int(self.bpm_slider.get()))
            self.metronome.start()
            self.metronome_btn.configure(
                text="⏱️ Metrónomo: A Tocar",
                fg_color=theme.COLOR_PRIMARY,
            )

    def _on_bpm_changed(self, value):
        val = int(value)
        self.bpm_lbl.configure(text=str(val))
        self.metronome.set_bpm(val)

    def _update_legend_text(self):
        if self.instrument_mode == "Piano":
            text = (
                "⌨️ **Atalhos de Teclado no Piano** (ou Teclado MIDI USB conectado):\n"
                "• Teclas Brancas: [A] = Dó4, [S] = Ré4, [D] = Mi4, [F] = Fá4, [G] = Sol4, [H] = Lá4, [J] = Si4, [K] = Dó5, [L] = Ré5, [;] = Mi5\n"
                "• Teclas Pretas:  [W] = Dó#4, [E] = Ré#4, [T] = Fá#4, [Y] = Sol#4, [U] = Lá#4, [O] = Dó#5, [P] = Ré#5"
            )
        elif self.instrument_mode == "Viola":
            text = (
                "⌨️ **Atalhos de Teclado na Viola**:\n"
                "• Teclas [6] a [1] tocam as 6 cordas: [6]=6ª (Mi grave) ... [1]=1ª (Mi agudo).\n"
                "• O traste é indicado no braço e no banner — basta pressionar a tecla da corda certa!"
            )
        else:
            text = "⌨️ **Atalhos**: Podes usar o teclado do PC para tocar tanto no Piano ([A]..[L]) como na Viola ([1]..[6]) ou Teclado MIDI USB."
        self.legend_lbl.configure(text=text)

    def _on_instrument_mode_changed(self, mode: str):
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
        self._update_legend_text()
        self._highlight_active_note()

    def _load_song(self, song: Song):
        self._stop_demo_playback()
        self.current_song = song
        self.current_note_idx = 0
        self.session_correct = 0
        self.session_mistakes = 0
        self.current_combo = 0
        self.max_combo = 0
        self.rhythm_score = 0
        self.song_completed = False
        self.score_card.pack_forget()

        # Update Sidebar button styles
        for i, btn in enumerate(self.song_buttons):
            if SONG_LIBRARY[i].id == song.id:
                btn.configure(
                    fg_color=theme.COLOR_PRIMARY,
                    text_color="#FFFFFF",
                    hover_color=theme.COLOR_PRIMARY_HOVER,
                    font=theme.get_font(theme.FONT_BODY_BOLD),
                )
            else:
                btn.configure(
                    fg_color=theme.COLOR_SURFACE_SECONDARY,
                    text_color=theme.COLOR_TEXT_PRIMARY,
                    hover_color=theme.COLOR_SURFACE_HOVER,
                    font=theme.get_font(theme.FONT_BODY),
                )

        # Update Info Card
        self.song_title_lbl.configure(text=f"{song.title} — {song.composer}")
        self.song_meta_lbl.configure(text=f"Dificuldade: {song.difficulty} • BPM: {song.bpm} • {song.note_count} Notas")
        self.song_desc_lbl.configure(text=song.description)

        # Update Slider
        self.bpm_slider.set(song.bpm)
        self.bpm_lbl.configure(text=str(song.bpm))
        self.metronome.set_bpm(song.bpm)

        # Update Staff clef
        self.staff_view.clef = song.clef
        self._update_legend_text()
        self._highlight_active_note()

    def _highlight_active_note(self):
        if not self.current_song or not self.current_song.notes:
            return

        total_notes = len(self.current_song.notes)
        idx = min(self.current_note_idx, total_notes - 1)
        sn = self.current_song.notes[idx]
        note = sn.note

        pct = idx / float(total_notes) if total_notes > 0 else 0.0
        self.progress_bar.set(pct)

        # 1. Staff Display
        self.staff_view.set_single_note(note, color=theme.COLOR_SUCCESS)

        # 2. Piano Display with Fingering
        piano_fingering = {}
        if sn.piano_finger is not None:
            piano_fingering[note.midi] = sn.piano_finger

        self.piano_view.highlight_notes([note], color=theme.COLOR_SUCCESS)
        self.piano_view.set_fingering(piano_fingering)

        # 3. Guitar / Viola Display
        self.guitar_view.highlight_positions = {}
        self.guitar_view.current_chord_shape = None
        self.guitar_view.highlighted_positions.clear()

        if sn.guitar_string is not None and sn.guitar_fret is not None:
            self.guitar_view.highlighted_positions[(sn.guitar_string, sn.guitar_fret)] = {
                "color": theme.COLOR_SUCCESS,
                "label": note.pitch,
                "is_root": True,
                "note": note,
            }
        else:
            self.guitar_view.highlight_scale([note])

        self.guitar_view.redraw()

        # 4. Guidance Text Banner
        finger_str = f"Dedo {sn.piano_finger} (Mão {sn.piano_hand.capitalize()})" if sn.piano_finger else "Dedo Livre"
        guitar_pos_str = f"{sn.guitar_string + 1}ª Corda, Traste {sn.guitar_fret}" if (sn.guitar_string is not None and sn.guitar_fret is not None) else "Ver no braço"
        syllable = f" «{sn.lyric_syllable}»" if sn.lyric_syllable else ""

        combo_str = f" | 🔥 Combo {self.current_combo}x" if self.current_combo > 1 else ""

        banner_text = (
            f"Nota {idx + 1}/{total_notes}: {note.pitch} ({note.name_pt}){syllable}  |  "
            f"🎹 Piano: {finger_str}  |  🎸 Viola: {guitar_pos_str}{combo_str}"
        )
        self.note_guide_lbl.configure(text=banner_text)

    def _restart_practice(self):
        self.current_note_idx = 0
        self.session_correct = 0
        self.session_mistakes = 0
        self.current_combo = 0
        self.rhythm_score = 0
        self.song_completed = False
        self.score_card.pack_forget()
        self.instruction_banner.configure(fg_color=theme.COLOR_SUCCESS_BG, border_color=theme.COLOR_SUCCESS)
        self._highlight_active_note()

    def _on_physical_key_press(self, event):
        """Processes key presses on the physical computer keyboard."""
        if not self.winfo_exists() or self.is_playing_demo or self.song_completed or not self.current_song:
            return

        if self.current_note_idx >= len(self.current_song.notes):
            return

        char = event.char.lower() if event.char else ""
        if not char:
            return

        expected_sn = self.current_song.notes[self.current_note_idx]
        expected_note = expected_sn.note

        is_match = False

        if self.instrument_mode in ["Piano", "Ambos"] and char in PIANO_KEY_MAPPINGS:
            played_pitch_oct = PIANO_KEY_MAPPINGS[char]
            played_note = Note(played_pitch_oct)
            if played_note.normalized_pitch == expected_note.normalized_pitch:
                is_match = True

        elif self.instrument_mode in ["Viola", "Ambos"] and char in GUITAR_KEY_MAPPINGS:
            played_string_idx = GUITAR_KEY_MAPPINGS[char]
            if expected_sn.guitar_string is not None:
                if played_string_idx == expected_sn.guitar_string:
                    is_match = True
            else:
                is_match = True

        if is_match:
            self._handle_correct_note()
        elif char in PIANO_KEY_MAPPINGS or char in GUITAR_KEY_MAPPINGS:
            self._handle_incorrect_note()

    def _on_user_piano_click(self, clicked_note: Note):
        if not self.winfo_exists() or self.is_playing_demo or self.song_completed or not self.current_song:
            return
        if self.current_note_idx >= len(self.current_song.notes):
            return
        expected_note = self.current_song.notes[self.current_note_idx].note
        if clicked_note.normalized_pitch == expected_note.normalized_pitch:
            self._handle_correct_note()
        else:
            self._handle_incorrect_note()

    def _on_user_guitar_click(self, clicked_note: Note):
        if not self.winfo_exists() or self.is_playing_demo or self.song_completed or not self.current_song:
            return
        if self.current_note_idx >= len(self.current_song.notes):
            return
        expected_note = self.current_song.notes[self.current_note_idx].note
        if clicked_note.normalized_pitch == expected_note.normalized_pitch:
            self._handle_correct_note()
        else:
            self._handle_incorrect_note()

    def _handle_correct_note(self):
        if not self.current_song or self.current_note_idx >= len(self.current_song.notes):
            return

        self.session_correct += 1
        self.current_combo += 1
        if self.current_combo > self.max_combo:
            self.max_combo = self.current_combo

        # Rhythm timing evaluation if metronome is on
        if self.metronome.is_running:
            rating, delta_ms, pts = evaluate_rhythm_accuracy(self._expected_note_timestamp, time.time())
            self.rhythm_score += pts * min(4, 1 + (self.current_combo // 5))

        sn = self.current_song.notes[self.current_note_idx]
        self.audio_player.play_note(sn.note, duration=0.6)

        if self.current_note_idx < len(self.current_song.notes) - 1:
            self.current_note_idx += 1
            self._highlight_active_note()
        else:
            self._finish_song_performance()

    def _handle_incorrect_note(self):
        self.session_mistakes += 1
        self.current_combo = 0
        self.instruction_banner.configure(fg_color=theme.COLOR_CRIMSON_BG, border_color=theme.COLOR_ACCENT_CRIMSON)
        self.after(200, self._restore_banner_color)

    def _restore_banner_color(self):
        if self.winfo_exists():
            self.instruction_banner.configure(fg_color=theme.COLOR_SUCCESS_BG, border_color=theme.COLOR_SUCCESS)

    def _finish_song_performance(self):
        self.song_completed = True
        self.progress_bar.set(1.0)
        if self.metronome.is_running:
            self.metronome.stop()

        total_attempts = self.session_correct + self.session_mistakes
        accuracy = (self.session_correct / float(total_attempts) * 100.0) if total_attempts > 0 else 100.0
        is_passed = accuracy >= 70.0

        # Record attempt in UserManager
        stats = self.user_manager.record_attempt(
            category="repertorio",
            question_type="song_performance",
            is_correct=is_passed,
            prompt=f"Peça: {self.current_song.title}",
            user_answer=f"{self.session_correct}/{len(self.current_song.notes)} notas ({accuracy:.0f}%)",
            correct_answer=self.current_song.title,
        )

        # Check for newly unlocked achievements
        unlocked = self.user_manager.check_achievements()
        ach_msg = f"\n🏆 Desbloqueaste a medalha «{unlocked[0].title}» (+{unlocked[0].xp_reward} XP)!" if unlocked else ""

        msg = f"🎉 Peça Concluída! Precisão: {accuracy:.0f}% • Maior Combo: 🔥 {self.max_combo}x{ach_msg}"
        self.note_guide_lbl.configure(text=msg)

        # Show score card
        self.score_card.show_feedback(
            is_correct=is_passed,
            explanation=f"Tocaste «{self.current_song.title}» com {accuracy:.0f}% de precisão e combo de {self.max_combo}x!",
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
        self.play_demo_btn.configure(
            text="⏸ Pausar Demonstração",
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
        self.play_demo_btn.configure(
            text="▶ Ouvir Demonstração",
            fg_color=theme.COLOR_SUCCESS,
            hover_color=theme.COLOR_SUCCESS_HOVER,
        )

    def _schedule_next_demo_note(self):
        if not self.is_playing_demo or not self.winfo_exists() or not self.current_song:
            return

        if self.current_note_idx >= len(self.current_song.notes):
            self._stop_demo_playback()
            return

        sn = self.current_song.notes[self.current_note_idx]
        bpm = int(self.bpm_slider.get()) if hasattr(self, "bpm_slider") else self.current_song.bpm
        beat_duration_sec = 60.0 / bpm
        note_duration_sec = beat_duration_sec * sn.duration_beats

        self._highlight_active_note()
        self.audio_player.play_note(sn.note, duration=note_duration_sec * 0.9)

        self.current_note_idx += 1
        delay_ms = int(note_duration_sec * 1000)

        self._demo_timer_id = self.after(delay_ms, self._schedule_next_demo_note)

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
