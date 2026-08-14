"""Statistics, progress tracking, user comparison leaderboard, gamification achievements, and export screen."""
import datetime
from tkinter import messagebox
from typing import Callable, Optional
import customtkinter as ctk
from core.user_manager import UserManager, LESSON_IDS
from core.gamification import ACHIEVEMENT_LIBRARY, get_achievement_by_id
from core.exporter import export_student_report_file
from gui import theme


class StatsScreen(ctk.CTkFrame):
    """Visual dashboard displaying performance metrics, streaks, XP level, achievements, and export options."""

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
            text=f"📊 Estatísticas & Conquistas — {user.avatar} {user.username}",
            font=theme.get_font(theme.FONT_TITLE),
            text_color=theme.COLOR_TEXT_PRIMARY,
        )
        title_lbl.pack(side="left", padx=16)

        btns_right = ctk.CTkFrame(nav_bar, fg_color="transparent")
        btns_right.pack(side="right")

        export_btn = ctk.CTkButton(
            btns_right,
            text="📥 Exportar Progresso",
            font=theme.get_font(theme.FONT_BODY_BOLD),
            fg_color=theme.COLOR_PRIMARY,
            hover_color=theme.COLOR_PRIMARY_HOVER,
            width=160,
            height=38,
            corner_radius=theme.RADIUS_MD,
            command=self._handle_export_report,
        )
        export_btn.pack(side="left", padx=4)

        reset_btn = ctk.CTkButton(
            btns_right,
            text="↺ Reiniciar Progresso",
            font=theme.get_font(theme.FONT_BODY_BOLD),
            fg_color=theme.COLOR_ACCENT_CRIMSON,
            hover_color=theme.COLOR_ACCENT_CRIMSON_HOVER,
            width=160,
            height=38,
            corner_radius=theme.RADIUS_MD,
            command=self._handle_reset,
        )
        reset_btn.pack(side="left", padx=4)

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
        lvl = user.level_info

        # 1. Level & XP Progression Card
        xp_card = ctk.CTkFrame(
            self.container,
            corner_radius=theme.RADIUS_LG,
            fg_color=theme.COLOR_SURFACE,
            border_width=1,
            border_color=theme.COLOR_BORDER,
        )
        xp_card.pack(fill="x", pady=(0, 14))

        xp_inner = ctk.CTkFrame(xp_card, fg_color="transparent")
        xp_inner.pack(fill="x", padx=20, pady=16)

        left_lvl = ctk.CTkFrame(xp_inner, fg_color="transparent")
        left_lvl.pack(side="left", fill="x", expand=True)

        ctk.CTkLabel(
            left_lvl,
            text=f"{lvl['icon']} Nível {lvl['level']}: {lvl['title']}",
            font=theme.get_font(theme.FONT_TITLE, size=22),
            text_color=theme.COLOR_PRIMARY,
        ).pack(anchor="w")

        xp_sub_text = (
            f"Experiência Total: {user.xp} XP  •  "
            f"{'Faltam ' + str(lvl['xp_needed']) + ' XP para o Nível ' + str(lvl['level'] + 1) if lvl['xp_needed'] > 0 else 'Nível Máximo Atingido!'}"
        )
        ctk.CTkLabel(
            left_lvl,
            text=xp_sub_text,
            font=theme.get_font(theme.FONT_BODY),
            text_color=theme.COLOR_TEXT_MUTED,
        ).pack(anchor="w", pady=(2, 6))

        xp_bar = ctk.CTkProgressBar(left_lvl, height=10, progress_color=theme.COLOR_PRIMARY)
        xp_bar.set(lvl["progress_pct"] / 100.0)
        xp_bar.pack(fill="x", pady=(2, 0))

        # 2. Global Overview Cards
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
            text=f"Desempenho de {user.avatar} {user.username}",
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

        # 3. Badges & Achievements Showcase (12 Achievements)
        ach_card = ctk.CTkFrame(
            self.container,
            corner_radius=theme.RADIUS_LG,
            fg_color=theme.COLOR_SURFACE,
            border_width=1,
            border_color=theme.COLOR_BORDER,
        )
        ach_card.pack(fill="x", pady=(0, 14))

        ctk.CTkLabel(
            ach_card,
            text=f"🏅 Medalhas & Conquistas ({len(user.unlocked_achievements)}/{len(ACHIEVEMENT_LIBRARY)})",
            font=theme.get_font(theme.FONT_SECTION),
            text_color=theme.COLOR_TEXT_PRIMARY,
        ).pack(anchor="w", padx=18, pady=(14, 8))

        ach_grid = ctk.CTkFrame(ach_card, fg_color="transparent")
        ach_grid.pack(fill="x", padx=14, pady=(0, 14))
        for col in range(3):
            ach_grid.grid_columnconfigure(col, weight=1, uniform="achs")

        for idx, ach in enumerate(ACHIEVEMENT_LIBRARY):
            row_idx = idx // 3
            col_idx = idx % 3
            is_unlocked = ach.id in user.unlocked_achievements

            item = ctk.CTkFrame(
                ach_grid,
                corner_radius=theme.RADIUS_MD,
                fg_color=theme.COLOR_SUCCESS_BG if is_unlocked else theme.COLOR_SURFACE_SECONDARY,
                border_width=1,
                border_color=theme.COLOR_SUCCESS if is_unlocked else theme.COLOR_BORDER,
            )
            item.grid(row=row_idx, column=col_idx, padx=4, pady=4, sticky="nsew")

            top_a = ctk.CTkFrame(item, fg_color="transparent")
            top_a.pack(fill="x", padx=10, pady=(8, 2))

            ctk.CTkLabel(top_a, text=ach.icon, font=ctk.CTkFont(size=20)).pack(side="left")
            ctk.CTkLabel(
                top_a,
                text=ach.title,
                font=theme.get_font(theme.FONT_BODY_BOLD),
                text_color=theme.COLOR_SUCCESS if is_unlocked else theme.COLOR_TEXT_MUTED,
            ).pack(side="left", padx=6)

            reward_text = f"+{ach.xp_reward} XP" if not is_unlocked else "✓ Ganho"
            ctk.CTkLabel(
                top_a,
                text=reward_text,
                font=theme.get_font(theme.FONT_BADGE),
                text_color=theme.COLOR_PRIMARY if not is_unlocked else theme.COLOR_SUCCESS,
            ).pack(side="right")

            ctk.CTkLabel(
                item,
                text=ach.description,
                font=theme.get_font(theme.FONT_SMALL),
                text_color=theme.COLOR_TEXT_MUTED,
                wraplength=230,
                justify="left",
            ).pack(anchor="w", padx=10, pady=(0, 8))

        # 4. Completed Lessons Status Cards (8 Chapters)
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

        # 5. Student Leaderboard Card
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
            text="🏆 Tabela Geral de Alunos & Classificação XP",
            font=theme.get_font(theme.FONT_SECTION),
            text_color=theme.COLOR_TEXT_PRIMARY,
        ).pack(anchor="w", padx=18, pady=(14, 6))

        lead_grid = ctk.CTkFrame(lead_card, fg_color="transparent")
        lead_grid.pack(fill="x", padx=14, pady=(0, 14))

        all_users = sorted(
            self.user_manager.get_all_users(),
            key=lambda u: (u.xp, len(u.completed_lessons), u.accuracy_rate),
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
                text=f"{rank_emoji}  {u.avatar} {u.username}  ({u.level_info['icon']} Nível {u.level})",
                font=theme.get_font(theme.FONT_BODY_BOLD),
                text_color="#FFFFFF" if is_active else theme.COLOR_TEXT_PRIMARY,
            ).pack(side="left", padx=14, pady=8)

            txt_info = f"XP: {u.xp}  •  Lições: {len(u.completed_lessons)}/8  •  Precisão: {u.accuracy_rate:.0f}%"
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

    def _handle_export_report(self):
        user = self.user_manager.current_user
        try:
            filepath = export_student_report_file(user)
            messagebox.showinfo(
                "Exportação Concluída",
                f"Relatório de progresso e certificado de {user.username} exportado com sucesso para:\n\n{filepath}",
            )
        except Exception as e:
            messagebox.showerror("Erro ao Exportar", f"Não foi possível exportar o relatório: {e}")

    def _handle_reset(self):
        user = self.user_manager.current_user
        confirm = messagebox.askyesno(
            "Limpar Dados",
            f"Tens a certeza que desejas apagar o histórico, XP e lições do aluno «{user.username}»?",
        )
        if confirm:
            self.user_manager.reset_current_user_scores()
            self._render_stats_content()
            messagebox.showinfo("Sucesso", "Progresso reiniciado com sucesso!")
