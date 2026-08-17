"""Interactive Multi-Bar Step Sequencer Rhythm Grid Canvas widget with horizontal scrolling.

Draws a multi-bar (e.g. 16, 32, 64, 128, 256 steps) matrix for percussion instruments
using high-performance canvas rectangles, a fixed instrument label column on the left,
numbered bar headers with distinct visual dividers, and smooth horizontal scrolling.
"""
from typing import Callable, Dict, List, Optional, Tuple
import tkinter as tk
import customtkinter as ctk
from gui import theme

DRUM_ROWS = [
    ("kick", "🥁 Bombo (Kick)", "#EF4444"),
    ("snare", "🪘 Tarola (Snare)", "#F59E0B"),
    ("hihat_closed", "🥢 Hi-Hat Fechado", "#10B981"),
    ("hihat_open", "🔔 Hi-Hat Aberto", "#06B6D4"),
    ("ride", "✨ Prato Ride", "#8B5CF6"),
]


class StepGrid(ctk.CTkFrame):
    """
    High-performance canvas-based multi-bar step grid with fixed left header column and horizontal scrollbar.
    """

    def __init__(
        self,
        master,
        grid: Optional[List[List[str]]] = None,
        steps_per_bar: int = 16,
        bars: int = 4,
        on_grid_change: Optional[Callable[[List[List[str]]], None]] = None,
        **kwargs,
    ):
        super().__init__(master, fg_color=theme.COLOR_SURFACE, corner_radius=theme.RADIUS_MD, **kwargs)
        self.steps_per_bar = max(4, steps_per_bar)
        self.bars = max(1, bars)
        self.total_steps = self.bars * self.steps_per_bar
        self.on_grid_change = on_grid_change

        # Initialize grid copy with total_steps length
        if grid:
            self.grid_data: List[List[str]] = [list(step) for step in grid]
        else:
            self.grid_data = [[] for _ in range(self.total_steps)]

        # Ensure grid matches total_steps count
        while len(self.grid_data) < self.total_steps:
            self.grid_data.append([])
        if len(self.grid_data) > self.total_steps:
            self.grid_data = self.grid_data[:self.total_steps]

        self._cell_regions: Dict[Tuple[int, int], Tuple[int, int, int, int]] = {}  # (row_idx, step_idx) -> (x1, y1, x2, y2)
        self.row_height = 34.0
        self.header_height = 28.0
        self.step_width = 24.0
        self.label_width = 155

        self.canvas_height = int(len(DRUM_ROWS) * self.row_height + self.header_height + 8)

        self._build_ui()

    def _build_ui(self):
        # 1. Top container holding Fixed Label Canvas + Scrollable Grid Canvas
        self.grid_container = ctk.CTkFrame(self, fg_color="transparent")
        self.grid_container.pack(fill="both", expand=True, padx=10, pady=(8, 0))

        # Left Fixed Canvas for Drum Labels
        bg_col = theme.COLOR_SURFACE[1] if isinstance(theme.COLOR_SURFACE, tuple) else theme.COLOR_SURFACE
        self.label_canvas = tk.Canvas(
            self.grid_container,
            width=self.label_width,
            height=self.canvas_height,
            bg=bg_col,
            highlightthickness=0,
        )
        self.label_canvas.pack(side="left", fill="y")

        # Right Scrollable Canvas for Steps
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

    def set_grid(self, grid: List[List[str]], steps_per_bar: int = 16, bars: int = 4):
        """Updates the active rhythm matrix, bar count, and redraws the canvas."""
        self.steps_per_bar = max(4, steps_per_bar)
        self.bars = max(1, bars)
        self.total_steps = self.bars * self.steps_per_bar

        self.grid_data = [list(step) for step in grid]
        while len(self.grid_data) < self.total_steps:
            self.grid_data.append([])
        if len(self.grid_data) > self.total_steps:
            self.grid_data = self.grid_data[:self.total_steps]
        self.redraw()

    def get_grid(self) -> List[List[str]]:
        return [list(step) for step in self.grid_data]

    def clear(self):
        self.grid_data = [[] for _ in range(self.total_steps)]
        self.redraw()
        if self.on_grid_change:
            self.on_grid_change(self.grid_data)

    def redraw(self):
        """Redraws the fixed labels and multi-bar step matrix."""
        # 1. Redraw Left Labels Canvas
        self.label_canvas.delete("all")
        for r_idx, (inst_key, inst_label, color) in enumerate(DRUM_ROWS):
            y1 = self.header_height + r_idx * self.row_height
            y2 = y1 + self.row_height - 5
            self.label_canvas.create_text(
                8, (y1 + y2) / 2, text=inst_label, anchor="w", fill="#F1F5F9", font=("Helvetica", 11, "bold")
            )

        # 2. Redraw Right Scrollable Steps Canvas
        self.step_canvas.delete("all")
        self._cell_regions.clear()

        total_grid_width = max(self.step_canvas.winfo_width(), int(self.total_steps * self.step_width + 20))
        self.step_canvas.config(scrollregion=(0, 0, total_grid_width, self.canvas_height))

        # Draw Step Headers & Bar Numbers
        for step in range(self.total_steps):
            x1 = step * self.step_width + 4
            x2 = x1 + self.step_width - 3
            center_x = (x1 + x2) / 2

            bar_idx = step // self.steps_per_bar + 1
            step_in_bar = step % self.steps_per_bar
            is_bar_start = (step_in_bar == 0)
            is_beat_start = (step_in_bar % 4 == 0) if self.steps_per_bar == 16 else (step_in_bar % 3 == 0)

            # Draw bar header label at the beginning of each bar
            if is_bar_start:
                self.step_canvas.create_text(
                    x1 + 2, 8, text=f"Comp {bar_idx}", anchor="w", fill="#38BDF8", font=("Helvetica", 10, "bold")
                )

            # Step number label
            text_color = "#FFFFFF" if is_bar_start else ("#CBD5E1" if is_beat_start else "#64748B")
            step_lbl = f"{step_in_bar // 4 + 1}" if (is_beat_start and self.steps_per_bar == 16) else f"{step_in_bar + 1}"
            self.step_canvas.create_text(
                center_x, 20, text=step_lbl, fill=text_color, font=("Helvetica", 9, "bold" if is_beat_start else "normal")
            )

            # Draw Bar Divider Line
            if is_bar_start and step > 0:
                self.step_canvas.create_line(
                    x1 - 2, 0, x1 - 2, self.canvas_height, fill="#64748B", width=2
                )

        # Draw Instrument Rows and Multi-Bar Cells
        for r_idx, (inst_key, inst_label, color) in enumerate(DRUM_ROWS):
            y1 = self.header_height + r_idx * self.row_height
            y2 = y1 + self.row_height - 5

            for s_idx in range(self.total_steps):
                x1 = s_idx * self.step_width + 4
                x2 = x1 + self.step_width - 3

                is_active = (s_idx < len(self.grid_data) and inst_key in self.grid_data[s_idx])
                step_in_bar = s_idx % self.steps_per_bar
                is_beat_group = (step_in_bar // 4) % 2 == 0 if self.steps_per_bar == 16 else (step_in_bar // 3) % 2 == 0

                if is_active:
                    fill_color = color
                    outline_color = "#FFFFFF"
                else:
                    fill_color = "#1E293B" if is_beat_group else "#0F172A"
                    outline_color = "#334155"

                rect_id = self.step_canvas.create_rectangle(
                    x1, y1, x2, y2, fill=fill_color, outline=outline_color, width=1.5 if is_active else 1
                )
                self._cell_regions[(r_idx, s_idx)] = (int(x1), int(y1), int(x2), int(y2))

    def _on_step_canvas_click(self, event):
        # Convert viewport click to canvas scrollregion coordinates
        canvas_x = self.step_canvas.canvasx(event.x)
        canvas_y = self.step_canvas.canvasy(event.y)

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
                break
