"""Song Repertoire Module with note-by-note coordinates, durations, lyrics, and fingerings."""
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
    description: str = ""
    notes: List[SongNote] = field(default_factory=list)

    @property
    def note_count(self) -> int:
        return len(self.notes)

    @property
    def total_beats(self) -> float:
        return sum(sn.duration_beats for sn in self.notes)


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
    # 1. HINO À ALEGRIA (Beethoven)
    Song(
        id="ode_to_joy",
        title="Hino à Alegria (9ª Sinfonia)",
        composer="Ludwig van Beethoven",
        difficulty="Iniciante",
        bpm=108,
        clef="treble",
        description="O tema imortal do 4º andamento da Nona Sinfonia de Beethoven. Melodia por graus conjuntos, perfeita para aprender no piano e viola.",
        notes=[
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
        ],
    ),

    # 2. BRILHA, BRILHA ESTRELINHA (Mozart / Tradicional)
    Song(
        id="twinkle_star",
        title="Brilha, Brilha Estrelinha (Ah! vous dirai-je, maman)",
        composer="W. A. Mozart / Tradicional",
        difficulty="Iniciante",
        bpm=100,
        clef="treble",
        description="Melodia infantil clássica harmonizada por Mozart em 12 variações (K. 265). Excelente para dominar saltos de 5ª justa.",
        notes=[
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

    # 3. PAPAGAIO LOIRO (Cantiga Popular Portuguesa)
    Song(
        id="papagaio_loiro",
        title="Papagaio Loiro (Cantiga Tradicional)",
        composer="Folclore Português",
        difficulty="Iniciante",
        bpm=110,
        clef="treble",
        description="Cantiga tradicional portuguesa muito popular nas escolas e ranchos infantis. Prática de arpejo de Dó Maior e Sol.",
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
        ],
    ),

    # 4. POMBINHA BRANCA (Tradicional Portuguesa)
    Song(
        id="pombinha_branca",
        title="Pombinha Branca",
        composer="Folclore Português",
        difficulty="Iniciante",
        bpm=96,
        clef="treble",
        description="Melodia suave do cancioneiro tradicional português em compasso binário simples.",
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
        ],
    ),

    # 5. FÜR ELISE (Beethoven - Motivo Principal)
    Song(
        id="fur_elise",
        title="Für Elise (Motivo Principal)",
        composer="Ludwig van Beethoven",
        difficulty="Intermédio",
        bpm=120,
        clef="treble",
        description="A famosa Bagatela em Lá menor (WoO 59). O motivo cromático alternado entre Mi e Ré# é um dos temas mais reconhecidos da história.",
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
            _sn("C4", 1.0, 1, 4, 1, "Dó"),
            _sn("E4", 1.0, 2, 5, 0, "Mi"),
            _sn("A4", 1.0, 3, 5, 5, "Lá"),
            _sn("B4", 2.0, 4, 5, 7, "Si"),
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

    # 8. CANON EM DÓ / RÉ (Pachelbel)
    Song(
        id="canon_in_d",
        title="Canon em Dó / Ré (Tema Principal)",
        composer="Johann Pachelbel",
        difficulty="Iniciante",
        bpm=76,
        clef="treble",
        description="A progressão harmónica e melodia barroca mais famosa de sempre. Perfeita para treino de legato e dedilhação linear.",
        notes=[
            _sn("E4", 1.0, 3, 5, 0, "Mi"),
            _sn("D4", 1.0, 2, 4, 3, "Ré"),
            _sn("C4", 1.0, 1, 4, 1, "Dó"),
            _sn("B3", 1.0, 1, 4, 0, "Si"),
            _sn("A3", 1.0, 1, 3, 2, "Lá"),
            _sn("G3", 1.0, 1, 3, 0, "Sol"),
            _sn("A3", 1.0, 1, 3, 2, "Lá"),
            _sn("B3", 1.0, 2, 4, 0, "Si"),
            _sn("C4", 2.0, 3, 4, 1, "Dó"),
        ],
    ),

    # 9. EINE KLEINE NACHTMUSIK (Mozart)
    Song(
        id="nachtmusik",
        title="Eine kleine Nachtmusik (Serenata K. 525)",
        composer="Wolfgang Amadeus Mozart",
        difficulty="Intermédio",
        bpm=124,
        clef="treble",
        description="O brilhante motivo de abertura em Sol Maior da serenata mais tocada de Mozart.",
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
        ],
    ),

    # 10. GREENSLEEVES (Tradicional Inglesa)
    Song(
        id="greensleeves",
        title="Greensleeves (Melodia Renascentista)",
        composer="Tradicional Século XVI",
        difficulty="Intermédio",
        bpm=92,
        clef="treble",
        description="Clássico do período Tudor em modo Dórico e Menor Melódico, com expressão melancólica inconfundível.",
        notes=[
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
        ],
    ),

    # 11. O CRAVO E A ROSA (Tradicional Portuguesa)
    Song(
        id="cravo_e_rosa",
        title="O Cravo e a Rosa",
        composer="Cancioneiro Popular",
        difficulty="Iniciante",
        bpm=104,
        clef="treble",
        description="Famosa cantiga de roda da tradição lusófona, excelente para primeiras lições de leitura e ritmo.",
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
        ],
    ),

    # 12. GRÂNDOLA, VILA MORENA (Zeca Afonso)
    Song(
        id="grandola",
        title="Grândola, Vila Morena",
        composer="José Afonso (Zeca Afonso)",
        difficulty="Iniciante",
        bpm=84,
        clef="treble",
        description="O hino histórico da Revolução dos Cravos de 1974. Frase melódica modal e profunda com cadência solene.",
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
            _sn("C4", 2.0, 1, 4, 1, "ter-ni-da-de."),
        ],
    ),
]


def get_song_by_id(song_id: str) -> Optional[Song]:
    """Retrieves a song by its unique ID."""
    for song in SONG_LIBRARY:
        if song.id == song_id:
            return song
    return None
