"""Interactive Piano Roll Canvas Component (Phase 56).

Features:
- Fixed vertical MIDI pitch ruler on the left (C3 48 to C6 84 or custom range)
- Horizontal step timeline aligned with the composition's bars and steps
- Pure canvas rendering of note blocks (zero widget explosion)
- Click to insert notes, drag to move, drag right edge to resize duration
- Selection, deletion via Delete/Backspace
- Dynamic synchronization with PianoKeyboard, GuitarFretboard, and StaffCanvas
"""
import math
import tkinter as tk
from typing import Callable, List, Optional, Tuple
import customtkinter as ctk

from core.composition import NoteEvent
from core.notes import NOTE_NAMES, NOTE_NAMES_PT, midi_to_note
from gui.scroll_utils import bind_mousewheel
from gui import theme

# Default pitch range for Piano Roll: C3 (48) to B5 (83) -> 36 semitones
DEFAULT_MIN_MIDI = 48
DEFAULT_MAX_MIDI = 83

ROW_HEIGHT = 16
PIANO_KEY_WIDTH = 70
STEP_WIDTH = 22
HEADER_HEIGHT = 26


class PianoRoll(ctk.CTkFrame):
    """
    Two-panel canvas piano roll:
    - Left Canvas: Fixed vertical piano key / pitch labels
    - Right Canvas: Scrollable note grid and draggable NoteEvent blocks
    """

    def __init__(
        self,
        master,
        notes: Optional[List[NoteEvent]] = None,
        bars: int = 4,
        steps_per_bar: int = 16,
        min_midi: int = DEFAULT_MIN_MIDI,
        max_midi: int = DEFAULT_MAX_MIDI,
        on_notes_changed: Optional[Callable[[List[NoteEvent]], None]] = None,
        on_note_selected: Optional[Callable[[Optional[NoteEvent]], None]] = None,
        **kwargs,
    ):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.notes: List[NoteEvent] = notes if notes is not None else []
        self.bars = max(1, bars)
        self.steps_per_bar = max(4, steps_per_bar)
        self.min_midi = min_midi
        self.max_midi = max_midi
        self.on_notes_changed = on_notes_changed
        self.on_note_selected = on_note_selected

        self.selected_note_idx: Optional[int] = None
        self.current_instrument = "piano"

        # Drag & Interaction state
        self._drag_mode: Optional[str] = None  # "move" | "resize"
        self._drag_note_idx: Optional[int] = None
        self._drag_start_x = 0
        self._drag_start_y = 0
        self._drag_orig_beat = 0.0
        self._drag_orig_midi = 60
        self._drag_orig_dur = 1.0
        self._is_dragging = False

        self._build_ui()
        self.redraw()

    def _build_ui(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        bg_surf = theme.COLOR_SURFACE[1] if isinstance(theme.COLOR_SURFACE, tuple) else theme.COLOR_SURFACE
        bg_main = theme.COLOR_BG[1] if isinstance(theme.COLOR_BG, tuple) else theme.COLOR_BG

        # 1. Left Pitch Label Canvas (Fixed)
        self.label_canvas = tk.Canvas(
            self,
            width=PIANO_KEY_WIDTH,
            bg=bg_surf,
            highlightthickness=0,
            bd=0,
        )
        self.label_canvas.grid(row=0, column=0, sticky="ns")

        # 2. Right Note Grid Canvas (Scrollable)
        self.grid_canvas = tk.Canvas(
            self,
            bg=bg_main,
            highlightthickness=0,
            bd=0,
        )
        self.grid_canvas.grid(row=0, column=1, sticky="nsew")

        # 3. Horizontal Scrollbar
        self.h_scrollbar = ctk.CTkScrollbar(
            self,
            orientation="horizontal",
            command=self._on_hscroll,
            height=12,
            corner_radius=theme.RADIUS_SM,
        )
        self.h_scrollbar.grid(row=1, column=1, sticky="ew", pady=(2, 0))
        self.grid_canvas.configure(xscrollcommand=self.h_scrollbar.set)

        # Bindings
        self.grid_canvas.bind("<ButtonPress-1>", self._on_press)
        self.grid_canvas.bind("<B1-Motion>", self._on_drag)
        self.grid_canvas.bind("<ButtonRelease-1>", self._on_release)
        self.grid_canvas.bind("<Escape>", lambda e: self._cancel_drag())
        self.grid_canvas.bind("<Delete>", self._on_delete_key)
        self.grid_canvas.bind("<BackSpace>", self._on_delete_key)

        # Mousewheel scroll support
        bind_mousewheel(self.grid_canvas, recursive=False)

    def _on_hscroll(self, *args):
        self.grid_canvas.xview(*args)

    def set_notes(self, notes: List[NoteEvent], selected_idx: Optional[int] = None):
        self.notes = notes
        self.selected_note_idx = selected_idx
        self.redraw()

    def set_bars(self, bars: int, steps_per_bar: int = 16):
        self.bars = max(1, bars)
        self.steps_per_bar = max(4, steps_per_bar)
        self.redraw()

    def set_instrument(self, instrument: str):
        self.current_instrument = instrument
        if self.selected_note_idx is not None and 0 <= self.selected_note_idx < len(self.notes):
            self.notes[self.selected_note_idx].instrument = instrument
            self.redraw()
            if self.on_notes_changed:
                self.on_notes_changed(self.notes)

    def _get_num_pitches(self) -> int:
        return self.max_midi - self.min_midi + 1

    def _midi_to_y(self, midi: int) -> float:
        # Highest pitch at top
        pitch_idx = self.max_midi - midi
        return HEADER_HEIGHT + pitch_idx * ROW_HEIGHT

    def _y_to_midi(self, y: float) -> int:
        rel_y = y - HEADER_HEIGHT
        pitch_idx = int(rel_y // ROW_HEIGHT)
        midi = self.max_midi - pitch_idx
        return max(self.min_midi, min(self.max_midi, midi))

    def _beat_to_x(self, beat: float) -> float:
        steps_per_beat = self.steps_per_bar / 4.0
        return beat * steps_per_beat * STEP_WIDTH

    def _x_to_beat(self, x: float) -> float:
        steps_per_beat = self.steps_per_bar / 4.0
        step_pos = x / float(STEP_WIDTH)
        beat = step_pos / steps_per_beat
        # Snap to nearest step (1/4 beat for 16 steps, etc.)
        snap_step = 1.0 / steps_per_beat
        snapped_beat = round(beat / snap_step) * snap_step
        return max(0.0, snapped_beat)

    def redraw(self):
        self.label_canvas.delete("all")
        self.grid_canvas.delete("all")

        total_steps = self.bars * self.steps_per_bar
        total_width = total_steps * STEP_WIDTH
        total_height = HEADER_HEIGHT + self._get_num_pitches() * ROW_HEIGHT

        self.grid_canvas.configure(scrollregion=(0, 0, total_width, total_height))
        self.label_canvas.configure(height=total_height)

        # Draw Left Pitch Keys
        for midi in range(self.min_midi, self.max_midi + 1):
            y = self._midi_to_y(midi)
            semitone = midi % 12
            is_black = semitone in (1, 3, 6, 8, 10)
            key_color = "#1E293B" if is_black else "#334155"
            text_color = "#94A3B8" if is_black else "#F1F5F9"

            self.label_canvas.create_rectangle(
                0, y, PIANO_KEY_WIDTH, y + ROW_HEIGHT,
                fill=key_color, outline="#1E293B" if not is_black else "#0F172A",
            )
            pitch_name, octv = midi_to_note(midi)
            lbl = f"{pitch_name}{octv}"
            self.label_canvas.create_text(
                PIANO_KEY_WIDTH - 8, y + ROW_HEIGHT / 2,
                text=lbl, anchor="e",
                fill=text_color, font=("Helvetica", 9, "bold" if semitone == 0 else "normal"),
            )

        # Draw Right Grid Background
        for midi in range(self.min_midi, self.max_midi + 1):
            y = self._midi_to_y(midi)
            semitone = midi % 12
            is_black = semitone in (1, 3, 6, 8, 10)
            bg_row = "#0B0F19" if not is_black else "#080C14"
            self.grid_canvas.create_rectangle(
                0, y, total_width, y + ROW_HEIGHT,
                fill=bg_row, outline="#1E293B", width=1,
            )

        # Draw Step Vertical Grid Lines & Bar Dividers
        for step in range(total_steps + 1):
            x = step * STEP_WIDTH
            is_bar_start = (step % self.steps_per_bar == 0)
            is_beat_start = (step % (self.steps_per_bar // 4) == 0) if self.steps_per_bar >= 4 else False

            line_color = "#475569" if is_bar_start else ("#334155" if is_beat_start else "#1E293B")
            line_width = 2 if is_bar_start else 1

            self.grid_canvas.create_line(x, 0, x, total_height, fill=line_color, width=line_width)

            # Bar Numbers at top header
            if is_bar_start and step < total_steps:
                bar_num = (step // self.steps_per_bar) + 1
                self.grid_canvas.create_text(
                    x + 6, 12, text=f"Compasso {bar_num}",
                    anchor="w", fill="#38BDF8", font=("Helvetica", 10, "bold"),
                )

        # Draw Notes
        for idx, ne in enumerate(self.notes):
            self._draw_note_block(idx, ne)

    def _draw_note_block(self, idx: int, ne: NoteEvent, is_ghost: bool = False):
        if not (self.min_midi <= ne.midi <= self.max_midi):
            return

        x1 = self._beat_to_x(ne.start_beat)
        x2 = self._beat_to_x(ne.start_beat + ne.duration_beats)
        y1 = self._midi_to_y(ne.midi)
        y2 = y1 + ROW_HEIGHT

        is_selected = (idx == self.selected_note_idx)
        inst = getattr(ne, "instrument", "piano")

        if is_ghost:
            fill_col = "#F59E0B"
            outline_col = "#FFFFFF"
            stipple = "gray50"
        elif is_selected:
            fill_col = "#38BDF8"
            outline_col = "#FFFFFF"
            stipple = ""
        else:
            fill_col = "#4F46E5" if inst == "piano" else "#10B981"
            outline_col = "#818CF8" if inst == "piano" else "#34D399"
            stipple = ""

        # Draw Main Note Rectangle
        self.grid_canvas.create_rectangle(
            x1 + 1, y1 + 1, x2 - 1, y2 - 1,
            fill=fill_col, outline=outline_col, width=2 if is_selected else 1,
            stipple=stipple, tags=(f"note_{idx}", "note_item"),
        )

        # Right Resize Handle indicator if selected
        if is_selected and not is_ghost:
            self.grid_canvas.create_rectangle(
                x2 - 5, y1 + 2, x2 - 1, y2 - 2,
                fill="#FFFFFF", outline="", tags=(f"note_{idx}", "note_item"),
            )

        # Note Label
        pitch_name, octv = midi_to_note(ne.midi)
        lbl_text = f"{pitch_name}{octv}"
        if (x2 - x1) >= 28:
            self.grid_canvas.create_text(
                x1 + 4, y1 + ROW_HEIGHT / 2,
                text=lbl_text, anchor="w",
                fill="#FFFFFF", font=("Helvetica", 9, "bold"),
                tags=(f"note_{idx}", "note_item"),
            )

    def _find_note_at(self, canvas_x: float, canvas_y: float) -> Tuple[Optional[int], str]:
        """Returns (note_index, target_zone) where target_zone is 'move', 'resize', or 'none'."""
        for idx in reversed(range(len(self.notes))):
            ne = self.notes[idx]
            x1 = self._beat_to_x(ne.start_beat)
            x2 = self._beat_to_x(ne.start_beat + ne.duration_beats)
            y1 = self._midi_to_y(ne.midi)
            y2 = y1 + ROW_HEIGHT

            if x1 <= canvas_x <= x2 and y1 <= canvas_y <= y2:
                # If within 8 pixels of right edge -> resize
                if canvas_x >= x2 - 8:
                    return idx, "resize"
                return idx, "move"
        return None, "none"

    def _on_press(self, event):
        canvas_x = self.grid_canvas.canvasx(event.x)
        canvas_y = self.grid_canvas.canvasy(event.y)

        self._drag_start_x = canvas_x
        self._drag_start_y = canvas_y
        self._is_dragging = False

        note_idx, zone = self._find_note_at(canvas_x, canvas_y)

        if note_idx is not None:
            self.selected_note_idx = note_idx
            self._drag_note_idx = note_idx
            self._drag_mode = zone
            ne = self.notes[note_idx]
            self._drag_orig_beat = ne.start_beat
            self._drag_orig_midi = ne.midi
            self._drag_orig_dur = ne.duration_beats
            self.redraw()
            if self.on_note_selected:
                self.on_note_selected(ne)
        else:
            # Clicked empty space: Create a new 1-beat note
            new_beat = self._x_to_beat(canvas_x)
            new_midi = self._y_to_midi(canvas_y)
            max_beats = self.bars * 4.0

            if new_beat < max_beats:
                dur = min(1.0, max_beats - new_beat)
                new_note = NoteEvent(
                    midi=new_midi,
                    start_beat=new_beat,
                    duration_beats=dur,
                    velocity=0.8,
                    instrument=self.current_instrument,
                )
                self.notes.append(new_note)
                self.selected_note_idx = len(self.notes) - 1
                self.redraw()
                if self.on_notes_changed:
                    self.on_notes_changed(self.notes)
                if self.on_note_selected:
                    self.on_note_selected(new_note)

    def _on_drag(self, event):
        if self._drag_note_idx is None or self._drag_note_idx >= len(self.notes):
            return

        canvas_x = self.grid_canvas.canvasx(event.x)
        canvas_y = self.grid_canvas.canvasy(event.y)

        dx = canvas_x - self._drag_start_x
        dy = canvas_y - self._drag_start_y

        if not self._is_dragging and (abs(dx) > 4 or abs(dy) > 4):
            self._is_dragging = True

        if self._is_dragging:
            self.grid_canvas.delete("ghost_block")
            ne = self.notes[self._drag_note_idx]
            max_beats = self.bars * 4.0

            if self._drag_mode == "resize":
                # Resizing duration
                curr_beat = self._x_to_beat(canvas_x)
                new_dur = max(0.25, curr_beat - self._drag_orig_beat)
                if self._drag_orig_beat + new_dur > max_beats:
                    new_dur = max_beats - self._drag_orig_beat
                ghost = NoteEvent(
                    midi=self._drag_orig_midi,
                    start_beat=self._drag_orig_beat,
                    duration_beats=new_dur,
                    velocity=ne.velocity,
                    instrument=ne.instrument,
                )
            else:
                # Moving position and pitch
                delta_beat = self._x_to_beat(canvas_x) - self._x_to_beat(self._drag_start_x)
                new_beat = max(0.0, min(max_beats - self._drag_orig_dur, self._drag_orig_beat + delta_beat))
                new_midi = self._y_to_midi(canvas_y)
                ghost = NoteEvent(
                    midi=new_midi,
                    start_beat=new_beat,
                    duration_beats=self._drag_orig_dur,
                    velocity=ne.velocity,
                    instrument=ne.instrument,
                )

            # Draw ghost
            x1 = self._beat_to_x(ghost.start_beat)
            x2 = self._beat_to_x(ghost.start_beat + ghost.duration_beats)
            y1 = self._midi_to_y(ghost.midi)
            y2 = y1 + ROW_HEIGHT
            self.grid_canvas.create_rectangle(
                x1 + 1, y1 + 1, x2 - 1, y2 - 1,
                fill="#F59E0B", outline="#FFFFFF", width=2, stipple="gray50",
                tags=("ghost_block",),
            )

    def _on_release(self, event):
        self.grid_canvas.delete("ghost_block")
        if self._is_dragging and self._drag_note_idx is not None and self._drag_note_idx < len(self.notes):
            canvas_x = self.grid_canvas.canvasx(event.x)
            canvas_y = self.grid_canvas.canvasy(event.y)
            ne = self.notes[self._drag_note_idx]
            max_beats = self.bars * 4.0

            if self._drag_mode == "resize":
                curr_beat = self._x_to_beat(canvas_x)
                new_dur = max(0.25, curr_beat - self._drag_orig_beat)
                if self._drag_orig_beat + new_dur > max_beats:
                    new_dur = max_beats - self._drag_orig_beat
                ne.duration_beats = new_dur
            else:
                delta_beat = self._x_to_beat(canvas_x) - self._x_to_beat(self._drag_start_x)
                new_beat = max(0.0, min(max_beats - self._drag_orig_dur, self._drag_orig_beat + delta_beat))
                new_midi = self._y_to_midi(canvas_y)
                ne.start_beat = new_beat
                ne.midi = new_midi

            self.redraw()
            if self.on_notes_changed:
                self.on_notes_changed(self.notes)
            if self.on_note_selected:
                self.on_note_selected(ne)

        self._drag_mode = None
        self._drag_note_idx = None
        self._is_dragging = False

    def _cancel_drag(self):
        self.grid_canvas.delete("ghost_block")
        self._drag_mode = None
        self._drag_note_idx = None
        self._is_dragging = False
        self.redraw()

    def _on_delete_key(self, event=None):
        if self.selected_note_idx is not None and 0 <= self.selected_note_idx < len(self.notes):
            del self.notes[self.selected_note_idx]
            self.selected_note_idx = None
            self.redraw()
            if self.on_notes_changed:
                self.on_notes_changed(self.notes)
            if self.on_note_selected:
                self.on_note_selected(None)

    def delete_selected_note(self):
        self._on_delete_key()
