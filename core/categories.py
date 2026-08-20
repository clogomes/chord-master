"""Central registry for practice categories in ChordMaster."""

CATEGORY_NAMES_PT = {
    "treino_auditivo": "Treino Auditivo",
    "leitura_pauta": "Leitura de Pauta",
    "teoria": "Teoria Musical",
    "repertorio": "Repertório Clássico",
    "pratica_instrumento": "Aulas Acústicas",
    "escalas_modos": "Escalas & Modos",
    "tecnica": "Exercícios Técnicos",
    "ritmo": "Prática Rítmica"
}

CATEGORY_NAMES_EN = {
    "treino_auditivo": "Ear Training",
    "leitura_pauta": "Sight Reading",
    "teoria": "Music Theory",
    "repertorio": "Classical Repertoire",
    "pratica_instrumento": "Acoustic Lessons",
    "escalas_modos": "Scales & Modes",
    "tecnica": "Technical Exercises",
    "ritmo": "Rhythm Practice"
}

CATEGORY_ROUTES = {
    "treino_auditivo": "practice_ear",
    "leitura_pauta": "practice_staff",
    "teoria": "theory",
    "repertorio": "practice_song",
    "pratica_instrumento": "practice_instrument",
    "escalas_modos": "practice_scales",
    "tecnica": "practice_technique",
    "ritmo": "practice_rhythm"
}

CATEGORY_TIPS = {
    "treino_auditivo": "Começa por identificar intervalos simples (segundas e terças).",
    "leitura_pauta": "Usa mnemónicas (ex: Sol-Si-Ré-Fá-Lá) para ler mais depressa.",
    "teoria": "Revê as lições teóricas para consolidar a fundação.",
    "repertorio": "Pratica devagar (com o metrónomo) antes de aumentar a velocidade.",
    "pratica_instrumento": "Mantém o teu instrumento afinado e a postura correta.",
    "escalas_modos": "As escalas são a base de tudo. Toca com ritmo firme.",
    "tecnica": "Aquece sempre antes de tocar e mantém as mãos relaxadas.",
    "ritmo": "Bate a barra de espaço exatamente a cada tempo; o desvio em ms diz-te se estás a atrasar."
}

CATEGORY_TIPS_EN = {
    "treino_auditivo": "Start by identifying simple intervals (seconds and thirds).",
    "leitura_pauta": "Use mnemonics (e.g., Every Good Boy Does Fine) to read faster.",
    "teoria": "Review theoretical lessons to consolidate your foundation.",
    "repertorio": "Practice slowly (with the metronome) before increasing speed.",
    "pratica_instrumento": "Keep your instrument in tune and maintain good posture.",
    "escalas_modos": "Scales are the foundation of everything. Play with a steady rhythm.",
    "tecnica": "Always warm up before playing and keep your hands relaxed.",
    "ritmo": "Tap the spacebar exactly on each beat; the ms offset tells you if you're running late."
}

CATEGORY_COLORS = {
    "treino_auditivo": "#4F46E5",
    "leitura_pauta": "#10B981",
    "teoria": "#8B5CF6",
    "repertorio": "#F59E0B",
    "pratica_instrumento": "#EF4444",
    "escalas_modos": "#0ea5e9",
    "tecnica": "#F59E0B",
    "ritmo": "#EC4899"
}
