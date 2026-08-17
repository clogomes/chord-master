"""Musical Glossary & Terminology Explorer Screen."""
import time
from typing import Callable, List, Optional
import customtkinter as ctk
from core.glossary import GLOSSARY_DATABASE, GlossaryTerm, search_terms, get_term_by_id
from core.user_manager import UserManager
from gui.i18n import t, get_language
from gui import theme
from audio.player import get_audio_player
from gui.scroll_utils import bind_mousewheel


CATEGORY_OPTIONS = [
    ("todos", "Todos"),
    ("harmonia", "Harmonia"),
    ("ritmo", "Ritmo"),
    ("notacao", "Notação"),
    ("modos", "Modos & Escalas"),
    ("tecnica", "Técnica"),
    ("acustica", "Acústica"),
    ("forma", "Forma & Estrutura"),
    ("jazz", "Jazz & Bossa"),
]

ALPHABET = ["Todos", "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "Z"]


class GlossaryScreen(ctk.CTkFrame):
    """
    Comprehensive interactive musical glossary and terminology search screen.
    Includes instant full-text filtering, A-Z index, category chips, instrument examples, and audio playback.
    """

    def __init__(
        self,
        master,
        user_manager: UserManager,
        on_back: Callable[[], None],
        on_navigate_chapter: Optional[Callable[[str], None]] = None,
        initial_term_id: Optional[str] = None,
        **kwargs,
    ):
        super().__init__(master, fg_color=theme.COLOR_BG, **kwargs)
        self.user_manager = user_manager
        self.on_back = on_back
        self.on_navigate_chapter = on_navigate_chapter
        self.audio_player = get_audio_player()
        self.lang = get_language()

        self.active_category = "todos"
        self.active_letter = "Todos"
        self.active_chapter = "todos"
        self.selected_term: Optional[GlossaryTerm] = None
        self.filtered_terms: List[GlossaryTerm] = []

        self._search_job = None
        self._displayed_count = 35
        self._term_card_widgets = {}  # term_id -> (card_frame, title_lbl, snippet_lbl, cat_pill)
        self._load_more_btn = None

        self._term_buttons: List[ctk.CTkButton] = []

        self._build_ui()

        # Select initial or first term
        if initial_term_id:
            self.select_term_by_id(initial_term_id)
        else:
            self._filter_terms()
            if self.filtered_terms:
                self.select_term(self.filtered_terms[0])

    def _build_ui(self):
        # 1. Top Navigation Bar
        nav_bar = ctk.CTkFrame(self, fg_color="transparent")
        nav_bar.pack(fill="x", padx=20, pady=(16, 6))

        back_btn = ctk.CTkButton(
            nav_bar,
            text=t("btn_back", "← Voltar ao Menu"),
            font=theme.get_font(theme.FONT_BODY_BOLD),
            fg_color="#475569",
            hover_color="#334155",
            width=140,
            height=38,
            corner_radius=theme.RADIUS_MD,
            command=self.on_back,
        )
        back_btn.pack(side="left")

        user = self.user_manager.current_user
        title_lbl = ctk.CTkLabel(
            nav_bar,
            text=f"📚 {t('glossary_title', 'Glossário Musical Interativo')} ({user.avatar} {user.username})",
            font=theme.get_font(theme.FONT_TITLE),
            text_color=theme.COLOR_TEXT_PRIMARY,
        )
        title_lbl.pack(side="left", padx=16)

        self.term_count_lbl = ctk.CTkLabel(
            nav_bar,
            text=f"{len(GLOSSARY_DATABASE)} Termos",
            font=theme.get_font(theme.FONT_BADGE),
            text_color="#FFFFFF",
            fg_color=theme.COLOR_PRIMARY,
            corner_radius=theme.RADIUS_SM,
            padx=10,
            pady=4,
        )
        self.term_count_lbl.pack(side="right")

        # 2. Search & Category Filter Header
        filters_card = ctk.CTkFrame(
            self,
            corner_radius=theme.RADIUS_LG,
            fg_color=theme.COLOR_SURFACE,
            border_width=1,
            border_color=theme.COLOR_BORDER,
        )
        filters_card.pack(fill="x", padx=20, pady=(4, 10))

        # Search Row
        search_row = ctk.CTkFrame(filters_card, fg_color="transparent")
        search_row.pack(fill="x", padx=16, pady=(12, 6))

        search_icon = ctk.CTkLabel(
            search_row,
            text="🔍",
            font=theme.get_font(theme.FONT_BODY),
            text_color=theme.COLOR_TEXT_PRIMARY,
        )
        search_icon.pack(side="left", padx=(0, 6))

        self.search_entry = ctk.CTkEntry(
            search_row,
            placeholder_text=t("glossary_search_placeholder", "Pesquisar termo, fórmula, conceito ou instrumento..."),
            font=theme.get_font(theme.FONT_BODY),
            height=38,
            corner_radius=theme.RADIUS_MD,
        )
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.search_entry.bind("<KeyRelease>", lambda e: self._on_search_changed())

        clear_btn = ctk.CTkButton(
            search_row,
            text="✕ Limpar",
            font=theme.get_font(theme.FONT_SMALL),
            fg_color=theme.COLOR_SURFACE_SECONDARY,
            hover_color=theme.COLOR_BORDER,
            text_color=theme.COLOR_TEXT_PRIMARY,
            width=80,
            height=36,
            corner_radius=theme.RADIUS_MD,
            command=self._clear_search,
        )
        clear_btn.pack(side="right")

        # Category Chips Row
        cats_row = ctk.CTkFrame(filters_card, fg_color="transparent")
        cats_row.pack(fill="x", padx=16, pady=(0, 10))

        cat_lbl = ctk.CTkLabel(
            cats_row,
            text=t("lbl_category", "Categoria:"),
            font=theme.get_font(theme.FONT_BODY_BOLD),
            text_color=theme.COLOR_TEXT_PRIMARY,
        )
        cat_lbl.pack(side="left", padx=(0, 10))

        self.cat_segmented = ctk.CTkSegmentedButton(
            cats_row,
            values=[label for _, label in CATEGORY_OPTIONS],
            command=self._on_category_selected,
            selected_color=theme.COLOR_PRIMARY,
            selected_hover_color=theme.COLOR_PRIMARY_HOVER,
            font=theme.get_font(theme.FONT_SMALL),
            height=32,
        )
        self.cat_segmented.set("Todos")
        self.cat_segmented.pack(side="left", fill="x", expand=True)

        # 3. Main Two-Pane Split Layout
        split_frame = ctk.CTkFrame(self, fg_color="transparent")
        split_frame.pack(fill="both", expand=True, padx=20, pady=(0, 16))
        split_frame.grid_columnconfigure(0, weight=4)  # Left list
        split_frame.grid_columnconfigure(1, weight=6)  # Right detail
        split_frame.grid_rowconfigure(0, weight=1)

        # Left Column: Alphabet Bar + Terms List
        left_col = ctk.CTkFrame(
            split_frame,
            corner_radius=theme.RADIUS_LG,
            fg_color=theme.COLOR_SURFACE,
            border_width=1,
            border_color=theme.COLOR_BORDER,
        )
        left_col.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        # Alphabet Index Bar
        alpha_frame = ctk.CTkScrollableFrame(
            left_col,
            orientation="horizontal",
            height=40,
            fg_color="transparent",
        )
        alpha_frame.pack(fill="x", padx=8, pady=(8, 4))
        bind_mousewheel(alpha_frame, recursive=False)

        self._alpha_btns = {}
        for letter in ALPHABET:
            btn = ctk.CTkButton(
                alpha_frame,
                text=letter,
                width=34,
                height=28,
                font=theme.get_font(theme.FONT_SMALL),
                fg_color=theme.COLOR_PRIMARY if letter == "Todos" else theme.COLOR_SURFACE_SECONDARY,
                hover_color=theme.COLOR_PRIMARY_HOVER,
                text_color="#FFFFFF" if letter == "Todos" else theme.COLOR_TEXT_PRIMARY,
                corner_radius=theme.RADIUS_SM,
                command=lambda l=letter: self._on_letter_selected(l),
            )
            btn.pack(side="left", padx=2)
            self._alpha_btns[letter] = btn

        # Terms Scrollable List
        self.terms_list_frame = ctk.CTkScrollableFrame(
            left_col,
            corner_radius=theme.RADIUS_MD,
            fg_color="transparent",
        )
        self.terms_list_frame.pack(fill="both", expand=True, padx=8, pady=(4, 8))
        bind_mousewheel(self.terms_list_frame, recursive=False)

        # Right Column: Term Detail Card
        self.detail_card = ctk.CTkScrollableFrame(
            split_frame,
            corner_radius=theme.RADIUS_LG,
            fg_color=theme.COLOR_SURFACE,
            border_width=1,
            border_color=theme.COLOR_BORDER,
        )
        self.detail_card.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        bind_mousewheel(self.detail_card, recursive=False)

    def _filter_terms(self):
        query = self.search_entry.get().strip()
        cat_key = "todos"
        for k, label in CATEGORY_OPTIONS:
            if label == self.active_category:
                cat_key = k
                break

        results = search_terms(
            query=query,
            category=cat_key,
            chapter=self.active_chapter if self.active_chapter != "todos" else None,
            lang=self.lang,
        )

        # Filter by letter if selected
        if self.active_letter != "Todos":
            results = [
                t for t in results
                if t.get_term(self.lang).upper().startswith(self.active_letter)
            ]

        self.filtered_terms = results
        self.term_count_lbl.configure(text=f"{len(results)} Termos")
        self._displayed_count = 35
        self._render_terms_list()

    def _render_terms_list(self):
        # Clear existing term cards
        for widget in self.terms_list_frame.winfo_children():
            widget.destroy()

        self._term_card_widgets.clear()
        self._load_more_btn = None

        if not self.filtered_terms:
            empty_lbl = ctk.CTkLabel(
                self.terms_list_frame,
                text=t("glossary_empty_search", "Nenhum termo encontrado."),
                font=theme.get_font(theme.FONT_BODY),
                text_color=theme.COLOR_TEXT_MUTED,
            )
            empty_lbl.pack(pady=40)
            return

        visible_terms = self.filtered_terms[:self._displayed_count]

        for term in visible_terms:
            self._create_term_card(term)

        if len(self.filtered_terms) > self._displayed_count:
            remaining = len(self.filtered_terms) - self._displayed_count
            self._load_more_btn = ctk.CTkButton(
                self.terms_list_frame,
                text=f"Carregar Mais (+{min(remaining, 35)} de {remaining} restantes)...",
                font=theme.get_font(theme.FONT_BODY_BOLD),
                fg_color=theme.COLOR_SURFACE_SECONDARY,
                hover_color=theme.COLOR_BORDER,
                text_color=theme.COLOR_TEXT_PRIMARY,
                height=36,
                corner_radius=theme.RADIUS_MD,
                command=self._load_more_terms,
            )
            self._load_more_btn.pack(fill="x", pady=(6, 12), padx=4)

    def _create_term_card(self, term: GlossaryTerm):
        is_active = (self.selected_term and self.selected_term.id == term.id)
        
        card = ctk.CTkFrame(
            self.terms_list_frame,
            corner_radius=theme.RADIUS_MD,
            fg_color=theme.COLOR_PRIMARY if is_active else theme.COLOR_SURFACE_SECONDARY,
            border_width=1,
            border_color=theme.COLOR_PRIMARY if is_active else theme.COLOR_BORDER,
            cursor="hand2",
        )
        card.pack(fill="x", pady=3, padx=2)

        def make_click_handler(t_obj=term):
            return lambda e: self.select_term(t_obj)

        card.bind("<Button-1>", make_click_handler())

        # Top row: Term name + Category tag
        top_row = ctk.CTkFrame(card, fg_color="transparent")
        top_row.pack(fill="x", padx=10, pady=(6, 2))
        top_row.bind("<Button-1>", make_click_handler())

        title_lbl = ctk.CTkLabel(
            top_row,
            text=term.get_term(self.lang),
            font=theme.get_font(theme.FONT_BODY_BOLD),
            text_color="#FFFFFF" if is_active else theme.COLOR_TEXT_PRIMARY,
            anchor="w",
        )
        title_lbl.pack(side="left", fill="x", expand=True)
        title_lbl.bind("<Button-1>", make_click_handler())

        cat_pill = ctk.CTkLabel(
            top_row,
            text=term.category.upper(),
            font=theme.get_font(theme.FONT_SMALL),
            text_color="#FFFFFF" if is_active else theme.COLOR_TEXT_MUTED,
            fg_color=theme.COLOR_PRIMARY_HOVER if is_active else theme.COLOR_SURFACE,
            corner_radius=theme.RADIUS_SM,
            padx=6,
            pady=1,
        )
        cat_pill.pack(side="right")
        cat_pill.bind("<Button-1>", make_click_handler())

        # Preview snippet
        snippet_lbl = ctk.CTkLabel(
            card,
            text=term.get_short_def(self.lang),
            font=theme.get_font(theme.FONT_SMALL),
            text_color="#E0E7FF" if is_active else theme.COLOR_TEXT_MUTED,
            anchor="w",
            justify="left",
            wraplength=340,
        )
        snippet_lbl.pack(fill="x", padx=10, pady=(0, 6))
        snippet_lbl.bind("<Button-1>", make_click_handler())

        self._term_card_widgets[term.id] = (card, title_lbl, snippet_lbl, cat_pill)

    def _load_more_terms(self):
        if self._load_more_btn:
            self._load_more_btn.destroy()
            self._load_more_btn = None

        start_idx = self._displayed_count
        self._displayed_count += 35
        next_batch = self.filtered_terms[start_idx:self._displayed_count]

        for term in next_batch:
            self._create_term_card(term)

        if len(self.filtered_terms) > self._displayed_count:
            remaining = len(self.filtered_terms) - self._displayed_count
            self._load_more_btn = ctk.CTkButton(
                self.terms_list_frame,
                text=f"Carregar Mais (+{min(remaining, 35)} de {remaining} restantes)...",
                font=theme.get_font(theme.FONT_BODY_BOLD),
                fg_color=theme.COLOR_SURFACE_SECONDARY,
                hover_color=theme.COLOR_BORDER,
                text_color=theme.COLOR_TEXT_PRIMARY,
                height=36,
                corner_radius=theme.RADIUS_MD,
                command=self._load_more_terms,
            )
            self._load_more_btn.pack(fill="x", pady=(6, 12), padx=4)

    def select_term_by_id(self, term_id: str):
        term = get_term_by_id(term_id)
        if term:
            self.select_term(term)

    def select_term(self, term: GlossaryTerm):
        prev_term = self.selected_term
        self.selected_term = term

        # Update previous card styling without re-rendering entire list
        if prev_term and prev_term.id in self._term_card_widgets:
            card, title_lbl, snippet_lbl, cat_pill = self._term_card_widgets[prev_term.id]
            try:
                card.configure(fg_color=theme.COLOR_SURFACE_SECONDARY, border_color=theme.COLOR_BORDER)
                title_lbl.configure(text_color=theme.COLOR_TEXT_PRIMARY)
                snippet_lbl.configure(text_color=theme.COLOR_TEXT_MUTED)
                cat_pill.configure(fg_color=theme.COLOR_SURFACE, text_color=theme.COLOR_TEXT_MUTED)
            except Exception:
                pass

        # Update newly selected card styling
        if term.id in self._term_card_widgets:
            card, title_lbl, snippet_lbl, cat_pill = self._term_card_widgets[term.id]
            try:
                card.configure(fg_color=theme.COLOR_PRIMARY, border_color=theme.COLOR_PRIMARY)
                title_lbl.configure(text_color="#FFFFFF")
                snippet_lbl.configure(text_color="#E0E7FF")
                cat_pill.configure(fg_color=theme.COLOR_PRIMARY_HOVER, text_color="#FFFFFF")
            except Exception:
                pass

        self._render_detail_pane()

    def _render_detail_pane(self):
        # Clear detail card
        for widget in self.detail_card.winfo_children():
            widget.destroy()

        if not self.selected_term:
            return

        term = self.selected_term

        # 1. Header: Category + Formula
        meta_row = ctk.CTkFrame(self.detail_card, fg_color="transparent")
        meta_row.pack(fill="x", padx=16, pady=(12, 6))

        cat_badge = ctk.CTkLabel(
            meta_row,
            text=f"🏷️ {term.category.upper()}",
            font=theme.get_font(theme.FONT_BADGE),
            text_color="#FFFFFF",
            fg_color=theme.COLOR_PRIMARY,
            corner_radius=theme.RADIUS_SM,
            padx=10,
            pady=4,
        )
        cat_badge.pack(side="left")

        if term.formula:
            form_badge = ctk.CTkLabel(
                meta_row,
                text=f"📐 {term.formula}",
                font=theme.get_font(theme.FONT_BADGE),
                text_color=theme.COLOR_TEXT_PRIMARY,
                fg_color=theme.COLOR_SURFACE_SECONDARY,
                corner_radius=theme.RADIUS_SM,
                padx=10,
                pady=4,
            )
            form_badge.pack(side="left", padx=10)

        # 2. Term Title & English Subtitle
        term_title = ctk.CTkLabel(
            self.detail_card,
            text=term.get_term(self.lang),
            font=theme.get_font(theme.FONT_TITLE),
            text_color=theme.COLOR_TEXT_PRIMARY,
            anchor="w",
        )
        term_title.pack(fill="x", padx=16, pady=(4, 2))

        if term.term_en and self.lang == "pt":
            en_sub = ctk.CTkLabel(
                self.detail_card,
                text=f"Termo em Inglês: {term.term_en}",
                font=theme.get_font(theme.FONT_SMALL),
                text_color=theme.COLOR_TEXT_MUTED,
                anchor="w",
            )
            en_sub.pack(fill="x", padx=16, pady=(0, 10))

        # 3. Audio Demo Button if notes provided
        if term.hear_it:
            audio_btn = ctk.CTkButton(
                self.detail_card,
                text=f"🔊 {t('btn_hear_concept', 'Ouvir Conceito Sonoro')} ({', '.join(term.hear_it)})",
                font=theme.get_font(theme.FONT_BODY_BOLD),
                fg_color=theme.COLOR_SUCCESS,
                hover_color=theme.COLOR_SUCCESS_HOVER,
                height=38,
                corner_radius=theme.RADIUS_MD,
                command=self._play_term_audio,
            )
            audio_btn.pack(anchor="w", padx=16, pady=(0, 14))

        # 4. Short Definition Callout
        short_card = ctk.CTkFrame(
            self.detail_card,
            corner_radius=theme.RADIUS_MD,
            fg_color=theme.COLOR_SURFACE_SECONDARY,
            border_width=1,
            border_color=theme.COLOR_BORDER,
        )
        short_card.pack(fill="x", padx=16, pady=(0, 14))

        ctk.CTkLabel(
            short_card,
            text=term.get_short_def(self.lang),
            font=theme.get_font(theme.FONT_BODY_BOLD),
            text_color=theme.COLOR_TEXT_PRIMARY,
            wraplength=480,
            justify="left",
            anchor="w",
            padx=14,
            pady=10,
        ).pack(fill="x")

        # 5. Long Detailed Definition
        long_box = ctk.CTkFrame(self.detail_card, fg_color="transparent")
        long_box.pack(fill="x", padx=16, pady=(0, 14))

        ctk.CTkLabel(
            long_box,
            text=term.get_long_def(self.lang),
            font=theme.get_font(theme.FONT_BODY),
            text_color=theme.COLOR_TEXT_MUTED,
            wraplength=480,
            justify="left",
            anchor="w",
        ).pack(fill="x")

        # 6. Instrument Practical Applications (Piano & Guitar)
        if term.example_piano or term.example_guitar:
            inst_card = ctk.CTkFrame(
                self.detail_card,
                corner_radius=theme.RADIUS_MD,
                fg_color=theme.COLOR_SURFACE_SECONDARY,
                border_width=1,
                border_color=theme.COLOR_BORDER,
            )
            inst_card.pack(fill="x", padx=16, pady=(0, 14))

            ctk.CTkLabel(
                inst_card,
                text="🎸 Aplicação nos Instrumentos",
                font=theme.get_font(theme.FONT_SECTION),
                text_color=theme.COLOR_TEXT_PRIMARY,
                anchor="w",
            ).pack(fill="x", padx=14, pady=(10, 6))

            if term.example_piano:
                ctk.CTkLabel(
                    inst_card,
                    text=f"🎹 **Piano**: {term.example_piano}",
                    font=theme.get_font(theme.FONT_BODY),
                    text_color=theme.COLOR_TEXT_PRIMARY,
                    wraplength=460,
                    justify="left",
                    anchor="w",
                ).pack(fill="x", padx=14, pady=(2, 4))

            if term.example_guitar:
                ctk.CTkLabel(
                    inst_card,
                    text=f"🎸 **Viola / Guitarra**: {term.example_guitar}",
                    font=theme.get_font(theme.FONT_BODY),
                    text_color=theme.COLOR_TEXT_PRIMARY,
                    wraplength=460,
                    justify="left",
                    anchor="w",
                ).pack(fill="x", padx=14, pady=(2, 10))

        # 7. Cross-References ("Ver Também")
        if term.see_also:
            see_frame = ctk.CTkFrame(self.detail_card, fg_color="transparent")
            see_frame.pack(fill="x", padx=16, pady=(0, 14))

            ctk.CTkLabel(
                see_frame,
                text="🔗 Ver Também:",
                font=theme.get_font(theme.FONT_BODY_BOLD),
                text_color=theme.COLOR_TEXT_PRIMARY,
                anchor="w",
            ).pack(side="left", padx=(0, 8))

            tags_row = ctk.CTkFrame(see_frame, fg_color="transparent")
            tags_row.pack(side="left", fill="x", expand=True)

            for rel_id in term.see_also:
                rel_term = get_term_by_id(rel_id)
                btn_text = rel_term.get_term(self.lang) if rel_term else rel_id.replace("_", " ").title()
                
                tag_btn = ctk.CTkButton(
                    tags_row,
                    text=btn_text,
                    font=theme.get_font(theme.FONT_SMALL),
                    fg_color=theme.COLOR_SURFACE_SECONDARY,
                    hover_color=theme.COLOR_PRIMARY,
                    text_color=theme.COLOR_TEXT_PRIMARY,
                    height=28,
                    corner_radius=theme.RADIUS_SM,
                    command=lambda tid=rel_id: self.select_term_by_id(tid),
                )
                tag_btn.pack(side="left", padx=3, pady=2)

        # 8. Related Chapters ("Capítulos de Teoria")
        if term.chapters:
            chap_frame = ctk.CTkFrame(self.detail_card, fg_color="transparent")
            chap_frame.pack(fill="x", padx=16, pady=(0, 14))

            ctk.CTkLabel(
                chap_frame,
                text="📖 Capítulos de Teoria Relacionados:",
                font=theme.get_font(theme.FONT_BODY_BOLD),
                text_color=theme.COLOR_TEXT_PRIMARY,
                anchor="w",
            ).pack(fill="x", pady=(0, 6))

            chaps_box = ctk.CTkFrame(chap_frame, fg_color="transparent")
            chaps_box.pack(fill="x")

            for chap_id in term.chapters:
                chap_title = self._get_chapter_title(chap_id)
                chap_btn = ctk.CTkButton(
                    chaps_box,
                    text=f"👉 {chap_title}",
                    font=theme.get_font(theme.FONT_BODY_BOLD),
                    fg_color=theme.COLOR_PRIMARY,
                    hover_color=theme.COLOR_PRIMARY_HOVER,
                    height=34,
                    corner_radius=theme.RADIUS_MD,
                    command=lambda cid=chap_id: self._handle_chapter_click(cid),
                )
                chap_btn.pack(side="left", padx=4, pady=2)

    def _get_chapter_title(self, chapter_id: str) -> str:
        try:
            from core.theory_content import THEORY_CHAPTERS
            for ch in THEORY_CHAPTERS:
                if ch.id == chapter_id:
                    return ch.get_title(self.lang)
        except Exception:
            pass
        return chapter_id.replace("_", " ").title()

    def _handle_chapter_click(self, chapter_id: str):
        if self.on_navigate_chapter:
            self.on_navigate_chapter(chapter_id)
        else:
            # Fallback to back
            self.on_back()

    def _play_term_audio(self):
        if not self.selected_term or not self.selected_term.hear_it:
            return
        for i, pitch in enumerate(self.selected_term.hear_it):
            self.after(i * 320, lambda p=pitch: self.audio_player.play_note(p, duration_ms=650))

    def _on_search_changed(self):
        if self._search_job is not None:
            self.after_cancel(self._search_job)
            self._search_job = None
        self._search_job = self.after(220, self._filter_terms)

    def _clear_search(self):
        if self._search_job is not None:
            self.after_cancel(self._search_job)
            self._search_job = None
        self.search_entry.delete(0, "end")
        self._filter_terms()

    def _on_category_selected(self, value: str):
        self.active_category = value
        self._filter_terms()

    def _on_letter_selected(self, letter: str):
        self.active_letter = letter
        for l, btn in self._alpha_btns.items():
            if l == letter:
                btn.configure(fg_color=theme.COLOR_PRIMARY, text_color="#FFFFFF")
            else:
                btn.configure(fg_color=theme.COLOR_SURFACE_SECONDARY, text_color=theme.COLOR_TEXT_PRIMARY)
        self._filter_terms()
