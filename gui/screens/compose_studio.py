"""Composition Studio Screen (Phase 43) with interactive step sequencer, chord track, and dual piano/guitar visualizers."""
import threading
from tkinter import messagebox
from typing import Callable, Dict, List, Optional
import customtkinter as ctk
import numpy as np
from core.composition import Composition, ChordEvent, RhythmTrack
from core.compositions import (
    get_template_composition,
    save_user_composition,
    load_user_compositions,
    delete_user_composition,
)
from core.user_manager import UserManager
from core.chords import CHORD_TYPES, get_chord_notes
from core.guitar import GUITAR_CHORD_LIBRARY, GuitarChordShape
from core.notes import Note
from audio.composition_renderer import CompositionRenderer
from audio.backing_tracks import BACKING_TRACK_LIBRARY
from audio.player import get_audio_player
from gui.components.step_grid import StepGrid
from gui.components.piano_keyboard import PianoKeyboard
from gui.components.guitar_fretboard import GuitarFretboard
from gui.scroll_utils import bind_mousewheel
from gui.i18n import t, get_language
from gui import theme

try:
    import pygame
    HAS_PYGAME = True
except ImportError:
    HAS_PYGAME = False

# 17 standard musical roots covering naturals, sharps, and flats
ROOT_OPTIONS = ["C", "C#", "Db", "D", "D#", "Eb", "E", "F", "F#", "Gb", "G", "G#", "Ab", "A", "A#", "Bb", "B"]


class ComposeStudioScreen(ctk.CTkFrame):
    """
    Interactive Studio for creating and editing multi-track musical compositions:
    - 16-step percussion canvas sequencer
    - Harmonic chord track (Piano & Viola) with full 22 CHORD_TYPES and 17 root notes
    - Synchronized dual interactive visualizers (PianoKeyboard + GuitarFretboard)
    - Jitter-free offline audio rendering with background worker thread
    """

    def __init__(
        self,
        master,
        user_manager: UserManager,
        on_back: Callable[[], None],
        initial_composition: Optional[Composition] = None,
        **kwargs,
    ):
        super().__init__(master, fg_color=theme.COLOR_BG, **kwargs)
        self.user_manager = user_manager
        self.on_back = on_back
        self.audio_player = get_audio_player()
        self.renderer = CompositionRenderer(sample_rate=44100)
        self.lang = get_language()

        # Active composition state
        self.composition = initial_composition or get_template_composition("rock_basic")
        self.selected_chord_idx: Optional[int] = None
        self.is_playing = False
        self._current_sound = None
        self._render_thread: Optional[threading.Thread] = None

        self._build_ui()

    def _build_ui(self):
        # 1. Top Navigation & Transport Bar
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
            command=self._on_back_clicked,
        )
        back_btn.pack(side="left")

        title_lbl = ctk.CTkLabel(
            nav_bar,
            text=f"🎛️ {t('compose_title', 'Estúdio de Composição')}",
            font=theme.get_font(theme.FONT_TITLE),
            text_color=theme.COLOR_TEXT_PRIMARY,
        )
        title_lbl.pack(side="left", padx=16)

        # 2. Main Scrollable Container (Single non-recursive mousewheel)
        self.scroll_container = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            corner_radius=theme.RADIUS_LG,
        )
        self.scroll_container.pack(fill="both", expand=True, padx=20, pady=(0, 16))
        bind_mousewheel(self.scroll_container, recursive=False)

        # 3. Transport & Global Settings Card
        transport_card = ctk.CTkFrame(
            self.scroll_container,
            corner_radius=theme.RADIUS_LG,
            fg_color=theme.COLOR_SURFACE,
            border_width=1,
            border_color=theme.COLOR_BORDER,
        )
        transport_card.pack(fill="x", pady=(4, 10))

        t_row = ctk.CTkFrame(transport_card, fg_color="transparent")
        t_row.pack(fill="x", padx=16, pady=12)

        # Title Input
        ctk.CTkLabel(
            t_row, text="Título:", font=theme.get_font(theme.FONT_BODY_BOLD), text_color=theme.COLOR_TEXT_PRIMARY
        ).pack(side="left", padx=(0, 6))
        self.title_entry = ctk.CTkEntry(
            t_row, width=180, height=34, font=theme.get_font(theme.FONT_BODY), corner_radius=theme.RADIUS_SM
        )
        self.title_entry.insert(0, self.composition.title)
        self.title_entry.pack(side="left", padx=(0, 14))
        self.title_entry.bind("<FocusOut>", lambda e: self._on_title_changed())

        # Play / Stop Button
        self.play_btn = ctk.CTkButton(
            t_row,
            text="▶ Ouvir Composição",
            font=theme.get_font(theme.FONT_BODY_BOLD),
            fg_color=theme.COLOR_SUCCESS,
            hover_color=theme.COLOR_SUCCESS_HOVER,
            width=165,
            height=36,
            corner_radius=theme.RADIUS_MD,
            command=self._toggle_playback,
        )
        self.play_btn.pack(side="left", padx=(0, 14))

        # BPM Slider & Label
        ctk.CTkLabel(
            t_row, text="BPM:", font=theme.get_font(theme.FONT_BODY_BOLD), text_color=theme.COLOR_TEXT_PRIMARY
        ).pack(side="left", padx=(0, 6))
        self.bpm_slider = ctk.CTkSlider(
            t_row,
            from_=40,
            to=220,
            number_of_steps=180,
            width=110,
            command=self._on_bpm_slider_changed,
        )
        self.bpm_slider.set(self.composition.bpm)
        self.bpm_slider.pack(side="left", padx=(0, 6))
        self.bpm_val_lbl = ctk.CTkLabel(
            t_row, text=f"{self.composition.bpm}", font=theme.get_font(theme.FONT_BODY_BOLD), text_color="#38BDF8", width=32
        )
        self.bpm_val_lbl.pack(side="left", padx=(0, 14))

        # Bars Selector
        ctk.CTkLabel(
            t_row, text="Compassos:", font=theme.get_font(theme.FONT_BODY_BOLD), text_color=theme.COLOR_TEXT_PRIMARY
        ).pack(side="left", padx=(0, 6))
        self.bars_menu = ctk.CTkOptionMenu(
            t_row,
            values=["2", "4", "8", "16"],
            width=65,
            height=32,
            font=theme.get_font(theme.FONT_BODY_BOLD),
            command=self._on_bars_changed,
        )
        self.bars_menu.set(str(self.composition.bars))
        self.bars_menu.pack(side="left", padx=(0, 14))

        # Save Button
        save_btn = ctk.CTkButton(
            t_row,
            text="💾 Guardar",
            font=theme.get_font(theme.FONT_BODY_BOLD),
            fg_color=theme.COLOR_PRIMARY,
            hover_color=theme.COLOR_PRIMARY_HOVER,
            width=95,
            height=34,
            corner_radius=theme.RADIUS_MD,
            command=self._save_composition,
        )
        save_btn.pack(side="right")

        # 4. Preset Presets Row & Storage Bar
        presets_card = ctk.CTkFrame(
            self.scroll_container,
            corner_radius=theme.RADIUS_LG,
            fg_color=theme.COLOR_SURFACE,
            border_width=1,
            border_color=theme.COLOR_BORDER,
        )
        presets_card.pack(fill="x", pady=(0, 10))

        p_row = ctk.CTkFrame(presets_card, fg_color="transparent")
        p_row.pack(fill="x", padx=16, pady=10)

        ctk.CTkLabel(
            p_row, text="Modelos de Ritmo:", font=theme.get_font(theme.FONT_BODY_BOLD), text_color=theme.COLOR_TEXT_PRIMARY
        ).pack(side="left", padx=(0, 8))

        preset_options = [f"{p.name_pt} ({pid})" for pid, p in BACKING_TRACK_LIBRARY.items()]
        self.presets_menu = ctk.CTkOptionMenu(
            p_row,
            values=preset_options,
            width=230,
            height=32,
            font=theme.get_font(theme.FONT_SMALL),
            command=self._on_preset_selected,
        )
        self.presets_menu.set("Escolher Ritmo Base...")
        self.presets_menu.pack(side="left", padx=(0, 12))

        # Load Saved Compositions
        self.saved_menu = ctk.CTkOptionMenu(
            p_row,
            values=self._get_saved_titles(),
            width=210,
            height=32,
            font=theme.get_font(theme.FONT_SMALL),
            command=self._on_saved_composition_selected,
        )
        self.saved_menu.set("📂 Minhas Composições...")
        self.saved_menu.pack(side="left", padx=(0, 12))

        # Clear Grid Button
        clear_btn = ctk.CTkButton(
            p_row,
            text="🗑️ Limpar Ritmo",
            font=theme.get_font(theme.FONT_SMALL),
            fg_color=theme.COLOR_SURFACE_SECONDARY,
            hover_color=theme.COLOR_BORDER,
            text_color=theme.COLOR_TEXT_PRIMARY,
            width=105,
            height=32,
            corner_radius=theme.RADIUS_SM,
            command=self._clear_grid,
        )
        clear_btn.pack(side="right")

        # 5. Interactive Rhythm Step Grid Card
        grid_card = ctk.CTkFrame(
            self.scroll_container,
            corner_radius=theme.RADIUS_LG,
            fg_color=theme.COLOR_SURFACE,
            border_width=1,
            border_color=theme.COLOR_BORDER,
        )
        grid_card.pack(fill="both", expand=True, pady=(0, 12))

        grid_header = ctk.CTkFrame(grid_card, fg_color="transparent")
        grid_header.pack(fill="x", padx=16, pady=(10, 4))

        ctk.CTkLabel(
            grid_header,
            text="🥁 Faixa de Percussão (Sequenciador 16 Passos)",
            font=theme.get_font(theme.FONT_SECTION),
            text_color=theme.COLOR_TEXT_PRIMARY,
        ).pack(side="left")

        ctk.CTkLabel(
            grid_header,
            text="💡 Clica para ativar/desativar cada batida.",
            font=theme.get_font(theme.FONT_SMALL),
            text_color=theme.COLOR_TEXT_MUTED,
        ).pack(side="right")

        # Step Grid Canvas Component (Unified Multi-bar Rhythm & Chord Timeline)
        steps = self.composition.rhythm.steps_per_bar if self.composition.rhythm else 16
        bars = self.composition.bars
        grid_data = self.composition.rhythm.grid if self.composition.rhythm else []
        self.step_grid = StepGrid(
            grid_card,
            grid=grid_data,
            chords=self.composition.chords,
            steps_per_bar=steps,
            bars=bars,
            time_signature=self.composition.time_signature,
            selected_chord_idx=self.selected_chord_idx,
            on_grid_change=self._on_grid_updated,
            on_chord_click=self._select_chord,
            on_chord_lane_click=self._on_chord_lane_clicked,
        )
        self.step_grid.pack(fill="both", expand=True, padx=14, pady=(4, 12))

        # 6. Harmonic Chords Track & Editor Card
        self.chords_card = ctk.CTkFrame(
            self.scroll_container,
            corner_radius=theme.RADIUS_LG,
            fg_color=theme.COLOR_SURFACE,
            border_width=1,
            border_color=theme.COLOR_BORDER,
        )
        self.chords_card.pack(fill="both", expand=True, pady=(0, 12))
        self._build_chords_section()

        # 7. Interactive Instrument Visualizers Card (Piano & Viola)
        vis_card = ctk.CTkFrame(
            self.scroll_container,
            corner_radius=theme.RADIUS_LG,
            fg_color=theme.COLOR_SURFACE,
            border_width=1,
            border_color=theme.COLOR_BORDER,
        )
        vis_card.pack(fill="both", expand=True, pady=(0, 16))
        self._build_visualizers_section(vis_card)

    def _build_chords_section(self):
        """Builds the chord sequencer list and chord creation controls."""
        header = ctk.CTkFrame(self.chords_card, fg_color="transparent")
        header.pack(fill="x", padx=16, pady=(12, 6))

        ctk.CTkLabel(
            header,
            text="🎹 Faixa Harmónica (Acordes de Piano e Viola)",
            font=theme.get_font(theme.FONT_SECTION),
            text_color=theme.COLOR_TEXT_PRIMARY,
        ).pack(side="left")

        ctk.CTkLabel(
            header,
            text="💡 Seleciona um acorde para visualizar a digitação no Piano e no Braço da Viola.",
            font=theme.get_font(theme.FONT_SMALL),
            text_color=theme.COLOR_TEXT_MUTED,
        ).pack(side="right")

        # Chord Control Strip (Add/Edit)
        ctrl_strip = ctk.CTkFrame(self.chords_card, fg_color=theme.COLOR_SURFACE_SECONDARY, corner_radius=theme.RADIUS_MD)
        ctrl_strip.pack(fill="x", padx=14, pady=(0, 8))

        c_inner = ctk.CTkFrame(ctrl_strip, fg_color="transparent")
        c_inner.pack(fill="x", padx=12, pady=8)

        # Root Selector (17 roots)
        ctk.CTkLabel(c_inner, text="Tónica:", font=theme.get_font(theme.FONT_SMALL_BOLD)).pack(side="left", padx=(0, 4))
        self.root_menu = ctk.CTkOptionMenu(
            c_inner,
            values=ROOT_OPTIONS,
            width=70,
            height=30,
            font=theme.get_font(theme.FONT_BODY_BOLD),
        )
        self.root_menu.set("C")
        self.root_menu.pack(side="left", padx=(0, 10))

        # Chord Type Selector (22 types)
        ctk.CTkLabel(c_inner, text="Tipo:", font=theme.get_font(theme.FONT_SMALL_BOLD)).pack(side="left", padx=(0, 4))
        chord_type_labels = [f"{cd.key} ({cd.name_pt})" for cd in CHORD_TYPES.values()]
        self.chord_type_menu = ctk.CTkOptionMenu(
            c_inner,
            values=chord_type_labels,
            width=180,
            height=30,
            font=theme.get_font(theme.FONT_SMALL),
        )
        self.chord_type_menu.set("major (Tríade Maior)")
        self.chord_type_menu.pack(side="left", padx=(0, 10))

        # Instrument Selector
        ctk.CTkLabel(c_inner, text="Instrumento:", font=theme.get_font(theme.FONT_SMALL_BOLD)).pack(side="left", padx=(0, 4))
        self.inst_menu = ctk.CTkOptionMenu(
            c_inner,
            values=["🎹 Piano", "🎸 Viola"],
            width=110,
            height=30,
            font=theme.get_font(theme.FONT_SMALL),
        )
        self.inst_menu.set("🎹 Piano")
        self.inst_menu.pack(side="left", padx=(0, 10))

        # Start Beat
        ctk.CTkLabel(c_inner, text="Tempo:", font=theme.get_font(theme.FONT_SMALL_BOLD)).pack(side="left", padx=(0, 4))
        self.start_beat_menu = ctk.CTkOptionMenu(
            c_inner,
            values=[str(float(b)) for b in range(16)],
            width=70,
            height=30,
            font=theme.get_font(theme.FONT_SMALL),
        )
        self.start_beat_menu.set("0.0")
        self.start_beat_menu.pack(side="left", padx=(0, 10))

        # Duration Beats
        ctk.CTkLabel(c_inner, text="Duração:", font=theme.get_font(theme.FONT_SMALL_BOLD)).pack(side="left", padx=(0, 4))
        self.dur_menu = ctk.CTkOptionMenu(
            c_inner,
            values=["1.0", "2.0", "3.0", "4.0", "8.0"],
            width=70,
            height=30,
            font=theme.get_font(theme.FONT_SMALL),
        )
        self.dur_menu.set("4.0")
        self.dur_menu.pack(side="left", padx=(0, 12))

        # Add Chord Button
        add_chord_btn = ctk.CTkButton(
            c_inner,
            text="➕ Adicionar Acorde",
            font=theme.get_font(theme.FONT_BODY_BOLD),
            fg_color=theme.COLOR_PRIMARY,
            hover_color=theme.COLOR_PRIMARY_HOVER,
            width=140,
            height=32,
            corner_radius=theme.RADIUS_SM,
            command=self._add_chord_event,
        )
        add_chord_btn.pack(side="left")

        # Scrollable Chord Events List Frame
        self.chords_list_frame = ctk.CTkFrame(self.chords_card, fg_color="transparent")
        self.chords_list_frame.pack(fill="x", padx=14, pady=(4, 14))
        self._refresh_chords_list()

    def _refresh_chords_list(self):
        for widget in self.chords_list_frame.winfo_children():
            widget.destroy()

        if not self.composition.chords:
            ctk.CTkLabel(
                self.chords_list_frame,
                text="Sem acordes adicionados nesta composição. Adiciona acordes acima para harmonizar o teu ritmo!",
                font=theme.get_font(theme.FONT_BODY),
                text_color=theme.COLOR_TEXT_MUTED,
            ).pack(pady=10)
            return

        # Sort chords by start beat
        self.composition.chords.sort(key=lambda c: c.start_beat)

        # Draw chord event cards in a horizontal-flow grid
        row_frame = ctk.CTkFrame(self.chords_list_frame, fg_color="transparent")
        row_frame.pack(fill="x", pady=2)

        for idx, chord in enumerate(self.composition.chords):
            is_selected = (self.selected_chord_idx == idx)
            card_bg = theme.COLOR_PRIMARY if is_selected else theme.COLOR_SURFACE_SECONDARY
            text_col = "#FFFFFF" if is_selected else theme.COLOR_TEXT_PRIMARY

            chord_box = ctk.CTkFrame(
                row_frame,
                fg_color=card_bg,
                corner_radius=theme.RADIUS_MD,
                border_width=1,
                border_color=theme.COLOR_PRIMARY if not is_selected else "#FFFFFF",
            )
            chord_box.pack(side="left", padx=4, pady=4)

            # Click to select & inspect
            chord_box.bind("<Button-1>", lambda e, i=idx: self._select_chord(i))

            c_info = ctk.CTkFrame(chord_box, fg_color="transparent")
            c_info.pack(padx=8, pady=6)
            c_info.bind("<Button-1>", lambda e, i=idx: self._select_chord(i))

            inst_icon = "🎹" if chord.instrument == "piano" else "🎸"
            chord_lbl = ctk.CTkLabel(
                c_info,
                text=f"{inst_icon} {chord.root}{CHORD_TYPES.get(chord.chord_type, CHORD_TYPES['major']).symbol or chord.chord_type}",
                font=theme.get_font(theme.FONT_BODY_BOLD),
                text_color=text_col,
            )
            chord_lbl.pack(anchor="w")
            chord_lbl.bind("<Button-1>", lambda e, i=idx: self._select_chord(i))

            timing_lbl = ctk.CTkLabel(
                c_info,
                text=f"T:{chord.start_beat:.1f} ({chord.duration_beats:.1f}t)",
                font=theme.get_font(theme.FONT_SMALL),
                text_color="#CBD5E1" if is_selected else theme.COLOR_TEXT_MUTED,
            )
            timing_lbl.pack(anchor="w")
            timing_lbl.bind("<Button-1>", lambda e, i=idx: self._select_chord(i))

            # Delete button
            del_btn = ctk.CTkButton(
                c_info,
                text="✕",
                width=22,
                height=20,
                font=("Helvetica", 10, "bold"),
                fg_color="transparent",
                hover_color=theme.COLOR_ACCENT_CRIMSON,
                text_color="#EF4444" if not is_selected else "#FFFFFF",
                command=lambda i=idx: self._delete_chord(i),
            )
            del_btn.pack(anchor="e", pady=(2, 0))

    def _build_visualizers_section(self, parent):
        """Builds synchronized Piano Keyboard and Guitar Fretboard widgets."""
        header = ctk.CTkFrame(parent, fg_color="transparent")
        header.pack(fill="x", padx=16, pady=(12, 6))

        ctk.CTkLabel(
            header,
            text="🎼 Visualizadores de Instrumento (Sincronizados com o Acorde Ativo)",
            font=theme.get_font(theme.FONT_SECTION),
            text_color=theme.COLOR_TEXT_PRIMARY,
        ).pack(side="left")

        # Visualizer tabs / toggle
        self.vis_selector = ctk.CTkSegmentedButton(
            header,
            values=["🎹 Piano", "🎸 Viola", "👥 Ambos"],
            font=theme.get_font(theme.FONT_SMALL_BOLD),
            command=self._on_vis_mode_changed,
        )
        self.vis_selector.set("👥 Ambos")
        self.vis_selector.pack(side="right")

        # Piano Container
        self.piano_container = ctk.CTkFrame(parent, fg_color="transparent")
        self.piano_container.pack(fill="x", padx=14, pady=(4, 8))

        ctk.CTkLabel(
            self.piano_container,
            text="🎹 Teclado de Piano (Notas & Digitação do Acorde):",
            font=theme.get_font(theme.FONT_BODY_BOLD),
            text_color=theme.COLOR_TEXT_PRIMARY,
        ).pack(anchor="w", padx=4, pady=(0, 4))

        self.piano_widget = PianoKeyboard(
            self.piano_container,
            start_octave=3,
            num_octaves=2,
            key_width=38,
            key_height=125,
            show_labels=True,
            enable_audio=True,
        )
        self.piano_widget.pack(anchor="center", pady=2)

        # Guitar Container
        self.guitar_container = ctk.CTkFrame(parent, fg_color="transparent")
        self.guitar_container.pack(fill="x", padx=14, pady=(4, 14))

        ctk.CTkLabel(
            self.guitar_container,
            text="🎸 Braço da Viola / Guitarra (Posição CAGED & Trastes):",
            font=theme.get_font(theme.FONT_BODY_BOLD),
            text_color=theme.COLOR_TEXT_PRIMARY,
        ).pack(anchor="w", padx=4, pady=(0, 4))

        self.guitar_widget = GuitarFretboard(
            self.guitar_container,
            width=680,
            height=145,
            num_frets=12,
            enable_audio=True,
        )
        self.guitar_widget.pack(anchor="center", pady=2)

    def _on_vis_mode_changed(self, value: str):
        if value == "🎹 Piano":
            self.piano_container.pack(fill="x", padx=14, pady=(4, 8))
            self.guitar_container.pack_forget()
        elif value == "🎸 Viola":
            self.piano_container.pack_forget()
            self.guitar_container.pack(fill="x", padx=14, pady=(4, 14))
        else:
            self.piano_container.pack(fill="x", padx=14, pady=(4, 8))
            self.guitar_container.pack(fill="x", padx=14, pady=(4, 14))

    def _add_chord_event(self):
        root = self.root_menu.get()
        raw_type = self.chord_type_menu.get().split()[0]
        inst_label = self.inst_menu.get()
        instrument = "piano" if "Piano" in inst_label else "guitar"
        start_beat = float(self.start_beat_menu.get())
        duration_beats = float(self.dur_menu.get())

        event = ChordEvent(
            root=root,
            chord_type=raw_type,
            start_beat=start_beat,
            duration_beats=duration_beats,
            instrument=instrument,
        )
        self.composition.chords.append(event)
        self._refresh_chords_list()
        self.selected_chord_idx = self.composition.chords.index(event) if event in self.composition.chords else 0
        self.step_grid.set_chords(self.composition.chords, self.selected_chord_idx)
        self._update_visualizers_for_chord(event)

        # Advance start beat suggestion by duration
        next_beat = start_beat + duration_beats
        if str(next_beat) in self.start_beat_menu._values:
            self.start_beat_menu.set(str(next_beat))

    def _on_chord_lane_clicked(self, instrument: str, beat: float):
        """Called when clicking on an empty area of the chord timeline canvas."""
        root = self.root_menu.get()
        raw_type = self.chord_type_menu.get().split()[0]
        duration_beats = float(self.dur_menu.get())

        event = ChordEvent(
            root=root,
            chord_type=raw_type,
            start_beat=beat,
            duration_beats=duration_beats,
            instrument=instrument,
        )
        self.composition.chords.append(event)
        self._refresh_chords_list()
        self.selected_chord_idx = self.composition.chords.index(event) if event in self.composition.chords else 0
        self.step_grid.set_chords(self.composition.chords, self.selected_chord_idx)
        self._update_visualizers_for_chord(event)

    def _delete_chord(self, index: int):
        if 0 <= index < len(self.composition.chords):
            self.composition.chords.pop(index)
            if self.selected_chord_idx == index:
                self.selected_chord_idx = None
                self.piano_widget.clear_highlights()
                self.guitar_widget.clear_highlights()
            elif self.selected_chord_idx is not None and self.selected_chord_idx > index:
                self.selected_chord_idx -= 1
            self._refresh_chords_list()
            self.step_grid.set_chords(self.composition.chords, self.selected_chord_idx)

    def _select_chord(self, index: int):
        self.selected_chord_idx = index
        self._refresh_chords_list()
        self.step_grid.set_chords(self.composition.chords, self.selected_chord_idx)
        if 0 <= index < len(self.composition.chords):
            chord = self.composition.chords[index]
            self._update_visualizers_for_chord(chord)

    def _update_visualizers_for_chord(self, chord: ChordEvent):
        """Highlights chord notes and CAGED positions on Piano and Guitar visualizers."""
        try:
            notes = get_chord_notes(chord.root, chord.chord_type)
        except Exception:
            notes = [Note(chord.root, 4)]

        # 1. Update Piano Keyboard
        self.piano_widget.highlight_notes(notes, color=theme.COLOR_PRIMARY)

        # 2. Update Guitar Fretboard with CAGED chord shape if available
        # Check direct key (e.g. "Am", "C7", "C", "Cmaj7") or root list
        shapes = GUITAR_CHORD_LIBRARY.get(chord.root, [])
        matching_shape = next((s for s in shapes if s.chord_type == chord.chord_type), None)
        if not matching_shape:
            sym = CHORD_TYPES.get(chord.chord_type, CHORD_TYPES["major"]).symbol
            combined_key = f"{chord.root}{sym}"
            shapes_comb = GUITAR_CHORD_LIBRARY.get(combined_key, [])
            if shapes_comb:
                matching_shape = shapes_comb[0]

        if matching_shape:
            self.guitar_widget.set_chord_shape(matching_shape)
        else:
            # Fallback to highlighting chord notes across the fretboard
            self.guitar_widget.highlight_scale(notes)

    def _get_saved_titles(self) -> List[str]:
        comps = load_user_compositions()
        if not comps:
            return ["(Nenhuma composição guardada)"]
        return [f"{c.title} ({c.id})" for c in comps]

    def _on_grid_updated(self, new_grid: List[List[str]]):
        self.composition.rhythm.grid = new_grid

    def _on_title_changed(self):
        new_title = self.title_entry.get().strip()
        if new_title:
            self.composition.title = new_title

    def _on_bpm_slider_changed(self, value):
        bpm = int(value)
        self.composition.bpm = bpm
        self.bpm_val_lbl.configure(text=f"{bpm}")

    def _on_bars_changed(self, value: str):
        new_bars = int(value)
        old_bars = self.composition.bars
        steps_per_bar = self.composition.rhythm.steps_per_bar if self.composition.rhythm else 16
        old_total_steps = old_bars * steps_per_bar
        new_total_steps = new_bars * steps_per_bar

        if new_bars < old_bars:
            # Check if user has active percussion or chords past the new length
            has_drums_to_lose = any(
                len(step) > 0 for step in self.composition.rhythm.grid[new_total_steps:old_total_steps]
            ) if self.composition.rhythm and self.composition.rhythm.grid else False
            has_chords_to_lose = any(
                c.start_beat >= new_bars * 4 for c in self.composition.chords
            )
            if has_drums_to_lose or has_chords_to_lose:
                confirm = messagebox.askyesno(
                    "Reduzir Compassos",
                    f"Reduzir de {old_bars} para {new_bars} compassos irá descartar eventos nos compassos finais.\n\nDesejas continuar?",
                )
                if not confirm:
                    self.bars_menu.set(str(old_bars))
                    return

        self.composition.bars = new_bars
        if self.composition.rhythm:
            # Adjust grid length
            if len(self.composition.rhythm.grid) < new_total_steps:
                while len(self.composition.rhythm.grid) < new_total_steps:
                    self.composition.rhythm.grid.append([])
            elif len(self.composition.rhythm.grid) > new_total_steps:
                self.composition.rhythm.grid = self.composition.rhythm.grid[:new_total_steps]
            self.step_grid.set_grid(self.composition.rhythm.grid, steps_per_bar, new_bars)

    def _on_preset_selected(self, value: str):
        for pid in BACKING_TRACK_LIBRARY:
            if pid in value:
                pattern = BACKING_TRACK_LIBRARY[pid]
                self.composition.rhythm = RhythmTrack.from_pattern(pattern, bars=self.composition.bars)
                self.composition.time_signature = pattern.time_signature
                self.step_grid.set_grid(
                    self.composition.rhythm.grid,
                    self.composition.rhythm.steps_per_bar,
                    self.composition.bars,
                )
                break

    def _on_saved_composition_selected(self, value: str):
        comps = load_user_compositions()
        for c in comps:
            if c.id in value or c.title in value:
                self.composition = c
                self.title_entry.delete(0, "end")
                self.title_entry.insert(0, c.title)
                self.bpm_slider.set(c.bpm)
                self.bpm_val_lbl.configure(text=f"{c.bpm}")
                self.bars_menu.set(str(c.bars))
                steps = c.rhythm.steps_per_bar if c.rhythm else 16
                grid_data = c.rhythm.grid if c.rhythm else []
                self.step_grid.set_grid(grid_data, steps, c.bars)
                self._refresh_chords_list()
                if self.composition.chords:
                    self._select_chord(0)
                break

    def _clear_grid(self):
        self.step_grid.clear()
        self.composition.rhythm.grid = self.step_grid.get_grid()

    def _save_composition(self):
        self._on_title_changed()
        self.composition.rhythm.grid = self.step_grid.get_grid()
        save_user_composition(self.composition)
        self.saved_menu.configure(values=self._get_saved_titles())
        messagebox.showinfo("Guardado", f"Composição «{self.composition.title}» guardada com sucesso!")

    def _toggle_playback(self):
        if self.is_playing:
            self._stop_playback()
        else:
            self._start_playback()

    def _start_playback(self):
        self.is_playing = True
        self.play_btn.configure(text="⏳ A renderizar...", fg_color="#F59E0B")

        def _render_and_play():
            try:
                # 1. Offline render in worker thread
                stereo_float32 = self.renderer.render(self.composition)

                # 2. Marshal sound creation and playback back to UI
                self.after(0, lambda: self._play_rendered_buffer(stereo_float32))
            except Exception as e:
                self.after(0, lambda: self._handle_playback_error(e))

        self._render_thread = threading.Thread(target=_render_and_play, daemon=True)
        self._render_thread.start()

    def _play_rendered_buffer(self, buffer_float32: np.ndarray):
        if not self.is_playing:
            return

        if not HAS_PYGAME:
            self._stop_playback()
            return

        try:
            # Convert float32 [-1.0, 1.0] to int16 stereo array
            pcm_int16 = np.int16(np.clip(buffer_float32 * 32767.0, -32768, 32767))
            self._current_sound = pygame.sndarray.make_sound(pcm_int16)
            self._current_sound.play()
            self.play_btn.configure(text="⏹ Parar Reprodução", fg_color=theme.COLOR_ACCENT_CRIMSON)

            # Auto-reset button after audio finish
            duration_ms = int(len(buffer_float32) / 44100.0 * 1000.0)
            self.after(duration_ms, self._on_playback_finished)
        except Exception as e:
            self._handle_playback_error(e)

    def _handle_playback_error(self, error: Exception):
        self._stop_playback()
        print(f"[ComposeStudio] Playback error: {error}")

    def _on_playback_finished(self):
        if self.is_playing:
            self._stop_playback()

    def _stop_playback(self):
        self.is_playing = False
        if self._current_sound:
            try:
                self._current_sound.stop()
            except Exception:
                pass
            self._current_sound = None
        self.play_btn.configure(text="▶ Ouvir Composição", fg_color=theme.COLOR_SUCCESS)

    def _on_back_clicked(self):
        self._stop_playback()
        self.on_back()
