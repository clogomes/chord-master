from dataclasses import dataclass, field
from typing import List

@dataclass
class QuizQuestion:
    question: str
    options: List[str]  # exactly 4 options
    correct_index: int  # 0-based index of the correct answer
    explanation: str    # shown after the answer

@dataclass
class ChapterQuiz:
    chapter_id: str     # matches TheoryChapter.id
    questions: List[QuizQuestion]

CHAPTER_QUIZZES: List[ChapterQuiz] = [
    ChapterQuiz(
        chapter_id="chap1_fundamentals",
        questions=[
            QuizQuestion(
                question="Quantas notas existem na escala cromática?",
                options=["7", "8", "12", "24"],
                correct_index=2,
                explanation="A escala cromática tem 12 semitons iguais por oitava — 7 notas naturais e 5 alteradas."
            ),
            QuizQuestion(
                question="O que significa um sustenido (♯)?",
                options=["Baixa 1 semitom", "Eleva 1 semitom", "Cancela o acidente", "Eleva 1 tom"],
                correct_index=1,
                explanation="O sustenido eleva a nota em 1 semitom (meio-tom)."
            ),
            QuizQuestion(
                question="Quantas linhas tem a pauta musical?",
                options=["3", "4", "5", "6"],
                correct_index=2,
                explanation="A pauta (pentagrama) tem 5 linhas e 4 espaços."
            ),
            QuizQuestion(
                question="Na Clave de Sol, que nota fica fixada na 2ª linha?",
                options=["Dó", "Ré", "Sol", "Lá"],
                correct_index=2,
                explanation="A Clave de Sol fixa a nota Sol na 2ª linha da pauta — daí o seu nome."
            ),
            QuizQuestion(
                question="Dó♯ e Ré♭ são a mesma nota acústica?",
                options=["Sim, são enarmónicas", "Não, são diferentes", "Só em piano", "Dependendo da oitava"],
                correct_index=0,
                explanation="Enarmonia: notas com nomes diferentes mas a mesma frequência acústica (mesma tecla no piano)."
            ),
        ]
    ),
    ChapterQuiz(
        chapter_id="chap2_intervals",
        questions=[
            QuizQuestion(
                question="O que é um intervalo musical?",
                options=["A distância de altura entre duas notas", "A duração de uma nota", "O volume do som", "Uma pausa longa"],
                correct_index=0,
                explanation="Um intervalo é a distância de altura (frequência) entre duas notas musicais."
            ),
            QuizQuestion(
                question="Quantos semitons tem uma Quinta Justa?",
                options=["5", "6", "7", "8"],
                correct_index=2,
                explanation="Uma Quinta Justa corresponde a 7 semitons."
            ),
            QuizQuestion(
                question="Qual destes intervalos é considerado uma dissonância extrema?",
                options=["Oitava Justa", "Terça Maior", "Trítono", "Quarta Justa"],
                correct_index=2,
                explanation="O Trítono (4ª aumentada ou 5ª diminuta, 6 semitons) é conhecido como a maior dissonância da escala."
            ),
            QuizQuestion(
                question="Na guitarra, a que distância corresponde 1 tom inteiro?",
                options=["1 corda de diferença", "1 traste", "2 trastes", "3 trastes"],
                correct_index=2,
                explanation="Um semitom equivale a 1 traste, logo 1 tom inteiro corresponde a 2 trastes na mesma corda."
            ),
            QuizQuestion(
                question="Se invertermos uma Terça Maior, o que obtemos?",
                options=["Sexta Maior", "Terça Menor", "Sexta Menor", "Quinta Justa"],
                correct_index=2,
                explanation="Ao inverter, a soma dá sempre 9 (3+6=9) e o que é Maior passa a Menor. Logo, torna-se uma Sexta Menor."
            ),
        ]
    ),
    ChapterQuiz(
        chapter_id="chap3_scales_modes",
        questions=[
            QuizQuestion(
                question="Qual a fórmula da Escala Maior Natural em tons (T) e semitons (ST)?",
                options=["T-T-ST-T-T-T-ST", "T-ST-T-T-ST-T-T", "ST-T-T-T-T-ST-T", "T-T-T-ST-T-T-ST"],
                correct_index=0,
                explanation="A estrutura da Escala Maior é composta por dois tetracordes separados por um tom: T-T-ST e T-T-T-ST."
            ),
            QuizQuestion(
                question="Quantas notas diferentes compõem a Escala Maior?",
                options=["5", "7", "8", "12"],
                correct_index=1,
                explanation="A Escala Maior é diatónica, sendo formada por 7 notas diferentes (a 8ª é a repetição da tónica)."
            ),
            QuizQuestion(
                question="O Modo Dórico é semelhante à escala menor natural, mas tem uma alteração. Qual é?",
                options=["2ª Maior", "6ª Maior", "7ª Maior", "4ª Aumentada"],
                correct_index=1,
                explanation="O Modo Dórico (modo do 2º grau) caracteriza-se por ter a 3ª menor mas manter a 6ª Maior."
            ),
            QuizQuestion(
                question="No Círculo de Quintas (sentido horário), o que acontece à armação de clave de cada nova tonalidade?",
                options=["Adiciona 1 sustenido", "Adiciona 1 bemol", "Cancela os acidentes", "Fica igual"],
                correct_index=0,
                explanation="Ao avançar por quintas justas, acrescenta-se sempre um sustenido à armação de clave (C=0, G=1#, D=2#, etc)."
            ),
            QuizQuestion(
                question="Qual destas escalas ou modos tem uma sonoridade típica do blues e rock clássico?",
                options=["Modo Frígio", "Modo Lócrio", "Modo Jónio", "Modo Mixolídio"],
                correct_index=3,
                explanation="O Modo Mixolídio (Maior com 7ª Menor) é a base de muitos riffs de rock e blues clássico."
            ),
        ]
    ),
    ChapterQuiz(
        chapter_id="chap4_chords_triads",
        questions=[
            QuizQuestion(
                question="Uma tríade é formada por três notas sobrepostas em intervalos de:",
                options=["Segundas", "Terças", "Quartas", "Quintas"],
                correct_index=1,
                explanation="As tríades formam-se empilhando terças (ex: 1, 3 e 5)."
            ),
            QuizQuestion(
                question="Uma Tríade Maior é formada por quais intervalos consecutivos?",
                options=["Terça Maior + Terça Maior", "Terça Menor + Terça Menor", "Terça Menor + Terça Maior", "Terça Maior + Terça Menor"],
                correct_index=3,
                explanation="Uma tríade maior empilha uma Terça Maior (4 semitons) seguida de uma Terça Menor (3 semitons) em relação a essa."
            ),
            QuizQuestion(
                question="O que caracteriza um acorde Sus4?",
                options=["A terça é substituída pela quarta", "Tem quatro notas", "A quinta é omitida", "Tem uma quarta aumentada"],
                correct_index=0,
                explanation="No acorde Suspensos (Sus4), a quarta justa substitui a terça, eliminando o caráter de maior ou menor."
            ),
            QuizQuestion(
                question="Na 1ª inversão de um acorde de Dó Maior (C/E), qual nota fica no baixo?",
                options=["Dó", "Mi", "Sol", "Fá"],
                correct_index=1,
                explanation="A 1ª inversão coloca a terça (Mi) no baixo."
            ),
            QuizQuestion(
                question="Qual é a principal vantagem de usar inversões de acordes?",
                options=["Aumentar o volume", "Permitir um voice leading mais suave", "Mudar a tonalidade", "Facilitar a leitura da clave"],
                correct_index=1,
                explanation="Inversões permitem mover as vozes (em especial o baixo) de forma próxima e elegante, evitando grandes saltos."
            ),
        ]
    ),
    ChapterQuiz(
        chapter_id="chap5_harmonic_field_tetrads",
        questions=[
            QuizQuestion(
                question="Num Campo Harmónico Maior, qual é o tipo de acorde do grau ii?",
                options=["Maior", "Menor", "Diminuto", "Aumentado"],
                correct_index=1,
                explanation="O grau ii num Campo Harmónico Maior é sempre menor (ex: em Dó Maior, o grau ii é Ré menor)."
            ),
            QuizQuestion(
                question="Qual função harmónica transmite a máxima tensão e urgência de resolução?",
                options=["Tónica", "Subdominante", "Dominante", "Relativa"],
                correct_index=2,
                explanation="A Função Dominante (graus V e vii°) pede resolução fortemente para a Tónica."
            ),
            QuizQuestion(
                question="Uma tétrade adiciona uma quarta nota à tríade básica. A que distância da quinta fica essa nota?",
                options=["Uma segunda", "Uma terça", "Uma quarta", "Uma oitava"],
                correct_index=1,
                explanation="As tétrades continuam o empilhamento original de tríades, adicionando uma sétima (que está à distância de uma terça da quinta)."
            ),
            QuizQuestion(
                question="Que acorde é formado pelos graus 1 - ♭3 - 5 - ♭7?",
                options=["Maior com 7ª Maior (maj7)", "Menor com 7ª (m7)", "Dominante com 7ª (7)", "Meio-Diminuto (m7b5)"],
                correct_index=1,
                explanation="O acorde Menor com 7ª (m7) possui a terça menor (♭3), a quinta justa e a sétima menor (♭7)."
            ),
            QuizQuestion(
                question="A progressão ii - V - I é especialmente comum em que estilos musicais?",
                options=["Heavy Metal", "Jazz e Bossa Nova", "Música Barroca", "Punk Rock"],
                correct_index=1,
                explanation="O ii - V - I é a base estrutural de inúmeros temas de Jazz, Bossa Nova e Pop."
            ),
        ]
    ),
    ChapterQuiz(
        chapter_id="chap6_advanced_harmony",
        questions=[
            QuizQuestion(
                question="O que é uma Dominante Secundária?",
                options=["O acorde V de qualquer grau que não seja o I", "O segundo acorde de uma música", "Um acorde menor com 7ª", "Uma dominante sem trítono"],
                correct_index=0,
                explanation="É um acorde maior com 7ª que atua temporariamente como dominante (V) para resolver noutro acorde diatónico."
            ),
            QuizQuestion(
                question="O que é o Empréstimo Modal (ou Intercâmbio Modal)?",
                options=["Mudar de instrumento", "Usar acordes da escala homónima menor num tom maior", "Tocar acordes mais graves", "Alterar a afinação"],
                correct_index=1,
                explanation="Consiste em \"pedir emprestados\" acordes da escala paralela (ex: usar um Fm numa progressão em Dó Maior)."
            ),
            QuizQuestion(
                question="Na substituição tritónica (SubV7), o acorde G7 (em Dó Maior) pode ser substituído por qual acorde?",
                options=["Dm7", "Cmaj7", "D♭7", "F♯7"],
                correct_index=2,
                explanation="O G7 pode ser substituído por D♭7, que partilha o mesmo trítono (B e F) mas tem o baixo a um semitom do acorde de resolução (C)."
            ),
            QuizQuestion(
                question="Qual é o efeito no baixo ao usar uma substituição tritónica do grau V para o I?",
                options=["O baixo salta uma quinta", "O baixo desce cromaticamente por meio-tom", "O baixo sobe um tom", "O baixo mantém-se igual"],
                correct_index=1,
                explanation="A substituição tritónica permite uma descida suave em semitom do baixo até à tónica (ex: D♭ desce para C)."
            ),
            QuizQuestion(
                question="Que acorde clássico de empréstimo modal tem uma forte carga emotiva/nostálgica quando resolve na tónica maior?",
                options=["O V Maior", "O iv menor", "O ii menor", "O vi menor"],
                correct_index=1,
                explanation="O uso do acorde subdominante menor (iv menor, como Fm em Dó Maior) cria uma sensação agridoce e muito nostálgica."
            ),
        ]
    ),
    ChapterQuiz(
        chapter_id="chap7_piano_guide",
        questions=[
            QuizQuestion(
                question="Como são numerados os dedos no piano para cada mão?",
                options=["1 a 5 da esquerda para a direita", "1 (mindinho) a 5 (polegar)", "1 (polegar) a 5 (mindinho)", "A, B, C, D, E"],
                correct_index=2,
                explanation="Em ambas as mãos, o polegar é sempre o dedo 1 e o mindinho o dedo 5."
            ),
            QuizQuestion(
                question="Qual é o padrão de acompanhamento conhecido como Baixo Alberti?",
                options=["Acordes em bloco no 1º tempo", "Arpejo sequencial 1 - 5 - 3 - 5", "Tocar todas as teclas juntas", "Alternar entre as duas mãos a cada nota"],
                correct_index=1,
                explanation="O Baixo Alberti é um acompanhamento clássico que arpeja as notas da tríade na ordem Fundamental, Quinta, Terça e Quinta (1-5-3-5)."
            ),
            QuizQuestion(
                question="Qual é a postura recomendada para o pulso ao tocar piano?",
                options=["Afundado abaixo das teclas", "Levantado o mais alto possível", "Alinhado e flexível com o antebraço", "Rígido e imóvel"],
                correct_index=2,
                explanation="O pulso deve estar alinhado com o antebraço e flexível como um amortecedor suave."
            ),
            QuizQuestion(
                question="Num acorde Cmaj7 (C-E-G-B) em posição fundamental na mão direita, qual é a dedilhação recomendada?",
                options=["1-2-3-5", "1-3-4-5", "1-2-4-5", "2-3-4-5"],
                correct_index=0,
                explanation="Para cobrir as quatro notas mantendo a mão relaxada, a dedilhação habitual é 1-2-3-5, deixando o dedo 4 repousar livremente."
            ),
            QuizQuestion(
                question="Para destacar a melodia principal ao tocar acordes no piano, onde deve recair mais 'peso'?",
                options=["No polegar", "Na mão esquerda", "No dedo 5 (mindinho)", "No pedal"],
                correct_index=2,
                explanation="Para que a nota mais aguda (a melodia) sobressaia dos acordes, deve-se aplicar ligeiramente mais peso no lado do dedo mindinho da mão direita."
            ),
        ]
    ),
    ChapterQuiz(
        chapter_id="chap8_guitar_guide",
        questions=[
            QuizQuestion(
                question="No sistema CAGED, quantas formas fundamentais de acordes abertos existem?",
                options=["3", "5", "7", "12"],
                correct_index=1,
                explanation="O CAGED baseia-se em 5 formas de acordes abertos: Dó (C), Lá (A), Sol (G), Mi (E) e Ré (D)."
            ),
            QuizQuestion(
                question="O que permite transpor as formas do CAGED ao longo de todo o braço da guitarra?",
                options=["O uso do polegar atrás do braço", "Mudar de afinação", "Tocar apenas cordas soltas", "O uso do dedo indicador como pestana móvel"],
                correct_index=3,
                explanation="O dedo indicador atua como uma 'pestana' (capotraste humano), permitindo deslocar os acordes abertos pelo braço."
            ),
            QuizQuestion(
                question="Para fazer uma pestana sem dor, que parte do dedo indicador deve pressionar as cordas?",
                options=["A almofada macia central", "A ponta do dedo", "A lateral ligeiramente externa e ossuda", "A parte de trás do dedo"],
                correct_index=2,
                explanation="A lateral do dedo é mais firme e óssea, fornecendo pressão uniforme nas cordas com menos fadiga."
            ),
            QuizQuestion(
                question="Na mão direita, num dedilhado padrão (P.I.M.A.), que dedo é responsável pelas cordas graves (6ª, 5ª, 4ª)?",
                options=["Indicador (I)", "Médio (M)", "Anelar (A)", "Polegar (P)"],
                correct_index=3,
                explanation="O Polegar (P) encarrega-se do baixo e das cordas graves, enquanto o I, M e A dedilham as cordas mais agudas."
            ),
            QuizQuestion(
                question="Qual é a finalidade do exercício 'Spider Walk 1-2-3-4' na guitarra?",
                options=["Um dedilhado com a mão direita", "Tocar trastes consecutivos para ganhar força e independência na mão esquerda", "Deslizar a pestana rapidamente", "Tocar as 6 cordas ao mesmo tempo"],
                correct_index=1,
                explanation="É um exercício clássico de coordenação e destreza onde cada dedo pressiona um traste de cada vez, corda por corda."
            ),
        ]
    ),
    ChapterQuiz(
        chapter_id="chap9_rhythm",
        questions=[
            QuizQuestion(
                question="Como é medido o andamento (a velocidade da batida) musical?",
                options=["Em Decibéis (dB)", "Em Hertz (Hz)", "Em BPM (Batidas por Minuto)", "Em Compassos"],
                correct_index=2,
                explanation="O BPM (Beats Per Minute) define a velocidade constante do pulso musical."
            ),
            QuizQuestion(
                question="Num compasso de 4/4, qual figura rítmica vale 1 batida (1 tempo)?",
                options=["Semibreve", "Mínima", "Semínima", "Colcheia"],
                correct_index=2,
                explanation="A Semínima (figura 4) é a unidade de tempo do compasso 4/4, durando 1 batida."
            ),
            QuizQuestion(
                question="O que faz um 'ponto de aumentação' ao lado de uma figura rítmica?",
                options=["Dobra o seu valor", "Corta o valor a meio", "Acrescenta metade do seu valor original", "Anula a nota"],
                correct_index=2,
                explanation="O ponto prolonga a nota em mais metade do seu próprio valor de duração."
            ),
            QuizQuestion(
                question="Quantas batidas vale uma Semibreve num compasso 4/4?",
                options=["1", "2", "3", "4"],
                correct_index=3,
                explanation="A Semibreve preenche todo o compasso de 4/4, durando as 4 batidas."
            ),
            QuizQuestion(
                question="Como se chama o efeito rítmico quando o acento cai num tempo fraco ou contratempo?",
                options=["Legato", "Síncopa", "Crescendo", "Staccato"],
                correct_index=1,
                explanation="A síncopa (ou sincopado) desloca o acento rítmico forte esperado, criando fluidez e tensão."
            ),
        ]
    ),
    ChapterQuiz(
        chapter_id="chap10_form",
        questions=[
            QuizQuestion(
                question="O que descreve a Forma Musical?",
                options=["A disposição dos músicos no palco", "O volume da peça ao longo do tempo", "A organização temporal de secções, temas e contrastes", "O formato acústico do instrumento"],
                correct_index=2,
                explanation="A forma musical é a estrutura ou arquitetura de como a música se divide em partes (A, B, refrões, etc)."
            ),
            QuizQuestion(
                question="Uma forma Ternária clássica é habitualmente representada por que letras?",
                options=["AB", "AABB", "ABC", "ABA"],
                correct_index=3,
                explanation="Na forma ABA, apresenta-se um tema A, um contraste B, e regressa-se ao tema inicial A."
            ),
            QuizQuestion(
                question="Na Forma Sonata, em que secção se fragmenta e transforma os temas, criando tensão máxima?",
                options=["Exposição", "Desenvolvimento", "Reexposição", "Coda"],
                correct_index=1,
                explanation="O Desenvolvimento é a secção central da sonata onde os temas viajam por tonalidades instáveis."
            ),
            QuizQuestion(
                question="Numa estrutura de canção Pop/Rock, que secção costuma ser o clímax emocional e melódico?",
                options=["O Verso", "A Introdução", "O Refrão", "O Outro"],
                correct_index=2,
                explanation="O Refrão é geralmente o clímax que concentra a mensagem principal e a energia da canção."
            ),
            QuizQuestion(
                question="A técnica de 'repetir um motivo a alturas diferentes (ex: subindo grau a grau)' chama-se:",
                options=["Sequência", "Inversão", "Aumentação", "Diminuição"],
                correct_index=0,
                explanation="Uma progressão sequencial consiste em repetir a mesma figura melódica deslocando-a paralelamente."
            ),
        ]
    ),
    ChapterQuiz(
        chapter_id="chap11_dynamics",
        questions=[
            QuizQuestion(
                question="O que indica o símbolo dinâmico 'ff' numa partitura?",
                options=["Muito suave (Pianissimo)", "Fim da peça (Fine)", "Rápido (Presto)", "Muito forte (Fortissimo)"],
                correct_index=3,
                explanation="O 'ff' (Fortissimo) instrui a tocar a peça muito forte."
            ),
            QuizQuestion(
                question="Como se chama o aumento gradual de volume numa frase musical?",
                options=["Accelerando", "Crescendo", "Decrescendo", "Legato"],
                correct_index=1,
                explanation="Crescendo significa aumentar gradualmente a intensidade/volume do som."
            ),
            QuizQuestion(
                question="O que significa a indicação para tocar em 'Staccato'?",
                options=["Tocar notas curtas e separadas", "Tocar as notas perfeitamente ligadas", "Tocar muito devagar", "Tocar com muita força"],
                correct_index=0,
                explanation="O staccato é a articulação que encurta a nota, tornando-a destacada e separada da próxima."
            ),
            QuizQuestion(
                question="O que é o 'Rubato' na expressão musical?",
                options=["Uma pausa longa obrigatória", "Tocar perfeitamente no tempo mecânico", "Liberdade expressiva no tempo (atrasar ou acelerar levemente)", "Um tipo de acorde invertido"],
                correct_index=2,
                explanation="O rubato permite ao intérprete dar elasticidade ao tempo, acelerando e abrandando para maior emoção."
            ),
            QuizQuestion(
                question="Qual é a melhor prática para o uso do Pedal de Sustain no piano?",
                options=["Manter sempre pressionado", "Trocar o pedal a cada mudança harmónica para não misturar os acordes", "Nunca usar o pedal em peças clássicas", "Trocar a cada batida rigorosa do metrónomo"],
                correct_index=1,
                explanation="Levantar e pressionar novamente o pedal (troca de pedal) a cada mudança de acorde evita que as notas embolem e criem ruído harmónico."
            ),
        ]
    ),
    ChapterQuiz(
        chapter_id="chap12_transposition",
        questions=[
            QuizQuestion(
                question="O que significa 'Transpor' uma peça musical?",
                options=["Mudar o ritmo principal da música", "Mudar de instrumento durante a peça", "Mover a música para uma tonalidade diferente mantendo as relações intervalares", "Tocar de trás para a frente"],
                correct_index=2,
                explanation="Transpor é executar a mesma peça noutro tom (mais alto ou mais baixo)."
            ),
            QuizQuestion(
                question="Seguindo o Círculo de Quintas, se avançares uma casa a partir de Dó Maior (adicionando 1 sustenido), qual é a nova tonalidade?",
                options=["Fá Maior", "Sol Maior", "Ré Maior", "Lá Maior"],
                correct_index=1,
                explanation="Dó Maior não tem acidentes. A quinta justa acima de Dó é Sol, e Sol Maior tem exatamente 1 sustenido."
            ),
            QuizQuestion(
                question="Se transpores uma melodia de Dó Maior para Sol Maior, qual é o intervalo exato da transposição ascendente?",
                options=["Uma terça maior", "Uma quarta justa", "Uma quinta justa", "Uma oitava"],
                correct_index=2,
                explanation="De C para G ascendente, o intervalo é de uma Quinta Justa (7 semitons)."
            ),
            QuizQuestion(
                question="Quantos acidentes tem a armação de clave da tonalidade de Si♭ Maior?",
                options=["1 bemol", "2 bemóis", "3 bemóis", "1 sustenido"],
                correct_index=1,
                explanation="Si♭ Maior tem 2 bemóis na sua armação de clave (Si♭ e Mi♭)."
            ),
            QuizQuestion(
                question="Na guitarra, qual é a ferramenta rápida para transpor a música para um tom mais alto usando exatamente os mesmos acordes abertos?",
                options=["Mudar a afinação de cada corda", "Usar uma Capotraste (cejilha)", "Tocar apenas acordes em pestana", "Diminuir a grossura das cordas"],
                correct_index=1,
                explanation="A Capotraste age como uma 'pestana móvel', subindo a afinação geral e permitindo usar as mesmas formas CAGED que se usaria no início do braço."
            ),
        ]
    ),
    ChapterQuiz(
        chapter_id="chap13_jazz_harmony",
        questions=[
            QuizQuestion(
                question="Qual é a progressão de acordes mais célebre no Jazz e Bossa Nova?",
                options=["I - IV - V", "ii - V - I", "I - vi - IV - V", "iii - vi - ii - V"],
                correct_index=1,
                explanation="A progressão ii - V - I é o bloco harmónico mais usado no Jazz (ex: Dm7 - G7 - Cmaj7)."
            ),
            QuizQuestion(
                question="Quantos compassos tem a estrutura clássica do Blues?",
                options=["8", "12", "16", "32"],
                correct_index=1,
                explanation="O Blues tradicional baseia-se numa estrutura formal rígida de 12 compassos."
            ),
            QuizQuestion(
                question="Segundo a teoria acorde-escala (chord-scale theory), qual o modo associado ao grau ii (m7)?",
                options=["Jónio", "Dórico", "Frígio", "Lídio"],
                correct_index=1,
                explanation="O acorde de grau ii (m7) associa-se ao Modo Dórico."
            ),
            QuizQuestion(
                question="O que é o 'Turnaround' nos compassos 11-12 do Blues?",
                options=["Uma pausa completa", "A repetição da melodia", "A progressão final que conduz o regresso ao início (I7 - V7)", "Um solo de bateria"],
                correct_index=2,
                explanation="O turnaround prepara a repetição da forma de 12 compassos conduzindo de volta à tónica."
            ),
            QuizQuestion(
                question="Em Rootless Voicings no piano, o que se omite na mão direita?",
                options=["A terça", "A sétima", "A fundamental", "A quinta"],
                correct_index=2,
                explanation="No piano jazz, a fundamental é deixada para o baixo (mão esquerda), libertando a mão direita para tocar guide tones e extensões."
            ),
        ]
    ),
    ChapterQuiz(
        chapter_id="chap14_improvisation",
        questions=[
            QuizQuestion(
                question="O que são 'Guide Tones' numa harmonia de acordes?",
                options=["A fundamental e a quinta", "A 3ª e a 7ª de cada acorde", "As notas mais agudas da escala", "As notas tocadas em staccato"],
                correct_index=1,
                explanation="A 3ª e a 7ª definem o carácter do acorde (maior, menor, dominante) e são os alvos melódicos principais."
            ),
            QuizQuestion(
                question="Em que notas do acorde deve idealmente aterrar uma frase de improvisação nos tempos fortes?",
                options=["Nas notas de aproximação cromática", "Nas notas alvo (Target Notes / 3ª e 7ª)", "Em pausas", "Apenas na fundamental"],
                correct_index=1,
                explanation="Aterrar nas notas alvo nos tempos fortes dá clareza harmónica à improvisação."
            ),
            QuizQuestion(
                question="Qual a escala mais utilizada para solos de Blues e Rock?",
                options=["Escala Maior", "Escala Pentatónica Menor (com a Blue Note)", "Escala Cromática", "Modo Lócrio"],
                correct_index=1,
                explanation="A Pentatónica Menor com a Blue Note (trítono) é o pilar da improvisação de Blues e Rock."
            ),
            QuizQuestion(
                question="O que é uma aproximação cromática?",
                options=["Tocar desafinado", "Tocar um semitom acima ou abaixo da nota alvo antes de a atingir", "Saltar uma oitava", "Acelerar o tempo"],
                correct_index=1,
                explanation="A aproximação cromática cria tensão momentânea que resolve na nota do acorde."
            ),
            QuizQuestion(
                question="Como se liga uma linha melódica entre acordes com fluidez?",
                options=["Saltando grandes oitavas", "Movendo-se por passos de semitom/tom em direção aos Guide Tones", "Parando de tocar entre acordes", "Repetindo sempre a mesma nota"],
                correct_index=1,
                explanation="Conduzir frases por graus conjuntos em direção aos Guide Tones cria linhas melódicas contínuas."
            ),
        ]
    ),
    ChapterQuiz(
        chapter_id="chap15_counterpoint",
        questions=[
            QuizQuestion(
                question="Qual o tipo de movimento entre vozes considerado mais independente e elegante?",
                options=["Movimento Paralelo", "Movimento Contrário (uma voz sobe e a outra desce)", "Movimento Direto", "Movimento Nulo"],
                correct_index=1,
                explanation="No movimento contrário, a independência contrapontística das vozes é máxima."
            ),
            QuizQuestion(
                question="Na condução de vozes tradicional, que intervalo paralelo deve ser rigorosamente evitado?",
                options=["Terças paralelas", "Sextas paralelas", "Quintas e Oitavas paralelas", "Quartas paralelas"],
                correct_index=2,
                explanation="Quintas e oitavas paralelas destroem a individualidade melódica das duas vozes."
            ),
            QuizQuestion(
                question="O que caracteriza o Movimento Oblíquo entre duas vozes?",
                options=["Ambas as vozes sobem", "Uma voz permanece fixa enquanto a outra se move", "Ambas descem", "Nenhuma se move"],
                correct_index=1,
                explanation="No movimento oblíquo, uma linha mantém-se estática enquanto a outra progride."
            ),
            QuizQuestion(
                question="Qual o princípio de 'Economia de Movimento' na condução de vozes?",
                options=["Mover cada voz pelo menor caminho possível (passos de semitom ou tom)", "Dar grandes saltos de oitava", "Usar só uma mão", "Tocar o mais rápido possível"],
                correct_index=0,
                explanation="A economia de movimento garante uma transição vocal fluida e natural."
            ),
            QuizQuestion(
                question="Em peças a duas vozes na viola (como as de Bach), qual o papel do polegar direito?",
                options=["Tocar a melodia aguda", "Manter a linha de baixo independente", "Abafar as cordas", "Tocar em staccato"],
                correct_index=1,
                explanation="O polegar conduz a linha de baixo contrapontística."
            ),
        ]
    ),
    ChapterQuiz(
        chapter_id="chap16_deliberate_practice",
        questions=[
            QuizQuestion(
                question="O que caracteriza a Prática Deliberada por oposição a tocar apenas a peça?",
                options=["Tocar sem metrónomo", "Estudo focado na correção consciente de falhas específicas", "Tocar 5 horas seguidas", "Tocar o mais rápido possível"],
                correct_index=1,
                explanation="A Prática Deliberada isola e corrige fraquezas de forma consciente e focada."
            ),
            QuizQuestion(
                question="A que velocidade de rampa se deve começar a praticar uma passagem complexa?",
                options=["A 120% do BPM alvo", "A 70% do BPM alvo (velocidade lenta e precisa)", "Sem metrónomo", "A 100% do BPM alvo"],
                correct_index=1,
                explanation="Estudar a 70% do BPM consolida a precisão neuromuscular antes de aumentar a velocidade."
            ),
            QuizQuestion(
                question="O que significa a técnica de 'Chunking' no estudo musical?",
                options=["Repetir a peça do início ao fim", "Isolar pequenos blocos de 1 a 2 compassos onde ocorre o erro", "Tocar com os olhos fechados", "Mudar de instrumento"],
                correct_index=1,
                explanation="Chunking divide o problema em segmentos pequenos e controláveis."
            ),
            QuizQuestion(
                question="Para a retenção de memória muscular a longo prazo, qual o formato de estudo mais eficaz?",
                options=["3 horas num único dia do fim de semana", "Sessões diárias curtas e focadas de 20 a 30 minutos (repetição espaçada)", "Estudar apenas antes do concerto", "Não praticar com frequência"],
                correct_index=1,
                explanation="A repetição espaçada diária consolida a memória a longo prazo muito melhor do que maratonas esporádicas."
            ),
            QuizQuestion(
                question="Qual o procedimento correto na Rampa de Tempo se cometeres um erro ao subir 5 BPM?",
                options=["Aumentar mais 10 BPM", "Reduzir 2 a 5 BPM e consolidar a precisão sem erros", "Desistir da passagem", "Ignorar o erro e continuar"],
                correct_index=1,
                explanation="Regredir ligeiramente o tempo permite fixar o padrão correto sem reforçar o erro."
            ),
        ]
    ),
]
