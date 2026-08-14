"""Quiz engine for music theory, ear training, sight reading, and solfege singing exercises."""
import random
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Tuple
from .notes import Note, NOTE_NAMES, NOTE_NAMES_PT
from .intervals import INTERVALS, Interval, get_interval
from .scales import SCALE_TYPES, Scale
from .chords import CHORD_TYPES, Chord


class QuestionType(Enum):
    EAR_INTERVAL = "ear_interval"
    EAR_CHORD = "ear_chord"
    STAFF_NOTE = "staff_note"
    THEORY_INTERVAL = "theory_interval"
    THEORY_SCALE = "theory_scale"
    THEORY_CHORD = "theory_chord"
    SOLFEGE_SING = "solfege_sing"


@dataclass
class QuizQuestion:
    """Represents a single quiz question with musical context and options."""
    question_type: QuestionType
    prompt_text: str
    category: str
    options: List[str]
    correct_index: int
    explanation: str
    notes_to_play: List[Note] = field(default_factory=list)
    play_mode: str = "melodic_asc"  # "melodic_asc", "melodic_desc", "harmonic", "chord"
    staff_note: Optional[Note] = None
    clef: str = "treble"  # "treble" or "bass"
    target_note: Optional[Note] = None
    reference_note: Optional[Note] = None

    @property
    def correct_answer(self) -> str:
        return self.options[self.correct_index]


class QuizEngine:
    """Generates and validates interactive music theory, ear training, and solfege exercises."""

    @staticmethod
    def generate_ear_interval_question(difficulty: str = "beginner") -> QuizQuestion:
        """
        Generates an ear training interval exercise.
        - beginner: 2ª Maior, 3ª Menor, 3ª Maior, 4ª Justa, 5ª Justa, 8ª Justa
        - intermediate: All diatonic intervals + 2ª Menor + 7ªs
        - advanced: All intervals including Tritone, 6ª Menor, 7ª Maior, harmonic playback
        """
        if difficulty == "beginner":
            allowed_semitones = [2, 3, 4, 5, 7, 12]
            play_modes = ["melodic_asc"]
        elif difficulty == "intermediate":
            allowed_semitones = [1, 2, 3, 4, 5, 7, 9, 10, 12]
            play_modes = ["melodic_asc", "melodic_desc"]
        else:
            allowed_semitones = list(range(1, 13))
            play_modes = ["melodic_asc", "melodic_desc", "harmonic"]

        target_st = random.choice(allowed_semitones)
        target_interval = INTERVALS[target_st]

        # Pick a random base root note (between C3 and G4)
        root_midi = random.randint(48, 67)
        root_note = Note.from_midi(root_midi)

        play_mode = random.choice(play_modes)
        if play_mode == "melodic_desc":
            second_note = root_note
            first_note = root_note.transpose(target_st)
            notes_to_play = [first_note, second_note]
        else:
            second_note = root_note.transpose(target_st)
            notes_to_play = [root_note, second_note]

        # Generate 4 unique options
        other_intervals = [i for i in INTERVALS.values() if i.semitones != target_st and i.semitones in allowed_semitones]
        if len(other_intervals) < 3:
            other_intervals = [i for i in INTERVALS.values() if i.semitones != target_st]
        random.shuffle(other_intervals)

        distractors = [f"{i.name_pt} ({i.short_code})" for i in other_intervals[:3]]
        correct_label = f"{target_interval.name_pt} ({target_interval.short_code})"
        options = distractors + [correct_label]
        random.shuffle(options)
        correct_index = options.index(correct_label)

        direction_str = "descendente" if play_mode == "melodic_desc" else ("harmónico (simultâneo)" if play_mode == "harmonic" else "ascendente")
        prompt = f"Ouve o intervalo musical {direction_str} e identifica a sua classificação:"
        explanation = (
            f"Correto! O intervalo tocado é uma **{target_interval.name_pt}** ({target_interval.short_code}), "
            f"correspondendo a **{target_interval.semitones} semitons**.\n"
            f"💡 Mnemónica: Lembra-te do início da canção «{target_interval.mnemonic}»."
        )

        return QuizQuestion(
            question_type=QuestionType.EAR_INTERVAL,
            prompt_text=prompt,
            category="treino_auditivo",
            options=options,
            correct_index=correct_index,
            explanation=explanation,
            notes_to_play=notes_to_play,
            play_mode=play_mode,
        )

    @staticmethod
    def generate_ear_chord_question(difficulty: str = "beginner") -> QuizQuestion:
        """
        Generates an ear training chord quality exercise.
        - beginner: Maior, Menor
        - intermediate: Maior, Menor, Diminuto, Aumentado
        - advanced: Maior, Menor, Diminuto, Aumentado, Sétima Dominante (7), Sétima Maior (maj7)
        """
        if difficulty == "beginner":
            allowed_chords = ["major", "minor"]
        elif difficulty == "intermediate":
            allowed_chords = ["major", "minor", "diminished", "augmented"]
        else:
            allowed_chords = ["major", "minor", "diminished", "augmented", "dom7", "maj7"]

        target_type_key = random.choice(allowed_chords)
        target_chord_def = CHORD_TYPES[target_type_key]

        # Root between C3 and F4
        root_midi = random.randint(48, 65)
        root_note = Note.from_midi(root_midi)
        chord_obj = Chord(root_note, target_type_key)

        # Distractor options from all available chord types to ensure 4 options
        other_keys = [k for k in CHORD_TYPES.keys() if k != target_type_key]
        random.shuffle(other_keys)
        distractor_keys = other_keys[:3]
        distractors = [CHORD_TYPES[k].name_pt for k in distractor_keys]

        correct_label = target_chord_def.name_pt
        options = distractors + [correct_label]
        random.shuffle(options)
        correct_index = options.index(correct_label)

        prompt = "Ouve o acorde tocado e identifica a sua qualidade harmónica:"
        explanation = (
            f"Correto! O acorde tocado é um acorde **{target_chord_def.name_pt}** "
            f"({target_chord_def.symbol or 'M'}).\n"
            f"Fórmula: {target_chord_def.formula_intervals} ({target_chord_def.description})."
        )

        return QuizQuestion(
            question_type=QuestionType.EAR_CHORD,
            prompt_text=prompt,
            category="treino_auditivo",
            options=options,
            correct_index=correct_index,
            explanation=explanation,
            notes_to_play=chord_obj.notes,
            play_mode="chord",
        )

    @staticmethod
    def generate_staff_reading_question(
        clef: str = "treble",
        include_accidentals: bool = False,
        difficulty: str = "beginner",
    ) -> QuizQuestion:
        diff = "advanced" if include_accidentals else difficulty
        return QuizEngine.generate_staff_question(clef=clef, difficulty=diff)

    @staticmethod
    def generate_staff_question(
        clef: str = "treble",
        difficulty: str = "beginner",
    ) -> QuizQuestion:
        """
        Generates a sheet music reading exercise.
        - beginner: Natural diatonic notes within the 5 main staff lines
        - intermediate: Includes ledger lines (linhas suplementares)
        - advanced: Includes accidentals (sustenidos e bemóis)
        """
        if clef == "treble":
            if difficulty == "beginner":
                # E4 to F5 (Within staff lines)
                midi_range = [64, 65, 67, 69, 71, 72, 74, 76, 77]
            elif difficulty == "intermediate":
                # C4 to A5 (with ledger lines)
                midi_range = [60, 62, 64, 65, 67, 69, 71, 72, 74, 76, 77, 79, 81]
            else:
                # With chromatic accidentals
                midi_range = list(range(60, 82))
        else:  # Bass clef
            if difficulty == "beginner":
                # G2 to A3 (Within staff lines)
                midi_range = [43, 45, 47, 48, 50, 52, 53, 55, 57]
            elif difficulty == "intermediate":
                # E2 to C4
                midi_range = [40, 41, 43, 45, 47, 48, 50, 52, 53, 55, 57, 59, 60]
            else:
                midi_range = list(range(40, 61))

        target_midi = random.choice(midi_range)
        target_note = Note.from_midi(target_midi)

        # Distractor options
        all_possible_pitches = list(NOTE_NAMES)
        distractors_pitches = [p for p in all_possible_pitches if p != target_note.pitch]
        random.shuffle(distractors_pitches)

        correct_label = f"{target_note.name_pt} ({target_note.pitch})"
        distractor_labels = [f"{NOTE_NAMES_PT[p]} ({p})" for p in distractors_pitches[:3]]

        options = distractor_labels + [correct_label]
        random.shuffle(options)
        correct_index = options.index(correct_label)

        clef_name = "Clave de Sol" if clef == "treble" else "Clave de Fá"
        prompt = f"Identifica a nota desenhada na pauta na **{clef_name}**:"
        explanation = (
            f"Correto! A nota na pauta é **{target_note.name_pt}** ({target_note.pitch}{target_note.octave}), "
            f"com frequência de **{target_note.frequency:.1f} Hz** (MIDI {target_note.midi})."
        )

        return QuizQuestion(
            question_type=QuestionType.STAFF_NOTE,
            prompt_text=prompt,
            category="leitura_pauta",
            options=options,
            correct_index=correct_index,
            explanation=explanation,
            notes_to_play=[target_note],
            play_mode="melodic_asc",
            staff_note=target_note,
            clef=clef,
        )

    @staticmethod
    def generate_solfege_sing_question(difficulty: str = "beginner") -> QuizQuestion:
        """
        Generates a vocal Solfège Dictation exercise validated via real-time microphone pitch detection.
        - beginner: Natural diatonic notes (C, D, E, F, G, A, B) with C4 reference pitch.
        - intermediate: Chromatic notes and larger melodic jumps from reference.
        - advanced: Challenging vocal intervals, sharps/flats, octave shifts.
        """
        ref_note = Note("C4")  # Reference Dó Central (261.6 Hz)

        if difficulty == "beginner":
            # Natural notes in C major scale
            pool = [Note("C4"), Note("D4"), Note("E4"), Note("F4"), Note("G4"), Note("A4"), Note("B4")]
        elif difficulty == "intermediate":
            # Chromatic notes or 3rd/5th jumps
            pool = [
                Note("C#4"), Note("D#4"), Note("F#4"), Note("G#4"), Note("A#4"),
                Note("E4"), Note("G4"), Note("A4"), Note("C5"),
            ]
        else:
            # Extended vocal range
            pool = [
                Note("G3"), Note("A3"), Note("B3"), Note("C4"), Note("C#4"), Note("D4"),
                Note("E4"), Note("F4"), Note("F#4"), Note("G4"), Note("A4"), Note("B4"), Note("C5"), Note("D5")
            ]

        target_note = random.choice(pool)

        # Options for UI fallback/selection
        other_notes = [n for n in pool if n.normalized_pitch != target_note.normalized_pitch]
        if len(other_notes) < 3:
            other_notes = [Note(p + "4") for p in ["C", "D", "E", "F", "G", "A", "B"] if p != target_note.pitch]
        random.shuffle(other_notes)

        correct_label = f"{target_note.name_pt} ({target_note.pitch}{target_note.octave})"
        distractor_labels = [f"{n.name_pt} ({n.pitch}{n.octave})" for n in other_notes[:3]]
        options = distractor_labels + [correct_label]
        random.shuffle(options)
        correct_index = options.index(correct_label)

        prompt = f"🎤 Ditado de Solfejo: Canta a nota **{target_note.name_pt}** ({target_note.pitch}{target_note.octave})"
        explanation = (
            f"Excelente! Cantaste afinado a nota **{target_note.name_pt}** ({target_note.pitch}{target_note.octave}), "
            f"com frequência fundamental de **{target_note.frequency:.1f} Hz**."
        )

        return QuizQuestion(
            question_type=QuestionType.SOLFEGE_SING,
            prompt_text=prompt,
            category="treino_auditivo",
            options=options,
            correct_index=correct_index,
            explanation=explanation,
            notes_to_play=[ref_note],
            play_mode="melodic_asc",
            target_note=target_note,
            reference_note=ref_note,
            staff_note=target_note,
        )

    @staticmethod
    def generate_theory_question(topic: str = "mixed") -> QuizQuestion:
        """Generates a multiple-choice music theory conceptual exercise."""
        topics = ["scale_formula", "chord_formula", "interval_semitones"]
        q_type = random.choice(topics) if topic == "mixed" else topic

        if q_type == "scale_formula":
            key = random.choice(["major", "natural_minor", "harmonic_minor", "pentatonic_major", "dorian"])
            scale_def = SCALE_TYPES[key]
            other_defs = [s for k, s in SCALE_TYPES.items() if k != key]
            random.shuffle(other_defs)

            prompt = f"Qual é o padrão de intervalos (Tons e Semitons) da **{scale_def.name_pt}**?"
            correct_label = scale_def.formula_steps
            distractors = [s.formula_steps for s in other_defs[:3]]
            options = distractors + [correct_label]
            random.shuffle(options)
            correct_index = options.index(correct_label)

            explanation = (
                f"Correto! A **{scale_def.name_pt}** é construída com a fórmula de passos: "
                f"**{scale_def.formula_steps}** (onde T=Tom e S=Semi-tom).\n"
                f"Descrição: {scale_def.description}"
            )
            sample_scale = Scale(Note("C", 4), key)
            notes_to_play = sample_scale.notes

        elif q_type == "chord_formula":
            key = random.choice(["major", "minor", "diminished", "augmented", "dom7", "maj7"])
            chord_def = CHORD_TYPES[key]
            other_defs = [c for k, c in CHORD_TYPES.items() if k != key]
            random.shuffle(other_defs)

            prompt = f"Como é formada a **{chord_def.name_pt}**?"
            correct_label = chord_def.formula_intervals
            distractors = [c.formula_intervals for c in other_defs[:3]]
            options = distractors + [correct_label]
            random.shuffle(options)
            correct_index = options.index(correct_label)

            explanation = (
                f"Correto! A **{chord_def.name_pt}** ({chord_def.symbol or 'Maior'}) tem a fórmula de graus "
                f"**{chord_def.formula_degrees}** e intervalos: {chord_def.formula_intervals}.\n"
                f"Descrição: {chord_def.description}"
            )
            sample_chord = Chord(Note("C", 4), key)
            notes_to_play = chord_obj_notes = sample_chord.notes

        else:  # interval_semitones
            st = random.randint(1, 12)
            interval = INTERVALS[st]
            other_intervals = [i for i in INTERVALS.values() if i.semitones != st]
            random.shuffle(other_intervals)

            prompt = f"Quantos semitons existem no intervalo de **{interval.name_pt}** ({interval.short_code})?"
            correct_label = f"{interval.semitones} semitons"
            distractors = [f"{i.semitones} semitons" for i in other_intervals[:3]]
            options = distractors + [correct_label]
            random.shuffle(options)
            correct_index = options.index(correct_label)

            explanation = (
                f"Correto! O intervalo de **{interval.name_pt}** possui **{interval.semitones} semitons**.\n"
                f"💡 Mnemónica auditiva: {interval.mnemonic}."
            )
            root = Note("C", 4)
            notes_to_play = [root, root.transpose(st)]

        return QuizQuestion(
            question_type=QuestionType.THEORY_SCALE,
            prompt_text=prompt,
            category="teoria",
            options=options,
            correct_index=correct_index,
            explanation=explanation,
            notes_to_play=notes_to_play,
            play_mode="melodic_asc",
        )
