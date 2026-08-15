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
    clef: str = "treble"  # "treble" ou "bass"
    time_signature: str = "4/4"
    description: str = ""
    notes: List[SongNote] = field(default_factory=list)

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
    # 1. HINO À ALEGRIA (Beethoven) — Peça Completa (Parte A + B + Reprise)
    Song(
        id="ode_to_joy",
        title="Hino à Alegria (9ª Sinfonia)",
        composer="Ludwig van Beethoven",
        difficulty="Iniciante",
        bpm=108,
        clef="treble",
        description="O tema imortal da Nona Sinfonia de Beethoven na íntegra. Melodia por graus conjuntos com frase A, ponte B e conclusão solene.",
        notes=[
            # Frase A
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
            # Frase A' (Variação com resolução em Dó)
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
            # Ponte B
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
            _sn("D4", 1.0, 2, 4, 3, "za!"),
            # Conclusão Reprise A
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

    # 2. BRILHA, BRILHA ESTRELINHA (Mozart) — Peça Completa (Forma Ternária A-B-A)
    Song(
        id="twinkle_star",
        title="Brilha, Brilha Estrelinha (Completo A-B-A)",
        composer="W. A. Mozart / Tradicional",
        difficulty="Iniciante",
        bpm=100,
        clef="treble",
        description="A famosa melodia infantil clássica na sua forma ternária completa (Tema A + Frase do Meio B + Reprise A).",
        notes=[
            # Parte A
            _sn("C4", 1.0, 1, 4, 1, "Bri-"),
            _sn("C4", 1.0, 1, 4, 1, "lha,"),
            _sn("G4", 1.0, 5, 5, 3, "bri-"),
            _sn("G4", 1.0, 5, 5, 3, "lha,"),
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
            # Parte B
            _sn("G4", 1.0, 5, 5, 3, "Lá"),
            _sn("G4", 1.0, 5, 5, 3, "no"),
            _sn("F4", 1.0, 4, 5, 1, "al-"),
            _sn("F4", 1.0, 4, 5, 1, "to,"),
            _sn("E4", 1.0, 3, 5, 0, "a"),
            _sn("E4", 1.0, 3, 5, 0, "bri-"),
            _sn("D4", 2.0, 2, 4, 3, "lhar,"),
            _sn("G4", 1.0, 5, 5, 3, "co-"),
            _sn("G4", 1.0, 5, 5, 3, "mo_um"),
            _sn("F4", 1.0, 4, 5, 1, "di-"),
            _sn("F4", 1.0, 4, 5, 1, "a-"),
            _sn("E4", 1.0, 3, 5, 0, "man-"),
            _sn("E4", 1.0, 3, 5, 0, "te_ao"),
            _sn("D4", 2.0, 2, 4, 3, "luar."),
            # Reprise A
            _sn("C4", 1.0, 1, 4, 1, "Bri-"),
            _sn("C4", 1.0, 1, 4, 1, "lha,"),
            _sn("G4", 1.0, 5, 5, 3, "bri-"),
            _sn("G4", 1.0, 5, 5, 3, "lha,"),
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

    # 3. PAPAGAIO LOIRO (Cantiga Popular Portuguesa Completa)
    Song(
        id="papagaio_loiro",
        title="Papagaio Loiro (Cantiga Tradicional Completa)",
        composer="Folclore Português",
        difficulty="Iniciante",
        bpm=110,
        clef="treble",
        description="Cantiga tradicional portuguesa completa em dois andamentos com letra tradicional integral.",
        notes=[
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
            # 2ª Frase
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
            # Refrão
            _sn("G4", 1.0, 5, 5, 3, "Que_es-"),
            _sn("E4", 1.0, 3, 5, 0, "tá"),
            _sn("G4", 1.0, 5, 5, 3, "na"),
            _sn("E4", 1.0, 3, 5, 0, "es-"),
            _sn("G4", 1.0, 5, 5, 3, "co-"),
            _sn("A4", 1.0, 5, 5, 5, "la"),
            _sn("G4", 1.0, 4, 5, 3, "a"),
            _sn("F4", 1.0, 3, 5, 1, "a-"),
            _sn("E4", 1.0, 2, 5, 0, "pren-"),
            _sn("D4", 2.0, 1, 4, 3, "der!"),
        ],
    ),

    # 4. POMBINHA BRANCA (Tradicional Portuguesa Completa)
    Song(
        id="pombinha_branca",
        title="Pombinha Branca (Cantiga Completa)",
        composer="Folclore Português",
        difficulty="Iniciante",
        bpm=96,
        clef="treble",
        description="Melodia suave e completa do cancioneiro tradicional português.",
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
            _sn("G4", 2.0, 5, 5, 3, "fa-zer?"),
            _sn("G4", 1.0, 5, 5, 3, "Es-"),
            _sn("E4", 1.0, 3, 5, 0, "tou"),
            _sn("C4", 1.0, 1, 4, 1, "a"),
            _sn("E4", 1.0, 3, 5, 0, "la-"),
            _sn("D4", 1.0, 2, 4, 3, "var"),
            _sn("D4", 1.0, 2, 4, 3, "a"),
            _sn("D4", 1.0, 2, 4, 3, "rou-"),
            _sn("E4", 1.0, 3, 5, 0, "pa"),
            _sn("D4", 1.0, 2, 4, 3, "pro"),
            _sn("C4", 2.0, 1, 4, 1, "meu_bem!"),
        ],
    ),

    # 5. FÜR ELISE (Beethoven) — Tema Principal Completo com Transição
    Song(
        id="fur_elise",
        title="Für Elise (Tema Principal Completo)",
        composer="Ludwig van Beethoven",
        difficulty="Intermédio",
        bpm=120,
        clef="treble",
        time_signature="3/4",
        description="A célebre Bagatela em Lá menor (WoO 59) de Beethoven com o motivo cromático inicial, arpejos de Lá menor e Mi Maior e cadência harmónica.",
        notes=[
            _sn("E5", 1.0, 5, 5, 12, "Mi"),
            _sn("D#5", 1.0, 4, 5, 11, "Ré#"),
            _sn("E5", 1.0, 5, 5, 12, "Mi"),
            _sn("D#5", 1.0, 4, 5, 11, "Ré#"),
            _sn("E5", 1.0, 5, 5, 12, "Mi"),
            _sn("B4", 1.0, 3, 5, 7, "Si"),
            _sn("D5", 1.0, 4, 5, 10, "Ré"),
            _sn("C5", 1.0, 3, 5, 8, "Dó"),
            _sn("A4", 2.0, 1, 5, 5, "Lá"),
            # Arpejo Dó-Mi-Lá-Si
            _sn("C4", 1.0, 1, 4, 1, "Dó"),
            _sn("E4", 1.0, 2, 5, 0, "Mi"),
            _sn("A4", 1.0, 3, 5, 5, "Lá"),
            _sn("B4", 2.0, 4, 5, 7, "Si"),
            # Arpejo Mi-Sol#-Si-Dó
            _sn("E4", 1.0, 1, 5, 0, "Mi"),
            _sn("G#4", 1.0, 2, 5, 4, "Sol#"),
            _sn("B4", 1.0, 3, 5, 7, "Si"),
            _sn("C5", 2.0, 4, 5, 8, "Dó"),
            # Reprise com resolução final em Lá
            _sn("E4", 1.0, 1, 5, 0, "Mi"),
            _sn("E5", 1.0, 5, 5, 12, "Mi"),
            _sn("D#5", 1.0, 4, 5, 11, "Ré#"),
            _sn("E5", 1.0, 5, 5, 12, "Mi"),
            _sn("D#5", 1.0, 4, 5, 11, "Ré#"),
            _sn("E5", 1.0, 5, 5, 12, "Mi"),
            _sn("B4", 1.0, 3, 5, 7, "Si"),
            _sn("D5", 1.0, 4, 5, 10, "Ré"),
            _sn("C5", 1.0, 3, 5, 8, "Dó"),
            _sn("A4", 2.0, 1, 5, 5, "Lá"),
            _sn("C4", 1.0, 1, 4, 1, "Dó"),
            _sn("E4", 1.0, 2, 5, 0, "Mi"),
            _sn("A4", 1.0, 3, 5, 5, "Lá"),
            _sn("B4", 1.5, 4, 5, 7, "Si"),
            _sn("C5", 0.5, 3, 5, 8, "Dó"),
            _sn("B4", 0.5, 2, 5, 7, "Si"),
            _sn("A4", 2.5, 1, 5, 5, "Lá!"),
        ],
    ),

    # 6. MINUETO EM SOL (Bach / Petzold) — Seção A Completa (16 Compassos)
    Song(
        id="minuet_in_g",
        title="Minueto em Sol Maior (Seção A Completa)",
        composer="Christian Petzold / J. S. Bach",
        difficulty="Intermédio",
        bpm=116,
        clef="treble",
        time_signature="3/4",
        description="Do Pequeno Livro de Anna Magdalena Bach. A Seção A completa de 16 compassos em Sol Maior.",
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
            # Segunda Frase com Cadência
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
            _sn("F#4", 0.5, 1, 5, 2, "Fá#"),
            _sn("G4", 0.5, 1, 5, 3, "Sol"),
            _sn("A4", 0.5, 2, 5, 5, "Lá"),
            _sn("B4", 0.5, 3, 5, 7, "Si"),
            _sn("G4", 1.0, 1, 5, 3, "Sol"),
            _sn("A4", 2.0, 2, 5, 5, "Lá"),
        ],
    ),

    # 7. MARCHA NUPCIAL (Wagner) — Tema Coral Completo
    Song(
        id="bridal_chorus",
        title="Marcha Nupcial (Trevo Coral Completo)",
        composer="Richard Wagner (Lohengrin)",
        difficulty="Iniciante",
        bpm=88,
        clef="treble",
        description="A clássica marcha nupcial tocada em cerimónias no mundo inteiro, com melodia solene integral e frase central.",
        notes=[
            _sn("C4", 1.0, 1, 4, 1, "Dó"),
            _sn("F4", 1.5, 3, 5, 1, "Fá"),
            _sn("F4", 0.5, 3, 5, 1, "Fá"),
            _sn("F4", 1.0, 3, 5, 1, "Fá"),
            _sn("C4", 0.5, 1, 4, 1, "Dó"),
            _sn("G4", 1.5, 5, 5, 3, "Sol"),
            _sn("E4", 0.5, 2, 5, 0, "Mi"),
            _sn("F4", 2.0, 3, 5, 1, "Fá"),
            # Segunda Frase
            _sn("C4", 1.0, 1, 4, 1, "Dó"),
            _sn("F4", 1.5, 3, 5, 1, "Fá"),
            _sn("A4", 0.5, 5, 5, 5, "Lá"),
            _sn("F4", 1.0, 3, 5, 1, "Fá"),
            _sn("C4", 0.5, 1, 4, 1, "Dó"),
            _sn("G4", 1.5, 5, 5, 3, "Sol"),
            _sn("E4", 0.5, 2, 5, 0, "Mi"),
            _sn("F4", 2.0, 3, 5, 1, "Fá"),
            # Meio Solene
            _sn("A4", 1.0, 4, 5, 5, "Lá"),
            _sn("A4", 1.0, 4, 5, 5, "Lá"),
            _sn("G4", 1.0, 3, 5, 3, "Sol"),
            _sn("F4", 1.0, 2, 5, 1, "Fá"),
            _sn("G4", 1.0, 3, 5, 3, "Sol"),
            _sn("A4", 1.0, 4, 5, 5, "Lá"),
            _sn("F4", 2.0, 2, 5, 1, "Fá"),
        ],
    ),

    # 8. CANON EM DÓ / RÉ (Pachelbel) — Tema e Variação Completa
    Song(
        id="canon_in_d",
        title="Canon em Dó / Ré (Tema & Variação Completa)",
        composer="Johann Pachelbel",
        difficulty="Iniciante",
        bpm=76,
        clef="treble",
        description="A progressão harmónica e melodia barroca mais famosa de sempre, com o tema principal e a sua variação em colcheias.",
        notes=[
            # Tema Principal
            _sn("E4", 1.0, 3, 5, 0, "Mi"),
            _sn("D4", 1.0, 2, 4, 3, "Ré"),
            _sn("C4", 1.0, 1, 4, 1, "Dó"),
            _sn("B3", 1.0, 1, 4, 0, "Si"),
            _sn("A3", 1.0, 1, 3, 2, "Lá"),
            _sn("G3", 1.0, 1, 3, 0, "Sol"),
            _sn("A3", 1.0, 1, 3, 2, "Lá"),
            _sn("B3", 1.0, 2, 4, 0, "Si"),
            # Variação em Graus Conjuntos
            _sn("C4", 1.0, 3, 4, 1, "Dó"),
            _sn("B3", 1.0, 2, 4, 0, "Si"),
            _sn("A3", 1.0, 1, 3, 2, "Lá"),
            _sn("G3", 1.0, 1, 3, 0, "Sol"),
            _sn("F3", 1.0, 1, 2, 3, "Fá"),
            _sn("E3", 1.0, 1, 2, 2, "Mi"),
            _sn("F3", 1.0, 1, 2, 3, "Fá"),
            _sn("G3", 1.0, 2, 3, 0, "Sol"),
            # Frase Final
            _sn("E4", 0.5, 3, 5, 0, "Mi"),
            _sn("G4", 0.5, 5, 5, 3, "Sol"),
            _sn("A4", 0.5, 5, 5, 5, "Lá"),
            _sn("G4", 0.5, 4, 5, 3, "Sol"),
            _sn("F4", 0.5, 3, 5, 1, "Fá"),
            _sn("E4", 0.5, 2, 5, 0, "Mi"),
            _sn("F4", 0.5, 3, 5, 1, "Fá"),
            _sn("D4", 0.5, 1, 4, 3, "Ré"),
            _sn("C4", 2.0, 1, 4, 1, "Dó!"),
        ],
    ),

    # 9. EINE KLEINE NACHTMUSIK (Mozart) — Allegro Completo
    Song(
        id="nachtmusik",
        title="Eine kleine Nachtmusik (Serenata K. 525 Completa)",
        composer="Wolfgang Amadeus Mozart",
        difficulty="Intermédio",
        bpm=124,
        clef="treble",
        description="O brilhante motivo de abertura em Sol Maior da serenata mais tocada de Mozart na sua forma completa com resolução.",
        notes=[
            _sn("G4", 1.5, 1, 5, 3, "Sol"),
            _sn("D4", 0.5, 1, 4, 3, "Ré"),
            _sn("G4", 1.0, 1, 5, 3, "Sol"),
            _sn("D4", 1.0, 1, 4, 3, "Ré"),
            _sn("G4", 0.5, 1, 5, 3, "Sol"),
            _sn("B4", 0.5, 3, 5, 7, "Si"),
            _sn("D5", 1.0, 5, 5, 10, "Ré"),
            _sn("C5", 1.5, 4, 5, 8, "Dó"),
            _sn("A4", 0.5, 2, 5, 5, "Lá"),
            _sn("C5", 1.0, 4, 5, 8, "Dó"),
            _sn("A4", 1.0, 2, 5, 5, "Lá"),
            _sn("F#4", 0.5, 1, 5, 2, "Fá#"),
            _sn("A4", 0.5, 2, 5, 5, "Lá"),
            _sn("D4", 1.0, 1, 4, 3, "Ré"),
            # Segunda Frase
            _sn("B4", 1.0, 3, 5, 7, "Si"),
            _sn("B4", 0.5, 3, 5, 7, "Si"),
            _sn("C5", 0.5, 4, 5, 8, "Dó"),
            _sn("D5", 1.0, 5, 5, 10, "Ré"),
            _sn("D5", 0.5, 5, 5, 10, "Ré"),
            _sn("C5", 0.5, 4, 5, 8, "Dó"),
            _sn("B4", 0.5, 3, 5, 7, "Si"),
            _sn("A4", 0.5, 2, 5, 5, "Lá"),
            _sn("G4", 1.0, 1, 5, 3, "Sol"),
            _sn("G4", 0.5, 1, 5, 3, "Sol"),
            _sn("A4", 0.5, 2, 5, 5, "Lá"),
            _sn("B4", 1.0, 3, 5, 7, "Si"),
            _sn("B4", 0.5, 3, 5, 7, "Si"),
            _sn("A4", 0.5, 2, 5, 5, "Lá"),
            _sn("G4", 0.5, 1, 5, 3, "Sol"),
            _sn("F#4", 0.5, 1, 5, 2, "Fá#"),
            _sn("G4", 2.0, 1, 5, 3, "Sol!"),
        ],
    ),

    # 10. GREENSLEEVES (Tradicional Inglesa) — Verso & Refrão Completo
    Song(
        id="greensleeves",
        title="Greensleeves (Verso & Refrão Completo)",
        composer="Tradicional Século XVI",
        difficulty="Intermédio",
        bpm=92,
        clef="treble",
        description="Clássico do período Tudor em modo Dórico e Menor Melódico, com verso integral e refrão tradicional.",
        notes=[
            # Verso
            _sn("A4", 1.0, 1, 5, 5, "A-"),
            _sn("C5", 1.5, 3, 5, 8, "las,"),
            _sn("D5", 0.5, 4, 5, 10, "my"),
            _sn("E5", 1.0, 5, 5, 12, "love,"),
            _sn("F5", 0.5, 5, 5, 13, "you"),
            _sn("E5", 0.5, 5, 5, 12, "do"),
            _sn("D5", 1.0, 4, 5, 10, "me"),
            _sn("B4", 1.5, 2, 5, 7, "wrong,"),
            _sn("G4", 0.5, 1, 5, 3, "to"),
            _sn("A4", 1.0, 2, 5, 5, "cast"),
            _sn("B4", 0.5, 3, 5, 7, "me"),
            _sn("C5", 1.5, 4, 5, 8, "off"),
            _sn("A4", 2.0, 2, 5, 5, "dis-"),
            # Refrão
            _sn("G5", 2.0, 5, 5, 15, "Green-"),
            _sn("G5", 1.0, 5, 5, 15, "sleeves"),
            _sn("F5", 0.5, 5, 5, 13, "was"),
            _sn("E5", 0.5, 5, 5, 12, "all"),
            _sn("D5", 1.0, 4, 5, 10, "my"),
            _sn("B4", 1.5, 2, 5, 7, "joy,"),
            _sn("G4", 0.5, 1, 5, 3, "and"),
            _sn("A4", 1.0, 2, 5, 5, "who"),
            _sn("B4", 0.5, 3, 5, 7, "but"),
            _sn("C5", 1.5, 4, 5, 8, "my"),
            _sn("A4", 2.0, 2, 5, 5, "la-dy!"),
        ],
    ),

    # 11. O CRAVO E A ROSA (Tradicional Portuguesa Completa)
    Song(
        id="cravo_e_rosa",
        title="O Cravo e a Rosa (Cantiga Completa)",
        composer="Cancioneiro Popular",
        difficulty="Iniciante",
        bpm=104,
        clef="treble",
        description="Famosa cantiga de roda da tradição lusófona na sua versão integral de 4 estrofes.",
        notes=[
            _sn("C4", 1.0, 1, 4, 1, "O"),
            _sn("C4", 1.0, 1, 4, 1, "cra-"),
            _sn("G4", 1.0, 5, 5, 3, "vo"),
            _sn("G4", 1.0, 5, 5, 3, "bri-"),
            _sn("A4", 1.0, 5, 5, 5, "gou"),
            _sn("A4", 1.0, 5, 5, 5, "com"),
            _sn("G4", 2.0, 4, 5, 3, "a"),
            _sn("F4", 1.0, 4, 5, 1, "ro-"),
            _sn("F4", 1.0, 4, 5, 1, "sa,"),
            _sn("E4", 1.0, 3, 5, 0, "de-"),
            _sn("E4", 1.0, 3, 5, 0, "bai-"),
            _sn("D4", 1.0, 2, 4, 3, "xo"),
            _sn("D4", 1.0, 2, 4, 3, "de"),
            _sn("C4", 2.0, 1, 4, 1, "u-ma"),
            _sn("G4", 1.0, 5, 5, 3, "sa-"),
            _sn("G4", 1.0, 5, 5, 3, "ca-"),
            _sn("F4", 1.0, 4, 5, 1, "da;"),
            _sn("E4", 1.0, 3, 5, 0, "o"),
            _sn("E4", 1.0, 3, 5, 0, "cra-"),
            _sn("D4", 1.0, 2, 4, 3, "vo"),
            _sn("D4", 1.0, 2, 4, 3, "sa-"),
            _sn("C4", 2.0, 1, 4, 1, "iu ferido!"),
        ],
    ),

    # 12. GRÂNDOLA, VILA MORENA (Zeca Afonso) — Hino Completo
    Song(
        id="grandola",
        title="Grândola, Vila Morena (Hino Completo)",
        composer="José Afonso (Zeca Afonso)",
        difficulty="Iniciante",
        bpm=84,
        clef="treble",
        description="O hino histórico da Revolução dos Cravos de 1974 na íntegra com a estrofe completa e cadência solene.",
        notes=[
            _sn("C4", 1.0, 1, 4, 1, "Grân-"),
            _sn("D4", 1.0, 2, 4, 3, "do-"),
            _sn("E4", 1.5, 3, 5, 0, "la,"),
            _sn("F4", 0.5, 4, 5, 1, "vi-"),
            _sn("E4", 1.0, 3, 5, 0, "la"),
            _sn("D4", 1.0, 2, 4, 3, "mo-"),
            _sn("C4", 2.0, 1, 4, 1, "re-na,"),
            _sn("D4", 1.0, 2, 4, 3, "ter-"),
            _sn("E4", 1.0, 3, 5, 0, "ra"),
            _sn("C4", 1.0, 1, 4, 1, "da"),
            _sn("D4", 1.0, 2, 4, 3, "fra-"),
            _sn("C4", 2.0, 1, 4, 1, "ter-ni-da-de,"),
            # Segunda Estrofe
            _sn("E4", 1.0, 3, 5, 0, "em"),
            _sn("F4", 1.0, 4, 5, 1, "ca-"),
            _sn("G4", 1.5, 5, 5, 3, "da"),
            _sn("A4", 0.5, 5, 5, 5, "es-"),
            _sn("G4", 1.0, 4, 5, 3, "qui-"),
            _sn("F4", 1.0, 3, 5, 1, "na"),
            _sn("E4", 2.0, 2, 5, 0, "um_amigo,"),
            _sn("F4", 1.0, 3, 5, 1, "em"),
            _sn("G4", 1.0, 4, 5, 3, "ca-"),
            _sn("E4", 1.0, 2, 5, 0, "da"),
            _sn("F4", 1.0, 3, 5, 1, "ros-"),
            _sn("E4", 2.0, 2, 5, 0, "to_i-gual-da-de!"),
        ],
    ),
    # 13. STAIRWAY TO HEAVEN (Led Zeppelin) — Introdução Acústica
    Song(
        id="stairway_to_heaven",
        title="Stairway to Heaven (Intro Acústica)",
        composer="Jimmy Page & Robert Plant (Led Zeppelin)",
        difficulty="Iniciante",
        bpm=76,
        clef="treble",
        description="O lendário arpejo dedilhado em Lá menor que abre uma das maiores obras do rock. Simples e memorável para tocar na viola e no piano.",
        notes=[
            _sn("A3", 1.0, 1, 3, 2, "Lá"),
            _sn("C4", 1.0, 2, 4, 1, "Dó"),
            _sn("E4", 1.0, 3, 5, 0, "Mi"),
            _sn("A4", 1.0, 5, 5, 5, "Lá"),
            _sn("B4", 1.0, 5, 5, 7, "Si"),
            _sn("E4", 1.0, 3, 5, 0, "Mi"),
            _sn("C4", 1.0, 2, 4, 1, "Dó"),
            _sn("B4", 1.0, 5, 5, 7, "Si"),
            _sn("C5", 1.0, 5, 5, 8, "Dó"),
            _sn("E4", 1.0, 3, 5, 0, "Mi"),
            _sn("C4", 1.0, 2, 4, 1, "Dó"),
            _sn("C5", 1.0, 5, 5, 8, "Dó"),
            _sn("F#4", 1.0, 4, 5, 2, "Fá#"),
            _sn("D4", 1.0, 2, 4, 3, "Ré"),
            _sn("A3", 1.0, 1, 3, 2, "Lá"),
            _sn("F4", 1.0, 3, 5, 1, "Fá"),
            _sn("E4", 1.0, 2, 5, 0, "Mi"),
            _sn("C4", 1.0, 1, 4, 1, "Dó"),
            _sn("A3", 2.0, 1, 3, 2, "Lá!"),
        ],
    ),

    # 14. NOTHING ELSE MATTERS (Metallica) — Introdução Clássica em Cordas Soltas
    Song(
        id="nothing_else_matters",
        title="Nothing Else Matters (Intro Dedilhada)",
        composer="James Hetfield & Lars Ulrich (Metallica)",
        difficulty="Iniciante",
        bpm=70,
        clef="treble",
        time_signature="6/8",
        description="A introdução mais famosa do heavy metal acústico. Toca-se inteiramente em cordas soltas no Mi menor (E2, G3, B3, E4) antes do tema principal.",
        notes=[
            # Arpejo de Cordas Soltas (Mi Menor)
            _sn("E2", 1.0, 1, 0, 0, "Mi"),
            _sn("G3", 1.0, 1, 3, 0, "Sol"),
            _sn("B3", 1.0, 2, 4, 0, "Si"),
            _sn("E4", 1.5, 3, 5, 0, "Mi"),
            _sn("B3", 0.5, 2, 4, 0, "Si"),
            _sn("G3", 1.0, 1, 3, 0, "Sol"),
            _sn("E4", 2.0, 3, 5, 0, "Mi"),
            # Segunda repetição
            _sn("G3", 1.0, 1, 3, 0, "Sol"),
            _sn("B3", 1.0, 2, 4, 0, "Si"),
            _sn("E4", 1.5, 3, 5, 0, "Mi"),
            _sn("B3", 0.5, 2, 4, 0, "Si"),
            _sn("G3", 1.0, 1, 3, 0, "Sol"),
            _sn("E2", 2.0, 1, 0, 0, "Mi"),
            # Frase melódica
            _sn("B4", 1.0, 4, 5, 7, "Si"),
            _sn("E4", 1.0, 1, 5, 0, "Mi"),
            _sn("G4", 1.0, 2, 5, 3, "Sol"),
            _sn("F#4", 1.0, 2, 5, 2, "Fá#"),
            _sn("E4", 2.0, 1, 5, 0, "Mi!"),
        ],
    ),

    # 15. ENTER SANDMAN (Metallica) — Riff Principal
    Song(
        id="enter_sandman",
        title="Enter Sandman (Riff Principal)",
        composer="Metallica",
        difficulty="Iniciante",
        bpm=120,
        clef="treble",
        description="O riff de abertura mais marcante do álbum 'Black Album' em Mi menor com tritono em Fá e Sol solto.",
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

    # 16. SMOKE ON THE WATER (Deep Purple) — O Riff Clássico
    Song(
        id="smoke_on_the_water",
        title="Smoke on the Water (Riff Lendário)",
        composer="Ritchie Blackmore / Deep Purple",
        difficulty="Iniciante",
        bpm=112,
        clef="treble",
        description="O riff em Sol menor mais famoso do mundo. Simples, poderoso e ideal para aprender ritmo e troca de notas.",
        notes=[
            _sn("G3", 1.0, 1, 3, 0, "Sol"),
            _sn("A#3", 1.0, 2, 3, 3, "Si♭"),
            _sn("C4", 1.5, 3, 4, 1, "Dó"),
            _sn("G3", 1.0, 1, 3, 0, "Sol"),
            _sn("A#3", 1.0, 2, 3, 3, "Si♭"),
            _sn("C#4", 0.5, 3, 4, 2, "Dó#"),
            _sn("C4", 2.0, 3, 4, 1, "Dó"),
            _sn("G3", 1.0, 1, 3, 0, "Sol"),
            _sn("A#3", 1.0, 2, 3, 3, "Si♭"),
            _sn("C4", 1.5, 3, 4, 1, "Dó"),
            _sn("A#3", 1.0, 2, 3, 3, "Si♭"),
            _sn("G3", 2.5, 1, 3, 0, "Sol!"),
        ],
    ),

    # NOVO: 4 Piano-focused
    Song(
        id="piano_fur_elise",
        title="Pour Élise (Tema)",
        composer="Ludwig van Beethoven",
        difficulty="Iniciante",
        bpm=130,
        clef="treble",
        description="Clássico tema de Beethoven focado no piano.",
        notes=[_sn("E5", 1.0), _sn("D#5", 1.0), _sn("E5", 1.0), _sn("D#5", 1.0), _sn("E5", 1.0), _sn("B4", 1.0), _sn("D5", 1.0), _sn("C5", 1.0), _sn("A4", 2.0)]
    ),
    Song(
        id="piano_moonlight",
        title="Sonata ao Luar (Adagio)",
        composer="Ludwig van Beethoven",
        difficulty="Intermédio",
        bpm=60,
        clef="bass",
        description="Famoso adágio da Sonata ao Luar, focado no piano.",
        notes=[_sn("G#3", 1.0), _sn("C#4", 1.0), _sn("E4", 1.0), _sn("G#3", 1.0), _sn("C#4", 1.0), _sn("E4", 1.0)]
    ),
    Song(
        id="piano_gymnopedie",
        title="Gymnopédie No. 1",
        composer="Erik Satie",
        difficulty="Intermédio",
        bpm=75,
        clef="treble",
        description="Melodia etérea de Satie.",
        notes=[_sn("F#4", 2.0), _sn("A4", 1.0), _sn("G4", 2.0), _sn("F#4", 1.0), _sn("C#4", 2.0)]
    ),
    Song(
        id="piano_canon_c",
        title="Cânone em Dó Maior",
        composer="Johann Pachelbel",
        difficulty="Iniciante",
        bpm=90,
        clef="treble",
        description="Clássico cânone focado no piano.",
        notes=[_sn("C4", 1.0), _sn("G3", 1.0), _sn("A3", 1.0), _sn("E3", 1.0), _sn("F3", 1.0), _sn("C3", 1.0), _sn("F3", 1.0), _sn("G3", 1.0)]
    ),
    # NOVO: 4 Guitar-focused
    Song(
        id="guitar_malaguena",
        title="Malagueña (Tema Flamenco)",
        composer="Tradicional Espanhol",
        difficulty="Iniciante",
        bpm=120,
        clef="treble",
        description="Tradicional tema espanhol para viola.",
        notes=[_sn("E4", 1.0), _sn("F4", 1.0), _sn("E4", 1.0), _sn("D4", 1.0), _sn("C4", 1.0), _sn("B3", 1.0)]
    ),
    Song(
        id="guitar_house_rising_sun",
        title="The House of the Rising Sun",
        composer="Tradicional / Folk",
        difficulty="Intermédio",
        bpm=110,
        clef="treble",
        description="Clássico folk americano.",
        notes=[_sn("A3", 1.0), _sn("C4", 1.0), _sn("E4", 1.0), _sn("A4", 1.0), _sn("E4", 1.0), _sn("C4", 1.0)]
    ),
    Song(
        id="guitar_spanish_romance",
        title="Romance Anónimo (Romance de Amor)",
        composer="Tradicional Espanhol",
        difficulty="Intermédio",
        bpm=84,
        clef="treble",
        description="Peça essencial no repertório de guitarra clássica.",
        notes=[_sn("E5", 1.0), _sn("E5", 1.0), _sn("E5", 1.0), _sn("D5", 1.0), _sn("C5", 1.0), _sn("B4", 1.0)]
    ),
    Song(
        id="guitar_greensleeves_full",
        title="Greensleeves (Arranjo para Viola)",
        composer="Tradicional Inglês",
        difficulty="Iniciante",
        bpm=100,
        clef="treble",
        description="Arranjo dedilhado clássico de Greensleeves.",
        notes=[_sn("A3", 1.0), _sn("C4", 1.5), _sn("D4", 0.5), _sn("E4", 1.5), _sn("F4", 0.5), _sn("E4", 1.0)]
    ),
]



def get_song_by_id(song_id: str) -> Optional[Song]:
    """Retrieves a song by its unique ID."""
    for song in SONG_LIBRARY:
        if song.id == song_id:
            return song
    return None


from core.fingering import assign_piano_fingerings
from core.guitar import assign_guitar_coordinates

for song in SONG_LIBRARY:
    if song.notes and all(sn.piano_finger is None for sn in song.notes):
        p_fingers = assign_piano_fingerings([sn.note for sn in song.notes])
        g_coords = assign_guitar_coordinates([sn.note for sn in song.notes])
        for i, sn in enumerate(song.notes):
            if i < len(p_fingers): sn.piano_finger = p_fingers[i]
            if i < len(g_coords):
                sn.guitar_string, sn.guitar_fret = g_coords[i]
