"""Composition Studio Screen (Phase 42) with interactive step sequencer and offline audio player."""
import threading
from tkinter import messagebox
from typing import Callable, List, Optional
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
from audio.composition_renderer import CompositionRenderer
from audio.backing_tracks import BACKING_TRACK_LIBRARY
from audio.player import get_audio_player
from gui.components.step_grid import StepGrid
from gui.scroll_utils import bind_mousewheel
from gui.i18n import t, get_language
from gui import theme

try:
    import pygame
    HAS_PYGAME = True
except ImportError:
    HAS_PYGAME = False


class ComposeStudioScreen(ctk.CTkFrame):
    """
    Interactive Studio for creating and editing custom rhythmic grooves and compositions.
    Includes canvas step-sequencer, BPM/bars transport controls, template presets, and offline audio rendering.
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

        # 3. Transport & Settings Card
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
            t_row, width=200, height=34, font=theme.get_font(theme.FONT_BODY), corner_radius=theme.RADIUS_SM
        )
        self.title_entry.insert(0, self.composition.title)
        self.title_entry.pack(side="left", padx=(0, 16))
        self.title_entry.bind("<FocusOut>", lambda e: self._on_title_changed())

        # Play / Stop Button
        self.play_btn = ctk.CTkButton(
            t_row,
            text="▶ Ouvir Composição",
            font=theme.get_font(theme.FONT_BODY_BOLD),
            fg_color=theme.COLOR_SUCCESS,
            hover_color=theme.COLOR_SUCCESS_HOVER,
            width=170,
            height=36,
            corner_radius=theme.RADIUS_MD,
            command=self._toggle_playback,
        )
        self.play_btn.pack(side="left", padx=(0, 16))

        # BPM Slider & Label
        ctk.CTkLabel(
            t_row, text="Andamento (BPM):", font=theme.get_font(theme.FONT_BODY_BOLD), text_color=theme.COLOR_TEXT_PRIMARY
        ).pack(side="left", padx=(0, 6))
        self.bpm_slider = ctk.CTkSlider(
            t_row,
            from_=40,
            to=220,
            number_of_steps=180,
            width=120,
            command=self._on_bpm_slider_changed,
        )
        self.bpm_slider.set(self.composition.bpm)
        self.bpm_slider.pack(side="left", padx=(0, 6))
        self.bpm_val_lbl = ctk.CTkLabel(
            t_row, text=f"{self.composition.bpm}", font=theme.get_font(theme.FONT_BODY_BOLD), text_color="#38BDF8", width=35
        )
        self.bpm_val_lbl.pack(side="left", padx=(0, 16))

        # Bars Selector
        ctk.CTkLabel(
            t_row, text="Compassos:", font=theme.get_font(theme.FONT_BODY_BOLD), text_color=theme.COLOR_TEXT_PRIMARY
        ).pack(side="left", padx=(0, 6))
        self.bars_menu = ctk.CTkOptionMenu(
            t_row,
            values=["2", "4", "8", "16"],
            width=70,
            height=32,
            font=theme.get_font(theme.FONT_BODY_BOLD),
            command=self._on_bars_changed,
        )
        self.bars_menu.set(str(self.composition.bars))
        self.bars_menu.pack(side="left", padx=(0, 16))

        # Save Button
        save_btn = ctk.CTkButton(
            t_row,
            text="💾 Guardar",
            font=theme.get_font(theme.FONT_BODY_BOLD),
            fg_color=theme.COLOR_PRIMARY,
            hover_color=theme.COLOR_PRIMARY_HOVER,
            width=100,
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
            p_row, text="Modelos / Ritmos Pré-definidos:", font=theme.get_font(theme.FONT_BODY_BOLD), text_color=theme.COLOR_TEXT_PRIMARY
        ).pack(side="left", padx=(0, 10))

        preset_options = [f"{p.name_pt} ({pid})" for pid, p in BACKING_TRACK_LIBRARY.items()]
        self.presets_menu = ctk.CTkOptionMenu(
            p_row,
            values=preset_options,
            width=250,
            height=32,
            font=theme.get_font(theme.FONT_SMALL),
            command=self._on_preset_selected,
        )
        self.presets_menu.set("Escolher Ritmo Base...")
        self.presets_menu.pack(side="left", padx=(0, 14))

        # Load Saved Compositions
        self.saved_menu = ctk.CTkOptionMenu(
            p_row,
            values=self._get_saved_titles(),
            width=220,
            height=32,
            font=theme.get_font(theme.FONT_SMALL),
            command=self._on_saved_composition_selected,
        )
        self.saved_menu.set("📂 Minhas Composições...")
        self.saved_menu.pack(side="left", padx=(0, 14))

        # Clear Grid Button
        clear_btn = ctk.CTkButton(
            p_row,
            text="🗑️ Limpar Grelha",
            font=theme.get_font(theme.FONT_SMALL),
            fg_color=theme.COLOR_SURFACE_SECONDARY,
            hover_color=theme.COLOR_BORDER,
            text_color=theme.COLOR_TEXT_PRIMARY,
            width=110,
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
            text="🥁 Grelha Rítmica Interativa (16 Passos por Compasso)",
            font=theme.get_font(theme.FONT_SECTION),
            text_color=theme.COLOR_TEXT_PRIMARY,
        ).pack(side="left")

        ctk.CTkLabel(
            grid_header,
            text="💡 Clica nas células para ativar/desativar cada instrumento de percussão.",
            font=theme.get_font(theme.FONT_SMALL),
            text_color=theme.COLOR_TEXT_MUTED,
        ).pack(side="right")

        # Step Grid Canvas Component
        steps = self.composition.rhythm.steps_per_bar if self.composition.rhythm else 16
        grid_data = self.composition.rhythm.grid if self.composition.rhythm else []
        self.step_grid = StepGrid(
            grid_card,
            grid=grid_data,
            steps_per_bar=steps,
            on_grid_change=self._on_grid_updated,
        )
        self.step_grid.pack(fill="both", expand=True, padx=14, pady=(4, 14))

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
        self.composition.bars = int(value)

    def _on_preset_selected(self, value: str):
        for pid in BACKING_TRACK_LIBRARY:
            if pid in value:
                pattern = BACKING_TRACK_LIBRARY[pid]
                self.composition.rhythm = RhythmTrack.from_pattern(pattern)
                self.composition.time_signature = pattern.time_signature
                self.step_grid.set_grid(self.composition.rhythm.grid, self.composition.rhythm.steps_per_bar)
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
                self.step_grid.set_grid(grid_data, steps)
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
