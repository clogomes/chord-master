"""Ecrã de Prática Rítmica (Fase 49).

O Capítulo 9 ensina ritmo (compassos, figuras, síncopa) mas a app não tinha
nenhum exercício que o *praticasse*. Este ecrã fecha essa lacuna:

- O metrónomo toca com uma contagem de 1 compasso de entrada.
- A figura rítmica é desenhada na pauta, com a posição atual destacada.
- O utilizador *bate* com a barra de espaço (ou o botão grande) no tempo certo.
- Cada batida é avaliada por `evaluate_rhythm_accuracy` e mostra o desvio em
  milissegundos + rótulo (o feedback numérico é o que ensina).
- No fim: precisão média, batidas certas/erradas e desvio médio (e, se for
  sistematicamente positivo, avisa que o aluno está a atrasar).
- Regista a competência atómica com `category="ritmo"` (revisão espaçada +
  estatísticas + motor adaptativo).
"""
import time
from typing import Callable, List, Optional, Tuple
import customtkinter as ctk
from core.notes import Note
from core.user_manager import UserManager
from core.rhythm_exercises import RHYTHM_EXERCISES, RhythmPattern_Exercise
from audio.metronome import Metronome, evaluate_rhythm_accuracy
from gui.components.staff_canvas import StaffCanvas
from gui.components.score_card import ScoreCard
from gui.scroll_utils import bind_mousewheel
from gui.i18n import get_language, t
from gui import theme

# Limiar (ms) abaixo do qual uma batida conta como "certa" (rótulos BOM/PERFEITO)
ON_TIME_MS = 220.0
# Fração mínima de batidas certas para a sessão contar como "correta" (SRS grade 5)
PASS_RATIO = 0.6

# Cores da figura rítmica
_COLOR_DONE = "#34D399"     # verde — batidas já dadas
_COLOR_CURRENT = "#F59E0B"  # âmbar — posição a bater
_COLOR_TODO = "#64748B"     # cinza — ainda por vir


class PracticeRhythmScreen(ctk.CTkFrame):
    """Ecrã de prática de ritmo com metrónomo, contagem de entrada e feedback em ms."""

    def __init__(self, master, user_manager: UserManager, on_back: Callable[[], None], **kwargs):
        super().__init__(master, fg_color=theme.COLOR_BG, **kwargs)
        self.user_manager = user_manager
        self.on_back = on_back

        self.current_exercise: RhythmPattern_Exercise = RHYTHM_EXERCISES[0]
        self.current_note_idx: int = 0

        # Metrónomo + rampa de tempo
        self.target_bpm: int = 90
        self.current_ramp_bpm: int = max(40, int(self.target_bpm * 0.70))
        self.tempo_ramp_var = ctk.BooleanVar(value=False)
        self.metronome = Metronome(bpm=self.target_bpm, on_beat=self._on_metronome_beat)

        # Estados da sessão
        self.session_active: bool = False
        self.is_finished: bool = False
        self.counting_in: bool = False
        self._count_beat: int = 0
        self._count_total: int = 4
        self.taps: List[Tuple[str, float, float, int]] = []  # (rótulo, |delta| ms, desvio assinado ms, pontos)
        self._expected_timestamps: List[float] = []
        self._demo_timer: Optional[str] = None
        self._demo_idx: int = 0
        self.is_playing_demo: bool = False

        self._build_ui()
        self._bind_keyboard_events()
        self._load_exercise(self.current_exercise)

    # ── UI ────────────────────────────────────────────────────────────────────
    def _build_ui(self):
        # Barra de navegação
        nav_bar = ctk.CTkFrame(self, fg_color="transparent")
        nav_bar.pack(fill="x", padx=18, pady=(14, 6))
        back_btn = ctk.CTkButton(
            nav_bar,
            text=t("btn_back", "← Voltar ao Menu"),
            font=theme.get_font(theme.FONT_BODY_BOLD),
            fg_color="#475569", hover_color="#334155",
            width=140, height=38, corner_radius=theme.RADIUS_MD,
            command=self._handle_back,
        )
        back_btn.pack(side="left")
        user = self.user_manager.current_user
        title_lbl = ctk.CTkLabel(
            nav_bar,
            text=f"🥁 Prática Rítmica ({user.avatar} {user.username})",
            font=theme.get_font(theme.FONT_TITLE),
            text_color=theme.COLOR_TEXT_PRIMARY,
        )
        title_lbl.pack(side="left", padx=14)

        self.stage_scroll = ctk.CTkScrollableFrame(
            self, corner_radius=theme.RADIUS_LG,
            fg_color=theme.COLOR_BG, border_width=1, border_color=theme.COLOR_BORDER,
        )
        self.stage_scroll.pack(fill="both", expand=True, padx=18, pady=(4, 14))
        bind_mousewheel(self.stage_scroll)

        # Barra de configuração
        cfg_bar = ctk.CTkFrame(
            self.stage_scroll, corner_radius=theme.RADIUS_LG,
            fg_color=theme.COLOR_SURFACE, border_width=1, border_color=theme.COLOR_BORDER,
        )
        cfg_bar.pack(fill="x", padx=6, pady=(0, 10))

        ctk.CTkLabel(cfg_bar, text=t("rhythm_exercise_label", "Padrão:"),
                     font=theme.get_font(theme.FONT_BODY_BOLD),
                     text_color=theme.COLOR_TEXT_PRIMARY).pack(side="left", padx=(14, 4), pady=12)
        self.ex_option = ctk.CTkOptionMenu(
            cfg_bar, values=[e.get_name(get_language()) for e in RHYTHM_EXERCISES],
            command=self._on_exercise_selected, font=theme.get_font(theme.FONT_BODY),
            height=34, corner_radius=theme.RADIUS_SM, width=300,
        )
        self.ex_option.pack(side="left", padx=4)

        self.bpm_lbl = ctk.CTkLabel(cfg_bar, text=f"{self.target_bpm} BPM",
                                    font=theme.get_font(theme.FONT_BODY_BOLD),
                                    text_color=theme.COLOR_PRIMARY, width=80)
        self.bpm_lbl.pack(side="left", padx=8)
        self.bpm_slider = ctk.CTkSlider(cfg_bar, from_=40, to=180, number_of_steps=140,
                                        width=90, command=self._on_bpm_changed)
        self.bpm_slider.set(self.target_bpm)
        self.bpm_slider.pack(side="left", padx=2)

        self.ramp_checkbox = ctk.CTkCheckBox(
            cfg_bar, text="🏎️ Rampa (70%➔100%)", variable=self.tempo_ramp_var,
            command=self._on_tempo_ramp_toggled, font=theme.get_font(theme.FONT_SMALL_BOLD),
        )
        self.ramp_checkbox.pack(side="left", padx=8)

        self.demo_btn = ctk.CTkButton(
            cfg_bar, text="🔊 Ouvir Padrão",
            font=theme.get_font(theme.FONT_BODY_BOLD),
            fg_color=theme.COLOR_PRIMARY, hover_color=theme.COLOR_PRIMARY_HOVER,
            text_color="#FFFFFF", height=34, corner_radius=theme.RADIUS_SM,
            command=self._toggle_demo,
        )
        self.demo_btn.pack(side="left", padx=8)

        self.start_btn = ctk.CTkButton(
            cfg_bar, text="▶ Iniciar Contagem",
            font=theme.get_font(theme.FONT_BODY_BOLD),
            fg_color=theme.COLOR_SUCCESS, hover_color=theme.COLOR_SUCCESS_HOVER,
            text_color="#04231A", height=34, corner_radius=theme.RADIUS_SM,
            command=self._start_count_in,
        )
        self.start_btn.pack(side="right", padx=10)

        # Cartão de informação
        self.info_card = ctk.CTkFrame(
            self.stage_scroll, corner_radius=theme.RADIUS_LG,
            fg_color=theme.COLOR_SURFACE, border_width=1, border_color=theme.COLOR_BORDER,
        )
        self.info_card.pack(fill="x", padx=6, pady=(0, 10))
        info_header = ctk.CTkFrame(self.info_card, fg_color="transparent")
        info_header.pack(fill="x", padx=16, pady=(12, 4))
        self.ex_title_lbl = ctk.CTkLabel(info_header, text="",
                                         font=theme.get_font(theme.FONT_TITLE),
                                         text_color=theme.COLOR_TEXT_PRIMARY)
        self.ex_title_lbl.pack(side="left")
        self.ex_meta_lbl = ctk.CTkLabel(info_header, text="",
                                        font=theme.get_font(theme.FONT_BODY_BOLD),
                                        text_color=theme.COLOR_TEXT_MUTED)
        self.ex_meta_lbl.pack(side="right")
        self.ex_desc_lbl = ctk.CTkLabel(self.info_card, text="",
                                        font=theme.get_font(theme.FONT_BODY),
                                        text_color=theme.COLOR_TEXT_MUTED, wraplength=720, justify="left")
        self.ex_desc_lbl.pack(anchor="w", padx=16, pady=(0, 12))
        self.progress_bar = ctk.CTkProgressBar(self.info_card, height=8,
                                               fg_color=theme.COLOR_SURFACE_SECONDARY,
                                               progress_color=theme.COLOR_PRIMARY)
        self.progress_bar.pack(fill="x", padx=16, pady=(0, 12))

        # Pauta com a figura rítmica
        self.staff_view = StaffCanvas(self.stage_scroll, width=700, height=140)
        self.staff_view.pack(pady=4)

        # Contador / display principal
        self.count_lbl = ctk.CTkLabel(
            self.stage_scroll, text="", font=theme.get_font(theme.FONT_TITLE),
            text_color=theme.COLOR_PRIMARY, height=50,
        )
        self.count_lbl.pack(pady=(4, 2))

        self.feedback_lbl = ctk.CTkLabel(
            self.stage_scroll,
            text=t("rhythm_hint", "Pré-para-te: quando a contagem terminar, bate no tempo certo."),
            font=theme.get_font(theme.FONT_SUBTITLE), text_color=theme.COLOR_TEXT_PRIMARY,
        )
        self.feedback_lbl.pack(pady=8)

        # Botão grande de batida
        self.tap_btn = ctk.CTkButton(
            self.stage_scroll, text=t("rhythm_tap", "👏 BATIR (Espaço)"),
            font=theme.get_font(theme.FONT_TITLE),
            fg_color=theme.COLOR_SURFACE_SECONDARY, hover_color=theme.COLOR_SURFACE_HOVER,
            text_color=theme.COLOR_TEXT_PRIMARY, height=64, corner_radius=theme.RADIUS_LG,
            command=self._on_tap,
        )
        self.tap_btn.pack(fill="x", padx=24, pady=(4, 8))

        self.score_card = ScoreCard(self.stage_scroll, on_next=self._restart)

    # ── Seleção / carregamento ────────────────────────────────────────────────
    def _on_exercise_selected(self, option_name: str):
        lang = get_language()
        for e in RHYTHM_EXERCISES:
            if e.get_name(lang) == option_name:
                self._load_exercise(e)
                break

    def _load_exercise(self, exercise: RhythmPattern_Exercise):
        self._stop_demo()
        self._reset_session()
        self.current_exercise = exercise
        self._count_total = self._beats_per_measure(exercise.time_signature)

        lang = get_language()
        self.ex_title_lbl.configure(text=exercise.get_name(lang))
        self.ex_meta_lbl.configure(
            text=f"Compasso: {exercise.time_signature} • Nível: {exercise.level} • "
                 f"{len(exercise.durations)} batidas"
        )
        self.ex_desc_lbl.configure(text=exercise.get_description(lang))
        self.staff_view.set_time_signature(exercise.time_signature)
        self._render_pattern()

    def _beats_per_measure(self, time_signature: str) -> int:
        try:
            n_val, d_val = time_signature.split("/")
            # 6/8 -> 6 colcheias = 2 tempos de semínima, mas contamos "pulsos" = n_val
            return int(n_val)
        except Exception:
            return 4

    # ── Desenho da figura ─────────────────────────────────────────────────────
    def _render_pattern(self):
        durations = self.current_exercise.durations
        notes = [Note("C4") for _ in durations]
        colors: List[str] = []
        for i in range(len(durations)):
            if i < self.current_note_idx:
                colors.append(_COLOR_DONE)
            elif i == self.current_note_idx:
                colors.append(_COLOR_CURRENT)
            else:
                colors.append(_COLOR_TODO)
        self.staff_view.set_notes(notes, colors, list(durations))
        total = len(durations)
        self.progress_bar.set(self.current_note_idx / float(total) if total else 0.0)

    # ── Contagem de entrada + sessão ──────────────────────────────────────────
    def _reset_session(self):
        self.current_note_idx = 0
        self.taps = []
        self.session_active = False
        self.is_finished = False
        self.counting_in = False
        self._count_beat = 0
        self._expected_timestamps = []
        self.score_card.pack_forget()
        self.count_lbl.configure(text="", text_color=theme.COLOR_PRIMARY)
        self.feedback_lbl.configure(
            text=t("rhythm_hint", "Pré-para-te: quando a contagem terminar, bate no tempo certo."),
            text_color=theme.COLOR_TEXT_PRIMARY,
        )
        self.start_btn.configure(state="normal")
        self._render_pattern()

    def _start_count_in(self):
        if self.counting_in or self.session_active:
            return
        self.counting_in = True
        self._count_beat = 0
        self._count_total = self._beats_per_measure(self.current_exercise.time_signature)
        self.count_lbl.configure(text="…", text_color=theme.COLOR_TEXT_MUTED)
        self.feedback_lbl.configure(text=t("rhythm_countin", "Contagem de entrada..."),
                                    text_color=theme.COLOR_TEXT_MUTED)
        self.start_btn.configure(state="disabled")
        # A contagem de entrada usa o próprio callback do metrónomo: o 1.º compasso
        # é a contagem (1..N), ao fim do qual a sessão começa. O ciclo de tempos do
        # metrónomo tem de bater certo com o compasso do exercício (ex.: 6/8 -> 6).
        self.metronome.set_beats_per_measure(self._count_total)
        self._phase = "count_in"
        self.metronome.start()

    def _on_metronome_beat(self, beat_num: int, timestamp: float = 0.0):
        # Callback chamado pela thread do metrónomo -> saltar para a thread da UI.
        self.after(0, lambda b=beat_num, ts=timestamp: self._handle_beat(b, ts))

    def _handle_beat(self, beat_num: int, ts: float):
        if not hasattr(self, "_phase"):
            return
        if self._phase == "count_in":
            self._count_beat = beat_num
            self.count_lbl.configure(text=str(beat_num), text_color=theme.COLOR_TEXT_MUTED)
            # Fim do compasso de entrada -> começar a sessão e pré-computar os tempos.
            if beat_num == self._count_total:
                self._begin_session(ts)
        elif self._phase == "tapping":
            # Destaque a posição atual à medida que os tempos passam.
            if self.current_note_idx < len(self.current_exercise.durations):
                self._render_pattern()

    def _begin_session(self, start_ts: float):
        bpm = self.metronome.bpm
        beat_dur = 60.0 / bpm
        durations = self.current_exercise.durations
        # A 1.ª batida acontece no próximo pulso do metrónomo (1 intervalo à frente);
        # as seguintes, acumulando as durações a partir daí.
        acc = start_ts + beat_dur
        self._expected_timestamps = []
        for d in durations:
            self._expected_timestamps.append(acc)
            acc += d * beat_dur
        self.current_note_idx = 0
        self.taps = []
        self.session_active = True
        self.counting_in = False
        self._phase = "tapping"
        self.count_lbl.configure(text="👏", text_color=theme.COLOR_PRIMARY)
        self.feedback_lbl.configure(text=t("rhythm_tap_now", "Bate no tempo certo! (Espaço)"),
                                    text_color=theme.COLOR_TEXT_PRIMARY)
        self._render_pattern()

    # ── Batida do utilizador ──────────────────────────────────────────────────
    def _on_tap(self):
        if not self.session_active or self.is_finished:
            return
        idx = self.current_note_idx
        if idx >= len(self._expected_timestamps):
            return
        actual = time.time()
        expected = self._expected_timestamps[idx]
        label, delta_ms, points = evaluate_rhythm_accuracy(expected, actual)
        signed_ms = (actual - expected) * 1000.0  # + = atrasado, - = adiantado
        self.taps.append((label, delta_ms, signed_ms, points))

        # Feedback imediato, numérico e acionável.
        on_time = delta_ms <= ON_TIME_MS
        if on_time:
            self.feedback_lbl.configure(text=f"✓ {label} · {delta_ms:.0f} ms",
                                        text_color=theme.COLOR_SUCCESS)
        else:
            self.feedback_lbl.configure(text=f"⚠ {label} · {delta_ms:.0f} ms",
                                        text_color=theme.COLOR_ACCENT_CRIMSON)

        self.current_note_idx += 1
        if self.current_note_idx >= len(self.current_exercise.durations):
            self._finish_session()
        else:
            self._render_pattern()

    # ── Fim da sessão ─────────────────────────────────────────────────────────
    def _finish_session(self):
        self.session_active = False
        self.is_finished = True
        if self.metronome.is_running:
            self.metronome.stop()
        self.start_btn.configure(state="normal")

        total = len(self.taps)
        on_time = sum(1 for (_, d, _, _) in self.taps if d <= ON_TIME_MS)
        ratio = (on_time / total) if total else 0.0
        avg_abs = (sum(d for (_, d, _, _) in self.taps) / total) if total else 0.0
        avg_signed = (sum(s for (_, _, s, _) in self.taps) / total) if total else 0.0
        is_correct = ratio >= PASS_RATIO

        ramp_msg = ""
        if self.tempo_ramp_var.get() and is_correct and self.current_ramp_bpm < self.target_bpm:
            self.current_ramp_bpm = min(self.target_bpm, int(self.current_ramp_bpm + max(2, self.target_bpm * 0.05)))
            self.bpm_slider.set(self.current_ramp_bpm)
            self._update_bpm_label()
            self.metronome.set_bpm(self.current_ramp_bpm)
            ramp_msg = f"\n🏎️ Rampa avançou para {self.current_ramp_bpm} BPM."

        lang = get_language()
        stats = self.user_manager.record_atomic_review(
            skill_id=f"rhythm:{self.current_exercise.id}",
            is_correct=is_correct,
            category="ritmo",
            question_type="rhythm_pattern",
            prompt=f"Padrão Rítmico: {self.current_exercise.get_name(lang)} ({self.current_exercise.time_signature})",
            user_answer=f"{on_time}/{total} batidas certas · desvio médio {avg_signed:+.0f} ms",
            correct_answer=self.current_exercise.get_name(lang),
        )

        # Desvio sistématico -> orientação explícita (o que ensina).
        if avg_signed > 40:
            tendency = t("rhythm_late", "Estás a bater sistematicamente ATRASADO — tenta antecipares um pouco.")
        elif avg_signed < -40:
            tendency = t("rhythm_early", "Estás a bater sistematicamente ADIANTADO — tenta segurares mais.")
        else:
            tendency = t("rhythm_steady", "Bom equilíbrio: sem tendência clara para atrasar ou adiantar.")

        explanation = (
            f"🥁 {self.current_exercise.get_name(lang)}\n\n"
            f"• {t('rhythm_acc', 'Precisão média')}: {ratio * 100:.0f}% ({on_time}/{total} {t('rhythm_on_time', 'batidas certas')})\n"
            f"• {t('rhythm_avg_abs', 'Desvio médio absoluto')}: {avg_abs:.0f} ms\n"
            f"• {t('rhythm_avg_signed', 'Desvio médio')}: {avg_signed:+.0f} ms\n"
            f"• {tendency}\n"
            f"{ramp_msg}"
        )
        self.progress_bar.set(1.0)
        self.count_lbl.configure(text="✅" if is_correct else "🔁",
                                 text_color=theme.COLOR_SUCCESS if is_correct else theme.COLOR_ACCENT_CRIMSON)
        self.score_card.show_feedback(
            is_correct=is_correct,
            explanation=explanation,
            stats=stats,
            can_replay=True,
        )
        self.score_card.pack(fill="x", padx=6, pady=(12, 10))

    # ── Demo (ouvir o padrão) ─────────────────────────────────────────────────
    def _toggle_demo(self):
        if self.is_playing_demo:
            self._stop_demo()
        else:
            self._stop_demo()
            self.is_playing_demo = True
            self._demo_idx = 0
            self.demo_btn.configure(text="⏹️ Parar", fg_color=theme.COLOR_ACCENT_CRIMSON)
            # Tocar o padrão: cada posição avança conforme a duração, com destaque.
            self._schedule_demo_note()

    def _stop_demo(self):
        if self._demo_timer:
            self.after_cancel(self._demo_timer)
            self._demo_timer = None
        self.is_playing_demo = False
        self._render_pattern()
        if self.demo_btn:
            self.demo_btn.configure(text="🔊 Ouvir Padrão", fg_color=theme.COLOR_PRIMARY)

    def _schedule_demo_note(self):
        if not self.is_playing_demo:
            return
        idx = self._demo_idx
        durations = self.current_exercise.durations
        if idx >= len(durations):
            self._stop_demo()
            return
        # Destacar a posição e avançar conforme a duração real (em ms).
        colors = []
        for i in range(len(durations)):
            if i < idx:
                colors.append(_COLOR_DONE)
            elif i == idx:
                colors.append(_COLOR_CURRENT)
            else:
                colors.append(_COLOR_TODO)
        notes = [Note("C4") for _ in durations]
        self.staff_view.set_notes(notes, colors, list(durations))

        beat_ms = (60.000 / self.metronome.bpm) * durations[idx] * 1000.0
        self._demo_idx = idx + 1
        self._demo_timer = self.after(int(max(120, beat_ms)), self._schedule_demo_note)

    # ── BPM / rampa ───────────────────────────────────────────────────────────
    def _on_bpm_changed(self, val):
        self.target_bpm = int(float(val))
        self.metronome.set_bpm(self.target_bpm)
        self._update_bpm_label()

    def _update_bpm_label(self):
        suffix = " (Rampa)" if self.tempo_ramp_var.get() else ""
        shown = self.current_ramp_bpm if self.tempo_ramp_var.get() else self.target_bpm
        self.bpm_lbl.configure(text=f"{shown} BPM{suffix}")

    def _on_tempo_ramp_toggled(self):
        if self.tempo_ramp_var.get():
            self.current_ramp_bpm = max(40, int(self.target_bpm * 0.70))
            self.bpm_slider.set(self.current_ramp_bpm)
            self.metronome.set_bpm(self.current_ramp_bpm)
        else:
            self.bpm_slider.set(self.target_bpm)
            self.metronome.set_bpm(self.target_bpm)
        self._update_bpm_label()

    def _restart(self):
        self._load_exercise(self.current_exercise)

    # ── Teclado / limpeza ─────────────────────────────────────────────────────
    def _bind_keyboard_events(self):
        self.winfo_toplevel().bind("<space>", self._on_space)

    def _unbind_keyboard_events(self):
        try:
            self.winfo_toplevel().unbind("<space>")
        except Exception:
            pass

    def _on_space(self, event):
        self._on_tap()
        return "break"

    def _handle_back(self):
        self._unbind_keyboard_events()
        self._stop_demo()
        self.metronome.stop()
        self.on_back()

    def destroy(self):
        self._unbind_keyboard_events()
        self._stop_demo()
        self.metronome.stop()
        super().destroy()
