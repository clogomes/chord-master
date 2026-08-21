from gui.i18n import t
"""Interactive Guitar/Viola Fretboard and Chord Box Diagram component."""
import tkinter as tk
from typing import Callable, Dict, List, Optional, Set, Tuple
import customtkinter as ctk
from core.notes import Note
from core.guitar import GuitarChordShape, GuitarFretboardModel, STANDARD_TUNING, STRING_NAMES_PT
from audio.player import get_audio_player


class GuitarFretboard(ctk.CTkFrame):
    """
    Renders an interactive 6-string guitar/viola fretboard or a compact chord diagram box,
    supporting interactive note clicking, scale visualizations, and CAGED shape displays.
    """

    def __init__(
        self,
        master,
        width: int = 680,
        height: int = 160,
        num_frets: int = 14,
        on_note_clicked: Optional[Callable[[Note], None]] = None,
        enable_audio: bool = True,
        **kwargs,
    ):
        super().__init__(master, fg_color=("#F8FAFC", "#0F172A"), **kwargs)
        self.canvas_width = width
        self.canvas_height = height
        self.num_frets = num_frets
        self.on_note_clicked = on_note_clicked
        self.enable_audio = enable_audio
        self.audio_player = get_audio_player()
        self.model = GuitarFretboardModel(num_frets=num_frets)

        self.highlighted_positions: Dict[Tuple[int, int], Dict] = {}  # (string, fret) -> {color, label, is_root}
        self.current_chord_shape: Optional[GuitarChordShape] = None
        self._hovered_cell: Optional[Tuple[int, int]] = None

        self.canvas = tk.Canvas(
            self,
            width=self.canvas_width,
            height=self.canvas_height,
            bg="#1E293B",  # Slate 800 fretboard wood background
            highlightthickness=1,
            highlightbackground="#334155",
            cursor="hand2",
        )
        self.canvas.pack(padx=6, pady=6)

        self.canvas.bind("<Button-1>", self._on_canvas_click)
        self.canvas.bind("<Motion>", self._on_mouse_motion)
        self.canvas.bind("<Leave>", lambda e: self._clear_hover())

        self.redraw()

    def set_chord_shape(self, shape: GuitarChordShape):
        """Displays a specific chord shape on the fretboard with fingering and markers."""
        self.current_chord_shape = shape
        self.highlighted_positions.clear()

        for str_idx, fret in enumerate(shape.frets):
            if fret > 0:
                note = self.model.get_note_at(str_idx, fret)
                is_root = (note.letter == shape.root[0])
                finger = shape.fingers[str_idx] if shape.fingers and str_idx < len(shape.fingers) else None
                label = str(finger) if finger and finger > 0 else note.pitch

                self.highlighted_positions[(str_idx, fret)] = {
                    "color": "#10B981" if is_root else "#38BDF8",
                    "label": label,
                    "is_root": is_root,
                    "note": note,
                }
        self.redraw()

    def highlight_scale(self, scale_notes: List[Note]):
        """Highlights all occurrences of scale notes on the fretboard."""
        self.current_chord_shape = None
        self.highlighted_positions.clear()

        scale_results = self.model.get_scale_positions_on_fretboard(scale_notes)
        for item in scale_results:
            color = "#10B981" if item["is_root"] else "#38BDF8"
            self.highlighted_positions[(item["string"], item["fret"])] = {
                "color": color,
                "label": item["note"].pitch,
                "is_root": item["is_root"],
                "note": item["note"],
            }
        self.redraw()

    def clear_highlights(self):
        """Clears all markers from the fretboard."""
        self.highlighted_positions.clear()
        self.current_chord_shape = None
        self.redraw()

    def _get_string_y(self, string_idx: int) -> float:
        """String 0 (6th string E2 thickest) is at the bottom, String 5 (1st string E4) is at the top."""
        # Margin top & bottom
        margin_y = 24
        available_h = self.canvas_height - (2 * margin_y)
        # string 5 (1st) at top (idx 5 -> pos 0), string 0 (6th) at bottom (idx 0 -> pos 5)
        pos = 5 - string_idx
        return margin_y + (pos * (available_h / 5.0))

    def _get_fret_x(self, fret: int) -> float:
        """Nut is at fret 0. Frets 1..N extend to the right."""
        margin_x = 55
        nut_x = margin_x + 20
        available_w = self.canvas_width - nut_x - 20
        fret_w = available_w / self.num_frets
        return nut_x + (fret * fret_w)

    def _get_cell_center(self, string_idx: int, fret: int) -> Tuple[float, float]:
        y = self._get_string_y(string_idx)
        if fret == 0:
            x = 42  # Open string marker column
        else:
            fret_x_right = self._get_fret_x(fret)
            fret_x_left = self._get_fret_x(fret - 1)
            x = (fret_x_left + fret_x_right) / 2.0
        return x, y

    def _find_cell_at_pos(self, px: float, py: float) -> Optional[Tuple[int, int]]:
        for str_idx in range(6):
            sy = self._get_string_y(str_idx)
            if abs(py - sy) <= 14:
                # Check open string area
                if px < self._get_fret_x(0):
                    return (str_idx, 0)
                # Check frets
                for fret in range(1, self.num_frets + 1):
                    x_left = self._get_fret_x(fret - 1)
                    x_right = self._get_fret_x(fret)
                    if x_left <= px <= x_right:
                        return (str_idx, fret)
        return None

    def _on_mouse_motion(self, event):
        cell = self._find_cell_at_pos(event.x, event.y)
        if cell != self._hovered_cell:
            self._hovered_cell = cell
            self.redraw()

    def _clear_hover(self):
        if self._hovered_cell is not None:
            self._hovered_cell = None
            self.redraw()

    def _on_canvas_click(self, event):
        cell = self._find_cell_at_pos(event.x, event.y)
        if cell:
            str_idx, fret = cell
            note = self.model.get_note_at(str_idx, fret)
            if self.enable_audio:
                self.audio_player.play_note(note, duration=0.8, instrument="guitar")
            if self.on_note_clicked:
                self.on_note_clicked(note)

    def redraw(self):
        """Draws wood texture, frets, inlays, strings with gauges, and note markers."""
        self.canvas.delete("all")

        # 1. Draw Fretboard Wood Base
        top_y = self._get_string_y(5) - 14
        bottom_y = self._get_string_y(0) + 14
        nut_x = self._get_fret_x(0)
        end_x = self._get_fret_x(self.num_frets)

        self.canvas.create_rectangle(
            nut_x, top_y, end_x, bottom_y,
            fill="#292524",  # Rosewood / Ebony wood dark tone
            outline="#44403C",
            width=1,
        )

        # 2. Draw Inlay Dots (Trastes 3, 5, 7, 9, 12, 15)
        inlay_frets = [3, 5, 7, 9, 12, 15]
        mid_y = (top_y + bottom_y) / 2.0

        for f in inlay_frets:
            if f <= self.num_frets:
                fx = (self._get_fret_x(f - 1) + self._get_fret_x(f)) / 2.0
                if f == 12:
                    # Double dot on 12th fret
                    self.canvas.create_oval(fx - 4, mid_y - 18, fx + 4, mid_y - 10, fill="#78716C", outline="")
                    self.canvas.create_oval(fx - 4, mid_y + 10, fx + 4, mid_y + 18, fill="#78716C", outline="")
                else:
                    self.canvas.create_oval(fx - 4.5, mid_y - 4.5, fx + 4.5, mid_y + 4.5, fill="#78716C", outline="")

        # 3. Draw Fret Wires (Trastes metálicos)
        for f in range(1, self.num_frets + 1):
            fx = self._get_fret_x(f)
            self.canvas.create_line(fx, top_y, fx, bottom_y, fill="#D6D3D1", width=2)
            # Fret number label below
            self.canvas.create_text(
                (self._get_fret_x(f - 1) + fx) / 2.0,
                bottom_y + 12,
                text=str(f),
                font=("Helvetica", 9, "bold"),
                fill="#94A3B8" if f in [3, 5, 7, 9, 12] else "#64748B",
            )

        # 4. Draw Nut (Pestana de osso/ivory na casa 0)
        self.canvas.create_rectangle(
            nut_x - 5, top_y - 1, nut_x, bottom_y + 1,
            fill="#FEF3C7",  # Cream bone nut
            outline="#F59E0B",
            width=1,
        )

        # 5. Draw 6 Strings with realistic thicknesses (gauges)
        string_gauges = [3.5, 2.8, 2.2, 1.6, 1.2, 0.9]  # 6th to 1st
        for str_idx in range(6):
            sy = self._get_string_y(str_idx)
            gauge = string_gauges[str_idx]
            color = "#D4D4D8" if str_idx < 3 else "#F4F4F5"  # Wound bronze/nickel vs plain steel

            self.canvas.create_line(
                nut_x, sy, end_x, sy,
                fill=color,
                width=int(gauge),
            )

            # String name label on the headstock left
            open_note = STANDARD_TUNING[str_idx]
            self.canvas.create_text(
                20, sy,
                text=f"{6 - str_idx}ª {open_note.letter}",
                font=("Helvetica", 9, "bold"),
                fill="#94A3B8",
            )

        # 6. Draw Chord Shape Open/Muted indicators (if active)
        if self.current_chord_shape:
            for str_idx, fret_val in enumerate(self.current_chord_shape.frets):
                sy = self._get_string_y(str_idx)
                if fret_val == -1:
                    # Muted (X)
                    self.canvas.create_text(
                        nut_x - 14, sy,
                        text="✕",
                        font=("Helvetica", 11, "bold"),
                        fill="#EF4444",
                    )
                elif fret_val == 0:
                    # Open (O)
                    self.canvas.create_text(
                        nut_x - 14, sy,
                        text="◯",
                        font=("Helvetica", 11, "bold"),
                        fill="#10B981",
                    )

        # 7. Draw Highlighted Notes / Fret Markers
        for (str_idx, fret), data in self.highlighted_positions.items():
            cx, cy = self._get_cell_center(str_idx, fret)
            color = data.get("color", "#38BDF8")
            label = data.get("label", "")
            is_root = data.get("is_root", False)
            is_active = data.get("is_active", False)

            # Note circle bubble
            if is_active:
                # Distinctive active note styling: Outer glowing ring + enlarged bubble + thick white border
                r_outer = 15.0
                self.canvas.create_oval(
                    cx - r_outer, cy - r_outer, cx + r_outer, cy + r_outer,
                    fill="",
                    outline="#38BDF8",
                    width=2,
                )
                r = 12.5
                self.canvas.create_oval(
                    cx - r, cy - r, cx + r, cy + r,
                    fill=color,
                    outline="#FFFFFF",
                    width=3,
                )
                self.canvas.create_text(
                    cx, cy,
                    text=label,
                    font=("Helvetica", 10, "bold"),
                    fill="#FFFFFF",
                )
            else:
                r = 10.5
                self.canvas.create_oval(
                    cx - r, cy - r, cx + r, cy + r,
                    fill=color,
                    outline="#FFFFFF" if is_root else "#0F172A",
                    width=1.5 if is_root else 1,
                )
                self.canvas.create_text(
                    cx, cy,
                    text=label,
                    font=("Helvetica", 9, "bold"),
                    fill="#FFFFFF" if color in ["#10B981", "#2563EB", "#7C3AED", "#EF4444"] else "#0F172A",
                )

        # 8. Draw Hover Cursor
        if self._hovered_cell and self._hovered_cell not in self.highlighted_positions:
            str_idx, fret = self._hovered_cell
            cx, cy = self._get_cell_center(str_idx, fret)
            note = self.model.get_note_at(str_idx, fret)

            self.canvas.create_oval(
                cx - 9, cy - 9, cx + 9, cy + 9,
                fill="#475569",
                outline="#94A3B8",
                width=1,
            )
            self.canvas.create_text(
                cx, cy,
                text=note.pitch,
                font=("Helvetica", 8, "bold"),
                fill="#F8FAFC",
            )
