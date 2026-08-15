"""Comprehensive, structured music theory curriculum covering beginner to advanced levels, with deep piano and guitar/viola focus."""
from dataclasses import dataclass
from typing import List


@dataclass
class TheoryChapter:
    """Represents an extensive music theory chapter with sub-topics, practical guides, and demonstrations."""
    id: str
    number: int
    title: str
    subtitle: str
    difficulty: str  # "Iniciante", "Intermédio", "Avançado", "Prático"
    category: str
    summary: str
    content_markdown: str
    piano_focus: str
    guitar_focus: str
    interactive_demo: str  # "notes", "intervals", "scales", "chords", "fretboard", "circle_of_fifths"
    
    # Optional English translations (i18n)
    title_en: str = ""
    subtitle_en: str = ""
    summary_en: str = ""
    content_markdown_en: str = ""
    piano_focus_en: str = ""
    guitar_focus_en: str = ""

    def get_title(self, lang: str = "pt") -> str:
        return self.title_en if lang == "en" and self.title_en else self.title

    def get_subtitle(self, lang: str = "pt") -> str:
        return self.subtitle_en if lang == "en" and self.subtitle_en else self.subtitle

    def get_summary(self, lang: str = "pt") -> str:
        return self.summary_en if lang == "en" and self.summary_en else self.summary

    def get_content_markdown(self, lang: str = "pt") -> str:
        return self.content_markdown_en if lang == "en" and self.content_markdown_en else self.content_markdown

    def get_piano_focus(self, lang: str = "pt") -> str:
        return self.piano_focus_en if lang == "en" and self.piano_focus_en else self.piano_focus

    def get_guitar_focus(self, lang: str = "pt") -> str:
        return self.guitar_focus_en if lang == "en" and self.guitar_focus_en else self.guitar_focus


THEORY_CHAPTERS: List[TheoryChapter] = [
    # ----------------------------------------------------
    # CAPÍTULO 1
    # ----------------------------------------------------
    TheoryChapter(
        id="chap1_fundamentals",
        number=1,
        title="Fundamentos da Música & Notação",
        subtitle="Propriedades do som, notas, cifras, pauta e acidentes",
        difficulty="Iniciante",
        category="Fundamentos",
        summary="Aprende as bases da linguagem musical: as 12 notas cromáticas, a notação de solfejo e cifrada, a pauta com as claves de Sol e Fá, e o funcionamento dos acidentes (sustenidos e bemóis).",
        content_markdown="""
### 1. As 12 Notas da Música Ocidental
A música ocidental organiza as frequências audíveis em ciclos repetitivos chamados **Oitavas**. Cada oitava é dividida em **12 semitons iguais** (sistema temperado):

• **7 Notas Naturais**: C (Dó), D (Ré), E (Mi), F (Fá), G (Sol), A (Lá), B (Si).
• **5 Notas Alteradas (Acidentes)**: C♯/D♭, D♯/E♭, F♯/G♭, G♯/A♭, A♯/B♭.

---

### 2. Acidentes Musicais e Enarmonia
• **Sustenido (♯)**: Eleva a altura da nota em **1 semitom** (meio-tom). Ex: Dó → Dó♯.
• **Bemol (♭)**: Abaixa a altura da nota em **1 semitom**. Ex: Ré → Ré♭.
• **Bequadro (♮)**: Cancela qualquer acidente anterior, restaurando a nota natural.
• **Enarmonia**: Notas que têm nomes diferentes mas produzem a **mesma frequência acústica** (ex: Dó♯ e Ré♭ são a mesma nota/tecla).

---

### 3. A Pauta Musical & Claves
A pauta (ou pentagrama) é composta por **5 linhas e 4 espaços**, contados de baixo para cima:

• **Clave de Sol (𝄞)**: Usada para instrumentos de registo agudo e médio (mão direita do piano, viola/guitarra, violino, voz soprano/tenor). Fixa a nota **Sol na 2ª linha**.
• **Clave de Fá (𝄢)**: Usada para instrumentos de registo grave (mão esquerda do piano, baixo elétrico, violoncelo). Fixa a nota **Fá na 4ª linha**.
• **Dó Central (C4 / Dó 3)**: Ponto de encontro entre as duas claves, representado na 1ª linha suplementar inferior na Clave de Sol.
""",
        piano_focus="""
🎹 **No Piano**:
• As teclas brancas correspondem às 7 notas naturais (C, D, E, F, G, A, B).
• As teclas pretas são os acidentes (agrupadas em pares de 2 e trios de 3).
• O **Dó Central (C4)** localiza-se à esquerda do grupo de 2 teclas pretas mais próximo do centro do teclado.
• **Postura & Altura do Banco**: Senta-te na metade frontal do banco com as costas direitas e os dois pés assentes no chão. Os teus cotovelos devem ficar ligeiramente acima do nível das teclas brancas.
• **Relaxamento dos Ombros**: Mantém os ombros baixos e descontraídos; a tensão nos ombros e no pescoço bloqueia a circulação e causa fadiga precoce.
""",
        guitar_focus="""
🎸 **Na Viola / Guitarra**:
• A afinação padrão das 6 cordas soltas (da 6ª mais grossa para a 1ª mais fina) é: **E2 - A2 - D3 - G3 - B3 - E4** (Mi, Lá, Ré, Sol, Si, Mi).
• Cada traste no braço avança exatamente **1 semitom**.
• A música de guitarra é escrita na **Clave de Sol**, mas soa uma oitava abaixo do que está escrito (instrumento transpositor de 8ª).
• **Ângulo do Instrumento**: Apoia a viola com o braço inclinado a cerca de 30º-45º para cima; nunca toques com o braço paralelo ao chão, pois força uma dobra prejudicial no pulso esquerdo.
• **Ataque na Ponta dos Dedos**: Pressiona as cordas rigorosamente com a ponta dos dedos (a 90º da escala) para evitar que a almofada do dedo encoste e abafe as cordas soltas vizinhas.
""",
        interactive_demo="notes",
        title_en="Music Fundamentals & Notation",
        subtitle_en="Properties of sound, notes, staff, clefs, and accidentals",
        summary_en="Learn the foundations of musical language: the 12 chromatic notes, solfège and letter notation, the staff with Treble and Bass clefs, and how accidentals work.",
        content_markdown_en="""
### 1. The 12 Western Music Notes
Western music organizes audible frequencies into repeating cycles called **Octaves**. Each octave is divided into **12 equal semitones**:

• **7 Natural Notes**: C, D, E, F, G, A, B.
• **5 Altered Notes (Accidentals)**: C♯/D♭, D♯/E♭, F♯/G♭, G♯/A♭, A♯/B♭.

---

### 2. Accidentals and Enharmonics
• **Sharp (♯)**: Raises the pitch by **1 semitone**. E.g.: C → C♯.
• **Flat (♭)**: Lowers the pitch by **1 semitone**. E.g.: D → D♭.
• **Natural (♮)**: Cancels previous accidentals, restoring the natural note.
• **Enharmonics**: Notes with different names that share the **same acoustic frequency** (e.g. C♯ and D♭).

---

### 3. Musical Staff & Clefs
The staff consists of **5 lines and 4 spaces**, counted from bottom to top:

• **Treble Clef (𝄞)**: Used for higher pitch ranges (piano right hand, guitar, violin). Places **G on the 2nd line**.
• **Bass Clef (𝄢)**: Used for lower pitch ranges (piano left hand, bass guitar, cello). Places **F on the 4th line**.
• **Middle C (C4)**: Meeting point between both clefs, placed on the 1st ledger line below the treble staff.
""",
        piano_focus_en="""
🎹 **On Piano**:
• White keys correspond to the 7 natural notes (C, D, E, F, G, A, B).
• Black keys are accidentals (grouped in pairs of 2 and trios of 3).
• **Middle C (C4)** is located to the left of the 2-black-key group closest to the center.
""",
        guitar_focus_en="""
🎸 **On Guitar / Viola**:
• Standard tuning of the 6 open strings: **E2 - A2 - D3 - G3 - B3 - E4**.
• Each fret advances by exactly **1 semitone**.
• Guitar music is written in **Treble Clef**, sounding one octave lower than written.
""",
    ),

    # ----------------------------------------------------
    # CAPÍTULO 2
    # ----------------------------------------------------
    TheoryChapter(
        id="chap2_intervals",
        number=2,
        title="Intervalos & Física Harmónica",
        subtitle="A unidade fundamental da harmonia e consonâncias",
        difficulty="Iniciante",
        category="Intervalos",
        summary="Descobre o que são intervalos, como medir a distância entre notas em semitons, a diferença entre intervalos melódicos e harmónicos, e as mnemónicas para treino auditivo.",
        content_markdown="""
### 1. O que é um Intervalo?
Um **intervalo** é a distância de altura entre duas notas musicais. É o bloco fundamental a partir do qual se constroem todas as melodias, escalas e acordes.

• **Intervalo Melódico**: As notas são tocadas sucessivamente (uma a seguir à outra). Pode ser ascendente ou descendente.
• **Intervalo Harmónico**: As notas são tocadas em simultâneo (em uníssono).

---

### 2. Tabela Completa de Intervalos (0 a 12 Semitons)

| Semitons | Nome em Português | Símbolo | Qualidade | Mnemónica Auditiva |
| :--- | :--- | :--- | :--- | :--- |
| **0** | Uníssono Justo | P1 | Consonância Perfeita | Mesma nota repetida |
| **1** | Segunda Menor | m2 | Dissonância Forte | Tema de *Tubarão (Jaws)* |
| **2** | Segunda Maior | M2 | Dissonância Suave | *Parabéns a Você* (1º salto) |
| **3** | Terça Menor | m3 | Consonância Imperfeita | *Greensleeves* / *Smoke on the Water* |
| **4** | Terça Maior | M3 | Consonância Imperfeita | *Oh When the Saints* / *Kumbaya* |
| **5** | Quarta Justa | P4 | Consonância Perfeita | *Hino da Champions League* |
| **6** | Trítono (4ª aum / 5ª dim) | TT | Dissonância Extrema | Tema de *Os Simpsons* / *Maria* |
| **7** | Quinta Justa | P5 | Consonância Perfeita | Tema de *Star Wars* / *Twinkle Twinkle* |
| **8** | Sexta Menor | m6 | Consonância Imperfeita | *Love Story* / *In My Life (Beatles)* |
| **9** | Sexta Maior | M6 | Consonância Imperfeita | *My Bonnie Lies Over the Ocean* |
| **10** | Sétima Menor | m7 | Dissonância Suave | *The Winner Takes It All (ABBA)* |
| **11** | Sétima Maior | M7 | Dissonância Tensa | *Take On Me* (salto do refrão) |
| **12** | Oitava Justa | P8 | Consonância Perfeita | *Somewhere Over the Rainbow* |

---

### 3. Inversão de Intervalos
Quando invertemos as duas notas de um intervalo (por exemplo, Dó-Sol vira Sol-Dó):
• A soma do intervalo original com a sua inversão é sempre **9**.
• O Maior torna-se Menor (e vice-versa).
• O Aumentado torna-se Diminuto (e vice-versa).
• O Justo permanece Justo (P5 invertida vira P4; P4 vira P5).
""",
        piano_focus="""
🎹 **No Piano**:
• Segunda Menor (1 semitom) = Tecla branca imediatamente adjacente à tecla preta (ou Mi-Fá e Si-Dó).
• Quinta Justa (7 semitons) = Distância padrão natural da mão em posição de repouso (dedo 1 ao dedo 5).
• Terça Maior vs Menor = 4 semitons (2 tons inteiros) vs 3 semitons (1 tom e meio).
• **Exercício de Independência dos Dedos**: Mantém o Dó premido com o polegar (dedo 1) e toca os intervalos de 2ª, 3ª, 4ª e 5ª com os dedos 2, 3, 4 e 5 sem soltar o polegar e sem contrair o pulso.
• **Flexibilidade do Pulso**: O pulso deve agir como um amortecedor suave (como a suspensão de um carro), subindo e descendo ligeiramente ao articular intervalos distantes.
""",
        guitar_focus="""
🎸 **Na Viola / Guitarra**:
• 1 Semitom = 1 Traste de distância na mesma corda.
• 1 Tom (2 semitons) = 2 Trastes de distância na mesma corda.
• Quinta Justa = 1 corda abaixo e 2 trastes à frente (ex: 3º traste na 6ª corda [Sol] → 5º traste na 5ª corda [Ré]).
• Exceção da 2ª corda (Si): A afinação entre a 3ª corda (Sol) e a 2ª (Si) é de uma Terça Maior (4 semitons), enquanto todas as outras cordas são afinadas em Quartas Justas (5 semitons).
• **Evitar o 'Fret Buzz' (Trastejar)**: Coloca o dedo imediatamente atrás do ferrinho do traste (a 1-2 mm), nunca no meio do espaço, para obter o som mais límpido com a menor pressão possível.
• **Pressão Mínima**: Experimenta tocar uma nota aliviando a força até trastejar, e depois aperta apenas o milímetro suficiente para soar limpa — evita gastar o dobro da energia necessária.
""",
        interactive_demo="intervals",
        title_en="Intervals & Harmonic Physics",
        subtitle_en="The fundamental building blocks of harmony and consonances",
        summary_en="Discover what intervals are, how to measure note distances in semitones, melodic vs harmonic intervals, and ear training mnemonics.",
        content_markdown_en="""
### 1. What is an Interval?
An **interval** is the distance in pitch between two musical notes. It is the fundamental building block from which melodies, scales, and chords are built.

• **Melodic Interval**: Notes are played sequentially (one after another).
• **Harmonic Interval**: Notes are played simultaneously.

---

### 2. Complete Intervals Table (0 to 12 Semitones)
• **0 Semitones (P1)**: Perfect Unison
• **1 Semitone (m2)**: Minor 2nd (Jaws theme)
• **2 Semitones (M2)**: Major 2nd (Happy Birthday)
• **3 Semitones (m3)**: Minor 3rd (Greensleeves)
• **4 Semitones (M3)**: Major 3rd (Oh When the Saints)
• **5 Semitones (P4)**: Perfect 4th (Amazing Grace)
• **6 Semitones (TT)**: Tritone (The Simpsons)
• **7 Semitones (P5)**: Perfect 5th (Star Wars)
• **8 Semitones (m6)**: Minor 6th (Love Story)
• **9 Semitones (M6)**: Major 6th (My Bonnie)
• **10 Semitones (m7)**: Minor 7th (The Winner Takes It All)
• **11 Semitones (M7)**: Major 7th (Take On Me)
• **12 Semitones (P8)**: Perfect Octave (Somewhere Over the Rainbow)
""",
        piano_focus_en="""
🎹 **On Piano**:
• Minor 2nd = Immediately adjacent black/white key (or E-F, B-C).
• Perfect 5th = Natural distance of hand in rest position (thumb to pinky).
""",
        guitar_focus_en="""
🎸 **On Guitar / Viola**:
• 1 Semitone = 1 Fret distance on the same string.
• Perfect 5th = 1 string down and 2 frets forward.
""",
    ),

    # ----------------------------------------------------
    # CAPÍTULO 3
    # ----------------------------------------------------
    TheoryChapter(
        id="chap3_scales_modes",
        number=3,
        title="Escalas, Modos Gregos & Círculo de Quintas",
        subtitle="Estruturas melódicas tonais, modais e o ciclo das tonalidades",
        difficulty="Intermédio",
        category="Escalas",
        summary="Aprende as fórmulas intervalares da Escala Maior, Menores (Natural, Harmónica, Melódica), Pentatónicas, a sonoridade dos 7 Modos Gregos e o Círculo de Quintas.",
        content_markdown="""
### 1. A Escala Maior Natural
A **Escala Maior** é o pilar de toda a harmonia tonal ocidental. A sua fórmula em tons (T) e semitons (ST) é:

**T – T – ST – T – T – T – ST**

Graus da escala: **1 - 2 - 3 - 4 - 5 - 6 - 7**.
Exemplo em Dó Maior: **C - D - E - F - G - A - B - C**.

---

### 2. As Três Escalas Menores
1. **Menor Natural (Modo Eólio)**: Fórmula: **T - ST - T - T - ST - T - T** (Graus: **1 - 2 - ♭3 - 4 - 5 - ♭6 - ♭7**).
2. **Menor Harmónica**: Eleva o 7º grau para criar uma sensível a 1 semitom da tónica (Graus: **1 - 2 - ♭3 - 4 - 5 - ♭6 - 7**). Gera o exótico salto de 1 tom e meio entre o 6º e 7º grau.
3. **Menor Melódica**: Eleva tanto o 6º como o 7º grau na subida para suavizar a condução melódica (Graus: **1 - 2 - ♭3 - 4 - 5 - 6 - 7**).

---

### 3. Os 7 Modos Gregos
Os modos são permutações da escala maior iniciando em cada um dos seus 7 graus:

1. **Jónio (I)**: Escala Maior padrão (**1, 2, 3, 4, 5, 6, 7**) — Alegre, estável.
2. **Dórico (ii)**: Menor com 6ª Maior (**1, 2, ♭3, 4, 5, 6, ♭7**) — Jazz, elegante, nostálgico (*So What* de Miles Davis).
3. **Frígio (iii)**: Menor com 2ª Menor (**1, ♭2, ♭3, 4, 5, ♭6, ♭7**) — Flamenco, espanhol, misterioso.
4. **Lídio (IV)**: Maior com 4ª Aumentada (**1, 2, 3, ♯4, 5, 6, 7**) — Místico, etéreo, bandas sonoras de cinema.
5. **Mixolídio (V)**: Maior com 7ª Menor (**1, 2, 3, 4, 5, 6, ♭7**) — Blues, Rock clássico, *Sweet Child O' Mine*.
6. **Eólio (vi)**: Menor Natural padrão (**1, 2, ♭3, 4, 5, ♭6, ♭7**) — Melancólico, solene.
7. **Lócrio (vii°)**: Diminuto com 2ª menor e 5ª diminuta (**1, ♭2, ♭3, 4, ♭5, ♭6, ♭7**) — Tenso, instável.

---

### 4. O Círculo de Quintas
O Círculo de Quintas organiza as 12 armações de clave:
• **Sentido Horário (+ Quintas / 7 st)**: Adiciona 1 sustenido (C=0♯, G=1♯, D=2♯, A=3♯, E=4♯, B=5♯, F♯=6♯, C♯=7♯).
• **Sentido Anti-horário (+ Quartas / 5 st)**: Adiciona 1 bemol (C=0♭, F=1♭, B♭=2♭, E♭=3♭, A♭=4♭, D♭=5♭, G♭=6♭, C♭=7♭).
""",
        piano_focus="""
🎹 **No Piano**:
• Dó Maior toca-se apenas nas teclas brancas.
• Digitação clássica da Escala Maior (Mão Direita): **1-2-3-1-2-3-4-5** (o polegar passa por baixo do dedo 3 após o Mi).
• Digitação (Mão Esquerda): **5-4-3-2-1-3-2-1** (o dedo 3 passa por cima do polegar após o Sol).
• **Rotina de Prática com Rampa de Tempo**: Começa a praticar a escala a 60 BPM (70% do tempo final). Foca-te na igualdade sonora de cada nota e na passagem macia do polegar por baixo da mão antes de acelerar progressivamente.
• **Passagem Oculta do Polegar**: Não levantes o cotovelo para fora ao passar o polegar; mantém o antebraço calmo e move o polegar horizontalmente por baixo da palma.
""",
        guitar_focus="""
🎸 **Na Viola / Guitarra**:
• As escalas são memorizadas em **padrões geométricos (Boxes / Posições)** ao longo do braço.
• A **Pentatónica Menor** (Posição 1) é o padrão mais famoso do mundo: 2 notas por corda começando na tónica da 6ª corda.
• O Sistema **CAGED** divide o braço em 5 regiões sobrepostas onde todas as escalas e modos podem ser tocados sem mudar de afinação.
• **Palhetada Alternada Estrita**: Pratica cada escala com palhetada estritamente alternada (Baixo - Cima - Baixo - Cima) para sincronizar o movimento rítmico das duas mãos com o metrónomo.
• **Mão Esquerda Estável**: Mantém os dedos curvados e perto das cordas mesmo quando não estão a tocar — dedos que voam longe do braço perdem preciosas frações de segundo.
""",
        interactive_demo="scales",
        title_en="Scales, Greek Modes & Circle of Fifths",
        subtitle_en="Tonal, modal melodic structures and key signatures",
        summary_en="Learn formulaic structures for Major, Minor (Natural, Harmonic, Melodic), Pentatonic scales, Greek modes, and Circle of Fifths.",
        content_markdown_en="""
### 1. Major Scale Formula
The **Major Scale** formula in Whole (W) and Half (H) steps is:

**W – W – H – W – W – W – H**

Degrees: **1 - 2 - 3 - 4 - 5 - 6 - 7**.
Example in C Major: **C - D - E - F - G - A - B - C**.

---

### 2. The 7 Greek Modes
1. **Ionian (I)**: Major Scale (**1, 2, 3, 4, 5, 6, 7**) — Bright, stable.
2. **Dorian (ii)**: Minor with Major 6th (**1, 2, ♭3, 4, 5, 6, ♭7**) — Jazz, cool.
3. **Phrygian (iii)**: Minor with Minor 2nd (**1, ♭2, ♭3, 4, 5, ♭6, ♭7**) — Spanish, exotic.
4. **Lydian (IV)**: Major with Augmented 4th (**1, 2, 3, ♯4, 5, 6, 7**) — Ethereal, filmic.
5. **Mixolydian (V)**: Major with Minor 7th (**1, 2, 3, 4, 5, 6, ♭7**) — Blues, Rock.
6. **Aeolian (vi)**: Natural Minor (**1, 2, ♭3, 4, 5, ♭6, ♭7**) — Sad, dark.
7. **Locrian (vii°)**: Diminished (**1, ♭2, ♭3, 4, ♭5, ♭6, ♭7**) — Unstable.
""",
        piano_focus_en="""
🎹 **On Piano**:
• C Major scale uses only white keys.
• Fingering pattern for C Major (Right Hand): **1-2-3-1-2-3-4-5** (thumb under after 3rd finger E).
""",
        guitar_focus_en="""
🎸 **On Guitar / Viola**:
• Major scale box pattern: 3-notes-per-string system across 6 strings.
""",
    ),

    # ----------------------------------------------------
    # CAPÍTULO 4
    # ----------------------------------------------------
    TheoryChapter(
        id="chap4_chords_triads",
        number=4,
        title="Formação de Acordes, Tríades & Inversões",
        subtitle="A anatomia das tríades, acordes suspensos e voice leading",
        difficulty="Intermédio",
        category="Harmonia",
        summary="Compreende como as notas se empilham em terças para criar acordes, a diferença estrutural entre Tríades Maiores, Menores, Diminutas e Aumentadas, e como usar inversões para conduzir vozes suaves.",
        content_markdown="""
### 1. O que é uma Tríade?
Uma **tríade** é um acorde formado por **3 notas sobrepostas em intervalos de terça**:
1. **Tónica (Fundamental / 1)**: A nota que dá nome ao acorde.
2. **Terça (3)**: Define a natureza do acorde (Maior ou Menor).
3. **Quinta (5)**: Define a estabilidade ou tensão (Justa, Diminuta ou Aumentada).

---

### 2. Os 4 Tipos Básicos de Tríades

| Tipo de Tríade | Símbolo | Fórmula de Graus | Intervalos Consecutivos | Exemplo (Dó) | Caráter Emocional |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Maior** | C, CM | **1 - 3 - 5** | Terça Maior (4st) + Terça Menor (3st) | C - E - G | Alegre, brilhante, estável |
| **Menor** | Cm, C- | **1 - ♭3 - 5** | Terça Menor (3st) + Terça Maior (4st) | C - E♭ - G | Melancólico, emotivo |
| **Diminuta** | Cdim, C° | **1 - ♭3 - ♭5** | Terça Menor (3st) + Terça Menor (3st) | C - E♭ - G♭ | Tenso, sombrio, dramático |
| **Aumentada** | Caug, C+ | **1 - 3 - ♯5** | Terça Maior (4st) + Terça Maior (4st) | C - E - G♯ | Misterioso, suspenso |

---

### 3. Acordes Suspensos (Sus4 e Sus2)
Substituem a terça pela quarta ou segunda, eliminando a definição de maior/menor:
• **Sus4**: **1 - 4 - 5** (Ex: C - F - G). Cria forte expectativa de resolver na terça maior.
• **Sus2**: **1 - 2 - 5** (Ex: C - D - G). Tem sonoridade aberta, suave e moderna.

---

### 4. Inversões de Acordes
A nota mais grave tocada no acorde (o **Baixo**) define o estado de inversão:
• **Posição Fundamental**: A tónica está no baixo (**1 - 3 - 5**). Ex: C no baixo → C/C.
• **1ª Inversão**: A terça está no baixo (**3 - 5 - 1**). Ex: E no baixo → C/E.
• **2ª Inversão**: A quinta está no baixo (**5 - 1 - 3**). Ex: G no baixo → C/G.

*Aplicações de Voice Leading*: As inversões permitem que as notas do baixo se movam por graus conjuntos (passos de 1 ou 2 semitons) em vez de grandes saltos, tornando a música muito mais fluida e elegante.
""",
        piano_focus="""
🎹 **No Piano**:
• Posição Fundamental de Dó Maior (Mão Direita): Dedos **1-3-5** nas teclas C - E - G.
• 1ª Inversão (C/E): Dedos **1-2-5** nas teclas E - G - C.
• 2ª Inversão (C/G): Dedos **1-3-5** nas teclas G - C - E.
• Na mão esquerda, pode-se tocar apenas a fundamental da oitava grave (ex: Dó 2) ou uma oitava completa.
• **Economia de Movimento (Voice Leading)**: Ao passar de C [C-E-G] para F [C-F-A], repara que a nota C é comum — mantém o dedo 1 no C e move apenas os dedos 3 e 5 para F e A (2ª inversão de Fá).
• **Ataque Sincronizado**: Pressiona as 3 notas da tríade rigorosamente ao mesmo milissegundo para evitar que soe como um arpejo desleixado.
""",
        guitar_focus="""
🎸 **Na Viola / Guitarra**:
• Os acordes de viola frequentemente dobram notas (por exemplo, a forma aberta de Dó Maior [X-3-2-0-1-0] toca: Mudo - C - E - G - C - E, contendo duas tónicas e duas terças).
• As tríades estritas de 3 cordas (em cordas agudas: 1ª, 2ª e 3ª cordas) são a ferramenta secreta dos guitarristas de Funk, Pop e Jazz para cortar na mistura sem embolar com o baixo.
• **Técnica do Dedo Pivot**: Na transição entre acordes (ex: Am para C), mantém o dedo indicador e médio fixos na 2ª e 4ª cordas e desloca apenas o dedo 3 para a 5ª corda.
• **Troca Antecipada no Ar**: Ao mudar de acorde, move todos os dedos em bloco no ar já com a forma do próximo acorde, em vez de assentar um dedo de cada vez.
""",
        interactive_demo="chords",
        title_en="Chord Construction, Triads & Inversions",
        subtitle_en="Triad anatomy, suspended chords, and voice leading",
        summary_en="Understand how notes stack in 3rds to form chords, structural differences between Major, Minor, Diminished, and Augmented triads, and inversions.",
        content_markdown_en="""
### 1. What is a Triad?
A **triad** is a 3-note chord built by stacking thirds:
1. **Root (1)**: Defines the chord name.
2. **Third (3)**: Defines Major or Minor quality.
3. **Fifth (5)**: Defines stability or tension (Perfect, Diminished, Augmented).

---

### 2. The 4 Basic Triad Types
• **Major (C)**: 1 - 3 - 5 (C - E - G)
• **Minor (Cm)**: 1 - ♭3 - 5 (C - E♭ - G)
• **Diminished (Cdim)**: 1 - ♭3 - ♭5 (C - E♭ - G♭)
• **Augmented (Caug)**: 1 - 3 - ♯5 (C - E - G♯)
""",
        piano_focus_en="""
🎹 **On Piano**:
• Root position C Major: fingers 1-3-5 on C - E - G.
• 1st Inversion (C/E): fingers 1-2-5 on E - G - C.
• 2nd Inversion (C/G): fingers 1-3-5 on G - C - E.
""",
        guitar_focus_en="""
🎸 **On Guitar / Viola**:
• Open C chord (X-3-2-0-1-0) doubles the root and 3rd.
""",
    ),

    # ----------------------------------------------------
    # CAPÍTULO 5
    # ----------------------------------------------------
    TheoryChapter(
        id="chap5_harmonic_field_tetrads",
        number=5,
        title="Campo Harmónico, Graus Tonais & Tétrades",
        subtitle="A matriz das progressões harmónicas, funções e sétimas",
        difficulty="Avançado",
        category="Harmonia Funcional",
        summary="Aprende a harmonizar uma escala para extrair o Campo Harmónico Maior e Menor, as funções de Tónica, Subdominante e Dominante, e a construção de Tétrades com 7ªs (maj7, 7, m7, m7b5).",
        content_markdown="""
### 1. O Campo Harmónico Maior
Ao construir tríades sobre cada grau da escala maior usando apenas as notas da escala, obtemos os 7 acordes da tonalidade:

**I (Maior)   ii (menor)   iii (menor)   IV (Maior)   V (Maior)   vi (menor)   vii° (diminuto)**

Exemplo no Campo Harmónico de **Dó Maior**:
• **I**: C (Dó Maior)
• **ii**: Dm (Ré Menor)
• **iii**: Em (Mi Menor)
• **IV**: F (Fá Maior)
• **V**: G (Sol Maior)
• **vi**: Am (Lá Menor - Relativa Menor)
• **vii°**: Bdim (Si Diminuto)

---

### 2. As 3 Funções Harmónicas Fundamentais
1. **Função Tónica (I, vi, iii)**: Sensação de repouso, estabilidade, casa e conclusão.
2. **Função Subdominante (IV, ii)**: Sensação de movimento, afastamento moderado e preparação.
3. **Função Dominante (V, vii°)**: Tensão máxima, atração e urgência irresistível de resolução na Tónica (devido à presença do trítono).

---

### 3. Tétrades: Acordes com Sétima (4 Notas)
Ao adicionar uma quarta nota a 1 terça de distância da quinta, criamos as **Tétrades**:

• **Maior com 7ª Maior (maj7 / **Δ**)**: **1 - 3 - 5 - 7** (Graus I e IV). Sonoridade doce, sofisticada, jazz e bossa nova (ex: Cmaj7).
• **Dominante com 7ª (7)**: **1 - 3 - 5 - ♭7** (Grau V). Contém o trítono entre a 3ª e a 7ª menor (ex: G7 resolvendo em C).
• **Menor com 7ª (m7)**: **1 - ♭3 - 5 - ♭7** (Graus ii, iii e vi). Sonoridade suave e aveludada (ex: Dm7, Am7).
• **Meio-Diminuto (m7**♭**5 / **ø**)**: **1 - ♭3 - ♭5 - ♭7** (Grau vii°). Tenso e dramático, o grau ii em tonalidades menores (ex: Bm7b5).
• **Diminuto Completo (dim7 / °7)**: **1 - ♭3 - ♭5 - ♭♭7**. Acorde simétrico de 4 terças menores consecutivas.

---

### 4. As Progressões de Acordes Mais Célebres
• **ii - V - I**: A progressão mais importante do Jazz, Bossa Nova e Pop (ex: Dm7 → G7 → Cmaj7).
• **I - V - vi - IV**: A progressão dos '4 acordes' presente em centenas de êxitos pop (ex: C → G → Am → F).
• **I - vi - IV - V**: A progressão clássica dos anos 50 / Doo-wop (ex: C → Am → F → G).
""",
        piano_focus="""
🎹 **No Piano**:
• Para tocar tétrades com sonoridade rica, evita duplicar a fundamental na mão direita.
• Distribuição recomendada (*Rootless Voicings*):
  - Mão Esquerda: Toca a Fundamental e a Quinta (ou só a Fundamental no baixo).
  - Mão Direita: Toca a 3ª e a 7ª (as *Guide Tones* que definem o acorde) + extensões (9ª).
• **Equilíbrio Dinâmico (Voicing Balance)**: Aplica mais peso no dedo 5 (a nota mais aguda da tétrade) para que a melodia sobressaia com clareza sobre os acordes de acompanhamento.
• **Dedilhação de 4 Notas**: Para tétrades em posição fundamental (ex: Cmaj7 [C-E-G-B]), usa os dedos **1-2-3-5** (o dedo 4 fica relaxado sem rigidez).
""",
        guitar_focus="""
🎸 **Na Viola / Guitarra**:
• Em estilos como Bossa Nova e Jazz, usam-se acordes *Drop 2* e *Drop 3* nas cordas médias (6-4-3-2 ou 5-4-3-2) sem palheta, dedilhando com o polegar (baixo) e dedos indicador, médio e anelar.
• Exemplo clássico de Bossa Nova em Dó Maior:
  - Cmaj7: [X-3-2-4-0-0] ou [X-3-5-4-5-X]
  - Dm7: [X-5-7-5-6-X]
  - G7: [3-X-3-4-3-X] ou [3-5-3-4-6-X]
• **Abafamento Intencional de Cordas (String Muting)**: Usa a lateral do polegar esquerdo ou a ponta do dedo que faz a tónica para tocar suavemente na corda 6 ou 5 e calá-la, garantindo que cordas indesejadas nunca soam.
• **Sincronismo Polegar + Dedos (PIMA)**: O polegar toca o baixo no tempo forte e os dedos I-M-A puxam as 3 cordas agudas em uníssono como uma pinça coordenada.
""",
        interactive_demo="fretboard",
        title_en="Harmonic Field, Tonal Functions & Seventh Chords",
        subtitle_en="Harmonic progressions matrix, functional harmony, and 7th chords",
        summary_en="Learn how to harmonize major/minor scales to build diatonic fields, Tonic/Subdominant/Dominant functions, and 7th chords (maj7, 7, m7, m7b5).",
        content_markdown_en="""
### 1. Major Harmonic Field
Building triads on each degree of the Major scale yields 7 diatonic chords:

**I (Major)   ii (minor)   iii (minor)   IV (Major)   V (Major)   vi (minor)   vii° (diminished)**

Example in C Major: **C, Dm, Em, F, G, Am, Bdim**.

---

### 2. Fundamental Harmonic Functions
1. **Tonic (I, vi, iii)**: Rest, stability, resolution.
2. **Subdominant (IV, ii)**: Moderate motion, preparation.
3. **Dominant (V, vii°)**: Maximum tension, strong pull toward Tonic.

---

### 3. Seventh Chords (4-Note Tetrads)
• **Major 7th (maj7)**: 1 - 3 - 5 - 7 (e.g. Cmaj7)
• **Dominant 7th (7)**: 1 - 3 - 5 - ♭7 (e.g. G7)
• **Minor 7th (m7)**: 1 - ♭3 - 5 - ♭7 (e.g. Dm7, Am7)
• **Half-Diminished (m7♭5)**: 1 - ♭3 - ♭5 - ♭7 (e.g. Bm7b5)
""",
        piano_focus_en="""
🎹 **On Piano**:
• Use rootless voicings: left hand plays root, right hand plays guide tones (3rd & 7th).
• Common progression: **ii7 - V7 - Imaj7** (e.g. Dm7 → G7 → Cmaj7).
""",
        guitar_focus_en="""
🎸 **On Guitar / Viola**:
• Drop 2 and Drop 3 chord shapes across middle string sets.
""",
    ),

    # ----------------------------------------------------
    # CAPÍTULO 6
    # ----------------------------------------------------
    TheoryChapter(
        id="chap6_advanced_harmony",
        number=6,
        title="Harmonia Avançada, Modulação & Empréstimo Modal",
        subtitle="Dominantes secundárias, intercâmbio modal e substituição tritónica",
        difficulty="Avançado",
        category="Harmonia Avançada",
        summary="Leva a tua compreensão harmónica ao nível profissional: aprende a usar dominantes secundárias (V7/V), acordes de empréstimo modal (como o iv menor e bVI), substituição de trítono (SubV7) e modulações suaves.",
        content_markdown="""
### 1. Dominantes Secundárias (V7 / X)
Qualquer acorde diatónico maior ou menor do campo harmónico pode ser antecedido pela sua própria dominante (um acorde maior com 7ª a 1 quinta justa acima dele):

• **V7 / V**: Dominante da Dominante (ex: D7 conduzindo a G7 em tom de Dó).
• **V7 / ii**: Dominante do grau ii (ex: A7 conduzindo a Dm em tom de Dó).
• **V7 / vi**: Dominante do grau vi (ex: E7 conduzindo a Am em tom de Dó).

*Efeito sonoro*: Cria uma atração direcional irresistível e introduz notas fora da escala (*acidentes ocorrentes*) que enriquecem a harmonia sem mudar de tom.

---

### 2. Empréstimo Modal (Intercâmbio Modal)
Consiste em 'pedir emprestados' acordes da escala homónima menor para usar numa tonalidade maior:

• **O Subdominante Menor (iv)**: Usar **Fm** em vez de **F** em tom de Dó Maior (progressão clássica: **I → IV → iv → I**, ex: **C → F → Fm → C**). Soa extremamente emotivo e nostálgico.
• **♭VI** e **♭VII**: Usar A♭ e B♭ em tom de Dó Maior (muito comum no Rock e Cinema).

---

### 3. Substituição Tritónica (SubV7)
Todo o acorde dominante com 7ª pode ser substituído por outro dominante localizado a **1 trítono de distância**:
• Em Dó Maior, o dominante normal é **G7** (notas: G - B - D - F).
• O trítono entre as notas **B** e **F** é exatamente o mesmo presente no acorde de **D♭7** (notas: D♭ - F - A♭ - C♭/B).
• Logo, podemos substituir **Dm7 → G7 → C** por **Dm7 → D♭7 → C**.
• *Vantagem*: O baixo desce cromaticamente por meio-tom (**D → D♭→ C**), criando a assinatura harmónica da Bossa Nova e do Jazz contemporâneo!
""",
        piano_focus="""
🎹 **No Piano**:
• A descida cromática do SubV7 permite uma condução de vozes espetacular:
  - Dm7: Baixo D / Mão Direita [F - A - C]
  - D♭7: Baixo D♭ / Mão Direita [F - A♭ - B]
  - Cmaj7: Baixo C / Mão Direita [E - G - B]
• Repara como o baixo e a voz superior descem suavemente em semitons!
• **Pedalação Sincopada (Troca de Pedal de Sustentação)**: Ao mudar para o acorde SubV7 ou de empréstimo modal, solta e volta a carregar no pedal *imediatamente após* tocar o novo acorde para limpar as ressonâncias do acorde anterior sem cortar o som.
• **Toque Legato com Dedos**: Pratica ligar as notas de topo da harmonia exclusivamente com a articulação dos dedos antes de adicionar o pedal.
""",
        guitar_focus="""
🎸 **Na Viola / Guitarra**:
• A substituição tritónica na viola é extremamente confortável porque a digitação do acorde dominante simplesmente desliza 1 traste para trás:
  - Dm7 no 5º traste [X-5-7-5-6-X]
  - D♭7 no 4º traste [X-4-3-4-2-X]
  - Cmaj7 no 3º traste [X-3-5-4-5-X]
• João Gilberto e Tom Jobim construíram a linguagem da Bossa Nova explorando estes movimentos cromáticos no violão/viola.
• **Deslizar de Traste com Dedo Guia**: Mantém a pressão do dedo que faz a nota guia enquanto deslizas 1 traste para trás, mantendo a continuidade tímbrica.
• **Substituição de Baixos com o Polegar**: Nas cordas graves 6 e 5, usa o polegar com peso natural para dar clareza aos baixos cromáticos descendentes.
""",
        interactive_demo="circle_of_fifths",
        title_en="Advanced Harmony, Modulation & Modal Interchange",
        subtitle_en="Secondary dominants, modal borrowing, and tritone substitution",
        summary_en="Master secondary dominants (V7/V), modal borrowing (like minor iv and bVI), tritone substitution (SubV7), and smooth modulations.",
        content_markdown_en="""
### 1. Secondary Dominants (V7 / X)
Any diatonic chord can be preceded by its own dominant chord (a Major 7th chord 1 fifth above):
• **V7 / V**: Dominant of the Dominant (e.g. D7 → G7 in C Major).
• **V7 / ii**: Dominant of the ii chord (e.g. A7 → Dm in C Major).

---

### 2. Modal Borrowing
Borrowing chords from the parallel minor scale into a major key:
• **Minor Subdominant (iv)**: Using **Fm** instead of **F** in C Major (**C → F → Fm → C**).

---

### 3. Tritone Substitution (SubV7)
Replacing a dominant 7th chord with another dominant 1 tritone away (e.g. **Dm7 → D♭7 → Cmaj7** instead of G7).
""",
        piano_focus_en="""
🎹 **On Piano**:
• SubV7 creates smooth chromatic voice leading in the bass (D → D♭ → C).
""",
        guitar_focus_en="""
🎸 **On Guitar / Viola**:
• Tritone substitution simply slides the dominant chord shape 1 fret down.
""",
    ),

    # ----------------------------------------------------
    # CAPÍTULO 7
    # ----------------------------------------------------
    TheoryChapter(
        id="chap7_piano_guide",
        number=7,
        title="Guia Prático de Piano & Teclado",
        subtitle="Postura, digitação, coordenação das mãos e aberturas de acordes",
        difficulty="Prático",
        category="Instrumento: Piano",
        summary="Manual essencial para tocar piano com boa técnica: numeração dos dedos, padrões de digitação de escalas, coordenação rítmica entre a mão esquerda e direita, e técnicas de acompanhamento em bloco e arpejado.",
        content_markdown="""
### 1. Numeração dos Dedos no Piano
Em ambas as mãos, os dedos são numerados do polegar ao mindinho:
• **1**: Polegar
• **2**: Indicador
• **3**: Médio
• **4**: Anelar
• **5**: Mindinho

---

### 2. Postura e Toque
• Mãos relaxadas e curvadas como se estivesses a segurar uma bola de ténis suave.
• Pulsos alinhados com os antebraços (sem afundar nem levantar excessivamente).
• O peso dos braços transfere-se para a ponta dos dedos em vez de fazer força apenas com as articulações.

---

### 3. Padrões de Acompanhamento no Piano
1. **Acordes em Bloco (Root + Chords)**:
   - Mão Esquerda: Toca a fundamental ou oitava no 1º tempo do compasso.
   - Mão Direita: Toca a tríade/tétrade em ritmo estável (ex: semínimas ou síncopes).
2. **Baixo Alberti**: Arpejo clássico **1 - 5 - 3 - 5** (muito comum em Mozart e no Pop clássico).
3. **Arpejo Balada 1-5-8-9-10**:
   - Mão Esquerda dedilha a Fundamental (1), Quinta (5), Oitava (8) e Nona (9) criando uma textura orquestral contínua e moderna.
""",
        piano_focus="""
🎹 **Exercício Recomendado**:
1. Toca a progressão **I - vi - IV - V** em Dó Maior (C - Am - F - G).
2. Na mão esquerda, toca a nota fundamental em oitavas graves.
3. Na mão direita, usa inversões para manter a mão quase no mesmo sítio:
   - C: [G - C - E]
   - Am: [A - C - E]
   - F: [A - C - F]
   - G: [G - B - D]
• **Independência dos Dedos 4 e 5**: Como os dedos 4 e 5 partilham tendões comuns, pratica levantar o dedo 4 mantendo o 3 e o 5 apoiados, sem forçar nem sentir dor.
• **Estrutura de Rotina de 20 Minutos**:
  - 5 min: Aquecimento & Escalas a 70% BPM.
  - 10 min: Peça / Repertório por secções pequenas de 2 a 4 compassos.
  - 5 min: Treino auditivo e leitura de pauta à primeira vista.
""",
        guitar_focus="""
🎸 **Dica de Interligação**:
• Entender as aberturas do piano ajuda o guitarrista a visualizar as notas absolutas que compõem a harmonia, permitindo criar linhas melódicas mais ricas na guitarra/viola.
• **Crossover de Repertório**: Experimenta tocar a linha do baixo de Alberti do piano (1-5-3-5) nas 3 cordas mais graves da viola usando o polegar e indicador.
• **Treino de Ouvido Harmónico**: Toca um acorde de piano no estúdio e tenta reproduzir o mesmo som na viola de ouvido, encontrando os trastes certos.
""",
        interactive_demo="piano_interactive",
        title_en="Practical Piano & Keyboard Guide",
        subtitle_en="Posture, fingering, hand coordination, and chord voicings",
        summary_en="Essential guide to playing piano with sound technique: finger numbering, scale fingerings, hand independence, and accompaniment patterns.",
        content_markdown_en="""
### 1. Piano Finger Numbering
• **1**: Thumb
• **2**: Index
• **3**: Middle
• **4**: Ring
• **5**: Pinky

---

### 2. Posture & Touch
• Curved, relaxed hands like holding a soft tennis ball.
• Wrists aligned with forearms.
""",
        piano_focus_en="""
🎹 **Recommended Exercise**:
• Play **I - vi - IV - V** in C Major (C - Am - F - G) using voice leading inversions.
""",
        guitar_focus_en="""
🎸 **Cross-Instrument Tip**:
• Understanding piano voicings helps guitarists visualize chord notes across frets.
""",
    ),

    # ----------------------------------------------------
    # CAPÍTULO 8
    # ----------------------------------------------------
    TheoryChapter(
        id="chap8_guitar_guide",
        number=8,
        title="Guia Prático de Viola & Sistema CAGED",
        subtitle="O mapa do braço, pestanas, dedilhados e formas móveis de acordes",
        difficulty="Prático",
        category="Instrumento: Viola",
        summary="Domina o braço da viola e guitarra acústica: o revolucionário Sistema CAGED para tocar qualquer acorde em 5 regiões do braço, técnica de pestana sem dor, dedilhados e leitura de cifras e diagramas.",
        content_markdown="""
### 1. As 6 Cordas e Numeração dos Dedos na Viola
• **Mão Esquerda (Digitação no Braço)**:
  - **1**: Indicador
  - **2**: Médio
  - **3**: Anelar
  - **4**: Mindinho
  - *(T / P)*: Polegar (para bordões ou apoio atrás do braço).
• **Mão Direita (Dedilhados / P.I.M.A.)**:
  - **P**: Polegar (responsável pelas cordas graves: 6ª, 5ª e 4ª).
  - **I**: Indicador (3ª corda).
  - **M**: Médio (2ª corda).
  - **A**: Anelar (1ª corda).

---

### 2. O Sistema CAGED
O **Sistema CAGED** baseia-se no facto de existirem **5 formas de acordes abertos fundamentais**:
**C (Dó)   A (Lá)   G (Sol)   E (Mi)   D (Ré)**

Qualquer um destes 5 formatos pode ser deslocado para a frente no braço usando uma **Pestana** (o dedo indicador a fazer de capotraste móvel), permitindo tocar **qualquer acorde em 5 posições diferentes** ao longo de todo o instrumento!

• **Forma de E**: Pestana com a tónica na 6ª corda (ex: Fá no 1º traste, Sol no 3º traste, Lá no 5º traste).
• **Forma de A**: Pestana com a tónica na 5ª corda (ex: Si no 2º traste, Dó no 3º traste, Ré no 5º traste).

---

### 3. Dicas de Ouro para a Pestana (Barre Chords)
1. **Posição do Dedo 1**: Usa a lateral ligeiramente externa e ossuda do dedo indicador, não a parte macia da frente.
2. **Proximidade do Traste**: Coloca o dedo bem encostado ao ferrinho do traste (sem ficar em cima).
3. **Polegar Atrás**: O polegar da mão esquerda deve ficar centrado atrás do braço à altura do dedo médio, criando uma pinça firme sem forçar o pulso.
4. **Puxar com o Braço**: Usa a força da musculatura das costas e do braço em direção ao corpo, em vez de apenas espremer com a mão.
""",
        piano_focus="""
🎹 **Dica de Interligação**:
• O teclado do piano é linear (uma única linha reta de notas graves a agudas).
• O braço da viola é uma matriz bidimensional (as mesmas notas repetem-se em diferentes cordas e trastes com timbres distintos).
• **Visualização Mental**: Imagina as 5 formas do CAGED como transposição cromática em blocos, equivalente a usar a função de transpose ou mudar de oitava no teclado.
""",
        guitar_focus="""
🎸 **Exercício Recomendado**:
1. Toca o acorde de **Sol Maior** nas suas 3 formas principais:
   - Aberto (Forma G aberta): [3-2-0-0-0-3]
   - Pestana na 6ª corda (Forma E no 3º traste): [3-5-5-4-3-3]
   - Pestana na 5ª corda (Forma A no 10º traste): [X-10-12-12-12-10]
2. Ouve como todas contêm as notas Sol, Si e Ré, mas com 'voicings' e brilho diferentes!
• **Exercício da Aranha (Spider Walk 1-2-3-4)**: Toca trastes 1-2-3-4 corda a corda com dedos 1-2-3-4 sem levantar os dedos anteriores para desenvolver força, independência e precisão cirúrgica.
• **Rotina de Prática Diária Eficaz**:
  - 5 min: Spider Walk e alongamentos lentos.
  - 10 min: Mudanças de pestanas e repertório com metrónomo a 70% BPM.
  - 5 min: Prática de palhetada alternada e improvisação sobre backing track.
""",
        interactive_demo="guitar_fretboard",
        title_en="Practical Guitar & CAGED System Guide",
        subtitle_en="Fretboard navigation, barre chords, fingerpicking, and mobile chord shapes",
        summary_en="Master the guitar fretboard: the CAGED system for 5 positions per chord, pain-free barre technique, and PIMA fingerpicking.",
        content_markdown_en="""
### 1. The CAGED System
The **CAGED System** is based on 5 open chord shapes: **C - A - G - E - D**. Sliding any shape with a barre allows playing **any chord in 5 fretboard regions**.
""",
        piano_focus_en="""
🎹 **Cross-Instrument Tip**:
• View CAGED shapes as movable chromatic blocks across 2D string matrices.
""",
        guitar_focus_en="""
🎸 **Recommended Exercise**:
• Play G Major in 3 positions: Open G, E-shape (3rd fret), A-shape (10th fret).
""",
    ),

    # ----------------------------------------------------
    # CAPÍTULO 9 — Ritmo, Compasso & Pulsação
    # ----------------------------------------------------
    TheoryChapter(
        id="chap9_rhythm",
        number=9,
        title="Ritmo, Compasso & Pulsação",
        subtitle="A dimensão temporal da música: tempo, métricas e figuras rítmicas",
        difficulty="Iniciante",
        category="Fundamentos",
        summary="Compreende como a música se organiza no tempo: o que é o pulso, o compasso, as figuras rítmicas e como ler e executar ritmos simples e compostos.",
        content_markdown="""
### 1. O Pulso e o Tempo
O **pulso** (ou batida) é a unidade de tempo constante e regular que estrutura toda a música — como o tick do metrónomo. O **tempo** define a velocidade dessa batida, medido em **BPM (Beats Per Minute)**:
• 60 BPM = 1 batida por segundo (Largo)
• 100 BPM = velocidade moderada de marcha
• 160 BPM = rápido (Allegro)

**Exemplo prático**: Bate palmas regularmente enquanto ouves uma música. Se consegues manter-te sincronizado, estás a sentir o pulso.

---

### 2. O Compasso
O compasso organiza os pulsos em grupos regulares. A **fração de compasso** (ou clave de tempo) indica:
• **Numerador**: quantas batidas há por compasso
• **Denominador**: qual figura rítmica vale 1 batida

| Compasso | Leitura | Carácter |
| --- | --- | --- |
| 4/4 | 4 semínimas por compasso | Marcha, Pop, Rock |
| 3/4 | 3 semínimas por compasso | Valsa, Canção de embalar |
| 6/8 | 6 colcheias (2 grupos de 3) | Barcarola, Jig irlandesa |
| 2/4 | 2 semínimas por compasso | Marcha militar, Polca |

---

### 3. Figuras Rítmicas e seus Valores
| Figura | Nome PT | Valor (em 4/4) | Símbolo |
| --- | --- | --- | --- |
| Semibreve | Whole note | 4 batidas | ○ |
| Mínima | Half note | 2 batidas | ♩ aberta |
| Semínima | Quarter note | 1 batida | ♩ |
| Colcheia | Eighth note | 1/2 batida | ♪ |
| Semicolcheia | Sixteenth note | 1/4 batida | ♬ |

**Ponto de aumentação**: Acrescenta metade do valor à figura. Ex: Semínima com ponto = 1 + 0.5 = **1.5 batidas**.

---

### 4. Pausa e Silêncio
Cada figura tem uma pausa correspondente com o mesmo valor de duração. As pausas são tão musicais quanto as notas — o silêncio cria tensão, espaço e expressão.

---

### 5. Síncopa e Contratempos
A **síncopa** ocorre quando o acento cai num tempo fraco ou entre tempos, criando surpresa rítmica. É a base do jazz, funk e bossa nova.

**Exemplo prático de síncopa**: Em 4/4, em vez de acentuar os tempos 1-2-3-4, acentua os tempos "e" (entre 1 e 2) — dás um salto rítmico que "engana" o ouvido de forma agradável.
""",
        piano_focus="""
🎹 **Exercício de Ritmo no Piano**:
1. Usa o **metrónomo** a 60 BPM.
2. Toca a nota C4 (Dó central) com a mão direita em semínimas (1 nota por batida).
3. Com a mão esquerda, toca C3 em mínimas (1 nota a cada 2 batidas).
4. Aumenta progressivamente para 80 BPM → 100 BPM quando sentires estabilidade.
5. Experimenta valsa (3/4): 1 nota grave no tempo 1, 2 acordes leves nos tempos 2 e 3 (boom-chick-chick).

**Exercício de independência rítmica**: Toca com a MD um ritmo em semínimas (1-2-3-4) e com a ME colcheias (1-e-2-e-3-e-4-e). Começa devagar — a independência das mãos é um dos maiores desafios do piano.
""",
        guitar_focus="""
🎸 **Ritmo na Viola**:
• O ritmo na guitarra expressa-se sobretudo na **mão direita** (palhetada ou dedilhado).
• Padrão de palhetada em 4/4 básico: **↓ ↓ ↑ ↓ ↑** (tempo 1: baixo, 2: baixo, "e": cima, 3: baixo, "e": cima).
• Para valsa (3/4): **↓ ↑ ↑** — acenta fortemente o primeiro tempo.

**Exercício prático**: Com o acorde de Lá menor (Am) aberto:
1. Toca só as palhetadas para baixo nos 4 tempos durante 4 compassos.
2. Adiciona as palhetadas para cima entre os tempos.
3. Varia o padrão criando o teu próprio groove.
""",
        interactive_demo="notes",
        title_en="Rhythm, Meter & Pulse",
        subtitle_en="The temporal dimension of music: tempo, meters, and rhythmic values",
        summary_en="Understand how music organizes in time: pulse, meters, note values, rest durations, and syncopation.",
        content_markdown_en="""
### 1. Pulse and Tempo
The **pulse** is the regular beat structuring music. **Tempo** measures its speed in **BPM (Beats Per Minute)**:
• 60 BPM = 1 beat/sec (Largo)
• 120 BPM = Moderate speed
• 160 BPM = Fast (Allegro)

---

### 2. Time Signatures
• **4/4**: 4 quarter notes per measure (Pop, Rock)
• **3/4**: 3 quarter notes per measure (Waltz)
• **6/8**: 6 eighth notes per measure (Compound)
""",
        piano_focus_en="""
🎹 **Piano Rhythm Practice**:
• Play C4 quarter notes with right hand while left hand plays C3 half notes at 60 BPM.
""",
        guitar_focus_en="""
🎸 **Guitar Strumming**:
• 4/4 Basic Strum Pattern: **↓ ↓ ↑ ↓ ↑** (Down, Down, Up, Down, Up).
""",
    ),

    # ----------------------------------------------------
    # CAPÍTULO 10 — Forma Musical & Estrutura
    # ----------------------------------------------------
    TheoryChapter(
        id="chap10_form",
        number=10,
        title="Forma Musical & Estrutura",
        subtitle="Como a música se organiza em secções, temas e arcos dramáticos",
        difficulty="Intermédio",
        category="Composição",
        summary="Aprende a reconhecer e utilizar as formas musicais mais comuns — de simples estruturas AB a complexas formas de sonata — e como a repetição e o contraste criam significado.",
        content_markdown="""
### 1. O que é a Forma Musical?
A **forma** é a arquitectura de uma peça — como as secções se organizam no tempo para criar unidade, variedade e significado. Reconhecer a forma ajuda a:
• Aprender repertório mais depressa (sabes o que vem a seguir)
• Memorizar de forma mais eficiente
• Improvisar com estrutura

---

### 2. Formas Fundamentais

**Forma Binária (AB)**
Duas secções contrastantes. Frequente em danças barrocas.
• A: Tema principal (frequentemente termina na dominante)
• B: Desenvolvimento e regresso à tónica
*Exemplo*: Muitos Minuetos de Bach e Handel.

**Forma Ternária (ABA)**
A secção A regressa após um contraste B. Cria sensação de regresso a casa.
*Exemplos*: Noturnos de Chopin, Blues de 12 compassos (AAB), a maioria das canções pop.

**Forma Rondó (ABACA...)**
Um refrão (A) alterna com episódios diferentes (B, C...). Muito usado em finais de concertos clássicos.

**Forma Sonata (Exposição → Desenvolvimento → Reexposição)**
A forma mais complexa e influente da música erudita:
• **Exposição**: Apresenta 2 temas — Tema I (tónica) e Tema II (dominante/relativa maior)
• **Desenvolvimento**: Fragmenta e transforma os temas, modula por várias tonalidades, cria tensão máxima
• **Reexposição**: Ambos os temas regressam à tónica, resolvendo a tensão

---

### 3. Estrutura de uma Canção Pop/Rock
| Secção | Função | Compassos típicos |
| --- | --- | --- |
| Intro | Estabelece o ambiente | 4–8 compassos |
| Verso | Conta a história | 8–16 compassos |
| Pré-refrão | Cria tensão ascendente | 4–8 compassos |
| Refrão | Clímax emocional e melódico | 8–16 compassos |
| Ponte | Contraste — nova perspectiva | 8 compassos |
| Outro/Fade | Encerramento | 4–8 compassos |

---

### 4. Repetição e Variação
A música usa repetição para criar familiaridade e coerência, e variação para manter o interesse. Algumas técnicas:
• **Sequência**: Repete um motivo a alturas diferentes (ex: subindo grau a grau)
• **Aumentação/Diminuição**: O mesmo motivo em valores rítmicos maiores/menores
• **Inversão**: O motivo de pernas para o ar (o que subia desce, e vice-versa)
""",
        piano_focus="""
🎹 **Análise de Forma ao Piano**:
1. Pega numa peça que já saibas (ex: "Ode à Alegria").
2. Identifica onde as secções começam e terminam — marca com lápis na partitura.
3. Pergunta: esta secção é repetição, variação ou contraste?

**Exercício de composição simples (Forma ABA)**:
• A (4 compassos): Improvisa uma melodia simples em Dó Maior, toca-a duas vezes.
• B (4 compassos): Muda para Lá menor (relativa menor) — cria contraste de carácter.
• A' (4 compassos): Regressa à melodia original — podes ornamentá-la ligeiramente.
""",
        guitar_focus="""
🎸 **Forma no Contexto da Viola**:
• Aprende a reconhecer versos e refrões pelas progressões de acordes — o refrão normalmente resolve de forma mais conclusiva na tónica.
• **Progressão de verso típica**: Am - F - C - G (carácter aberto, interrogativo)
• **Progressão de refrão típica**: C - G - Am - F (mais resolutiva, "completa")
• Experimenta tocar ambas e sente a diferença emocional.

**Exercício**: Cria uma música em forma ABA com apenas 4 acordes:
• A: G - D - Em - C (Sol Maior — luminoso)
• B: Em - C - G - D (Meu menor — mais íntimo)
• A: G - D - Em - C (regresso)
""",
        interactive_demo="chords",
        title_en="Musical Form & Structure",
        subtitle_en="How music organizes in sections, themes, and dramatic arcs",
        summary_en="Learn to recognize common musical forms (AB, ABA, Rondo, Sonata) and how repetition and contrast build musical narrative.",
        content_markdown_en="""
### 1. What is Musical Form?
**Form** is the architecture of a piece — organizing sections in time to create unity, contrast, and dramatic arc.

• **Binary Form (AB)**: Two contrasting sections.
• **Ternary Form (ABA)**: Section A returns after a B contrast.
• **Rondo (ABACA)**: Repeating main refrain (A) alternating with episodes (B, C).
""",
        piano_focus_en="""
🎹 **Piano Form Analysis**:
• Identify section boundaries and mark thematic returns.
""",
        guitar_focus_en="""
🎸 **Guitar Song Structure**:
• Recognize verse vs chorus chord progressions.
""",
    ),

    # ----------------------------------------------------
    # CAPÍTULO 11 — Dinâmica, Articulação & Expressão
    # ----------------------------------------------------
    TheoryChapter(
        id="chap11_dynamics",
        number=11,
        title="Dinâmica, Articulação & Expressão Musical",
        subtitle="Como o volume, o toque e o fraseado transformam notas em emoção",
        difficulty="Intermédio",
        category="Interpretação",
        summary="Domina as ferramentas da expressão musical: dinâmicas (pp a ff), articulações (legato, staccato, acento), fraseado e uso do pedal — os elementos que separam tocar notas de fazer música.",
        content_markdown="""
### 1. Dinâmicas — O Volume como Expressão
As indicações de dinâmica dizem-nos com que intensidade tocar. São sempre relativas ao contexto da peça:

| Símbolo | Nome | Significado |
| --- | --- | --- |
| ppp | Pianississimo | Extremamente suave |
| pp | Pianissimo | Muito suave |
| p | Piano | Suave |
| mp | Mezzo-piano | Moderadamente suave |
| mf | Mezzo-forte | Moderadamente forte |
| f | Forte | Forte |
| ff | Fortissimo | Muito forte |
| fff | Fortississimo | Extremamente forte |

**Crescendo (< )**: Aumento gradual de volume.
**Decrescendo/Diminuendo (> )**: Diminuição gradual de volume.

*Dica de interpretação*: Uma nota **p** tocada após um longo **ff** parece ainda mais silenciosa do que seria de outra forma — o ouvido é relativo, não absoluto.

---

### 2. Articulações — Como Tocar as Notas
• **Legato**: Notas ligadas sem interrupção. Notado por uma **ligadura de expressão** (arco curvo). Cria fluidez e cantabilidade.
• **Staccato**: Notas curtas e separadas (ponto acima/abaixo da nota). Cria leveza, humor, dança.
• **Acento (>)**: Nota tocada com ênfase súbita de volume.
• **Tenuto (—)**: Mantém a nota pelo seu valor total, com ligeiro peso.
• **Sforzando (sfz/sf)**: Acento súbito e forte numa nota específica.

---

### 3. Fraseado Musical
O fraseado é a arte de organizar as notas em **frases musicais** com início, desenvolvimento e conclusão — como frases faladas. Uma boa frase musical:
• Tem uma **cúpula** (nota mais alta ou mais intensa) para a qual todas as outras confluem
• Respira: deixa espaço antes de começar a próxima frase
• Conta uma história: início → tensão → resolução

**Exemplo**: Na melodia de "Happy Birthday", as primeiras 4 notas formam uma frase que "pergunta", e as 4 seguintes "respondem".

---

### 4. Agógica — Flexibilidade de Tempo
• **Rubato**: Liberdade expressiva no tempo — atrasar aqui, acelerar ali. Usado extensivamente em Chopin e Brahms.
• **Ritardando (rit.)**: Abrandar gradualmente.
• **Accelerando (accel.)**: Acelerar gradualmente.
• **A tempo**: Regressar ao tempo original.
""",
        piano_focus="""
🎹 **Dinâmica e Expressão no Piano**:
• O piano é o instrumento com **maior gama dinâmica** — do ppp ao fff.
• **Toque de peso**: Para tocar forte, usa o peso natural do braço em vez de força muscular dos dedos — o som fica mais cheio e menos duro.
• **Toque de legato**: Para ligar notas, levanta o dedo anterior apenas quando o próximo está completamente pressionado.

**Exercício de dinâmica**: Toca a escala de Dó Maior (C-D-E-F-G-A-B-C) de forma crescente (muito suave em C, fortíssimo em C agudo), depois de forma decrescente. Faz isto sem acelerar — o volume e o ritmo são independentes.

**Uso do Pedal de Sustain**:
• Pressiona o pedal com o calcanhar no chão e o pé inclinado para a frente.
• Troca o pedal (levanta e pressiona de novo) a cada mudança harmónica para evitar misturar acordes diferentes.
""",
        guitar_focus="""
🎸 **Expressão na Viola/Guitarra**:
• **Dinâmica de mão direita**: Toca mais perto da boca (ponte) para som mais brilhante e forte; mais perto do braço (escala) para som mais suave e aveludado.
• **Vibrato**: Oscila ligeiramente o dedo da mão esquerda no traste para criar vibração de tom — acrescenta emoção e sustain à nota.
  - Vibrato de pulso: o pulso esquerdo oscila para cima e para baixo.
  - Vibrato de braço: todo o antebraço gira ligeiramente.
• **Bend (dobrar a corda)**: Puxa a corda lateralmente para elevar o tom — efeito expressivo do blues e rock.

**Exercício de fraseado**: Toca uma melodia simples (ex: os primeiros 8 compassos de "Greensleeves") com staccato, depois com legato, depois com vibrato em cada nota longa. Sente como cada articulação cria uma emoção completamente diferente.
""",
        interactive_demo="notes",
        title_en="Dynamics, Articulation & Expression",
        subtitle_en="How volume, touch, and phrasing turn notes into emotion",
        summary_en="Master dynamic range (pp to ff), articulations (legato, staccato, accents), musical phrasing, and pedal technique.",
        content_markdown_en="""
### 1. Dynamics
• **pp**: Pianissimo (Very soft)
• **p**: Piano (Soft)
• **mf**: Mezzo-forte (Medium loud)
• **f**: Forte (Loud)
• **ff**: Fortissimo (Very loud)

---

### 2. Articulations
• **Legato**: Smooth, connected notes.
• **Staccato**: Short, detached notes.
• **Accent (>)**: Emphasized note.
""",
        piano_focus_en="""
🎹 **Dynamics on Piano**:
• Use arm weight for forte tones, controlled fingertips for pianissimo.
""",
        guitar_focus_en="""
🎸 **Guitar Expression**:
• Right-hand position changes tone (near bridge = bright, near fretboard = soft).
• Add vibrato on long sustained notes.
""",
    ),

    # ----------------------------------------------------
    # CAPÍTULO 12 — Transposição Prática & Tonalidades
    # ----------------------------------------------------
    TheoryChapter(
        id="chap12_transposition",
        number=12,
        title="Transposição Prática & Ciclo das Tonalidades",
        subtitle="Mover música entre tonalidades e dominar o círculo de quintas em contexto prático",
        difficulty="Avançado",
        category="Teoria Aplicada",
        summary="Aprende a transpor melodias e acordes para qualquer tonalidade, a usar o círculo de quintas como mapa de navegação harmónica, e a identificar rapidamente a armação de clave de qualquer tom.",
        content_markdown="""
### 1. O que é Transpor?
**Transpor** significa mover toda uma peça (ou secção) para uma tonalidade diferente, mantendo as relações intervalares entre todas as notas. O resultado soa igual mas numa altura diferente.

**Porquê transpor?**
• Adaptar à tessitura do cantor ou instrumento
• Facilitar a execução (ex: num instrumento transpositor como clarinete em Si♭)
• Criar contraste dentro da mesma peça (modulação)

---

### 2. O Círculo de Quintas — Mapa de Tonalidades
O círculo de quintas organiza as 12 tonalidades de forma que cada tonalidade adjacente difere por apenas **1 acidente** (1 sustenido ou 1 bemol a mais/menos):

**Tonalidades com Sustenidos** (sentido horário, adicionando ♯):
C → G → D → A → E → B → F♯/G♭

**Tonalidades com Bemóis** (sentido anti-horário, adicionando ♭):
C → F → B♭ → E♭ → A♭ → D♭ → G♭/F♯

**Regra para sustenidos**: O último ♯ adicionado é sempre o **7º grau** da nova tonalidade (um semitom abaixo da tónica).
**Regra para bemóis**: O penúltimo ♭ é sempre a **tónica** da nova tonalidade.

---

### 3. Como Transpor uma Melodia (Passo a Passo)
**Exemplo**: Transpor "Parabéns" de Dó Maior para Sol Maior (subir uma 5ª perfeita):

1. Identifica a tonalidade de origem: **Dó Maior** (sem acidentes)
2. Identifica a tonalidade de destino: **Sol Maior** (1 sustenido: F♯)
3. Calcula o intervalo de transposição: C → G = **5ª Perfeita (7 semitons)**
4. Sobe cada nota da melodia 7 semitons:
   - C (Dó) → G (Sol)
   - D (Ré) → A (Lá)
   - E (Mi) → B (Si)
   - F (Fá) → C (Dó)
   - G (Sol) → D (Ré)
5. Aplica os acidentes da nova armação de clave (F torna-se F♯)

---

### 4. Tabela de Armações de Clave
| Tonalidade Maior | Relativa Menor | # de Acidentes | Acidentes |
| --- | --- | --- | --- |
| Dó / C | Lá m / Am | 0 | — |
| Sol / G | Mi m / Em | 1♯ | F♯ |
| Ré / D | Si m / Bm | 2♯ | F♯, C♯ |
| Lá / A | Fá♯m / F♯m | 3♯ | F♯, C♯, G♯ |
| Mi / E | Dó♯m / C♯m | 4♯ | F♯, C♯, G♯, D♯ |
| Fá / F | Ré m / Dm | 1♭ | B♭ |
| Si♭ / B♭ | Sol m / Gm | 2♭ | B♭, E♭ |
| Mi♭ / E♭ | Dó m / Cm | 3♭ | B♭, E♭, A♭ |

---

### 5. Instrumentos Transpositores
Alguns instrumentos soam numa tonalidade diferente da escrita:
• **Clarinete em Si♭**: Soa 1 Tom abaixo — escreve-se 1 Tom acima do som desejado
• **Trompa em Fá**: Soa uma 5ª abaixo
• **Saxofone Alto em Mi♭**: Soa uma 6ª maior abaixo
• **Piano e Viola**: Não transpositores — o que está escrito é o que soa.
""",
        piano_focus="""
🎹 **Transposição ao Piano**:
• O piano é ideal para aprender transposição porque podes **ver** as teclas e **ouvir** imediatamente o resultado.

**Exercício de transposição prática**:
1. Toca a escala de Dó Maior: C-D-E-F-G-A-B-C (apenas teclas brancas).
2. Agora toca Sol Maior: G-A-B-C-D-E-F♯-G (a única mudança é F → F♯).
3. Faz o mesmo para Ré Maior: D-E-F♯-G-A-B-C♯-D.

**Padrão das Escalas Maiores**: Sempre T-T-ST-T-T-T-ST (Tom-Tom-Semitom-Tom-Tom-Tom-Semitom). Aplica este padrão a qualquer nota de início e obtens a escala maior correspondente.

**Transpor acordes**: Para transpor uma progressão Am-F-C-G para Lá Maior (transposição ascendente de 1ª Maior):
- Am → Bm
- F → G
- C → D
- G → A
""",
        guitar_focus="""
🎸 **Transposição na Viola — A Capotraste**:
A **capotraste** (ou cejilha) é a ferramenta de transposição por excelência na guitarra:
• Coloca a capo no traste N → toda a guitarra sobe N semitons.
• **Vantagem**: Podes usar as mesmas formas de acordes abertos mas em qualquer tonalidade.

**Exemplo prático**:
• Acorde aberto de Sol (G): [320003]
• Com capo no 2º traste → soa como Lá Maior (A)
• Com capo no 5º traste → soa como Dó Maior (C)

**Tabela de capo rápida**:
| Acorde digitado | Capo 1 | Capo 2 | Capo 3 | Capo 5 |
| --- | --- | --- | --- | --- |
| C | C♯ | D | E♭ | F |
| G | G♯ | A | B♭ | C |
| D | E♭ | E | F | G |
| Em | Fm | F♯m | Gm | Am |

**Exercício**: Aprende a progressão G-Em-C-D. Agora coloca a capo no 2º traste e toca as mesmas formas — a música está agora em Lá Maior!
""",
        interactive_demo="circle_of_fifths",
        title_en="Practical Transposition & Key Signatures",
        subtitle_en="Shifting music between keys and applying the Circle of Fifths",
        summary_en="Learn to transpose melodies and chords to any key, use the Circle of Fifths as a harmonic map, and identify key signatures.",
        content_markdown_en="""
### 1. What is Transposition?
**Transposing** means shifting a whole piece or section to a different key while maintaining interval relationships.

---

### 2. Transposing Step-by-Step
1. Identify source key (e.g. C Major).
2. Identify destination key (e.g. G Major).
3. Calculate interval distance (5th = +7 semitones).
4. Shift every note by +7 semitones.
""",
        piano_focus_en="""
🎹 **Piano Transposition**:
• Apply the **W-W-H-W-W-W-H** pattern starting from any pitch to build its major scale.
""",
        guitar_focus_en="""
🎸 **Guitar Capo Transposition**:
• Placing a capo on fret N raises pitch by N semitones, using open chord shapes in new keys.
""",
    ),
]
