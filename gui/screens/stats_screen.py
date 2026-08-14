"""Statistics, progress tracking, user comparison leaderboard, and activity history screen."""
import datetime
from tkinter import messagebox
from typing import Callable, Optional
import customtkinter as ctk
from core.user_manager import UserManager, LESSON_IDS
from gui import theme


class StatsScreen(ctk.CTkFrame):
    """Visual dashboard displaying performance metrics, streaks, completed lessons, and student leaderboard."""

    def __init__(
        self,
        master,
        user_manager: UserManager,
        on_back: Callable[[], None],
        on_user_switched: Optional[Callable[[str], None]] = None,
        **kwargs,
    ):
        super().__init__(master, fg_color=theme.COLOR_BG, **kwargs)
        self.user_manager = user_manager
        self.on_back = on_back
        self.on_user_switched = on_user_switched

        self._build_ui()

    def _build_ui(self):
        user = self.user_manager.current_user

        # Top Navigation Bar
        nav_bar = ctk.CTkFrame(self, fg_color="transparent")
        nav_bar.pack(fill="x", padx=20, pady=(16, 6))

        back_btn = ctk.CTkButton(
            nav_bar,
            text="← Voltar ao Menu",
            font=theme.get_font(theme.FONT_BODY_BOLD),
            fg_color="#475569",
            hover_color="#334155",
            width=140,
            height=38,
            corner_radius=theme.RADIUS_MD,
            command=self.on_back,
        )
        back_btn.pack(side="left")

        title_lbl = ctk.CTkLabel(
            nav_bar,
            text=f"📊 Estatísticas & Alunos — {user.avatar} {user.username}",
            font=theme.get_font(theme.FONT_TITLE),
            text_color=theme.COLOR_TEXT_PRIMARY,
        )
        title_lbl.pack(side="left", padx=16)

        reset_btn = ctk.CTkButton(
            nav_bar,
            text="↺ Reiniciar Meu Progresso",
            font=theme.get_font(theme.FONT_BODY_BOLD),
            fg_color=theme.COLOR_ACCENT_CRIMSON,
            hover_color=theme.COLOR_ACCENT_CRIMSON_HOVER,
            width=180,
            height=38,
            corner_radius=theme.RADIUS_MD,
            command=self._handle_reset,
        )
        reset_btn.pack(side="right")

        # Scrollable Content
        self.container = ctk.CTkScrollableFrame(
            self,
            corner_radius=theme.RADIUS_LG,
            fg_color=theme.COLOR_BG,
            border_width=1,
            border_color=theme.COLOR_BORDER,
        )
        self.container.pack(fill="both", expand=True, padx=20, pady=(4, 16))

        self._render_stats_content()

    def _render_stats_content(self):
        for child in self.container.winfo_children():
            child.destroy()

        user = self.user_manager.current_user

        # 1. Global Overview Cards for Active User
        global_card = ctk.CTkFrame(
            self.container,
            corner_radius=theme.RADIUS_LG,
            fg_color=theme.COLOR_SURFACE,
            border_width=1,
            border_color=theme.COLOR_BORDER,
        )
        global_card.pack(fill="x", pady=(0, 14))

        header_row = ctk.CTkFrame(global_card, fg_color="transparent")
        header_row.pack(fill="x", padx=18, pady=(14, 6))

        ctk.CTkLabel(
            header_row,
            text=f"Desempenho Geral de {user.avatar} {user.username}",
            font=theme.get_font(theme.FONT_SECTION),
            text_color=theme.COLOR_TEXT_PRIMARY,
        ).pack(side="left")

        prog_badge = ctk.CTkLabel(
            header_row,
            text=f"Lições: {len(user.completed_lessons)}/8 ({user.lessons_progress_percent:.0f}%)",
            font=theme.get_font(theme.FONT_BADGE),
            text_color=theme.COLOR_SUCCESS,
        )
        prog_badge.pack(side="right")

        stats_row = ctk.CTkFrame(global_card, fg_color="transparent")
        stats_row.pack(fill="x", padx=14, pady=(0, 14))

        self._create_stat_box(stats_row, "Exercícios Realizados", str(user.total_attempts), theme.COLOR_ACCENT_SKY)
        self._create_stat_box(stats_row, "Total de Acertos", str(user.total_correct), theme.COLOR_SUCCESS)
        self._create_stat_box(stats_row, "Precisão Global", f"{user.accuracy_rate:.1f}%", theme.COLOR_PRIMARY)
        self._create_stat_box(stats_row, "Melhor Sequência", f"🔥 {user.best_streak}", theme.COLOR_ACCENT_AMBER)

        # 2. Completed Lessons Status Cards (8 Chapters)
        lessons_card = ctk.CTkFrame(
            self.container,
            corner_radius=theme.RADIUS_LG,
            fg_color=theme.COLOR_SURFACE,
            border_width=1,
            border_color=theme.COLOR_BORDER,
        )
        lessons_card.pack(fill="x", pady=(0, 14))

        ctk.CTkLabel(
            lessons_card,
            text="Progresso nas 8 Lições Teóricas",
            font=theme.get_font(theme.FONT_SECTION),
            text_color=theme.COLOR_TEXT_PRIMARY,
        ).pack(anchor="w", padx=18, pady=(14, 8))

        lessons_row = ctk.CTkFrame(lessons_card, fg_color="transparent")
        lessons_row.pack(fill="x", padx=14, pady=(0, 14))
        for col in range(4):
            lessons_row.grid_columnconfigure(col, weight=1, uniform="lessons")

        for idx, (lid, ltitle) in enumerate(LESSON_IDS):
            row_idx = idx // 4
            col_idx = idx % 4
            is_done = lid in user.completed_lessons
            badge_frame = ctk.CTkFrame(
                lessons_row,
                corner_radius=theme.RADIUS_MD,
                fg_color=theme.COLOR_SUCCESS_BG if is_done else theme.COLOR_SURFACE_SECONDARY,
                border_width=1,
                border_color=theme.COLOR_SUCCESS if is_done else theme.COLOR_BORDER,
            )
            badge_frame.grid(row=row_idx, column=col_idx, padx=4, pady=4, sticky="nsew")

            status_icon = "✅" if is_done else "⏳"
            ctk.CTkLabel(
                badge_frame,
                text=f"{status_icon} {ltitle}",
                font=theme.get_font(theme.FONT_BADGE),
                text_color=theme.COLOR_SUCCESS if is_done else theme.COLOR_TEXT_MUTED,
            ).pack(padx=8, pady=10)

        # 3. Category Breakdown Cards (5 Categories)
        cat_grid = ctk.CTkFrame(self.container, fg_color="transparent")
        cat_grid.pack(fill="x", pady=(0, 14))
        cat_grid.grid_columnconfigure((0, 1, 2), weight=1, uniform="cats")

        cats_data = [
            ("repertorio", "🎵 Tocar Repertório", theme.COLOR_PRIMARY),
            ("pratica_instrumento", "🎯 Prática c/ Microfone", theme.COLOR_ACCENT_AMBER),
            ("treino_auditivo", "🎧 Treino Auditivo", theme.COLOR_ACCENT_PURPLE),
            ("leitura_pauta", "🎼 Leitura de Pauta", theme.COLOR_SUCCESS),
            ("teoria", "📖 Teoria Musical", theme.COLOR_ACCENT_SKY),
        ]

        for idx, (cat_key, cat_title, color) in enumerate(cats_data):
            row_idx = idx // 3
            col_idx = idx % 3
            stats = user.categories.get(cat_key, None)
            card = ctk.CTkFrame(
                cat_grid,
                corner_radius=theme.RADIUS_LG,
                fg_color=theme.COLOR_SURFACE,
                border_width=1,
                border_color=theme.COLOR_BORDER,
            )
            card.grid(row=row_idx, column=col_idx, padx=6, pady=4, sticky="nsew")

            ctk.CTkLabel(
                card,
                text=cat_title,
                font=theme.get_font(theme.FONT_SUBTITLE),
                text_color=theme.COLOR_TEXT_PRIMARY,
            ).pack(anchor="w", padx=16, pady=(12, 4))

            if stats and stats.total_attempts > 0:
                acc = (stats.correct_count / float(stats.total_attempts) * 100.0)
                txt = f"Tentativas: {stats.total_attempts} • Acertos: {stats.correct_count}\nPrecisão: {acc:.0f}% • Sequência Atual: 🔥 {stats.current_streak}"
            else:
                txt = "Nenhum exercício realizado ainda."

            ctk.CTkLabel(
                card,
                text=txt,
                font=theme.get_font(theme.FONT_BODY),
                text_color=theme.COLOR_TEXT_MUTED,
                justify="left",
            ).pack(anchor="w", padx=16, pady=(0, 14))

        # 4. Student Leaderboard Card
        lead_card = ctk.CTkFrame(
            self.container,
            corner_radius=theme.RADIUS_LG,
            fg_color=theme.COLOR_SURFACE,
            border_width=1,
            border_color=theme.COLOR_BORDER,
        )
        lead_card.pack(fill="x", pady=(0, 14))

        ctk.CTkLabel(
            lead_card,
            text="🏆 Tabela de Alunos & Classificação",
            font=theme.get_font(theme.FONT_SECTION),
            text_color=theme.COLOR_TEXT_PRIMARY,
        ).pack(anchor="w", padx=18, pady=(14, 6))

        lead_grid = ctk.CTkFrame(lead_card, fg_color="transparent")
        lead_grid.pack(fill="x", padx=14, pady=(0, 14))

        all_users = sorted(
            self.user_manager.get_all_users(),
            key=lambda u: (len(u.completed_lessons), u.accuracy_rate, u.total_attempts),
            reverse=True,
        )

        for rank, u in enumerate(all_users, start=1):
            is_active = u.username == user.username
            row_f = ctk.CTkFrame(
                lead_grid,
                corner_radius=theme.RADIUS_MD,
                fg_color=theme.COLOR_PRIMARY if is_active else theme.COLOR_SURFACE_SECONDARY,
                border_width=1 if is_active else 0,
                border_color=theme.COLOR_PRIMARY,
            )
            row_f.pack(fill="x", pady=2)

            rank_emoji = "🥇" if rank == 1 else ("🥈" if rank == 2 else ("🥉" if rank == 3 else f"#{rank}"))
            ctk.CTkLabel(
                row_f,
                text=f"{rank_emoji}  {u.avatar} {u.username}",
                font=theme.get_font(theme.FONT_BODY_BOLD),
                text_color="#FFFFFF" if is_active else theme.COLOR_TEXT_PRIMARY,
            ).pack(side="left", padx=14, pady=8)

            txt_info = f"Lições: {len(u.completed_lessons)}/8  •  Precisão: {u.accuracy_rate:.0f}%  •  Exercícios: {u.total_attempts}"
            ctk.CTkLabel(
                row_f,
                text=txt_info,
                font=theme.get_font(theme.FONT_BODY),
                text_color="#DBEAFE" if is_active else theme.COLOR_TEXT_MUTED,
            ).pack(side="right", padx=14)

    def _create_stat_box(self, parent, label: str, value: str, accent_color: str):
        box = ctk.CTkFrame(
            parent,
            corner_radius=theme.RADIUS_MD,
            fg_color=theme.COLOR_SURFACE_SECONDARY,
            border_width=1,
            border_color=theme.COLOR_BORDER,
        )
        box.pack(side="left", fill="both", expand=True, padx=4, pady=4)

        ctk.CTkLabel(
            box,
            text=value,
            font=theme.get_font(theme.FONT_TITLE, size=24),
            text_color=accent_color,
        ).pack(pady=(10, 0))

        ctk.CTkLabel(
            box,
            text=label,
            font=theme.get_font(theme.FONT_SMALL),
            text_color=theme.COLOR_TEXT_MUTED,
        ).pack(pady=(0, 10))

    def _handle_reset(self):
        user = self.user_manager.current_user
        confirm = messagebox.askyesno(
            "Limpar Dados",
            f"Tens a certeza que desejas apagar o histórico e progresso do aluno «{user.username}»?",
        )
        if confirm:
            self.user_manager.reset_current_user_scores()
            self._render_stats_content()
            messagebox.showinfo("Sucesso", "Progresso reiniciado com sucesso!")
