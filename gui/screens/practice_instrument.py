"""Live acoustic instrument practice screen with real-time microphone pitch listening and auto-advance."""
import time
from typing import Callable, Dict, List, Optional
import customtkinter as ctk
from core.notes import Note
from core.scales import Scale
from core.chords import Chord
from core.songs import Song, SONG_LIBRARY, get_song_by_id
from core.user_manager import UserManager
from audio.player import get_audio_player
from audio.pitch_listener import PitchListener
from gui.components.piano_keyboard import PianoKeyboard
from gui.components.staff_canvas import StaffCanvas
from gui.components.guitar_fretboard import GuitarFretboard
from gui.components.score_card import ScoreCard


class PracticeInstrumentScreen(ctk.CTkFrame):
    """
    Live acoustic instrument trainer. Listens to real physical piano or guitar
    through the microphone, evaluates intonation in cents, and advances when sustained.
    """

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
        self.audio_player = get_audio_player()
        self.pitch_listener = PitchListener()

        self.instrument_type: str = "Piano"  # "Piano" ou "Viola"
        self.exercise_type: str = "Escalas"  # "Escalas", "Acordes", "Repertório"

        self.exercise_notes: List[Note] = []
        self.current_note_idx: int = 0
        self.exercise_title: str = ""

        # Note sustain tracking
        self._matched_start_time: Optional[float] = None
        self._sustain_threshold_sec: float = 0.30  # 300 ms required sustain
        self._is_advancing: bool = False
        self.exercise_completed: bool = False

        # Scoring
        self.correct_notes_count: int = 0
        self.total_notes_played: int = 0

        self._build_ui()
        self._setup_default_exercise()

    def _build_ui(self):
        # 1. Top Navigation Bar
        nav_bar = ctk.CTkFrame(self, fg_color="transparent")
        nav_bar.pack(fill="x", padx=18, pady=(14, 6))

        back_btn = ctk.CTkButton(
            nav_bar,
            text="← Voltar ao Menu",
            font=ctk.CTkFont(family="Helvetica", size=13, weight="bold"),
            fg_color="#475569",
            hover_color="#334155",
            width=130,
            command=self._handle_back,
        )
        back_btn.pack(side="left")

        user = self.user_manager.current_user
        title_lbl = ctk.CTkLabel(
            nav_bar,
            text=f"🎙️ Prática com Instrumento Real ({user.avatar} {user.username})",
            font=ctk.CTkFont(family="Helvetica", size=20, weight="bold"),
            text_color=("#0F172A", "#F8FAFC"),
        )
        title_lbl.pack(side="left", padx=14)

        # Microphone Toggle Button on top right
        self.mic_btn = ctk.CTkButton(
            nav_bar,
            text="🎙️ Ativar Microfone",
            font=ctk.CTkFont(family="Helvetica", size=12, weight="bold"),
            fg_color="#059669",
            hover_color="#047857",
            width=160,
            command=self._toggle_microphone,
        )
        self.mic_btn.pack(side="right")

        # 2. Main Scrollable Container
        self.container = ctk.CTkScrollableFrame(
            self,
            corner_radius=12,
            fg_color=("#F8FAFC", "#0F172A"),
            border_width=1,
            border_color=("#E2E8F0", "#334155"),
        )
        self.container.pack(fill="both", expand=True, padx=18, pady=(4, 14))

        # 2.1 Configuration Controls Bar
        cfg_bar = ctk.CTkFrame(
            self.container,
            corner_radius=10,
            fg_color=("#F1F5F9", "#1E293B"),
            border_width=1,
            border_color=("#E2E8F0", "#334155"),
        )
        cfg_bar.pack(fill="x", padx=6, pady=(0, 10))

        # Instrument Selector
        ctk.CTkLabel(cfg_bar, text="Instrumento:", font=ctk.CTkFont(family="Helvetica", size=12, weight="bold")).pack(side="left", padx=(12, 4), pady=10)
        self.inst_select = ctk.CTkOptionMenu(
            cfg_bar,
            values=["🎹 Piano Acústico", "🎸 Viola / Guitarra"],
            command=self._on_instrument_changed,
            width=170,
        )
        self.inst_select.set("🎹 Piano Acústico")
        self.inst_select.pack(side="left", padx=4)

        # Exercise Type
        ctk.CTkLabel(cfg_bar, text="Tipo de Exercício:", font=ctk.CTkFont(family="Helvetica", size=12, weight="bold")).pack(side="left", padx=(14, 4))
        self.exercise_type_select = ctk.CTkOptionMenu(
            cfg_bar,
            values=["Escala Maior de Dó", "Escala Menor de Lá", "Arpejo Dó Maior (C)", "Arpejo Lá Menor (Am)", "Música: Hino à Alegria", "Música: Brilha Estrelinha", "Música: Für Elise"],
            command=self._on_exercise_changed,
            width=230,
        )
        self.exercise_type_select.set("Escala Maior de Dó")
        self.exercise_type_select.pack(side="left", padx=4)

        # Restart exercise button
        restart_btn = ctk.CTkButton(
            cfg_bar,
            text="↺ Reiniciar",
            font=ctk.CTkFont(family="Helvetica", size=12),
            fg_color="#475569",
            hover_color="#334155",
            width=100,
            command=self._restart_exercise,
        )
        restart_btn.pack(side="right", padx=12)

        # 2.2 Live Tuner Gauge / Pitch Display Card
        self.tuner_card = ctk.CTkFrame(
            self.container,
            corner_radius=12,
            fg_color=("#F1F5F9", "#1E293B"),
            border_width=2,
            border_color="#334155",
        )
        self.tuner_card.pack(fill="x", padx=6, pady=(0, 10))

        tuner_grid = ctk.CTkFrame(self.tuner_card, fg_color="transparent")
        tuner_grid.pack(fill="x", padx=16, pady=12)
        tuner_grid.grid_columnconfigure((0, 1), weight=1)

        # Left: Target Note Box
        target_box = ctk.CTkFrame(tuner_grid, corner_radius=10, fg_color=("#E2E8F0", "#0F172A"))
        target_box.grid(row=0, column=0, padx=(0, 8), sticky="nsew")

        ctk.CTkLabel(target_box, text="NOTA ALVO", font=ctk.CTkFont(family="Helvetica", size=11, weight="bold"), text_color=("#64748B", "#94A3B8")).pack(pady=(8, 0))
        self.target_note_lbl = ctk.CTkLabel(target_box, text="C4 (Dó)", font=ctk.CTkFont(family="Helvetica", size=24, weight="bold"), text_color="#3B82F6")
        self.target_note_lbl.pack(pady=(0, 8))

        # Right: Detected Note Box
        detected_box = ctk.CTkFrame(tuner_grid, corner_radius=10, fg_color=("#E2E8F0", "#0F172A"))
        detected_box.grid(row=0, column=1, padx=(8, 0), sticky="nsew")

        ctk.CTkLabel(detected_box, text="MICROFONE / NOTA DETETADA", font=ctk.CTkFont(family="Helvetica", size=11, weight="bold"), text_color=("#64748B", "#94A3B8")).pack(pady=(8, 0))
        self.detected_note_lbl = ctk.CTkLabel(detected_box, text="A aguardar áudio...", font=ctk.CTkFont(family="Helvetica", size=24, weight="bold"), text_color=("#64748B", "#94A3B8"))
        self.detected_note_lbl.pack(pady=(0, 8))

        # Cents offset meter / needle
        meter_frame = ctk.CTkFrame(self.tuner_card, fg_color="transparent")
        meter_frame.pack(fill="x", padx=16, pady=(0, 10))

        self.cents_bar = ctk.CTkProgressBar(meter_frame, height=10, progress_color="#10B981")
        self.cents_bar.set(0.5)  # 0.5 = perfectly in tune
        self.cents_bar.pack(fill="x", pady=4)

        self.intonation_status_lbl = ctk.CTkLabel(
            meter_frame,
            text="Toca a nota no teu instrumento real e o microfone detetará o som automaticamente!",
            font=ctk.CTkFont(family="Helvetica", size=13, weight="bold"),
            text_color=("#475569", "#CBD5E1"),
        )
        self.intonation_status_lbl.pack()

        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(self.container, height=6, progress_color="#2563EB")
        self.progress_bar.set(0.0)
        self.progress_bar.pack(fill="x", padx=6, pady=(0, 8))

        # 2.3 Visualizers
        vis_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        vis_frame.pack(fill="x", padx=6, pady=2)

        # 1. Staff Canvas
        self.staff_view = StaffCanvas(vis_frame, width=650, height=145, clef="treble", show_note_names=True)
        self.staff_view.pack(pady=4)

        # 2. Piano View
        self.piano_view = PianoKeyboard(vis_frame, start_octave=3, num_octaves=2, key_width=42, key_height=125)
        self.piano_view.pack(pady=4)

        # 3. Guitar View
        self.guitar_view = GuitarFretboard(vis_frame, width=650, height=155, num_frets=15)
        # Initially hidden if in Piano mode

        # macOS Microphone permission hint
        hint_card = ctk.CTkFrame(
            self.container,
            corner_radius=10,
            fg_color=("#EFF6FF", "#172554"),
            border_width=1,
            border_color=("#BFDBFE", "#1E40AF"),
        )
        hint_card.pack(fill="x", padx=6, pady=(8, 10))

        ctk.CTkLabel(
            hint_card,
            text="ℹ️ **Como Funciona**: Toca a nota pedida no teu instrumento acústico perto do microfone. Quando a afinação estiver afinada (±25 cents) e sustentada por 0.3s, a aplicação avança automaticamente!",
            font=ctk.CTkFont(family="Helvetica", size=11),
            text_color=("#1E40AF", "#DBEAFE"),
            justify="left",
            wraplength=660,
        ).pack(padx=14, pady=10)

        # Score Card for completion
        self.score_card = ScoreCard(self.container, on_next=self._restart_exercise)

    def _on_instrument_changed(self, choice: str):
        if "Viola" in choice:
            self.instrument_type = "Viola"
            self.piano_view.pack_forget()
            self.guitar_view.pack(pady=4)
        else:
            self.instrument_type = "Piano"
            self.piano_view.pack(pady=4)
            self.guitar_view.pack_forget()
        self._highlight_target_note()

    def _setup_default_exercise(self):
        self._on_exercise_changed(self.exercise_type_select.get())

    def _on_exercise_changed(self, choice: str):
        self.current_note_idx = 0
        self.correct_notes_count = 0
        self.total_notes_played = 0
        self.exercise_completed = False
        self._matched_start_time = None
        self.score_card.pack_forget()

        if "Escala Maior de Dó" in choice:
            scale = Scale(Note("C4"), "major")
            self.exercise_notes = list(scale.notes)
            self.exercise_title = "Escala Maior de Dó"
        elif "Escala Menor de Lá" in choice:
            scale = Scale(Note("A3"), "natural_minor")
            self.exercise_notes = list(scale.notes)
            self.exercise_title = "Escala Menor de Lá"
        elif "Arpejo Dó Maior" in choice:
            chord = Chord(Note("C4"), "major")
            self.exercise_notes = [chord.root, chord.notes[1], chord.notes[2], Note("C5")]
            self.exercise_title = "Arpejo de Dó Maior"
        elif "Arpejo Lá Menor" in choice:
            chord = Chord(Note("A3"), "minor")
            self.exercise_notes = [chord.root, chord.notes[1], chord.notes[2], Note("A4")]
            self.exercise_title = "Arpejo de Lá Menor"
        elif "Hino à Alegria" in choice:
            song = get_song_by_id("ode_to_joy")
            self.exercise_notes = [sn.note for sn in song.notes] if song else [Note("C4")]
            self.exercise_title = "Hino à Alegria"
        elif "Brilha Estrelinha" in choice:
            song = get_song_by_id("twinkle_star")
            self.exercise_notes = [sn.note for sn in song.notes] if song else [Note("C4")]
            self.exercise_title = "Brilha, Brilha Estrelinha"
        elif "Für Elise" in choice:
            song = get_song_by_id("fur_elise")
            self.exercise_notes = [sn.note for sn in song.notes] if song else [Note("C4")]
            self.exercise_title = "Für Elise"
        else:
            self.exercise_notes = [Note("C4"), Note("D4"), Note("E4"), Note("F4"), Note("G4")]
            self.exercise_title = "Exercício Livre"

        self._highlight_target_note()

    def _highlight_target_note(self):
        if not self.exercise_notes:
            return

        total = len(self.exercise_notes)
        idx = min(self.current_note_idx, total - 1)
        target = self.exercise_notes[idx]

        self.progress_bar.set(idx / float(total) if total > 0 else 0.0)
        self.target_note_lbl.configure(text=f"{target.pitch}{target.octave} ({target.name_pt})")

        # 1. Staff
        self.staff_view.set_single_note(target, color="#3B82F6")

        # 2. Piano
        if self.instrument_type == "Piano":
            self.piano_view.highlight_notes([target], color="#3B82F6")
            self.piano_view.set_fingering({target.midi: 1})

        # 3. Guitar
        if self.instrument_type == "Viola":
            self.guitar_view.highlight_scale([target])

    def _toggle_microphone(self):
        if self.pitch_listener.is_listening:
            self.pitch_listener.stop_listening()
            self.mic_btn.configure(
                text="🎙️ Ativar Microfone",
                fg_color="#059669",
                hover_color="#047857",
            )
            self.detected_note_lbl.configure(text="Microfone desligado", text_color=("#64748B", "#94A3B8"))
        else:
            started = self.pitch_listener.start_listening(self._on_live_audio_block)
            if started:
                self.mic_btn.configure(
                    text="⏹️ Desativar Microfone",
                    fg_color="#DC2626",
                    hover_color="#B91C1C",
                )
                self.detected_note_lbl.configure(text="A ouvir...", text_color="#38BDF8")
            else:
                self.detected_note_lbl.configure(text="Erro ao aceder ao microfone", text_color="#EF4444")

    def _on_live_audio_block(
        self,
        detected_note: Optional[Note],
        cents: float,
        conf: float,
        f0: float,
    ):
        """Threaded callback from sounddevice audio stream."""
        # Schedule GUI updates on main Tkinter thread safely
        if self.winfo_exists():
            self.after(0, lambda: self._process_pitch_on_gui(detected_note, cents, conf, f0))

    def _process_pitch_on_gui(
        self,
        detected_note: Optional[Note],
        cents: float,
        conf: float,
        f0: float,
    ):
        if not self.winfo_exists() or self.exercise_completed:
            return

        if detected_note is None:
            self._matched_start_time = None
            return

        # Display detected note text
        cents_str = f"{cents:+.0f}c" if abs(cents) >= 1.0 else "0c"
        self.detected_note_lbl.configure(
            text=f"{detected_note.pitch}{detected_note.octave} ({cents_str})",
            text_color="#10B981" if abs(cents) <= 25 else "#F59E0B",
        )

        # Update progress bar position (0.0 = -50 cents, 0.5 = 0 cents, 1.0 = +50 cents)
        normalized_cents = max(-50.0, min(50.0, cents))
        meter_val = (normalized_cents + 50.0) / 100.0
        self.cents_bar.set(meter_val)

        target_note = self.exercise_notes[self.current_note_idx]

        # Check if detected note matches target note pitch class
        if detected_note.normalized_pitch == target_note.normalized_pitch:
            if abs(cents) <= 25.0:
                self.intonation_status_lbl.configure(
                    text="✓ Excelente afinação! Sustenta a nota...",
                    text_color="#10B981",
                )
                self.tuner_card.configure(border_color="#10B981")

                now = time.time()
                if self._matched_start_time is None:
                    self._matched_start_time = now
                elif (now - self._matched_start_time) >= self._sustain_threshold_sec and not self._is_advancing:
                    self._advance_to_next_target_note()
            elif cents < -25.0:
                self.intonation_status_lbl.configure(
                    text="▲ Toca ligeiramente mais agudo",
                    text_color="#F59E0B",
                )
                self.tuner_card.configure(border_color="#F59E0B")
                self._matched_start_time = None
            else:
                self.intonation_status_lbl.configure(
                    text="▼ Toca ligeiramente mais grave",
                    text_color="#F59E0B",
                )
                self.tuner_card.configure(border_color="#F59E0B")
                self._matched_start_time = None
        else:
            self.intonation_status_lbl.configure(
                text=f"Nota incorreta (detetado {detected_note.pitch}, esperado {target_note.pitch})",
                text_color="#EF4444",
            )
            self.tuner_card.configure(border_color="#EF4444")
            self._matched_start_time = None

    def _advance_to_next_target_note(self):
        self._is_advancing = True
        self.correct_notes_count += 1
        self.total_notes_played += 1

        # Small pleasant chime feedback
        self.audio_player.play_note(self.exercise_notes[self.current_note_idx], duration=0.4)

        if self.current_note_idx < len(self.exercise_notes) - 1:
            self.current_note_idx += 1
            self._highlight_target_note()
            self._matched_start_time = None
            self._is_advancing = False
        else:
            self._finish_acoustic_exercise()

    def _finish_acoustic_exercise(self):
        self.exercise_completed = True
        self.progress_bar.set(1.0)
        self.pitch_listener.stop_listening()
        self.mic_btn.configure(text="🎙️ Ativar Microfone", fg_color="#059669")

        accuracy = 100.0
        stats = self.user_manager.record_attempt(
            category="pratica_instrumento",
            question_type="acoustic_pitch",
            is_correct=True,
            prompt=f"Exercício: {self.exercise_title}",
            user_answer=f"{self.correct_notes_count}/{len(self.exercise_notes)} notas afinadas",
            correct_answer=self.exercise_title,
        )

        self.intonation_status_lbl.configure(
            text=f"🎉 Parabéns! Completaste «{self.exercise_title}» com o teu instrumento real!",
            text_color="#10B981",
        )

        self.score_card.show_feedback(
            is_correct=True,
            explanation=f"Excelente desempenho acústico no {self.instrument_type}! Tocaste e afinaste todas as {len(self.exercise_notes)} notas com sucesso.",
            stats=stats,
            can_replay=True,
        )
        self.score_card.pack(fill="x", padx=6, pady=(12, 10))

    def _restart_exercise(self):
        self.current_note_idx = 0
        self.correct_notes_count = 0
        self.total_notes_played = 0
        self.exercise_completed = False
        self._matched_start_time = None
        self._is_advancing = False
        self.score_card.pack_forget()
        self.tuner_card.configure(border_color="#334155")
        self.intonation_status_lbl.configure(
            text="Toca a nota no teu instrumento real e o microfone detetará o som automaticamente!",
            text_color=("#475569", "#CBD5E1"),
        )
        self._highlight_target_note()

    def _handle_back(self):
        self.pitch_listener.stop_listening()
        self.audio_player.stop_all()
        self.on_back()
