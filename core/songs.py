"""Public domain song repertoire for piano and guitar practice, with fingering and tab mapping."""
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from .notes import Note
from .guitar import STANDARD_TUNING, GuitarFretboardModel


@dataclass
class SongNote:
    """
    Represents an individual musical note in a melody piece,
    including timing, piano fingering, and guitar string/fret coordinates.
    """
    note: Note
    duration_beats: float       # 1.0 = semínima (quarter note), 0.5 = colcheia, 2.0 = mínima
    piano_finger: Optional[int] = None  # 1=Polegar..5=Mindinho
    piano_hand: str = "right"   # "right" ou "left"
    guitar_string: Optional[int] = None  # 0=6ª grossa (E2) .. 5=1ª fina (E4)
    guitar_fret: Optional[int] = None    # 0=corda solta .. 15
    lyric_syllable: Optional[str] = None # Sílaba de solfejo ou letra da canção


@dataclass
class Song:
    """Represents a complete musical piece for repertoire practice."""
    id: str
    title: str
    composer: str
    difficulty: str  # "Iniciante", "Intermédio"
    bpm: int
    clef: str        # "treble" ou "bass"
    notes: List[SongNote]
    description: str = ""

    @property
    def total_beats(self) -> float:
        return sum(n.duration_beats for n in self.notes)

    @property
    def note_count(self) -> int:
        return len(self.notes)


# Helper to build SongNote quickly
def _sn(
    pitch_oct: str,
    beats: float = 1.0,
    finger: Optional[int] = None,
    g_str: Optional[int] = None,
    g_fret: Optional[int] = None,
    lyric: Optional[str] = None,
) -> SongNote:
    return SongNote(
        note=Note(pitch_oct),
        duration_beats=beats,
        piano_finger=finger,
        guitar_string=g_str,
        guitar_fret=g_fret,
        lyric_syllable=lyric or Note(pitch_oct).name_pt,
    )


# -------------------------------------------------------------------------
# REPERTOIRE LIBRARY (Public Domain Classics & Traditional Pieces)
# -------------------------------------------------------------------------
SONG_LIBRARY: List[Song] = [
    # 1. HINO À ALEGRIA (Beethoven)
    Song(
        id="ode_to_joy",
        title="Hino à Alegria (9ª Sinfonia)",
        composer="Ludwig van Beethoven",
        difficulty="Iniciante",
        bpm=108,
        clef="treble",
        description="O tema mais célebre do mundo na 9ª Sinfonia. Perfeito para mão direita no piano (posição de Dó a Sol) e primeiras cordas da viola.",
        notes=[
            _sn("E4", 1.0, 3, 5, 0, "Mi"),
            _sn("E4", 1.0, 3, 5, 0, "Mi"),
            _sn("F4", 1.0, 4, 5, 1, "Fá"),
            _sn("G4", 1.0, 5, 5, 3, "Sol"),
            _sn("G4", 1.0, 5, 5, 3, "Sol"),
            _sn("F4", 1.0, 4, 5, 1, "Fá"),
            _sn("E4", 1.0, 3, 5, 0, "Mi"),
            _sn("D4", 1.0, 2, 4, 3, "Ré"),
            _sn("C4", 1.0, 1, 4, 1, "Dó"),
            _sn("C4", 1.0, 1, 4, 1, "Dó"),
            _sn("D4", 1.0, 2, 4, 3, "Ré"),
            _sn("E4", 1.0, 3, 5, 0, "Mi"),
            _sn("E4", 1.5, 3, 5, 0, "Mi"),
            _sn("D4", 0.5, 2, 4, 3, "Ré"),
            _sn("D4", 2.0, 2, 4, 3, "Ré"),
        ],
    ),

    # 2. BRILHA, BRILHA ESTRELINHA (Mozart / Tradicional)
    Song(
        id="twinkle_star",
        title="Brilha, Brilha Estrelinha",
        composer="W. A. Mozart / Tradicional",
        difficulty="Iniciante",
        bpm=100,
        clef="treble",
        description="Melodia clássica infantil baseada nas variações K. 265 de Mozart. Exercita o salto de quinta (Dó-Sol) e passos descendentes.",
        notes=[
            _sn("C4", 1.0, 1, 4, 1, "Dó"),
            _sn("C4", 1.0, 1, 4, 1, "Dó"),
            _sn("G4", 1.0, 5, 5, 3, "Sol"),
            _sn("G4", 1.0, 5, 5, 3, "Sol"),
            _sn("A4", 1.0, 5, 5, 5, "Lá"),
            _sn("A4", 1.0, 5, 5, 5, "Lá"),
            _sn("G4", 2.0, 4, 5, 3, "Sol"),
            _sn("F4", 1.0, 3, 5, 1, "Fá"),
            _sn("F4", 1.0, 3, 5, 1, "Fá"),
            _sn("E4", 1.0, 2, 5, 0, "Mi"),
            _sn("E4", 1.0, 2, 5, 0, "Mi"),
            _sn("D4", 1.0, 1, 4, 3, "Ré"),
            _sn("D4", 1.0, 1, 4, 3, "Ré"),
            _sn("C4", 2.0, 1, 4, 1, "Dó"),
        ],
    ),

    # 3. PAPAGAIO LOIRO (Tradicional Portuguesa)
    Song(
        id="papagaio_loiro",
        title="Papagaio Loiro",
        composer="Canção Tradicional Portuguesa",
        difficulty="Iniciante",
        bpm=112,
        clef="treble",
        description="Cantiga popular portuguesa muito conhecida de ritmo alegre e melodia simples nas notas fundamentais de Dó Maior.",
        notes=[
            _sn("G4", 0.5, 5, 5, 3, "Pa-"),
            _sn("G4", 0.5, 5, 5, 3, "pa-"),
            _sn("E4", 1.0, 3, 5, 0, "gaio"),
            _sn("G4", 0.5, 5, 5, 3, "loi-"),
            _sn("G4", 0.5, 5, 5, 3, "ro"),
            _sn("E4", 1.0, 3, 5, 0, "de"),
            _sn("G4", 0.5, 5, 5, 3, "bi-"),
            _sn("G4", 0.5, 5, 5, 3, "co"),
            _sn("A4", 1.0, 5, 5, 5, "dou-"),
            _sn("G4", 1.0, 4, 5, 3, "ra-"),
            _sn("F4", 0.5, 3, 5, 1, "di-"),
            _sn("E4", 0.5, 2, 5, 0, "nho,"),
            _sn("D4", 2.0, 1, 4, 3, "ó"),
        ],
    ),

    # 4. POMBINHA BRANCA (Tradicional Portuguesa)
    Song(
        id="pombinha_branca",
        title="Pombinha Branca",
        composer="Canção Tradicional Portuguesa",
        difficulty="Iniciante",
        bpm=104,
        clef="treble",
        description="Famosa cantiga de roda portuguesa ideal para desenvolver a leitura das notas na pauta e coordenação dedo a dedo.",
        notes=[
            _sn("C4", 1.0, 1, 4, 1, "Pom-"),
            _sn("E4", 1.0, 3, 5, 0, "bi-"),
            _sn("G4", 1.0, 5, 5, 3, "nha"),
            _sn("G4", 1.0, 5, 5, 3, "bran-"),
            _sn("A4", 1.0, 5, 5, 5, "ca,"),
            _sn("A4", 1.0, 5, 5, 5, "que"),
            _sn("G4", 2.0, 4, 5, 3, "vais"),
            _sn("F4", 1.0, 3, 5, 1, "fa-"),
            _sn("F4", 1.0, 3, 5, 1, "zer?"),
            _sn("E4", 1.0, 2, 5, 0, "Vou"),
            _sn("E4", 1.0, 2, 5, 0, "la-"),
            _sn("D4", 2.0, 1, 4, 3, "var"),
            _sn("C4", 2.0, 1, 4, 1, "roupa"),
        ],
    ),

    # 5. FÜR ELISE (Beethoven - Motivo Principal)
    Song(
        id="fur_elise",
        title="Pour Élise (Motivo Principal)",
        composer="Ludwig van Beethoven",
        difficulty="Intermédio",
        bpm=120,
        clef="treble",
        description="O motivo melódico de piano mais famoso da história. Explora o semitom cromático (Mi-Ré#) e o arpejo de Lá menor.",
        notes=[
            _sn("E5", 0.5, 5, 5, 12, "Mi"),
            _sn("D#5", 0.5, 4, 5, 11, "Ré#"),
            _sn("E5", 0.5, 5, 5, 12, "Mi"),
            _sn("D#5", 0.5, 4, 5, 11, "Ré#"),
            _sn("E5", 0.5, 5, 5, 12, "Mi"),
            _sn("B4", 0.5, 2, 5, 7, "Si"),
            _sn("D5", 0.5, 4, 5, 10, "Ré"),
            _sn("C5", 0.5, 3, 5, 8, "Dó"),
            _sn("A4", 1.5, 1, 5, 5, "Lá"),
            _sn("C4", 0.5, 1, 4, 1, "Dó"),
            _sn("E4", 0.5, 2, 5, 0, "Mi"),
            _sn("A4", 0.5, 3, 5, 5, "Lá"),
            _sn("B4", 1.5, 4, 5, 7, "Si"),
        ],
    ),

    # 6. MINUETO EM SOL (Bach / Petzold)
    Song(
        id="minuet_in_g",
        title="Minueto em Sol Maior (BWV Anh. 114)",
        composer="Christian Petzold / J. S. Bach",
        difficulty="Intermédio",
        bpm=116,
        clef="treble",
        description="Do célebre Pequeno Livro de Anna Magdalena Bach. Frase de abertura elegante em compasso ternário.",
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
        ],
    ),

    # 7. MARCHA NUPCIAL (Wagner)
    Song(
        id="bridal_chorus",
        title="Marcha Nupcial (Trevo Coral)",
        composer="Richard Wagner (Lohengrin)",
        difficulty="Iniciante",
        bpm=88,
        clef="treble",
        description="A clássica marcha nupcial tocada em cerimónias no mundo inteiro. Melodia solene com ritmo pontuado.",
        notes=[
            _sn("C4", 1.0, 1, 4, 1, "Dó"),
            _sn("F4", 1.5, 3, 5, 1, "Fá"),
            _sn("F4", 0.5, 3, 5, 1, "Fá"),
            _sn("F4", 1.0, 3, 5, 1, "Fá"),
            _sn("C4", 0.5, 1, 4, 1, "Dó"),
            _sn("G4", 1.5, 5, 5, 3, "Sol"),
            _sn("E4", 0.5, 2, 5, 0, "Mi"),
            _sn("F4", 2.0, 3, 5, 1, "Fá"),
        ],
    ),
]


def get_song_by_id(song_id: str) -> Optional[Song]:
    """Retrieves a song by its unique ID."""
    for song in SONG_LIBRARY:
        if song.id == song_id:
            return song
    return None
