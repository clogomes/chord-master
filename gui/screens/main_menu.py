"""Main Menu screen with personalized user dashboard and module launcher cards."""
from typing import Callable, Optional
import customtkinter as ctk
from core.user_manager import UserManager, LESSON_IDS


class MainMenuScreen(ctk.CTkFrame):
    """Modern home dashboard displaying student progress, lesson completion, and mode launchers."""

    def __init__(
        self,
        master,
        user_manager: UserManager,
        on_navigate: Callable[[str], None],
        on_open_users: Optional[Callable[[], None]] = None,
        **kwargs,
    ):
        super().__init__(master, fg_color=("#F8FAFC", "#0F172A"), **kwargs)
        self.user_manager = user_manager
        self.on_navigate = on_navigate
        self.on_open_users = on_open_users

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
            font=ctk.CTkFont(family="Helvetica", size=26, weight="bold"),
            text_color=("#0F172A", "#F8FAFC"),
        )
        title_label.pack(anchor="w")

        subtitle_label = ctk.CTkLabel(
            left_header,
            text="Bem-vindo ao teu estúdio interativo de teoria musical e prática.",
            font=ctk.CTkFont(family="Helvetica", size=14),
            text_color=("#64748B", "#94A3B8"),
        )
        subtitle_label.pack(anchor="w", pady=(2, 0))

        if self.on_open_users:
            user_btn = ctk.CTkButton(
                header_frame,
                text=f"{user.avatar} Trocar Perfil",
                font=ctk.CTkFont(family="Helvetica", size=12, weight="bold"),
                fg_color="#334155",
                hover_color="#475569",
                height=32,
                command=self.on_open_users,
            )
            user_btn.pack(side="right", padx=(10, 0))

        # Lesson Progress Banner
        lesson_card = ctk.CTkFrame(
            self,
            corner_radius=12,
            fg_color=("#EFF6FF", "#172554"),
            border_width=1,
            border_color=("#BFDBFE", "#1E40AF"),
        )
        lesson_card.pack(fill="x", padx=24, pady=(4, 10))

        lesson_inner = ctk.CTkFrame(lesson_card, fg_color="transparent")
        lesson_inner.pack(fill="x", padx=16, pady=10)

        lesson_left = ctk.CTkFrame(lesson_inner, fg_color="transparent")
        lesson_left.pack(side="left", fill="x", expand=True)

        completed_count = len(user.completed_lessons)
        total_count = len(LESSON_IDS)
        prog_pct = user.lessons_progress_percent

        ctk.CTkLabel(
            lesson_left,
            text=f"🎯 Progresso nas Lições Teóricas: {completed_count} de {total_count} Concluídas ({prog_pct:.0f}%)",
            font=ctk.CTkFont(family="Helvetica", size=13, weight="bold"),
            text_color=("#1E40AF", "#93C5FD"),
        ).pack(anchor="w")

        pbar = ctk.CTkProgressBar(lesson_left, height=7, progress_color="#2563EB")
        pbar.set(prog_pct / 100.0)
        pbar.pack(fill="x", pady=(4, 0))

        goto_theory_btn = ctk.CTkButton(
            lesson_inner,
            text="Continuar Lições →",
            font=ctk.CTkFont(family="Helvetica", size=12, weight="bold"),
            fg_color="#2563EB",
            hover_color="#1D4ED8",
            height=30,
            command=lambda: self.on_navigate("theory"),
        )
        goto_theory_btn.pack(side="right", padx=(12, 0))

        # Metrics bar
        self.metrics_frame = ctk.CTkFrame(
            self,
            corner_radius=12,
            fg_color=("#F8FAFC", "#1E293B"),
            border_width=1,
            border_color=("#E2E8F0", "#334155"),
        )
        self.metrics_frame.pack(fill="x", padx=24, pady=(2, 10))

        self._create_metric_item(self.metrics_frame, "Exercícios Realizados", f"{user.total_attempts}", 0)
        self._create_metric_item(self.metrics_frame, "Taxa de Precisão", f"{user.accuracy_rate:.1f}%", 1)
        self._create_metric_item(self.metrics_frame, "Melhor Sequência", f"🔥 {user.best_streak}", 2)

        # Navigation Grid
        cards_container = ctk.CTkFrame(self, fg_color="transparent")
        cards_container.pack(fill="both", expand=True, padx=24, pady=(4, 16))
        cards_container.grid_columnconfigure((0, 1), weight=1, uniform="group1")
        cards_container.grid_rowconfigure((0, 1), weight=1, uniform="group1")

        # Card 1: Teoria Musical
        self._create_nav_card(
            cards_container,
            row=0,
            col=0,
            icon="📖",
            title="Módulo de Teoria",
            subtitle="Lições interativas de notas, intervalos, escalas e formação de acordes maiores/menores.",
            button_text="Explorar Teoria",
            color_accent="#2563EB",
            target_screen="theory",
        )

        # Card 2: Treino Auditivo
        self._create_nav_card(
            cards_container,
            row=0,
            col=1,
            icon="🎧",
            title="Treino Auditivo",
            subtitle="Ouve intervalos melódicos/harmónicos e acordes sintetizados e adivinha a sua sonoridade.",
            button_text="Iniciar Treino Auditivo",
            color_accent="#7C3AED",
            target_screen="practice_ear",
        )

        # Card 3: Leitura de Pauta
        self._create_nav_card(
            cards_container,
            row=1,
            col=0,
            icon="🎼",
            title="Leitura de Pauta",
            subtitle="Pratica a identificação de notas na pauta musical com Clave de Sol e Clave de Fá.",
            button_text="Praticar Pauta",
            color_accent="#059669",
            target_screen="practice_staff",
        )

        # Card 4: Estatísticas
        self._create_nav_card(
            cards_container,
            row=1,
            col=1,
            icon="📊",
            title="Estatísticas & Histórico",
            subtitle="Acompanha o teu progresso detalhado por categoria, histórico de respostas e líderes.",
            button_text="Ver Estatísticas",
            color_accent="#D97706",
            target_screen="stats",
        )

    def _create_metric_item(self, parent, label: str, value: str, col: int):
        item_frame = ctk.CTkFrame(parent, fg_color="transparent")
        item_frame.pack(side="left", expand=True, fill="both", padx=16, pady=10)

        val_lbl = ctk.CTkLabel(
            item_frame,
            text=value,
            font=ctk.CTkFont(family="Helvetica", size=22, weight="bold"),
            text_color=("#0F172A", "#F8FAFC"),
        )
        val_lbl.pack()

        title_lbl = ctk.CTkLabel(
            item_frame,
            text=label,
            font=ctk.CTkFont(family="Helvetica", size=12),
            text_color=("#64748B", "#94A3B8"),
        )
        title_lbl.pack()

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
            corner_radius=14,
            fg_color=("#F8FAFC", "#1E293B"),
            border_width=1,
            border_color=("#E2E8F0", "#334155"),
        )
        card.grid(row=row, column=col, padx=8, pady=6, sticky="nsew")

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=18, pady=14)

        header = ctk.CTkFrame(inner, fg_color="transparent")
        header.pack(fill="x", pady=(0, 4))

        icon_lbl = ctk.CTkLabel(
            header,
            text=icon,
            font=ctk.CTkFont(family="Helvetica", size=24),
        )
        icon_lbl.pack(side="left", padx=(0, 8))

        title_lbl = ctk.CTkLabel(
            header,
            text=title,
            font=ctk.CTkFont(family="Helvetica", size=17, weight="bold"),
            text_color=("#0F172A", "#F8FAFC"),
        )
        title_lbl.pack(side="left", anchor="w")

        desc_lbl = ctk.CTkLabel(
            inner,
            text=subtitle,
            font=ctk.CTkFont(family="Helvetica", size=12),
            text_color=("#64748B", "#94A3B8"),
            wraplength=340,
            justify="left",
        )
        desc_lbl.pack(anchor="w", expand=True, pady=(2, 10))

        btn = ctk.CTkButton(
            inner,
            text=button_text,
            font=ctk.CTkFont(family="Helvetica", size=13, weight="bold"),
            fg_color=color_accent,
            hover_color=color_accent,
            command=lambda: self.on_navigate(target_screen),
            height=34,
            corner_radius=8,
        )
        btn.pack(fill="x")
