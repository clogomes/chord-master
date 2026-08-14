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

$$\\text{Tom} - \\text{Tom} - \\text{Semitom} - \\text{Tom} - \\text{Tom} - \\text{Tom} - \\text{Semitom} \\quad (T - T - ST - T - T - T - ST)$$

Graus da escala: **1 - 2 - 3 - 4 - 5 - 6 - 7**.
Exemplo em Dó Maior: **C - D - E - F - G - A - B - C**.

---

### 2. As Três Escalas Menores
1. **Menor Natural (Modo Eólio)**: Fórmula: $T - ST - T - T - ST - T - T$ (Graus: $1 - 2 - \\flat 3 - 4 - 5 - \\flat 6 - \\flat 7$).
2. **Menor Harmónica**: Eleva o 7º grau para criar uma sensível a 1 semitom da tónica (Graus: $1 - 2 - \\flat 3 - 4 - 5 - \\flat 6 - 7$). Gera o exótico salto de 1 tom e meio entre o 6º e 7º grau.
3. **Menor Melódica**: Eleva tanto o 6º como o 7º grau na subida para suavizar a condução melódica (Graus: $1 - 2 - \\flat 3 - 4 - 5 - 6 - 7$).

---

### 3. Os 7 Modos Gregos
Os modos são permutações da escala maior iniciando em cada um dos seus 7 graus:

1. **Jónio (I)**: Escala Maior padrão ($1, 2, 3, 4, 5, 6, 7$) — Alegre, estável.
2. **Dórico (ii)**: Menor com 6ª Maior ($1, 2, \\flat 3, 4, 5, 6, \\flat 7$) — Jazz, elegante, nostálgico (*So What* de Miles Davis).
3. **Frígio (iii)**: Menor com 2ª Menor ($1, \\flat 2, \\flat 3, 4, 5, \\flat 6, \\flat 7$) — Flamenco, espanhol, misterioso.
4. **Lídio (IV)**: Maior com 4ª Aumentada ($1, 2, 3, \\sharp 4, 5, 6, 7$) — Místico, etéreo, bandas sonoras de cinema.
5. **Mixolídio (V)**: Maior com 7ª Menor ($1, 2, 3, 4, 5, 6, \\flat 7$) — Blues, Rock clássico, *Sweet Child O' Mine*.
6. **Eólio (vi)**: Menor Natural padrão ($1, 2, \\flat 3, 4, 5, \\flat 6, \\flat 7$) — Melancólico, solene.
7. **Lócrio (vii°)**: Diminuto com 2ª menor e 5ª diminuta ($1, \\flat 2, \\flat 3, 4, \\flat 5, \\flat 6, \\flat 7$) — Tenso, instável.

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
| **Maior** | C, CM | $1 - 3 - 5$ | Terça Maior (4st) + Terça Menor (3st) | C - E - G | Alegre, brilhante, estável |
| **Menor** | Cm, C- | $1 - \\flat 3 - 5$ | Terça Menor (3st) + Terça Maior (4st) | C - E♭ - G | Melancólico, emotivo |
| **Diminuta** | Cdim, C° | $1 - \\flat 3 - \\flat 5$ | Terça Menor (3st) + Terça Menor (3st) | C - E♭ - G♭ | Tenso, sombrio, dramático |
| **Aumentada** | Caug, C+ | $1 - 3 - \\sharp 5$ | Terça Maior (4st) + Terça Maior (4st) | C - E - G♯ | Misterioso, suspenso |

---

### 3. Acordes Suspensos (Sus4 e Sus2)
Substituem a terça pela quarta ou segunda, eliminando a definição de maior/menor:
• **Sus4**: $1 - 4 - 5$ (Ex: C - F - G). Cria forte expectativa de resolver na terça maior.
• **Sus2**: $1 - 2 - 5$ (Ex: C - D - G). Tem sonoridade aberta, suave e moderna.

---

### 4. Inversões de Acordes
A nota mais grave tocada no acorde (o **Baixo**) define o estado de inversão:
• **Posição Fundamental**: A tónica está no baixo ($1 - 3 - 5$). Ex: C no baixo → C/C.
• **1ª Inversão**: A terça está no baixo ($3 - 5 - 1$). Ex: E no baixo → C/E.
• **2ª Inversão**: A quinta está no baixo ($5 - 1 - 3$). Ex: G no baixo → C/G.

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

$$\\mathbf{I} \\text{ (Maior)} \\quad \\mathbf{ii} \\text{ (menor)} \\quad \\mathbf{iii} \\text{ (menor)} \\quad \\mathbf{IV} \\text{ (Maior)} \\quad \\mathbf{V} \\text{ (Maior)} \\quad \\mathbf{vi} \\text{ (menor)} \\quad \\mathbf{vii^\\circ} \\text{ (diminuto)}$$

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

• **Maior com 7ª Maior (maj7 / $\\Delta$)**: $1 - 3 - 5 - 7$ (Graus I e IV). Sonoridade doce, sofisticada, jazz e bossa nova (ex: Cmaj7).
• **Dominante com 7ª (7)**: $1 - 3 - 5 - \\flat 7$ (Grau V). Contém o trítono entre a 3ª e a 7ª menor (ex: G7 resolvendo em C).
• **Menor com 7ª (m7)**: $1 - \\flat 3 - 5 - \\flat 7$ (Graus ii, iii e vi). Sonoridade suave e aveludada (ex: Dm7, Am7).
• **Meio-Diminuto (m7$\\flat$5 / $\\oslash$)**: $1 - \\flat 3 - \\flat 5 - \\flat 7$ (Grau vii°). Tenso e dramático, o grau ii em tonalidades menores (ex: Bm7b5).
• **Diminuto Completo (dim7 / °7)**: $1 - \\flat 3 - \\flat 5 - \\flat\\flat 7$. Acorde simétrico de 4 terças menores consecutivas.

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

• **O Subdominante Menor (iv)**: Usar **Fm** em vez de **F** em tom de Dó Maior (progressão clássica: $I \\to IV \\to iv \\to I$, ex: $C \\to F \\to Fm \\to C$). Soa extremamente emotivo e nostálgico.
• **$\\flat\\text{VI}$ e $\\flat\\text{VII}$**: Usar A♭ e B♭ em tom de Dó Maior (muito comum no Rock e Cinema).

---

### 3. Substituição Tritónica (SubV7)
Todo o acorde dominante com 7ª pode ser substituído por outro dominante localizado a **1 trítono de distância**:
• Em Dó Maior, o dominante normal é **G7** (notas: G - B - D - F).
• O trítono entre as notas **B** e **F** é exatamente o mesmo presente no acorde de **D♭7** (notas: D♭ - F - A♭ - C♭/B).
• Logo, podemos substituir $Dm7 \\to G7 \\to C$ por $Dm7 \\to \\mathbf{D\\flat 7} \\to C$.
• *Vantagem*: O baixo desce cromaticamente por meio-tom ($D \\to D\\flat \\to C$), criando a assinatura harmónica da Bossa Nova e do Jazz contemporâneo!
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
2. **Baixo Alberti**: Arpejo clássico $1 - 5 - 3 - 5$ (muito comum em Mozart e no Pop clássico).
3. **Arpejo Balada 1-5-8-9-10**:
   - Mão Esquerda dedilha a Fundamental (1), Quinta (5), Oitava (8) e Nona (9) criando uma textura orquestral contínua e moderna.
""",
        piano_focus="""
🎹 **Exercício Recomendado**:
1. Toca a progressão $I - vi - IV - V$ em Dó Maior (C - Am - F - G).
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
$$\\mathbf{C} \\text{ (Dó)} \\quad \\mathbf{A} \\text{ (Lá)} \\quad \\mathbf{G} \\text{ (Sol)} \\quad \\mathbf{E} \\text{ (Mi)} \\quad \\mathbf{D} \\text{ (Ré)}$$

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
    ),
]
