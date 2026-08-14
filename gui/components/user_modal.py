"""User Profile management modal dialog for creating, switching, and managing student profiles."""
from tkinter import messagebox
from typing import Callable, Optional
import customtkinter as ctk
from core.user_manager import UserManager, AVATAR_CHOICES, LESSON_IDS
from gui import theme


class UserManagementModal(ctk.CTkToplevel):
    """Modal dialog allowing users to switch profiles, create new student accounts, and pick avatars."""

    def __init__(
        self,
        master,
        user_manager: UserManager,
        on_user_changed: Optional[Callable[[], None]] = None,
        on_user_switched: Optional[Callable[[str], None]] = None,
        **kwargs,
    ):
        super().__init__(master, **kwargs)
        self.user_manager = user_manager
        self.on_user_changed = on_user_changed
        self.on_user_switched = on_user_switched

        self.title("Gestão de Perfis de Alunos")
        self.geometry("560x640")
        self.minsize(500, 560)
        self.configure(fg_color=theme.COLOR_BG)

        # Make modal
        self.transient(master)
        self.grab_set()

        self.selected_avatar = AVATAR_CHOICES[0]
        self._build_ui()

    def _notify_change(self, username: Optional[str] = None):
        active = username or self.user_manager.active_username
        if self.on_user_switched:
            self.on_user_switched(active)
        if self.on_user_changed:
            self.on_user_changed()

    def _build_ui(self):
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=24, pady=(20, 10))

        ctk.CTkLabel(
            header,
            text="👥 Perfis de Alunos & Utilizadores",
            font=theme.get_font(theme.FONT_TITLE),
            text_color=theme.COLOR_TEXT_PRIMARY,
        ).pack(anchor="w")

        ctk.CTkLabel(
            header,
            text="Escolhe o teu perfil ou cria um novo para guardar o teu progresso nas lições e exercícios.",
            font=theme.get_font(theme.FONT_BODY),
            text_color=theme.COLOR_TEXT_MUTED,
            wraplength=480,
            justify="left",
        ).pack(anchor="w", pady=(2, 0))

        # Main scrollable list of profiles
        self.list_container = ctk.CTkScrollableFrame(
            self,
            height=230,
            fg_color=theme.COLOR_SURFACE,
            corner_radius=theme.RADIUS_LG,
            border_width=1,
            border_color=theme.COLOR_BORDER,
        )
        self.list_container.pack(fill="x", padx=24, pady=10)

        self._render_profile_list()

        # Create New Profile Section
        create_frame = ctk.CTkFrame(
            self,
            fg_color=theme.COLOR_SURFACE,
            corner_radius=theme.RADIUS_LG,
            border_width=1,
            border_color=theme.COLOR_BORDER,
        )
        create_frame.pack(fill="both", expand=True, padx=24, pady=(4, 20))

        ctk.CTkLabel(
            create_frame,
            text="➕ Criar Novo Aluno",
            font=theme.get_font(theme.FONT_SECTION),
            text_color=theme.COLOR_TEXT_PRIMARY,
        ).pack(anchor="w", padx=18, pady=(14, 6))

        # Name input row
        input_row = ctk.CTkFrame(create_frame, fg_color="transparent")
        input_row.pack(fill="x", padx=18, pady=4)

        ctk.CTkLabel(
            input_row,
            text="Nome:",
            font=theme.get_font(theme.FONT_BODY_BOLD),
            text_color=theme.COLOR_TEXT_PRIMARY,
        ).pack(side="left", padx=(0, 10))

        self.name_entry = ctk.CTkEntry(
            input_row,
            placeholder_text="Ex: Maria, Carlos, Beatriz...",
            height=36,
            font=theme.get_font(theme.FONT_BODY),
        )
        self.name_entry.pack(side="left", expand=True, fill="x")

        # Avatar picker row
        ctk.CTkLabel(
            create_frame,
            text="Escolhe o Avatar do Aluno:",
            font=theme.get_font(theme.FONT_BODY_BOLD),
            text_color=theme.COLOR_TEXT_PRIMARY,
        ).pack(anchor="w", padx=18, pady=(10, 4))

        avatar_row = ctk.CTkFrame(create_frame, fg_color="transparent")
        avatar_row.pack(fill="x", padx=18, pady=(0, 12))

        self.avatar_buttons = []
        for av in AVATAR_CHOICES:
            btn = ctk.CTkButton(
                avatar_row,
                text=av,
                font=ctk.CTkFont(size=20),
                width=38,
                height=38,
                corner_radius=theme.RADIUS_SM,
                fg_color=theme.COLOR_PRIMARY if av == self.selected_avatar else theme.COLOR_SURFACE_SECONDARY,
                hover_color=theme.COLOR_PRIMARY_HOVER,
                command=lambda a=av: self._select_avatar(a),
            )
            btn.pack(side="left", padx=3)
            self.avatar_buttons.append((av, btn))

        # Create button
        create_btn = ctk.CTkButton(
            create_frame,
            text="Criar & Ativar Perfil",
            font=theme.get_font(theme.FONT_BODY_BOLD),
            fg_color=theme.COLOR_SUCCESS,
            hover_color=theme.COLOR_SUCCESS_HOVER,
            corner_radius=theme.RADIUS_MD,
            height=38,
            command=self._handle_create_user,
        )
        create_btn.pack(fill="x", padx=18, pady=(4, 16))

    def _render_profile_list(self):
        for child in self.list_container.winfo_children():
            child.destroy()

        users = self.user_manager.get_all_users()
        active_name = self.user_manager.active_username

        for profile in users:
            is_active = profile.username == active_name
            row = ctk.CTkFrame(
                self.list_container,
                corner_radius=theme.RADIUS_MD,
                fg_color=theme.COLOR_PRIMARY if is_active else theme.COLOR_SURFACE_SECONDARY,
                border_width=1 if is_active else 0,
                border_color=theme.COLOR_PRIMARY,
            )
            row.pack(fill="x", padx=6, pady=4)

            # Avatar + Name
            av_lbl = ctk.CTkLabel(row, text=profile.avatar, font=ctk.CTkFont(size=22))
            av_lbl.pack(side="left", padx=(12, 8), pady=8)

            info_box = ctk.CTkFrame(row, fg_color="transparent")
            info_box.pack(side="left", expand=True, fill="x", padx=4)

            name_color = "#FFFFFF" if is_active else theme.COLOR_TEXT_PRIMARY
            ctk.CTkLabel(
                info_box,
                text=profile.username + (" (Ativo)" if is_active else ""),
                font=theme.get_font(theme.FONT_BODY_BOLD),
                text_color=name_color,
            ).pack(anchor="w")

            detail_text = f"Lições: {len(profile.completed_lessons)}/8 • Precisão: {profile.accuracy_rate:.0f}% ({profile.total_attempts} ex.)"
            sub_color = "#DBEAFE" if is_active else theme.COLOR_TEXT_MUTED
            ctk.CTkLabel(
                info_box,
                text=detail_text,
                font=theme.get_font(theme.FONT_SMALL),
                text_color=sub_color,
            ).pack(anchor="w")

            # Actions
            if not is_active:
                select_btn = ctk.CTkButton(
                    row,
                    text="Selecionar",
                    font=theme.get_font(theme.FONT_SMALL_BOLD),
                    width=90,
                    height=30,
                    corner_radius=theme.RADIUS_SM,
                    fg_color=theme.COLOR_PRIMARY,
                    hover_color=theme.COLOR_PRIMARY_HOVER,
                    command=lambda u=profile.username: self._handle_switch_user(u),
                )
                select_btn.pack(side="right", padx=6)

                if len(users) > 1:
                    del_btn = ctk.CTkButton(
                        row,
                        text="✕",
                        font=ctk.CTkFont(size=12, weight="bold"),
                        width=30,
                        height=30,
                        corner_radius=theme.RADIUS_SM,
                        fg_color=theme.COLOR_ACCENT_CRIMSON,
                        hover_color=theme.COLOR_ACCENT_CRIMSON_HOVER,
                        command=lambda u=profile.username: self._handle_delete_user(u),
                    )
                    del_btn.pack(side="right", padx=(0, 6))
            else:
                badge = ctk.CTkLabel(
                    row,
                    text="✓ EM USO",
                    font=theme.get_font(theme.FONT_BADGE),
                    text_color="#FFFFFF",
                )
                badge.pack(side="right", padx=14)

    def _select_avatar(self, avatar: str):
        self.selected_avatar = avatar
        for av, btn in self.avatar_buttons:
            if av == avatar:
                btn.configure(fg_color=theme.COLOR_PRIMARY)
            else:
                btn.configure(fg_color=theme.COLOR_SURFACE_SECONDARY)

    def _handle_create_user(self):
        name = self.name_entry.get().strip()
        if not name:
            name = f"Utilizador {len(self.user_manager.get_all_users()) + 1}"

        self.user_manager.create_user(name, avatar=self.selected_avatar)
        self.name_entry.delete(0, "end")
        self._render_profile_list()
        self._notify_change()

    def _handle_switch_user(self, username: str):
        self.user_manager.switch_user(username)
        self._render_profile_list()
        self._notify_change(username)

    def _handle_delete_user(self, username: str):
        confirm = messagebox.askyesno("Remover Perfil", f"Tens a certeza que desejas remover o perfil «{username}»?")
        if confirm:
            self.user_manager.delete_user(username)
            self._render_profile_list()
            self._notify_change()
