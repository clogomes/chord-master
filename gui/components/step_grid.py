"""Interactive Step Sequencer Rhythm Grid Canvas widget.

Draws a 16-step matrix for percussion instruments using lightweight canvas rectangles
with hover effects, beat grouping markers, and immediate toggle callbacks.
Zero child widget overhead.
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
    High-performance canvas-based step grid for interactive rhythm editing.
    """

    def __init__(
        self,
        master,
        grid: Optional[List[List[str]]] = None,
        steps_per_bar: int = 16,
        on_grid_change: Optional[Callable[[List[List[str]]], None]] = None,
        **kwargs,
    ):
        super().__init__(master, fg_color=theme.COLOR_SURFACE, corner_radius=theme.RADIUS_MD, **kwargs)
        self.steps_per_bar = max(4, steps_per_bar)
        self.on_grid_change = on_grid_change

        # Initialize grid copy
        if grid:
            self.grid_data: List[List[str]] = [list(step) for step in grid]
        else:
            self.grid_data = [[] for _ in range(self.steps_per_bar)]

        # Ensure grid matches step count
        while len(self.grid_data) < self.steps_per_bar:
            self.grid_data.append([])
        if len(self.grid_data) > self.steps_per_bar:
            self.grid_data = self.grid_data[:self.steps_per_bar]

        self._cell_regions: Dict[Tuple[int, int], Tuple[int, int, int, int]] = {}  # (row_idx, step_idx) -> (x1, y1, x2, y2)
        self._current_step_cursor: Optional[int] = None

        # Build Canvas
        self.canvas_height = len(DRUM_ROWS) * 36 + 32
        self.canvas = tk.Canvas(
            self,
            bg=theme.COLOR_SURFACE[1] if isinstance(theme.COLOR_SURFACE, tuple) else theme.COLOR_SURFACE,
            highlightthickness=0,
            height=self.canvas_height,
        )
        self.canvas.pack(fill="both", expand=True, padx=12, pady=10)

        self.canvas.bind("<Configure>", lambda e: self.redraw())
        self.canvas.bind("<Button-1>", self._on_canvas_click)

    def set_grid(self, grid: List[List[str]], steps_per_bar: int = 16):
        """Updates the active rhythm matrix and redraws the canvas."""
        self.steps_per_bar = max(4, steps_per_bar)
        self.grid_data = [list(step) for step in grid]
        while len(self.grid_data) < self.steps_per_bar:
            self.grid_data.append([])
        if len(self.grid_data) > self.steps_per_bar:
            self.grid_data = self.grid_data[:self.steps_per_bar]
        self.redraw()

    def get_grid(self) -> List[List[str]]:
        return [list(step) for step in self.grid_data]

    def clear(self):
        self.grid_data = [[] for _ in range(self.steps_per_bar)]
        self.redraw()
        if self.on_grid_change:
            self.on_grid_change(self.grid_data)

    def redraw(self):
        """Redraws all step buttons, track labels, and beat dividers on the canvas."""
        self.canvas.delete("all")
        self._cell_regions.clear()

        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        if width <= 50:
            return

        label_col_width = 155
        grid_width = width - label_col_width - 20
        step_width = max(18.0, grid_width / self.steps_per_bar)
        row_height = 34.0
        start_y = 26.0

        # Draw Step Header Numbers
        for step in range(self.steps_per_bar):
            x1 = label_col_width + step * step_width
            x2 = x1 + step_width - 3
            center_x = (x1 + x2) / 2
            is_beat_start = (step % 4 == 0) if self.steps_per_bar == 16 else (step % 3 == 0)
            text_color = "#F8FAFC" if is_beat_start else "#94A3B8"
            step_label = f"{step // 4 + 1}" if (is_beat_start and self.steps_per_bar == 16) else f"{step+1}"
            self.canvas.create_text(
                center_x, 14, text=step_label, fill=text_color, font=("Helvetica", 10, "bold" if is_beat_start else "normal")
            )

        # Draw Instrument Rows and Cells
        for r_idx, (inst_key, inst_label, color) in enumerate(DRUM_ROWS):
            y1 = start_y + r_idx * row_height
            y2 = y1 + row_height - 5

            # Instrument Label
            self.canvas.create_text(
                12, (y1 + y2) / 2, text=inst_label, anchor="w", fill="#F1F5F9", font=("Helvetica", 11, "bold")
            )

            # Step Rectangles
            for s_idx in range(self.steps_per_bar):
                x1 = label_col_width + s_idx * step_width
                x2 = x1 + step_width - 3

                is_active = (s_idx < len(self.grid_data) and inst_key in self.grid_data[s_idx])
                is_beat_group = (s_idx // 4) % 2 == 0 if self.steps_per_bar == 16 else (s_idx // 3) % 2 == 0

                if is_active:
                    fill_color = color
                    outline_color = "#FFFFFF"
                else:
                    fill_color = "#1E293B" if is_beat_group else "#0F172A"
                    outline_color = "#334155"

                # Draw cell rounded-look rectangle
                rect_id = self.canvas.create_rectangle(
                    x1, y1, x2, y2, fill=fill_color, outline=outline_color, width=1.5 if is_active else 1
                )
                self._cell_regions[(r_idx, s_idx)] = (int(x1), int(y1), int(x2), int(y2))

    def _on_canvas_click(self, event):
        x, y = event.x, event.y
        for (r_idx, s_idx), (x1, y1, x2, y2) in self._cell_regions.items():
            if x1 <= x <= x2 and y1 <= y <= y2:
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
