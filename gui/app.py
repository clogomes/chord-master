"""Main CustomTkinter application window, multi-user manager, and screen router."""
import tkinter as tk
from tkinter import messagebox
from typing import Dict, Optional
import customtkinter as ctk
from core.user_manager import UserManager, LESSON_IDS
from audio.player import get_audio_player
from gui import theme
from gui.i18n import t, get_language, set_language
from gui.components.user_modal import UserManagementModal
from gui.screens.main_menu import MainMenuScreen
from gui.screens.theory_screen import TheoryScreen
from gui.screens.practice_ear import PracticeEarScreen
from gui.screens.practice_staff import PracticeStaffScreen
from gui.screens.practice_song import PracticeSongScreen
from gui.screens.practice_scales import PracticeScalesScreen
from gui.screens.practice_instrument import PracticeInstrumentScreen
from gui.screens.practice_technique import PracticeTechniqueScreen
from gui.screens.tuner_screen import LamireScreen
from gui.screens.stats_screen import StatsScreen
from gui.screens.glossary_screen import GlossaryScreen

# Appearance configuration
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class ChordMasterApp(ctk.CTk):
    """
    Main application shell managing global state, navigation sidebar,
    multi-user student profiles, themes, and screen transitions.
    """

    def __init__(self):
        super().__init__()

        # Window settings & background
        self.title("ChordMaster — Teoria Musical & Prática Interativa")
        self.geometry("1160x780")
        self.minsize(1000, 680)
        self.configure(fg_color=theme.COLOR_BG)

        # Core state
        self.user_manager = UserManager()
        self.audio_player = get_audio_player()

        # Navigation state
        self.current_screen_name: Optional[str] = None
        self.current_screen_widget: Optional[ctk.CTkFrame] = None
        self.nav_buttons: Dict[str, ctk.CTkButton] = {}

        self._build_layout()
        self.navigate_to("main_menu")

        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_layout(self):
        # Master grid layout: 1 row, 2 columns (Sidebar + Content)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # 1. Left Sidebar
        self.sidebar_frame = ctk.CTkFrame(
            self,
            width=260,
            corner_radius=0,
            fg_color=theme.COLOR_SURFACE,
            border_width=0,
        )
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(10, weight=1)

        # App Logo & Branding
        logo_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        logo_frame.grid(row=0, column=0, padx=18, pady=(22, 12), sticky="w")

        ctk.CTkLabel(
            logo_frame,
            text="🎵 ChordMaster",
            font=ctk.CTkFont(family=theme.FONT_FAMILY, size=22, weight="bold"),
            text_color=theme.COLOR_TEXT_PRIMARY,
        ).pack(anchor="w")

        ctk.CTkLabel(
            logo_frame,
            text="Estúdio & Academia Musical",
            font=theme.get_font(theme.FONT_SMALL),
            text_color=theme.COLOR_TEXT_MUTED,
        ).pack(anchor="w")

        # Active User Profile Card
        self.profile_card = ctk.CTkFrame(
            self.sidebar_frame,
            corner_radius=theme.RADIUS_MD,
            fg_color=theme.COLOR_SURFACE_SECONDARY,
            border_width=1,
            border_color=theme.COLOR_BORDER,
        )
        self.profile_card.grid(row=1, column=0, padx=14, pady=(4, 14), sticky="ew")
        self._update_profile_card()

        # Navigation Buttons
        self._build_nav_buttons()

        # Reset Progress, Theme & Language Controls at bottom
        bottom_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        bottom_frame.grid(row=11, column=0, padx=14, pady=(10, 16), sticky="ew")

        # Language Selector
        self.lang_lbl = ctk.CTkLabel(
            bottom_frame,
            text=t("language_label", "Idioma / Language:"),
            font=theme.get_font(theme.FONT_SMALL_BOLD),
            text_color=theme.COLOR_TEXT_MUTED,
        )
        self.lang_lbl.pack(anchor="w", pady=(0, 2))

        self.lang_option = ctk.CTkSegmentedButton(
            bottom_frame,
            values=["🇵🇹 PT", "🇬🇧 EN"],
            command=self._change_language,
            height=30,
            font=theme.get_font(theme.FONT_SMALL_BOLD),
            selected_color=theme.COLOR_PRIMARY,
            selected_hover_color=theme.COLOR_PRIMARY_HOVER,
        )
        self.lang_option.set("🇵🇹 PT" if get_language() == "pt" else "🇬🇧 EN")
        self.lang_option.pack(fill="x", pady=(0, 8))

        # Reset Progress Button
        self.reset_btn = ctk.CTkButton(
            bottom_frame,
            text=t("reset_progress", "↺ Reiniciar Progresso"),
            font=theme.get_font(theme.FONT_SMALL_BOLD),
            fg_color="transparent",
            text_color=theme.COLOR_ACCENT_CRIMSON,
            hover_color=theme.COLOR_CRIMSON_BG,
            height=30,
            corner_radius=theme.RADIUS_SM,
            command=self.confirm_reset_user_progress,
        )
        self.reset_btn.pack(fill="x", pady=(0, 8))

        self.theme_lbl = ctk.CTkLabel(
            bottom_frame,
            text=t("theme_label", "Tema Visual:"),
            font=theme.get_font(theme.FONT_SMALL_BOLD),
            text_color=theme.COLOR_TEXT_MUTED,
        )
        self.theme_lbl.pack(anchor="w", pady=(0, 4))

        self.theme_option = ctk.CTkOptionMenu(
            bottom_frame,
            values=["Dark", "Light", "System"],
            command=self._change_theme,
            height=32,
            corner_radius=theme.RADIUS_SM,
            font=theme.get_font(theme.FONT_SMALL),
            fg_color="#334155",
            button_color="#475569",
        )
        self.theme_option.set("Dark")
        self.theme_option.pack(fill="x")

        # 2. Right Content Area
        self.content_area = ctk.CTkFrame(
            self,
            corner_radius=0,
            fg_color=theme.COLOR_BG,
        )
        self.content_area.grid(row=0, column=1, sticky="nsew")

    def _update_profile_card(self):
        for widget in self.profile_card.winfo_children():
            widget.destroy()

        user = self.user_manager.current_user

        top_row = ctk.CTkFrame(self.profile_card, fg_color="transparent")
        top_row.pack(fill="x", padx=12, pady=(10, 2))

        avatar_lbl = ctk.CTkLabel(
            top_row,
            text=user.avatar,
            font=ctk.CTkFont(size=24),
        )
        avatar_lbl.pack(side="left")

        name_box = ctk.CTkFrame(top_row, fg_color="transparent")
        name_box.pack(side="left", padx=8)

        name_lbl = ctk.CTkLabel(
            name_box,
            text=user.username,
            font=theme.get_font(theme.FONT_BODY_BOLD),
            text_color=theme.COLOR_TEXT_PRIMARY,
        )
        name_lbl.pack(anchor="w")

        lessons_count = len(user.completed_lessons)
        stats_lbl = ctk.CTkLabel(
            name_box,
            text=f"{lessons_count}/{len(LESSON_IDS)} lições • {user.accuracy_rate:.0f}% acertos",
            font=theme.get_font(theme.FONT_SMALL),
            text_color=theme.COLOR_TEXT_MUTED,
        )
        stats_lbl.pack(anchor="w")

        switch_btn = ctk.CTkButton(
            self.profile_card,
            text="👥 Gerir Alunos / Perfis",
            font=theme.get_font(theme.FONT_SMALL_BOLD),
            height=28,
            corner_radius=theme.RADIUS_SM,
            fg_color=theme.COLOR_PRIMARY,
            hover_color=theme.COLOR_PRIMARY_HOVER,
            command=self._open_user_modal,
        )
        switch_btn.pack(fill="x", padx=12, pady=(6, 10))

    def _build_nav_buttons(self):
        nav_items = [
            ("main_menu", t("nav_main_menu", "🏠 Menu Principal")),
            ("theory", t("nav_theory", f"📖 Teoria Musical ({len(LESSON_IDS)} Cap)")),
            ("practice_song", t("nav_practice_song", "🎶 Tocar Repertório")),
            ("practice_scales", t("nav_practice_scales", "🎼 Prática de Escalas")),
            ("lamire", t("nav_lamire", "🎙️ Lamiré & Afinador")),
            ("practice_instrument", t("nav_practice_instrument", "🎯 Prática c/ Microfone")),
            ("practice_ear", t("nav_practice_ear", "🎧 Treino Auditivo")),
            ("practice_staff", t("nav_practice_staff", "🎼 Leitura de Pauta")),
            ("glossary", t("nav_glossary", "📚 Glossário Musical")),
            ("stats", t("nav_stats", "📊 Estatísticas & Alunos")),
        ]

        for i, (key, label) in enumerate(nav_items, start=2):
            if key in self.nav_buttons:
                self.nav_buttons[key].configure(text=label)
            else:
                btn = ctk.CTkButton(
                    self.sidebar_frame,
                    text=label,
                    font=theme.get_font(theme.FONT_BODY_BOLD),
                    anchor="w",
                    height=40,
                    corner_radius=theme.RADIUS_MD,
                    fg_color="transparent",
                    text_color=theme.COLOR_TEXT_MUTED,
                    hover_color=theme.COLOR_SURFACE_HOVER,
                    command=lambda k=key: self.navigate_to(k),
                )
                btn.grid(row=i, column=0, padx=14, pady=2, sticky="ew")
                self.nav_buttons[key] = btn

    def _change_language(self, val: str):
        lang = "pt" if "PT" in val else "en"
        set_language(lang)
        self._refresh_ui_language()

    def _refresh_ui_language(self):
        # Update sidebar labels and buttons
        self._build_nav_buttons()
        self.lang_lbl.configure(text=t("language_label", "Idioma / Language:"))
        self.theme_lbl.configure(text=t("theme_label", "Tema Visual:"))
        self.reset_btn.configure(text=t("reset_progress", "↺ Reiniciar Progresso"))
        self._update_profile_card()

        # Re-navigate to refresh current screen content in new language
        if self.current_screen_name:
            self.navigate_to(self.current_screen_name)

    def _open_user_modal(self):
        modal = UserManagementModal(
            self,
            user_manager=self.user_manager,
            on_user_switched=self._on_user_switched,
        )
        modal.grab_set()

    def _on_user_switched(self, username: str):
        self._update_profile_card()
        # Refresh current screen
        if self.current_screen_name:
            self.navigate_to(self.current_screen_name)

    def confirm_reset_user_progress(self):
        """Displays confirmation dialog before resetting learning progress for active user."""
        user = self.user_manager.current_user
        confirm = messagebox.askyesno(
            "Reiniciar Aprendizagem",
            f"Tens a certeza que desejas reiniciar todo o progresso do aluno «{user.username}»?\n\n"
            "Isto irá limpar as lições concluídas, estatísticas de exercícios e histórico para recomeçar do zero.",
        )
        if confirm:
            self.user_manager.reset_current_user_scores()
            self._update_profile_card()
            if self.current_screen_name:
                self.navigate_to(self.current_screen_name)
            messagebox.showinfo("Progresso Reiniciado", f"O progresso de {user.username} foi reiniciado com sucesso!")

    def navigate_to(self, screen_name: str):
        """Switches the active view in the content area."""
        self.audio_player.stop_all()

        # Update button highlights
        for key, btn in self.nav_buttons.items():
            if key == screen_name:
                btn.configure(
                    fg_color=theme.COLOR_PRIMARY,
                    text_color="#FFFFFF",
                    hover_color=theme.COLOR_PRIMARY_HOVER,
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    text_color=theme.COLOR_TEXT_MUTED,
                    hover_color=theme.COLOR_SURFACE_HOVER,
                )

        # Destroy existing screen widget
        if self.current_screen_widget is not None:
            self.current_screen_widget.destroy()
            self.current_screen_widget = None

        self.current_screen_name = screen_name

        # Create target screen
        if screen_name == "main_menu":
            self.current_screen_widget = MainMenuScreen(
                self.content_area,
                user_manager=self.user_manager,
                on_navigate=self.navigate_to,
                on_switch_user=self._open_user_modal,
            )
        elif screen_name == "theory":
            self.current_screen_widget = TheoryScreen(
                self.content_area,
                user_manager=self.user_manager,
                on_back=lambda: self.navigate_to("main_menu"),
                on_user_updated=self._update_profile_card,
            )
        elif screen_name == "practice_song":
            self.current_screen_widget = PracticeSongScreen(
                self.content_area,
                user_manager=self.user_manager,
                on_back=lambda: self.navigate_to("main_menu"),
            )
        elif screen_name == "practice_scales":
            self.current_screen_widget = PracticeScalesScreen(
                self.content_area,
                user_manager=self.user_manager,
                on_back=lambda: self.navigate_to("main_menu"),
            )
        elif screen_name == "lamire":
            self.current_screen_widget = LamireScreen(
                self.content_area,
                on_back=lambda: self.navigate_to("main_menu"),
            )
        elif screen_name == "practice_instrument":
            self.current_screen_widget = PracticeInstrumentScreen(
                self.content_area,
                user_manager=self.user_manager,
                on_back=lambda: self.navigate_to("main_menu"),
            )
        elif screen_name == "practice_technique":
            self.current_screen_widget = PracticeTechniqueScreen(
                self.content_area,
                user_manager=self.user_manager,
                on_back=lambda: self.navigate_to("main_menu"),
            )
        elif screen_name == "practice_ear":
            self.current_screen_widget = PracticeEarScreen(
                self.content_area,
                user_manager=self.user_manager,
                on_back=lambda: self.navigate_to("main_menu"),
            )
        elif screen_name == "practice_staff":
            self.current_screen_widget = PracticeStaffScreen(
                self.content_area,
                user_manager=self.user_manager,
                on_back=lambda: self.navigate_to("main_menu"),
            )
        elif screen_name == "glossary":
            self.current_screen_widget = GlossaryScreen(
                self.content_area,
                user_manager=self.user_manager,
                on_back=lambda: self.navigate_to("main_menu"),
                on_navigate_chapter=self._navigate_to_theory_chapter,
            )
        elif screen_name == "stats":
            self.current_screen_widget = StatsScreen(
                self.content_area,
                user_manager=self.user_manager,
                on_back=lambda: self.navigate_to("main_menu"),
                on_user_switched=self._on_user_switched,
            )
        else:
            print(f"Aviso: Rota desconhecida '{screen_name}', redirecionando para main_menu")
            self.current_screen_widget = MainMenuScreen(
                self.content_area,
                user_manager=self.user_manager,
                on_navigate=self.navigate_to,
                on_switch_user=self._open_user_modal,
            )
            self.current_screen_name = "main_menu"

        if self.current_screen_widget is not None:
            self.current_screen_widget.pack(fill="both", expand=True)

    def _navigate_to_theory_chapter(self, chapter_id: str):
        """Switches to the theory screen and selects the requested chapter."""
        self.navigate_to("theory")
        if self.current_screen_widget and hasattr(self.current_screen_widget, "load_chapter_by_id"):
            self.current_screen_widget.load_chapter_by_id(chapter_id)

    def _change_theme(self, choice: str):
        ctk.set_appearance_mode(choice)

    def _on_close(self):
        self.audio_player.stop_all()
        self.destroy()


def run_app():
    app = ChordMasterApp()
    app.mainloop()


if __name__ == "__main__":
    run_app()
