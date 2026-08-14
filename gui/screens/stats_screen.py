"""Statistics, progress tracking, user comparison leaderboard, and activity history screen."""
import datetime
from typing import Callable
import customtkinter as ctk
from core.user_manager import UserManager, LESSON_IDS


class StatsScreen(ctk.CTkFrame):
    """Visual dashboard displaying performance metrics, streaks, completed lessons, and student leaderboard."""

    def __init__(
        self,
        master,
        user_manager: UserManager,
        on_back: Callable[[], None],
        **kwargs,
    ):
        super().__init__(master, fg_color=("#F8FAFC", "#0F172A"), **kwargs)
        self.user_manager = user_manager
        self.on_back = on_back

        self._build_ui()

    def _build_ui(self):
        user = self.user_manager.current_user

        # Top Navigation Bar
        nav_bar = ctk.CTkFrame(self, fg_color="transparent")
        nav_bar.pack(fill="x", padx=20, pady=(16, 6))

        back_btn = ctk.CTkButton(
            nav_bar,
            text="← Voltar ao Menu",
            font=ctk.CTkFont(family="Helvetica", size=13, weight="bold"),
            fg_color="#475569",
            hover_color="#334155",
            width=130,
            command=self.on_back,
        )
        back_btn.pack(side="left")

        title_lbl = ctk.CTkLabel(
            nav_bar,
            text=f"📊 Estatísticas — {user.avatar} {user.username}",
            font=ctk.CTkFont(family="Helvetica", size=22, weight="bold"),
            text_color=("#0F172A", "#F8FAFC"),
        )
        title_lbl.pack(side="left", padx=16)

        reset_btn = ctk.CTkButton(
            nav_bar,
            text="🗑️ Limpar Meus Dados",
            font=ctk.CTkFont(family="Helvetica", size=12, weight="bold"),
            fg_color="#DC2626",
            hover_color="#B91C1C",
            width=140,
            command=self._handle_reset,
        )
        reset_btn.pack(side="right")

        # Scrollable Content
        self.container = ctk.CTkScrollableFrame(self, fg_color=("#F8FAFC", "#0F172A"))
        self.container.pack(fill="both", expand=True, padx=20, pady=(4, 16))

        self._render_stats_content()

    def _render_stats_content(self):
        # Clean previous items
        for child in self.container.winfo_children():
            child.destroy()

        user = self.user_manager.current_user

        # 1. Global Overview Cards for Active User
        global_card = ctk.CTkFrame(
            self.container,
            corner_radius=12,
            fg_color=("#F8FAFC", "#1E293B"),
            border_width=1,
            border_color=("#E2E8F0", "#334155"),
        )
        global_card.pack(fill="x", pady=(0, 12))

        header_row = ctk.CTkFrame(global_card, fg_color="transparent")
        header_row.pack(fill="x", padx=16, pady=(12, 4))

        ctk.CTkLabel(
            header_row,
            text=f"Desempenho de {user.avatar} {user.username}",
            font=ctk.CTkFont(family="Helvetica", size=16, weight="bold"),
            text_color=("#0F172A", "#F8FAFC"),
        ).pack(side="left")

        prog_badge = ctk.CTkLabel(
            header_row,
            text=f"Lições: {len(user.completed_lessons)}/4 ({user.lessons_progress_percent:.0f}%)",
            font=ctk.CTkFont(family="Helvetica", size=12, weight="bold"),
            text_color="#10B981",
        )
        prog_badge.pack(side="right")

        stats_row = ctk.CTkFrame(global_card, fg_color="transparent")
        stats_row.pack(fill="x", padx=12, pady=(0, 12))

        self._create_stat_box(stats_row, "Total de Exercícios", str(user.total_attempts), "#3B82F6")
        self._create_stat_box(stats_row, "Total de Acertos", str(user.total_correct), "#10B981")
        self._create_stat_box(stats_row, "Precisão Global", f"{user.accuracy_rate:.1f}%", "#8B5CF6")
        self._create_stat_box(stats_row, "Maior Sequência", f"🔥 {user.best_streak}", "#F59E0B")

        # 2. Completed Lessons Status Cards
        lessons_card = ctk.CTkFrame(
            self.container,
            corner_radius=12,
            fg_color=("#F8FAFC", "#1E293B"),
            border_width=1,
            border_color=("#E2E8F0", "#334155"),
        )
        lessons_card.pack(fill="x", pady=(0, 12))

        ctk.CTkLabel(
            lessons_card,
            text="Progresso nas Lições Teóricas",
            font=ctk.CTkFont(family="Helvetica", size=15, weight="bold"),
            text_color=("#0F172A", "#F8FAFC"),
        ).pack(anchor="w", padx=16, pady=(12, 6))

        lessons_row = ctk.CTkFrame(lessons_card, fg_color="transparent")
        lessons_row.pack(fill="x", padx=12, pady=(0, 12))
        lessons_row.grid_columnconfigure((0, 1, 2, 3), weight=1, uniform="lessons")

        for i, (lid, ltitle) in enumerate(LESSON_IDS):
            is_done = lid in user.completed_lessons
            badge_frame = ctk.CTkFrame(
                lessons_row,
                corner_radius=8,
                fg_color=("#DCFCE7", "#064E3B") if is_done else ("#F1F5F9", "#0F172A"),
                border_width=1,
                border_color="#10B981" if is_done else "#334155",
            )
            badge_frame.grid(row=0, column=i, padx=4, pady=4, sticky="nsew")

            status_icon = "✅" if is_done else "⏳"
            ctk.CTkLabel(
                badge_frame,
                text=f"{status_icon} {ltitle}",
                font=ctk.CTkFont(family="Helvetica", size=11, weight="bold"),
                text_color="#065F46" if is_done else ("#64748B", "#94A3B8"),
            ).pack(padx=8, pady=8)

        # 3. Category Breakdown Cards (5 Categories)
        cat_grid = ctk.CTkFrame(self.container, fg_color="transparent")
        cat_grid.pack(fill="x", pady=(0, 12))
        cat_grid.grid_columnconfigure((0, 1, 2), weight=1, uniform="cats")

        cats_data = [
            ("repertorio", "🎵 Tocar Repertório", "#D97706"),
            ("pratica_instrumento", "🎙️ Instrumento Real", "#DC2626"),
            ("treino_auditivo", "🎧 Treino Auditivo", "#7C3AED"),
            ("leitura_pauta", "🎼 Leitura de Pauta", "#059669"),
            ("teoria", "📖 Teoria Musical", "#2563EB"),
        ]

        for idx, (cat_key, cat_title, color) in enumerate(cats_data):
            row_idx = idx // 3
            col_idx = idx % 3
            stats = user.categories.get(cat_key, None)
            card = ctk.CTkFrame(
                cat_grid,
                corner_radius=12,
                fg_color=("#F8FAFC", "#1E293B"),
                border_width=1,
                border_color=("#E2E8F0", "#334155"),
            )
            card.grid(row=row_idx, column=col_idx, padx=6, pady=4, sticky="nsew")

            ctk.CTkLabel(
                card,
                text=cat_title,
                font=ctk.CTkFont(family="Helvetica", size=15, weight="bold"),
                text_color=color,
            ).pack(anchor="w", padx=14, pady=(12, 6))

            acc = stats.accuracy_rate if stats else 0.0
            attempts = stats.total_attempts if stats else 0
            correct = stats.correct_count if stats else 0
            cur_streak = stats.current_streak if stats else 0
            b_streak = stats.best_streak if stats else 0

            pbar = ctk.CTkProgressBar(card, progress_color=color, height=8)
            pbar.set(acc / 100.0)
            pbar.pack(fill="x", padx=14, pady=4)

            info_text = (
                f"• Exercícios: **{attempts}**\n"
                f"• Acertos: **{correct}**\n"
                f"• Precisão: **{acc:.1f}%**\n"
                f"• Sequência Atual: **{cur_streak}**\n"
                f"• Melhor Sequência: **{b_streak}**"
            )
            ctk.CTkLabel(
                card,
                text=info_text,
                font=ctk.CTkFont(family="Helvetica", size=12),
                justify="left",
                text_color=("#334155", "#CBD5E1"),
            ).pack(anchor="w", padx=14, pady=(4, 12))

        # 4. Multi-user Comparison / Leaderboard
        all_users = self.user_manager.get_all_users()
        if len(all_users) > 1:
            lead_card = ctk.CTkFrame(
                self.container,
                corner_radius=12,
                fg_color=("#F8FAFC", "#1E293B"),
                border_width=1,
                border_color=("#E2E8F0", "#334155"),
            )
            lead_card.pack(fill="x", pady=(0, 12))

            ctk.CTkLabel(
                lead_card,
                text="🏆 Tabela de Estudantes Registados",
                font=ctk.CTkFont(family="Helvetica", size=15, weight="bold"),
                text_color=("#0F172A", "#F8FAFC"),
            ).pack(anchor="w", padx=16, pady=(12, 6))

            # Sorted by completed lessons then accuracy
            sorted_users = sorted(all_users, key=lambda u: (len(u.completed_lessons), u.accuracy_rate, u.total_attempts), reverse=True)

            for rank, u in enumerate(sorted_users, 1):
                is_curr = u.username == user.username
                urow = ctk.CTkFrame(
                    lead_card,
                    corner_radius=8,
                    fg_color=("#EFF6FF", "#172554") if is_curr else ("#F1F5F9", "#0F172A"),
                    border_width=1 if is_curr else 0,
                    border_color="#3B82F6",
                )
                urow.pack(fill="x", padx=14, pady=3)

                medal = "🥇" if rank == 1 else ("🥈" if rank == 2 else ("🥉" if rank == 3 else f"#{rank}"))
                ctk.CTkLabel(
                    urow,
                    text=f"{medal} {u.avatar} {u.username}" + (" (Tu)" if is_curr else ""),
                    font=ctk.CTkFont(family="Helvetica", size=13, weight="bold"),
                    text_color=("#1D4ED8", "#93C5FD") if is_curr else ("#0F172A", "#F8FAFC"),
                ).pack(side="left", padx=12, pady=6)

                stats_str = f"Lições: {len(u.completed_lessons)}/4 • Precisão: {u.accuracy_rate:.0f}% ({u.total_attempts} ex.) • Recorde: 🔥 {u.best_streak}"
                ctk.CTkLabel(
                    urow,
                    text=stats_str,
                    font=ctk.CTkFont(family="Helvetica", size=12),
                    text_color=("#64748B", "#94A3B8"),
                ).pack(side="right", padx=12)

            ctk.CTkLabel(lead_card, text="", height=4).pack()

        # 5. Recent Activity Log for Active User
        log_frame = ctk.CTkFrame(
            self.container,
            corner_radius=12,
            fg_color=("#F8FAFC", "#1E293B"),
            border_width=1,
            border_color=("#E2E8F0", "#334155"),
        )
        log_frame.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            log_frame,
            text=f"Histórico Recente de {user.avatar} {user.username}",
            font=ctk.CTkFont(family="Helvetica", size=15, weight="bold"),
            text_color=("#0F172A", "#F8FAFC"),
        ).pack(anchor="w", padx=16, pady=(12, 6))

        if not user.history:
            ctk.CTkLabel(
                log_frame,
                text="Ainda não existem exercícios registados para este utilizador.",
                font=ctk.CTkFont(family="Helvetica", size=13),
                text_color=("#64748B", "#94A3B8"),
            ).pack(padx=16, pady=(0, 16))
        else:
            for record in reversed(user.history[-15:]):
                item_row = ctk.CTkFrame(log_frame, fg_color=("#F1F5F9", "#0F172A"), corner_radius=8)
                item_row.pack(fill="x", padx=14, pady=3)

                badge_color = "#10B981" if record.is_correct else "#EF4444"
                badge_text = "✓ CERTO" if record.is_correct else "✗ ERRO"

                badge = ctk.CTkLabel(
                    item_row,
                    text=badge_text,
                    font=ctk.CTkFont(family="Helvetica", size=11, weight="bold"),
                    text_color=badge_color,
                    width=60,
                )
                badge.pack(side="left", padx=8, pady=6)

                cat_clean = record.category.replace("_", " ").title()
                cat_lbl = ctk.CTkLabel(
                    item_row,
                    text=f"[{cat_clean}]",
                    font=ctk.CTkFont(family="Helvetica", size=12, weight="bold"),
                    text_color=("#64748B", "#94A3B8"),
                    width=130,
                )
                cat_lbl.pack(side="left", padx=4)

                details = f"Resposta: {record.user_answer} | Correta: {record.correct_answer}"
                det_lbl = ctk.CTkLabel(
                    item_row,
                    text=details,
                    font=ctk.CTkFont(family="Helvetica", size=12),
                    text_color=("#0F172A", "#E2E8F0"),
                )
                det_lbl.pack(side="left", padx=8)

            ctk.CTkLabel(log_frame, text="", height=4).pack()

    def _create_stat_box(self, parent, label: str, val: str, accent_color: str):
        box = ctk.CTkFrame(parent, fg_color="transparent")
        box.pack(side="left", expand=True, fill="both", padx=8, pady=6)

        ctk.CTkLabel(
            box,
            text=val,
            font=ctk.CTkFont(family="Helvetica", size=24, weight="bold"),
            text_color=accent_color,
        ).pack()

        ctk.CTkLabel(
            box,
            text=label,
            font=ctk.CTkFont(family="Helvetica", size=12),
            text_color=("#64748B", "#94A3B8"),
        ).pack()

    def _handle_reset(self):
        self.user_manager.reset_current_user_scores()
        self._render_stats_content()
