"""Lamiré & Chromatic Tuner screen with real-time microphone pitch detection and reference tone generator."""
import math
import time
import tkinter as tk
from typing import Callable, Dict, List, Optional
import customtkinter as ctk
from core.notes import Note
from audio.player import get_audio_player
from audio.pitch_listener import PitchListener
from gui.scroll_utils import bind_mousewheel
from gui import theme


# Guitar standard tuning reference strings
GUITAR_STRINGS = [
    ("6ª Corda", Note("E2"), "82.4 Hz", 0),
    ("5ª Corda", Note("A2"), "110.0 Hz", 1),
    ("4ª Corda", Note("D3"), "146.8 Hz", 2),
    ("3ª Corda", Note("G3"), "196.0 Hz", 3),
    ("2ª Corda", Note("B3"), "246.9 Hz", 4),
    ("1ª Corda", Note("E4"), "329.6 Hz", 5),
]


class LamireScreen(ctk.CTkFrame):
    """
    Ultra-modern Lamiré (Diapason) and Chromatic Tuner.
    Captures live microphone audio, detects notes and cents in real-time,
    and provides reference acoustic pitch generator (440 Hz).
    """

    def __init__(
        self,
        master,
        on_back: Callable[[], None],
        **kwargs,
    ):
        super().__init__(master, fg_color=theme.COLOR_BG, **kwargs)
        self.on_back = on_back
        self.audio_player = get_audio_player()
        self.pitch_listener = PitchListener(max_fps=15.0)

        self.tuner_mode = "Cromático"  # "Cromático" ou "Viola (6 Cordas)"
        self.current_cents: float = 0.0
        self.current_freq: float = 0.0
        self.current_note: Optional[Note] = None

        self._is_gui_busy: bool = False
        self._last_gui_update: float = 0.0

        self._build_ui()

    def _build_ui(self):
        # 1. Top Navigation Bar
        nav_bar = ctk.CTkFrame(self, fg_color="transparent")
        nav_bar.pack(fill="x", padx=20, pady=(16, 8))

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

        title_box = ctk.CTkFrame(nav_bar, fg_color="transparent")
        title_box.pack(side="left", padx=16)

        ctk.CTkLabel(
            title_box,
            text="🎙️ Lamiré & Afinador Cromático",
            font=theme.get_font(theme.FONT_TITLE),
            text_color=theme.COLOR_TEXT_PRIMARY,
        ).pack(anchor="w")

        ctk.CTkLabel(
            title_box,
            text="Deteção de afinação ao vivo pelo microfone e diapasão de referência (Lá 440 Hz)",
            font=theme.get_font(theme.FONT_SMALL),
            text_color=theme.COLOR_TEXT_MUTED,
        ).pack(anchor="w")

        # Live Mic Toggle Button
        self.mic_toggle_btn = ctk.CTkButton(
            nav_bar,
            text="🎙️ Ativar Microfone",
            font=theme.get_font(theme.FONT_BODY_BOLD),
            fg_color=theme.COLOR_SUCCESS,
            hover_color=theme.COLOR_SUCCESS_HOVER,
            width=170,
            height=38,
            corner_radius=theme.RADIUS_MD,
            command=self._toggle_mic,
        )
        self.mic_toggle_btn.pack(side="right")

        # 2. Main Scrollable View
        self.scroll = ctk.CTkScrollableFrame(
            self,
            corner_radius=theme.RADIUS_LG,
            fg_color=theme.COLOR_BG,
            border_width=1,
            border_color=theme.COLOR_BORDER,
        )
        self.scroll.pack(fill="both", expand=True, padx=20, pady=(4, 16))
        bind_mousewheel(self.scroll)

        # Mode Selector
        mode_frame = ctk.CTkFrame(self.scroll, fg_color="transparent")
        mode_frame.pack(fill="x", padx=10, pady=(4, 10))

        self.mode_segmented = ctk.CTkSegmentedButton(
            mode_frame,
            values=["🎯 Afinador Cromático Geral", "🎸 Afinador de Viola (6 Cordas)", "🔊 Gerador de Lamiré (Diapasão)"],
            command=self._on_mode_change,
            selected_color=theme.COLOR_PRIMARY,
            selected_hover_color=theme.COLOR_PRIMARY_HOVER,
            font=theme.get_font(theme.FONT_BODY_BOLD),
            height=38,
        )
        self.mode_segmented.set("🎯 Afinador Cromático Geral")
        self.mode_segmented.pack(fill="x")

        # 3. Big Central Tuner Display Card
        self.tuner_card = ctk.CTkFrame(
            self.scroll,
            corner_radius=theme.RADIUS_LG,
            fg_color=theme.COLOR_SURFACE,
            border_width=2,
            border_color=theme.COLOR_BORDER,
        )
        self.tuner_card.pack(fill="x", padx=10, pady=(0, 12))

        # Note display bubble
        note_center_frame = ctk.CTkFrame(self.tuner_card, fg_color="transparent")
        note_center_frame.pack(pady=(20, 8))

        self.note_letter_lbl = ctk.CTkLabel(
            note_center_frame,
            text="--",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=68, weight="bold"),
            text_color=theme.COLOR_TEXT_MUTED,
        )
        self.note_letter_lbl.pack()

        self.note_name_lbl = ctk.CTkLabel(
            note_center_frame,
            text="Clica em «Ativar Microfone» e toca uma nota...",
            font=theme.get_font(theme.FONT_SECTION),
            text_color=theme.COLOR_TEXT_MUTED,
        )
        self.note_name_lbl.pack(pady=(2, 4))

        self.freq_lbl = ctk.CTkLabel(
            note_center_frame,
            text="0.0 Hz  |  0 cents",
            font=theme.get_font(theme.FONT_BODY),
            text_color=theme.COLOR_TEXT_MUTED,
        )
        self.freq_lbl.pack()

        # Canvas Needle Gauge (580px wide by 65px high)
        self.gauge_canvas = tk.Canvas(
            self.tuner_card,
            width=580,
            height=65,
            bg="#0B0F19",
            highlightthickness=1,
            highlightbackground="#374151",
        )
        self.gauge_canvas.pack(padx=20, pady=(10, 8))

        self.status_hint_lbl = ctk.CTkLabel(
            self.tuner_card,
            text="Microfone em pausa. Clica no botão acima para iniciar a deteção.",
            font=theme.get_font(theme.FONT_SUBTITLE),
            text_color=theme.COLOR_TEXT_MUTED,
        )
        self.status_hint_lbl.pack(pady=(4, 18))

        # 4. Viola Strings Visualizer (visible in guitar mode)
        self.guitar_strings_card = ctk.CTkFrame(
            self.scroll,
            corner_radius=theme.RADIUS_LG,
            fg_color=theme.COLOR_SURFACE,
            border_width=1,
            border_color=theme.COLOR_BORDER,
        )

        self.string_buttons: List[ctk.CTkFrame] = []
        self._build_guitar_strings_ui()

        # 5. Reference Pitch Generator Card (Diapasão)
        self.diapason_card = ctk.CTkFrame(
            self.scroll,
            corner_radius=theme.RADIUS_LG,
            fg_color=theme.COLOR_SURFACE,
            border_width=1,
            border_color=theme.COLOR_BORDER,
        )
        self._build_diapason_ui()

        self._draw_gauge(0.0, is_active=False)

    def _build_guitar_strings_ui(self):
        ctk.CTkLabel(
            self.guitar_strings_card,
            text="🎸 Afinação Padrão da Viola / Guitarra",
            font=theme.get_font(theme.FONT_SECTION),
            text_color=theme.COLOR_TEXT_PRIMARY,
        ).pack(anchor="w", padx=16, pady=(14, 6))

        grid = ctk.CTkFrame(self.guitar_strings_card, fg_color="transparent")
        grid.pack(fill="x", padx=14, pady=(0, 14))
        grid.grid_columnconfigure((0, 1, 2, 3, 4, 5), weight=1, uniform="strings")

        for col, (sname, snote, sfreq, sidx) in enumerate(GUITAR_STRINGS):
            card = ctk.CTkFrame(
                grid,
                corner_radius=theme.RADIUS_MD,
                fg_color=theme.COLOR_SURFACE_SECONDARY,
                border_width=1,
                border_color=theme.COLOR_BORDER,
            )
            card.grid(row=0, column=col, padx=4, pady=4, sticky="nsew")

            ctk.CTkLabel(
                card,
                text=sname,
                font=theme.get_font(theme.FONT_BADGE),
                text_color=theme.COLOR_TEXT_MUTED,
            ).pack(pady=(8, 2))

            ctk.CTkLabel(
                card,
                text=f"{snote.pitch}{snote.octave}",
                font=ctk.CTkFont(family=theme.FONT_FAMILY, size=22, weight="bold"),
                text_color=theme.COLOR_PRIMARY,
            ).pack()

            ctk.CTkLabel(
                card,
                text=f"{snote.name_pt}\n({sfreq})",
                font=theme.get_font(theme.FONT_SMALL),
                text_color=theme.COLOR_TEXT_MUTED,
            ).pack(pady=(2, 6))

            play_btn = ctk.CTkButton(
                card,
                text="🔊 Ouvir",
                font=theme.get_font(theme.FONT_SMALL_BOLD),
                height=28,
                corner_radius=theme.RADIUS_SM,
                fg_color=theme.COLOR_PRIMARY,
                hover_color=theme.COLOR_PRIMARY_HOVER,
                command=lambda n=snote: self.audio_player.play_note(n, duration=1.2),
            )
            play_btn.pack(fill="x", padx=8, pady=(0, 8))

            self.string_buttons.append(card)

    def _build_diapason_ui(self):
        ctk.CTkLabel(
            self.diapason_card,
            text="🔊 Gerador de Tom de Referência (Diapasão / Lamiré)",
            font=theme.get_font(theme.FONT_SECTION),
            text_color=theme.COLOR_TEXT_PRIMARY,
        ).pack(anchor="w", padx=16, pady=(14, 6))

        # Main 440 Hz Button
        a440_btn = ctk.CTkButton(
            self.diapason_card,
            text="🔔 Tocar Lá Central (A4 - 440 Hz) — Padrão Internacional",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=15, weight="bold"),
            fg_color=theme.COLOR_PRIMARY,
            hover_color=theme.COLOR_PRIMARY_HOVER,
            corner_radius=theme.RADIUS_MD,
            height=44,
            command=lambda: self.audio_player.play_note(Note("A4"), duration=2.5),
        )
        a440_btn.pack(fill="x", padx=16, pady=(4, 12))

        # 12 Chromatic Notes Row
        ctk.CTkLabel(
            self.diapason_card,
            text="Tocar outras notas de referência (Oitava 4):",
            font=theme.get_font(theme.FONT_BODY_BOLD),
            text_color=theme.COLOR_TEXT_MUTED,
        ).pack(anchor="w", padx=16, pady=(4, 6))

        chrom_row = ctk.CTkFrame(self.diapason_card, fg_color="transparent")
        chrom_row.pack(fill="x", padx=14, pady=(0, 16))
        for col in range(12):
            chrom_row.grid_columnconfigure(col, weight=1)

        chromatic_notes = ["C4", "C#4", "D4", "D#4", "E4", "F4", "F#4", "G4", "G#4", "A4", "A#4", "B4"]
        for i, n_str in enumerate(chromatic_notes):
            n = Note(n_str)
            btn = ctk.CTkButton(
                chrom_row,
                text=n.pitch,
                font=theme.get_font(theme.FONT_SMALL_BOLD),
                height=32,
                corner_radius=theme.RADIUS_SM,
                fg_color=theme.COLOR_SURFACE_SECONDARY,
                text_color=theme.COLOR_TEXT_PRIMARY,
                hover_color=theme.COLOR_PRIMARY,
                command=lambda note_obj=n: self.audio_player.play_note(note_obj, duration=1.5),
            )
            btn.grid(row=0, column=i, padx=2, pady=2, sticky="nsew")

    def _on_mode_change(self, mode: str):
        if "Viola" in mode:
            self.tuner_mode = "Viola"
            self.guitar_strings_card.pack(fill="x", padx=10, pady=(0, 12))
            self.diapason_card.pack_forget()
        elif "Diapasão" in mode:
            self.tuner_mode = "Diapasão"
            self.guitar_strings_card.pack_forget()
            self.diapason_card.pack(fill="x", padx=10, pady=(0, 12))
        else:
            self.tuner_mode = "Cromático"
            self.guitar_strings_card.pack_forget()
            self.diapason_card.pack_forget()

    def _toggle_mic(self):
        if self.pitch_listener.is_listening:
            self._stop_listening()
        else:
            self._start_listening()

    def _start_listening(self):
        started = self.pitch_listener.start_listening(self._on_live_audio)
        if started:
            self.mic_toggle_btn.configure(
                text="⏹️ Desativar Microfone",
                fg_color=theme.COLOR_ACCENT_CRIMSON,
                hover_color=theme.COLOR_ACCENT_CRIMSON_HOVER,
            )
            self.status_hint_lbl.configure(text="🎙️ A ouvir... Toca uma nota no teu instrumento.", text_color="#38BDF8")
        else:
            self.status_hint_lbl.configure(text="⚠️ Erro: Microfone não disponível", text_color=theme.COLOR_ACCENT_CRIMSON)

    def _stop_listening(self):
        self.pitch_listener.stop_listening()
        self.mic_toggle_btn.configure(
            text="🎙️ Ativar Microfone",
            fg_color=theme.COLOR_SUCCESS,
            hover_color=theme.COLOR_SUCCESS_HOVER,
        )
        self.note_letter_lbl.configure(text="--", text_color=theme.COLOR_TEXT_MUTED)
        self.note_name_lbl.configure(text="Microfone em pausa", text_color=theme.COLOR_TEXT_MUTED)
        self.freq_lbl.configure(text="0.0 Hz  |  0 cents")
        self.status_hint_lbl.configure(text="Microfone desligado. Clica em «Ativar Microfone» para retomar.", text_color=theme.COLOR_TEXT_MUTED)
        self.tuner_card.configure(border_color=theme.COLOR_BORDER)
        self._draw_gauge(0.0, is_active=False)

    def _on_live_audio(self, note: Optional[Note], cents: float, conf: float, freq: float):
        now = time.time()
        if now - self._last_gui_update < 0.075:
            return
        if self._is_gui_busy or not self.winfo_exists():
            return
        self._last_gui_update = now
        self._is_gui_busy = True
        try:
            self.after(0, lambda: self._safe_update_gui(note, cents, conf, freq))
        except Exception:
            self._is_gui_busy = False

    def _safe_update_gui(self, note: Optional[Note], cents: float, conf: float, freq: float):
        try:
            self._update_gui(note, cents, conf, freq)
        finally:
            self._is_gui_busy = False

    def _update_gui(self, note: Optional[Note], cents: float, conf: float, freq: float):
        if not self.winfo_exists():
            return

        if note is None:
            return

        self.current_note = note
        self.current_cents = cents
        self.current_freq = freq

        # Update note text
        self.note_letter_lbl.configure(
            text=f"{note.pitch}{note.octave}",
            text_color=theme.COLOR_SUCCESS if abs(cents) <= 8.0 else (theme.COLOR_PRIMARY if abs(cents) <= 25.0 else theme.COLOR_ACCENT_AMBER),
        )
        self.note_name_lbl.configure(
            text=f"{note.name_pt} (Oitava {note.octave})",
            text_color=theme.COLOR_TEXT_PRIMARY,
        )
        self.freq_lbl.configure(
            text=f"{freq:.1f} Hz  |  {cents:+.0f} cents (Precisão {conf*100:.0f}%)",
            text_color=theme.COLOR_TEXT_MUTED,
        )

        # Intonation Advice
        if abs(cents) <= 6.0:
            status_text = "✓ AFINADO (No Ponto Perfeito!)"
            status_color = theme.COLOR_SUCCESS
            self.tuner_card.configure(border_color=theme.COLOR_SUCCESS)
        elif abs(cents) <= 20.0:
            status_text = "✓ Boa afinação (Dentro da tolerância)"
            status_color = theme.COLOR_PRIMARY
            self.tuner_card.configure(border_color=theme.COLOR_PRIMARY)
        elif cents < -20.0:
            status_text = f"▲ Muito Grave ({abs(cents):.0f}c abaixo) — Estica a corda / Toca mais agudo"
            status_color = theme.COLOR_ACCENT_AMBER
            self.tuner_card.configure(border_color=theme.COLOR_ACCENT_AMBER)
        else:
            status_text = f"▼ Muito Agudo ({cents:.0f}c acima) — Afrouxa a corda / Toca mais grave"
            status_color = theme.COLOR_ACCENT_AMBER
            self.tuner_card.configure(border_color=theme.COLOR_ACCENT_AMBER)

        self.status_hint_lbl.configure(text=status_text, text_color=status_color)
        self._draw_gauge(cents, is_active=True)

        # Highlight nearest guitar string if in Viola mode
        if self.tuner_mode == "Viola":
            for i, (_, snote, _, _) in enumerate(GUITAR_STRINGS):
                card = self.string_buttons[i]
                if snote.pitch == note.pitch:
                    card.configure(border_color=theme.COLOR_SUCCESS if abs(cents) <= 10 else theme.COLOR_PRIMARY, border_width=2)
                else:
                    card.configure(border_color=theme.COLOR_BORDER, border_width=1)

    def _draw_gauge(self, cents: float, is_active: bool = True):
        """Draws a high-precision chromatic tuner needle on the Canvas."""
        self.gauge_canvas.delete("all")
        w = 580
        h = 65
        cx = w / 2.0
        cy = h - 14

        # Background track
        self.gauge_canvas.create_rectangle(14, cy - 8, w - 14, cy + 4, fill="#1E293B", outline="")

        # Green Center Safe Zone (±10 cents)
        safe_half_w = (w - 28) * (10.0 / 100.0)
        self.gauge_canvas.create_rectangle(
            cx - safe_half_w, cy - 8, cx + safe_half_w, cy + 4,
            fill="#064E3B", outline=theme.COLOR_SUCCESS, width=1
        )

        # Ticks (-50, -25, 0, +25, +50)
        for c in [-50, -25, 0, 25, 50]:
            tx = cx + (w - 30) * (c / 100.0)
            is_zero = (c == 0)
            self.gauge_canvas.create_line(
                tx, cy - (14 if is_zero else 8), tx, cy + 6,
                fill=theme.COLOR_SUCCESS if is_zero else "#64748B",
                width=2 if is_zero else 1,
            )
            # Labels
            sign = "+" if c > 0 else ""
            lbl_text = f"{sign}{c}" if c != 0 else "0 (Afinado)"
            self.gauge_canvas.create_text(
                tx, cy - 22,
                text=lbl_text,
                font=("Helvetica", 10, "bold" if is_zero else "normal"),
                fill=theme.COLOR_SUCCESS if is_zero else "#94A3B8",
            )

        if not is_active:
            return

        # Active Needle
        clamped_cents = max(-50.0, min(50.0, cents))
        needle_x = cx + (w - 30) * (clamped_cents / 100.0)

        needle_color = theme.COLOR_SUCCESS if abs(cents) <= 8.0 else ("#38BDF8" if abs(cents) <= 20.0 else theme.COLOR_ACCENT_AMBER)

        # Needle pointer
        self.gauge_canvas.create_line(
            needle_x, cy + 8, needle_x, cy - 24,
            fill=needle_color,
            width=3,
        )
        self.gauge_canvas.create_oval(
            needle_x - 5, cy + 4, needle_x + 5, cy + 14,
            fill=needle_color, outline="#FFFFFF", width=1,
        )

    def _handle_back(self):
        self._stop_listening()
        self.audio_player.stop_all()
        self.on_back()

    def destroy(self):
        self._stop_listening()
        super().destroy()
