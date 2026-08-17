from gui.i18n import t
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
            text=t("btn_back", "← Voltar ao Menu"),
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
            fg_color=theme.COLOR_SURFACE,
            border_width=1,
            border_color=theme.COLOR_BORDER,
        )
        self.chapter_nav_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        bind_mousewheel(self.chapter_nav_frame)

        ctk.CTkLabel(
            self.chapter_nav_frame,
            text=t("theory_course_chapters", "Capítulos do Curso"),
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

        from gui.i18n import get_language, t
        lang = get_language()

        for idx, chap in enumerate(THEORY_CHAPTERS):
            is_active = (idx == self.current_chapter_idx)
            is_done = self.user_manager.is_lesson_completed(chap.id)

            status_mark = "✅ " if is_done else f"{chap.number}. "
            btn_text = f"{status_mark}{chap.get_title(lang)}"

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

    def load_chapter_by_id(self, chapter_id: str):
        """Switches directly to a specific chapter by its unique ID."""
        for idx, chap in enumerate(THEORY_CHAPTERS):
            if chap.id == chapter_id:
                self._load_chapter(idx)
                break

    def _load_chapter(self, chapter_idx: int):
        from gui.i18n import get_language, t
        lang = get_language()

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
            fg_color=theme.COLOR_SURFACE,
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
        
        diff_key = {
            "Iniciante": "diff_beginner",
            "Intermédio": "diff_intermediate",
            "Avançado": "diff_advanced"
        }.get(chap.difficulty, "")

        badge = ctk.CTkLabel(
            top_info,
            text=f"  {t(diff_key, chap.difficulty).upper()}  ",
            font=theme.get_font(theme.FONT_BADGE),
            text_color="#FFFFFF",
            fg_color=diff_color,
            corner_radius=theme.RADIUS_SM,
        )
        badge.pack(side="left")

        chap_lbl = "Chapter" if lang == "en" else "Capítulo"
        ctk.CTkLabel(
            top_info,
            text=f"{chap_lbl} {chap.number} • {chap.category}",
            font=theme.get_font(theme.FONT_BODY_BOLD),
            text_color=theme.COLOR_TEXT_MUTED,
        ).pack(side="left", padx=10)

        ctk.CTkLabel(
            header_card,
            text=chap.get_title(lang),
            font=theme.get_font(theme.FONT_TITLE),
            text_color=theme.COLOR_TEXT_PRIMARY,
        ).pack(anchor="w", padx=16, pady=(2, 2))

        ctk.CTkLabel(
            header_card,
            text=chap.get_subtitle(lang),
            font=theme.get_font(theme.FONT_BODY),
            text_color=theme.COLOR_TEXT_MUTED,
        ).pack(anchor="w", padx=16, pady=(0, 6))

        # Prerequisites tag if present
        if chap.prerequisites:
            prereq_names = []
            for pid in chap.prerequisites:
                target_chap = next((c for c in THEORY_CHAPTERS if c.id == pid), None)
                if target_chap:
                    prereq_names.append(f"Cap. {target_chap.number}")
            if prereq_names:
                prereq_lbl = "Prerequisites" if lang == "en" else "Pré-requisitos recomendados"
                prereq_frame = ctk.CTkFrame(header_card, fg_color="transparent")
                prereq_frame.pack(fill="x", padx=16, pady=(0, 6))
                ctk.CTkLabel(
                    prereq_frame,
                    text=f"📌 {prereq_lbl}: {', '.join(prereq_names)}",
                    font=theme.get_font(theme.FONT_SMALL_BOLD),
                    text_color="#F59E0B",
                ).pack(side="left")

        # Summary box
        summary_box = ctk.CTkFrame(header_card, fg_color=theme.COLOR_SURFACE_SECONDARY, corner_radius=theme.RADIUS_MD)
        summary_box.pack(fill="x", padx=16, pady=(4, 14))

        obj_label = "Goal" if lang == "en" else "Objetivo"
        ctk.CTkLabel(
            summary_box,
            text=f"💡 **{obj_label}**: {chap.get_summary(lang)}",
            font=theme.get_font(theme.FONT_BODY),
            text_color=theme.COLOR_TEXT_PRIMARY,
            justify="left",
            wraplength=660,
        ).pack(anchor="w", padx=12, pady=8)

        # 2. Main Theory Markdown Text Container
        text_card = ctk.CTkFrame(
            self.content_scroll,
            corner_radius=theme.RADIUS_LG,
            fg_color=theme.COLOR_SURFACE,
            border_width=1,
            border_color=theme.COLOR_BORDER,
        )
        text_card.pack(fill="x", padx=8, pady=(0, 10))

        content_box = ctk.CTkTextbox(
            text_card,
            height=500,
            corner_radius=theme.RADIUS_MD,
            fg_color=theme.COLOR_SURFACE,
            text_color=theme.COLOR_TEXT_PRIMARY,
            font=theme.get_font(theme.FONT_BODY),
            wrap="word",
        )
        content_box.pack(fill="both", expand=True, padx=14, pady=14)
        
        piano_header = "### 🎹 Piano Application" if lang == "en" else "### 🎹 Aplicação no Piano"
        guitar_header = "### 🎸 Guitar / Viola Application" if lang == "en" else "### 🎸 Aplicação na Viola"
        combined_markdown = chap.get_content_markdown(lang).strip() + f"\n\n---\n\n{piano_header}\n\n" + chap.get_piano_focus(lang).strip() + f"\n\n---\n\n{guitar_header}\n\n" + chap.get_guitar_focus(lang).strip()
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
        demo_type = getattr(chap, "interactive_demo", "chords")
        
        if demo_type == "circle_of_fifths":
            self._build_circle_of_fifths_lab(chap)
        elif demo_type == "voice_leading":
            self._build_voice_leading_lab(chap)
        elif demo_type == "harmonic_field_builder":
            self._build_harmonic_field_lab(chap)
        else:
            self._build_standard_theory_lab(chap)

    # ── LAB 1: CÍRCULO DE QUINTAS INTERATIVO ────────────────────────────────────
    def _build_circle_of_fifths_lab(self, chap: TheoryChapter):
        from gui.i18n import get_language, t
        lang = get_language()

        card = ctk.CTkFrame(
            self.content_scroll,
            corner_radius=theme.RADIUS_LG,
            fg_color=theme.COLOR_SURFACE,
            border_width=1,
            border_color=theme.COLOR_BORDER,
        )
        card.pack(fill="x", padx=8, pady=(0, 12))

        title_lbl = "🎡 Círculo de Quintas Interativo: Armações & Relativas" if lang != "en" else "🎡 Interactive Circle of Fifths: Key Signatures & Relatives"
        ctk.CTkLabel(card, text=title_lbl, font=theme.get_font(theme.FONT_SUBTITLE), text_color=theme.COLOR_TEXT_PRIMARY).pack(anchor="w", padx=16, pady=(12, 4))

        sub_desc = "Clica numa tonalidade maior para explorar a sua armação de clave, relativa menor e acordes diatónicos:" if lang != "en" else "Click on a major key to explore its key signature, relative minor, and diatonic chords:"
        ctk.CTkLabel(card, text=sub_desc, font=theme.get_font(theme.FONT_BODY), text_color=theme.COLOR_TEXT_MUTED).pack(anchor="w", padx=16, pady=(0, 8))

        # Circle buttons row
        CIRCLE_KEYS = [
            ("C", "0 ♯/♭", "Am"),
            ("G", "1 ♯", "Em"),
            ("D", "2 ♯", "Bm"),
            ("A", "3 ♯", "F#m"),
            ("E", "4 ♯", "C#m"),
            ("B", "5 ♯", "G#m"),
            ("F#", "6 ♯", "D#m"),
            ("Db", "5 ♭", "Bbm"),
            ("Ab", "4 ♭", "Fm"),
            ("Eb", "3 ♭", "Cm"),
            ("Bb", "2 ♭", "Gm"),
            ("F", "1 ♭", "Dm"),
        ]

        keys_frame = ctk.CTkFrame(card, fg_color="transparent")
        keys_frame.pack(fill="x", padx=16, pady=4)

        self._circle_btn_dict = {}
        self._selected_circle_key = "C"

        for i, (k_maj, acc, k_min) in enumerate(CIRCLE_KEYS):
            row = i // 6
            col = i % 6
            btn = ctk.CTkButton(
                keys_frame,
                text=f"{k_maj}\n({k_min})",
                font=theme.get_font(theme.FONT_BADGE),
                width=85,
                height=45,
                fg_color=theme.COLOR_PRIMARY if k_maj == "C" else theme.COLOR_SURFACE_SECONDARY,
                text_color="#FFFFFF" if k_maj == "C" else theme.COLOR_TEXT_PRIMARY,
                hover_color=theme.COLOR_PRIMARY_HOVER,
                command=lambda k=k_maj, a=acc, m=k_min: self._on_circle_key_selected(k, a, m),
            )
            btn.grid(row=row, column=col, padx=4, pady=4, sticky="nsew")
            keys_frame.grid_columnconfigure(col, weight=1)
            self._circle_btn_dict[k_maj] = btn

        # Info & Diatonic chords panel
        self.circle_info_frame = ctk.CTkFrame(card, fg_color=theme.COLOR_SURFACE_SECONDARY, corner_radius=theme.RADIUS_MD)
        self.circle_info_frame.pack(fill="x", padx=16, pady=(8, 12))

        self.circle_info_lbl = ctk.CTkLabel(
            self.circle_info_frame,
            text="",
            font=theme.get_font(theme.FONT_BODY_BOLD),
            text_color="#38BDF8",
            justify="left",
        )
        self.circle_info_lbl.pack(anchor="w", padx=14, pady=(8, 4))

        self.circle_chords_lbl = ctk.CTkLabel(
            self.circle_info_frame,
            text="",
            font=theme.get_font(theme.FONT_BODY),
            text_color=theme.COLOR_TEXT_PRIMARY,
            justify="left",
        )
        self.circle_chords_lbl.pack(anchor="w", padx=14, pady=(0, 8))

        # Audio Play Scale button
        circle_audio_btn = ctk.CTkButton(
            self.circle_info_frame,
            text="🔊 Ouvir Escala & Tríade Principal" if lang != "en" else "🔊 Play Scale & Primary Triad",
            font=theme.get_font(theme.FONT_SMALL_BOLD),
            fg_color=theme.COLOR_PRIMARY,
            hover_color=theme.COLOR_PRIMARY_HOVER,
            command=self._play_circle_audio,
        )
        circle_audio_btn.pack(anchor="w", padx=14, pady=(0, 10))

        self._on_circle_key_selected("C", "0 ♯/♭", "Am")

    def _on_circle_key_selected(self, key_maj: str, accidentals: str, key_min: str):
        self._selected_circle_key = key_maj
        for k, btn in self._circle_btn_dict.items():
            if k == key_maj:
                btn.configure(fg_color=theme.COLOR_PRIMARY, text_color="#FFFFFF")
            else:
                btn.configure(fg_color=theme.COLOR_SURFACE_SECONDARY, text_color=theme.COLOR_TEXT_PRIMARY)

        root = Note(key_maj, 4)
        scale = Scale(root, "major")
        pitches = scale.note_names

        # Compute diatonic triads I, ii, iii, IV, V, vi, vii°
        triad_types = ["", "m", "m", "", "", "m", "°"]
        diatonic_triads = [f"{pitches[i]}{triad_types[i]}" for i in range(7)]

        self.circle_info_lbl.configure(
            text=f"Tonalidade: {key_maj} Maior (Relativa: {key_min}) • Armação: {accidentals}\nNotas da Escala: {' - '.join(pitches)}"
        )
        self.circle_chords_lbl.configure(
            text=(
                f"Acordes Diatónicos:\n"
                f"  • Tónica (I): {diatonic_triads[0]} | Relativa Menor (vi): {diatonic_triads[5]}\n"
                f"  • Subdominante (IV): {diatonic_triads[3]} | Pré-dominante (ii): {diatonic_triads[1]}\n"
                f"  • Dominante (V): {diatonic_triads[4]} | Sensível (vii°): {diatonic_triads[6]}"
            )
        )

    def _play_circle_audio(self):
        root = Note(self._selected_circle_key, 4)
        scale = Scale(root, "major")
        chord = Chord(root, "major")
        # Play scale followed by chord
        self.audio_player.play_sequence(scale.notes, delay_between=0.25, note_duration=0.45)
        self.after(2200, lambda: self.audio_player.play_chord(chord.notes, duration=1.2))

    # ── LAB 2: VISUALIZADOR DE CONDUÇÃO DE VOZES (VOICE LEADING) ───────────────
    def _build_voice_leading_lab(self, chap: TheoryChapter):
        from gui.i18n import get_language
        lang = get_language()

        card = ctk.CTkFrame(
            self.content_scroll,
            corner_radius=theme.RADIUS_LG,
            fg_color=theme.COLOR_SURFACE,
            border_width=1,
            border_color=theme.COLOR_BORDER,
        )
        card.pack(fill="x", padx=8, pady=(0, 12))

        title_lbl = "🎼 Laboratório de Condução de Vozes & Cadências (Voice Leading)" if lang != "en" else "🎼 Voice Leading & Cadence Laboratory"
        ctk.CTkLabel(card, text=title_lbl, font=theme.get_font(theme.FONT_SUBTITLE), text_color=theme.COLOR_TEXT_PRIMARY).pack(anchor="w", padx=16, pady=(12, 4))

        sub_desc = "Observa que notas se mantêm comuns e como as vozes se movem por semitom ou tom entre acordes:" if lang != "en" else "Observe common tones and smooth stepwise voice movements between chords:"
        ctk.CTkLabel(card, text=sub_desc, font=theme.get_font(theme.FONT_BODY), text_color=theme.COLOR_TEXT_MUTED).pack(anchor="w", padx=16, pady=(0, 8))

        # Progression selector
        prog_row = ctk.CTkFrame(card, fg_color="transparent")
        prog_row.pack(fill="x", padx=16, pady=4)

        ctk.CTkLabel(prog_row, text="Progressão / Cadência:", font=theme.get_font(theme.FONT_BODY_BOLD), text_color=theme.COLOR_TEXT_PRIMARY).pack(side="left", padx=(0, 8))

        self.vl_prog_options = [
            "Cadência Autêntica (G7 → C)",
            "Cadência Plagal (F → C)",
            "Cadência Deceptiva (G7 → Am)",
            "ii - V - I em Dó (Dm7 → G7 → Cmaj7)",
            "Substituição Tritónica (Db7 → Cmaj7)",
            "Eólio / Pop Clássico (Am → F → C → G)",
        ]
        self.vl_prog_select = ctk.CTkOptionMenu(
            prog_row,
            values=self.vl_prog_options,
            command=lambda e: self._on_voice_leading_change(),
            width=280,
        )
        self.vl_prog_select.set(self.vl_prog_options[0])
        self.vl_prog_select.pack(side="left", padx=4)

        play_vl_btn = ctk.CTkButton(
            prog_row,
            text="▶ Ouvir Transição",
            font=theme.get_font(theme.FONT_SMALL_BOLD),
            fg_color="#7C3AED",
            hover_color="#6D28D9",
            command=self._play_voice_leading_audio,
        )
        play_vl_btn.pack(side="left", padx=8)

        # Voice leading visual analysis box
        self.vl_analysis_box = ctk.CTkFrame(card, fg_color=theme.COLOR_SURFACE_SECONDARY, corner_radius=theme.RADIUS_MD)
        self.vl_analysis_box.pack(fill="x", padx=16, pady=(8, 12))

        self.vl_analysis_lbl = ctk.CTkLabel(
            self.vl_analysis_box,
            text="",
            font=theme.get_font(theme.FONT_BODY_BOLD),
            text_color="#38BDF8",
            justify="left",
        )
        self.vl_analysis_lbl.pack(anchor="w", padx=14, pady=(8, 4))

        self.vl_details_lbl = ctk.CTkLabel(
            self.vl_analysis_box,
            text="",
            font=theme.get_font(theme.FONT_BODY),
            text_color=theme.COLOR_TEXT_PRIMARY,
            justify="left",
        )
        self.vl_details_lbl.pack(anchor="w", padx=14, pady=(0, 8))

        # Staff Canvas for visual comparison
        self.vl_staff = StaffCanvas(card, width=650, height=140, clef="treble", show_note_names=True)
        self.vl_staff.pack(pady=4)

        # Piano Keyboard
        self.vl_piano = PianoKeyboard(card, start_octave=2, num_octaves=4, key_width=25, key_height=110)
        self.vl_piano.pack(pady=(4, 12))

        self._on_voice_leading_change()

    def _get_voice_leading_data(self):
        sel = self.vl_prog_select.get()
        if "Autêntica" in sel:
            c1 = Chord(Note("G3"), "dom7")
            c2 = Chord(Note("C4"), "major")
            desc = "G7 (G-B-D-F) → C (C-E-G):\n• Nota Comum mantida: Sol (G)\n• Sensível Si (B) sobe meio-tom para a tónica Dó (C)\n• Sétima Fá (F) desce meio-tom para a terça Mi (E) — resolução do trítono Si-Fá!"
            return [c1, c2], desc
        elif "Plagal" in sel:
            c1 = Chord(Note("F3"), "major")
            c2 = Chord(Note("C4"), "major")
            desc = "F (F-A-C) → C (C-E-G):\n• Nota Comum mantida: Dó (C)\n• Fá desce para Mi (1 st), Lá desce para Sol (2 st). Resolução serena sem tensão de sensível."
            return [c1, c2], desc
        elif "Deceptiva" in sel:
            c1 = Chord(Note("G3"), "dom7")
            c2 = Chord(Note("A3"), "minor")
            desc = "G7 (G-B-D-F) → Am (A-C-E):\n• Surpresa auditiva: o ouvido espera Dó Maior (I) mas recebe Lá menor (vi)\n• Si sobe para Dó, Fá desce para Mi, mas o baixo resolve enganosamente em Lá!"
            return [c1, c2], desc
        elif "ii - V - I" in sel:
            c1 = Chord(Note("D4"), "min7")
            c2 = Chord(Note("G3"), "dom7")
            c3 = Chord(Note("C4"), "maj7")
            desc = "Dm7 → G7 → Cmaj7 (ii - V - I do Jazz):\n• Dm7 (D-F-A-C) → G7 (G-B-D-F) → Cmaj7 (C-E-G-B)\n• O 7º grau de cada acorde desce meio-tom para se tornar o 3º grau do acorde seguinte!"
            return [c1, c2, c3], desc
        elif "Tritónica" in sel:
            c1 = Chord(Note("Db4"), "dom7")
            c2 = Chord(Note("C4"), "maj7")
            desc = "D♭7 → Cmaj7 (Substituição Tritónica / SubV7):\n• D♭7 partilha exatamente o mesmo trítono Fá-Si de G7\n• Todas as vozes descem cromaticamente por meio-tom em direção a Cmaj7!"
            return [c1, c2], desc
        else:
            c1 = Chord(Note("A3"), "minor")
            c2 = Chord(Note("F3"), "major")
            c3 = Chord(Note("C4"), "major")
            c4 = Chord(Note("G3"), "major")
            desc = "Am → F → C → G (Progressão Eólia / Pop das 4 Chords):\n• Movimento contínuo de notas comuns: Dó compartilhado entre Am, F e C; Sol compartilhado entre C e G."
            return [c1, c2, c3, c4], desc

    def _on_voice_leading_change(self):
        chords, desc = self._get_voice_leading_data()
        self.vl_analysis_lbl.configure(text=f"Análise de Condução de Vozes: {self.vl_prog_select.get()}")
        self.vl_details_lbl.configure(text=desc)

        # Show first chord notes on staff and piano
        first_chord = chords[0]
        self.vl_staff.set_notes(first_chord.notes, colors=["#38BDF8"] * len(first_chord.notes))
        midi_map = {n.midi: "#38BDF8" for n in first_chord.notes}
        self.vl_piano.highlight_by_midi(midi_map)

    def _play_voice_leading_audio(self):
        chords, _ = self._get_voice_leading_data()
        for idx, chord in enumerate(chords):
            self.after(int(idx * 1100), lambda c=chord: self._display_and_play_vl_step(c))

    def _display_and_play_vl_step(self, chord: Chord):
        if not self.winfo_exists():
            return
        self.vl_staff.set_notes(chord.notes, colors=["#10B981"] * len(chord.notes))
        midi_map = {n.midi: "#10B981" for n in chord.notes}
        self.vl_piano.highlight_by_midi(midi_map)
        self.audio_player.play_chord(chord.notes, duration=1.0)

    # ── LAB 3: CONSTRUTOR DE CAMPO HARMÓNICO MAIOR E MENOR ─────────────────────
    def _build_harmonic_field_lab(self, chap: TheoryChapter):
        from gui.i18n import get_language
        lang = get_language()

        card = ctk.CTkFrame(
            self.content_scroll,
            corner_radius=theme.RADIUS_LG,
            fg_color=theme.COLOR_SURFACE,
            border_width=1,
            border_color=theme.COLOR_BORDER,
        )
        card.pack(fill="x", padx=8, pady=(0, 12))

        title_lbl = "🏛️ Construtor & Harmonizador de Campo Harmónico" if lang != "en" else "🏛️ Harmonic Field Builder & Harmonizer"
        ctk.CTkLabel(card, text=title_lbl, font=theme.get_font(theme.FONT_SUBTITLE), text_color=theme.COLOR_TEXT_PRIMARY).pack(anchor="w", padx=16, pady=(12, 4))

        ctrl_row = ctk.CTkFrame(card, fg_color="transparent")
        ctrl_row.pack(fill="x", padx=16, pady=4)

        ctk.CTkLabel(ctrl_row, text="Tónica:", font=theme.get_font(theme.FONT_BODY_BOLD), text_color=theme.COLOR_TEXT_PRIMARY).pack(side="left", padx=(0, 4))
        self.hf_root_select = ctk.CTkOptionMenu(
            ctrl_row,
            values=["C", "D", "E", "F", "G", "A", "B", "Bb", "Eb", "Ab", "F#"],
            command=lambda e: self._on_harmonic_field_change(),
            width=75,
        )
        self.hf_root_select.set("A" if "minor" in chap.id else "C")
        self.hf_root_select.pack(side="left", padx=4)

        ctk.CTkLabel(ctrl_row, text="Modo / Tipo de Campo:", font=theme.get_font(theme.FONT_BODY_BOLD), text_color=theme.COLOR_TEXT_PRIMARY).pack(side="left", padx=(10, 4))
        self.hf_mode_select = ctk.CTkOptionMenu(
            ctrl_row,
            values=["Maior Natural (Jónico)", "Menor Natural (Eólio)", "Menor Harmónica (V7 Maior)", "Dórico", "Mixolídio"],
            command=lambda e: self._on_harmonic_field_change(),
            width=220,
        )
        self.hf_mode_select.set("Menor Harmónica (V7 Maior)" if "minor" in chap.id else "Maior Natural (Jónico)")
        self.hf_mode_select.pack(side="left", padx=4)

        # 7 Degree Buttons Frame
        self.hf_degrees_frame = ctk.CTkFrame(card, fg_color="transparent")
        self.hf_degrees_frame.pack(fill="x", padx=16, pady=(8, 4))

        self.hf_info_lbl = ctk.CTkLabel(card, text="", font=theme.get_font(theme.FONT_BODY_BOLD), text_color="#38BDF8")
        self.hf_info_lbl.pack(anchor="w", padx=16, pady=(4, 6))

        # Staff Canvas
        self.hf_staff = StaffCanvas(card, width=650, height=140, clef="treble", show_note_names=True)
        self.hf_staff.pack(pady=4)

        # Piano Keyboard
        self.hf_piano = PianoKeyboard(card, start_octave=2, num_octaves=4, key_width=25, key_height=110)
        self.hf_piano.pack(pady=(4, 12))

        self._on_harmonic_field_change()

    def _on_harmonic_field_change(self):
        root_name = self.hf_root_select.get()
        mode = self.hf_mode_select.get()

        for child in self.hf_degrees_frame.winfo_children():
            child.destroy()

        root = Note(root_name, 4)
        if "Menor Harmónica" in mode:
            scale = Scale(root, "harmonic_minor")
            triad_qualities = ["m", "°", "aug", "m", "", "", "°"]
            romans = ["i", "ii°", "III+", "iv", "V", "VI", "vii°"]
        elif "Menor Natural" in mode:
            scale = Scale(root, "natural_minor")
            triad_qualities = ["m", "°", "", "m", "m", "", ""]
            romans = ["i", "ii°", "III", "iv", "v", "VI", "VII"]
        elif "Dórico" in mode:
            scale = Scale(root, "dorian")
            triad_qualities = ["m", "m", "", "", "m", "°", ""]
            romans = ["i", "ii", "III", "IV", "v", "vi°", "VII"]
        elif "Mixolídio" in mode:
            scale = Scale(root, "mixolydian")
            triad_qualities = ["", "m", "°", "", "m", "m", ""]
            romans = ["I", "ii", "iii°", "IV", "v", "vi", "VII"]
        else:
            scale = Scale(root, "major")
            triad_qualities = ["", "m", "m", "", "", "m", "°"]
            romans = ["I", "ii", "iii", "IV", "V", "vi", "vii°"]

        pitches = scale.note_names
        self.hf_generated_chords = []

        for i in range(7):
            chord_name = f"{pitches[i]}{triad_qualities[i]}"
            r_num = romans[i]
            # Form notes 1-3-5 on scale
            n1 = scale.notes[i % 7]
            n2 = scale.notes[(i + 2) % 7]
            n3 = scale.notes[(i + 4) % 7]
            chord_notes = [n1, n2, n3]
            self.hf_generated_chords.append((chord_name, r_num, chord_notes))

            btn = ctk.CTkButton(
                self.hf_degrees_frame,
                text=f"{r_num}\n{chord_name}",
                font=theme.get_font(theme.FONT_BADGE),
                width=80,
                height=42,
                fg_color=theme.COLOR_SURFACE_SECONDARY,
                text_color=theme.COLOR_TEXT_PRIMARY,
                hover_color=theme.COLOR_PRIMARY_HOVER,
                command=lambda idx=i: self._select_hf_degree(idx),
            )
            btn.pack(side="left", expand=True, fill="x", padx=2)

        self._select_hf_degree(0)

    def _select_hf_degree(self, degree_idx: int):
        chord_name, r_num, chord_notes = self.hf_generated_chords[degree_idx]
        note_str = " - ".join(n.pitch for n in chord_notes)
        self.hf_info_lbl.configure(text=f"Grau {r_num}: Acorde de {chord_name} (Notas: {note_str})")
        self.hf_staff.set_notes(chord_notes, colors=["#10B981"] + ["#38BDF8"] * (len(chord_notes) - 1))
        midi_map = {n.midi: ("#10B981" if i == 0 else "#38BDF8") for i, n in enumerate(chord_notes)}
        self.hf_piano.highlight_by_midi(midi_map)
        self.audio_player.play_chord(chord_notes, duration=1.0)

    # ── LAB 4: STANDARD THEME LAB (FALLBACK / GENERAL) ─────────────────────────
    def _build_standard_theory_lab(self, chap: TheoryChapter):
        demo_card = ctk.CTkFrame(
            self.content_scroll,
            corner_radius=theme.RADIUS_LG,
            fg_color=theme.COLOR_SURFACE,
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
            values=["C", "C#", "Db", "D", "D#", "Eb", "E", "F", "F#", "Gb", "G", "G#", "Ab", "A", "A#", "Bb", "B"],
            command=lambda e: self._on_demo_state_change(),
            width=80,
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
            fg_color=theme.COLOR_SURFACE,
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
