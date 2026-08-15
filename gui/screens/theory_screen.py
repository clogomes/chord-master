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
from gui.components.theory_quiz_widget import TheoryQuizWidget
from core.theory_quiz import CHAPTER_QUIZZES
from gui.scroll_utils import bind_mousewheel
from gui.markdown_renderer import render_markdown_to_textbox
from gui import theme


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
        on_user_updated: Optional[Callable[[], None]] = None,
        **kwargs,
    ):
        super().__init__(master, fg_color=theme.COLOR_BG, **kwargs)
        self.user_manager = user_manager
        self.on_back = on_back
        self.on_user_updated = on_user_updated
        self.audio_player = get_audio_player()

        self.current_chapter_idx = 0
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
            font=theme.get_font(theme.FONT_BODY_BOLD),
            fg_color=theme.COLOR_SURFACE_SECONDARY,
            hover_color=theme.COLOR_BORDER,
            text_color=theme.COLOR_TEXT_PRIMARY,
            width=130,
            command=self.on_back,
        )
        back_btn.pack(side="left")

        user = self.user_manager.current_user
        title_lbl = ctk.CTkLabel(
            nav_bar,
            text=f"📖 Teoria Musical & Prática ({user.avatar} {user.username})",
            font=theme.get_font(theme.FONT_TITLE),
            text_color=theme.COLOR_TEXT_PRIMARY,
        )
        title_lbl.pack(side="left", padx=14)


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
            corner_radius=theme.RADIUS_LG,
            fg_color=theme.COLOR_CARD_SURFACE,
            border_width=1,
            border_color=theme.COLOR_BORDER,
        )
        self.chapter_nav_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        bind_mousewheel(self.chapter_nav_frame)

        ctk.CTkLabel(
            self.chapter_nav_frame,
            text="Capítulos do Curso",
            font=theme.get_font(theme.FONT_SECTION),
            text_color=theme.COLOR_TEXT_PRIMARY,
        ).pack(anchor="w", padx=10, pady=(8, 8))

        self._render_chapter_list()

        # 2.2 Chapter Reader & Visualizers Area
        self.content_scroll = ctk.CTkScrollableFrame(
            main_layout,
            corner_radius=theme.RADIUS_LG,
            fg_color=theme.COLOR_BG,
            border_width=1,
            border_color=theme.COLOR_BORDER,
        )
        self.content_scroll.grid(row=0, column=1, sticky="nsew")
        bind_mousewheel(self.content_scroll)

    def _render_chapter_list(self):
        for btn in self.chapter_buttons:
            btn.destroy()
        self.chapter_buttons.clear()

        for idx, chap in enumerate(THEORY_CHAPTERS):
            is_active = (idx == self.current_chapter_idx)
            is_done = self.user_manager.is_lesson_completed(chap.id)

            status_mark = "✅ " if is_done else f"{chap.number}. "
            btn_text = f"{status_mark}{chap.title}"

            btn = ctk.CTkButton(
                self.chapter_nav_frame,
                text=btn_text,
                font=theme.get_font(theme.FONT_BODY_BOLD if is_active else theme.FONT_BODY),
                anchor="w",
                height=42,
                corner_radius=theme.RADIUS_MD,
                fg_color=theme.COLOR_PRIMARY if is_active else theme.COLOR_SURFACE_SECONDARY,
                text_color="#FFFFFF" if is_active else theme.COLOR_TEXT_PRIMARY,
                hover_color=theme.COLOR_PRIMARY_HOVER if is_active else theme.COLOR_BORDER,
                command=lambda i=idx: self._load_chapter(i),
            )
            btn.pack(fill="x", padx=6, pady=3)
            self.chapter_buttons.append(btn)

    def _load_chapter(self, chapter_idx: int):
        self.current_chapter_idx = chapter_idx
        chap = THEORY_CHAPTERS[chapter_idx]

        # Update sidebar button states
        for i, btn in enumerate(self.chapter_buttons):
            is_done = self.user_manager.is_lesson_completed(THEORY_CHAPTERS[i].id)
            status_mark = "✅ " if is_done else f"{THEORY_CHAPTERS[i].number}. "
            if i == chapter_idx:
                btn.configure(
                    fg_color=theme.COLOR_PRIMARY,
                    text_color="#FFFFFF",
                    hover_color=theme.COLOR_PRIMARY_HOVER,
                    font=theme.get_font(theme.FONT_BODY_BOLD),
                )
            else:
                btn.configure(
                    fg_color=theme.COLOR_SURFACE_SECONDARY,
                    text_color=theme.COLOR_TEXT_PRIMARY,
                    hover_color=theme.COLOR_BORDER,
                    font=theme.get_font(theme.FONT_BODY),
                )

        # Clear and build chapter view in content_scroll
        for child in self.content_scroll.winfo_children():
            child.destroy()

        # 1. Chapter Title Header Card
        header_card = ctk.CTkFrame(
            self.content_scroll,
            corner_radius=theme.RADIUS_LG,
            fg_color=theme.COLOR_CARD_SURFACE,
            border_width=1,
            border_color=theme.COLOR_BORDER,
        )
        header_card.pack(fill="x", padx=8, pady=(0, 10))

        top_info = ctk.CTkFrame(header_card, fg_color="transparent")
        top_info.pack(fill="x", padx=16, pady=(12, 4))

        diff_colors = {
            "Iniciante": theme.COLOR_SUCCESS,
            "Intermédio": theme.COLOR_PRIMARY,
            "Avançado": "#8B5CF6",
            "Prático": "#F59E0B",
        }
        diff_color = diff_colors.get(chap.difficulty, theme.COLOR_PRIMARY)

        badge = ctk.CTkLabel(
            top_info,
            text=f"  {chap.difficulty.upper()}  ",
            font=theme.get_font(theme.FONT_BADGE),
            text_color="#FFFFFF",
            fg_color=diff_color,
            corner_radius=theme.RADIUS_SM,
        )
        badge.pack(side="left")

        ctk.CTkLabel(
            top_info,
            text=f"Capítulo {chap.number} • {chap.category}",
            font=theme.get_font(theme.FONT_BODY_BOLD),
            text_color=theme.COLOR_TEXT_MUTED,
        ).pack(side="left", padx=10)

        ctk.CTkLabel(
            header_card,
            text=chap.title,
            font=theme.get_font(theme.FONT_TITLE),
            text_color=theme.COLOR_TEXT_PRIMARY,
        ).pack(anchor="w", padx=16, pady=(2, 2))

        ctk.CTkLabel(
            header_card,
            text=chap.subtitle,
            font=theme.get_font(theme.FONT_BODY),
            text_color=theme.COLOR_TEXT_MUTED,
        ).pack(anchor="w", padx=16, pady=(0, 6))

        # Summary box
        summary_box = ctk.CTkFrame(header_card, fg_color=theme.COLOR_SURFACE_SECONDARY, corner_radius=theme.RADIUS_MD)
        summary_box.pack(fill="x", padx=16, pady=(4, 14))

        ctk.CTkLabel(
            summary_box,
            text=f"💡 **Objetivo**: {chap.summary}",
            font=theme.get_font(theme.FONT_BODY),
            text_color=theme.COLOR_TEXT_PRIMARY,
            justify="left",
            wraplength=660,
        ).pack(anchor="w", padx=12, pady=8)

        # 2. Main Theory Markdown Text Container
        text_card = ctk.CTkFrame(
            self.content_scroll,
            corner_radius=theme.RADIUS_LG,
            fg_color=theme.COLOR_CARD_SURFACE,
            border_width=1,
            border_color=theme.COLOR_BORDER,
        )
        text_card.pack(fill="x", padx=8, pady=(0, 10))

        content_box = ctk.CTkTextbox(
            text_card,
            height=500,
            corner_radius=theme.RADIUS_MD,
            fg_color=theme.COLOR_CARD_SURFACE,
            text_color=theme.COLOR_TEXT_PRIMARY,
            font=theme.get_font(theme.FONT_BODY),
            wrap="word",
        )
        content_box.pack(fill="both", expand=True, padx=14, pady=14)
        
        combined_markdown = chap.content_markdown.strip() + "\n\n---\n\n### 🎹 Aplicação no Piano\n\n" + chap.piano_focus.strip() + "\n\n---\n\n### 🎸 Aplicação na Viola\n\n" + chap.guitar_focus.strip()
        render_markdown_to_textbox(content_box, combined_markdown, base_font_size=13)

        # 4. Interactive Demonstrator Suite (Piano + Viola + Staff)
        self._build_interactive_demo_area(chap)

        # 5. Lesson Completion Banner
        self._build_completion_footer(chap)

        # 6. Chapter Quiz
        self._build_quiz_area(chap)

    def _build_quiz_area(self, chap: TheoryChapter):
        quiz = next((q for q in CHAPTER_QUIZZES if q.chapter_id == chap.id), None)
        if not quiz:
            return

        ctk.CTkLabel(
            self.content_scroll,
            text="📝 Quiz do Capítulo",
            font=theme.get_font(theme.FONT_SECTION),
            text_color=theme.COLOR_TEXT_PRIMARY,
        ).pack(anchor="w", padx=16, pady=(10, 5))

        self.quiz_widget = TheoryQuizWidget(
            self.content_scroll,
            chapter_quiz=quiz,
            on_complete=self._on_quiz_complete,
            user_manager=self.user_manager
        )
        self.quiz_widget.pack(fill="x", padx=8, pady=(0, 20))

    def _on_quiz_complete(self, correct: int, total: int):
        if hasattr(self, 'quiz_widget') and self.quiz_widget.winfo_exists():
            ctk.CTkLabel(
                self.content_scroll,
                text=f"🎉 Parabéns! Completaste o quiz com {correct}/{total} de precisão.",
                font=theme.get_font(theme.FONT_BODY_BOLD),
                text_color=theme.COLOR_SUCCESS,
            ).pack(pady=10)

    def _build_interactive_demo_area(self, chap: TheoryChapter):
        demo_card = ctk.CTkFrame(
            self.content_scroll,
            corner_radius=theme.RADIUS_LG,
            fg_color=theme.COLOR_CARD_SURFACE,
            border_width=1,
            border_color=theme.COLOR_BORDER,
        )
        demo_card.pack(fill="x", padx=8, pady=(0, 12))

        ctk.CTkLabel(
            demo_card,
            text="🎛️ Laboratório Interativo: Experimenta o Som e a Digitação",
            font=theme.get_font(theme.FONT_SUBTITLE),
            text_color=theme.COLOR_TEXT_PRIMARY,
        ).pack(anchor="w", padx=16, pady=(12, 6))

        # Controls Row
        ctrl_row = ctk.CTkFrame(demo_card, fg_color="transparent")
        ctrl_row.pack(fill="x", padx=16, pady=(2, 8))

        ctk.CTkLabel(ctrl_row, text="Tónica / Nota:", font=theme.get_font(theme.FONT_BODY_BOLD), text_color=theme.COLOR_TEXT_PRIMARY).pack(side="left", padx=(0, 4))

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

        # 2. Piano Keyboard
        ctk.CTkLabel(
            demo_card,
            text="🎹 Como Tocar no Piano:",
            font=ctk.CTkFont(family="Helvetica", size=12, weight="bold"),
            text_color=("#64748B", "#94A3B8"),
        ).pack(anchor="w", padx=16, pady=(6, 2))

        self.demo_piano = PianoKeyboard(demo_card, start_octave=2, num_octaves=4, key_width=25, key_height=120)
        self.demo_piano.pack(pady=(0, 6))

        # 3. Guitar / Viola Fretboard
        ctk.CTkLabel(
            demo_card,
            text="🎸 Como Tocar na Viola / Guitarra (Braço & Dedilhado):",
            font=ctk.CTkFont(family="Helvetica", size=12, weight="bold"),
            text_color=("#64748B", "#94A3B8"),
        ).pack(anchor="w", padx=16, pady=(6, 2))

        self.demo_guitar = GuitarFretboard(demo_card, width=650, height=155, num_frets=14)
        self.demo_guitar.pack(pady=(0, 8))

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
        midi_map = {n.midi: ("#10B981" if i == 0 else "#38BDF8") for i, n in enumerate(notes)}
        self.demo_piano.highlight_by_midi(midi_map)
        elem = self.element_select.get()
        if "Tríade" in elem or "Acorde" in elem or "Sétima" in elem or "Maior com" in elem or "Menor com" in elem or "Justa" in elem or "Terça" in elem:
            fingering = get_chord_piano_fingering(notes, hand="right")
            self.demo_piano.set_fingering(fingering)
        else:
            self.demo_piano.set_fingering({})

        # 3. Update Guitar / Viola
        root_name = self.root_select.get()
        elem = self.element_select.get()
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
            corner_radius=theme.RADIUS_LG,
            fg_color=theme.COLOR_CARD_SURFACE,
            border_width=1,
            border_color=theme.COLOR_BORDER,
        )
        footer.pack(fill="x", padx=8, pady=(0, 10))

        user = self.user_manager.current_user
        is_done = self.user_manager.is_lesson_completed(chap.id)

        status_lbl = ctk.CTkLabel(
            footer,
            text=f"Estado para {user.avatar} {user.username}: " + ("✅ Concluído com Sucesso" if is_done else "⏳ Lição Pendente"),
            font=theme.get_font(theme.FONT_BODY_BOLD),
            text_color=theme.COLOR_SUCCESS if is_done else "#F59E0B",
        )
        status_lbl.pack(side="left", padx=18, pady=14)

        action_btn = ctk.CTkButton(
            footer,
            text="✓ Já Aprendi (Marcar como Concluído)" if not is_done else "Desmarcar Lição",
            font=theme.get_font(theme.FONT_BODY_BOLD),
            fg_color=theme.COLOR_SUCCESS if not is_done else theme.COLOR_SURFACE_SECONDARY,
            hover_color=theme.COLOR_SUCCESS_HOVER if not is_done else theme.COLOR_BORDER,
            text_color="#FFFFFF" if not is_done else theme.COLOR_TEXT_PRIMARY,
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
