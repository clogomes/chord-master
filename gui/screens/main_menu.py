from gui.i18n import t
"""Main Menu screen with personalized user dashboard and module launcher cards."""
from tkinter import messagebox
from typing import Callable, Optional
import customtkinter as ctk
from core.user_manager import UserManager, LESSON_IDS
from core.adaptive_engine import get_recommendation
from gui import theme


class MainMenuScreen(ctk.CTkFrame):
    """Modern home dashboard displaying student progress, lesson completion, and mode launchers."""

    def __init__(
        self,
        master,
        user_manager: UserManager,
        on_navigate: Callable[[str], None],
        on_open_users: Optional[Callable[[], None]] = None,
        on_switch_user: Optional[Callable[[], None]] = None,
        **kwargs,
    ):
        super().__init__(master, fg_color=theme.COLOR_BG, **kwargs)
        self.user_manager = user_manager
        self.on_navigate = on_navigate
        self.on_open_users = on_switch_user or on_open_users

        self._build_ui()

    def _build_ui(self):
        user = self.user_manager.current_user

        # Header banner with greeting & user switcher
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=24, pady=(20, 8))

        left_header = ctk.CTkFrame(header_frame, fg_color="transparent")
        left_header.pack(side="left", fill="x", expand=True)

        title_label = ctk.CTkLabel(
            left_header,
            text=f"Olá, {user.avatar} {user.username}! 👋",
            font=theme.get_font(theme.FONT_HERO, size=28),
            text_color=theme.COLOR_TEXT_PRIMARY,
        )
        title_label.pack(anchor="w")

        subtitle_label = ctk.CTkLabel(
            left_header,
            text="Bem-vindo ao teu estúdio interativo de teoria musical e prática instrumental.",
            font=theme.get_font(theme.FONT_BODY),
            text_color=theme.COLOR_TEXT_MUTED,
        )
        subtitle_label.pack(anchor="w", pady=(2, 0))

        if self.on_open_users:
            user_btn = ctk.CTkButton(
                header_frame,
                text=f"{user.avatar} Trocar Perfil",
                font=theme.get_font(theme.FONT_BODY_BOLD),
                fg_color=theme.COLOR_SURFACE_SECONDARY,
                hover_color=theme.COLOR_SURFACE_HOVER,
                text_color=theme.COLOR_TEXT_PRIMARY,
                border_width=1,
                border_color=theme.COLOR_BORDER,
                height=36,
                corner_radius=theme.RADIUS_MD,
                command=self.on_open_users,
            )
            user_btn.pack(side="right", padx=(10, 0))

        # Lesson Progress Banner
        lesson_card = ctk.CTkFrame(
            self,
            corner_radius=theme.RADIUS_LG,
            fg_color=theme.COLOR_PRIMARY_BG,
            border_width=1,
            border_color=theme.COLOR_PRIMARY_BORDER,
        )
        lesson_card.pack(fill="x", padx=24, pady=(4, 10))

        lesson_inner = ctk.CTkFrame(lesson_card, fg_color="transparent")
        lesson_inner.pack(fill="x", padx=18, pady=12)

        lesson_left = ctk.CTkFrame(lesson_inner, fg_color="transparent")
        lesson_left.pack(side="left", fill="x", expand=True)

        completed_count = len(user.completed_lessons)
        total_count = len(LESSON_IDS)
        prog_pct = user.lessons_progress_percent

        ctk.CTkLabel(
            lesson_left,
            text=f"🎯 Progresso nas Lições Teóricas: {completed_count} de {total_count} Concluídas ({prog_pct:.0f}%)",
            font=theme.get_font(theme.FONT_BODY_BOLD),
            text_color=theme.COLOR_PRIMARY,
        ).pack(anchor="w")

        pbar = ctk.CTkProgressBar(lesson_left, height=8, progress_color=theme.COLOR_PRIMARY)
        pbar.set(prog_pct / 100.0)
        pbar.pack(fill="x", pady=(6, 0))

        right_btns = ctk.CTkFrame(lesson_inner, fg_color="transparent")
        right_btns.pack(side="right", padx=(12, 0))

        goto_theory_btn = ctk.CTkButton(
            right_btns,
            text="Continuar Lições →",
            font=theme.get_font(theme.FONT_BODY_BOLD),
            fg_color=theme.COLOR_PRIMARY,
            hover_color=theme.COLOR_PRIMARY_HOVER,
            height=34,
            corner_radius=theme.RADIUS_MD,
            command=lambda: self.on_navigate("theory"),
        )
        goto_theory_btn.pack(side="left", padx=4)

        reset_prog_btn = ctk.CTkButton(
            right_btns,
            text=t("btn_restart", "↺ Reiniciar"),
            font=theme.get_font(theme.FONT_SMALL_BOLD),
            fg_color="transparent",
            text_color=theme.COLOR_ACCENT_CRIMSON,
            hover_color=theme.COLOR_CRIMSON_BG,
            height=34,
            width=90,
            corner_radius=theme.RADIUS_MD,
            command=self._confirm_reset,
        )
        reset_prog_btn.pack(side="left", padx=4)

        # Metrics bar (XP, Level, Exercises, Accuracy, Streak)
        self.metrics_frame = ctk.CTkFrame(
            self,
            corner_radius=theme.RADIUS_LG,
            fg_color=theme.COLOR_SURFACE,
            border_width=1,
            border_color=theme.COLOR_BORDER,
        )
        self.metrics_frame.pack(fill="x", padx=24, pady=(2, 10))

        lvl = user.level_info
        self._create_metric_item(self.metrics_frame, "Nível do Aluno", f"{lvl['icon']} Nível {user.level}", 0)
        self._create_metric_item(self.metrics_frame, "Pontos de XP", f"{user.xp} XP", 1)
        self._create_metric_item(self.metrics_frame, "Exercícios", f"{user.total_attempts}", 2)
        self._create_metric_item(self.metrics_frame, "Precisão", f"{user.accuracy_rate:.1f}%", 3)
        self._create_metric_item(self.metrics_frame, "Sequência", f"🔥 {user.best_streak}", 4)

        # Adaptive Practice Recommendation Card
        rec = get_recommendation(user)
        rec_card = ctk.CTkFrame(
            self,
            corner_radius=theme.RADIUS_LG,
            fg_color=theme.COLOR_SURFACE,
            border_width=1,
            border_color=theme.COLOR_PRIMARY,
        )
        rec_card.pack(fill="x", padx=24, pady=(0, 10))

        rec_inner = ctk.CTkFrame(rec_card, fg_color="transparent")
        rec_inner.pack(fill="x", padx=18, pady=12)

        rec_left = ctk.CTkFrame(rec_inner, fg_color="transparent")
        rec_left.pack(side="left", fill="x", expand=True)

        ctk.CTkLabel(
            rec_left,
            text=f"🎯 {rec['title']}",
            font=theme.get_font(theme.FONT_SECTION),
            text_color=theme.COLOR_TEXT_PRIMARY,
        ).pack(anchor="w")

        ctk.CTkLabel(
            rec_left,
            text=f"{rec['reason']} • {rec['tip']}",
            font=theme.get_font(theme.FONT_SMALL),
            text_color=theme.COLOR_TEXT_MUTED,
            wraplength=640,
            justify="left",
        ).pack(anchor="w", pady=(2, 0))

        rec_btn = ctk.CTkButton(
            rec_inner,
            text="Praticar Agora →",
            font=theme.get_font(theme.FONT_BODY_BOLD),
            fg_color=theme.COLOR_PRIMARY,
            hover_color=theme.COLOR_PRIMARY_HOVER,
            height=36,
            width=140,
            corner_radius=theme.RADIUS_MD,
            command=lambda r=rec['route']: self.on_navigate(r),
        )
        rec_btn.pack(side="right", padx=(12, 0))

        # Navigation Grid (2 Columns x 4 Rows)
        cards_container = ctk.CTkFrame(self, fg_color="transparent")
        cards_container.pack(fill="both", expand=True, padx=24, pady=(4, 16))
        cards_container.grid_columnconfigure((0, 1), weight=1, uniform="group1")
        cards_container.grid_rowconfigure((0, 1, 2, 3), weight=1, uniform="group1")

        # Card 1: Teoria Musical
        self._create_nav_card(
            cards_container,
            row=0,
            col=0,
            icon="📖",
            title="Módulo de Teoria",
            subtitle=f"{len(LESSON_IDS)} capítulos interativos: física acústica, intervalos, escalas, acordes e harmonia.",
            button_text="Explorar Teoria",
            color_accent=theme.COLOR_ACCENT_SKY,
            target_screen="theory",
        )

        # Card 2: Tocar Repertório
        self._create_nav_card(
            cards_container,
            row=0,
            col=1,
            icon="🎶",
            title="Tocar Repertório",
            subtitle="Toca 24 peças completas com acompanhamento de bateria, teclado do PC ou MIDI USB.",
            button_text="Tocar Músicas",
            color_accent=theme.COLOR_PRIMARY,
            target_screen="practice_song",
        )

        # Card 3: Estúdio de Escalas
        self._create_nav_card(
            cards_container,
            row=1,
            col=0,
            icon="🎼",
            title="Estúdio de Escalas",
            subtitle="Pratica 16 escalas e modos com dedilhação no piano, trastes na viola e bateria.",
            button_text="Praticar Escalas",
            color_accent="#8B5CF6",
            target_screen="practice_scales",
        )

        # Card 4: Instrumento Real
        self._create_nav_card(
            cards_container,
            row=1,
            col=1,
            icon="🎯",
            title="Prática c/ Microfone",
            subtitle="Toca no teu piano ou viola acústica e a app valida notas afinadas ao vivo.",
            button_text="Praticar Instrumento",
            color_accent=theme.COLOR_ACCENT_AMBER,
            target_screen="practice_instrument",
        )

        # Card 5: Lamiré & Afinador
        self._create_nav_card(
            cards_container,
            row=2,
            col=0,
            icon="🎙️",
            title="Lamiré & Afinador",
            subtitle="Deteção de afinação em tempo real pelo microfone e diapasão de 440 Hz.",
            button_text="Abrir Lamiré",
            color_accent=theme.COLOR_SUCCESS,
            target_screen="lamire",
        )

        # Card 6: Leitura de Pauta
        self._create_nav_card(
            cards_container,
            row=2,
            col=1,
            icon="📜",
            title="Leitura de Pauta",
            subtitle="Identifica notas na pauta com Clave de Sol (𝄞) e Clave de Fá (𝄢).",
            button_text="Praticar Pauta",
            color_accent=theme.COLOR_SUCCESS,
            target_screen="practice_staff",
        )

        # Card 7: Treino Auditivo
        self._create_nav_card(
            cards_container,
            row=3,
            col=0,
            icon="🎧",
            title="Treino Auditivo",
            subtitle="Reconhece intervalos melódicos, harmónicos e acordes sintetizados de ouvido.",
            button_text="Treino Auditivo",
            color_accent=theme.COLOR_ACCENT_PURPLE,
            target_screen="practice_ear",
        )

        # Card 8: Exercícios Técnicos
        self._create_nav_card(
            cards_container,
            row=3,
            col=1,
            icon="💪",
            title="Exercícios Técnicos",
            subtitle="Prática deliberada: Hanon, arpejos, spider walks e treino de agilidade/independência.",
            button_text="Treinar Técnica",
            color_accent="#F59E0B",
            target_screen="practice_technique",
        )

        # Card 9: Estatísticas & Alunos
        self._create_nav_card(
            cards_container,
            row=4,
            col=0,
            icon="📊",
            title="Estatísticas & Alunos",
            subtitle="Gráficos de evolução, mapa de atividade, leaderboard e exportação de certificados.",
            button_text="Ver Estatísticas",
            color_accent="#EC4899",
            target_screen="stats",
        )

        # Card 10: Glossário Musical
        self._create_nav_card(
            cards_container,
            row=4,
            col=1,
            icon="📚",
            title="Glossário Musical",
            subtitle="Mais de 130 termos pesquisáveis A-Z com fórmulas, exemplos práticos e áudio.",
            button_text="Abrir Glossário",
            color_accent="#0284C7",
            target_screen="glossary",
        )
        self._create_nav_card(
            cards_container,
            row=5,
            col=0,
            icon="🔄",
            title="Revisão de Hoje",
            subtitle="Sistema de repetição espaçada SM-2: estuda hoje os itens marcados para revisão.",
            button_text="Iniciar Revisão",
            color_accent="#8B5CF6",
            target_screen="daily_review",
        )
        self._create_nav_card(
            cards_container,
            row=5,
            col=1,
            icon="🎛️",
            title="Estúdio de Composição",
            subtitle="Cria ritmos com sequenciador interativo de 16 passos e renderização multi-pista offline.",
            button_text="Compor Ritmos",
            color_accent="#10B981",
            target_screen="compose_studio",
        )

    def _confirm_reset(self):
        user = self.user_manager.current_user
        confirm = messagebox.askyesno(
            "Reiniciar Aprendizagem",
            f"Desejas reiniciar o progresso e lições de {user.username} para começar do início?",
        )
        if confirm:
            self.user_manager.reset_current_user_scores()
            messagebox.showinfo("Sucesso", "O progresso foi reiniciado com sucesso!")
            self._build_ui()

    def _create_metric_item(self, parent, label: str, value: str, col: int):
        item_frame = ctk.CTkFrame(parent, fg_color="transparent")
        item_frame.pack(side="left", expand=True, fill="both", padx=16, pady=12)

        ctk.CTkLabel(
            item_frame,
            text=value,
            font=theme.get_font(theme.FONT_TITLE, size=24),
            text_color=theme.COLOR_PRIMARY,
        ).pack(anchor="center")

        ctk.CTkLabel(
            item_frame,
            text=label,
            font=theme.get_font(theme.FONT_SMALL),
            text_color=theme.COLOR_TEXT_MUTED,
        ).pack(anchor="center", pady=(2, 0))

    def _create_nav_card(
        self,
        parent,
        row: int,
        col: int,
        icon: str,
        title: str,
        subtitle: str,
        button_text: str,
        color_accent: str,
        target_screen: str,
    ):
        card = ctk.CTkFrame(
            parent,
            corner_radius=theme.RADIUS_LG,
            fg_color=theme.COLOR_SURFACE,
            border_width=1,
            border_color=theme.COLOR_BORDER,
        )
        card.grid(row=row, column=col, padx=8, pady=6, sticky="nsew")

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=18, pady=14)

        top_row = ctk.CTkFrame(inner, fg_color="transparent")
        top_row.pack(fill="x")

        icon_lbl = ctk.CTkLabel(
            top_row,
            text=icon,
            font=ctk.CTkFont(size=26),
        )
        icon_lbl.pack(side="left")

        title_lbl = ctk.CTkLabel(
            top_row,
            text=title,
            font=theme.get_font(theme.FONT_SECTION),
            text_color=theme.COLOR_TEXT_PRIMARY,
        )
        title_lbl.pack(side="left", padx=10)

        sub_lbl = ctk.CTkLabel(
            inner,
            text=subtitle,
            font=theme.get_font(theme.FONT_BODY),
            text_color=theme.COLOR_TEXT_MUTED,
            wraplength=340,
            justify="left",
        )
        sub_lbl.pack(fill="x", expand=True, pady=(8, 12), anchor="w")

        btn = ctk.CTkButton(
            inner,
            text=button_text,
            font=theme.get_font(theme.FONT_BODY_BOLD),
            fg_color=color_accent,
            hover_color=theme.COLOR_PRIMARY_HOVER,
            corner_radius=theme.RADIUS_MD,
            height=36,
            command=lambda: self.on_navigate(target_screen),
        )
        btn.pack(fill="x")
