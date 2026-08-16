from gui.i18n import t
"""
OMR Review & Manual Correction Screen — Phase 19.

After the OMR pipeline detects notes from a score image, this screen lets the
user review each detected note, correct pitch and duration, delete false positives,
and insert missing notes before saving as a real Song in the user library.
"""
from __future__ import annotations

import os
from typing import Callable, List, Optional

import customtkinter as ctk

from core.notes import Note, NOTE_NAMES
from core.songs import Song, SongNote
from core.fingering import assign_piano_fingerings
from core.guitar import assign_guitar_coordinates
from core.midi_importer import save_user_song
from core.user_manager import UserManager
from gui.scroll_utils import bind_mousewheel
from gui import theme

# Duration options shown in dropdowns
DURATION_OPTIONS = [
    ("Semibreve (4 tempos)", 4.0),
    ("Mínima (2 tempos)", 2.0),
    ("Semínima (1 tempo)", 1.0),
    ("Semínima com Ponto (1.5 tempos)", 1.5),
    ("Colcheia (0.5 tempos)", 0.5),
    ("Colcheia com Ponto (0.75 tempos)", 0.75),
]
DURATION_LABELS = [d[0] for d in DURATION_OPTIONS]
DURATION_VALUES = {d[0]: d[1] for d in DURATION_OPTIONS}

# All chromatic pitch names for the note dropdown
ALL_PITCHES = [f"{p}{o}" for o in range(2, 7) for p in NOTE_NAMES]


def _duration_label(beats: float) -> str:
    """Return the closest matching duration label for a beat value."""
    for label, val in DURATION_OPTIONS:
        if abs(val - beats) < 0.01:
            return label
    return f"Custom ({beats} tempos)"


class _NoteRow(ctk.CTkFrame):
    """A single editable row representing one detected note."""

    def __init__(
        self,
        master,
        index: int,
        song_note: SongNote,
        on_delete: Callable[[int], None],
        on_change: Callable[[int, str, float], None],
        **kwargs,
    ):
        bg = ("#F8FAFC", "#1F2937") if index % 2 == 0 else ("#F1F5F9", "#111827")
        super().__init__(master, fg_color=bg, corner_radius=6, **kwargs)
        self.index = index
        self.on_delete = on_delete
        self.on_change = on_change

        self.columnconfigure(0, minsize=40)   # #
        self.columnconfigure(1, weight=2)     # pitch selector
        self.columnconfigure(2, weight=3)     # duration selector
        self.columnconfigure(3, minsize=36)   # delete button

        # Row number
        ctk.CTkLabel(
            self, text=str(index + 1),
            font=theme.get_font(theme.FONT_SMALL),
            text_color=theme.COLOR_TEXT_MUTED,
            width=36,
        ).grid(row=0, column=0, padx=(8, 4), pady=6)

        # Pitch dropdown
        pitch_str = song_note.note.pitch_with_octave
        self._pitch_var = ctk.StringVar(value=pitch_str)
        pitch_choices = ALL_PITCHES if pitch_str in ALL_PITCHES else [pitch_str] + ALL_PITCHES
        self._pitch_cb = ctk.CTkComboBox(
            self,
            values=pitch_choices,
            variable=self._pitch_var,
            font=theme.get_font(theme.FONT_BODY),
            width=110,
            command=self._on_pitch_changed,
        )
        self._pitch_cb.grid(row=0, column=1, padx=6, pady=6, sticky="ew")

        # Duration dropdown
        dur_label = _duration_label(song_note.duration_beats)
        self._dur_var = ctk.StringVar(value=dur_label)
        self._dur_cb = ctk.CTkComboBox(
            self,
            values=DURATION_LABELS,
            variable=self._dur_var,
            font=theme.get_font(theme.FONT_BODY),
            width=220,
            command=self._on_duration_changed,
        )
        self._dur_cb.grid(row=0, column=2, padx=6, pady=6, sticky="ew")

        # Delete button
        ctk.CTkButton(
            self,
            text="✕",
            width=30, height=28,
            fg_color=("#EF4444", "#7F1D1D"),
            hover_color=("#DC2626", "#991B1B"),
            font=theme.get_font(theme.FONT_BODY_BOLD),
            command=lambda: self.on_delete(self.index),
        ).grid(row=0, column=3, padx=(4, 8), pady=6)

    def _on_pitch_changed(self, value: str):
        try:
            dur = DURATION_VALUES.get(self._dur_var.get(), 1.0)
            self.on_change(self.index, value, dur)
        except Exception:
            pass

    def _on_duration_changed(self, value: str):
        dur = DURATION_VALUES.get(value, 1.0)
        self.on_change(self.index, self._pitch_var.get(), dur)


class OMRReviewScreen(ctk.CTkFrame):
    """
    Full-screen overlay for reviewing and correcting OMR-detected notes before
    saving the resulting Song to the user library.
    """

    def __init__(
        self,
        master,
        draft_song: Song,
        original_filepath: str,
        user_manager: UserManager,
        on_save: Callable[[Song], None],
        on_cancel: Callable[[], None],
        **kwargs,
    ):
        super().__init__(master, fg_color=theme.COLOR_BG, **kwargs)
        self.draft_song = draft_song
        self.original_filepath = original_filepath
        self.user_manager = user_manager
        self.on_save = on_save
        self.on_cancel = on_cancel

        # Working copy of notes (mutable)
        self._notes: List[SongNote] = list(draft_song.notes)
        self._rows: List[_NoteRow] = []

        self._build_ui()

    # ── UI construction ────────────────────────────────────────────────────────

    def _build_ui(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        # Header
        header = ctk.CTkFrame(self, fg_color=("#111827", "#0B0F19"), corner_radius=0, height=72)
        header.grid(row=0, column=0, sticky="ew")
        header.columnconfigure(1, weight=1)

        ctk.CTkButton(
            header, text="← Cancelar", width=110, height=36,
            fg_color="transparent", hover_color=theme.COLOR_CARD_SURFACE,
            font=theme.get_font(theme.FONT_BODY_BOLD),
            text_color=theme.COLOR_TEXT_MUTED,
            command=self.on_cancel,
        ).grid(row=0, column=0, padx=16, pady=18)

        ctk.CTkLabel(
            header,
            text=f"🖋️  Rever Partitura — {self.draft_song.title}",
            font=theme.get_font(theme.FONT_SUBTITLE),
            text_color=theme.COLOR_TEXT_PRIMARY,
        ).grid(row=0, column=1, sticky="w", padx=8)

        note_count_lbl = ctk.CTkLabel(
            header,
            text=f"{len(self._notes)} notas detetadas",
            font=theme.get_font(theme.FONT_SMALL),
            text_color=theme.COLOR_TEXT_MUTED,
        )
        note_count_lbl.grid(row=0, column=2, padx=8)
        self._note_count_lbl = note_count_lbl

        save_btn = ctk.CTkButton(
            header, text="💾 Guardar como Música", height=36, width=200,
            fg_color=theme.COLOR_SUCCESS, hover_color=theme.COLOR_SUCCESS_DARK,
            font=theme.get_font(theme.FONT_BODY_BOLD),
            command=self._on_save,
        )
        save_btn.grid(row=0, column=3, padx=16, pady=18)

        # Body: split into notes list (left) + image preview (right)
        body = ctk.CTkFrame(self, fg_color="transparent")
        body.grid(row=1, column=0, sticky="nsew", padx=16, pady=12)
        body.columnconfigure(0, weight=3)
        body.columnconfigure(1, weight=2)
        body.rowconfigure(0, weight=1)

        # Left: scrollable note list
        list_frame = ctk.CTkFrame(body, corner_radius=theme.RADIUS_LG,
                                  fg_color=theme.COLOR_CARD_SURFACE,
                                  border_width=1, border_color=theme.COLOR_BORDER)
        list_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        list_frame.rowconfigure(1, weight=1)

        # List header row
        hdr = ctk.CTkFrame(list_frame, fg_color="transparent")
        hdr.pack(fill="x", padx=12, pady=(12, 4))
        ctk.CTkLabel(hdr, text="#", width=36,
                     font=theme.get_font(theme.FONT_BADGE),
                     text_color=theme.COLOR_TEXT_MUTED).pack(side="left")
        ctk.CTkLabel(hdr, text="Altura", width=110,
                     font=theme.get_font(theme.FONT_BADGE),
                     text_color=theme.COLOR_TEXT_MUTED).pack(side="left", padx=(38, 0))
        ctk.CTkLabel(hdr, text="Duração",
                     font=theme.get_font(theme.FONT_BADGE),
                     text_color=theme.COLOR_TEXT_MUTED).pack(side="left", padx=(38, 0))

        self._scroll = ctk.CTkScrollableFrame(
            list_frame,
            fg_color="transparent",
            corner_radius=0,
        )
        self._scroll.pack(fill="both", expand=True, padx=8, pady=(0, 8))
        bind_mousewheel(self._scroll)

        # "Add note" button
        add_btn = ctk.CTkButton(
            list_frame, text="+ Inserir Nota",
            height=32,
            fg_color=("#10B981", "#064E3B"),
            hover_color=("#059669", "#065F46"),
            font=theme.get_font(theme.FONT_BODY_BOLD),
            command=self._insert_note,
        )
        add_btn.pack(fill="x", padx=8, pady=(0, 8))

        # Right: image preview
        preview_frame = ctk.CTkFrame(body, corner_radius=theme.RADIUS_LG,
                                     fg_color=theme.COLOR_CARD_SURFACE,
                                     border_width=1, border_color=theme.COLOR_BORDER)
        preview_frame.grid(row=0, column=1, sticky="nsew")

        ctk.CTkLabel(
            preview_frame,
            text="📄 Imagem Original",
            font=theme.get_font(theme.FONT_BADGE),
            text_color=theme.COLOR_TEXT_MUTED,
        ).pack(anchor="w", padx=16, pady=(12, 6))

        self._img_label = ctk.CTkLabel(preview_frame, text="", image=None)
        self._img_label.pack(fill="both", expand=True, padx=8, pady=(0, 12))

        self._load_preview_image()
        self._rebuild_rows()

    # ── Helpers ────────────────────────────────────────────────────────────────

    def _load_preview_image(self):
        """Try to load the original score image for reference display."""
        try:
            from PIL import Image
            from PIL import ImageTk  # noqa: F401 — needed at runtime
            img = Image.open(self.original_filepath)
            img.thumbnail((480, 600))
            ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=img.size)
            self._img_label.configure(image=ctk_img, text="")
            self._img_label._image_ref = ctk_img  # prevent GC
        except Exception:
            self._img_label.configure(
                text="(pré-visualização não disponível)",
                text_color=theme.COLOR_TEXT_MUTED,
                font=theme.get_font(theme.FONT_SMALL),
            )

    def _rebuild_rows(self):
        """Clear and rebuild the scrollable note list from self._notes."""
        for widget in self._scroll.winfo_children():
            widget.destroy()
        self._rows.clear()

        for i, sn in enumerate(self._notes):
            row = _NoteRow(
                self._scroll, index=i, song_note=sn,
                on_delete=self._delete_note,
                on_change=self._update_note,
            )
            row.pack(fill="x", pady=2)
            self._rows.append(row)

        self._note_count_lbl.configure(text=f"{len(self._notes)} notas")

    def _delete_note(self, index: int):
        if 0 <= index < len(self._notes):
            self._notes.pop(index)
            self._rebuild_rows()

    def _update_note(self, index: int, pitch_str: str, duration: float):
        if 0 <= index < len(self._notes):
            try:
                new_note = Note(pitch_str)
                self._notes[index] = SongNote(
                    note=new_note,
                    duration_beats=duration,
                    piano_finger=self._notes[index].piano_finger,
                    piano_hand=self._notes[index].piano_hand,
                    guitar_string=self._notes[index].guitar_string,
                    guitar_fret=self._notes[index].guitar_fret,
                )
            except ValueError:
                pass

    def _insert_note(self):
        """Append a default C4 quarter note at the end of the list."""
        self._notes.append(SongNote(note=Note("C4"), duration_beats=1.0))
        self._rebuild_rows()

    def _on_save(self):
        """Assign fingerings, save to disk, and hand back to the practice screen."""
        from core.fingering import assign_piano_fingerings
        from core.guitar import assign_guitar_coordinates

        if not self._notes:
            from tkinter import messagebox
            messagebox.showwarning("Sem Notas", "Adiciona pelo menos uma nota antes de guardar.")
            return

        # Enrich with fingerings (same pipeline as MIDI import)
        try:
            assign_piano_fingerings(self._notes)
        except Exception:
            pass
        try:
            assign_guitar_coordinates(self._notes)
        except Exception:
            pass

        final_song = Song(
            id=self.draft_song.id,
            title=self.draft_song.title,
            composer=self.draft_song.composer,
            difficulty=self.draft_song.difficulty,
            bpm=self.draft_song.bpm,
            clef=self.draft_song.clef,
            notes=list(self._notes),
        )
        save_user_song(final_song)
        self.on_save(final_song)
        self.destroy()
