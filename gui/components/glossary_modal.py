"""Interactive modal popup for instant glossary term lookup without leaving current screen."""
from typing import Optional
import customtkinter as ctk
from core.glossary import get_term_by_id, GlossaryTerm
from core.notes import Note
from gui.i18n import t, get_language
from gui import theme
from audio.player import get_audio_player


class GlossaryTermModal(ctk.CTkToplevel):
    """
    Floating modal dialog displaying rich definitions, formulas, instrument examples,
    and instant audio playback for a glossary term.
    """

    def __init__(self, master, term_id: str, **kwargs):
        super().__init__(master, **kwargs)
        self.term: Optional[GlossaryTerm] = get_term_by_id(term_id)
        self.lang = get_language()
        self.audio_player = get_audio_player()

        self.title(t("glossary_title", "Glossário Musical"))
        self.geometry("620x520")
        self.minsize(540, 420)
        self.configure(fg_color=theme.COLOR_BG)

        # Center on parent
        self.transient(master)
        self.grab_set()
        self._center_window()

        self._build_ui()

    def _center_window(self):
        self.update_idletasks()
        try:
            pw = self.master.winfo_width()
            ph = self.master.winfo_height()
            px = self.master.winfo_rootx()
            py = self.master.winfo_rooty()
            w = 620
            h = 520
            x = px + max(0, (pw - w) // 2)
            y = py + max(0, (ph - h) // 2)
            self.geometry(f"{w}x{h}+{x}+{y}")
        except Exception:
            pass

    def _build_ui(self):
        if not self.term:
            err_lbl = ctk.CTkLabel(
                self,
                text=t("glossary_not_found", "Termo não encontrado no glossário."),
                font=theme.get_font(theme.FONT_BODY_BOLD),
                text_color=theme.COLOR_ACCENT_CRIMSON,
            )
            err_lbl.pack(pady=40)
            return

        term = self.term

        # Main Container with scroll
        main_frame = ctk.CTkScrollableFrame(
            self,
            corner_radius=theme.RADIUS_LG,
            fg_color=theme.COLOR_SURFACE,
            border_width=1,
            border_color=theme.COLOR_BORDER,
        )
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Top Header: Category Pill + Close Button
        hdr_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        hdr_frame.pack(fill="x", pady=(0, 10))

        cat_badge = ctk.CTkLabel(
            hdr_frame,
            text=f"🏷️ {term.category.upper()}",
            font=theme.get_font(theme.FONT_BADGE),
            text_color="#FFFFFF",
            fg_color=theme.COLOR_PRIMARY,
            corner_radius=theme.RADIUS_SM,
            padx=10,
            pady=3,
        )
        cat_badge.pack(side="left")

        if term.formula:
            form_badge = ctk.CTkLabel(
                hdr_frame,
                text=f"📐 {term.formula}",
                font=theme.get_font(theme.FONT_BADGE),
                text_color=theme.COLOR_TEXT_PRIMARY,
                fg_color=theme.COLOR_SURFACE_SECONDARY,
                corner_radius=theme.RADIUS_SM,
                padx=10,
                pady=3,
            )
            form_badge.pack(side="left", padx=8)

        # Term Title (PT & EN)
        term_title = ctk.CTkLabel(
            main_frame,
            text=term.get_term(self.lang),
            font=theme.get_font(theme.FONT_TITLE),
            text_color=theme.COLOR_TEXT_PRIMARY,
            anchor="w",
            justify="left",
        )
        term_title.pack(fill="x", pady=(6, 2))

        if term.term_en and self.lang == "pt":
            en_sub = ctk.CTkLabel(
                main_frame,
                text=f"Termo em Inglês: {term.term_en}",
                font=theme.get_font(theme.FONT_SMALL),
                text_color=theme.COLOR_TEXT_MUTED,
                anchor="w",
            )
            en_sub.pack(fill="x", pady=(0, 12))

        # Audio Button if notes available
        if term.hear_it:
            audio_btn = ctk.CTkButton(
                main_frame,
                text=t("btn_hear_concept", "🔊 Ouvir Conceito Sonoro"),
                font=theme.get_font(theme.FONT_BODY_BOLD),
                fg_color=theme.COLOR_SUCCESS,
                hover_color=theme.COLOR_SUCCESS_HOVER,
                height=36,
                corner_radius=theme.RADIUS_MD,
                command=self._play_audio,
            )
            audio_btn.pack(anchor="w", pady=(0, 14))

        # Short Definition Box
        short_box = ctk.CTkFrame(
            main_frame,
            corner_radius=theme.RADIUS_MD,
            fg_color=theme.COLOR_SURFACE_SECONDARY,
            border_width=1,
            border_color=theme.COLOR_BORDER,
        )
        short_box.pack(fill="x", pady=(0, 12))

        ctk.CTkLabel(
            short_box,
            text=term.get_short_def(self.lang),
            font=theme.get_font(theme.FONT_BODY_BOLD),
            text_color=theme.COLOR_TEXT_PRIMARY,
            wraplength=520,
            justify="left",
            padx=14,
            pady=10,
        ).pack(fill="x")

        # Long In-depth Explanation
        long_box = ctk.CTkFrame(main_frame, fg_color="transparent")
        long_box.pack(fill="x", pady=(0, 14))

        ctk.CTkLabel(
            long_box,
            text=term.get_long_def(self.lang),
            font=theme.get_font(theme.FONT_BODY),
            text_color=theme.COLOR_TEXT_MUTED,
            wraplength=520,
            justify="left",
        ).pack(fill="x")

        # Instrument Examples (Piano & Guitar)
        if term.example_piano or term.example_guitar:
            inst_frame = ctk.CTkFrame(
                main_frame,
                corner_radius=theme.RADIUS_MD,
                fg_color=theme.COLOR_SURFACE_SECONDARY,
                border_width=1,
                border_color=theme.COLOR_BORDER,
            )
            inst_frame.pack(fill="x", pady=(0, 14), padx=2)

            ctk.CTkLabel(
                inst_frame,
                text="🎸 Aplicação Prática nos Instrumentos",
                font=theme.get_font(theme.FONT_SECTION),
                text_color=theme.COLOR_TEXT_PRIMARY,
                anchor="w",
            ).pack(fill="x", padx=14, pady=(10, 6))

            if term.example_piano:
                ctk.CTkLabel(
                    inst_frame,
                    text=f"🎹 **Piano**: {term.example_piano}",
                    font=theme.get_font(theme.FONT_BODY),
                    text_color=theme.COLOR_TEXT_PRIMARY,
                    wraplength=500,
                    justify="left",
                    anchor="w",
                ).pack(fill="x", padx=14, pady=(2, 4))

            if term.example_guitar:
                ctk.CTkLabel(
                    inst_frame,
                    text=f"🎸 **Viola / Guitarra**: {term.example_guitar}",
                    font=theme.get_font(theme.FONT_BODY),
                    text_color=theme.COLOR_TEXT_PRIMARY,
                    wraplength=500,
                    justify="left",
                    anchor="w",
                ).pack(fill="x", padx=14, pady=(2, 10))

        # Close Button at bottom
        close_btn = ctk.CTkButton(
            main_frame,
            text=t("btn_close", "Fechar"),
            font=theme.get_font(theme.FONT_BODY_BOLD),
            fg_color=theme.COLOR_BORDER,
            hover_color=theme.COLOR_SURFACE_SECONDARY,
            height=36,
            corner_radius=theme.RADIUS_MD,
            command=self.destroy,
        )
        close_btn.pack(side="bottom", fill="x", pady=(10, 4))

    def _play_audio(self):
        if not self.term or not self.term.hear_it:
            return
        # If multiple notes, play sequentially as arpeggio or chord
        for i, pitch in enumerate(self.term.hear_it):
            self.after(i * 300, lambda p=pitch: self.audio_player.play_note(Note(p), duration=0.65))


def show_glossary_term_modal(master, term_id: str):
    """Utility function to launch the modal for any given term ID."""
    return GlossaryTermModal(master, term_id)
