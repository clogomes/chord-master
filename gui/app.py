"""Main CustomTkinter application window, multi-user manager, and screen router."""
import tkinter as tk
from typing import Dict, Optional
import customtkinter as ctk
from core.user_manager import UserManager
from audio.player import get_audio_player
from gui.components.user_modal import UserManagementModal
from gui.screens.main_menu import MainMenuScreen
from gui.screens.theory_screen import TheoryScreen
from gui.screens.practice_ear import PracticeEarScreen
from gui.screens.practice_staff import PracticeStaffScreen
from gui.screens.stats_screen import StatsScreen

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
        self.geometry("1120x760")
        self.minsize(980, 650)
        self.configure(fg_color=("#F8FAFC", "#0F172A"))

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
            width=240,
            corner_radius=0,
            fg_color=("#F1F5F9", "#0F172A"),
        )
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(8, weight=1)

        # App Logo & Branding
        logo_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        logo_frame.grid(row=0, column=0, padx=16, pady=(20, 10), sticky="w")

        ctk.CTkLabel(
            logo_frame,
            text="🎵 ChordMaster",
            font=ctk.CTkFont(family="Helvetica", size=20, weight="bold"),
            text_color=("#0F172A", "#F8FAFC"),
        ).pack(anchor="w")

        ctk.CTkLabel(
            logo_frame,
            text="Teoria & Prática Musical",
            font=ctk.CTkFont(family="Helvetica", size=12),
            text_color=("#64748B", "#94A3B8"),
        ).pack(anchor="w")

        # Active User Profile Card
        self.profile_card = ctk.CTkFrame(
            self.sidebar_frame,
            corner_radius=10,
            fg_color=("#E2E8F0", "#1E293B"),
            border_width=1,
            border_color=("#CBD5E1", "#334155"),
        )
        self.profile_card.grid(row=1, column=0, padx=14, pady=(4, 14), sticky="ew")
        self._update_profile_card()

        # Navigation Buttons
        nav_items = [
            ("main_menu", "🏠 Menu Principal"),
            ("theory", "📖 Teoria Musical"),
            ("practice_ear", "🎧 Treino Auditivo"),
            ("practice_staff", "🎼 Leitura de Pauta"),
            ("stats", "📊 Estatísticas"),
        ]

        for i, (key, label) in enumerate(nav_items, start=2):
            btn = ctk.CTkButton(
                self.sidebar_frame,
                text=label,
                font=ctk.CTkFont(family="Helvetica", size=13, weight="bold"),
                anchor="w",
                height=38,
                corner_radius=8,
                fg_color="transparent",
                text_color=("#334155", "#CBD5E1"),
                hover_color=("#E2E8F0", "#1E293B"),
                command=lambda k=key: self.navigate_to(k),
            )
            btn.grid(row=i, column=0, padx=14, pady=3, sticky="ew")
            self.nav_buttons[key] = btn

        # Theme Selector at bottom
        bottom_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        bottom_frame.grid(row=9, column=0, padx=14, pady=18, sticky="ew")

        ctk.CTkLabel(
            bottom_frame,
            text="Tema Visual:",
            font=ctk.CTkFont(family="Helvetica", size=11, weight="bold"),
            text_color=("#64748B", "#94A3B8"),
        ).pack(anchor="w", pady=(0, 4))

        self.theme_option = ctk.CTkOptionMenu(
            bottom_frame,
            values=["Dark", "Light", "System"],
            command=self._change_theme,
            height=30,
            fg_color="#334155",
            button_color="#475569",
        )
        self.theme_option.set("Dark")
        self.theme_option.pack(fill="x")

        # 2. Main Content Area
        self.content_area = ctk.CTkFrame(self, corner_radius=0, fg_color=("#F8FAFC", "#0F172A"))
        self.content_area.grid(row=0, column=1, sticky="nsew")

    def _update_profile_card(self):
        for child in self.profile_card.winfo_children():
            child.destroy()

        user = self.user_manager.current_user

        top_row = ctk.CTkFrame(self.profile_card, fg_color="transparent")
        top_row.pack(fill="x", padx=10, pady=(8, 2))

        av_lbl = ctk.CTkLabel(top_row, text=user.avatar, font=ctk.CTkFont(size=20))
        av_lbl.pack(side="left", padx=(0, 6))

        user_info = ctk.CTkFrame(top_row, fg_color="transparent")
        user_info.pack(side="left", fill="x", expand=True)

        ctk.CTkLabel(
            user_info,
            text=user.username,
            font=ctk.CTkFont(family="Helvetica", size=13, weight="bold"),
            text_color=("#0F172A", "#F8FAFC"),
        ).pack(anchor="w")

        prog_text = f"Lições: {len(user.completed_lessons)}/4 ({user.lessons_progress_percent:.0f}%)"
        ctk.CTkLabel(
            user_info,
            text=prog_text,
            font=ctk.CTkFont(family="Helvetica", size=10),
            text_color=("#64748B", "#94A3B8"),
        ).pack(anchor="w")

        # Progress bar
        pbar = ctk.CTkProgressBar(self.profile_card, height=5, progress_color="#10B981")
        pbar.set(user.lessons_progress_percent / 100.0)
        pbar.pack(fill="x", padx=10, pady=(2, 6))

        # Switch / manage profile button
        switch_btn = ctk.CTkButton(
            self.profile_card,
            text="Trocar Perfil 👥",
            font=ctk.CTkFont(family="Helvetica", size=11, weight="bold"),
            height=24,
            fg_color="#334155",
            hover_color="#475569",
            command=self._open_user_modal,
        )
        switch_btn.pack(fill="x", padx=10, pady=(0, 8))

    def _open_user_modal(self):
        UserManagementModal(self, user_manager=self.user_manager, on_user_changed=self._on_user_changed)

    def _on_user_changed(self):
        self._update_profile_card()
        # Refresh current screen
        if self.current_screen_name:
            self.navigate_to(self.current_screen_name)

    def navigate_to(self, screen_name: str):
        """Switches the active screen view in the content area."""
        if not self.winfo_exists():
            return

        self.audio_player.stop_all()
        self._update_profile_card()

        # Update sidebar highlight
        for key, btn in self.nav_buttons.items():
            if btn.winfo_exists():
                if key == screen_name:
                    btn.configure(
                        fg_color="#2563EB",
                        text_color="#FFFFFF",
                        hover_color="#1D4ED8",
                    )
                else:
                    btn.configure(
                        fg_color="transparent",
                        text_color=("#334155", "#CBD5E1"),
                        hover_color=("#E2E8F0", "#1E293B"),
                    )

        # Destroy existing screen widget
        if self.current_screen_widget and self.current_screen_widget.winfo_exists():
            self.current_screen_widget.destroy()

        self.current_screen_name = screen_name

        # Instantiate new screen view with user_manager
        if screen_name == "main_menu":
            self.current_screen_widget = MainMenuScreen(
                self.content_area,
                user_manager=self.user_manager,
                on_navigate=self.navigate_to,
                on_open_users=self._open_user_modal,
            )
        elif screen_name == "theory":
            self.current_screen_widget = TheoryScreen(
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
        elif screen_name == "stats":
            self.current_screen_widget = StatsScreen(
                self.content_area,
                user_manager=self.user_manager,
                on_back=lambda: self.navigate_to("main_menu"),
            )

        self.current_screen_widget.pack(fill="both", expand=True)

    def _change_theme(self, new_theme: str):
        ctk.set_appearance_mode(new_theme)

    def _on_close(self):
        self.audio_player.stop_all()
        self.user_manager.save()
        self.destroy()
