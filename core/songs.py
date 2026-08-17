"""Song Repertoire Module with full complete pieces, note-by-note coordinates, durations, lyrics, and fingerings."""
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from core.notes import Note


@dataclass
class SongNote:
    """Represents an individual musical event in a piece with fingerings and instrument coordinates."""
    note: Note
    duration_beats: float
    piano_finger: Optional[int] = None
    piano_hand: str = "direita"  # "direita" ou "esquerda"
    guitar_string: Optional[int] = None  # 0=6ª (Mi grave) ... 5=1ª (Mi agudo)
    guitar_fret: Optional[int] = None    # 0=solta, 1..15
    lyric_syllable: Optional[str] = None


@dataclass
class Song:
    """Metadata and full musical sequence for a repertoire piece."""
    id: str
    title: str
    composer: str
    difficulty: str  # "Iniciante", "Intermédio", "Avançado"
    bpm: int
    difficulty_en: Optional[str] = None
    clef: str = "treble"  # "treble" ou "bass"
    instrument: str = "piano"  # "piano" ou "guitar" / "viola"
    time_signature: str = "4/4"
    description: str = ""
    description_en: Optional[str] = None
    theory_analysis: Optional[str] = None
    theory_analysis_en: Optional[str] = None
    notes: List[SongNote] = field(default_factory=list)

    def get_theory_analysis(self, lang: str = "pt") -> Optional[str]:
        if lang == "en" and self.theory_analysis_en:
            return self.theory_analysis_en
        return self.theory_analysis

    def get_description(self, lang: str = "pt") -> str:
        if lang == "en" and self.description_en:
            return self.description_en
        return self.description

    def get_difficulty(self, lang: str = "pt") -> str:
        if lang == "en" and self.difficulty_en:
            return self.difficulty_en
        return self.difficulty

    @property
    def note_count(self) -> int:
        return len(self.notes)

    @property
    def total_beats(self) -> float:
        return sum(sn.duration_beats for sn in self.notes)

    @property
    def beats_per_measure(self) -> float:
        try:
            num, den = self.time_signature.split("/")
            return float(num) * (4.0 / float(den))
        except Exception:
            return 4.0


def _sn(
    pitch_str: str,
    beats: float,
    finger: Optional[int] = None,
    g_str: Optional[int] = None,
    g_fret: Optional[int] = None,
    lyric: Optional[str] = None,
    hand: str = "direita",
) -> SongNote:
    return SongNote(
        note=Note(pitch_str),
        duration_beats=beats,
        piano_finger=finger,
        piano_hand=hand,
        guitar_string=g_str,
        guitar_fret=g_fret,
        lyric_syllable=lyric,
    )


SONG_LIBRARY: List[Song] = [
    # 1. HINO À ALEGRIA (Beethoven) — Peça Completa (16 Compassos em 4/4 = 64 Tempos)
    Song(
        id="ode_to_joy",
        title="Hino à Alegria (9ª Sinfonia)",
        composer="Ludwig van Beethoven",
        difficulty="Iniciante",
        difficulty_en="Beginner",
        bpm=108,
        clef="treble",
        instrument="piano",
        time_signature="4/4",
        description="O tema imortal da Nona Sinfonia de Beethoven na íntegra. Melodia por graus conjuntos com frase A, ponte B e conclusão solene.",
        description_en="The immortal theme from Beethoven's Ninth Symphony in its entirety. Stepwise melody with phrase A, bridge B, and a solemn conclusion.",
        notes=[
            # Frase A (16 tempos)
            _sn("E4", 1.0, 3, 5, 0, "A-"),
            _sn("E4", 1.0, 3, 5, 0, "le-"),
            _sn("F4", 1.0, 4, 5, 1, "gri-"),
            _sn("G4", 1.0, 5, 5, 3, "a,"),
            _sn("G4", 1.0, 5, 5, 3, "bri-"),
            _sn("F4", 1.0, 4, 5, 1, "lho"),
            _sn("E4", 1.0, 3, 5, 0, "lin-"),
            _sn("D4", 1.0, 2, 4, 3, "do,"),
            _sn("C4", 1.0, 1, 4, 1, "dos"),
            _sn("C4", 1.0, 1, 4, 1, "deu-"),
            _sn("D4", 1.0, 2, 4, 3, "ses"),
            _sn("E4", 1.0, 3, 5, 0, "da"),
            _sn("E4", 1.5, 3, 5, 0, "ter-"),
            _sn("D4", 0.5, 2, 4, 3, "ra"),
            _sn("D4", 2.0, 2, 4, 3, "flor!"),
            # Frase A' (16 tempos)
            _sn("E4", 1.0, 3, 5, 0, "Teus"),
            _sn("E4", 1.0, 3, 5, 0, "en-"),
            _sn("F4", 1.0, 4, 5, 1, "can-"),
            _sn("G4", 1.0, 5, 5, 3, "tos"),
            _sn("G4", 1.0, 5, 5, 3, "no-"),
            _sn("F4", 1.0, 4, 5, 1, "va-"),
            _sn("E4", 1.0, 3, 5, 0, "men-"),
            _sn("D4", 1.0, 2, 4, 3, "te"),
            _sn("C4", 1.0, 1, 4, 1, "nos"),
            _sn("C4", 1.0, 1, 4, 1, "u-"),
            _sn("D4", 1.0, 2, 4, 3, "nem"),
            _sn("E4", 1.0, 3, 5, 0, "com"),
            _sn("D4", 1.5, 2, 4, 3, "a-"),
            _sn("C4", 0.5, 1, 4, 1, "mor"),
            _sn("C4", 2.0, 1, 4, 1, "só!"),
            # Ponte B (16 tempos)
            _sn("D4", 1.0, 2, 4, 3, "To-"),
            _sn("D4", 1.0, 2, 4, 3, "dos"),
            _sn("E4", 1.0, 3, 5, 0, "os"),
            _sn("C4", 1.0, 1, 4, 1, "seres"),
            _sn("D4", 1.0, 2, 4, 3, "be-"),
            _sn("E4", 0.5, 3, 5, 0, "bem"),
            _sn("F4", 0.5, 4, 5, 1, "a-"),
            _sn("E4", 1.0, 3, 5, 0, "le-"),
            _sn("C4", 1.0, 1, 4, 1, "gria"),
            _sn("D4", 1.0, 2, 4, 3, "no"),
            _sn("E4", 0.5, 3, 5, 0, "seio"),
            _sn("F4", 0.5, 4, 5, 1, "da"),
            _sn("E4", 1.0, 3, 5, 0, "na-"),
            _sn("D4", 1.0, 2, 4, 3, "tu-"),
            _sn("C4", 1.0, 1, 4, 1, "re-"),
            _sn("D4", 1.0, 2, 4, 3, "za,"),
            _sn("G3", 2.0, 1, 3, 0, "sim!"),
            # Conclusão Reprise A (16 tempos)
            _sn("E4", 1.0, 3, 5, 0, "A-"),
            _sn("E4", 1.0, 3, 5, 0, "le-"),
            _sn("F4", 1.0, 4, 5, 1, "gri-"),
            _sn("G4", 1.0, 5, 5, 3, "a,"),
            _sn("G4", 1.0, 5, 5, 3, "bri-"),
            _sn("F4", 1.0, 4, 5, 1, "lho"),
            _sn("E4", 1.0, 3, 5, 0, "lin-"),
            _sn("D4", 1.0, 2, 4, 3, "do,"),
            _sn("C4", 1.0, 1, 4, 1, "dos"),
            _sn("C4", 1.0, 1, 4, 1, "deu-"),
            _sn("D4", 1.0, 2, 4, 3, "ses"),
            _sn("E4", 1.0, 3, 5, 0, "da"),
            _sn("D4", 1.5, 2, 4, 3, "ter-"),
            _sn("C4", 0.5, 1, 4, 1, "ra"),
            _sn("C4", 2.0, 1, 4, 1, "flor!"),
        ],
    ),

    # 2. BRILHA, BRILHA ESTRELINHA (Mozart) — Peça Completa (12 Compassos em 4/4 = 48 Tempos)
    Song(
        id="twinkle_star",
        title="Brilha, Brilha Estrelinha (Completo A-B-A)",
        composer="Tradicional / Variações Mozart",
        difficulty="Iniciante",
        difficulty_en="Beginner",
        bpm=100,
        clef="treble",
        instrument="piano",
        time_signature="4/4",
        description="A melodia clássica completa em forma ternária A-B-A. Inclui a primeira estrofe e o tema central de retorno.",
        description_en="The complete classic melody in ternary A-B-A form. Includes the opening theme and the contrasting middle section.",
        notes=[
            # Secção A (16 tempos)
            _sn("C4", 1.0, 1, 4, 1, "Bri-"),
            _sn("C4", 1.0, 1, 4, 1, "lha,"),
            _sn("G4", 1.0, 5, 5, 3, "bri-"),
            _sn("G4", 1.0, 5, 5, 3, "lha"),
            _sn("A4", 1.0, 5, 5, 5, "es-"),
            _sn("A4", 1.0, 5, 5, 5, "tre-"),
            _sn("G4", 2.0, 4, 5, 3, "li-nha,"),
            _sn("F4", 1.0, 4, 5, 1, "lá"),
            _sn("F4", 1.0, 4, 5, 1, "no"),
            _sn("E4", 1.0, 3, 5, 0, "céu"),
            _sn("E4", 1.0, 3, 5, 0, "a"),
            _sn("D4", 1.0, 2, 4, 3, "bri-"),
            _sn("D4", 1.0, 2, 4, 3, "lhar,"),
            _sn("C4", 2.0, 1, 4, 1, "só!"),
            # Secção B (16 tempos)
            _sn("G4", 1.0, 5, 5, 3, "Vejo-"),
            _sn("G4", 1.0, 5, 5, 3, "te"),
            _sn("F4", 1.0, 4, 5, 1, "no"),
            _sn("F4", 1.0, 4, 5, 1, "céu"),
            _sn("E4", 1.0, 3, 5, 0, "bri-"),
            _sn("E4", 1.0, 3, 5, 0, "lhan-"),
            _sn("D4", 2.0, 2, 4, 3, "do,"),
            _sn("G4", 1.0, 5, 5, 3, "co-"),
            _sn("G4", 1.0, 5, 5, 3, "mo_um"),
            _sn("F4", 1.0, 4, 5, 1, "dia-"),
            _sn("F4", 1.0, 4, 5, 1, "man-"),
            _sn("E4", 1.0, 3, 5, 0, "te"),
            _sn("E4", 1.0, 3, 5, 0, "ra-"),
            _sn("D4", 2.0, 2, 4, 3, "dian-te!"),
            # Reprise Secção A (16 tempos)
            _sn("C4", 1.0, 1, 4, 1, "Bri-"),
            _sn("C4", 1.0, 1, 4, 1, "lha,"),
            _sn("G4", 1.0, 5, 5, 3, "bri-"),
            _sn("G4", 1.0, 5, 5, 3, "lha"),
            _sn("A4", 1.0, 5, 5, 5, "es-"),
            _sn("A4", 1.0, 5, 5, 5, "tre-"),
            _sn("G4", 2.0, 4, 5, 3, "li-nha,"),
            _sn("F4", 1.0, 4, 5, 1, "lá"),
            _sn("F4", 1.0, 4, 5, 1, "no"),
            _sn("E4", 1.0, 3, 5, 0, "céu"),
            _sn("E4", 1.0, 3, 5, 0, "a"),
            _sn("D4", 1.0, 2, 4, 3, "cin-"),
            _sn("D4", 1.0, 2, 4, 3, "ti-"),
            _sn("C4", 2.0, 1, 4, 1, "lar."),
        ],
    ),

    # 3. PAPAGAIO LOIRO (Cantiga Popular Portuguesa) — 18 Compassos em 2/4 = 36 Tempos
    Song(
        id="papagaio_loiro",
        title="Papagaio Loiro (Cantiga Tradicional Completa)",
        composer="Folclore Português",
        difficulty="Iniciante",
        difficulty_en="Beginner",
        bpm=110,
        clef="treble",
        instrument="piano",
        time_signature="2/4",
        description="Cantiga tradicional portuguesa completa em dois andamentos com letra tradicional integral.",
        description_en="Complete traditional Portuguese song in two movements with full traditional lyrics.",
        notes=[
            # 1ª Frase (12 tempos = 6 compassos de 2/4)
            _sn("G4", 1.0, 5, 5, 3, "Pa-"),
            _sn("E4", 1.0, 3, 5, 0, "pa-"),
            _sn("G4", 1.0, 5, 5, 3, "gaio"),
            _sn("E4", 1.0, 3, 5, 0, "loi-"),
            _sn("G4", 1.0, 5, 5, 3, "ro,"),
            _sn("G4", 1.0, 5, 5, 3, "do"),
            _sn("A4", 1.0, 5, 5, 5, "bi-"),
            _sn("G4", 1.0, 4, 5, 3, "co"),
            _sn("F4", 1.0, 3, 5, 1, "doi-"),
            _sn("E4", 1.0, 2, 5, 0, "ra-"),
            _sn("D4", 2.0, 1, 4, 3, "do!"),
            # 2ª Frase (12 tempos = 6 compassos de 2/4)
            _sn("D4", 1.0, 1, 4, 3, "Le-"),
            _sn("F4", 1.0, 3, 5, 1, "va_es-"),
            _sn("D4", 1.0, 1, 4, 3, "ta"),
            _sn("F4", 1.0, 3, 5, 1, "car-"),
            _sn("A4", 1.0, 5, 5, 5, "ti-"),
            _sn("A4", 1.0, 5, 5, 5, "nha"),
            _sn("G4", 1.0, 4, 5, 3, "ao"),
            _sn("F4", 1.0, 3, 5, 1, "meu"),
            _sn("E4", 1.0, 2, 5, 0, "na-"),
            _sn("D4", 1.0, 1, 4, 3, "mo-"),
            _sn("C4", 2.0, 1, 4, 1, "ra-do!"),
            # Refrão (12 tempos = 6 compassos de 2/4)
            _sn("G4", 1.0, 5, 5, 3, "Que_es-"),
            _sn("E4", 1.0, 3, 5, 0, "tá"),
            _sn("G4", 1.0, 5, 5, 3, "na"),
            _sn("E4", 1.0, 3, 5, 0, "es-"),
            _sn("G4", 1.0, 5, 5, 3, "co-"),
            _sn("A4", 1.0, 5, 5, 5, "la"),
            _sn("G4", 1.0, 4, 5, 3, "a"),
            _sn("F4", 1.0, 3, 5, 1, "a-"),
            _sn("E4", 1.0, 2, 5, 0, "pren-"),
            _sn("D4", 1.0, 1, 4, 3, "der"),
            _sn("C4", 2.0, 1, 4, 1, "já!"),
        ],
    ),

    # 4. POMBINHA BRANCA (Tradicional Portuguesa) — 6 Compassos em 4/4 = 24 Tempos
    Song(
        id="pombinha_branca",
        title="Pombinha Branca (Cantiga Completa)",
        composer="Folclore Português",
        difficulty="Iniciante",
        difficulty_en="Beginner",
        bpm=96,
        clef="treble",
        instrument="piano",
        time_signature="4/4",
        description="Melodia suave e completa do cancioneiro tradicional português.",
        description_en="Smooth and complete melody from the traditional Portuguese songbook.",
        notes=[
            _sn("G4", 1.0, 5, 5, 3, "Pom-"),
            _sn("E4", 1.0, 3, 5, 0, "bi-"),
            _sn("C4", 1.0, 1, 4, 1, "nha"),
            _sn("E4", 1.0, 3, 5, 0, "bran-"),
            _sn("D4", 1.0, 2, 4, 3, "ca,"),
            _sn("D4", 1.0, 2, 4, 3, "que"),
            _sn("D4", 1.0, 2, 4, 3, "es-"),
            _sn("E4", 1.0, 3, 5, 0, "tás"),
            _sn("F4", 1.0, 4, 5, 1, "a"),
            _sn("G4", 3.0, 5, 5, 3, "fa-zer?"),
            _sn("G4", 1.0, 5, 5, 3, "Es-"),
            _sn("E4", 1.0, 3, 5, 0, "tou"),
            _sn("C4", 1.0, 1, 4, 1, "a"),
            _sn("E4", 1.0, 3, 5, 0, "la-"),
            _sn("D4", 1.0, 2, 4, 3, "var"),
            _sn("D4", 1.0, 2, 4, 3, "a"),
            _sn("D4", 1.0, 2, 4, 3, "rou-"),
            _sn("E4", 1.0, 3, 5, 0, "pa"),
            _sn("D4", 1.0, 2, 4, 3, "pro"),
            _sn("C4", 3.0, 1, 4, 1, "meu_bem!"),
        ],
    ),

    # 5. FÜR ELISE (Beethoven) — Melodia Completa (13 Compassos em 3/8 = 19.5 Tempos)
    Song(
        id="fur_elise",
        title="Für Elise (Melodia Completa)",
        composer="Ludwig van Beethoven",
        difficulty="Intermédio",
        difficulty_en="Intermediate",
        bpm=120,
        clef="treble",
        instrument="piano",
        time_signature="3/8",
        description="A célebre Bagatela em Lá menor (WoO 59) de Beethoven com o motivo cromático inicial, arpejos de Lá menor e Mi Maior e cadência harmónica.",
        description_en="Beethoven's famous Bagatelle in A minor (WoO 59) with the initial chromatic motif, A minor and E Major arpeggios, and harmonic cadence.",
        notes=[
            _sn("E5", 0.5, 5, 5, 12, "Mi"),
            _sn("D#5", 0.5, 4, 5, 11, "Ré#"),
            _sn("E5", 0.5, 5, 5, 12, "Mi"),
            _sn("D#5", 0.5, 4, 5, 11, "Ré#"),
            _sn("E5", 0.5, 5, 5, 12, "Mi"),
            _sn("B4", 0.5, 3, 5, 7, "Si"),
            _sn("D5", 0.5, 4, 5, 10, "Ré"),
            _sn("C5", 0.5, 3, 5, 8, "Dó"),
            _sn("A4", 1.0, 1, 5, 5, "Lá"),
            # Arpejo Dó-Mi-Lá-Si
            _sn("C4", 0.5, 1, 4, 1, "Dó"),
            _sn("E4", 0.5, 2, 5, 0, "Mi"),
            _sn("A4", 0.5, 3, 5, 5, "Lá"),
            _sn("B4", 1.0, 4, 5, 7, "Si"),
            # Arpejo Mi-Sol#-Si-Dó
            _sn("E4", 0.5, 1, 5, 0, "Mi"),
            _sn("G#4", 0.5, 2, 5, 4, "Sol#"),
            _sn("B4", 0.5, 3, 5, 7, "Si"),
            _sn("C5", 1.0, 4, 5, 8, "Dó"),
            # Reprise do motivo
            _sn("E4", 0.5, 1, 5, 0, "Mi"),
            _sn("E5", 0.5, 5, 5, 12, "Mi"),
            _sn("D#5", 0.5, 4, 5, 11, "Ré#"),
            _sn("E5", 0.5, 5, 5, 12, "Mi"),
            _sn("D#5", 0.5, 4, 5, 11, "Ré#"),
            _sn("E5", 0.5, 5, 5, 12, "Mi"),
            _sn("B4", 0.5, 3, 5, 7, "Si"),
            _sn("D5", 0.5, 4, 5, 10, "Ré"),
            _sn("C5", 0.5, 3, 5, 8, "Dó"),
            _sn("A4", 1.0, 1, 5, 5, "Lá"),
            _sn("C4", 0.5, 1, 4, 1, "Dó"),
            _sn("E4", 0.5, 2, 5, 0, "Mi"),
            _sn("A4", 0.5, 3, 5, 5, "Lá"),
            _sn("B4", 0.5, 4, 5, 7, "Si"),
            _sn("C5", 0.5, 3, 5, 8, "Dó"),
            _sn("B4", 0.5, 2, 5, 7, "Si"),
            _sn("A4", 1.0, 1, 5, 5, "Lá!"),
        ],
    ),

    # 6. MINUETO EM SOL (Petzold / Bach) — Seção A (8 Compassos em 3/4 = 24 Tempos)
    Song(
        id="minuet_in_g",
        title="Minueto em Sol Maior (Frase Inicial)",
        composer="Christian Petzold / J. S. Bach",
        difficulty="Intermédio",
        difficulty_en="Intermediate",
        bpm=116,
        clef="treble",
        instrument="piano",
        time_signature="3/4",
        description="Do Pequeno Livro de Anna Magdalena Bach. A primeira frase completa de 8 compassos em Sol Maior.",
        description_en="From the Notebook for Anna Magdalena Bach. The opening 8-measure phrase in G Major.",
        notes=[
            _sn("D5", 1.0, 5, 5, 10, "Ré"),
            _sn("G4", 0.5, 1, 5, 3, "Sol"),
            _sn("A4", 0.5, 2, 5, 5, "Lá"),
            _sn("B4", 0.5, 3, 5, 7, "Si"),
            _sn("C5", 0.5, 4, 5, 8, "Dó"),
            _sn("D5", 1.0, 5, 5, 10, "Ré"),
            _sn("G4", 1.0, 1, 5, 3, "Sol"),
            _sn("G4", 1.0, 1, 5, 3, "Sol"),
            _sn("E5", 1.0, 5, 5, 12, "Mi"),
            _sn("C5", 0.5, 3, 5, 8, "Dó"),
            _sn("D5", 0.5, 4, 5, 10, "Ré"),
            _sn("E5", 0.5, 5, 5, 12, "Mi"),
            _sn("F#5", 0.5, 5, 5, 14, "Fá#"),
            _sn("G5", 1.0, 5, 5, 15, "Sol"),
            _sn("G4", 1.0, 1, 5, 3, "Sol"),
            _sn("G4", 1.0, 1, 5, 3, "Sol"),
            _sn("C5", 1.0, 4, 5, 8, "Dó"),
            _sn("D5", 0.5, 5, 5, 10, "Ré"),
            _sn("C5", 0.5, 4, 5, 8, "Dó"),
            _sn("B4", 0.5, 3, 5, 7, "Si"),
            _sn("A4", 0.5, 2, 5, 5, "Lá"),
            _sn("B4", 1.0, 3, 5, 7, "Si"),
            _sn("C5", 0.5, 4, 5, 8, "Dó"),
            _sn("B4", 0.5, 3, 5, 7, "Si"),
            _sn("A4", 0.5, 2, 5, 5, "Lá"),
            _sn("G4", 0.5, 1, 5, 3, "Sol"),
            _sn("F#4", 1.0, 2, 5, 2, "Fá#"),
            _sn("G4", 0.5, 1, 5, 3, "Sol"),
            _sn("A4", 0.5, 2, 5, 5, "Lá"),
            _sn("B4", 0.5, 3, 5, 7, "Si"),
            _sn("G4", 0.5, 1, 5, 3, "Sol"),
            _sn("A4", 2.0, 2, 5, 5, "Lá"),
            _sn("D4", 1.0, 1, 4, 3, "Ré"),
        ],
    ),

    # 7. MARCHA NUPCIAL (Wagner) — Tema Coral Completo (8 Compassos em 4/4 = 32 Tempos)
    Song(
        id="bridal_chorus",
        title="Marcha Nupcial (Tema Coral Completo)",
        composer="Richard Wagner",
        difficulty="Intermédio",
        difficulty_en="Intermediate",
        bpm=76,
        clef="treble",
        instrument="piano",
        time_signature="4/4",
        description="Tema do Coro Nupcial da ópera Lohengrin de Wagner com as frases de entrada, resposta modulante e cadência triunfal.",
        description_en="The Bridal Chorus theme from Wagner's opera Lohengrin featuring the opening phrases, modulating response, and triumphant cadence.",
        notes=[
            _sn("C4", 1.5, 1, 4, 1, "Tcham-"),
            _sn("F4", 0.5, 3, 5, 1, "tcham-"),
            _sn("F4", 2.0, 3, 5, 1, "tcham!"),
            _sn("C4", 1.5, 1, 4, 1, "Tcham-"),
            _sn("G4", 0.5, 4, 5, 3, "tcham-"),
            _sn("G4", 2.0, 4, 5, 3, "tcham!"),
            _sn("C4", 1.5, 1, 4, 1, "Tcham-"),
            _sn("A4", 0.5, 5, 5, 5, "tcham-"),
            _sn("G4", 1.0, 4, 5, 3, "tcham-"),
            _sn("F4", 1.0, 3, 5, 1, "tcham"),
            _sn("E4", 1.5, 2, 5, 0, "tcham-"),
            _sn("D4", 0.5, 1, 4, 3, "tcham-"),
            _sn("C4", 2.0, 1, 4, 1, "tcham!"),
            _sn("C4", 1.5, 1, 4, 1, "Tcham-"),
            _sn("F4", 0.5, 3, 5, 1, "tcham-"),
            _sn("F4", 2.0, 3, 5, 1, "tcham!"),
            _sn("C4", 1.5, 1, 4, 1, "Tcham-"),
            _sn("G4", 0.5, 4, 5, 3, "tcham-"),
            _sn("G4", 2.0, 4, 5, 3, "tcham!"),
            _sn("C4", 1.5, 1, 4, 1, "Tcham-"),
            _sn("A4", 0.5, 5, 5, 5, "tcham-"),
            _sn("G4", 1.0, 4, 5, 3, "tcham-"),
            _sn("F4", 1.0, 3, 5, 1, "tcham"),
            _sn("G4", 2.0, 4, 5, 3, "tcham-"),
            _sn("F4", 2.0, 3, 5, 1, "tcham!"),
        ],
    ),

    # 8. CÂNONE EM RÉ MAIOR (Pachelbel) — Melodia Principal (6 Compassos em 4/4 = 24 Tempos)
    Song(
        id="canon_in_d",
        title="Cânone em Ré Maior (Melodia Principal)",
        composer="Johann Pachelbel",
        difficulty="Intermédio",
        difficulty_en="Intermediate",
        bpm=80,
        clef="treble",
        instrument="piano",
        time_signature="4/4",
        description="A progressão de acordes barroca mais famosa de sempre. Melodia principal das cordas sobre o baixo ostinato.",
        description_en="The most famous Baroque chord progression in history. Lead string melody over the ground bass.",
        notes=[
            _sn("F#4", 2.0, 3, 5, 2, "Fá#"),
            _sn("E4", 2.0, 2, 5, 0, "Mi"),
            _sn("D4", 2.0, 1, 4, 3, "Ré"),
            _sn("C#4", 2.0, 1, 4, 2, "Dó#"),
            _sn("B3", 2.0, 1, 4, 0, "Si"),
            _sn("A3", 2.0, 1, 3, 2, "Lá"),
            _sn("B3", 2.0, 1, 4, 0, "Si"),
            _sn("C#4", 2.0, 1, 4, 2, "Dó#"),
            _sn("D4", 1.0, 1, 4, 3, "Ré"),
            _sn("C#4", 1.0, 1, 4, 2, "Dó#"),
            _sn("B3", 1.0, 1, 4, 0, "Si"),
            _sn("A3", 1.0, 1, 3, 2, "Lá"),
            _sn("G3", 1.0, 1, 3, 0, "Sol"),
            _sn("F#3", 1.0, 1, 2, 4, "Fá#"),
            _sn("G3", 1.0, 1, 3, 0, "Sol"),
            _sn("A3", 1.0, 1, 3, 2, "Lá!"),
        ],
    ),

    # 9. PEQUENA MÚSICA NOTURNA (Mozart) — 6 Compassos em 4/4 = 24 Tempos
    Song(
        id="nachtmusik",
        title="Eine kleine Nachtmusik (Abertura)",
        composer="W. A. Mozart",
        difficulty="Intermédio",
        difficulty_en="Intermediate",
        bpm=130,
        clef="treble",
        instrument="piano",
        time_signature="4/4",
        description="Serenata No. 13 em Sol Maior (K. 525). O tema de abertura brilhante e enérgico que define o classicismo vienense.",
        description_en="Serenade No. 13 in G Major (K. 525). The bright, energetic opening theme defining Viennese Classicism.",
        notes=[
            _sn("G4", 1.5, 1, 5, 3, "Sol"),
            _sn("D4", 0.5, 1, 4, 3, "Ré"),
            _sn("G4", 1.5, 1, 5, 3, "Sol"),
            _sn("D4", 0.5, 1, 4, 3, "Ré"),
            _sn("G4", 0.5, 1, 5, 3, "Sol"),
            _sn("B4", 0.5, 3, 5, 7, "Si"),
            _sn("D5", 1.0, 5, 5, 10, "Ré"),
            _sn("C5", 1.5, 4, 5, 8, "Dó"),
            _sn("A4", 0.5, 2, 5, 5, "Lá"),
            _sn("C5", 1.5, 4, 5, 8, "Dó"),
            _sn("A4", 0.5, 2, 5, 5, "Lá"),
            _sn("F#4", 0.5, 1, 5, 2, "Fá#"),
            _sn("A4", 0.5, 2, 5, 5, "Lá"),
            _sn("D4", 1.0, 1, 4, 3, "Ré"),
            _sn("G4", 1.0, 1, 5, 3, "Sol"),
            _sn("G4", 0.5, 1, 5, 3, "Sol"),
            _sn("B4", 0.5, 3, 5, 7, "Si"),
            _sn("D5", 0.5, 5, 5, 10, "Ré"),
            _sn("B4", 0.5, 3, 5, 7, "Si"),
            _sn("G4", 1.0, 1, 5, 3, "Sol"),
            _sn("A4", 1.0, 2, 5, 5, "Lá"),
            _sn("A4", 0.5, 2, 5, 5, "Lá"),
            _sn("C5", 0.5, 4, 5, 8, "Dó"),
            _sn("D5", 0.5, 5, 5, 10, "Ré"),
            _sn("C5", 0.5, 4, 5, 8, "Dó"),
            _sn("A4", 1.0, 2, 5, 5, "Lá"),
            _sn("G4", 2.0, 1, 5, 3, "Sol!"),
            _sn("G4", 2.0, 1, 5, 3, "Sol!"),
        ],
    ),

    # 10. GREENSLEEVES (Tradicional Inglesa) — 8 Compassos em 6/8 = 24 Tempos
    Song(
        id="greensleeves",
        title="Greensleeves (Melodia Tradicional)",
        composer="Tradicional Inglês (Século XVI)",
        difficulty="Intermédio",
        difficulty_en="Intermediate",
        bpm=108,
        clef="treble",
        instrument="guitar",
        time_signature="6/8",
        description="Balada renascentista inglesa em Lá menor (Eólio com 7ª elevada nas cadências).",
        description_en="English Renaissance ballad in A minor (Aeolian with raised 7th at cadences).",
        notes=[
            _sn("A3", 1.0, 1, 3, 2, "A-"),
            _sn("C4", 0.5, 2, 4, 1, "las,"),
            _sn("D4", 1.0, 3, 4, 3, "my"),
            _sn("E4", 0.5, 4, 5, 0, "love,"),
            _sn("F4", 1.5, 5, 5, 1, "you"),
            _sn("E4", 1.0, 4, 5, 0, "do"),
            _sn("D4", 0.5, 3, 4, 3, "me"),
            _sn("B3", 1.0, 2, 4, 0, "wrong,"),
            _sn("G3", 0.5, 1, 3, 0, "to"),
            _sn("A3", 1.0, 2, 3, 2, "cast"),
            _sn("B3", 0.5, 3, 4, 0, "me"),
            _sn("C4", 1.5, 4, 4, 1, "off"),
            _sn("A3", 1.0, 2, 3, 2, "dis-"),
            _sn("A3", 0.5, 2, 3, 2, "cour-"),
            _sn("G#3", 1.0, 1, 3, 1, "teous-"),
            _sn("E3", 0.5, 1, 2, 2, "ly,"),
            _sn("F#3", 1.0, 2, 2, 4, "and"),
            _sn("G#3", 0.5, 3, 3, 1, "I"),
            _sn("A3", 1.5, 4, 3, 2, "have"),
            _sn("A3", 1.0, 4, 3, 2, "loved"),
            _sn("B3", 0.5, 4, 4, 0, "you"),
            _sn("C4", 1.5, 4, 4, 1, "oh"),
            _sn("B3", 1.0, 3, 4, 0, "so"),
            _sn("A3", 0.5, 2, 3, 2, "long,"),
            _sn("G#3", 1.5, 1, 3, 1, "Green-"),
            _sn("A3", 1.5, 2, 3, 2, "sleeves!"),
        ],
    ),

    # 11. O CRAVO E A ROSA (Tradicional Portuguesa) — 8 Compassos em 4/4 = 32 Tempos
    Song(
        id="cravo_e_rosa",
        title="O Cravo e a Rosa (Cantiga Completa)",
        composer="Cancioneiro Popular",
        difficulty="Iniciante",
        difficulty_en="Beginner",
        bpm=104,
        clef="treble",
        instrument="piano",
        time_signature="4/4",
        description="Famosa cantiga de roda da tradição lusófona na sua versão melódica autêntica.",
        description_en="Famous traditional Lusophone nursery rhyme in its authentic melodic version.",
        notes=[
            _sn("G4", 1.0, 5, 5, 3, "O"),
            _sn("G4", 1.0, 5, 5, 3, "cra-"),
            _sn("E4", 1.0, 3, 5, 0, "vo"),
            _sn("C4", 1.0, 1, 4, 1, "bri-"),
            _sn("A4", 1.0, 5, 5, 5, "gou"),
            _sn("A4", 1.0, 5, 5, 5, "com"),
            _sn("G4", 2.0, 4, 5, 3, "a ro-sa,"),
            _sn("F4", 1.0, 4, 5, 1, "de-"),
            _sn("F4", 1.0, 4, 5, 1, "bai-"),
            _sn("D4", 1.0, 2, 4, 3, "xo"),
            _sn("B3", 1.0, 1, 4, 0, "de"),
            _sn("C4", 1.0, 1, 4, 1, "u-"),
            _sn("D4", 1.0, 2, 4, 3, "ma"),
            _sn("E4", 2.0, 3, 5, 0, "sa-ca-da;"),
            _sn("G4", 1.0, 5, 5, 3, "o"),
            _sn("G4", 1.0, 5, 5, 3, "cra-"),
            _sn("E4", 1.0, 3, 5, 0, "vo"),
            _sn("C4", 1.0, 1, 4, 1, "sa-"),
            _sn("A4", 1.0, 5, 5, 5, "iu"),
            _sn("A4", 1.0, 5, 5, 5, "fe-"),
            _sn("G4", 2.0, 4, 5, 3, "ri-do,"),
            _sn("F4", 1.0, 4, 5, 1, "e_a"),
            _sn("F4", 1.0, 4, 5, 1, "ro-"),
            _sn("D4", 1.0, 2, 4, 3, "sa"),
            _sn("B3", 1.0, 1, 4, 0, "des-"),
            _sn("D4", 1.0, 2, 4, 3, "pe-"),
            _sn("B3", 1.0, 1, 4, 0, "da-"),
            _sn("C4", 2.0, 1, 4, 1, "ça-da!"),
        ],
    ),

    # 12. GRÂNDOLA, VILA MORENA (Zeca Afonso) — 8 Compassos em 4/4 = 32 Tempos
    Song(
        id="grandola",
        title="Grândola, Vila Morena (Hino Completo)",
        composer="José Afonso (Zeca Afonso)",
        difficulty="Iniciante",
        difficulty_en="Beginner",
        bpm=88,
        clef="treble",
        instrument="guitar",
        time_signature="4/4",
        description="O hino da Revolução dos Cravos de 25 de Abril de 1974. Melodia popular alentejana em Mi menor.",
        description_en="The anthem of Portugal's Carnation Revolution of April 25, 1974. Traditional Alentejo melody in E minor.",
        notes=[
            _sn("E4", 1.0, 1, 5, 0, "Grân-"),
            _sn("G4", 1.0, 2, 5, 3, "do-"),
            _sn("A4", 1.0, 3, 5, 5, "la,"),
            _sn("B4", 1.0, 4, 5, 7, "vi-"),
            _sn("A4", 2.0, 3, 5, 5, "la"),
            _sn("G4", 2.0, 2, 5, 3, "mo-re-na,"),
            _sn("E4", 1.0, 1, 5, 0, "Ter-"),
            _sn("G4", 1.0, 2, 5, 3, "ra"),
            _sn("A4", 1.0, 3, 5, 5, "da"),
            _sn("B4", 1.0, 4, 5, 7, "fra-"),
            _sn("A4", 2.0, 3, 5, 5, "ter-"),
            _sn("G4", 2.0, 2, 5, 3, "ni-da-de,"),
            _sn("B4", 1.0, 4, 5, 7, "O"),
            _sn("C5", 1.0, 5, 5, 8, "po-"),
            _sn("D5", 1.0, 5, 5, 10, "vo_é"),
            _sn("C5", 1.0, 5, 5, 8, "quem"),
            _sn("B4", 2.0, 4, 5, 7, "mais"),
            _sn("A4", 2.0, 3, 5, 5, "or-de-na,"),
            _sn("G4", 1.0, 2, 5, 3, "den-"),
            _sn("A4", 1.0, 3, 5, 5, "tro"),
            _sn("B4", 1.0, 4, 5, 7, "de"),
            _sn("A4", 1.0, 3, 5, 5, "ti,"),
            _sn("G4", 2.0, 2, 5, 3, "ó"),
            _sn("E4", 2.0, 1, 5, 0, "ci-da-de!"),
        ],
    ),

    # 13. STAIRWAY TO HEAVEN (Led Zeppelin) — 5 Compassos em 4/4 = 20 Tempos
    Song(
        id="stairway_to_heaven",
        title="Stairway to Heaven (Introdução)",
        composer="Jimmy Page & Robert Plant",
        difficulty="Avançado",
        difficulty_en="Advanced",
        bpm=72,
        clef="treble",
        instrument="guitar",
        time_signature="4/4",
        description="A introdução dedilhada mais famosa do rock. Descida cromática do baixo de Lá menor sobre arpejo.",
        description_en="The most famous fingerstyle rock intro. Chromatic descending bassline in A minor over arpeggios.",
        notes=[
            _sn("A2", 1.0, 1, 1, 0, "A2"),
            _sn("C4", 1.0, 2, 4, 1, "C4"),
            _sn("E4", 1.0, 3, 5, 0, "E4"),
            _sn("A4", 1.0, 4, 5, 5, "A4"),
            _sn("B4", 1.0, 4, 5, 7, "B4"),
            _sn("E4", 1.0, 3, 5, 0, "E4"),
            _sn("C4", 1.0, 2, 4, 1, "C4"),
            _sn("B4", 1.0, 4, 5, 7, "B4"),
            _sn("C5", 1.0, 5, 5, 8, "C5"),
            _sn("E4", 1.0, 3, 5, 0, "E4"),
            _sn("C4", 1.0, 2, 4, 1, "C4"),
            _sn("C5", 1.0, 5, 5, 8, "C5"),
            _sn("D5", 1.0, 5, 5, 10, "D5"),
            _sn("F#4", 1.0, 3, 5, 2, "F#4"),
            _sn("D4", 1.0, 2, 4, 3, "D4"),
            _sn("F4", 1.0, 2, 5, 1, "F4"),
            _sn("E4", 1.0, 1, 5, 0, "E4"),
            _sn("C4", 1.0, 2, 4, 1, "C4"),
            _sn("A3", 1.0, 1, 3, 2, "A3"),
            _sn("A3", 1.0, 1, 3, 2, "A3!"),
        ],
    ),

    # 14. NOTHING ELSE MATTERS (Metallica) — 7 Compassos em 6/8 = 21 Tempos
    Song(
        id="nothing_else_matters",
        title="Nothing Else Matters (Introdução)",
        composer="James Hetfield & Lars Ulrich",
        difficulty="Iniciante",
        difficulty_en="Beginner",
        bpm=142,
        clef="treble",
        instrument="guitar",
        time_signature="6/8",
        description="A introdução dedilhada com cordas soltas mais conhecida do metal. Perfeita para praticar dedilhado 6/8.",
        description_en="The famous open-string fingerpicked metal intro. Perfect for practicing 6/8 fingerstyle patterns.",
        notes=[
            _sn("E2", 1.0, 1, 0, 0, "Mi"),
            _sn("G3", 0.5, 2, 3, 0, "Sol"),
            _sn("B3", 0.5, 3, 4, 0, "Si"),
            _sn("E4", 1.0, 4, 5, 0, "Mi"),
            _sn("B3", 0.5, 3, 4, 0, "Si"),
            _sn("G3", 0.5, 2, 3, 0, "Sol"),
            _sn("E4", 1.5, 4, 5, 0, "Mi"),
            _sn("B3", 0.5, 3, 4, 0, "Si"),
            _sn("G3", 0.5, 2, 3, 0, "Sol"),
            _sn("E4", 1.0, 4, 5, 0, "Mi"),
            _sn("B3", 0.5, 3, 4, 0, "Si"),
            _sn("G3", 0.5, 2, 3, 0, "Sol"),
            _sn("E4", 1.5, 4, 5, 0, "Mi"),
            _sn("B3", 0.5, 3, 4, 0, "Si"),
            _sn("G3", 0.5, 2, 3, 0, "Sol"),
            _sn("B4", 1.0, 4, 5, 7, "Si"),
            _sn("G4", 0.5, 2, 5, 3, "Sol"),
            _sn("E4", 0.5, 1, 5, 0, "Mi"),
            _sn("E4", 1.0, 1, 5, 0, "Mi"),
            _sn("B3", 0.5, 3, 4, 0, "Si"),
            _sn("G3", 0.5, 2, 3, 0, "Sol"),
            _sn("E2", 3.0, 1, 0, 0, "Mi!"),
        ],
    ),

    # 15. ENTER SANDMAN (Metallica) — 4 Compassos em 4/4 = 16 Tempos
    Song(
        id="enter_sandman",
        title="Enter Sandman (Riff Principal)",
        composer="Metallica",
        difficulty="Iniciante",
        difficulty_en="Beginner",
        bpm=120,
        clef="treble",
        instrument="guitar",
        time_signature="4/4",
        description="O riff de abertura mais marcante do álbum 'Black Album' em Mi menor com 2ª menor (Fá) e arpejo característico.",
        description_en="The iconic opening riff from the 'Black Album' in E minor featuring a minor 2nd (F) and open strings arpeggio.",
        notes=[
            _sn("E2", 1.0, 1, 0, 0, "Mi"),
            _sn("E3", 1.0, 2, 2, 2, "Mi"),
            _sn("B3", 1.0, 3, 4, 0, "Si"),
            _sn("E4", 1.0, 4, 5, 0, "Mi"),
            _sn("G3", 1.0, 2, 3, 0, "Sol"),
            _sn("F3", 1.0, 2, 2, 3, "Fá"),
            _sn("E2", 2.0, 1, 0, 0, "Mi"),
            # Repetição do Riff
            _sn("E2", 1.0, 1, 0, 0, "Mi"),
            _sn("E3", 1.0, 2, 2, 2, "Mi"),
            _sn("B3", 1.0, 3, 4, 0, "Si"),
            _sn("E4", 1.0, 4, 5, 0, "Mi"),
            _sn("G3", 1.0, 2, 3, 0, "Sol"),
            _sn("F3", 1.0, 2, 2, 3, "Fá"),
            _sn("E2", 2.0, 1, 0, 0, "Mi!"),
        ],
    ),

    # 16. SMOKE ON THE WATER (Deep Purple) — 4 Compassos em 4/4 = 16 Tempos
    Song(
        id="smoke_on_the_water",
        title="Smoke on the Water (Riff Principal)",
        composer="Deep Purple",
        difficulty="Iniciante",
        difficulty_en="Beginner",
        bpm=112,
        clef="treble",
        instrument="guitar",
        time_signature="4/4",
        description="O riff de blues-rock em quartas paralelas mais reconhecido da história da guitarra.",
        description_en="The most famous blues-rock riff in fourths in electric guitar history.",
        notes=[
            _sn("G3", 1.5, 1, 3, 0, "Sol"),
            _sn("Bb3", 1.5, 2, 3, 3, "Sib"),
            _sn("C4", 1.0, 3, 3, 5, "Dó"),
            _sn("G3", 1.5, 1, 3, 0, "Sol"),
            _sn("Bb3", 1.5, 2, 3, 3, "Sib"),
            _sn("Db4", 0.5, 4, 3, 6, "Réb"),
            _sn("C4", 0.5, 3, 3, 5, "Dó"),
            _sn("G3", 1.5, 1, 3, 0, "Sol"),
            _sn("Bb3", 1.5, 2, 3, 3, "Sib"),
            _sn("C4", 1.0, 3, 3, 5, "Dó"),
            _sn("Bb3", 1.5, 2, 3, 3, "Sib"),
            _sn("G3", 2.5, 1, 3, 0, "Sol!"),
        ],
    ),

    # 17. POUR ÉLISE (Estudo Introdutório) — 6 Compassos em 3/8 = 9 Tempos
    Song(
        id="piano_fur_elise",
        title="Pour Élise (Estudo Introdutório)",
        composer="Ludwig van Beethoven",
        difficulty="Iniciante",
        difficulty_en="Beginner",
        bpm=130,
        clef="treble",
        instrument="piano",
        time_signature="3/8",
        description="Arranjo curto de estudo focado no motivo cromático inicial de Beethoven ao piano.",
        description_en="Short introductory study arrangement of Beethoven's famous motif for piano.",
        theory_analysis="""### 🎓 Análise Harmónica & Estrutural

• **Tonalidade**: Lá Menor Harmónica (Am).
• **Cadências & Harmonia**: Cadência autêntica perfeita **MiM7 → Lam** (grau V7 da escala menor harmónica), meia-cadência **Lam → MiM**, e cadência deceptiva **MiM → FáM** na secção contrastante.
• **Conexão com a Teoria**: Aplicação direta do **Capítulo 17 (Campo Harmónico Menor)** e **Capítulo 18 (Cadências)**, com o motivo semitonal inicial Mi - Ré♯ (E5 - D♯5).""",
        theory_analysis_en="""### 🎓 Harmonic & Structural Analysis

• **Key**: A Harmonic Minor (Am).
• **Cadences & Harmony**: Features a perfect authentic cadence **EM7 → Am** (degree V7 of the harmonic minor field), a half-cadence **Am → EM**, and a deceptive cadence **EM → FM** in the contrasting section.
• **Theory Link**: Direct application of **Chapter 17 (Minor Harmonic Field)** and **Chapter 18 (Cadences)**.""",
        notes=[
            _sn("E5", 0.5), _sn("D#5", 0.5), _sn("E5", 0.5),
            _sn("D#5", 0.5), _sn("E5", 0.5), _sn("B4", 0.5),
            _sn("D5", 0.5), _sn("C5", 0.5), _sn("A4", 0.5),
            _sn("C4", 0.5), _sn("E4", 0.5), _sn("A4", 0.5),
            _sn("B4", 1.0), _sn("E4", 0.5),
            _sn("G#4", 0.5), _sn("B4", 0.5), _sn("C5", 0.5),
        ]
    ),

    # 18. SONATA AO LUAR — 2 Compassos em 4/4 = 8 Tempos
    Song(
        id="piano_moonlight",
        title="Sonata ao Luar (Adagio)",
        composer="Ludwig van Beethoven",
        difficulty="Intermédio",
        difficulty_en="Intermediate",
        bpm=60,
        clef="bass",
        instrument="piano",
        time_signature="4/4",
        description="Famoso adágio da Sonata ao Luar, focado no piano.",
        description_en="Famous adagio from the Moonlight Sonata, focused on the piano.",
        theory_analysis="""### 🎓 Análise Harmónica & Estrutural

• **Tonalidade**: Dó♯ Menor (C♯m).
• **Arpejo Triádico**: O acompanhamento desdobra tríades em colcheias ternárias (**Sol♯ - Dó♯ - Mi**).
• **Conexão com a Teoria**: Aplicação direta do **Capítulo 4 (Formação de Tríades & Inversões)**.""",
        theory_analysis_en="""### 🎓 Harmonic & Structural Analysis

• **Key**: C♯ Minor (C♯m).
• **Triadic Arpeggio**: The accompaniment unfolds triads in triplet eighths (**G♯ - C♯ - E**).
• **Theory Link**: Direct application of **Chapter 4 (Triad Construction & Inversions)**.""",
        notes=[
            _sn("G#3", 1.0), _sn("C#4", 1.0), _sn("E4", 1.0), _sn("G#3", 1.0),
            _sn("C#4", 1.0), _sn("E4", 1.0), _sn("G#3", 1.0), _sn("C#4", 1.0)
        ]
    ),

    # 19. GYMNOPÉDIE NO. 1 — 3 Compassos em 3/4 = 9 Tempos
    Song(
        id="piano_gymnopedie",
        title="Gymnopédie No. 1",
        composer="Erik Satie",
        difficulty="Intermédio",
        difficulty_en="Intermediate",
        bpm=75,
        clef="treble",
        instrument="piano",
        time_signature="3/4",
        description="Melodia etérea de Satie.",
        description_en="Ethereal melody by Satie.",
        theory_analysis="""### 🎓 Análise Harmónica & Estrutural

• **Tonalidade**: Ré Maior (D Major) / Modo Jónico.
• **Progressão**: Alternância suave entre **Gmaj7** e **Dmaj7**.
• **Conexão com a Teoria**: Ilustra o **Capítulo 5 (Tétrades maj7)**.""",
        theory_analysis_en="""### 🎓 Harmonic & Structural Analysis

• **Key**: D Major / Ionian Mode.
• **Progression**: Smooth oscillation between **Gmaj7** and **Dmaj7**.
• **Theory Link**: Demonstrates **Chapter 5 (maj7 Seventh Chords)**.""",
        notes=[_sn("F#4", 2.0), _sn("A4", 1.0), _sn("G4", 2.0), _sn("F#4", 1.0), _sn("C#4", 3.0)]
    ),

    # 20. CÂNONE EM DÓ MAIOR — 2 Compassos em 4/4 = 8 Tempos
    Song(
        id="piano_canon_c",
        title="Cânone em Dó Maior (Linha de Baixo)",
        composer="Johann Pachelbel",
        difficulty="Iniciante",
        difficulty_en="Beginner",
        bpm=90,
        clef="treble",
        instrument="piano",
        time_signature="4/4",
        description="Clássico cânone focado na progressão harmónica ao piano.",
        description_en="Classic canon focused on harmonic ground bass progression.",
        theory_analysis="""### 🎓 Análise Harmónica & Estrutural

• **Tonalidade**: Dó Maior.
• **Progressão de Baixo Ostinato**: **I - V - vi - iii - IV - I - IV - V** (C - G - Am - Em - F - C - F - G).
• **Conexão com a Teoria**: Uma das progressões encadeadas mais célebres da história, explicada no **Capítulo 5 (Campo Harmónico Maior)**.""",
        theory_analysis_en="""### 🎓 Harmonic & Structural Analysis

• **Key**: C Major.
• **Ground Bass Progression**: **I - V - vi - iii - IV - I - IV - V** (C - G - Am - Em - F - C - F - G).
• **Theory Link**: One of the most iconic harmonic sequences in history, featured in **Chapter 5 (Major Diatonic Field)**.""",
        notes=[_sn("C4", 1.0), _sn("G3", 1.0), _sn("A3", 1.0), _sn("E3", 1.0), _sn("F3", 1.0), _sn("C3", 1.0), _sn("F3", 1.0), _sn("G3", 1.0)]
    ),

    # 21. MALAGUEÑA — 2 Compassos em 3/4 = 6 Tempos
    Song(
        id="guitar_malaguena",
        title="Malagueña (Tema Flamenco)",
        composer="Tradicional Espanhol",
        difficulty="Iniciante",
        difficulty_en="Beginner",
        bpm=120,
        clef="treble",
        instrument="guitar",
        time_signature="3/4",
        description="Tradicional tema espanhol para viola.",
        description_en="Traditional Spanish theme for guitar.",
        theory_analysis="""### 🎓 Análise Harmónica & Estrutural

• **Tonalidade / Modo**: Frígio Dominante de Mi (E Phrygian Dominant).
• **Progressão Harmónica**: **Am → G → F → E** (iv - ♭III - ♭II - I com I Maior característico do flamenco).
• **Conexão com a Teoria**: Demonstração do uso da terça maior no modo frígio para a cadência andaluza flamenca.""",
        theory_analysis_en="""### 🎓 Harmonic & Structural Analysis

• **Key / Mode**: E Phrygian Dominant.
• **Progression**: **Am → G → F → E** (iv - ♭III - ♭II - I with Major I characteristic of flamenco).
• **Theory Link**: Showcase of Andalusian cadence using a major tonic chord.""",
        notes=[_sn("E4", 1.0), _sn("F4", 1.0), _sn("E4", 1.0), _sn("D4", 1.0), _sn("C4", 1.0), _sn("B3", 1.0)]
    ),

    # 22. THE HOUSE OF THE RISING SUN — 2 Compassos em 6/8 = 6 Tempos
    Song(
        id="guitar_house_rising_sun",
        title="The House of the Rising Sun",
        composer="Tradicional / Folk",
        difficulty="Intermédio",
        difficulty_en="Intermediate",
        bpm=110,
        clef="treble",
        instrument="guitar",
        time_signature="6/8",
        description="Clássico folk americano.",
        description_en="American folk classic.",
        theory_analysis="""### 🎓 Análise Harmónica & Estrutural

• **Tonalidade**: Lá Eólio (menor natural) em métrica de 6/8.
• **Progressão Harmónica**: **Am – C – D – F – Am – E** (i – III – IV – VI – i – V). O acorde Ré Maior (IV maior) atua como empréstimo modal com coloração Dórica/Maior, enquanto Mi Maior (V) provém da escala menor harmónica para fornecer cadência autêntica de regresso à tónica.
• **Conexão com a Teoria**: Exemplo magistral do **Capítulo 17 (Campo Harmónico Menor)** e arpejos em métrica composta (**Capítulo 9**).""",
        theory_analysis_en="""### 🎓 Harmonic & Structural Analysis

• **Key**: A Aeolian (natural minor) in 6/8 compound time.
• **Progression**: **Am – C – D – F – Am – E** (i – III – IV – VI – i – V). The D Major (IV) chord acts as a modal borrowing providing Dorian/Major flavor, while E Major (V) is borrowed from the harmonic minor scale for an authentic cadence.
• **Theory Link**: Masterful demonstration of **Chapter 17 (Minor Harmonic Field)** and compound time arpeggios (**Chapter 9**).""",
        notes=[
            _sn("A3", 0.5), _sn("C4", 0.5), _sn("E4", 0.5), _sn("A4", 0.5), _sn("E4", 0.5), _sn("C4", 0.5),
            _sn("D4", 0.5), _sn("F4", 0.5), _sn("A4", 0.5), _sn("D5", 0.5), _sn("A4", 0.5), _sn("F4", 0.5),
        ]
    ),

    # 23. ROMANCE ANÓNIMO — 2 Compassos em 3/4 = 6 Tempos
    Song(
        id="guitar_spanish_romance",
        title="Romance Anónimo (Romance de Amor)",
        composer="Tradicional Espanhol",
        difficulty="Intermédio",
        difficulty_en="Intermediate",
        bpm=84,
        clef="treble",
        instrument="guitar",
        time_signature="3/4",
        description="Famosa melodia tradicional de violão.",
        description_en="Famous traditional guitar melody.",
        theory_analysis="""### 🎓 Análise Harmónica & Estrutural

• **Tonalidade**: Mi Menor (Em) transitando para Mi Maior (E).
• **Estrutura Ternária**: Parte A em tom menor (melancólico) e Parte B em tom maior (luminoso).
• **Conexão com a Teoria**: Aplicação prática de **Mútua Homónima (Capítulo 3 & 6)**.""",
        theory_analysis_en="""### 🎓 Harmonic & Structural Analysis

• **Key**: E Minor (Em) shifting to E Major (E).
• **Ternary Structure**: Part A in minor, Part B in major.
• **Theory Link**: Direct demonstration of parallel major/minor interchange.""",
        notes=[_sn("B4", 1.0), _sn("B4", 1.0), _sn("B4", 1.0), _sn("B4", 1.0), _sn("A4", 1.0), _sn("G4", 1.0)]
    ),

    # 24. GREENSLEEVES (Arranjo para Viola) — 2 Compassos em 6/8 = 6 Tempos
    Song(
        id="guitar_greensleeves_full",
        title="Greensleeves (Estudo Dedilhado em 6/8 para Viola)",
        composer="Tradicional Inglês",
        difficulty="Iniciante",
        difficulty_en="Beginner",
        bpm=100,
        clef="treble",
        instrument="guitar",
        time_signature="6/8",
        description="Arranjo dedilhado de estudo renascentista para viola em compasso composto 6/8.",
        description_en="Fingerstyle Renaissance study arrangement for guitar in 6/8 compound time.",
        theory_analysis="""### 🎓 Análise Harmónica & Estrutural

• **Tonalidade / Modo**: Lá menor (Modo Eólio).
• **Estrutura de Compasso**: O ritmo 6/8 dá à melodia o seu balanço folclórico característico (dois pulsos pontuados por compasso).
• **Conexão com a Teoria**: Aplicação perfeita do **Capítulo 9 (Fórmulas de Compasso Compostas)**.""",
        theory_analysis_en="""### 🎓 Harmonic & Structural Analysis

• **Key / Mode**: A minor (Aeolian Mode).
• **Time Signature Structure**: The 6/8 meter provides the characteristic folk sway (two dotted beats per bar).
• **Theory Link**: Perfect showcase of **Chapter 9 (Compound Time Signatures)**.""",
        notes=[
            _sn("A3", 0.5), _sn("C4", 0.5), _sn("D4", 0.5), _sn("E4", 1.0), _sn("F4", 0.5),
            _sn("E4", 1.0), _sn("D4", 0.5), _sn("B3", 1.0), _sn("G3", 0.5),
        ]
    ),
]


# Compatibility aliases
REPERTOIRE_SONGS = SONG_LIBRARY


# Auto-assign piano fingerings and guitar coordinates for notes that don't have explicit values
from core.fingering import assign_piano_fingerings
from core.guitar import assign_guitar_coordinates

for _song in SONG_LIBRARY:
    _raw_notes = [_sn_item.note for _sn_item in _song.notes]
    _p_fingers = assign_piano_fingerings(_raw_notes)
    _g_coords = assign_guitar_coordinates(_raw_notes)
    for _i, _sn_item in enumerate(_song.notes):
        if _sn_item.piano_finger is None and _i < len(_p_fingers):
            _sn_item.piano_finger = _p_fingers[_i]
        if (_sn_item.guitar_string is None or _sn_item.guitar_fret is None) and _i < len(_g_coords):
            _sn_item.guitar_string, _sn_item.guitar_fret = _g_coords[_i]


def get_song_by_id(song_id: str) -> Optional[Song]:
    for song in SONG_LIBRARY:
        if song.id == song_id:
            return song
    return None
