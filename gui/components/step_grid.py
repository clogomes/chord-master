"""Interactive Multi-Bar Step Sequencer Rhythm & Chord Grid Canvas widget with horizontal scrolling.

Draws a unified multi-bar (e.g. 16, 32, 64, 128, 256 steps) timeline matrix:
1. Upper Section: 12 Percussion instruments with step toggle cells.
2. Distinct Visual Divider.
3. Lower Section: Harmonic chord lanes (Piano & Viola) showing ChordEvents as horizontal blocks.
4. Fixed instrument label column on the left, smooth horizontal scrolling, mouse wheel scrolling,
   and clock-based playback cursor (playhead).
"""
from typing import Callable, Dict, List, Optional, Tuple
import tkinter as tk
import customtkinter as ctk
from core.composition import ChordEvent
from core.chords import CHORD_TYPES
from gui import theme

DRUM_ROWS = [
    ("kick", "🥁 Bombo (Kick)", "#EF4444"),
    ("snare", "🪘 Tarola (Snare)", "#F59E0B"),
    ("rimshot", "🥢 Aro / Side Stick", "#FB923C"),
    ("clap", "👏 Palmas (Clap)", "#EC4899"),
    ("tom_high", "🪘 Tom Agudo (High)", "#E11D48"),
    ("tom_mid", "🪘 Tom Médio (Mid)", "#EA580C"),
    ("tom_low", "🪘 Tom Grave (Low)", "#B45309"),
    ("hihat_closed", "🥢 Hi-Hat Fechado", "#10B981"),
    ("hihat_open", "🔔 Hi-Hat Aberto", "#06B6D4"),
    ("crash", "💥 Prato Crash", "#3B82F6"),
    ("ride", "✨ Prato Ride", "#8B5CF6"),
    ("cowbell", "🔔 Cowbell / Sino", "#A855F7"),
]

CHORD_LANES = [
    ("piano", "🎹 Acordes (Piano)", "#4F46E5"),
    ("guitar", "🎸 Acordes (Viola)", "#D97706"),
]


class StepGrid(ctk.CTkFrame):
    """
    Unified canvas-based multi-bar step sequencer, chord lane editor, and playback cursor display.
    """

    def __init__(
        self,
        master,
        grid: Optional[List[List[str]]] = None,
        chords: Optional[List[ChordEvent]] = None,
        steps_per_bar: int = 16,
        bars: int = 4,
        time_signature: str = "4/4",
        selected_chord_idx: Optional[int] = None,
        on_grid_change: Optional[Callable[[List[List[str]]], None]] = None,
        on_chord_click: Optional[Callable[[int], None]] = None,
        on_chord_lane_click: Optional[Callable[[str, float], None]] = None,
        **kwargs,
    ):
        super().__init__(master, fg_color=theme.COLOR_SURFACE, corner_radius=theme.RADIUS_MD, **kwargs)
        self.steps_per_bar = max(4, steps_per_bar)
        self.bars = max(1, bars)
        self.time_signature = time_signature
        self.total_steps = self.bars * self.steps_per_bar
        self.selected_chord_idx = selected_chord_idx
        self.on_grid_change = on_grid_change
        self.on_chord_click = on_chord_click
        self.on_chord_lane_click = on_chord_lane_click

        # Initialize grid copy with total_steps length
        if grid:
            self.grid_data: List[List[str]] = [list(step) for step in grid]
        else:
            self.grid_data = [[] for _ in range(self.total_steps)]

        while len(self.grid_data) < self.total_steps:
            self.grid_data.append([])
        if len(self.grid_data) > self.total_steps:
            self.grid_data = self.grid_data[:self.total_steps]

        self.chords_data: List[ChordEvent] = list(chords) if chords else []

        self._cell_regions: Dict[Tuple[int, int], Tuple[int, int, int, int]] = {}  # (drum_row_idx, step_idx) -> (x1, y1, x2, y2)
        self._chord_block_regions: List[Tuple[int, int, int, int, int]] = []      # (chord_idx, x1, y1, x2, y2)
        self._chord_lane_regions: List[Tuple[str, int, int, int, int]] = []       # (instrument, x1, y1, x2, y2)

        self.row_height = 32.0
        self.chord_row_height = 36.0
        self.header_height = 28.0
        self.divider_height = 16.0
        self.step_width = 24.0
        self.label_width = 160

        self.drums_height = len(DRUM_ROWS) * self.row_height
        self.chords_height = len(CHORD_LANES) * self.chord_row_height
        self.canvas_height = int(self.header_height + self.drums_height + self.divider_height + self.chords_height + 10)

        self.cursor_line_id: Optional[int] = None

        self._build_ui()

    def _build_ui(self):
        # Top container holding Fixed Label Canvas + Scrollable Grid Canvas
        self.grid_container = ctk.CTkFrame(self, fg_color="transparent")
        self.grid_container.pack(fill="both", expand=True, padx=10, pady=(8, 0))

        # Left Fixed Canvas for Track Labels (no horizontal scroll)
        bg_col = theme.COLOR_SURFACE[1] if isinstance(theme.COLOR_SURFACE, tuple) else theme.COLOR_SURFACE
        self.label_canvas = tk.Canvas(
            self.grid_container,
            width=self.label_width,
            height=self.canvas_height,
            bg=bg_col,
            highlightthickness=0,
        )
        self.label_canvas.pack(side="left", fill="y")

        # Right Scrollable Canvas for Steps and Chords
        self.step_canvas = tk.Canvas(
            self.grid_container,
            height=self.canvas_height,
            bg=bg_col,
            highlightthickness=0,
        )
        self.step_canvas.pack(side="left", fill="both", expand=True)

        # Horizontal Scrollbar
        self.h_scrollbar = ctk.CTkScrollbar(
            self,
            orientation="horizontal",
            command=self.step_canvas.xview,
            height=14,
        )
        self.h_scrollbar.pack(fill="x", padx=10, pady=(4, 8))
        self.step_canvas.configure(xscrollcommand=self.h_scrollbar.set)

        self.step_canvas.bind("<Configure>", lambda e: self.redraw())
        self.step_canvas.bind("<Button-1>", self._on_step_canvas_click)

        # Mouse wheel horizontal scroll bindings on step canvas
        self.step_canvas.bind("<MouseWheel>", self._on_mousewheel)
        self.step_canvas.bind("<Shift-MouseWheel>", self._on_mousewheel)
        self.step_canvas.bind("<Button-4>", lambda e: self.step_canvas.xview_scroll(-2, "units"))
        self.step_canvas.bind("<Button-5>", lambda e: self.step_canvas.xview_scroll(2, "units"))

    def _on_mousewheel(self, event):
        """Scrolls the step canvas horizontally with mouse wheel or trackpad."""
        delta = 0
        if hasattr(event, "delta") and event.delta != 0:
            # macOS uses smaller deltas; Windows uses multiples of 120
            delta = -1 if event.delta > 0 else 1
            if abs(event.delta) >= 120:
                delta = -int(event.delta / 40)
        elif hasattr(event, "num"):
            if event.num == 4:
                delta = -2
            elif event.num == 5:
                delta = 2

        if delta != 0:
            self.step_canvas.xview_scroll(delta, "units")

    def _get_beats_per_bar(self) -> int:
        if "/" in self.time_signature:
            try:
                return int(self.time_signature.split("/")[0])
            except Exception:
                return 4
        return 4

    def _get_steps_per_beat(self) -> float:
        beats_per_bar = self._get_beats_per_bar()
        return self.steps_per_bar / float(beats_per_bar)

    def set_data(
        self,
        grid: List[List[str]],
        chords: List[ChordEvent],
        steps_per_bar: int = 16,
        bars: int = 4,
        time_signature: str = "4/4",
        selected_chord_idx: Optional[int] = None,
    ):
        """Updates grid, chords, and timeline dimensions, then redraws."""
        self.steps_per_bar = max(4, steps_per_bar)
        self.bars = max(1, bars)
        self.time_signature = time_signature
        self.total_steps = self.bars * self.steps_per_bar
        self.selected_chord_idx = selected_chord_idx
        self.chords_data = list(chords) if chords else []

        self.grid_data = [list(step) for step in grid]
        while len(self.grid_data) < self.total_steps:
            self.grid_data.append([])
        if len(self.grid_data) > self.total_steps:
            self.grid_data = self.grid_data[:self.total_steps]
        self.redraw()

    def set_grid(self, grid: List[List[str]], steps_per_bar: int = 16, bars: int = 4):
        self.set_data(grid=grid, chords=self.chords_data, steps_per_bar=steps_per_bar, bars=bars, time_signature=self.time_signature, selected_chord_idx=self.selected_chord_idx)

    def set_chords(self, chords: List[ChordEvent], selected_chord_idx: Optional[int] = None):
        self.chords_data = list(chords) if chords else []
        self.selected_chord_idx = selected_chord_idx
        self.redraw()

    def get_grid(self) -> List[List[str]]:
        return [list(step) for step in self.grid_data]

    def clear(self):
        self.grid_data = [[] for _ in range(self.total_steps)]
        self.redraw()
        if self.on_grid_change:
            self.on_grid_change(self.grid_data)

    def update_playback_cursor(self, elapsed_seconds: float, bpm: int):
        """Updates the vertical playhead line position based on elapsed time without calling redraw()."""
        if elapsed_seconds < 0:
            self.hide_playback_cursor()
            return

        beats_per_bar = self._get_beats_per_bar()
        seconds_per_beat = 60.0 / bpm
        seconds_per_step = (beats_per_bar * seconds_per_beat) / self.steps_per_bar
        step_pos = elapsed_seconds / seconds_per_step

        pixel_x = 4 + step_pos * self.step_width

        total_grid_width = max(self.step_canvas.winfo_width(), int(self.total_steps * self.step_width + 20))

        # Ensure cursor line exists on canvas
        if self.cursor_line_id is None:
            self.cursor_line_id = self.step_canvas.create_line(
                pixel_x, 0, pixel_x, self.canvas_height,
                fill="#38BDF8", width=2.5, stipple="gray50", tag="playhead"
            )
        else:
            self.step_canvas.coords(self.cursor_line_id, pixel_x, 0, pixel_x, self.canvas_height)
            self.step_canvas.tag_raise(self.cursor_line_id)

        # Auto-scroll view if cursor moves past visible viewport
        if self.step_canvas.winfo_width() > 0 and total_grid_width > 0:
            xview_left, xview_right = self.step_canvas.xview()
            visible_start_px = xview_left * total_grid_width
            visible_end_px = xview_right * total_grid_width

            if pixel_x > (visible_end_px - 40) and pixel_x < total_grid_width:
                new_view_start = (pixel_x - 40) / float(total_grid_width)
                self.step_canvas.xview_moveto(max(0.0, min(1.0, new_view_start)))

    def hide_playback_cursor(self):
        """Hides and resets the playhead line."""
        if self.cursor_line_id is not None:
            self.step_canvas.coords(self.cursor_line_id, -10, 0, -10, self.canvas_height)

    def redraw(self):
        """Redraws the fixed labels and multi-bar step matrix including chord lanes."""
        # 1. Redraw Left Labels Canvas
        self.label_canvas.delete("all")
        
        # Percussion Header Label
        self.label_canvas.create_text(
            8, 14, text="🥁 PERCUSSÃO", anchor="w", fill="#94A3B8", font=("Helvetica", 9, "bold")
        )
        
        for r_idx, (inst_key, inst_label, color) in enumerate(DRUM_ROWS):
            y1 = self.header_height + r_idx * self.row_height
            y2 = y1 + self.row_height - 5
            self.label_canvas.create_text(
                8, (y1 + y2) / 2, text=inst_label, anchor="w", fill="#F1F5F9", font=("Helvetica", 10, "bold")
            )

        # Section Divider
        div_y = self.header_height + self.drums_height + 4
        self.label_canvas.create_line(0, div_y, self.label_width, div_y, fill="#475569", width=2)
        self.label_canvas.create_text(
            8, div_y + 10, text="🎼 HARMONIA / ACORDES", anchor="w", fill="#94A3B8", font=("Helvetica", 9, "bold")
        )

        chord_start_y = self.header_height + self.drums_height + self.divider_height + 4
        for l_idx, (inst_key, inst_label, color) in enumerate(CHORD_LANES):
            y1 = chord_start_y + l_idx * self.chord_row_height
            y2 = y1 + self.chord_row_height - 5
            self.label_canvas.create_text(
                8, (y1 + y2) / 2, text=inst_label, anchor="w", fill="#F1F5F9", font=("Helvetica", 10, "bold")
            )

        # 2. Redraw Right Scrollable Steps Canvas
        self.step_canvas.delete("all")
        self.cursor_line_id = None
        self._cell_regions.clear()
        self._chord_block_regions.clear()
        self._chord_lane_regions.clear()

        total_grid_width = max(self.step_canvas.winfo_width(), int(self.total_steps * self.step_width + 20))
        self.step_canvas.config(scrollregion=(0, 0, total_grid_width, self.canvas_height))

        steps_per_beat = self._get_steps_per_beat()

        # Draw Step Headers & Bar Numbers
        for step in range(self.total_steps):
            x1 = step * self.step_width + 4
            x2 = x1 + self.step_width - 3
            center_x = (x1 + x2) / 2

            bar_idx = step // self.steps_per_bar + 1
            step_in_bar = step % self.steps_per_bar
            is_bar_start = (step_in_bar == 0)
            is_beat_start = (step_in_bar % int(steps_per_beat) == 0)

            if is_bar_start:
                self.step_canvas.create_text(
                    x1 + 2, 8, text=f"Comp {bar_idx}", anchor="w", fill="#38BDF8", font=("Helvetica", 10, "bold")
                )

            text_color = "#FFFFFF" if is_bar_start else ("#CBD5E1" if is_beat_start else "#64748B")
            step_lbl = f"{int(step_in_bar // steps_per_beat) + 1}" if is_beat_start else f"{step_in_bar + 1}"
            self.step_canvas.create_text(
                center_x, 20, text=step_lbl, fill=text_color, font=("Helvetica", 9, "bold" if is_beat_start else "normal")
            )

            # Draw Vertical Bar Divider across the entire canvas height
            if is_bar_start and step > 0:
                self.step_canvas.create_line(
                    x1 - 2, 0, x1 - 2, self.canvas_height, fill="#64748B", width=2
                )

        # Draw Percussion Matrix
        for r_idx, (inst_key, inst_label, color) in enumerate(DRUM_ROWS):
            y1 = self.header_height + r_idx * self.row_height
            y2 = y1 + self.row_height - 5

            for s_idx in range(self.total_steps):
                x1 = s_idx * self.step_width + 4
                x2 = x1 + self.step_width - 3

                is_active = (s_idx < len(self.grid_data) and inst_key in self.grid_data[s_idx])
                step_in_bar = s_idx % self.steps_per_bar
                is_beat_group = (step_in_bar // int(steps_per_beat)) % 2 == 0

                if is_active:
                    fill_color = color
                    outline_color = "#FFFFFF"
                else:
                    fill_color = "#1E293B" if is_beat_group else "#0F172A"
                    outline_color = "#334155"

                self.step_canvas.create_rectangle(
                    x1, y1, x2, y2, fill=fill_color, outline=outline_color, width=1.5 if is_active else 1
                )
                self._cell_regions[(r_idx, s_idx)] = (int(x1), int(y1), int(x2), int(y2))

        # Horizontal Divider Line on Step Canvas
        self.step_canvas.create_line(0, div_y, total_grid_width, div_y, fill="#475569", width=2)

        # Draw Chord Lanes Background & Cells
        for l_idx, (lane_inst, lane_label, lane_color) in enumerate(CHORD_LANES):
            y1 = chord_start_y + l_idx * self.chord_row_height
            y2 = y1 + self.chord_row_height - 5

            # Background lane strip
            self.step_canvas.create_rectangle(
                4, y1, self.total_steps * self.step_width + 1, y2, fill="#0F172A", outline="#334155", width=1
            )
            self._chord_lane_regions.append((lane_inst, 4, int(y1), int(self.total_steps * self.step_width + 1), int(y2)))

            # Draw subtle beat guidelines on chord lane
            for s_idx in range(self.total_steps):
                if s_idx % int(steps_per_beat) == 0:
                    bx = s_idx * self.step_width + 4
                    self.step_canvas.create_line(bx, y1, bx, y2, fill="#1E293B", width=1)

        # Draw ChordEvent Blocks
        for c_idx, chord in enumerate(self.chords_data):
            lane_idx = 0 if chord.instrument == "piano" else 1
            y1 = chord_start_y + lane_idx * self.chord_row_height + 2
            y2 = y1 + self.chord_row_height - 7

            start_step = chord.start_beat * steps_per_beat
            end_step = (chord.start_beat + chord.duration_beats) * steps_per_beat

            x1 = start_step * self.step_width + 4
            x2 = end_step * self.step_width + 1
            is_selected = (self.selected_chord_idx == c_idx)

            base_color = CHORD_LANES[lane_idx][2]
            fill_color = "#6366F1" if (chord.instrument == "piano" and is_selected) else (
                "#F59E0B" if (chord.instrument == "guitar" and is_selected) else base_color
            )
            outline_col = "#FFFFFF" if is_selected else "#CBD5E1"

            self.step_canvas.create_rectangle(
                x1, y1, x2, y2, fill=fill_color, outline=outline_col, width=2 if is_selected else 1
            )
            self._chord_block_regions.append((c_idx, int(x1), int(y1), int(x2), int(y2)))

            sym = CHORD_TYPES.get(chord.chord_type, CHORD_TYPES["major"]).symbol or chord.chord_type
            chord_name = f"{chord.root}{sym}"
            block_width = x2 - x1
            if block_width >= 28:
                self.step_canvas.create_text(
                    (x1 + x2) / 2, (y1 + y2) / 2, text=chord_name, fill="#FFFFFF", font=("Helvetica", 10, "bold")
                )

    def _on_step_canvas_click(self, event):
        canvas_x = self.step_canvas.canvasx(event.x)
        canvas_y = self.step_canvas.canvasy(event.y)

        # 1. Check if click was on a Drum Step Cell
        for (r_idx, s_idx), (x1, y1, x2, y2) in self._cell_regions.items():
            if x1 <= canvas_x <= x2 and y1 <= canvas_y <= y2:
                inst_key = DRUM_ROWS[r_idx][0]
                if s_idx < len(self.grid_data):
                    step_list = self.grid_data[s_idx]
                    if inst_key in step_list:
                        step_list.remove(inst_key)
                    else:
                        step_list.append(inst_key)
                    self.redraw()
                    if self.on_grid_change:
                        self.on_grid_change(self.grid_data)
                return

        # 2. Check if click was on an existing Chord Block
        for c_idx, x1, y1, x2, y2 in self._chord_block_regions:
            if x1 <= canvas_x <= x2 and y1 <= canvas_y <= y2:
                self.selected_chord_idx = c_idx
                self.redraw()
                if self.on_chord_click:
                    self.on_chord_click(c_idx)
                return

        # 3. Check if click was on an empty area of a Chord Lane (to insert a chord at that beat)
        for lane_inst, x1, y1, x2, y2 in self._chord_lane_regions:
            if x1 <= canvas_x <= x2 and y1 <= canvas_y <= y2:
                steps_per_beat = self._get_steps_per_beat()
                clicked_step = max(0, (canvas_x - 4) / self.step_width)
                clicked_beat = round(clicked_step / steps_per_beat * 2.0) / 2.0  # Quantize to nearest 0.5 beat
                if self.on_chord_lane_click:
                    self.on_chord_lane_click(lane_inst, clicked_beat)
                return
