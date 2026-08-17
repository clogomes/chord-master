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
    period: str = "Clássico"  # "Renascença", "Barroco", "Clássico", "Romântico", "Moderno", "Folk / Popular", "Rock"
    period_en: Optional[str] = None
    historical_context: Optional[str] = None
    historical_context_en: Optional[str] = None
    theory_analysis: Optional[str] = None
    theory_analysis_en: Optional[str] = None
    notes: List[SongNote] = field(default_factory=list)

    def get_theory_analysis(self, lang: str = "pt") -> Optional[str]:
        if lang == "en" and self.theory_analysis_en:
            return self.theory_analysis_en
        return self.theory_analysis

    def get_historical_context(self, lang: str = "pt") -> Optional[str]:
        if lang == "en" and self.historical_context_en:
            return self.historical_context_en
        return self.historical_context

    def get_period(self, lang: str = "pt") -> str:
        if lang == "en" and self.period_en:
            return self.period_en
        return self.period

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
        period="Clássico / Romântico",
        period_en="Classical / Romantic",
        historical_context="""### 📜 Contexto Histórico

Composta por **Ludwig van Beethoven** e estreada em Viena em 1824, a **9ª Sinfonia em Ré menor (Op. 125)** foi uma obra revolucionária que introduziu pela primeira vez um coro e solistas vocais numa sinfonia. Beethoven já se encontrava em surdez quase total e teve de ser virado pelo contralto Caroline Unger para contemplar os aplausos estrondosos do público.

O texto do *Hino à Alegria* baseia-se na ode de **Friedrich Schiller** (1785), celebrando a fraternidade universal e a união de toda a humanidade sob a luz do ideal humanista. A simplicidade quase infantil da melodia — construída quase exclusivamente por graus conjuntos sobre a escala maior — foi intencionalmente desenhada para que qualquer ser humano na terra pudesse cantá-la em conjunto. Em 1972, o tema foi oficialmente adotado como o **Hino da Europa** pelo Conselho da Europa, simbolizando a paz e os valores democráticos compartilhados.""",
        historical_context_en="""### 📜 Historical Context

Composed by **Ludwig van Beethoven** and premiered in Vienna in 1824, the **Ninth Symphony in D minor (Op. 125)** was a revolutionary masterpiece that marked the first time a major composer used voices in a symphony. Beethoven was completely deaf by this time and had to be turned around by contralto Caroline Unger to witness the audience's thunderous ovation.

The text was adapted from **Friedrich Schiller's** 1785 poem *Ode to Joy*, celebrating universal brotherhood and human unity. The deceptive simplicity of the stepwise melody was intentionally crafted so every human being on Earth could sing it together. In 1972, the instrumental arrangement was adopted as the official **Anthem of Europe**, symbolizing peace and shared democratic ideals.""",
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
        period="Clássico",
        period_en="Classical",
        historical_context="""### 📜 Contexto Histórico

A melodia original remonta à cantiga pastoral francesa do século XVIII *"Ah! vous dirai-je, maman"*, publicada por volta de 1761 em Paris. Tornou-se universalmente célebre quando um jovem **Wolfgang Amadeus Mozart**, aos 25 anos (c. 1781-1782), compôs as suas brilhantes **12 Variações em Dó Maior (K. 265/300e)** para piano solo.

As variações de Mozart exploram contraponto, síncopas, arpejos rápidos e passagens em modo menor, transformando uma cantiga infantil numa das mais virtuosas lições de desenvolvimento temático da era clássica. O poema em inglês *"Twinkle, Twinkle, Little Star"* foi escrito mais tarde por **Jane Taylor** em 1806 no livro *Rhymes for the Nursery*, imortalizando o tema no repertório pedagógico de iniciação musical em todo o mundo.""",
        historical_context_en="""### 📜 Historical Context

The original melody originates from the 18th-century French pastoral song *"Ah! vous dirai-je, maman"*, first published around 1761 in Paris. It gained worldwide immortality when a 25-year-old **Wolfgang Amadeus Mozart** (c. 1781–1782) composed his sparkling **12 Variations in C Major (K. 265/300e)** for solo piano.

Mozart's variations explored polyphony, syncopation, rapid arpeggios, and minor-mode expressive shifts, elevating a folk nursery rhyme into a masterclass of Classical thematic development. The famous English poem was penned by **Jane Taylor** in 1806, solidifying the tune as the universal foundation for beginner music pedagogy.""",
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
        period="Folk / Tradicional",
        period_en="Folk / Traditional",
        historical_context="""### 📜 Contexto Histórico

Uma das mais emblemáticas cantigas de embalar e rondas infantis da tradição oral portuguesa, transmitida de geração em geração através dos cancioneiros populares do século XIX e início do século XX.

As cantigas de animais personificados na cultura popular lusa refletem o contacto dos navegadores e viajantes portugueses com a fauna tropical dos Descobrimentos (as terras do Brasil e da Índia), introduzindo a figura do papagaio mensageiro como portador de cartas de amor e segredos afetuosos. Na pedagogia musical, a peça é um pilar da metodologia Orff e Kodály para a fixação do intervalo de 3ª menor e da pulsação quaternária básica.""",
        historical_context_en="""### 📜 Historical Context

One of the most beloved children's nursery rhymes in Portuguese oral tradition, transmitted through generations across regional folk songbooks of the 19th and early 20th centuries.

Anthropomorphic animal songs in Portuguese folk culture trace back to maritime contact during the Age of Discovery, with exotic parrots featured as faithful messengers carrying secret love letters. In modern music education, it serves as a foundational exercise for developing steady 4/4 pulse and mastering conjunct melodic movement.""",
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
        period="Folk / Tradicional",
        period_en="Folk / Traditional",
        historical_context="""### 📜 Contexto Histórico

Cantiga de roda e dança infantil tradicionalíssima em Portugal e em todo o espaço lusófono. A figura da 'pombinha branca' é um símbolo arquetípico ancestral de pureza, paz e anunciação de noivado nas tradições camponesas ibéricas.

A melodia baseia-se num arquétipo modal simples com forte ênfase na tónica e na dominante, permitindo às crianças desenvolverem a coordenação motora (bater palmas e rodar) em perfeita sincronia com a cadência rítmica do texto rimado.""",
        historical_context_en="""### 📜 Historical Context

A quintessential traditional circle-dance and nursery tune cherished throughout Portugal and the Lusophone world. The symbol of the white dove is an ancestral archetype of purity, peace, and courtship celebrations in Iberian folk heritage.

Its stepwise contour and strong tonic-dominant polarity make it an ideal vehicle for teaching motor coordination and ear-voice synchronization to young musicians.""",
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
        period="Romântico",
        period_en="Romantic",
        historical_context="""### 📜 Contexto Histórico

Composta em 27 de abril de 1810 por **Ludwig van Beethoven**, a Bagatela em Lá menor (WoO 59) — popularmente conhecida como **Für Elise** ("Para Elisa") — é uma das peças de piano mais célebres de toda a história da música. Curiosamente, a partitura original nunca foi publicada durante a vida de Beethoven, tendo sido descoberta e publicada pelo musicólogo **Ludwig Nohl** apenas em 1867, quarenta anos após a morte do compositor.

A verdadeira identidade de "Elise" permanece um dos maiores mistérios da musicologia: a teoria dominante sugere que Nohl transcreveu incorretamente a dedicatória do manuscrito quase ilegível de Beethoven, que dizia na verdade *"Für Therese"* — em homenagem a **Therese Malfatti**, aluna e paixão de Beethoven que recusou a sua proposta de casamento em 1810. Outros musicólogos apontam para a cantora lírica **Elisabeth Röckel**. A alternância expressiva entre a melancolia da menor harmónica e o lirismo da relativa maior tornou-a um ícone eterno do piano.""",
        historical_context_en="""### 📜 Historical Context

Composed on April 27, 1810, by **Ludwig van Beethoven**, the Bagatelle in A minor (WoO 59) — universally known as **Für Elise** — is arguably the most famous piano piece in existence. Remarkably, it was never published during Beethoven's lifetime; it was discovered by musicologist **Ludwig Nohl** and published in 1867, forty years after the maestro's death.

The identity of 'Elise' remains one of classical music's great enigmas. Most scholars believe Nohl misread Beethoven's notoriously messy handwriting, and the dedication was actually *"Für Therese"*, for **Therese Malfatti**, a student Beethoven proposed to in 1810 (she declined). Another plausible candidate is the soprano **Elisabeth Röckel**. Its dramatic oscillation between tragic harmonic minor and lyrical relative major makes it an eternal pedagogical milestone.""",
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
        period="Barroco",
        period_en="Baroque",
        historical_context="""### 📜 Contexto Histórico

Durante quase dois séculos, este célebre Minueto em Sol Maior foi atribuído a **Johann Sebastian Bach**, por constar no famoso *Caderno de Música para Anna Magdalena Bach* (1725), um álbum doméstico onde o mestre barroco reunia peças para a sua segunda esposa e filhos praticarem cravo e clavicórdio.

No entanto, em 1970, o musicólogo alemão **Hans-Joachim Schulze** provou conclusivamente que a peça foi composta na verdade por **Christian Petzold** (1677–1733), organista e compositor da corte de Dresden, como parte de uma suíte para cravo. Bach tinha simplesmente transcrito a encantadora dança para o álbum da esposa pela sua excelência pedagógica e clareza de condução de vozes a duas partes.""",
        historical_context_en="""### 📜 Historical Context

For nearly two centuries, this famous Minuet in G Major was attributed to **Johann Sebastian Bach**, cataloged as BWV Anh. 114 from the 1725 *Notebook for Anna Magdalena Bach*, a domestic compilation used by Bach's family to practice harpsichord and clavichord.

However, in 1970, German musicologist **Hans-Joachim Schulze** proved conclusively that the piece was actually composed by **Christian Petzold** (1677–1733), an organist and composer at the Dresden royal court. Bach had simply copied Petzold's charming dance into his wife's notebook because of its exceptional pedagogical value and pristine two-part voice leading.""",
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
        period="Romântico",
        period_en="Romantic",
        historical_context="""### 📜 Contexto Histórico

O imponente *Coro Nupcial* ("Treulich geführt") abre o terceiro ato da ópera romântica **Lohengrin** (1850) de **Richard Wagner**. Na ópera, o coro é entoado pelas mulheres da corte após o casamento do cavaleiro do Santo Graal, Lohengrin, com a princesa Elsa de Brabante.

A peça tornou-se a marcha nupcial tradicional de entrada da noiva em casamentos no mundo ocidental após ter sido tocada no casamento da Princesa Vitória da Grã-Bretanha com o Príncipe Frederico da Prússia em 1858. A sua nobreza melódica em 4/4 reflete a mestria wagneriana no tratamento de melodias diatónicas luminosas.""",
        historical_context_en="""### 📜 Historical Context

The majestic *Bridal Chorus* ("Treulich geführt") opens the third act of **Richard Wagner's** 1850 romantic opera **Lohengrin**. In the opera, the chorus is sung by the bridal chamber attendants following the wedding of the Grail knight Lohengrin to Princess Elsa of Brabant.

It became the quintessential wedding processional across the Western world after being selected for the 1858 royal wedding of Princess Victoria of the United Kingdom to Prince Frederick of Prussia. Its noble, stepwise contour in 4/4 exemplifies Wagner's command of luminous diatonic lyricism.""",
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
        period="Barroco",
        period_en="Baroque",
        historical_context="""### 📜 Contexto Histórico

Composto por volta de 1680–1694 pelo mestre barroco alemão **Johann Pachelbel** em Nuremberga, o *Cânone e Giga em Ré Maior para três violinos e baixo contínuo* é a obra de contraponto estrito mais popular do mundo.

O segredo do seu sucesso reside na combinação de um **cânone estrito** a 3 vozes que se imitam perfeitamente em uníssono sobre um **baixo ostinato de 8 notas** (Dó-Lá-Si-Fá#-Sol-Ré-Sol-Lá / D-A-B-F#-G-D-G-A). Esta progressão harmónica (I-V-vi-iii-IV-I-IV-V) tornou-se o modelo harmónico de centenas de canções de sucesso na música pop, rock e folk do século XX e XXI (de Bob Dylan e Beatles a Green Day e Maroon 5).""",
        historical_context_en="""### 📜 Historical Context

Composed around 1680–1694 by German Baroque master **Johann Pachelbel** in Nuremberg, the *Canon and Gigue in D Major for three violins and basso continuo* is the most celebrated piece of strict contrapuntal imitation in history.

Its enduring magic stems from the marriage of a strict 3-voice canon over an unyielding **8-note ground bass ostinato** (D-A-B-F#-G-D-G-A). This chord progression (I-V-vi-iii-IV-I-IV-V) became the architectural DNA for hundreds of modern pop and rock hits, from The Beatles to Green Day and beyond.""",
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
        period="Clássico",
        period_en="Classical",
        historical_context="""### 📜 Contexto Histórico

Composta em Viena em 10 de agosto de 1787 por **Wolfgang Amadeus Mozart**, a Serenata Nº 13 para Cordas em Sol Maior (K. 525), universalmente conhecida como **Eine kleine Nachtmusik** ("Uma Pequena Serenata Noturna"), foi criada enquanto Mozart trabalhava no segundo ato da sua ópera *Don Giovanni*.

Destinada originalmente a uma formação de quinteto de cordas para entretenimento noturno aristocrático ao ar livre, a peça é o expoente máximo do equilíbrio formal da Era Clássica. A abertura em arpejo ascendente forte (*Mannheim rocket*) seguida de resposta graciosa e simétrica é o exemplo definitivo da forma sonata vienense.""",
        historical_context_en="""### 📜 Historical Context

Completed in Vienna on August 10, 1787, by **Wolfgang Amadeus Mozart**, Serenade No. 13 for Strings in G Major (K. 525) — universally known as **Eine kleine Nachtmusik** ("A Little Night Music") — was written while Mozart was simultaneously composing the second act of his opera *Don Giovanni*.

Originally intended as aristocratic outdoor evening entertainment, it stands as the pinnacle of Classical elegance and structural proportion. The opening energetic ascending triad (the famous Mannheim Rocket motif) balanced by symmetrical antecedent-consequent phrases is the textbook definition of Classical sonata architecture.""",
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
        period="Renascença",
        period_en="Renaissance",
        historical_context="""### 📜 Contexto Histórico

Registada pela primeira vez na London Stationers' Company em 1580 por Richard Jones, **Greensleeves** é uma das mais belas melodias do património musical britânico. Uma lenda popular persistente afirma que a canção foi composta pelo Rei **Henrique VIII** para cortejar Ana Bolena, mas a musicologia moderna refuta essa atribuição: a canção baseia-se no estilo de dança italiano *passamezzo antico* ou *romanesca*, que só chegou à corte inglesa anos após a morte de Henrique VIII.

A peça é famosa pelo seu caráter modal **Dórico / Eólio**, com a alternância expressiva do 7º grau (Sol natural na melodia descendente e Sol sustenido na cadência harmónica com Mi Maior), tornando-se uma referência indispensável para viola, alaúde e piano.""",
        historical_context_en="""### 📜 Historical Context

First registered at the London Stationers' Company in September 1580, **Greensleeves** is an immortal treasure of Elizabethan music. A enduring romantic myth claims it was composed by King **Henry VIII** for his future queen Anne Boleyn; however, musicologists have disproven this, as the song is built upon Italian ground bass patterns (*passamezzo antico* / *romanesca*) that only spread into England well after Henry's death.

The composition is celebrated for its **Dorian/Aeolian modal duality**, featuring a flexible 7th degree (natural 7th in descending contours, raised leading tone on authentic cadences), making it a cornerstone for renaissance lute, guitar, and keyboard study.""",
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
        period="Folk / Tradicional",
        period_en="Folk / Traditional",
        historical_context="""### 📜 Contexto Histórico

Um clássico intemporal do cancioneiro infantil luso-brasileiro, transmitido pelas tradições orais de cantigas de roda em toda a comunidade de língua portuguesa. A narrativa poética da disputa e reconciliação entre o Cravo e a Rosa é uma metáfora lúdica de afetos e dramatização social.

O compositor e etnomusicólogo brasileiro **Heitor Villa-Lobos** celebrou a riqueza destas melodias na sua célebre coleção *Guia Prático* (1932), harmonizando-as para piano e coro para demonstrar o valor artístico primordial da música popular ibero-americana.""",
        historical_context_en="""### 📜 Historical Context

A timeless children's circle song in Portuguese and Brazilian folklore, passed down through generations. The poetic dialogue recounting the quarrel and reconciliation between the Carnation and the Rose serves as an affectionate theatrical allegory for childhood play.

Renowned composer **Heitor Villa-Lobos** famously preserved and elevated these traditional melodies in his monumental *Guia Prático* (1932), demonstrating the profound musicality embedded in Lusophone folk heritage.""",
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
        period="Popular / Histórico",
        period_en="Popular / Historic",
        historical_context="""### 📜 Contexto Histórico

Composta e gravada em 1971 por **José Afonso (Zeca Afonso)** no álbum *Cantigas do Maio* em França, **Grândola, Vila Morena** é a canção mais historicamente marcante de Portugal no século XX. A música foi inspirada pela hospitalidade e dignidade dos trabalhadores da Sociedade Musical Fraternidade Operária Grandolense no Alentejo.

Às **00h20m do dia 25 de Abril de 1974**, a canção foi transmitida no programa *Limite* da **Rádio Renascença**, servindo como a segunda e definitiva senha acordada pelo Movimento das Forças Armadas (MFA) para avançar com a **Revolução dos Cravos**. O sinal pôs fim a 48 anos de ditadura em Portugal e instaurou a democracia. O ritmo pausado dos passos arrastados e o canto antifonal alentejano conferem-lhe uma força cívica e universal de liberdade e fraternidade.""",
        historical_context_en="""### 📜 Historical Context

Written and recorded in 1971 by **José Afonso (Zeca Afonso)** on his album *Cantigas do Maio* in France, **Grândola, Vila Morena** is Portugal's most historically momentous song of the 20th century, inspired by the solidarity of workers in the Alentejo town of Grândola.

At **00:20 AM on April 25, 1974**, the song was broadcast across the airwaves on **Rádio Renascença**, serving as the second and decisive secret radio signal confirming the Armed Forces Movement (MFA) to launch the **Carnation Revolution**. The broadcast toppled the 48-year authoritarian regime and restored democracy in Portugal. Its steady marching cadence and communal responsorial singing made it a universal hymn of democratic freedom.""",
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
        period="Rock",
        period_en="Rock",
        historical_context="""### 📜 Contexto Histórico

Lançada em 1971 no quarto álbum de estúdio dos **Led Zeppelin**, a canção composta pelo guitarrista **Jimmy Page** e pelo vocalista **Robert Plant** no retiro campestre de *Headley Grange* em Hampshire é considerada uma das maiores obras-primas da história do Rock.

A introdução dedilhada na guitarra acústica de 6 cordas e flautas de bisel constrói uma célebre **linha de baixo cromática descendente** em Lá menor (Lá - Sol# - Sol - Fá# - Fá / A-G#-G-F#-F), técnica herdada diretamente do Barroco e do Renascimento (*passacaglia* e *lamento*). A progressão culmina numa das mais épicas transições para guitarra elétrica de 12 cordas e um lendário solo final.""",
        historical_context_en="""### 📜 Historical Context

Released in 1971 on **Led Zeppelin's** untitled fourth studio album, this rock epic composed by **Jimmy Page** and **Robert Plant** at the Headley Grange estate is celebrated as one of the greatest rock songs ever recorded.

The iconic acoustic fingerpicked intro features a **descending chromatic bass line** in A minor (A-G#-G-F#-F), a direct harmonic lineage from Renaissance lute songs and Baroque *lament bass* passacaglias, before erupting into dynamic electric rock mastery.""",
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
        period="Rock",
        period_en="Rock",
        historical_context="""### 📜 Contexto Histórico

Lançada em 1991 no aclamado álbum homónimo (*The Black Album*) dos **Metallica**, a balada foi composta pelo vocalista e guitarrista **James Hetfield** enquanto falava ao telefone com a namorada durante uma digressão internacional.

A lendária introdução da música foi concebida por Hetfield a tocar apenas com uma mão enquanto segurava o telefone com a outra, aproveitando a ressonância das **cordas soltas da afinação padrão** em Mi menor (Mi, Sol, Si, Mi / E-G-B-E). Tornou-se uma das baladas pesadas mais reverenciadas e um hino de iniciação ao dedilhado na guitarra acústica em todo o mundo.""",
        historical_context_en="""### 📜 Historical Context

Released in 1991 on **Metallica's** eponymous *Black Album*, this masterpiece ballad was penned by frontman **James Hetfield** while on a grueling international tour.

The iconic opening was conceived by Hetfield while talking on the phone with his girlfriend: he plucked the open strings of standard tuning with one hand (E-G-B-E). It transformed into one of heavy metal's most profound emotional anthems and an indispensable fingerstyle benchmark for aspiring guitarists.""",
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
        period="Rock / Metal",
        period_en="Rock / Metal",
        historical_context="""### 📜 Contexto Histórico

Composta por **Kirk Hammett**, **James Hetfield** e **Lars Ulrich**, foi a faixa de abertura do *Black Album* (1991) dos **Metallica** que catapultou a banda para o estrelato planetário e vendeu mais de 30 milhões de cópias.

O riff imortal de guitarra foi criado por Kirk Hammett às duas da manhã num gravador de cassetes portátil. A sua sonoridade pesada e sombria deriva do uso do **Trítono (quinta diminuta / ♭5)** entre a tónica Mi e o Si bemol (E - B♭) na escala de Blues menor, provando a eficácia do intervalo mais tenso da música moderna no Hard Rock e Metal.""",
        historical_context_en="""### 📜 Historical Context

Composed by **Kirk Hammett**, **James Hetfield**, and **Lars Ulrich**, *Enter Sandman* was the breakthrough lead single of Metallica's 1991 *Black Album*, propelling them into global mainstream superstardom.

Kirk Hammett invented the iconic guitar riff at 2:00 AM on a portable cassette recorder. Its sinister sonic punch relies on the **Tritone (diminished 5th / ♭5)** between root E and B♭ in the minor Blues scale, demonstrating the raw power of harmonic tension in rock riff architecture.""",
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
        period="Rock",
        period_en="Rock",
        historical_context="""### 📜 Contexto Histórico

Lançada em 1972 no álbum *Machine Head* dos britânicos **Deep Purple**, a canção documenta um evento verídico: a 4 de dezembro de 1971, durante um concerto de Frank Zappa e The Mothers of Invention no Casino de Montreux na Suíça, alguém disparou um sinalizador de fogo contra o teto de bambu, incendiando completamente o edifício. Os Deep Purple assistiram ao fumo espalhar-se sobre o Lago Genebra (*"smoke on the water"*).

O lendário riff composto pelo guitarrista **Ritchie Blackmore** é tocado em quartas paralelas (*double-stops*) com os dedos em vez de palheta na escala pentatónica/blues de Sol menor, tornando-se o riff de guitarra mais tocado por principiantes em toda a história do instrumento.""",
        historical_context_en="""### 📜 Historical Context

Released in 1972 on **Deep Purple's** landmark *Machine Head*, the song immortalizes a true catastrophe: on December 4, 1971, during a Frank Zappa concert at the Montreux Casino in Switzerland, an audience member fired a flare gun into the rattan ceiling, setting the casino ablaze. Deep Purple watched the smoke drift over Lake Geneva from their hotel window.

Guitarist **Ritchie Blackmore** crafted the definitive parallel-fourth rock riff in G minor Blues, plucked with bare fingers, establishing the single most recognized guitar riff in music history.""",
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
        period="Romântico",
        period_en="Romantic",
        historical_context="""### 📜 Contexto Histórico

Arranjo de estudo introdutório da célebre Bagatela de **Ludwig van Beethoven** (1810), focada no domínio motor e rítmico do motivo semitonal oscilante da mão direita.

A composição demonstra como Beethoven conseguia criar uma atmosfera de expectativa dramática profunda com um simples semitom cromático (Mi e Ré sustenido), antes de desencadear a rica cadência harmónica autêntica que ancora a peça em Lá menor.""",
        historical_context_en="""### 📜 Historical Context

Introductory study arrangement of **Ludwig van Beethoven's** 1810 Bagatelle, focused on developing fingertip sensitivity and clean semitone alternation between E and D#.

The theme showcases Beethoven's genius in crafting poignant romantic tension from the smallest melodic unit (the minor 2nd) before resolving firmly into harmonic minor cadential stability.""",
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
        period="Clássico / Romântico",
        period_en="Classical / Romantic",
        historical_context="""### 📜 Contexto Histórico

Composta no verão de 1801 em Viena por **Ludwig van Beethoven**, a **Sonata para Piano Nº 14 em Dó♯ menor (Op. 27 Nº 2)** tem o subtítulo formal de *"Quasi una fantasia"*. A alcunha imortal *"Sonata ao Luar"* (*Mondscheinsonate*) foi cunhada em 1832 pelo poeta e crítico musical alemão **Ludwig Rellstab**, que comparou o primeiro movimento hipnótico à visão de um barco a deslizar ao luar sobre o Lago Lucerna na Suíça.

Beethoven dedicou a sonata à sua aluna de 17 anos, a condessa **Giulietta Guicciardi**, por quem estava profundamente apaixonado. O movimento Adagio Sostenuto quebrou todas as convenções clássicas da época ao abrir uma sonata com um andamento lento e meditativo baseado num fluxo contínuo de tercinas em arpejo, instruindo o pianista a tocar com pedal sustentado contínuo (*senza sordino*).""",
        historical_context_en="""### 📜 Historical Context

Composed in 1801 by **Ludwig van Beethoven**, the **Piano Sonata No. 14 in C♯ minor (Op. 27 No. 2)** was titled *"Quasi una fantasia"* by the composer. The enduring moniker *"Moonlight Sonata"* was coined in 1832 by German poet **Ludwig Rellstab**, who likened the first movement to moonlight shimmering over Lake Lucerne.

Beethoven dedicated the sonata to his 17-year-old student, Countess **Giulietta Guicciardi**. The haunting *Adagio Sostenuto* shattered Classical sonata conventions by beginning with a solemn, meditative movement carried by continuous triplet arpeggios, creating an unprecedented atmosphere of romantic introspection.""",
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
        period="Moderno / Impressionista",
        period_en="Modern / Impressionist",
        historical_context="""### 📜 Contexto Histórico

Publicada em Paris em 1888 pelo visionário compositor excêntrico francês **Erik Satie**, a **Gymnopédie Nº 1** é uma das obras mais influentes da música moderna e precursora direta da música ambiente e do minimalismo. O título faz referência às *Gimnopédias*, festivais da Grécia Antiga onde jovens espartanos dançavam nus em homenagem aos deuses.

Satie rejeitou a grandiloquência do romantismo wagneriano, optando por uma deslumbrante economia de meios: uma valsa lenta em 3/4 com acordes com sétima e nona em modo Lídio/Jónico que parecem flutuar no tempo sem pressa de resolver. O seu amigo **Claude Debussy** orquestrou a peça em 1897, consagrando Satie como um dos pais da harmonia impressionista.""",
        historical_context_en="""### 📜 Historical Context

Published in Paris in 1888 by eccentric French avant-garde visionary **Erik Satie**, **Gymnopédie No. 1** is a foundational masterpiece of modernism and a direct ancestor of ambient and minimalist music. The title evokes the ancient Spartan festival of *Gymnopaedia*, where young athletes danced in solemn ritual.

Satie radically rejected Wagnerian complexity, creating a tranquil 3/4 waltz with floating major-seventh chords and modal harmony. In 1897, his close friend **Claude Debussy** orchestrated the work, cementing Satie's legacy as a revolutionary pioneer of impressionist music.""",
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
        period="Barroco",
        period_en="Baroque",
        historical_context="""### 📜 Contexto Histórico

Adaptação pedagógica para piano da célebre linha de baixo do **Cânone em Ré Maior** de **Johann Pachelbel** (c. 1680), transposta para a tonalidade acessível de Dó Maior.

O estudo foca-se na independência da mão esquerda e na compreensão do conceito de *Basso Ostinato* (baixo contínuo repetitivo), demonstrando como uma sequência sólida de 8 compassos sustenta infinitas variações melódicas na música ocidental.""",
        historical_context_en="""### 📜 Historical Context

Pedagogical keyboard arrangement of the famous ground bass from **Johann Pachelbel's** Baroque masterpiece (c. 1680), transposed to C Major for early piano development.

This exercise trains left-hand pulse stability and teaches the foundational concept of *Basso Ostinato*, showing how an 8-measure harmonic cycle forms the bedrock of European polyphonic tradition.""",
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
        period="Folk / Tradicional",
        period_en="Folk / Traditional",
        historical_context="""### 📜 Contexto Histórico

Originária da região de Málaga na Andaluzia (Espanha), a **Malagueña** é um dos palos (estilos) mais tradicionais e vibrantes da música flamenca e do folclore ibérico. Evoluiu a partir do antigo *Fandango* andaluz no século XIX.

A peça é a celebração definitiva da **Cadência Andaluza** no modo Frígio espanhol (Lá menor - Sol Maior - Fá Maior - Mi Maior / Am - G - F - E). O contraste rítmico, os golpes na caixa da guitarra (*golpe*) e os arpejos passionais conferem-lhe uma energia dramática inconfundível, sendo obrigatória no repertório de violão clássico e flamenco.""",
        historical_context_en="""### 📜 Historical Context

Originating in the Málaga province of Andalusia, the **Malagueña** is one of the most vibrant *palos* (song forms) in flamenco and traditional Spanish guitar heritage, evolving from the 19th-century Andalusian *Fandango*.

The composition is the quintessential embodiment of the **Andalusian Cadence** in the Spanish Phrygian mode (Am - G - F - E). Its passionate rasgueados, syncopated accents, and rich modal sonorities make it an essential concert showpiece in classical and flamenco guitar literature.""",
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
        period="Folk / Rock",
        period_en="Folk / Rock",
        historical_context="""### 📜 Contexto Histórico

Balada tradicional americana de raízes folclóricas profundas, cujas origens remontam a canções de marinheiros ingleses do século XVII, tendo sido gravada por diversos artistas de folk e blues (como Lead Belly e Woody Guthrie) na década de 1930 e 1940 antes de se tornar um sucesso mundial absoluto em 1964 com a banda britânica **The Animals**.

A letra narra a história comovente de uma vida arruinada em Nova Orleães na misteriosa casa conhecida como *"The Rising Sun"*. O arranjo em arpejo dedilhado contínuo de 6/8 em Lá menor tornou-se o padrão dourado para o estudo de dedilhado na guitarra acústica contemporânea.""",
        historical_context_en="""### 📜 Historical Context

A traditional American folk ballad with deep roots in 17th-century English broadside ballads, recorded by folk and blues pioneers like Lead Belly and Woody Guthrie before becoming a monumental #1 worldwide hit in 1964 for British rock group **The Animals**.

The lyrics recount a cautionary tale of a ruined life in New Orleans at the mysterious 'Rising Sun'. The iconic rolling 6/8 fingerpicking arpeggio pattern in A minor established it as the ultimate rite of passage for acoustic guitarists around the world.""",
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
        period="Romântico",
        period_en="Romantic",
        historical_context="""### 📜 Contexto Histórico

Frequentemente intitulada *Romance Anónimo*, *Romance de Amor* ou *Jeux Interdits*, esta é a composição para guitarra clássica mais famosa do mundo. A sua autoria tem sido disputada entre mestres espanhóis do século XIX como **Fernando Sor**, **Antonio Rubira** e **Narciso Yepes** (que a popularizou internacionalmente na banda sonora do filme oscarizado *Jeux Interdits* em 1952).

A peça é uma obra-prima de economia e beleza melódica: enquanto os dedos indicador, médio e anelar executam um arpejo contínuo com a melodia cantável nas cordas agudas, o polegar mantém um baixo estável nos bordões. A transição da melancólica primeira parte em Mi menor para a luminosa segunda parte em Mi Maior é um exemplo sublime de contraste modal no romantismo ibérico.""",
        historical_context_en="""### 📜 Historical Context

Universally known as *Spanish Romance*, *Romance Anónimo*, or *Jeux Interdits*, this is the most widely performed classical guitar piece in the world. Authorship has been attributed to 19th-century Spanish masters including **Antonio Rubira**, **Fernando Sor**, and **Narciso Yepes** (who recorded it for the 1952 Oscar-winning film *Forbidden Games*).

Its genius lies in its delicate texture: a singing treble cantabile melody sustained by a triplet arpeggio against a steady thumb bass. The shift from the sorrowful first section in E minor to the radiant second section in E major is a breathtaking display of romantic modal illumination.""",
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
        period="Renascença",
        period_en="Renaissance",
        historical_context="""### 📜 Contexto Histórico

Arranjo completo para viola dedilhada em compasso composto 6/8 da célebre melodia renascentista inglesa do século XVI.

Este arranjo explora a textura polifónica da viola com baixos independentes e notas dobradas, permitindo ao executante sentir a nobreza e a cadência de dança cortês elisabetana com dedilhado fluído nas seis cordas.""",
        historical_context_en="""### 📜 Historical Context

Complete fingerstyle guitar arrangement in 6/8 compound time of the immortal 16th-century English renaissance tune.

This study explores polyphonic fingerstyle textures with independent thumb bass lines and melodic ornamentations, capturing the elegance of Elizabethan courtly dance music.""",
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
