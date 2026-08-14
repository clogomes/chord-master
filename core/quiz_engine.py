"""Quiz engine for music theory and ear training practice exercises."""
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

    @property
    def correct_answer(self) -> str:
        return self.options[self.correct_index]


class QuizEngine:
    """Generates and validates interactive music theory and ear training exercises."""

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

        target_semitones = random.choice(allowed_semitones)
        target_interval = INTERVALS[target_semitones]

        # Choose a comfortable root note between C3 and G4
        root_midi = random.randint(55, 67)
        root_note = Note.from_midi(root_midi)

        play_mode = random.choice(play_modes)
        if play_mode == "melodic_desc":
            top_note = root_note.transpose(target_semitones)
            notes_to_play = [top_note, root_note]
        else:
            top_note = root_note.transpose(target_semitones)
            notes_to_play = [root_note, top_note]

        # Generate distractors
        other_semitones = [st for st in allowed_semitones if st != target_semitones]
        random.shuffle(other_semitones)
        distractors = [INTERVALS[st].name_pt for st in other_semitones[:3]]

        options = distractors + [target_interval.name_pt]
        random.shuffle(options)
        correct_index = options.index(target_interval.name_pt)

        mode_pt = "ascendente" if play_mode == "melodic_asc" else ("descendente" if play_mode == "melodic_desc" else "harmónico (em simultâneo)")
        prompt = f"Ouve as notas tocadas em modo {mode_pt} e identifica o intervalo:"

        explanation = (
            f"Correto! O intervalo é **{target_interval.name_pt}** ({target_interval.short_code}), "
            f"correspondendo a **{target_interval.semitones} semitons**.\n"
            f"💡 Mnemónica: *{target_interval.mnemonic}*.\n"
            f"Notas tocadas: {root_note.pitch} ({root_note.name_pt}) → {top_note.pitch} ({top_note.name_pt})."
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
        """Generates an ear training chord quality exercise."""
        if difficulty == "beginner":
            chord_keys = ["major", "minor"]
        elif difficulty == "intermediate":
            chord_keys = ["major", "minor", "diminished", "augmented"]
        else:
            chord_keys = ["major", "minor", "diminished", "augmented", "dom7", "maj7", "min7"]

        target_key = random.choice(chord_keys)
        target_def = CHORD_TYPES[target_key]

        root_midi = random.randint(53, 65)  # F3 to F4
        root_note = Note.from_midi(root_midi)
        chord = Chord(root_note, target_key)

        other_keys = [k for k in chord_keys if k != target_key]
        if len(other_keys) < 3:
            # Add from full pool if pool is small
            all_other = [k for k in CHORD_TYPES.keys() if k != target_key and k not in other_keys]
            other_keys += all_other

        random.shuffle(other_keys)
        distractors = [CHORD_TYPES[k].name_pt for k in other_keys[:3]]

        options = distractors + [target_def.name_pt]
        random.shuffle(options)
        correct_index = options.index(target_def.name_pt)

        prompt = "Ouve o acorde tocado e identifica a sua qualidade/tipo:"
        notes_str = ", ".join(f"{n.pitch} ({n.name_pt})" for n in chord.notes)

        explanation = (
            f"Correto! O acorde tocado é **{target_def.name_pt}** ({target_def.symbol or 'Maior'}).\n"
            f"Fórmula: {target_def.formula_degrees} ({target_def.formula_intervals}).\n"
            f"Notas: {notes_str}."
        )

        return QuizQuestion(
            question_type=QuestionType.EAR_CHORD,
            prompt_text=prompt,
            category="treino_auditivo",
            options=options,
            correct_index=correct_index,
            explanation=explanation,
            notes_to_play=chord.notes,
            play_mode="chord",
        )

    @staticmethod
    def generate_staff_reading_question(clef: str = "treble", include_accidentals: bool = False) -> QuizQuestion:
        """
        Generates a note identification exercise on the musical staff.
        - treble: C4 to G5 (diatonic or accidental)
        - bass: E2 to C4 (diatonic or accidental)
        """
        diatonic_pitches = ["C", "D", "E", "F", "G", "A", "B"]
        accidental_pitches = ["C#", "D#", "F#", "G#", "A#"] if include_accidentals else []
        all_pitches = diatonic_pitches + accidental_pitches

        if clef == "treble":
            octaves = [4, 5]
            # Valid comfortable treble range: C4 to A5
            valid_notes = [Note(p, oct) for oct in octaves for p in all_pitches if 60 <= Note(p, oct).midi <= 81]
        else:
            octaves = [2, 3]
            # Valid comfortable bass range: E2 to C4
            valid_notes = [Note(p, oct) for oct in octaves for p in all_pitches if 40 <= Note(p, oct).midi <= 60]

        target_note = random.choice(valid_notes)

        # Distractor options from diatonic / relevant pitches
        distractor_pitches = [p for p in diatonic_pitches if p != target_note.letter]
        random.shuffle(distractor_pitches)

        if include_accidentals and target_note.accidental:
            correct_label = f"{target_note.pitch} ({target_note.name_pt})"
            distractor_labels = [
                f"{p}{target_note.accidental} ({NOTE_NAMES_PT.get(p + target_note.accidental, p)})"
                for p in distractor_pitches[:3]
            ]
        else:
            correct_label = f"{target_note.letter} ({target_note.name_pt})"
            distractor_labels = [f"{p} ({NOTE_NAMES_PT[p]})" for p in distractor_pitches[:3]]

        options = distractor_labels + [correct_label]
        random.shuffle(options)
        correct_index = options.index(correct_label)

        clef_pt = "Clave de Sol" if clef == "treble" else "Clave de Fá"
        prompt = f"Identifica a nota exibida na pauta ({clef_pt}):"

        explanation = (
            f"Muito bem! A nota assinalada na {clef_pt} é **{target_note.pitch} ({target_note.name_pt}{target_note.octave})** "
            f"[Frequência: {target_note.frequency:.1f} Hz, MIDI: {target_note.midi}]."
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
    def generate_theory_question() -> QuizQuestion:
        """Generates conceptual music theory questions regarding scales and intervals."""
        q_type = random.choice(["scale_formula", "chord_formula", "interval_semitones"])

        if q_type == "scale_formula":
            key = random.choice(["major", "natural_minor", "harmonic_minor", "major_pentatonic", "minor_pentatonic"])
            scale_def = SCALE_TYPES[key]
            other_defs = [s for k, s in SCALE_TYPES.items() if k != key]
            random.shuffle(other_defs)

            prompt = f"Qual é a fórmula de intervalos da **{scale_def.name_pt}**?"
            correct_label = scale_def.formula_steps
            distractors = [s.formula_steps for s in other_defs[:3]]
            options = distractors + [correct_label]
            random.shuffle(options)
            correct_index = options.index(correct_label)

            explanation = (
                f"Correto! A **{scale_def.name_pt}** é estruturada como:\n"
                f"• Passos: {scale_def.formula_steps}\n"
                f"• Graus: {scale_def.formula_degrees}\n"
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
            notes_to_play = sample_chord.notes

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
