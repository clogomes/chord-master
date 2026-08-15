from dataclasses import dataclass
from typing import Dict, Optional

@dataclass
class EarMnemonic:
    interval_code: str
    name: str
    songs: str
    description: str

EAR_MNEMONICS: Dict[str, EarMnemonic] = {
    "P1": EarMnemonic("P1", "Uníssono", "Mesma nota", "A mesma frequência sem variação."),
    "m2": EarMnemonic("m2", "2ª Menor", "Tubarão (Jaws), Para Elisa", "Dissonante, tenso, muito próximo e misterioso."),
    "M2": EarMnemonic("M2", "2ª Maior", "Parabéns a Você, Frère Jacques", "Um passo inteiro, comum e com leve tensão inicial."),
    "m3": EarMnemonic("m3", "3ª Menor", "Greensleeves, Smoke on the Water", "Melancólico, sombrio e misterioso."),
    "M3": EarMnemonic("M3", "3ª Maior", "Oh When the Saints, Primavera de Vivaldi", "Brilhante, alegre, estável e radiante."),
    "P4": EarMnemonic("P4", "4ª Perfeita", "Hino Nacional, Ó Ramos Ó Ramos", "Heróico, estável e forte."),
    "TT": EarMnemonic("TT", "Trítono", "Os Simpsons, Maria (West Side Story)", "Muito dissonante, diabólico, pede resolução."),
    "P5": EarMnemonic("P5", "5ª Perfeita", "Star Wars, Twinkle Twinkle Little Star", "Aberto, oco, muito estável e brilhante."),
    "m6": EarMnemonic("m6", "6ª Menor", "Love Story", "Triste e expressivo."),
    "M6": EarMnemonic("M6", "6ª Maior", "My Bonnie Lies Over the Ocean", "Alegre, salteado, ligeiramente instável."),
    "m7": EarMnemonic("m7", "7ª Menor", "The Winner Takes It All", "Tensão suave, característico de blues e funk."),
    "M7": EarMnemonic("M7", "7ª Maior", "Take On Me", "Muito dissonante mas etéreo, pede para subir para a oitava."),
    "P8": EarMnemonic("P8", "Oitava", "Over the Rainbow", "Mesma nota, muito aberta e familiar."),
}

def get_mnemonic_by_code(code: str) -> Optional[EarMnemonic]:
    """Retrieve mnemonic data by interval short code (e.g. 'm3')."""
    return EAR_MNEMONICS.get(code)
