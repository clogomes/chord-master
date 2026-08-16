from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class QuizQuestion:
    question: str
    options: List[str]  # exactly 4 options
    correct_index: int  # 0-based index of the correct answer
    explanation: str    # shown after the answer
    question_en: Optional[str] = None
    options_en: List[str] = field(default_factory=list)
    explanation_en: Optional[str] = None

    def get_question(self, lang="pt") -> str:
        if lang == "en" and self.question_en:
            return self.question_en
        return self.question

    def get_options(self, lang="pt") -> List[str]:
        if lang == "en" and self.options_en:
            return self.options_en
        return self.options

    def get_explanation(self, lang="pt") -> str:
        if lang == "en" and self.explanation_en:
            return self.explanation_en
        return self.explanation

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
                explanation="A escala cromática tem 12 semitons iguais por oitava — 7 notas naturais e 5 alteradas.",
                question_en="How many notes are there in the chromatic scale?",
                options_en=["7", "8", "12", "24"],
                explanation_en="The chromatic scale has 12 equal semitones per octave — 7 natural notes and 5 altered notes."
            ),
            QuizQuestion(
                question="O que significa um sustenido (♯)?",
                options=["Baixa 1 semitom", "Eleva 1 semitom", "Cancela o acidente", "Eleva 1 tom"],
                correct_index=1,
                explanation="O sustenido eleva a nota em 1 semitom (meio-tom).",
                question_en="What does a sharp (♯) mean?",
                options_en=["Lowers by 1 semitone", "Raises by 1 semitone", "Cancels the accidental", "Raises by 1 whole step"],
                explanation_en="A sharp raises the note by 1 semitone (half step)."
            ),
            QuizQuestion(
                question="Quantas linhas tem a pauta musical?",
                options=["3", "4", "5", "6"],
                correct_index=2,
                explanation="A pauta (pentagrama) tem 5 linhas e 4 espaços.",
                question_en="How many lines does a musical staff have?",
                options_en=["3", "4", "5", "6"],
                explanation_en="The staff (pentagram) has 5 lines and 4 spaces."
            ),
            QuizQuestion(
                question="Na Clave de Sol, que nota fica fixada na 2ª linha?",
                options=["Dó", "Ré", "Sol", "Lá"],
                correct_index=2,
                explanation="A Clave de Sol fixa a nota Sol na 2ª linha da pauta — daí o seu nome.",
                question_en="In the Treble Clef, which note is fixed on the 2nd line?",
                options_en=["C", "D", "G", "A"],
                explanation_en="The Treble Clef fixes the note G on the 2nd line of the staff — hence its name."
            ),
            QuizQuestion(
                question="Dó♯ e Ré♭ são a mesma nota acústica?",
                options=["Sim, são enarmónicas", "Não, são diferentes", "Só em piano", "Dependendo da oitava"],
                correct_index=0,
                explanation="Enarmonia: notas com nomes diferentes mas a mesma frequência acústica (mesma tecla no piano).",
                question_en="Are C♯ and D♭ the same acoustic note?",
                options_en=["Yes, they are enharmonic", "No, they are different", "Only on piano", "Depending on the octave"],
                explanation_en="Enharmonic: notes with different names but the same acoustic frequency (same key on the piano)."
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
                explanation="Um intervalo é a distância de altura (frequência) entre duas notas musicais.",
                question_en="What is a musical interval?",
                options_en=["The pitch distance between two notes", "The duration of a note", "The volume of the sound", "A long pause"],
                explanation_en="An interval is the distance in pitch (frequency) between two musical notes."
            ),
            QuizQuestion(
                question="Quantos semitons tem uma Quinta Justa?",
                options=["5", "6", "7", "8"],
                correct_index=2,
                explanation="Uma Quinta Justa corresponde a 7 semitons.",
                question_en="How many semitones does a Perfect Fifth have?",
                options_en=["5", "6", "7", "8"],
                explanation_en="A Perfect Fifth corresponds to 7 semitones."
            ),
            QuizQuestion(
                question="Qual destes intervalos é considerado uma dissonância extrema?",
                options=["Oitava Justa", "Terça Maior", "Trítono", "Quarta Justa"],
                correct_index=2,
                explanation="O Trítono (4ª aumentada ou 5ª diminuta, 6 semitons) é conhecido como a maior dissonância da escala.",
                question_en="Which of these intervals is considered an extreme dissonance?",
                options_en=["Perfect Octave", "Major Third", "Tritone", "Perfect Fourth"],
                explanation_en="The Tritone (augmented 4th or diminished 5th, 6 semitones) is known as the greatest dissonance in the scale."
            ),
            QuizQuestion(
                question="Na guitarra, a que distância corresponde 1 tom inteiro?",
                options=["1 corda de diferença", "1 traste", "2 trastes", "3 trastes"],
                correct_index=2,
                explanation="Um semitom equivale a 1 traste, logo 1 tom inteiro corresponde a 2 trastes na mesma corda.",
                question_en="On the guitar, what distance corresponds to 1 whole step?",
                options_en=["1 string difference", "1 fret", "2 frets", "3 frets"],
                explanation_en="A semitone equals 1 fret, so 1 whole step corresponds to 2 frets on the same string."
            ),
            QuizQuestion(
                question="Se invertermos uma Terça Maior, o que obtemos?",
                options=["Sexta Maior", "Terça Menor", "Sexta Menor", "Quinta Justa"],
                correct_index=2,
                explanation="Ao inverter, a soma dá sempre 9 (3+6=9) e o que é Maior passa a Menor. Logo, torna-se uma Sexta Menor.",
                question_en="If we invert a Major Third, what do we get?",
                options_en=["Major Sixth", "Minor Third", "Minor Sixth", "Perfect Fifth"],
                explanation_en="When inverting, the sum always equals 9 (3+6=9) and Major becomes Minor. Therefore, it becomes a Minor Sixth."
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
                explanation="A estrutura da Escala Maior é composta por dois tetracordes iguais (T-T-ST) unidos por um tom central: (T-T-ST) + T + (T-T-ST).",
                question_en="What is the formula of the Natural Major Scale in whole steps (W) and half steps (H)?",
                options_en=["W-W-H-W-W-W-H", "W-H-W-W-H-W-W", "H-W-W-W-W-H-W", "W-W-W-H-W-W-H"],
                explanation_en="The Major Scale is composed of two identical tetrachords (W-W-H) joined by a central whole step: (W-W-H) + W + (W-W-H)."
            ),
            QuizQuestion(
                question="Quantas notas diferentes compõem a Escala Maior?",
                options=["5", "7", "8", "12"],
                correct_index=1,
                explanation="A Escala Maior é diatónica, sendo formada por 7 notas diferentes (a 8ª é a repetição da tónica).",
                question_en="How many different notes make up the Major Scale?",
                options_en=["5", "7", "8", "12"],
                explanation_en="The Major Scale is diatonic, consisting of 7 different notes (the 8th is the repetition of the root)."
            ),
            QuizQuestion(
                question="O Modo Dórico é semelhante à escala menor natural, mas tem uma alteração. Qual é?",
                options=["2ª Maior", "6ª Maior", "7ª Maior", "4ª Aumentada"],
                correct_index=1,
                explanation="O Modo Dórico (modo do 2º grau) caracteriza-se por ter a 3ª menor mas manter a 6ª Maior.",
                question_en="The Dorian Mode is similar to the natural minor scale, but has one alteration. What is it?",
                options_en=["Major 2nd", "Major 6th", "Major 7th", "Augmented 4th"],
                explanation_en="The Dorian Mode (2nd degree mode) is characterized by having a minor 3rd but maintaining a Major 6th."
            ),
            QuizQuestion(
                question="No Círculo de Quintas (sentido horário), o que acontece à armação de clave de cada nova tonalidade?",
                options=["Adiciona 1 sustenido", "Adiciona 1 bemol", "Cancela os acidentes", "Fica igual"],
                correct_index=0,
                explanation="Ao avançar por quintas justas, acrescenta-se sempre um sustenido à armação de clave (C=0, G=1#, D=2#, etc).",
                question_en="In the Circle of Fifths (clockwise), what happens to the key signature of each new key?",
                options_en=["Adds 1 sharp", "Adds 1 flat", "Cancels the accidentals", "Stays the same"],
                explanation_en="Moving forward by perfect fifths always adds one sharp to the key signature (C=0, G=1#, D=2#, etc)."
            ),
            QuizQuestion(
                question="Qual destas escalas ou modos tem uma sonoridade típica do blues e rock clássico?",
                options=["Modo Frígio", "Modo Lócrio", "Modo Jónio", "Modo Mixolídio"],
                correct_index=3,
                explanation="O Modo Mixolídio (Maior com 7ª Menor) é a base de muitos riffs de rock e blues clássico.",
                question_en="Which of these scales or modes has a sound typical of classic blues and rock?",
                options_en=["Phrygian Mode", "Locrian Mode", "Ionian Mode", "Mixolydian Mode"],
                explanation_en="The Mixolydian Mode (Major with a Minor 7th) is the foundation of many classic rock and blues riffs."
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
                explanation="As tríades formam-se empilhando terças (ex: 1, 3 e 5).",
                question_en="A triad is formed by three notes stacked in intervals of:",
                options_en=["Seconds", "Thirds", "Fourths", "Fifths"],
                explanation_en="Triads are formed by stacking thirds (e.g., 1, 3 and 5)."
            ),
            QuizQuestion(
                question="Uma Tríade Maior é formada por quais intervalos consecutivos?",
                options=["Terça Maior + Terça Maior", "Terça Menor + Terça Menor", "Terça Menor + Terça Maior", "Terça Maior + Terça Menor"],
                correct_index=3,
                explanation="Uma tríade maior empilha uma Terça Maior (4 semitons) seguida de uma Terça Menor (3 semitons) em relação a essa.",
                question_en="A Major Triad is formed by which consecutive intervals?",
                options_en=["Major Third + Major Third", "Minor Third + Minor Third", "Minor Third + Major Third", "Major Third + Minor Third"],
                explanation_en="A major triad stacks a Major Third (4 semitones) followed by a Minor Third (3 semitones) relative to it."
            ),
            QuizQuestion(
                question="O que caracteriza um acorde Sus4?",
                options=["A terça é substituída pela quarta", "Tem quatro notas", "A quinta é omitida", "Tem uma quarta aumentada"],
                correct_index=0,
                explanation="No acorde Suspensos (Sus4), a quarta justa substitui a terça, eliminando o caráter de maior ou menor.",
                question_en="What characterizes a Sus4 chord?",
                options_en=["The third is replaced by the fourth", "It has four notes", "The fifth is omitted", "It has an augmented fourth"],
                explanation_en="In Suspended (Sus4) chords, the perfect fourth replaces the third, eliminating its major or minor character."
            ),
            QuizQuestion(
                question="Na 1ª inversão de um acorde de Dó Maior (C/E), qual nota fica no baixo?",
                options=["Dó", "Mi", "Sol", "Fá"],
                correct_index=1,
                explanation="A 1ª inversão coloca a terça (Mi) no baixo.",
                question_en="In the 1st inversion of a C Major chord (C/E), which note is in the bass?",
                options_en=["C", "E", "G", "F"],
                explanation_en="The 1st inversion places the third (E) in the bass."
            ),
            QuizQuestion(
                question="Qual é a principal vantagem de usar inversões de acordes?",
                options=["Aumentar o volume", "Permitir um voice leading mais suave", "Mudar a tonalidade", "Facilitar a leitura da clave"],
                correct_index=1,
                explanation="Inversões permitem mover as vozes (em especial o baixo) de forma próxima e elegante, evitando grandes saltos.",
                question_en="What is the main advantage of using chord inversions?",
                options_en=["Increase volume", "Allow smoother voice leading", "Change the key", "Make clef reading easier"],
                explanation_en="Inversions allow voices (especially the bass) to move closely and elegantly, avoiding large leaps."
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
                explanation="O grau ii num Campo Harmónico Maior é sempre menor (ex: em Dó Maior, o grau ii é Ré menor).",
                question_en="In a Major Harmonic Field, what chord type is the ii degree?",
                options_en=["Major", "Minor", "Diminished", "Augmented"],
                explanation_en="The ii degree in a Major Harmonic Field is always minor (e.g., in C Major, the ii degree is D minor)."
            ),
            QuizQuestion(
                question="Qual função harmónica transmite a máxima tensão e urgência de resolução?",
                options=["Tónica", "Subdominante", "Dominante", "Relativa"],
                correct_index=2,
                explanation="A Função Dominante (graus V e vii°) pede resolução fortemente para a Tónica.",
                question_en="Which harmonic function conveys maximum tension and urgency for resolution?",
                options_en=["Tonic", "Subdominant", "Dominant", "Relative"],
                explanation_en="The Dominant Function (V and vii° degrees) strongly demands resolution to the Tonic."
            ),
            QuizQuestion(
                question="Uma tétrade adiciona uma quarta nota à tríade básica. A que distância da quinta fica essa nota?",
                options=["Uma segunda", "Uma terça", "Uma quarta", "Uma oitava"],
                correct_index=1,
                explanation="As tétrades continuam o empilhamento original de tríades, adicionando uma sétima (que está à distância de uma terça da quinta).",
                question_en="A tetrad adds a fourth note to the basic triad. How far from the fifth is this note?",
                options_en=["A second", "A third", "A fourth", "An octave"],
                explanation_en="Tetrads continue the original stacking of triads, adding a seventh (which is a third away from the fifth)."
            ),
            QuizQuestion(
                question="Que acorde é formado pelos graus 1 - ♭3 - 5 - ♭7?",
                options=["Maior com 7ª Maior (maj7)", "Menor com 7ª (m7)", "Dominante com 7ª (7)", "Meio-Diminuto (m7b5)"],
                correct_index=1,
                explanation="O acorde Menor com 7ª (m7) possui a terça menor (♭3), a quinta justa e a sétima menor (♭7).",
                question_en="Which chord is formed by the degrees 1 - ♭3 - 5 - ♭7?",
                options_en=["Major 7th (maj7)", "Minor 7th (m7)", "Dominant 7th (7)", "Half-Diminished (m7b5)"],
                explanation_en="The Minor 7th chord (m7) has a minor third (♭3), perfect fifth, and minor seventh (♭7)."
            ),
            QuizQuestion(
                question="A progressão ii - V - I é especialmente comum em que estilos musicais?",
                options=["Heavy Metal", "Jazz e Bossa Nova", "Música Barroca", "Punk Rock"],
                correct_index=1,
                explanation="O ii - V - I é a base estrutural de inúmeros temas de Jazz, Bossa Nova e Pop.",
                question_en="The ii - V - I progression is especially common in which musical styles?",
                options_en=["Heavy Metal", "Jazz and Bossa Nova", "Baroque Music", "Punk Rock"],
                explanation_en="The ii - V - I is the structural foundation of countless Jazz, Bossa Nova, and Pop tunes."
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
                explanation="É um acorde maior com 7ª que atua temporariamente como dominante (V) para resolver noutro acorde diatónico.",
                question_en="What is a Secondary Dominant?",
                options_en=["The V chord of any degree other than I", "The second chord of a song", "A minor 7th chord", "A dominant without a tritone"],
                explanation_en="It is a major 7th chord that temporarily acts as a dominant (V) to resolve to another diatonic chord."
            ),
            QuizQuestion(
                question="O que é o Empréstimo Modal (ou Intercâmbio Modal)?",
                options=["Mudar de instrumento", "Usar acordes da escala homónima menor num tom maior", "Tocar acordes mais graves", "Alterar a afinação"],
                correct_index=1,
                explanation='Consiste em "pedir emprestados" acordes da escala paralela (ex: usar um Fm numa progressão em Dó Maior).',
                question_en="What is Modal Borrowing (or Modal Interchange)?",
                options_en=["Changing instruments", "Using chords from the parallel minor scale in a major key", "Playing lower chords", "Changing tuning"],
                explanation_en='It consists of "borrowing" chords from the parallel scale (e.g., using an Fm in a C Major progression).'
            ),
            QuizQuestion(
                question="Na substituição tritónica (SubV7), o acorde G7 (em Dó Maior) pode ser substituído por qual acorde?",
                options=["Dm7", "Cmaj7", "D♭7", "F♯7"],
                correct_index=2,
                explanation="O G7 pode ser substituído por D♭7, que partilha o mesmo trítono (B e F) mas tem o baixo a um semitom do acorde de resolução (C).",
                question_en="In tritone substitution (SubV7), the G7 chord (in C Major) can be replaced by which chord?",
                options_en=["Dm7", "Cmaj7", "D♭7", "F♯7"],
                explanation_en="G7 can be replaced by D♭7, which shares the same tritone (B and F) but has its bass a semitone away from the resolution chord (C)."
            ),
            QuizQuestion(
                question="Qual é o efeito no baixo ao usar uma substituição tritónica do grau V para o I?",
                options=["O baixo salta uma quinta", "O baixo desce cromaticamente por meio-tom", "O baixo sobe um tom", "O baixo mantém-se igual"],
                correct_index=1,
                explanation="A substituição tritónica permite uma descida suave em semitom do baixo até à tónica (ex: D♭ desce para C).",
                question_en="What is the bass effect when using a tritone substitution from the V degree to the I?",
                options_en=["The bass leaps a fifth", "The bass descends chromatically by a half step", "The bass goes up a whole step", "The bass stays the same"],
                explanation_en="Tritone substitution allows a smooth half-step descent of the bass down to the tonic (e.g., D♭ down to C)."
            ),
            QuizQuestion(
                question="Que acorde clássico de empréstimo modal tem uma forte carga emotiva/nostálgica quando resolve na tónica maior?",
                options=["O V Maior", "O iv menor", "O ii menor", "O vi menor"],
                correct_index=1,
                explanation="O uso do acorde subdominante menor (iv menor, como Fm em Dó Maior) cria uma sensação agridoce e muito nostálgica.",
                question_en="Which classic modal borrowed chord has a strong emotional/nostalgic feel when resolving to the major tonic?",
                options_en=["The V Major", "The iv minor", "The ii minor", "The vi minor"],
                explanation_en="The use of the minor subdominant chord (iv minor, like Fm in C Major) creates a bittersweet and very nostalgic feeling."
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
                explanation="Em ambas as mãos, o polegar é sempre o dedo 1 e o mindinho o dedo 5.",
                question_en="How are fingers numbered on the piano for each hand?",
                options_en=["1 to 5 from left to right", "1 (pinky) to 5 (thumb)", "1 (thumb) to 5 (pinky)", "A, B, C, D, E"],
                explanation_en="On both hands, the thumb is always finger 1 and the pinky is finger 5."
            ),
            QuizQuestion(
                question="Qual é o padrão de acompanhamento conhecido como Baixo Alberti?",
                options=["Acordes em bloco no 1º tempo", "Arpejo sequencial 1 - 5 - 3 - 5", "Tocar todas as teclas juntas", "Alternar entre as duas mãos a cada nota"],
                correct_index=1,
                explanation="O Baixo Alberti é um acompanhamento clássico que arpeja as notas da tríade na ordem Fundamental, Quinta, Terça e Quinta (1-5-3-5).",
                question_en="What is the accompaniment pattern known as Alberti Bass?",
                options_en=["Block chords on the 1st beat", "Sequential arpeggio 1 - 5 - 3 - 5", "Playing all keys together", "Alternating between both hands for each note"],
                explanation_en="Alberti Bass is a classic accompaniment that arpeggiates the triad notes in the order Root, Fifth, Third, and Fifth (1-5-3-5)."
            ),
            QuizQuestion(
                question="Qual é a postura recomendada para o pulso ao tocar piano?",
                options=["Afundado abaixo das teclas", "Levantado o mais alto possível", "Alinhado e flexível com o antebraço", "Rígido e imóvel"],
                correct_index=2,
                explanation="O pulso deve estar alinhado com o antebraço e flexível como um amortecedor suave.",
                question_en="What is the recommended wrist posture when playing the piano?",
                options_en=["Sunken below the keys", "Raised as high as possible", "Aligned and flexible with the forearm", "Rigid and motionless"],
                explanation_en="The wrist should be aligned with the forearm and flexible like a soft shock absorber."
            ),
            QuizQuestion(
                question="Num acorde Cmaj7 (C-E-G-B) em posição fundamental na mão direita, qual é a dedilhação recomendada?",
                options=["1-2-3-5", "1-3-4-5", "1-2-4-5", "2-3-4-5"],
                correct_index=0,
                explanation="Para cobrir as quatro notas mantendo a mão relaxada, a dedilhação habitual é 1-2-3-5, deixando o dedo 4 repousar livremente.",
                question_en="In a Cmaj7 chord (C-E-G-B) in root position on the right hand, what is the recommended fingering?",
                options_en=["1-2-3-5", "1-3-4-5", "1-2-4-5", "2-3-4-5"],
                explanation_en="To cover the four notes while keeping the hand relaxed, the usual fingering is 1-2-3-5, letting finger 4 rest freely."
            ),
            QuizQuestion(
                question="Para destacar a melodia principal ao tocar acordes no piano, onde deve recair mais 'peso'?",
                options=["No polegar", "Na mão esquerda", "No dedo 5 (mindinho)", "No pedal"],
                correct_index=2,
                explanation="Para que a nota mais aguda (a melodia) sobressaia dos acordes, deve-se aplicar ligeiramente mais peso no lado do dedo mindinho da mão direita.",
                question_en="To highlight the main melody when playing chords on the piano, where should more 'weight' fall?",
                options_en=["On the thumb", "On the left hand", "On finger 5 (pinky)", "On the pedal"],
                explanation_en="So that the highest note (the melody) stands out from the chords, slightly more weight should be applied to the pinky side of the right hand."
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
                explanation="O CAGED baseia-se em 5 formas de acordes abertos: Dó (C), Lá (A), Sol (G), Mi (E) e Ré (D).",
                question_en="In the CAGED system, how many fundamental open chord shapes are there?",
                options_en=["3", "5", "7", "12"],
                explanation_en="CAGED is based on 5 open chord shapes: C, A, G, E, and D."
            ),
            QuizQuestion(
                question="O que permite transpor as formas do CAGED ao longo de todo o braço da guitarra?",
                options=["O uso do polegar atrás do braço", "Mudar de afinação", "Tocar apenas cordas soltas", "O uso do dedo indicador como pestana móvel"],
                correct_index=3,
                explanation="O dedo indicador atua como uma 'pestana' (capotraste humano), permitindo deslocar os acordes abertos pelo braço.",
                question_en="What allows transposing CAGED shapes all over the guitar fretboard?",
                options_en=["Using the thumb behind the neck", "Changing tuning", "Playing only open strings", "Using the index finger as a movable barre"],
                explanation_en="The index finger acts as a 'barre' (human capo), allowing open chords to be moved up the neck."
            ),
            QuizQuestion(
                question="Para fazer uma pestana sem dor, que parte do dedo indicador deve pressionar as cordas?",
                options=["A almofada macia central", "A ponta do dedo", "A lateral ligeiramente externa e ossuda", "A parte de trás do dedo"],
                correct_index=2,
                explanation="A lateral do dedo é mais firme e óssea, fornecendo pressão uniforme nas cordas com menos fadiga.",
                question_en="To play a barre chord without pain, which part of the index finger should press the strings?",
                options_en=["The soft central pad", "The fingertip", "The slightly outer bony side", "The back of the finger"],
                explanation_en="The side of the finger is firmer and bonier, providing even string pressure with less fatigue."
            ),
            QuizQuestion(
                question="Na mão direita, num dedilhado padrão (P.I.M.A.), que dedo é responsável pelas cordas graves (6ª, 5ª, 4ª)?",
                options=["Indicador (I)", "Médio (M)", "Anelar (A)", "Polegar (P)"],
                correct_index=3,
                explanation="O Polegar (P) encarrega-se do baixo e das cordas graves, enquanto o I, M e A dedilham as cordas mais agudas.",
                question_en="On the right hand, in a standard fingerpicking pattern (P.I.M.A.), which finger is responsible for the bass strings (6th, 5th, 4th)?",
                options_en=["Index (I)", "Middle (M)", "Ring (A)", "Thumb (P)"],
                explanation_en="The Thumb (P) handles the bass and lower strings, while I, M, and A pluck the higher strings."
            ),
            QuizQuestion(
                question="Qual é a finalidade do exercício 'Spider Walk 1-2-3-4' na guitarra?",
                options=["Um dedilhado com a mão direita", "Tocar trastes consecutivos para ganhar força e independência na mão esquerda", "Deslizar a pestana rapidamente", "Tocar as 6 cordas ao mesmo tempo"],
                correct_index=1,
                explanation="É um exercício clássico de coordenação e destreza onde cada dedo pressiona um traste de cada vez, corda por corda.",
                question_en="What is the purpose of the 'Spider Walk 1-2-3-4' exercise on the guitar?",
                options_en=["A right-hand picking pattern", "Playing consecutive frets to gain strength and independence in the left hand", "Sliding the barre quickly", "Strumming all 6 strings at once"],
                explanation_en="It is a classic coordination and dexterity exercise where each finger presses one fret at a time, string by string."
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
                explanation="O BPM (Beats Per Minute) define a velocidade constante do pulso musical.",
                question_en="How is musical tempo (beat speed) measured?",
                options_en=["In Decibels (dB)", "In Hertz (Hz)", "In BPM (Beats Per Minute)", "In Measures"],
                explanation_en="BPM (Beats Per Minute) sets the constant speed of the musical pulse."
            ),
            QuizQuestion(
                question="Num compasso de 4/4, qual figura rítmica vale 1 batida (1 tempo)?",
                options=["Semibreve", "Mínima", "Semínima", "Colcheia"],
                correct_index=2,
                explanation="A Semínima (figura 4) é a unidade de tempo do compasso 4/4, durando 1 batida.",
                question_en="In a 4/4 time signature, which rhythmic figure is worth 1 beat?",
                options_en=["Whole note", "Half note", "Quarter note", "Eighth note"],
                explanation_en="The Quarter note (figure 4) is the beat unit in 4/4 time, lasting 1 beat."
            ),
            QuizQuestion(
                question="O que faz um 'ponto de aumentação' ao lado de uma figura rítmica?",
                options=["Dobra o seu valor", "Corta o valor a meio", "Acrescenta metade do seu valor original", "Anula a nota"],
                correct_index=2,
                explanation="O ponto prolonga a nota em mais metade do seu próprio valor de duração.",
                question_en="What does a 'dot' next to a rhythmic figure do?",
                options_en=["Doubles its value", "Cuts its value in half", "Adds half of its original value", "Cancels the note"],
                explanation_en="The dot extends the note by an additional half of its original duration value."
            ),
            QuizQuestion(
                question="Quantas batidas vale uma Semibreve num compasso 4/4?",
                options=["1", "2", "3", "4"],
                correct_index=3,
                explanation="A Semibreve preenche todo o compasso de 4/4, durando as 4 batidas.",
                question_en="How many beats is a Whole note worth in 4/4 time?",
                options_en=["1", "2", "3", "4"],
                explanation_en="The Whole note fills the entire 4/4 measure, lasting all 4 beats."
            ),
            QuizQuestion(
                question="Como se chama o efeito rítmico quando o acento cai num tempo fraco ou contratempo?",
                options=["Legato", "Síncopa", "Crescendo", "Staccato"],
                correct_index=1,
                explanation="A síncopa (ou sincopado) desloca o acento rítmico forte esperado, criando fluidez e tensão.",
                question_en="What is the rhythmic effect called when the accent falls on a weak or off-beat?",
                options_en=["Legato", "Syncopation", "Crescendo", "Staccato"],
                explanation_en="Syncopation shifts the expected strong rhythmic accent, creating flow and tension."
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
                explanation="A forma musical é a estrutura ou arquitetura de como a música se divide em partes (A, B, refrões, etc).",
                question_en="What describes Musical Form?",
                options_en=["The arrangement of musicians on stage", "The volume of the piece over time", "The temporal organization of sections, themes, and contrasts", "The acoustic shape of the instrument"],
                explanation_en="Musical form is the structure or architecture of how music is divided into parts (A, B, choruses, etc)."
            ),
            QuizQuestion(
                question="Uma forma Ternária clássica é habitualmente representada por que letras?",
                options=["AB", "AABB", "ABC", "ABA"],
                correct_index=3,
                explanation="Na forma ABA, apresenta-se um tema A, um contraste B, e regressa-se ao tema inicial A.",
                question_en="A classic Ternary form is usually represented by which letters?",
                options_en=["AB", "AABB", "ABC", "ABA"],
                explanation_en="In ABA form, a theme A is presented, followed by a contrasting B, and returning to the initial A theme."
            ),
            QuizQuestion(
                question="Na Forma Sonata, em que secção se fragmenta e transforma os temas, criando tensão máxima?",
                options=["Exposição", "Desenvolvimento", "Reexposição", "Coda"],
                correct_index=1,
                explanation="O Desenvolvimento é a secção central da sonata onde os temas viajam por tonalidades instáveis.",
                question_en="In Sonata Form, in which section are the themes fragmented and transformed, creating maximum tension?",
                options_en=["Exposition", "Development", "Recapitulation", "Coda"],
                explanation_en="The Development is the central section of the sonata where themes travel through unstable keys."
            ),
            QuizQuestion(
                question="Numa estrutura de canção Pop/Rock, que secção costuma ser o clímax emocional e melódico?",
                options=["O Verso", "A Introdução", "O Refrão", "O Outro"],
                correct_index=2,
                explanation="O Refrão é geralmente o clímax que concentra a mensagem principal e a energia da canção.",
                question_en="In a Pop/Rock song structure, which section is usually the emotional and melodic climax?",
                options_en=["The Verse", "The Intro", "The Chorus", "The Outro"],
                explanation_en="The Chorus is generally the climax that concentrates the main message and energy of the song."
            ),
            QuizQuestion(
                question="A técnica de 'repetir um motivo a alturas diferentes (ex: subindo grau a grau)' chama-se:",
                options=["Sequência", "Inversão", "Aumentação", "Diminuição"],
                correct_index=0,
                explanation="Uma progressão sequencial consiste em repetir a mesma figura melódica deslocando-a paralelamente.",
                question_en="The technique of 'repeating a motif at different pitches (e.g., rising degree by degree)' is called:",
                options_en=["Sequence", "Inversion", "Augmentation", "Diminution"],
                explanation_en="A sequential progression consists of repeating the same melodic figure by shifting it in parallel."
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
                explanation="O 'ff' (Fortissimo) instrui a tocar a peça muito forte.",
                question_en="What does the dynamic symbol 'ff' indicate in a score?",
                options_en=["Very soft (Pianissimo)", "End of the piece (Fine)", "Fast (Presto)", "Very loud (Fortissimo)"],
                explanation_en="The 'ff' (Fortissimo) instructs to play the piece very loudly."
            ),
            QuizQuestion(
                question="Como se chama o aumento gradual de volume numa frase musical?",
                options=["Accelerando", "Crescendo", "Decrescendo", "Legato"],
                correct_index=1,
                explanation="Crescendo significa aumentar gradualmente a intensidade/volume do som.",
                question_en="What is the gradual increase in volume in a musical phrase called?",
                options_en=["Accelerando", "Crescendo", "Decrescendo", "Legato"],
                explanation_en="Crescendo means to gradually increase the intensity/volume of the sound."
            ),
            QuizQuestion(
                question="O que significa a indicação para tocar em 'Staccato'?",
                options=["Tocar notas curtas e separadas", "Tocar as notas perfeitamente ligadas", "Tocar muito devagar", "Tocar com muita força"],
                correct_index=0,
                explanation="O staccato é a articulação que encurta a nota, tornando-a destacada e separada da próxima.",
                question_en="What does the indication to play in 'Staccato' mean?",
                options_en=["Play short, detached notes", "Play the notes perfectly connected", "Play very slowly", "Play with a lot of force"],
                explanation_en="Staccato is the articulation that shortens the note, making it detached and separated from the next one."
            ),
            QuizQuestion(
                question="O que é o 'Rubato' na expressão musical?",
                options=["Uma pausa longa obrigatória", "Tocar perfeitamente no tempo mecânico", "Liberdade expressiva no tempo (atrasar ou acelerar levemente)", "Um tipo de acorde invertido"],
                correct_index=2,
                explanation="O rubato permite ao intérprete dar elasticidade ao tempo, acelerando e abrandando para maior emoção.",
                question_en="What is 'Rubato' in musical expression?",
                options_en=["A mandatory long pause", "Playing perfectly in mechanical time", "Expressive freedom in tempo (slightly speeding up or slowing down)", "A type of inverted chord"],
                explanation_en="Rubato allows the performer to give elasticity to the tempo, speeding up and slowing down for greater emotion."
            ),
            QuizQuestion(
                question="Qual é a melhor prática para o uso do Pedal de Sustain no piano?",
                options=["Manter sempre pressionado", "Trocar o pedal a cada mudança harmónica para não misturar os acordes", "Nunca usar o pedal em peças clássicas", "Trocar a cada batida rigorosa do metrónomo"],
                correct_index=1,
                explanation="Levantar e pressionar novamente o pedal (troca de pedal) a cada mudança de acorde evita que as notas embolem e criem ruído harmónico.",
                question_en="What is the best practice for using the Sustain Pedal on the piano?",
                options_en=["Keep it pressed down at all times", "Change the pedal on every chord change so as not to mix chords", "Never use the pedal in classical pieces", "Change on every strict metronome beat"],
                explanation_en="Lifting and repressing the pedal (pedal change) on every chord change prevents the notes from blurring and creating harmonic noise."
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
                explanation="Transpor é executar a mesma peça noutro tom (mais alto ou mais baixo).",
                question_en="What does it mean to 'Transpose' a musical piece?",
                options_en=["Change the main rhythm of the song", "Change instruments during the piece", "Move the song to a different key while maintaining interval relationships", "Play backwards"],
                explanation_en="To transpose is to perform the same piece in a different key (higher or lower)."
            ),
            QuizQuestion(
                question="Seguindo o Círculo de Quintas, se avançares uma casa a partir de Dó Maior (adicionando 1 sustenido), qual é a nova tonalidade?",
                options=["Fá Maior", "Sol Maior", "Ré Maior", "Lá Maior"],
                correct_index=1,
                explanation="Dó Maior não tem acidentes. A quinta justa acima de Dó é Sol, e Sol Maior tem exatamente 1 sustenido.",
                question_en="Following the Circle of Fifths, if you move one step from C Major (adding 1 sharp), what is the new key?",
                options_en=["F Major", "G Major", "D Major", "A Major"],
                explanation_en="C Major has no accidentals. The perfect fifth above C is G, and G Major has exactly 1 sharp."
            ),
            QuizQuestion(
                question="Se transpores uma melodia de Dó Maior para Sol Maior, qual é o intervalo exato da transposição ascendente?",
                options=["Uma terça maior", "Uma quarta justa", "Uma quinta justa", "Uma oitava"],
                correct_index=2,
                explanation="De C para G ascendente, o intervalo é de uma Quinta Justa (7 semitons).",
                question_en="If you transpose a melody from C Major to G Major, what is the exact interval of the upward transposition?",
                options_en=["A major third", "A perfect fourth", "A perfect fifth", "An octave"],
                explanation_en="From C to G ascending, the interval is a Perfect Fifth (7 semitones)."
            ),
            QuizQuestion(
                question="Quantos acidentes tem a armação de clave da tonalidade de Si♭ Maior?",
                options=["1 bemol", "2 bemóis", "3 bemóis", "1 sustenido"],
                correct_index=1,
                explanation="Si♭ Maior tem 2 bemóis na sua armação de clave (Si♭ e Mi♭).",
                question_en="How many accidentals does the key signature of B♭ Major have?",
                options_en=["1 flat", "2 flats", "3 flats", "1 sharp"],
                explanation_en="B♭ Major has 2 flats in its key signature (B♭ and E♭)."
            ),
            QuizQuestion(
                question="Na guitarra, qual é a ferramenta rápida para transpor a música para um tom mais alto usando exatamente os mesmos acordes abertos?",
                options=["Mudar a afinação de cada corda", "Usar uma Capotraste (cejilha)", "Tocar apenas acordes em pestana", "Diminuir a grossura das cordas"],
                correct_index=1,
                explanation="A Capotraste age como uma 'pestana móvel', subindo a afinação geral e permitindo usar as mesmas formas CAGED que se usaria no início do braço.",
                question_en="On the guitar, what is a quick tool to transpose the song to a higher key using the exact same open chords?",
                options_en=["Change the tuning of each string", "Use a Capo", "Play only barre chords", "Decrease the string gauge"],
                explanation_en="A Capo acts as a 'movable barre', raising the overall pitch and allowing the use of the same CAGED shapes you would use at the nut."
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
                explanation="A progressão ii - V - I é o bloco harmónico mais usado no Jazz (ex: Dm7 - G7 - Cmaj7).",
                question_en="What is the most famous chord progression in Jazz and Bossa Nova?",
                options_en=["I - IV - V", "ii - V - I", "I - vi - IV - V", "iii - vi - ii - V"],
                explanation_en="The ii - V - I progression is the most used harmonic building block in Jazz (e.g., Dm7 - G7 - Cmaj7)."
            ),
            QuizQuestion(
                question="Quantos compassos tem a estrutura clássica do Blues?",
                options=["8", "12", "16", "32"],
                correct_index=1,
                explanation="O Blues tradicional baseia-se numa estrutura formal rígida de 12 compassos.",
                question_en="How many measures does the classic Blues structure have?",
                options_en=["8", "12", "16", "32"],
                explanation_en="Traditional Blues is based on a rigid formal structure of 12 measures."
            ),
            QuizQuestion(
                question="Segundo a teoria acorde-escala (chord-scale theory), qual o modo associado ao grau ii (m7)?",
                options=["Jónio", "Dórico", "Frígio", "Lídio"],
                correct_index=1,
                explanation="O acorde de grau ii (m7) associa-se ao Modo Dórico.",
                question_en="According to chord-scale theory, which mode is associated with the ii degree (m7)?",
                options_en=["Ionian", "Dorian", "Phrygian", "Lydian"],
                explanation_en="The ii degree chord (m7) is associated with the Dorian Mode."
            ),
            QuizQuestion(
                question="O que é o 'Turnaround' nos compassos 11-12 do Blues?",
                options=["Uma pausa completa", "A repetição da melodia", "A progressão final que conduz o regresso ao início (I7 - V7)", "Um solo de bateria"],
                correct_index=2,
                explanation="O turnaround prepara a repetição da forma de 12 compassos conduzindo de volta à tónica.",
                question_en="What is the 'Turnaround' in measures 11-12 of the Blues?",
                options_en=["A complete pause", "The repetition of the melody", "The final progression that leads back to the beginning (I7 - V7)", "A drum solo"],
                explanation_en="The turnaround sets up the repetition of the 12-bar form by leading back to the tonic."
            ),
            QuizQuestion(
                question="Em Rootless Voicings no piano, o que se omite na mão direita?",
                options=["A terça", "A sétima", "A fundamental", "A quinta"],
                correct_index=2,
                explanation="No piano jazz, a fundamental é deixada para o baixo (mão esquerda), libertando a mão direita para tocar guide tones e extensões.",
                question_en="In Rootless Voicings on the piano, what is omitted in the right hand?",
                options_en=["The third", "The seventh", "The root", "The fifth"],
                explanation_en="In jazz piano, the root is left for the bass (left hand), freeing the right hand to play guide tones and extensions."
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
                explanation="A 3ª e a 7ª definem o carácter do acorde (maior, menor, dominante) e são os alvos melódicos principais.",
                question_en="What are 'Guide Tones' in a chord progression?",
                options_en=["The root and the fifth", "The 3rd and 7th of each chord", "The highest notes of the scale", "Notes played in staccato"],
                explanation_en="The 3rd and 7th define the character of the chord (major, minor, dominant) and are the main melodic targets."
            ),
            QuizQuestion(
                question="Em que notas do acorde deve idealmente aterrar uma frase de improvisação nos tempos fortes?",
                options=["Nas notas de aproximação cromática", "Nas notas alvo (Target Notes / 3ª e 7ª)", "Em pausas", "Apenas na fundamental"],
                correct_index=1,
                explanation="Aterrar nas notas alvo nos tempos fortes dá clareza harmónica à improvisação.",
                question_en="On which chord notes should an improvisation phrase ideally land on the strong beats?",
                options_en=["On chromatic approach notes", "On target notes (3rd and 7th)", "On rests", "Only on the root"],
                explanation_en="Landing on target notes on the strong beats provides harmonic clarity to the improvisation."
            ),
            QuizQuestion(
                question="Qual a escala mais utilizada para solos de Blues e Rock?",
                options=["Escala Maior", "Escala Pentatónica Menor (com a Blue Note)", "Escala Cromática", "Modo Lócrio"],
                correct_index=1,
                explanation="A Pentatónica Menor com a Blue Note (trítono) é o pilar da improvisação de Blues e Rock.",
                question_en="What is the most used scale for Blues and Rock solos?",
                options_en=["Major Scale", "Minor Pentatonic Scale (with the Blue Note)", "Chromatic Scale", "Locrian Mode"],
                explanation_en="The Minor Pentatonic with the Blue Note (tritone) is the pillar of Blues and Rock improvisation."
            ),
            QuizQuestion(
                question="O que é uma aproximação cromática?",
                options=["Tocar desafinado", "Tocar um semitom acima ou abaixo da nota alvo antes de a atingir", "Saltar uma oitava", "Acelerar o tempo"],
                correct_index=1,
                explanation="A aproximação cromática cria tensão momentânea que resolve na nota do acorde.",
                question_en="What is a chromatic approach?",
                options_en=["Playing out of tune", "Playing a semitone above or below the target note before hitting it", "Jumping an octave", "Speeding up the tempo"],
                explanation_en="A chromatic approach creates momentary tension that resolves to the chord tone."
            ),
            QuizQuestion(
                question="Como se liga uma linha melódica entre acordes com fluidez?",
                options=["Saltando grandes oitavas", "Movendo-se por passos de semitom/tom em direção aos Guide Tones", "Parando de tocar entre acordes", "Repetindo sempre a mesma nota"],
                correct_index=1,
                explanation="Conduzir frases por graus conjuntos em direção aos Guide Tones cria linhas melódicas contínuas.",
                question_en="How do you connect a melodic line between chords fluidly?",
                options_en=["By jumping large octaves", "By moving in half-steps/whole-steps towards the Guide Tones", "By stopping playing between chords", "By constantly repeating the same note"],
                explanation_en="Leading phrases by step towards Guide Tones creates continuous melodic lines."
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
                explanation="No movimento contrário, a independência contrapontística das vozes é máxima.",
                question_en="What type of motion between voices is considered the most independent and elegant?",
                options_en=["Parallel Motion", "Contrary Motion (one voice ascends and the other descends)", "Direct Motion", "No Motion"],
                explanation_en="In contrary motion, the contrapuntal independence of the voices is at its maximum."
            ),
            QuizQuestion(
                question="Na condução de vozes tradicional, que intervalo paralelo deve ser rigorosamente evitado?",
                options=["Terças paralelas", "Sextas paralelas", "Quintas e Oitavas paralelas", "Quartas paralelas"],
                correct_index=2,
                explanation="Quintas e oitavas paralelas destroem a individualidade melódica das duas vozes.",
                question_en="In traditional voice leading, which parallel interval should be strictly avoided?",
                options_en=["Parallel thirds", "Parallel sixths", "Parallel fifths and octaves", "Parallel fourths"],
                explanation_en="Parallel fifths and octaves destroy the melodic individuality of the two voices."
            ),
            QuizQuestion(
                question="O que caracteriza o Movimento Oblíquo entre duas vozes?",
                options=["Ambas as vozes sobem", "Uma voz permanece fixa enquanto a outra se move", "Ambas descem", "Nenhuma se move"],
                correct_index=1,
                explanation="No movimento oblíquo, uma linha mantém-se estática enquanto a outra progride.",
                question_en="What characterizes Oblique Motion between two voices?",
                options_en=["Both voices ascend", "One voice remains stationary while the other moves", "Both descend", "Neither moves"],
                explanation_en="In oblique motion, one line remains static while the other progresses."
            ),
            QuizQuestion(
                question="Qual o princípio de 'Economia de Movimento' na condução de vozes?",
                options=["Mover cada voz pelo menor caminho possível (passos de semitom ou tom)", "Dar grandes saltos de oitava", "Usar só uma mão", "Tocar o mais rápido possível"],
                correct_index=0,
                explanation="A economia de movimento garante uma transição vocal fluida e natural.",
                question_en="What is the principle of 'Economy of Motion' in voice leading?",
                options_en=["Moving each voice by the shortest path possible (half or whole steps)", "Making large octave jumps", "Using only one hand", "Playing as fast as possible"],
                explanation_en="Economy of motion ensures a smooth and natural vocal transition."
            ),
            QuizQuestion(
                question="Em peças a duas vozes na viola (como as de Bach), qual o papel do polegar direito?",
                options=["Tocar a melodia aguda", "Manter a linha de baixo independente", "Abafar as cordas", "Tocar em staccato"],
                correct_index=1,
                explanation="O polegar conduz a linha de baixo contrapontística.",
                question_en="In two-voice pieces on the guitar (like Bach's), what is the role of the right thumb?",
                options_en=["To play the high melody", "To maintain the independent bass line", "To mute the strings", "To play in staccato"],
                explanation_en="The thumb leads the contrapuntal bass line."
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
                explanation="A Prática Deliberada isola e corrige fraquezas de forma consciente e focada.",
                question_en="What characterizes Deliberate Practice as opposed to just playing through the piece?",
                options_en=["Playing without a metronome", "Focused study on the conscious correction of specific flaws", "Playing for 5 hours straight", "Playing as fast as possible"],
                explanation_en="Deliberate Practice isolates and corrects weaknesses in a conscious, focused manner."
            ),
            QuizQuestion(
                question="A que velocidade de rampa se deve começar a praticar uma passagem complexa?",
                options=["A 120% do BPM alvo", "A 70% do BPM alvo (velocidade lenta e precisa)", "Sem metrónomo", "A 100% do BPM alvo"],
                correct_index=1,
                explanation="Estudar a 70% do BPM consolida a precisão neuromuscular antes de aumentar a velocidade.",
                question_en="At what ramp speed should you start practicing a complex passage?",
                options_en=["At 120% of target BPM", "At 70% of target BPM (slow and precise speed)", "Without a metronome", "At 100% of target BPM"],
                explanation_en="Studying at 70% of the BPM solidifies neuromuscular precision before increasing speed."
            ),
            QuizQuestion(
                question="O que significa a técnica de 'Chunking' no estudo musical?",
                options=["Repetir a peça do início ao fim", "Isolar pequenos blocos de 1 a 2 compassos onde ocorre o erro", "Tocar com os olhos fechados", "Mudar de instrumento"],
                correct_index=1,
                explanation="Chunking divide o problema em segmentos pequenos e controláveis.",
                question_en="What does the 'Chunking' technique mean in musical study?",
                options_en=["Repeating the piece from beginning to end", "Isolating small blocks of 1 to 2 measures where the error occurs", "Playing with eyes closed", "Changing instruments"],
                explanation_en="Chunking divides the problem into small, manageable segments."
            ),
            QuizQuestion(
                question="Para a retenção de memória muscular a longo prazo, qual o formato de estudo mais eficaz?",
                options=["3 horas num único dia do fim de semana", "Sessões diárias curtas e focadas de 20 a 30 minutos (repetição espaçada)", "Estudar apenas antes do concerto", "Não praticar com frequência"],
                correct_index=1,
                explanation="A repetição espaçada diária consolida a memória a longo prazo muito melhor do que maratonas esporádicas.",
                question_en="For long-term muscle memory retention, what is the most effective study format?",
                options_en=["3 hours on a single weekend day", "Short, focused daily sessions of 20 to 30 minutes (spaced repetition)", "Studying only before the concert", "Not practicing often"],
                explanation_en="Daily spaced repetition consolidates long-term memory much better than sporadic marathons."
            ),
            QuizQuestion(
                question="Qual o procedimento correto na Rampa de Tempo se cometeres um erro ao subir 5 BPM?",
                options=["Aumentar mais 10 BPM", "Reduzir 2 a 5 BPM e consolidar a precisão sem erros", "Desistir da passagem", "Ignorar o erro e continuar"],
                correct_index=1,
                explanation="Regredir ligeiramente o tempo permite fixar o padrão correto sem reforçar o erro.",
                question_en="What is the correct procedure in a Tempo Ramp if you make a mistake when going up 5 BPM?",
                options_en=["Increase another 10 BPM", "Reduce 2 to 5 BPM and consolidate accuracy without errors", "Give up on the passage", "Ignore the error and continue"],
                explanation_en="Slightly rolling back the tempo allows the correct pattern to stick without reinforcing the mistake."
            ),
        ]
    ),
]
