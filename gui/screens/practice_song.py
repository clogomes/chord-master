"""Interactive Song Performance & Play-Along Studio for Piano and Viola/Guitar."""
from typing import Callable, Dict, List, Optional
import customtkinter as ctk
from core.notes import Note
from core.songs import Song, SongNote, SONG_LIBRARY, get_song_by_id
from core.user_manager import UserManager
from audio.player import get_audio_player
from gui.components.piano_keyboard import PianoKeyboard
from gui.components.staff_canvas import StaffCanvas
from gui.components.guitar_fretboard import GuitarFretboard


class PracticeSongScreen(ctk.CTkFrame):
    """
    Interactive play-along performance studio where students learn to play real songs
    with synchronized staff notation, piano fingering, and guitar fretboard tab guidance.
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

        self.current_song: Song = SONG_LIBRARY[0]
        self.current_note_idx: int = 0
        self.is_playing_demo: bool = False
        self.playback_speed: float = 1.0  # 1.0 = normal 100%
        self.instrument_mode: str = "Ambos"  # "Piano", "Viola", "Ambos"
        self._demo_timer_id: Optional[str] = None
        self.practice_mode: str = "passo_a_passo"  # "passo_a_passo" ou "demonstracao"

        self._build_ui()
        self._load_song(self.current_song)

    def _build_ui(self):
        # 1. Top Navigation Bar
        nav_bar = ctk.CTkFrame(self, fg_color="transparent")
        nav_bar.pack(fill="x", padx=18, pady=(14, 6))

        back_btn = ctk.CTkButton(
            nav_bar,
            text="← Voltar ao Menu",
            font=ctk.CTkFont(family="Helvetica", size=13, weight="bold"),
            fg_color="#475569",
            hover_color="#334155",
            width=130,
            command=self._handle_back,
        )
        back_btn.pack(side="left")

        user = self.user_manager.current_user
        title_lbl = ctk.CTkLabel(
            nav_bar,
            text=f"🎶 Estúdio de Repertório ({user.avatar} {user.username})",
            font=ctk.CTkFont(family="Helvetica", size=20, weight="bold"),
            text_color=("#0F172A", "#F8FAFC"),
        )
        title_lbl.pack(side="left", padx=14)

        # Instrument Selector
        inst_box = ctk.CTkFrame(nav_bar, fg_color="transparent")
        inst_box.pack(side="right")

        self.inst_segmented = ctk.CTkSegmentedButton(
            inst_box,
            values=["🎹 Piano", "🎸 Viola", "🎹 + 🎸 Ambos"],
            command=self._on_instrument_mode_changed,
            selected_color="#2563EB",
            selected_hover_color="#1D4ED8",
        )
        self.inst_segmented.set("🎹 + 🎸 Ambos")
        self.inst_segmented.pack(side="left")

        # 2. Main Layout (Sidebar with song selection + Main Practice Canvas)
        main_layout = ctk.CTkFrame(self, fg_color="transparent")
        main_layout.pack(fill="both", expand=True, padx=18, pady=(4, 14))
        main_layout.grid_columnconfigure(0, weight=0)  # Song selection sidebar
        main_layout.grid_columnconfigure(1, weight=1)  # Active song stage
        main_layout.grid_rowconfigure(0, weight=1)

        # 2.1 Song Selection Sidebar
        self.song_sidebar = ctk.CTkScrollableFrame(
            main_layout,
            width=240,
            corner_radius=12,
            fg_color=("#F1F5F9", "#1E293B"),
            border_width=1,
            border_color=("#E2E8F0", "#334155"),
        )
        self.song_sidebar.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        ctk.CTkLabel(
            self.song_sidebar,
            text="Peças Disponíveis",
            font=ctk.CTkFont(family="Helvetica", size=14, weight="bold"),
            text_color=("#0F172A", "#F8FAFC"),
        ).pack(anchor="w", padx=10, pady=(8, 8))

        self.song_buttons: List[ctk.CTkButton] = []
        for s in SONG_LIBRARY:
            btn = ctk.CTkButton(
                self.song_sidebar,
                text=f"{s.title}\n{s.composer} ({s.difficulty})",
                font=ctk.CTkFont(family="Helvetica", size=11),
                anchor="w",
                height=48,
                corner_radius=8,
                fg_color=("#E2E8F0", "#0F172A"),
                text_color=("#1E293B", "#E2E8F0"),
                hover_color=("#CBD5E1", "#334155"),
                command=lambda chosen=s: self._load_song(chosen),
            )
            btn.pack(fill="x", padx=6, pady=3)
            self.song_buttons.append(btn)

        # 2.2 Active Song Studio Stage
        self.stage_scroll = ctk.CTkScrollableFrame(
            main_layout,
            corner_radius=12,
            fg_color=("#F8FAFC", "#0F172A"),
            border_width=1,
            border_color=("#E2E8F0", "#334155"),
        )
        self.stage_scroll.grid(row=0, column=1, sticky="nsew")

        self._build_stage_ui()

    def _build_stage_ui(self):
        # Header Info Card
        self.info_card = ctk.CTkFrame(
            self.stage_scroll,
            corner_radius=12,
            fg_color=("#F1F5F9", "#1E293B"),
            border_width=1,
            border_color=("#E2E8F0", "#334155"),
        )
        self.info_card.pack(fill="x", padx=6, pady=(0, 8))

        top_info = ctk.CTkFrame(self.info_card, fg_color="transparent")
        top_info.pack(fill="x", padx=14, pady=(10, 2))

        self.song_title_lbl = ctk.CTkLabel(
            top_info,
            text="",
            font=ctk.CTkFont(family="Helvetica", size=18, weight="bold"),
            text_color=("#0F172A", "#F8FAFC"),
        )
        self.song_title_lbl.pack(side="left")

        self.song_meta_lbl = ctk.CTkLabel(
            top_info,
            text="",
            font=ctk.CTkFont(family="Helvetica", size=12, weight="bold"),
            text_color=("#64748B", "#94A3B8"),
        )
        self.song_meta_lbl.pack(side="right")

        self.song_desc_lbl = ctk.CTkLabel(
            self.info_card,
            text="",
            font=ctk.CTkFont(family="Helvetica", size=12),
            text_color=("#475569", "#CBD5E1"),
            wraplength=640,
            justify="left",
        )
        self.song_desc_lbl.pack(anchor="w", padx=14, pady=(0, 10))

        # Playback Controls Bar
        ctrl_bar = ctk.CTkFrame(
            self.stage_scroll,
            corner_radius=10,
            fg_color=("#F1F5F9", "#1E293B"),
            border_width=1,
            border_color=("#E2E8F0", "#334155"),
        )
        ctrl_bar.pack(fill="x", padx=6, pady=(0, 8))

        # Mode Buttons
        self.play_demo_btn = ctk.CTkButton(
            ctrl_bar,
            text="▶ Ouvir Demonstração",
            font=ctk.CTkFont(family="Helvetica", size=12, weight="bold"),
            fg_color="#059669",
            hover_color="#047857",
            width=160,
            command=self._toggle_demo_playback,
        )
        self.play_demo_btn.pack(side="left", padx=10, pady=8)

        self.prev_note_btn = ctk.CTkButton(
            ctrl_bar,
            text="⏮ Nota Anterior",
            font=ctk.CTkFont(family="Helvetica", size=12),
            fg_color="#475569",
            hover_color="#334155",
            width=120,
            command=self._prev_note,
        )
        self.prev_note_btn.pack(side="left", padx=4)

        self.next_note_btn = ctk.CTkButton(
            ctrl_bar,
            text="Nota Seguinte ⏭",
            font=ctk.CTkFont(family="Helvetica", size=12, weight="bold"),
            fg_color="#2563EB",
            hover_color="#1D4ED8",
            width=130,
            command=self._next_note,
        )
        self.next_note_btn.pack(side="left", padx=4)

        self.replay_current_btn = ctk.CTkButton(
            ctrl_bar,
            text="🔊 Tocar Esta Nota",
            font=ctk.CTkFont(family="Helvetica", size=12),
            fg_color="#7C3AED",
            hover_color="#6D28D9",
            width=130,
            command=self._play_current_active_note,
        )
        self.replay_current_btn.pack(side="left", padx=6)

        # Active Note Instruction Banner (Dedo & Traste)
        self.instruction_banner = ctk.CTkFrame(
            self.stage_scroll,
            corner_radius=10,
            fg_color=("#DCFCE7", "#064E3B"),
            border_width=1,
            border_color="#10B981",
        )
        self.instruction_banner.pack(fill="x", padx=6, pady=(0, 8))

        self.note_guide_lbl = ctk.CTkLabel(
            self.instruction_banner,
            text="",
            font=ctk.CTkFont(family="Helvetica", size=15, weight="bold"),
            text_color=("#065F46", "#ECFDF5"),
        )
        self.note_guide_lbl.pack(padx=16, pady=10)

        # Visualizers Container
        vis_container = ctk.CTkFrame(self.stage_scroll, fg_color="transparent")
        vis_container.pack(fill="x", padx=6, pady=2)

        # 1. Staff Canvas
        self.staff_view = StaffCanvas(vis_container, width=650, height=150, clef="treble", show_note_names=True)
        self.staff_view.pack(pady=4)

        # 2. Piano Keyboard (Interactive)
        self.piano_view = PianoKeyboard(
            vis_container,
            start_octave=3,
            num_octaves=2,
            key_width=42,
            key_height=125,
            on_key_click=self._on_user_piano_click,
        )
        self.piano_view.pack(pady=4)

        # 3. Guitar / Viola Fretboard (Interactive)
        self.guitar_view = GuitarFretboard(
            vis_container,
            width=650,
            height=155,
            num_frets=15,
            on_note_clicked=self._on_user_guitar_click,
        )
        self.guitar_view.pack(pady=4)

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
        self._highlight_active_note()

    def _load_song(self, song: Song):
        self._stop_demo_playback()
        self.current_song = song
        self.current_note_idx = 0

        # Update Sidebar button styles
        for i, btn in enumerate(self.song_buttons):
            if SONG_LIBRARY[i].id == song.id:
                btn.configure(
                    fg_color="#2563EB",
                    text_color="#FFFFFF",
                    hover_color="#1D4ED8",
                    font=ctk.CTkFont(family="Helvetica", size=11, weight="bold"),
                )
            else:
                btn.configure(
                    fg_color=("#E2E8F0", "#0F172A"),
                    text_color=("#1E293B", "#E2E8F0"),
                    hover_color=("#CBD5E1", "#334155"),
                    font=ctk.CTkFont(family="Helvetica", size=11, weight="normal"),
                )

        # Update Info Card
        self.song_title_lbl.configure(text=f"{song.title} — {song.composer}")
        self.song_meta_lbl.configure(text=f"Dificuldade: {song.difficulty} • BPM: {song.bpm} • {song.note_count} Notas")
        self.song_desc_lbl.configure(text=song.description)

        # Update Staff clef
        self.staff_view.clef = song.clef

        self._highlight_active_note()

    def _highlight_active_note(self):
        if not self.current_song or not self.current_song.notes:
            return

        idx = self.current_note_idx
        sn = self.current_song.notes[idx]
        note = sn.note

        # 1. Update Staff Display
        self.staff_view.set_single_note(note, color="#10B981")

        # 2. Update Piano Display with Fingering Number
        piano_fingering = {}
        if sn.piano_finger is not None:
            piano_fingering[note.midi] = sn.piano_finger

        self.piano_view.highlight_notes([note], color="#10B981")
        self.piano_view.set_fingering(piano_fingering)

        # 3. Update Guitar / Viola Display with String & Fret
        self.guitar_view.highlight_positions = {}
        self.guitar_view.current_chord_shape = None
        self.guitar_view.highlighted_positions.clear()

        if sn.guitar_string is not None and sn.guitar_fret is not None:
            self.guitar_view.highlighted_positions[(sn.guitar_string, sn.guitar_fret)] = {
                "color": "#10B981",
                "label": note.pitch,
                "is_root": True,
                "note": note,
            }
        else:
            # Highlight all matches of this pitch
            self.guitar_view.highlight_scale([note])

        self.guitar_view.redraw()

        # 4. Update Guidance Text Banner
        finger_str = f"Dedo {sn.piano_finger} (Mão {sn.piano_hand.capitalize()})" if sn.piano_finger else "Dedo Livre"
        guitar_pos_str = f"{sn.guitar_string + 1}ª Corda, Traste {sn.guitar_fret}" if (sn.guitar_string is not None and sn.guitar_fret is not None) else "Ver no braço"
        syllable = f" «{sn.lyric_syllable}»" if sn.lyric_syllable else ""

        banner_text = (
            f"Nota {idx + 1}/{self.current_song.note_count}: {note.pitch} ({note.name_pt}){syllable}  |  "
            f"🎹 Piano: {finger_str}  |  🎸 Viola: {guitar_pos_str}"
        )
        self.note_guide_lbl.configure(text=banner_text)

    def _play_current_active_note(self):
        if not self.current_song or not self.current_song.notes:
            return
        sn = self.current_song.notes[self.current_note_idx]
        duration = max(0.4, (60.0 / self.current_song.bpm) * sn.duration_beats)
        self.audio_player.play_note(sn.note, duration=duration)

    def _next_note(self):
        if not self.current_song:
            return
        if self.current_note_idx < len(self.current_song.notes) - 1:
            self.current_note_idx += 1
            self._highlight_active_note()
            self._play_current_active_note()

    def _prev_note(self):
        if not self.current_song:
            return
        if self.current_note_idx > 0:
            self.current_note_idx -= 1
            self._highlight_active_note()
            self._play_current_active_note()

    def _on_user_piano_click(self, clicked_note: Note):
        """Called when student clicks a key on the piano keyboard."""
        if self.is_playing_demo or not self.current_song:
            return

        expected_note = self.current_song.notes[self.current_note_idx].note
        if clicked_note.normalized_pitch == expected_note.normalized_pitch:
            # Correct! Advance to next note
            if self.current_note_idx < len(self.current_song.notes) - 1:
                self.after(250, self._advance_on_correct)
            else:
                self.note_guide_lbl.configure(
                    text=f"🎉 Parabéns! Concluíste a música «{self.current_song.title}» com sucesso!",
                    text_color="#10B981",
                )

    def _on_user_guitar_click(self, clicked_note: Note):
        """Called when student clicks a string/fret on the guitar fretboard."""
        if self.is_playing_demo or not self.current_song:
            return

        expected_note = self.current_song.notes[self.current_note_idx].note
        if clicked_note.normalized_pitch == expected_note.normalized_pitch:
            if self.current_note_idx < len(self.current_song.notes) - 1:
                self.after(250, self._advance_on_correct)
            else:
                self.note_guide_lbl.configure(
                    text=f"🎉 Parabéns! Concluíste a música «{self.current_song.title}» com sucesso!",
                    text_color="#10B981",
                )

    def _advance_on_correct(self):
        if not self.winfo_exists():
            return
        if self.current_note_idx < len(self.current_song.notes) - 1:
            self.current_note_idx += 1
            self._highlight_active_note()

    def _toggle_demo_playback(self):
        if self.is_playing_demo:
            self._stop_demo_playback()
        else:
            self._start_demo_playback()

    def _start_demo_playback(self):
        self.is_playing_demo = True
        self.play_demo_btn.configure(
            text="⏸ Pausar Demonstração",
            fg_color="#DC2626",
            hover_color="#B91C1C",
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
            fg_color="#059669",
            hover_color="#047857",
        )

    def _schedule_next_demo_note(self):
        if not self.is_playing_demo or not self.winfo_exists() or not self.current_song:
            return

        if self.current_note_idx >= len(self.current_song.notes):
            self._stop_demo_playback()
            return

        sn = self.current_song.notes[self.current_note_idx]
        beat_duration_sec = 60.0 / self.current_song.bpm
        note_duration_sec = beat_duration_sec * sn.duration_beats

        self._highlight_active_note()
        self.audio_player.play_note(sn.note, duration=note_duration_sec * 0.9)

        # Advance index for next trigger
        self.current_note_idx += 1
        delay_ms = int(note_duration_sec * 1000)

        self._demo_timer_id = self.after(delay_ms, self._schedule_next_demo_note)

    def _handle_back(self):
        self._stop_demo_playback()
        self.audio_player.stop_all()
        self.on_back()
