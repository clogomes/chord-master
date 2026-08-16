from gui.i18n import t
"""Statistics, visual progress charts, activity calendar, leaderboard, and report exporter."""
import datetime
import time
import tkinter as tk
from tkinter import messagebox
from typing import Callable, Dict, List, Optional, Tuple
import customtkinter as ctk
from core.user_manager import UserManager, LESSON_IDS, UserProfile
from core.gamification import ACHIEVEMENT_LIBRARY, get_achievement_by_id
from core.exporter import export_student_report_file
from core.adaptive_engine import get_weak_areas
from gui.scroll_utils import bind_mousewheel
from gui import theme


class StatsScreen(ctk.CTkFrame):
    """Visual dashboard with Canvas-rendered trend charts, category comparisons, activity heatmaps, and achievements."""

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

        title_lbl = ctk.CTkLabel(
            nav_bar,
            text=f"📊 Estatísticas & Análise de Progresso — {user.avatar} {user.username}",
            font=theme.get_font(theme.FONT_TITLE),
            text_color=theme.COLOR_TEXT_PRIMARY,
        )
        title_lbl.pack(side="left", padx=16)

        btns_right = ctk.CTkFrame(nav_bar, fg_color="transparent")
        btns_right.pack(side="right")

        export_btn = ctk.CTkButton(
            btns_right,
            text=t("btn_export", "📥 Exportar Progresso"),
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
        bind_mousewheel(self.container)

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
            text=f"Resumo Geral de Desempenho",
            font=theme.get_font(theme.FONT_SECTION),
            text_color=theme.COLOR_TEXT_PRIMARY,
        ).pack(side="left")

        prog_badge = ctk.CTkLabel(
            header_row,
            text=f"Lições: {len(user.completed_lessons)}/{len(LESSON_IDS)} ({user.lessons_progress_percent:.0f}%)",
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

        # 3. Visual Charts Row (Accuracy Trend + Category Comparison Bars)
        charts_row = ctk.CTkFrame(self.container, fg_color="transparent")
        charts_row.pack(fill="x", pady=(0, 14))
        charts_row.grid_columnconfigure((0, 1), weight=1, uniform="charts")

        # Chart 1: Accuracy Trend (Last 4 Weeks)
        trend_card = ctk.CTkFrame(
            charts_row,
            corner_radius=theme.RADIUS_LG,
            fg_color=theme.COLOR_SURFACE,
            border_width=1,
            border_color=theme.COLOR_BORDER,
        )
        trend_card.grid(row=0, column=0, sticky="nsew", padx=(0, 6))

        ctk.CTkLabel(
            trend_card,
            text="📈 Tendência de Precisão (Últimas 4 Semanas)",
            font=theme.get_font(theme.FONT_SECTION),
            text_color=theme.COLOR_TEXT_PRIMARY,
        ).pack(anchor="w", padx=16, pady=(12, 6))

        trend_canvas = tk.Canvas(
            trend_card,
            height=240,
            bg="#111827",
            highlightthickness=0,
        )
        trend_canvas.pack(fill="x", padx=14, pady=(0, 12))
        self._draw_accuracy_trend(trend_canvas, user)

        # Chart 2: Category Comparison Bars
        cat_card = ctk.CTkFrame(
            charts_row,
            corner_radius=theme.RADIUS_LG,
            fg_color=theme.COLOR_SURFACE,
            border_width=1,
            border_color=theme.COLOR_BORDER,
        )
        cat_card.grid(row=0, column=1, sticky="nsew", padx=(6, 0))

        ctk.CTkLabel(
            cat_card,
            text="📊 Desempenho por Categoria (%)",
            font=theme.get_font(theme.FONT_SECTION),
            text_color=theme.COLOR_TEXT_PRIMARY,
        ).pack(anchor="w", padx=16, pady=(12, 6))

        cat_canvas = tk.Canvas(
            cat_card,
            height=240,
            bg="#111827",
            highlightthickness=0,
        )
        cat_canvas.pack(fill="x", padx=14, pady=(0, 12))
        self._draw_category_bars(cat_canvas, user)

        # 4. Activity Heatmap Calendar (GitHub Style ~90 Days)
        calendar_card = ctk.CTkFrame(
            self.container,
            corner_radius=theme.RADIUS_LG,
            fg_color=theme.COLOR_SURFACE,
            border_width=1,
            border_color=theme.COLOR_BORDER,
        )
        calendar_card.pack(fill="x", pady=(0, 14))

        cal_top = ctk.CTkFrame(calendar_card, fg_color="transparent")
        cal_top.pack(fill="x", padx=16, pady=(12, 4))

        ctk.CTkLabel(
            cal_top,
            text="📅 Calendário de Consistência & Atividade (Últimos 90 Dias)",
            font=theme.get_font(theme.FONT_SECTION),
            text_color=theme.COLOR_TEXT_PRIMARY,
        ).pack(side="left")

        # Active days count
        active_days_count = len(set(
            datetime.date.fromtimestamp(rec.timestamp)
            for rec in user.history
        ))
        ctk.CTkLabel(
            cal_top,
            text=f"Total de Dias Ativos: {active_days_count} dias",
            font=theme.get_font(theme.FONT_BADGE),
            text_color=theme.COLOR_SUCCESS,
        ).pack(side="right")

        cal_canvas = tk.Canvas(
            calendar_card,
            height=140,
            bg="#111827",
            highlightthickness=0,
        )
        cal_canvas.pack(fill="x", padx=14, pady=(0, 12))
        self._draw_activity_calendar(cal_canvas, user)

        # 5. Badges & Achievements Showcase (12 Achievements)
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

        # 6. Completed Lessons Status Cards (8 Chapters)
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
            text=f"Progresso nas {len(LESSON_IDS)} Lições Teóricas",
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

        # 7. Student Leaderboard Card
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

            txt_info = f"XP: {u.xp}  •  Lições: {len(u.completed_lessons)}/{len(LESSON_IDS)}  •  Precisão: {u.accuracy_rate:.0f}%"
            ctk.CTkLabel(
                row_f,
                text=txt_info,
                font=theme.get_font(theme.FONT_BODY),
                text_color="#DBEAFE" if is_active else theme.COLOR_TEXT_MUTED,
            ).pack(side="right", padx=14)

    def _draw_accuracy_trend(self, canvas: tk.Canvas, user: UserProfile):
        """Draws a 4-week accuracy trend line chart with percentage axes and highlighted data points."""
        canvas.delete("all")
        w = canvas.winfo_width() or 440
        h = 210

        # Calculate accuracy for each of the last 4 weeks
        now = time.time()
        week_seconds = 7 * 86400
        weeks_data = []  # list of (label, accuracy_pct, count)

        for i in range(3, -1, -1):
            start_t = now - (i + 1) * week_seconds
            end_t = now - i * week_seconds
            lbl = "Sem -3" if i == 3 else ("Sem -2" if i == 2 else ("Sem Passada" if i == 1 else "Esta Semana"))

            recs = [r for r in user.history if start_t <= r.timestamp <= end_t]
            if recs:
                corr = sum(1 for r in recs if r.is_correct)
                acc = (corr / len(recs)) * 100.0
            else:
                acc = user.accuracy_rate if user.history else 75.0
            weeks_data.append((lbl, acc, len(recs)))

        pad_l = 45
        pad_r = 25
        pad_t = 25
        pad_b = 35
        chart_w = w - pad_l - pad_r
        chart_h = h - pad_t - pad_b

        # Draw horizontal grid lines (0%, 25%, 50%, 75%, 100%)
        for pct in [0, 25, 50, 75, 100]:
            y = pad_t + chart_h - (pct / 100.0) * chart_h
            canvas.create_line(pad_l, y, w - pad_r, y, fill="#374151", dash=(2, 4))
            canvas.create_text(pad_l - 8, y, text=f"{pct}%", fill="#9CA3AF", font=("Helvetica", 10), anchor="e")

        # Coordinates for the 4 points
        points = []
        step_x = chart_w / 3.0
        for idx, (lbl, acc, count) in enumerate(weeks_data):
            x = pad_l + idx * step_x
            y = pad_t + chart_h - (acc / 100.0) * chart_h
            points.append((x, y, acc, lbl, count))

        # Draw connecting line
        line_coords = []
        for p in points:
            line_coords.extend([p[0], p[1]])
        if len(line_coords) >= 4:
            canvas.create_line(line_coords, fill="#4F46E5", width=3, smooth=True)

        # Draw point dots and values
        for x, y, acc, lbl, count in points:
            # Outer halo
            canvas.create_oval(x - 6, y - 6, x + 6, y + 6, fill="#111827", outline="#4F46E5", width=2)
            # Inner dot
            canvas.create_oval(x - 3, y - 3, x + 3, y + 3, fill="#10B981")
            # Percentage label
            canvas.create_text(x, y - 14, text=f"{acc:.0f}%", fill="#FFFFFF", font=("Helvetica", 11, "bold"))
            # Week label on bottom axis
            canvas.create_text(x, h - 14, text=lbl, fill="#9CA3AF", font=("Helvetica", 10))

    def _draw_category_bars(self, canvas: tk.Canvas, user: UserProfile):
        """Draws horizontal percentage comparison bars for all study categories."""
        canvas.delete("all")
        w = canvas.winfo_width() or 440
        h = 280

        from core.categories import CATEGORY_NAMES_PT, CATEGORY_COLORS
        categories = [(v, k, CATEGORY_COLORS.get(k, "#6B7280")) for k, v in CATEGORY_NAMES_PT.items()]

        pad_l = 150
        pad_r = 65
        pad_t = 16
        bar_h = 18
        spacing = 42

        for idx, (title, cat_key, col) in enumerate(categories):
            y = pad_t + idx * spacing

            # Calculate accuracy for this category
            cat_recs = [r for r in user.history if r.category == cat_key]
            if cat_recs:
                corr = sum(1 for r in cat_recs if r.is_correct)
                acc = (corr / len(cat_recs)) * 100.0
                sub_info = f"{corr}/{len(cat_recs)}"
            else:
                acc = 0.0
                sub_info = "0/0"

            # Label on left
            canvas.create_text(pad_l - 12, y + bar_h // 2, text=title, fill="#F9FAFB", font=("Helvetica", 11, "bold"), anchor="e")

            # Background bar track
            track_w = w - pad_l - pad_r
            canvas.create_rectangle(pad_l, y, pad_l + track_w, y + bar_h, fill="#1F2937", outline="")

            # Filled progress bar
            fill_w = max(4.0, (acc / 100.0) * track_w) if acc > 0 else 0
            if fill_w > 0:
                canvas.create_rectangle(pad_l, y, pad_l + fill_w, y + bar_h, fill=col, outline="")

            # Percentage text on right
            canvas.create_text(pad_l + track_w + 10, y + bar_h // 2, text=f"{acc:.0f}%", fill=col if acc > 0 else "#6B7280", font=("Helvetica", 11, "bold"), anchor="w")

    def _draw_activity_calendar(self, canvas: tk.Canvas, user: UserProfile):
        """Draws a 90-day activity heatmap grid (GitHub contribution graph style)."""
        canvas.delete("all")
        w = canvas.winfo_width() or 900
        h = 140

        # Group history by date
        history_by_date: Dict[datetime.date, int] = {}
        for rec in user.history:
            d = datetime.date.fromtimestamp(rec.timestamp)
            history_by_date[d] = history_by_date.get(d, 0) + 1

        today = datetime.date.today()
        # 13 weeks of 7 days = 91 days
        start_date = today - datetime.timedelta(days=90)
        # Adjust start_date to Monday
        start_monday = start_date - datetime.timedelta(days=start_date.weekday())

        box_size = 14
        gap = 4
        pad_l = 40
        pad_t = 28

        # Day initials on the left
        day_initials = ["S", "T", "Q", "Q", "S", "S", "D"]
        for d_idx, init in enumerate(day_initials):
            y = pad_t + d_idx * (box_size + gap) + box_size // 2
            canvas.create_text(pad_l - 12, y, text=init, fill="#6B7280", font=("Helvetica", 9), anchor="e")

        curr = start_monday
        week_idx = 0
        last_month = None

        while curr <= today or week_idx < 14:
            x = pad_l + week_idx * (box_size + gap)

            # Month label above first week of that month
            if curr.month != last_month and curr <= today:
                months_pt = ["", "Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
                canvas.create_text(x, pad_t - 14, text=months_pt[curr.month], fill="#9CA3AF", font=("Helvetica", 10, "bold"), anchor="w")
                last_month = curr.month

            for day_of_week in range(7):
                day_date = curr + datetime.timedelta(days=day_of_week)
                y = pad_t + day_of_week * (box_size + gap)

                if day_date > today or day_date < start_date:
                    col = "#111827"  # future or out of bounds
                else:
                    cnt = history_by_date.get(day_date, 0)
                    if cnt == 0:
                        col = "#1F2937"
                    elif cnt <= 2:
                        col = "#065F46"
                    elif cnt <= 5:
                        col = "#059669"
                    elif cnt <= 9:
                        col = "#10B981"
                    else:
                        col = "#34D399"

                canvas.create_rectangle(x, y, x + box_size, y + box_size, fill=col, outline="")

            curr += datetime.timedelta(days=7)
            week_idx += 1
            if week_idx >= 14:
                break

        # Legend at bottom right
        leg_x = pad_l + 14 * (box_size + gap) + 20
        leg_y = h - 22
        canvas.create_text(leg_x, leg_y, text="Menos", fill="#6B7280", font=("Helvetica", 9), anchor="w")
        legend_colors = ["#1F2937", "#065F46", "#059669", "#10B981", "#34D399"]
        for idx, col in enumerate(legend_colors):
            bx = leg_x + 42 + idx * (box_size + 3)
            canvas.create_rectangle(bx, leg_y - 7, bx + box_size, leg_y + 7, fill=col, outline="")
        canvas.create_text(leg_x + 42 + len(legend_colors) * (box_size + 3) + 8, leg_y, text="Mais", fill="#6B7280", font=("Helvetica", 9), anchor="w")

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
