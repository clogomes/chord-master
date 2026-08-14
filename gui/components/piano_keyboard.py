"""Interactive, visually responsive 2-octave piano keyboard component."""
import tkinter as tk
from typing import Callable, Dict, List, Optional, Set
import customtkinter as ctk
from core.notes import Note, NOTE_NAMES
from audio.player import get_audio_player


class PianoKeyboard(ctk.CTkFrame):
    """
    An interactive piano keyboard widget capable of playing audio on touch,
    visualizing chords, scales, and receiving user input for quizzes.
    """

    WHITE_NOTES = ["C", "D", "E", "F", "G", "A", "B"]
    BLACK_NOTES = {
        "C#": 0,  # relative to white key index 0 (C)
        "D#": 1,  # relative to D
        "F#": 3,  # relative to F
        "G#": 4,  # relative to G
        "A#": 5,  # relative to A
    }

    def __init__(
        self,
        master,
        start_octave: int = 3,
        num_octaves: int = 2,
        key_width: int = 42,
        key_height: int = 150,
        show_labels: bool = True,
        on_key_click: Optional[Callable[[Note], None]] = None,
        enable_audio: bool = True,
        **kwargs,
    ):
        super().__init__(master, fg_color=("#F8FAFC", "#0F172A"), **kwargs)
        self.start_octave = start_octave
        self.num_octaves = num_octaves
        self.key_width = key_width
        self.key_height = key_height
        self.black_width = int(key_width * 0.65)
        self.black_height = int(key_height * 0.62)
        self.show_labels = show_labels
        self.on_key_click = on_key_click
        self.enable_audio = enable_audio
        self.audio_player = get_audio_player()

        self.highlighted_midis: Dict[int, str] = {}  # midi -> color hex

        # Calculate canvas dimensions
        total_white_keys = self.num_octaves * 7
        self.canvas_width = total_white_keys * self.key_width + 4
        self.canvas_height = self.key_height + 4

        self.canvas = tk.Canvas(
            self,
            width=self.canvas_width,
            height=self.canvas_height,
            bg="#1E293B",  # Dark slate background
            highlightthickness=0,
            cursor="hand2",
        )
        self.canvas.pack(padx=6, pady=6)

        # Mapping for click detection
        self._key_regions: List[Dict] = []  # list of dicts with bounds and note
        self._hovered_note: Optional[Note] = None

        self.canvas.bind("<Button-1>", self._on_canvas_click)
        self.canvas.bind("<Motion>", self._on_mouse_motion)
        self.canvas.bind("<Leave>", lambda e: self._clear_hover())

        self.redraw()

    def set_range(self, start_octave: int, num_octaves: int = 2):
        """Updates the octaves shown on the keyboard."""
        self.start_octave = start_octave
        self.num_octaves = num_octaves
        total_white_keys = self.num_octaves * 7
        self.canvas_width = total_white_keys * self.key_width + 4
        self.canvas.config(width=self.canvas_width)
        self.redraw()

    def highlight_notes(self, notes: List[Note], color: str = "#3B82F6"):
        """Highlights a list of notes with the specified color."""
        self.highlighted_midis.clear()
        for note in notes:
            self.highlighted_midis[note.midi] = color
        self.redraw()

    def highlight_by_midi(self, midi_color_map: Dict[int, str]):
        """Highlights notes according to a mapping of MIDI number to color."""
        self.highlighted_midis = dict(midi_color_map)
        self.redraw()

    def clear_highlights(self):
        """Clears all highlighted keys."""
        self.highlighted_midis.clear()
        self.redraw()

    def _on_mouse_motion(self, event):
        x, y = event.x, event.y
        note = self._find_note_at_pos(x, y)
        if note != self._hovered_note:
            self._hovered_note = note
            self.redraw()

    def _clear_hover(self):
        if self._hovered_note is not None:
            self._hovered_note = None
            self.redraw()

    def _find_note_at_pos(self, x: int, y: int) -> Optional[Note]:
        # Check black keys first (they overlap on top)
        for key in self._key_regions:
            if key["is_black"]:
                if key["x1"] <= x <= key["x2"] and key["y1"] <= y <= key["y2"]:
                    return key["note"]

        # Check white keys
        for key in self._key_regions:
            if not key["is_black"]:
                if key["x1"] <= x <= key["x2"] and key["y1"] <= y <= key["y2"]:
                    return key["note"]

        return None

    def _on_canvas_click(self, event):
        note = self._find_note_at_pos(event.x, event.y)
        if note:
            if self.enable_audio:
                self.audio_player.play_note(note, duration=0.6)
            if self.on_key_click:
                self.on_key_click(note)

    def redraw(self):
        """Draws white and black keys with highlights, hover states, and labels."""
        self.canvas.delete("all")
        self._key_regions.clear()

        white_key_count = 0

        # Draw White Keys First
        for oct_idx in range(self.num_octaves):
            octave = self.start_octave + oct_idx
            for white_idx, letter in enumerate(self.WHITE_NOTES):
                note = Note(letter, octave)
                x1 = white_key_count * self.key_width + 2
                y1 = 2
                x2 = x1 + self.key_width
                y2 = y1 + self.key_height

                is_highlighted = note.midi in self.highlighted_midis
                is_hovered = self._hovered_note == note

                if is_highlighted:
                    bg_color = self.highlighted_midis[note.midi]
                    text_color = "#FFFFFF"
                elif is_hovered:
                    bg_color = "#E2E8F0"
                    text_color = "#0F172A"
                else:
                    bg_color = "#FFFFFF"
                    text_color = "#334155"

                # Key rectangle
                self.canvas.create_rectangle(
                    x1, y1, x2, y2,
                    fill=bg_color,
                    outline="#94A3B8",
                    width=1,
                )

                # Bottom lip highlight
                self.canvas.create_line(x1 + 1, y2 - 3, x2 - 1, y2 - 3, fill="#CBD5E1", width=2)

                # Note Label
                if self.show_labels:
                    label_text = f"{note.pitch}{note.octave}" if letter == "C" else note.pitch
                    self.canvas.create_text(
                        x1 + self.key_width // 2,
                        y2 - 16,
                        text=label_text,
                        fill=text_color,
                        font=("Helvetica", 9, "bold" if letter == "C" else "normal"),
                    )

                self._key_regions.append({
                    "note": note,
                    "is_black": False,
                    "x1": x1,
                    "y1": y1,
                    "x2": x2,
                    "y2": y2,
                })
                white_key_count += 1

        # Draw Black Keys on Top
        white_key_count = 0
        for oct_idx in range(self.num_octaves):
            octave = self.start_octave + oct_idx
            for black_name, rel_idx in self.BLACK_NOTES.items():
                note = Note(black_name, octave)
                abs_white_idx = oct_idx * 7 + rel_idx
                center_x = (abs_white_idx + 1) * self.key_width + 2
                x1 = center_x - self.black_width // 2
                y1 = 2
                x2 = x1 + self.black_width
                y2 = y1 + self.black_height

                is_highlighted = note.midi in self.highlighted_midis
                is_hovered = self._hovered_note == note

                if is_highlighted:
                    bg_color = self.highlighted_midis[note.midi]
                    text_color = "#FFFFFF"
                elif is_hovered:
                    bg_color = "#334155"
                    text_color = "#F8FAFC"
                else:
                    bg_color = "#0F172A"  # Deep obsidian black
                    text_color = "#94A3B8"

                # Black key shadow/base
                self.canvas.create_rectangle(
                    x1, y1, x2, y2,
                    fill=bg_color,
                    outline="#475569",
                    width=1,
                )

                # Key surface highlight for 3D realism
                self.canvas.create_line(x1 + 2, y1 + 2, x2 - 2, y1 + 2, fill="#64748B", width=1)
                self.canvas.create_line(x1 + 2, y2 - 4, x2 - 2, y2 - 4, fill="#1E293B", width=2)

                # Note Label on Black Key
                if self.show_labels:
                    self.canvas.create_text(
                        x1 + self.black_width // 2,
                        y2 - 14,
                        text=note.pitch,
                        fill=text_color,
                        font=("Helvetica", 7, "bold"),
                    )

                self._key_regions.append({
                    "note": note,
                    "is_black": True,
                    "x1": x1,
                    "y1": y1,
                    "x2": x2,
                    "y2": y2,
                })
