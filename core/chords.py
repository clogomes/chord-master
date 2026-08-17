"""Music theory representation of chords, triads, tetrads and their inversions."""
from dataclasses import dataclass
from typing import Dict, List, Optional
from .notes import Note


@dataclass(frozen=True)
class ChordDefinition:
    """Defines the formula and interval composition of a chord."""
    key: str
    symbol: str
    name_pt: str
    name_en: str
    intervals: List[int]      # Semitones from root
    formula_degrees: str     # e.g., "1 - 3 - 5"
    formula_intervals: str   # e.g., "Tónica + 3ª Maior + 5ª Justa"
    description: str


CHORD_TYPES: Dict[str, ChordDefinition] = {
    "major": ChordDefinition(
        key="major",
        symbol="",
        name_pt="Tríade Maior",
        name_en="Major Triad",
        intervals=[0, 4, 7],
        formula_degrees="1 - 3 - 5",
        formula_intervals="Tónica + Terça Maior (4 st) + Quinta Justa (7 st)",
        description="Acorde fundamental da harmonia tonal. Tem sonoridade aberta, alegre, estável e conclusiva."
    ),
    "minor": ChordDefinition(
        key="minor",
        symbol="m",
        name_pt="Tríade Menor",
        name_en="Minor Triad",
        intervals=[0, 3, 7],
        formula_degrees="1 - ♭3 - 5",
        formula_intervals="Tónica + Terça Menor (3 st) + Quinta Justa (7 st)",
        description="A terça menor confere a este acorde um caráter melancólico, introspectivo e emotivo."
    ),
    "diminished": ChordDefinition(
        key="diminished",
        symbol="dim",
        name_pt="Tríade Diminuta",
        name_en="Diminished Triad",
        intervals=[0, 3, 6],
        formula_degrees="1 - ♭3 - ♭5",
        formula_intervals="Tónica + Terça Menor (3 st) + Quinta Diminuta (6 st)",
        description="Composto por duas terças menores sobrepostas gerando um trítono. Soa instável e tenso, pedindo resolução."
    ),
    "augmented": ChordDefinition(
        key="augmented",
        symbol="aug",
        name_pt="Tríade Aumentada",
        name_en="Augmented Triad",
        intervals=[0, 4, 8],
        formula_degrees="1 - 3 - ♯5",
        formula_intervals="Tónica + Terça Maior (4 st) + Quinta Aumentada (8 st)",
        description="Composto por duas terças maiores sobrepostas. Soa misterioso, suspenso e sonhador."
    ),
    "sus4": ChordDefinition(
        key="sus4",
        symbol="sus4",
        name_pt="Acorde Suspenso 4",
        name_en="Suspended 4th",
        intervals=[0, 5, 7],
        formula_degrees="1 - 4 - 5",
        formula_intervals="Tónica + Quarta Justa (5 st) + Quinta Justa (7 st)",
        description="Substitui a terça pela quarta. Cria uma forte sensação de expectativa para resolver na terça maior."
    ),
    "sus2": ChordDefinition(
        key="sus2",
        symbol="sus2",
        name_pt="Acorde Suspenso 2",
        name_en="Suspended 2nd",
        intervals=[0, 2, 7],
        formula_degrees="1 - 2 - 5",
        formula_intervals="Tónica + Segunda Maior (2 st) + Quinta Justa (7 st)",
        description="Substitui a terça pela segunda maior. Tem uma sonoridade aberta, suave e moderna."
    ),
    "dom7": ChordDefinition(
        key="dom7",
        symbol="7",
        name_pt="Sétima da Dominante",
        name_en="Dominant 7th",
        intervals=[0, 4, 7, 10],
        formula_degrees="1 - 3 - 5 - ♭7",
        formula_intervals="Tríade Maior + Sétima Menor (10 st)",
        description="O motor harmónico do sistema tonal e do blues. Contém o trítono entre a 3ª e a 7ª, criando forte atração para o acorde de tónica."
    ),
    "maj7": ChordDefinition(
        key="maj7",
        symbol="maj7",
        name_pt="Maior com Sétima Maior",
        name_en="Major 7th",
        intervals=[0, 4, 7, 11],
        formula_degrees="1 - 3 - 5 - 7",
        formula_intervals="Tríade Maior + Sétima Maior (11 st)",
        description="Acorde exuberante, suave e sofisticado, muito característico do Jazz, Bossa Nova e Neo-Soul."
    ),
    "min7": ChordDefinition(
        key="min7",
        symbol="m7",
        name_pt="Menor com Sétima",
        name_en="Minor 7th",
        intervals=[0, 3, 7, 10],
        formula_degrees="1 - ♭3 - 5 - ♭7",
        formula_intervals="Tríade Menor + Sétima Menor (10 st)",
        description="Acorde elegante e suave, muito usado como grau ii em progressões ii-V-I."
    ),
    "m7b5": ChordDefinition(
        key="m7b5",
        symbol="m7(♭5)",
        name_pt="Meio-Diminuto (m7♭5)",
        name_en="Half-Diminished 7th",
        intervals=[0, 3, 6, 10],
        formula_degrees="1 - ♭3 - ♭5 - ♭7",
        formula_intervals="Tríade Diminuta + Sétima Menor (10 st)",
        description="O acorde de ii grau no modo menor. Soa sombrio, rico e conduz fortemente para o V grau dominante."
    ),
    "dim7": ChordDefinition(
        key="dim7",
        symbol="dim7",
        name_pt="Sétima Diminuta",
        name_en="Diminished 7th",
        intervals=[0, 3, 6, 9],
        formula_degrees="1 - ♭3 - ♭5 - ♭♭7",
        formula_intervals="Tríade Diminuta + Sétima Diminuta (9 st)",
        description="Acorde perfeitamente simétrico formado por 4 terças menores consecutivas. Altamente dramático e com multi-possibilidades modulatórias."
    ),
    "power": ChordDefinition(
        key="power",
        symbol="5",
        name_pt="Power Chord (Quinta)",
        name_en="Power Chord (5th)",
        intervals=[0, 7],
        formula_degrees="1 - 5",
        formula_intervals="Tónica + Quinta Justa (7 st)",
        description="Bidiade sem terça, neutra entre maior e menor. O pilar do Rock, Hard Rock e Heavy Metal, perfeito para distorção."
    ),
    "6": ChordDefinition(
        key="6",
        symbol="6",
        name_pt="Maior com Sexta",
        name_en="Major 6th",
        intervals=[0, 4, 7, 9],
        formula_degrees="1 - 3 - 5 - 6",
        formula_intervals="Tríade Maior + Sexta Maior (9 st)",
        description="Acorde clássico de Swing, Jazz e Bossa Nova, oferecendo uma resolução suave e luminosa sem a tensão da sétima maior."
    ),
    "m6": ChordDefinition(
        key="m6",
        symbol="m6",
        name_pt="Menor com Sexta",
        name_en="Minor 6th",
        intervals=[0, 3, 7, 9],
        formula_degrees="1 - ♭3 - 5 - 6",
        formula_intervals="Tríade Menor + Sexta Maior (9 st)",
        description="Sonoridade Dórica rica, muito presente no Jazz tradicional e na música de cinema noir / espionagem."
    ),
    "add9": ChordDefinition(
        key="add9",
        symbol="add9",
        name_pt="Maior com Nona Adicionada (add9)",
        name_en="Major Added 9th (add9)",
        intervals=[0, 4, 7, 14],
        formula_degrees="1 - 3 - 5 - 9",
        formula_intervals="Tríade Maior + Nona Maior (14 st)",
        description="Tríade maior com uma 9ª sobreposta (sem a 7ª). Extremamente brilhante, emotiva e indispensável na guitarra acústica contemporânea."
    ),
    "9": ChordDefinition(
        key="9",
        symbol="9",
        name_pt="Nona da Dominante",
        name_en="Dominant 9th",
        intervals=[0, 4, 7, 10, 14],
        formula_degrees="1 - 3 - 5 - ♭7 - 9",
        formula_intervals="Acorde Dominante 7 + Nona Maior (14 st)",
        description="Dominante expandida cheia de cor funk, blues e jazz."
    ),
    "7sus4": ChordDefinition(
        key="7sus4",
        symbol="7sus4",
        name_pt="Sétima com Quarta Suspensa",
        name_en="Dominant 7th Suspended 4th",
        intervals=[0, 5, 7, 10],
        formula_degrees="1 - 4 - 5 - ♭7",
        formula_intervals="Tríade Sus4 + Sétima Menor (10 st)",
        description="Mistura a suspensão da 4ª com a atração da 7ª menor. Sonoridade modal moderna de grande amplitude."
    ),
    "mMaj7": ChordDefinition(
        key="mMaj7",
        symbol="m(Maj7)",
        name_pt="Menor com Sétima Maior",
        name_en="Minor Major 7th",
        intervals=[0, 3, 7, 11],
        formula_degrees="1 - ♭3 - 5 - 7",
        formula_intervals="Tríade Menor + Sétima Maior (11 st)",
        description="Tétrade construída sobre o 1º grau da escala menor harmónica ou melódica. Famoso 'acorde de James Bond', misterioso e intrigante."
    ),
    "7b9": ChordDefinition(
        key="7b9",
        symbol="7(♭9)",
        name_pt="Dominante com Nona Bemol",
        name_en="Dominant 7th Flat 9",
        intervals=[0, 4, 7, 10, 13],
        formula_degrees="1 - 3 - 5 - ♭7 - ♭9",
        formula_intervals="Dominante 7 + Nona Menor (13 st)",
        description="Dominante alterada essencial na resolução para tonalidades menores (grau V7 no modo menor)."
    ),
    "7#9": ChordDefinition(
        key="7#9",
        symbol="7(♯9)",
        name_pt="Dominante com Nona Aumentada (Hendrix Chord)",
        name_en="Dominant 7th Sharp 9 (Hendrix Chord)",
        intervals=[0, 4, 7, 10, 15],
        formula_degrees="1 - 3 - 5 - ♭7 - ♯9",
        formula_intervals="Dominante 7 + Nona Aumentada (15 st)",
        description="O lendário 'Hendrix Chord' (Purple Haze). Combina a 3ª maior com a 3ª menor enarmónica (♯9), gerando tensão blues/rock única."
    ),
    "7#11": ChordDefinition(
        key="7#11",
        symbol="7(♯11)",
        name_pt="Dominante com 11ª Aumentada (Lídio ♭7)",
        name_en="Dominant 7th Sharp 11 (Lydian Dominant)",
        intervals=[0, 4, 7, 10, 18],
        formula_degrees="1 - 3 - 5 - ♭7 - ♯11",
        formula_intervals="Dominante 7 + Décima Primeira Aumentada (18 st)",
        description="Acorde do modo Lídio Dominante (4º grau da menor melódica), muito comum em substituições tritónicas."
    ),
    "7b13": ChordDefinition(
        key="7b13",
        symbol="7(♭13)",
        name_pt="Dominante com Décima Terceira Bemol",
        name_en="Dominant 7th Flat 13",
        intervals=[0, 4, 7, 10, 20],
        formula_degrees="1 - 3 - 5 - ♭7 - ♭13",
        formula_intervals="Dominante 7 + Décima Terceira Menor (20 st)",
        description="Dominante alterada de grande densidade harmónica usada em jazz e bossa nova."
    ),
}


from .notes import Note, DIATONIC_NAMES, spell_note_with_letter


class Chord:
    """Represents a concrete Chord built on a root note."""

    def __init__(self, root: Note, chord_type: str = "major", inversion: int = 0):
        if chord_type not in CHORD_TYPES:
            raise ValueError(f"Tipo de acorde desconhecido: '{chord_type}'")

        self.root = root
        self.chord_type = chord_type
        self.inversion = inversion
        self.definition = CHORD_TYPES[chord_type]
        self.notes = self._generate_notes()

    def _generate_notes(self) -> List[Note]:
        """Generates all Note objects in the chord accounting for inversions and harmonic spelling."""
        degree_offsets = []
        for deg in self.definition.formula_degrees.split("-"):
            deg_clean = deg.strip().replace("♭", "").replace("♯", "")
            if deg_clean.isdigit():
                val = int(deg_clean)
                degree_offsets.append(val - 1)
            else:
                degree_offsets.append(0)

        if self.root.letter in DIATONIC_NAMES and len(degree_offsets) == len(self.definition.intervals):
            start_letter_idx = DIATONIC_NAMES.index(self.root.letter)
            base_notes = []
            for i, st in enumerate(self.definition.intervals):
                target_midi = self.root.midi + st
                expected_letter = DIATONIC_NAMES[(start_letter_idx + degree_offsets[i]) % 7]
                base_notes.append(spell_note_with_letter(target_midi, expected_letter))
        else:
            base_notes = [self.root.transpose(st) for st in self.definition.intervals]

        if self.inversion == 0:
            return base_notes

        # Apply inversion: transpose the lowest notes up an octave
        inv_count = self.inversion % len(base_notes)
        inverted = []
        for i, note in enumerate(base_notes):
            if i < inv_count:
                inverted.append(note.transpose(12))
            else:
                inverted.append(note)
        # Sort by MIDI pitch
        inverted.sort(key=lambda n: n.midi)
        return inverted

    @property
    def chord_symbol(self) -> str:
        return f"{self.root.pitch}{self.definition.symbol}"

    @property
    def name_pt(self) -> str:
        inv_text = f" ({self.inversion}ª Inversão)" if self.inversion > 0 else ""
        return f"{self.root.name_pt} {self.definition.name_pt}{inv_text}"

    @property
    def note_names(self) -> List[str]:
        return [n.pitch for n in self.notes]

    @property
    def note_names_pt(self) -> List[str]:
        return [n.name_pt for n in self.notes]

    def __repr__(self) -> str:
        notes_str = ", ".join(self.note_names)
        return f"Chord({self.chord_symbol}: [{notes_str}])"


def get_chord_notes(root_name: str, chord_type: str = "major", octave: int = 4, inversion: int = 0) -> List[Note]:
    """Helper function to quickly generate notes for a chord."""
    root = Note(root_name, octave=octave)
    chord = Chord(root, chord_type, inversion)
    return chord.notes
