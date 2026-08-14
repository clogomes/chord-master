"""Vector musical staff canvas component for rendering Treble and Bass clefs, notes, and accidentals."""
import tkinter as tk
from typing import List, Optional, Tuple, Union
import customtkinter as ctk
from core.notes import Note, DIATONIC_STEPS


class StaffCanvas(ctk.CTkFrame):
    """
    Renders a standard 5-line musical staff with Treble (𝄞) or Bass (𝄢) clefs,
    drawing notes, ledger lines, stems, accidentals, and chord clusters with accurate positioning.
    """

    def __init__(
        self,
        master,
        width: int = 500,
        height: int = 200,
        clef: str = "treble",
        line_spacing: int = 14,
        show_note_names: bool = False,
        time_signature: Optional[str] = None,
        **kwargs,
    ):
        super().__init__(master, fg_color=("#F8FAFC", "#0F172A"), **kwargs)
        self.canvas_width = width
        self.canvas_height = height
        self.clef = clef
        self.line_spacing = line_spacing
        self.show_note_names = show_note_names
        self.time_signature = time_signature

        self.notes: List[Note] = []
        self.durations: List[float] = []
        self.note_colors: List[str] = []

        # Coordinate references
        self.staff_top_y = (self.canvas_height - (4 * self.line_spacing)) // 2
        self.staff_bottom_y = self.staff_top_y + (4 * self.line_spacing)

        self.canvas = tk.Canvas(
            self,
            width=self.canvas_width,
            height=self.canvas_height,
            bg="#1E293B",  # Slate 800
            highlightthickness=1,
            highlightbackground="#334155",
        )
        self.canvas.pack(padx=6, pady=6)
        self.redraw()

    def set_clef(self, clef: str):
        """Sets the clef ('treble' or 'bass') and refreshes."""
        self.clef = clef
        self.redraw()

    def set_time_signature(self, time_signature: Optional[str]):
        """Sets time signature (e.g. '4/4', '3/4', '6/8') and redraws."""
        self.time_signature = time_signature
        self.redraw()

    def set_notes(self, notes: List[Note], colors: Optional[List[str]] = None, durations: Optional[List[float]] = None):
        """Sets notes and optional durations to be rendered on the staff."""
        self.notes = list(notes)
        self.durations = list(durations) if durations else [1.0] * len(self.notes)
        if colors:
            self.note_colors = colors
        else:
            self.note_colors = ["#38BDF8"] * len(self.notes)  # Sky blue default
        self.redraw()

    def set_single_note(self, note: Note, color: str = "#38BDF8"):
        """Displays a single note centered on the staff."""
        self.set_notes([note], [color], [1.0])

    def clear(self):
        """Clears all notes from the staff."""
        self.notes.clear()
        self.durations.clear()
        self.note_colors.clear()
        self.redraw()

    def _get_note_y(self, note: Note) -> float:
        """
        Calculates the Y coordinate for a given note's diatonic pitch.
        Treble clef: Bottom line (Line 1) is E4 (diatonic step 30).
        Bass clef: Bottom line (Line 1) is G2 (diatonic step 18).
        Each diatonic step moves the note up by half the line spacing (line_spacing / 2).
        """
        if self.clef == "treble":
            base_step = 4 * 7 + DIATONIC_STEPS["E"]  # E4 = 30
        else:
            base_step = 2 * 7 + DIATONIC_STEPS["G"]  # G2 = 18

        diff_steps = note.diatonic_step - base_step
        y = self.staff_bottom_y - (diff_steps * (self.line_spacing / 2.0))
        return y

    def redraw(self):
        """Redraws the staff lines, clef symbol, time signature, barlines, ledger lines, and all notes."""
        self.canvas.delete("all")

        # 1. Draw 5 Staff Lines
        line_color = "#94A3B8"  # Slate 400
        start_x = 30
        end_x = self.canvas_width - 30

        for i in range(5):
            y = self.staff_top_y + (i * self.line_spacing)
            self.canvas.create_line(
                start_x, y, end_x, y,
                fill=line_color,
                width=2,
            )

        # 2. Draw Clef Symbol
        clef_x = 55
        if self.clef == "treble":
            # Treble Clef 𝄞
            self.canvas.create_text(
                clef_x,
                self.staff_top_y + (2 * self.line_spacing) + 2,
                text="𝄞",
                font=("Georgia", 56),
                fill="#F8FAFC",
            )
            self.canvas.create_text(
                clef_x + 35,
                self.staff_bottom_y + 24,
                text="Clave de Sol",
                font=("Helvetica", 9, "bold"),
                fill="#64748B",
            )
        else:
            # Bass Clef 𝄢
            self.canvas.create_text(
                clef_x,
                self.staff_top_y + (1.2 * self.line_spacing),
                text="𝄢",
                font=("Georgia", 48),
                fill="#F8FAFC",
            )
            self.canvas.create_text(
                clef_x + 35,
                self.staff_bottom_y + 24,
                text="Clave de Fá",
                font=("Helvetica", 9, "bold"),
                fill="#64748B",
            )

        # 3. Draw Time Signature (if present)
        ts_offset_x = 0
        if self.time_signature and "/" in self.time_signature:
            ts_x = clef_x + 46
            ts_offset_x = 32
            num, den = self.time_signature.split("/")[:2]
            # Draw Numerator & Denominator stacked
            self.canvas.create_text(
                ts_x,
                self.staff_top_y + (1 * self.line_spacing),
                text=num,
                font=("Helvetica", 18, "bold"),
                fill="#F8FAFC",
            )
            self.canvas.create_text(
                ts_x,
                self.staff_top_y + (3 * self.line_spacing),
                text=den,
                font=("Helvetica", 18, "bold"),
                fill="#F8FAFC",
            )

        # 4. Draw Notes & Barlines
        if not self.notes:
            return

        num_notes = len(self.notes)
        content_start_x = 120 + ts_offset_x
        available_width = end_x - content_start_x - 30

        if num_notes == 1:
            note_x_positions = [content_start_x + available_width // 2]
        else:
            spacing = available_width / max(1, num_notes - 1)
            note_x_positions = [content_start_x + int(i * spacing) for i in range(num_notes)]

        # Calculate measure beats for barlines
        beats_per_bar = 4.0
        if self.time_signature and "/" in self.time_signature:
            try:
                n_val, d_val = self.time_signature.split("/")[:2]
                beats_per_bar = float(n_val) * (4.0 / float(d_val))
            except Exception:
                beats_per_bar = 4.0

        cum_beats = 0.0
        for i, note in enumerate(self.notes):
            nx = note_x_positions[i]
            ny = self._get_note_y(note)
            color = self.note_colors[i] if i < len(self.note_colors) else "#38BDF8"
            dur = self.durations[i] if i < len(self.durations) else 1.0

            # Draw barline if reaching measure boundary
            cum_beats += dur
            if num_notes > 2 and (cum_beats % beats_per_bar == 0) and i < num_notes - 1:
                next_nx = note_x_positions[i + 1]
                bar_x = (nx + next_nx) / 2.0
                self.canvas.create_line(
                    bar_x, self.staff_top_y,
                    bar_x, self.staff_bottom_y,
                    fill="#94A3B8",
                    width=2,
                )

            self._draw_ledger_lines(nx, ny)
            self._draw_notehead(nx, ny, color, duration=dur)
            self._draw_accidental(nx, ny, note, color)
            self._draw_stem(nx, ny, color)

            if self.show_note_names:
                dur_text = f"{dur:g}t" if dur != 1.0 else ""
                label = f"{note.pitch} ({note.name_pt}) {dur_text}".strip()
                self.canvas.create_text(
                    nx,
                    self.staff_bottom_y + 25,
                    text=label,
                    font=("Helvetica", 10, "bold"),
                    fill="#E2E8F0",
                )

    def _draw_ledger_lines(self, x: float, y: float):
        """Draws ledger lines if the note is above or below the 5-line staff."""
        ledger_color = "#94A3B8"
        ledger_half_width = 16

        # Below staff
        if y > self.staff_bottom_y + (self.line_spacing / 4.0):
            curr_y = self.staff_bottom_y + self.line_spacing
            while curr_y <= y + (self.line_spacing / 4.0):
                self.canvas.create_line(
                    x - ledger_half_width, curr_y,
                    x + ledger_half_width, curr_y,
                    fill=ledger_color,
                    width=2,
                )
                curr_y += self.line_spacing

        # Above staff
        elif y < self.staff_top_y - (self.line_spacing / 4.0):
            curr_y = self.staff_top_y - self.line_spacing
            while curr_y >= y - (self.line_spacing / 4.0):
                self.canvas.create_line(
                    x - ledger_half_width, curr_y,
                    x + ledger_half_width, curr_y,
                    fill=ledger_color,
                    width=2,
                )
                curr_y -= self.line_spacing

    def _draw_notehead(self, x: float, y: float, color: str, duration: float = 1.0):
        """Draws an elliptical notehead (hollow for half/whole notes, filled for quarter/eighth)."""
        rx = 8.5
        ry = 6.0
        is_hollow = (duration >= 2.0)
        self.canvas.create_oval(
            x - rx, y - ry,
            x + rx, y + ry,
            fill="#1E293B" if is_hollow else color,
            outline=color if is_hollow else "#FFFFFF",
            width=2.5 if is_hollow else 1.5,
        )

    def _draw_accidental(self, x: float, y: float, note: Note, color: str):
        """Draws a sharp or flat symbol in front of the notehead."""
        if not note.accidental:
            return

        symbol = "♯" if note.accidental == "#" else "♭"
        font_size = 18 if note.accidental == "#" else 20
        offset_y = -1 if note.accidental == "#" else -4

        self.canvas.create_text(
            x - 18,
            y + offset_y,
            text=symbol,
            font=("Helvetica", font_size, "bold"),
            fill=color,
        )

    def _draw_stem(self, x: float, y: float, color: str):
        """Draws the vertical stem attached to the notehead."""
        staff_mid_y = self.staff_top_y + (2 * self.line_spacing)
        stem_length = 3.2 * self.line_spacing

        if y >= staff_mid_y:
            # Stem points upwards on the right side
            self.canvas.create_line(
                x + 7.5, y,
                x + 7.5, y - stem_length,
                fill=color,
                width=2,
            )
        else:
            # Stem points downwards on the left side
            self.canvas.create_line(
                x - 7.5, y,
                x - 7.5, y + stem_length,
                fill=color,
                width=2,
            )
