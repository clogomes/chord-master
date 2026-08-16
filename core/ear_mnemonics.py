from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class EarMnemonic:
    interval_code: str
    name: str
    name_en: str
    semitones: int
    songs_ascending: str
    songs_descending: str
    description: str
    description_en: str

    @property
    def songs(self) -> str:
        """Compatibility property returning ascending song mnemonics."""
        return self.songs_ascending


EAR_MNEMONICS: Dict[str, EarMnemonic] = {
    "P1": EarMnemonic(
        interval_code="P1",
        name="Uníssono Perfeito",
        name_en="Perfect Unison",
        semitones=0,
        songs_ascending="Mesma nota",
        songs_descending="Mesma nota",
        description="A mesma frequência sem variação.",
        description_en="The exact same pitch without variation."
    ),
    "m2": EarMnemonic(
        interval_code="m2",
        name="Segunda Menor",
        name_en="Minor 2nd",
        semitones=1,
        songs_ascending="Tubarão (Jaws), Para Elisa",
        songs_descending="Für Elise (E→D♯), Joy to the World",
        description="Dissonante, tenso, muito próximo e misterioso.",
        description_en="Dissonant, tense, extremely close and mysterious."
    ),
    "M2": EarMnemonic(
        interval_code="M2",
        name="Segunda Maior",
        name_en="Major 2nd",
        semitones=2,
        songs_ascending="Parabéns a Você, Frère Jacques",
        songs_descending="Yesterday, Mary Had a Little Lamb",
        description="Um passo inteiro diatónico, comum e com leve tensão inicial.",
        description_en="A whole diatonic step, standard and melodic."
    ),
    "m3": EarMnemonic(
        interval_code="m3",
        name="Terça Menor",
        name_en="Minor 3rd",
        semitones=3,
        songs_ascending="Greensleeves, Smoke on the Water",
        songs_descending="Hey Jude, Frosty the Snowman",
        description="Melancólico, sombrio e misterioso.",
        description_en="Melancholic, dark, and foundational for minor chords."
    ),
    "M3": EarMnemonic(
        interval_code="M3",
        name="Terça Maior",
        name_en="Major 3rd",
        semitones=4,
        songs_ascending="Oh When the Saints, Primavera de Vivaldi",
        songs_descending="5ª Sinfonia de Beethoven (Motivo do Destino), Summertime",
        description="Brilhante, alegre, estável e radiante.",
        description_en="Bright, cheerful, stable, and foundational for major chords."
    ),
    "P4": EarMnemonic(
        interval_code="P4",
        name="Quarta Justa",
        name_en="Perfect 4th",
        semitones=5,
        songs_ascending="Marcha Nupcial (Wagner), Amazing Grace",
        songs_descending="Born Free, Oh Come All Ye Faithful",
        description="Heróico, estável, afirmativo e consonante.",
        description_en="Heroic, stable, affirming, and consonant."
    ),
    "TT": EarMnemonic(
        interval_code="TT",
        name="Trítono",
        name_en="Tritone",
        semitones=6,
        songs_ascending="Os Simpsons, Maria (West Side Story)",
        songs_descending="Blue Seven, Black Sabbath",
        description="Muito dissonante, instável e pede resolução imediata.",
        description_en="Extremely dissonant, unstable, demands immediate resolution."
    ),
    "P5": EarMnemonic(
        interval_code="P5",
        name="Quinta Justa",
        name_en="Perfect 5th",
        semitones=7,
        songs_ascending="Star Wars (Tema Principal), Twinkle Twinkle Little Star",
        songs_descending="The Flintstones, Game of Thrones",
        description="Aberto, puro, muito estável e brilhante.",
        description_en="Open, pure, powerfully stable, and foundational for power chords."
    ),
    "m6": EarMnemonic(
        interval_code="m6",
        name="Sexta Menor",
        name_en="Minor 6th",
        semitones=8,
        songs_ascending="Love Story (Where Do I Begin), In My Life (Beatles)",
        songs_descending="Love Story (tema de amor), Manhã de Carnaval",
        description="Triste, expressivo, dramático e romântico.",
        description_en="Sad, expressive, highly dramatic, and romantic."
    ),
    "M6": EarMnemonic(
        interval_code="M6",
        name="Sexta Maior",
        name_en="Major 6th",
        semitones=9,
        songs_ascending="My Bonnie Lies Over the Ocean",
        songs_descending="Nobody Knows the Trouble I've Seen, Over There",
        description="Alegre, caloroso, aberto e pastoral.",
        description_en="Joyful, warm, open, and pastoral."
    ),
    "m7": EarMnemonic(
        interval_code="m7",
        name="Sétima Menor",
        name_en="Minor 7th",
        semitones=10,
        songs_ascending="Somewhere (West Side Story), The Winner Takes It All",
        songs_descending="An American in Paris, Watermelon Man",
        description="Tensão suave, característico de blues, jazz e funk.",
        description_en="Mellow tension, soul, characteristic of blues and jazz."
    ),
    "M7": EarMnemonic(
        interval_code="M7",
        name="Sétima Maior",
        name_en="Major 7th",
        semitones=11,
        songs_ascending="Take On Me (salto do refrão)",
        songs_descending="I Love You (Cole Porter)",
        description="Muito dissonante mas etéreo, pede para subir para a oitava.",
        description_en="Dissonant yet ethereal, longs to resolve up to the octave."
    ),
    "P8": EarMnemonic(
        interval_code="P8",
        name="Oitava Justa",
        name_en="Perfect Octave",
        semitones=12,
        songs_ascending="Over the Rainbow (Somewhere over...)",
        songs_descending="Willow Weep for Me",
        description="Mesma nota uma oitava acima, muito aberta e consonante.",
        description_en="Same pitch class one octave apart, perfectly consonant."
    ),
}


def get_mnemonic_by_code(code: str) -> Optional[EarMnemonic]:
    """Retrieve mnemonic data by interval short code (e.g. 'm3')."""
    return EAR_MNEMONICS.get(code)


def get_mnemonic_by_semitones(semitones: int) -> Optional[EarMnemonic]:
    """Retrieve mnemonic data by semitone count (0..12)."""
    for m in EAR_MNEMONICS.values():
        if m.semitones == semitones:
            return m
    return None
