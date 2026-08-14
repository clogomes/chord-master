"""Comprehensive Music Theory Academy screen with 8 progressive chapters, dual Piano + Viola fretboard, and interactive audio."""
from typing import Callable, Dict, List, Optional, Tuple
import customtkinter as ctk
from core.notes import Note, NOTE_NAMES, NOTE_NAMES_PT
from core.intervals import INTERVALS, Interval
from core.scales import SCALE_TYPES, Scale
from core.chords import CHORD_TYPES, Chord
from core.guitar import GuitarChordShape, GUITAR_CHORD_LIBRARY, GuitarFretboardModel
from core.theory_content import THEORY_CHAPTERS, TheoryChapter
from core.user_manager import UserManager
from core.fingering import get_chord_piano_fingering
from audio.player import get_audio_player
from gui.components.piano_keyboard import PianoKeyboard
from gui.components.staff_canvas import StaffCanvas
from gui.components.guitar_fretboard import GuitarFretboard


class TheoryScreen(ctk.CTkFrame):
    """
    Complete music theory encyclopedia covering fundamentals to advanced harmony,
    featuring synchronized Piano + Guitar/Viola interactive visualizations and audio demos.
    """

    def __init__(
        self,
        master,
        user_manager: UserManager,
        on_back: Callable[[], None],
        **kwargs,
    ):
        super().__init__(master, fg_color=("#F8FAFC", "#0F172A"), **kwargs)
        self.user_manager = user_manager
        self.on_back = on_back
        self.audio_player = get_audio_player()

        self.current_chapter_idx = 0
        self.display_instrument_mode = "Ambos"  # "Piano", "Viola", "Ambos"
        self.chapter_buttons: List[ctk.CTkButton] = []

        self._build_ui()
        self._load_chapter(0)

    def _build_ui(self):
        # 1. Top Navigation Bar
        nav_bar = ctk.CTkFrame(self, fg_color="transparent")
        nav_bar.pack(fill="x", padx=18, pady=(14, 6))

        back_btn = ctk.CTkButton(
            nav_bar,
            text="← Voltar ao Menu",
            font=ctk.CTkFont(family="Helvetica", size=13, weight="bold"),
            fg_color="#475569",
            hover_color="#334155",
            width=130,
            command=self.on_back,
        )
        back_btn.pack(side="left")

        user = self.user_manager.current_user
        title_lbl = ctk.CTkLabel(
            nav_bar,
            text=f"📖 Teoria Musical & Prática ({user.avatar} {user.username})",
            font=ctk.CTkFont(family="Helvetica", size=20, weight="bold"),
            text_color=("#0F172A", "#F8FAFC"),
        )
        title_lbl.pack(side="left", padx=14)

        # Instrument View Selector
        inst_box = ctk.CTkFrame(nav_bar, fg_color="transparent")
        inst_box.pack(side="right")

        ctk.CTkLabel(
            inst_box,
            text="Instrumento:",
            font=ctk.CTkFont(family="Helvetica", size=12, weight="bold"),
            text_color=("#64748B", "#94A3B8"),
        ).pack(side="left", padx=(0, 6))

        self.inst_segmented = ctk.CTkSegmentedButton(
            inst_box,
            values=["🎹 Piano", "🎸 Viola", "🎹 + 🎸 Ambos"],
            command=self._on_instrument_mode_changed,
            selected_color="#2563EB",
            selected_hover_color="#1D4ED8",
        )
        self.inst_segmented.set("🎹 + 🎸 Ambos")
        self.inst_segmented.pack(side="left")

        # 2. Main Two-Column Layout (Chapter Sidebar + Content)
        main_layout = ctk.CTkFrame(self, fg_color="transparent")
        main_layout.pack(fill="both", expand=True, padx=18, pady=(4, 14))
        main_layout.grid_columnconfigure(0, weight=0)  # Chapter nav
        main_layout.grid_columnconfigure(1, weight=1)  # Chapter reader & visualizers
        main_layout.grid_rowconfigure(0, weight=1)

        # 2.1 Chapter Navigation Sidebar
        self.chapter_nav_frame = ctk.CTkScrollableFrame(
            main_layout,
            width=260,
            corner_radius=12,
            fg_color=("#F1F5F9", "#1E293B"),
            border_width=1,
            border_color=("#E2E8F0", "#334155"),
        )
        self.chapter_nav_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        ctk.CTkLabel(
            self.chapter_nav_frame,
            text="Capítulos do Curso",
            font=ctk.CTkFont(family="Helvetica", size=14, weight="bold"),
            text_color=("#0F172A", "#F8FAFC"),
        ).pack(anchor="w", padx=10, pady=(8, 8))

        self._render_chapter_list()

        # 2.2 Chapter Reader & Visualizers Area
        self.content_scroll = ctk.CTkScrollableFrame(
            main_layout,
            corner_radius=12,
            fg_color=("#F8FAFC", "#0F172A"),
            border_width=1,
            border_color=("#E2E8F0", "#334155"),
        )
        self.content_scroll.grid(row=0, column=1, sticky="nsew")

    def _render_chapter_list(self):
        for btn in self.chapter_buttons:
            btn.destroy()
        self.chapter_buttons.clear()

        user = self.user_manager.current_user

        for idx, chap in enumerate(THEORY_CHAPTERS):
            is_active = (idx == self.current_chapter_idx)
            is_done = self.user_manager.is_lesson_completed(chap.id)

            status_mark = "✅ " if is_done else f"{chap.number}. "
            btn_text = f"{status_mark}{chap.title}"

            btn = ctk.CTkButton(
                self.chapter_nav_frame,
                text=btn_text,
                font=ctk.CTkFont(family="Helvetica", size=12, weight="bold" if is_active else "normal"),
                anchor="w",
                height=42,
                corner_radius=8,
                fg_color="#2563EB" if is_active else ("#E2E8F0", "#0F172A"),
                text_color="#FFFFFF" if is_active else ("#1E293B", "#E2E8F0"),
                hover_color="#1D4ED8" if is_active else ("#CBD5E1", "#334155"),
                command=lambda i=idx: self._load_chapter(i),
            )
            btn.pack(fill="x", padx=6, pady=3)
            self.chapter_buttons.append(btn)

    def _on_instrument_mode_changed(self, mode: str):
        if "Piano" in mode and "Viola" not in mode:
            self.display_instrument_mode = "Piano"
        elif "Viola" in mode and "Piano" not in mode:
            self.display_instrument_mode = "Viola"
        else:
            self.display_instrument_mode = "Ambos"
        self._load_chapter(self.current_chapter_idx)

    def _load_chapter(self, chapter_idx: int):
        self.current_chapter_idx = chapter_idx
        chap = THEORY_CHAPTERS[chapter_idx]

        # Update sidebar button states
        for i, btn in enumerate(self.chapter_buttons):
            is_done = self.user_manager.is_lesson_completed(THEORY_CHAPTERS[i].id)
            status_mark = "✅ " if is_done else f"{THEORY_CHAPTERS[i].number}. "
            if i == chapter_idx:
                btn.configure(
                    fg_color="#2563EB",
                    text_color="#FFFFFF",
                    hover_color="#1D4ED8",
                    font=ctk.CTkFont(family="Helvetica", size=12, weight="bold"),
                )
            else:
                btn.configure(
                    fg_color=("#E2E8F0", "#0F172A"),
                    text_color=("#1E293B", "#E2E8F0"),
                    hover_color=("#CBD5E1", "#334155"),
                    font=ctk.CTkFont(family="Helvetica", size=12, weight="normal"),
                )

        # Clear and build chapter view in content_scroll
        for child in self.content_scroll.winfo_children():
            child.destroy()

        # 1. Chapter Title Header Card
        header_card = ctk.CTkFrame(
            self.content_scroll,
            corner_radius=12,
            fg_color=("#F1F5F9", "#1E293B"),
            border_width=1,
            border_color=("#E2E8F0", "#334155"),
        )
        header_card.pack(fill="x", padx=8, pady=(0, 10))

        top_info = ctk.CTkFrame(header_card, fg_color="transparent")
        top_info.pack(fill="x", padx=16, pady=(12, 4))

        diff_colors = {
            "Iniciante": "#10B981",
            "Intermédio": "#3B82F6",
            "Avançado": "#8B5CF6",
            "Prático": "#F59E0B",
        }
        diff_color = diff_colors.get(chap.difficulty, "#3B82F6")

        badge = ctk.CTkLabel(
            top_info,
            text=f"  {chap.difficulty.upper()}  ",
            font=ctk.CTkFont(family="Helvetica", size=11, weight="bold"),
            text_color="#FFFFFF",
            fg_color=diff_color,
            corner_radius=6,
        )
        badge.pack(side="left")

        ctk.CTkLabel(
            top_info,
            text=f"Capítulo {chap.number} • {chap.category}",
            font=ctk.CTkFont(family="Helvetica", size=12, weight="bold"),
            text_color=("#64748B", "#94A3B8"),
        ).pack(side="left", padx=10)

        ctk.CTkLabel(
            header_card,
            text=chap.title,
            font=ctk.CTkFont(family="Helvetica", size=22, weight="bold"),
            text_color=("#0F172A", "#F8FAFC"),
        ).pack(anchor="w", padx=16, pady=(2, 2))

        ctk.CTkLabel(
            header_card,
            text=chap.subtitle,
            font=ctk.CTkFont(family="Helvetica", size=14),
            text_color=("#64748B", "#94A3B8"),
        ).pack(anchor="w", padx=16, pady=(0, 6))

        # Summary box
        summary_box = ctk.CTkFrame(header_card, fg_color=("#E2E8F0", "#0F172A"), corner_radius=8)
        summary_box.pack(fill="x", padx=16, pady=(4, 14))

        ctk.CTkLabel(
            summary_box,
            text=f"💡 **Objetivo**: {chap.summary}",
            font=ctk.CTkFont(family="Helvetica", size=13),
            text_color=("#1E293B", "#CBD5E1"),
            justify="left",
            wraplength=660,
        ).pack(anchor="w", padx=12, pady=8)

        # 2. Main Theory Markdown Text Container
        text_card = ctk.CTkFrame(
            self.content_scroll,
            corner_radius=12,
            fg_color=("#F1F5F9", "#1E293B"),
            border_width=1,
            border_color=("#E2E8F0", "#334155"),
        )
        text_card.pack(fill="x", padx=8, pady=(0, 10))

        content_box = ctk.CTkTextbox(
            text_card,
            height=260,
            corner_radius=8,
            fg_color=("#FFFFFF", "#0F172A"),
            text_color=("#0F172A", "#F8FAFC"),
            font=ctk.CTkFont(family="Helvetica", size=13),
            wrap="word",
        )
        content_box.pack(fill="both", expand=True, padx=14, pady=14)
        content_box.insert("0.0", chap.content_markdown.strip())
        content_box.configure(state="disabled")

        # 3. Practical Instrument Guides (Piano & Viola)
        if self.display_instrument_mode in ["Piano", "Ambos"]:
            piano_card = ctk.CTkFrame(
                self.content_scroll,
                corner_radius=12,
                fg_color=("#EFF6FF", "#172554"),
                border_width=1,
                border_color=("#BFDBFE", "#1E40AF"),
            )
            piano_card.pack(fill="x", padx=8, pady=(0, 8))

            ctk.CTkLabel(
                piano_card,
                text=chap.piano_focus.strip(),
                font=ctk.CTkFont(family="Helvetica", size=13),
                text_color=("#1E40AF", "#DBEAFE"),
                justify="left",
                wraplength=660,
            ).pack(anchor="w", padx=16, pady=12)

        if self.display_instrument_mode in ["Viola", "Ambos"]:
            guitar_card = ctk.CTkFrame(
                self.content_scroll,
                corner_radius=12,
                fg_color=("#FEF3C7", "#451A03"),
                border_width=1,
                border_color=("#FDE68A", "#92400E"),
            )
            guitar_card.pack(fill="x", padx=8, pady=(0, 10))

            ctk.CTkLabel(
                guitar_card,
                text=chap.guitar_focus.strip(),
                font=ctk.CTkFont(family="Helvetica", size=13),
                text_color=("#92400E", "#FEF3C7"),
                justify="left",
                wraplength=660,
            ).pack(anchor="w", padx=16, pady=12)

        # 4. Interactive Demonstrator Suite (Piano + Viola + Staff)
        self._build_interactive_demo_area(chap)

        # 5. Lesson Completion Banner
        self._build_completion_footer(chap)

    def _build_interactive_demo_area(self, chap: TheoryChapter):
        demo_card = ctk.CTkFrame(
            self.content_scroll,
            corner_radius=12,
            fg_color=("#F1F5F9", "#1E293B"),
            border_width=1,
            border_color=("#E2E8F0", "#334155"),
        )
        demo_card.pack(fill="x", padx=8, pady=(0, 12))

        ctk.CTkLabel(
            demo_card,
            text="🎛️ Laboratório Interativo: Experimenta o Som e a Digitação",
            font=ctk.CTkFont(family="Helvetica", size=15, weight="bold"),
            text_color=("#0F172A", "#F8FAFC"),
        ).pack(anchor="w", padx=16, pady=(12, 6))

        # Controls Row
        ctrl_row = ctk.CTkFrame(demo_card, fg_color="transparent")
        ctrl_row.pack(fill="x", padx=16, pady=(2, 8))

        ctk.CTkLabel(ctrl_row, text="Tónica / Nota:", font=ctk.CTkFont(family="Helvetica", size=12, weight="bold")).pack(side="left", padx=(0, 4))

        self.root_select = ctk.CTkOptionMenu(
            ctrl_row,
            values=["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"],
            command=lambda e: self._on_demo_state_change(),
            width=70,
        )
        self.root_select.set("C")
        self.root_select.pack(side="left", padx=4)

        ctk.CTkLabel(ctrl_row, text="Elemento Harmónico:", font=ctk.CTkFont(family="Helvetica", size=12, weight="bold")).pack(side="left", padx=(10, 4))

        # Demo item options (Chords, Scales, Intervals)
        demo_options = [
            "Tríade Maior (C)",
            "Tríade Menor (Cm)",
            "Sétima da Dominante (C7)",
            "Maior com 7ª Maior (Cmaj7)",
            "Menor com 7ª (Cm7)",
            "Escala Maior",
            "Escala Menor Natural",
            "Pentatónica Menor (Blues/Rock)",
            "Quinta Justa (P5)",
            "Terça Maior (M3)",
        ]
        self.element_select = ctk.CTkOptionMenu(
            ctrl_row,
            values=demo_options,
            command=lambda e: self._on_demo_state_change(),
            width=210,
        )
        self.element_select.set(demo_options[0])
        self.element_select.pack(side="left", padx=4)

        # Audio Buttons
        play_btn = ctk.CTkButton(
            ctrl_row,
            text="🔊 Ouvir Bloco",
            font=ctk.CTkFont(family="Helvetica", size=12, weight="bold"),
            fg_color="#7C3AED",
            hover_color="#6D28D9",
            width=100,
            command=self._play_demo_audio_block,
        )
        play_btn.pack(side="left", padx=6)

        play_arp_btn = ctk.CTkButton(
            ctrl_row,
            text="▶ Arpejo",
            font=ctk.CTkFont(family="Helvetica", size=12, weight="bold"),
            fg_color="#2563EB",
            hover_color="#1D4ED8",
            width=90,
            command=self._play_demo_audio_arp,
        )
        play_arp_btn.pack(side="left", padx=4)

        # Detail Info Label
        self.demo_info_lbl = ctk.CTkLabel(
            demo_card,
            text="",
            font=ctk.CTkFont(family="Helvetica", size=13, weight="bold"),
            text_color="#38BDF8",
        )
        self.demo_info_lbl.pack(anchor="w", padx=16, pady=(0, 6))

        # 1. Staff Canvas
        self.demo_staff = StaffCanvas(demo_card, width=650, height=150, clef="treble", show_note_names=True)
        self.demo_staff.pack(pady=4)

        # 2. Piano Keyboard (if enabled)
        if self.display_instrument_mode in ["Piano", "Ambos"]:
            ctk.CTkLabel(
                demo_card,
                text="🎹 Como Tocar no Piano:",
                font=ctk.CTkFont(family="Helvetica", size=12, weight="bold"),
                text_color=("#64748B", "#94A3B8"),
            ).pack(anchor="w", padx=16, pady=(6, 2))

            self.demo_piano = PianoKeyboard(demo_card, start_octave=3, num_octaves=2, key_width=42, key_height=120)
            self.demo_piano.pack(pady=(0, 6))
        else:
            self.demo_piano = None

        # 3. Guitar / Viola Fretboard (if enabled)
        if self.display_instrument_mode in ["Viola", "Ambos"]:
            ctk.CTkLabel(
                demo_card,
                text="🎸 Como Tocar na Viola / Guitarra (Braço & Dedilhado):",
                font=ctk.CTkFont(family="Helvetica", size=12, weight="bold"),
                text_color=("#64748B", "#94A3B8"),
            ).pack(anchor="w", padx=16, pady=(6, 2))

            self.demo_guitar = GuitarFretboard(demo_card, width=650, height=155, num_frets=14)
            self.demo_guitar.pack(pady=(0, 8))
        else:
            self.demo_guitar = None

        self._on_demo_state_change()

    def _get_current_demo_notes(self) -> Tuple[List[Note], str]:
        root_name = self.root_select.get()
        elem = self.element_select.get()
        root = Note(root_name, 4)

        if "Tríade Maior" in elem:
            chord = Chord(root, "major")
            return chord.notes, f"Tríade Maior de {root.name_pt}: {', '.join(chord.note_names)}"
        elif "Tríade Menor" in elem:
            chord = Chord(root, "minor")
            return chord.notes, f"Tríade Menor de {root.name_pt}: {', '.join(chord.note_names)}"
        elif "Sétima da Dominante" in elem:
            chord = Chord(root, "dom7")
            return chord.notes, f"Acorde {root.pitch}7: {', '.join(chord.note_names)}"
        elif "Maior com 7ª Maior" in elem:
            chord = Chord(root, "maj7")
            return chord.notes, f"Acorde {root.pitch}maj7: {', '.join(chord.note_names)}"
        elif "Menor com 7ª" in elem:
            chord = Chord(root, "min7")
            return chord.notes, f"Acorde {root.pitch}m7: {', '.join(chord.note_names)}"
        elif "Escala Maior" in elem:
            scale = Scale(root, "major")
            return scale.notes, f"Escala de {root.name_pt} Maior: {', '.join(scale.note_names)}"
        elif "Escala Menor Natural" in elem:
            scale = Scale(root, "natural_minor")
            return scale.notes, f"Escala de {root.name_pt} Menor Natural: {', '.join(scale.note_names)}"
        elif "Pentatónica Menor" in elem:
            scale = Scale(root, "minor_pentatonic")
            return scale.notes, f"Pentatónica Menor de {root.name_pt}: {', '.join(scale.note_names)}"
        elif "Quinta Justa" in elem:
            top = root.transpose(7)
            return [root, top], f"Intervalo de Quinta Justa (P5): {root.pitch} → {top.pitch} (7 semitons)"
        elif "Terça Maior" in elem:
            top = root.transpose(4)
            return [root, top], f"Intervalo de Terça Maior (M3): {root.pitch} → {top.pitch} (4 semitons)"
        else:
            return [root], f"Nota: {root.pitch}"

    def _on_demo_state_change(self):
        notes, info_text = self._get_current_demo_notes()
        self.demo_info_lbl.configure(text=info_text)

        # 1. Update Staff
        colors = ["#10B981" if i == 0 else "#38BDF8" for i in range(len(notes))]
        self.demo_staff.set_notes(notes, colors=colors)

        # 2. Update Piano
        if self.demo_piano:
            midi_map = {n.midi: ("#10B981" if i == 0 else "#38BDF8") for i, n in enumerate(notes)}
            self.demo_piano.highlight_by_midi(midi_map)
            elem = self.element_select.get()
            if "Tríade" in elem or "Acorde" in elem or "Sétima" in elem or "Maior com" in elem or "Menor com" in elem or "Justa" in elem or "Terça" in elem:
                fingering = get_chord_piano_fingering(notes, hand="right")
                self.demo_piano.set_fingering(fingering)
            else:
                self.demo_piano.set_fingering({})

        # 3. Update Guitar / Viola
        if self.demo_guitar:
            root_name = self.root_select.get()
            elem = self.element_select.get()

            # Check if there is a matching guitar chord shape in library
            symbol = root_name
            if "Tríade Menor" in elem:
                symbol = f"{root_name}m"
            elif "Sétima da Dominante" in elem:
                symbol = f"{root_name}7"
            elif "Maior com 7ª Maior" in elem:
                symbol = f"{root_name}maj7"
            elif "Menor com 7ª" in elem:
                symbol = f"{root_name}m7"

            shape = self.demo_guitar.model.get_chord_shape(symbol)
            if shape:
                self.demo_guitar.set_chord_shape(shape)
            else:
                # Highlight notes on fretboard as a scale
                self.demo_guitar.highlight_scale(notes)

    def _play_demo_audio_block(self):
        notes, _ = self._get_current_demo_notes()
        self.audio_player.play_chord(notes, duration=1.4)

    def _play_demo_audio_arp(self):
        notes, _ = self._get_current_demo_notes()
        self.audio_player.play_sequence(notes, delay_between=0.35, note_duration=0.55)

    def _build_completion_footer(self, chap: TheoryChapter):
        footer = ctk.CTkFrame(
            self.content_scroll,
            corner_radius=12,
            fg_color=("#F1F5F9", "#1E293B"),
            border_width=1,
            border_color=("#E2E8F0", "#334155"),
        )
        footer.pack(fill="x", padx=8, pady=(0, 10))

        user = self.user_manager.current_user
        is_done = self.user_manager.is_lesson_completed(chap.id)

        status_lbl = ctk.CTkLabel(
            footer,
            text=f"Estado para {user.avatar} {user.username}: " + ("✅ Concluído com Sucesso" if is_done else "⏳ Lição Pendente"),
            font=ctk.CTkFont(family="Helvetica", size=14, weight="bold"),
            text_color="#10B981" if is_done else "#F59E0B",
        )
        status_lbl.pack(side="left", padx=18, pady=14)

        action_btn = ctk.CTkButton(
            footer,
            text="✓ Já Aprendi (Marcar como Concluído)" if not is_done else "Desmarcar Lição",
            font=ctk.CTkFont(family="Helvetica", size=13, weight="bold"),
            fg_color="#059669" if not is_done else "#475569",
            hover_color="#047857" if not is_done else "#334155",
            width=230,
            height=36,
            command=lambda: self._toggle_chapter_completion(chap.id, status_lbl, action_btn),
        )
        action_btn.pack(side="right", padx=18, pady=14)

    def _toggle_chapter_completion(self, chap_id: str, status_lbl, action_btn):
        user = self.user_manager.current_user
        if chap_id in user.completed_lessons:
            user.completed_lessons.remove(chap_id)
            self.user_manager.save()
            status_lbl.configure(
                text=f"Estado para {user.avatar} {user.username}: ⏳ Lição Pendente",
                text_color="#F59E0B",
            )
            action_btn.configure(
                text="✓ Já Aprendi (Marcar como Concluído)",
                fg_color="#059669",
                hover_color="#047857",
            )
        else:
            self.user_manager.mark_lesson_completed(chap_id)
            status_lbl.configure(
                text=f"Estado para {user.avatar} {user.username}: ✅ Concluído com Sucesso",
                text_color="#10B981",
            )
            action_btn.configure(
                text="Desmarcar Lição",
                fg_color="#475569",
                hover_color="#334155",
            )
        self._render_chapter_list()
