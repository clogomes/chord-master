"""User Profile management modal dialog for creating, switching, and managing student profiles."""
from typing import Callable, Optional
import customtkinter as ctk
from core.user_manager import UserManager, AVATAR_CHOICES, LESSON_IDS


class UserManagementModal(ctk.CTkToplevel):
    """Modal dialog allowing users to switch profiles, create new student accounts, and pick avatars."""

    def __init__(
        self,
        master,
        user_manager: UserManager,
        on_user_changed: Callable[[], None],
        **kwargs,
    ):
        super().__init__(master, **kwargs)
        self.user_manager = user_manager
        self.on_user_changed = on_user_changed

        self.title("Gestão de Perfis de Utilizador")
        self.geometry("520x600")
        self.minsize(480, 520)
        self.configure(fg_color=("#F8FAFC", "#0F172A"))

        # Make modal
        self.transient(master)
        self.grab_set()

        self.selected_avatar = AVATAR_CHOICES[0]
        self._build_ui()

    def _build_ui(self):
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(20, 10))

        ctk.CTkLabel(
            header,
            text="👥 Perfis de Utilizador",
            font=ctk.CTkFont(family="Helvetica", size=22, weight="bold"),
            text_color=("#0F172A", "#F8FAFC"),
        ).pack(anchor="w")

        ctk.CTkLabel(
            header,
            text="Escolhe o teu perfil ou cria um novo para guardar o teu progresso nas lições.",
            font=ctk.CTkFont(family="Helvetica", size=12),
            text_color=("#64748B", "#94A3B8"),
            wraplength=460,
        ).pack(anchor="w", pady=(2, 0))

        # Main scrollable list of profiles
        self.list_container = ctk.CTkScrollableFrame(
            self,
            height=220,
            fg_color=("#F1F5F9", "#1E293B"),
            corner_radius=10,
        )
        self.list_container.pack(fill="x", padx=20, pady=10)

        self._render_profile_list()

        # Create New Profile Section
        create_frame = ctk.CTkFrame(
            self,
            fg_color=("#F1F5F9", "#1E293B"),
            corner_radius=12,
            border_width=1,
            border_color=("#E2E8F0", "#334155"),
        )
        create_frame.pack(fill="both", expand=True, padx=20, pady=(4, 20))

        ctk.CTkLabel(
            create_frame,
            text="➕ Criar Novo Perfil",
            font=ctk.CTkFont(family="Helvetica", size=14, weight="bold"),
            text_color=("#0F172A", "#F8FAFC"),
        ).pack(anchor="w", padx=16, pady=(12, 6))

        # Name input row
        input_row = ctk.CTkFrame(create_frame, fg_color="transparent")
        input_row.pack(fill="x", padx=16, pady=4)

        ctk.CTkLabel(
            input_row,
            text="Nome:",
            font=ctk.CTkFont(family="Helvetica", size=12, weight="bold"),
        ).pack(side="left", padx=(0, 8))

        self.name_entry = ctk.CTkEntry(
            input_row,
            placeholder_text="Ex: Carlos, Maria, João...",
            height=34,
            font=ctk.CTkFont(family="Helvetica", size=13),
        )
        self.name_entry.pack(side="left", expand=True, fill="x")

        # Avatar picker row
        avatar_lbl = ctk.CTkLabel(
            create_frame,
            text="Escolhe o teu Avatar:",
            font=ctk.CTkFont(family="Helvetica", size=12, weight="bold"),
        )
        avatar_lbl.pack(anchor="w", padx=16, pady=(8, 4))

        avatar_row = ctk.CTkFrame(create_frame, fg_color="transparent")
        avatar_row.pack(fill="x", padx=16, pady=(0, 10))

        self.avatar_buttons = []
        for av in AVATAR_CHOICES:
            btn = ctk.CTkButton(
                avatar_row,
                text=av,
                font=ctk.CTkFont(size=18),
                width=34,
                height=34,
                corner_radius=6,
                fg_color="#2563EB" if av == self.selected_avatar else "#334155",
                hover_color="#1D4ED8",
                command=lambda a=av: self._select_avatar(a),
            )
            btn.pack(side="left", padx=2)
            self.avatar_buttons.append((av, btn))

        # Create button
        create_btn = ctk.CTkButton(
            create_frame,
            text="Criar & Ativar Perfil",
            font=ctk.CTkFont(family="Helvetica", size=13, weight="bold"),
            fg_color="#059669",
            hover_color="#047857",
            height=36,
            command=self._handle_create_user,
        )
        create_btn.pack(fill="x", padx=16, pady=(4, 14))

    def _render_profile_list(self):
        for child in self.list_container.winfo_children():
            child.destroy()

        users = self.user_manager.get_all_users()
        active_name = self.user_manager.active_username

        for profile in users:
            is_active = profile.username == active_name
            row = ctk.CTkFrame(
                self.list_container,
                corner_radius=8,
                fg_color="#2563EB" if is_active else ("#FFFFFF", "#0F172A"),
                border_width=1 if is_active else 0,
                border_color="#60A5FA",
            )
            row.pack(fill="x", padx=6, pady=4)

            # Avatar + Name
            av_lbl = ctk.CTkLabel(row, text=profile.avatar, font=ctk.CTkFont(size=20))
            av_lbl.pack(side="left", padx=(10, 6), pady=8)

            info_box = ctk.CTkFrame(row, fg_color="transparent")
            info_box.pack(side="left", expand=True, fill="x", padx=4)

            name_color = "#FFFFFF" if is_active else ("#0F172A", "#F8FAFC")
            ctk.CTkLabel(
                info_box,
                text=profile.username + (" (Ativo)" if is_active else ""),
                font=ctk.CTkFont(family="Helvetica", size=13, weight="bold"),
                text_color=name_color,
            ).pack(anchor="w")

            detail_text = f"Lições: {len(profile.completed_lessons)}/4 • Precisão: {profile.accuracy_rate:.0f}% ({profile.total_attempts} ex.)"
            sub_color = "#DBEAFE" if is_active else ("#64748B", "#94A3B8")
            ctk.CTkLabel(
                info_box,
                text=detail_text,
                font=ctk.CTkFont(family="Helvetica", size=11),
                text_color=sub_color,
            ).pack(anchor="w")

            # Actions
            if not is_active:
                select_btn = ctk.CTkButton(
                    row,
                    text="Selecionar",
                    font=ctk.CTkFont(family="Helvetica", size=12, weight="bold"),
                    width=85,
                    height=28,
                    fg_color="#2563EB",
                    hover_color="#1D4ED8",
                    command=lambda u=profile.username: self._handle_switch_user(u),
                )
                select_btn.pack(side="right", padx=6)

                if len(users) > 1:
                    del_btn = ctk.CTkButton(
                        row,
                        text="✕",
                        font=ctk.CTkFont(size=12, weight="bold"),
                        width=28,
                        height=28,
                        fg_color="#DC2626",
                        hover_color="#B91C1C",
                        command=lambda u=profile.username: self._handle_delete_user(u),
                    )
                    del_btn.pack(side="right", padx=(0, 4))
            else:
                badge = ctk.CTkLabel(
                    row,
                    text="✓ EM USO",
                    font=ctk.CTkFont(family="Helvetica", size=11, weight="bold"),
                    text_color="#FFFFFF",
                )
                badge.pack(side="right", padx=12)

    def _select_avatar(self, avatar: str):
        self.selected_avatar = avatar
        for av, btn in self.avatar_buttons:
            if av == avatar:
                btn.configure(fg_color="#2563EB")
            else:
                btn.configure(fg_color="#334155")

    def _handle_create_user(self):
        name = self.name_entry.get().strip()
        if not name:
            name = f"Utilizador {len(self.user_manager.get_all_users()) + 1}"

        self.user_manager.create_user(name, avatar=self.selected_avatar)
        self.name_entry.delete(0, "end")
        self._render_profile_list()
        self.on_user_changed()

    def _handle_switch_user(self, username: str):
        self.user_manager.switch_user(username)
        self._render_profile_list()
        self.on_user_changed()

    def _handle_delete_user(self, username: str):
        self.user_manager.delete_user(username)
        self._render_profile_list()
        self.on_user_changed()
