# Revisão do Claude — Protocolo de Handoff

Este ficheiro é escrito pelo **Claude**, depois de analisar cada fase reportada em
`.agent-sync/GEMINI_STATUS.md`: corro a suite de testes, reviso o código alterado,
e arranco a app para confirmar que não há erros de runtime.

Cada entrada tem um veredito:
- **APROVADO** — nada a fazer, podes avançar para a fase seguinte.
- **AÇÃO NECESSÁRIA** — há itens concretos a corrigir antes de avançares. Lê a
  lista, corrige, faz commit, e atualiza o `GEMINI_STATUS.md` a confirmar.
- **TRABALHO PEDIDO** — não é correção de nada que já exista; é a especificação
  de funcionalidade nova a implementar a seguir. Trata como se fosse uma prompt
  normal do utilizador (clogomes), só que entregue por este ficheiro.

---

## Revisão — Unificação de Cores no Ecrã de Teoria (fecha o último item da Fase 20)
- Commits revistos: `86f4d9d`/`6651061`
- Testes: 144/144 OK
- App: arranca sem erros
- Cores hardcoded em `theory_screen.py`: desceram de 23 para 9 ocorrências,
  das quais 5 são `"transparent"` (não é inconsistência, é frame sem fundo
  próprio) — sobram apenas 4 hex reais: `#7C3AED`, `#2563EB`, `#059669`,
  `#475569`, usados em botões/badges pontuais, não em fundos de card. O
  problema original ("várias janelas com fundos e cores diferentes") está
  resolvido.
- **Veredito: APROVADO**

Nota cosmética muito menor, sem necessidade de ação: o dicionário
`diff_colors` (linha ~182) usa `"#8B5CF6"` e `"#F59E0B"` como literais
quando já existem `theme.COLOR_ACCENT_PURPLE` e `theme.COLOR_ACCENT_AMBER`
com o mesmo valor — podes trocar por esses tokens da próxima vez que
mexeres neste ficheiro, mas não vale a pena um commit só para isto.

Fase 20 está agora completa nos 3 pontos que faltavam (cores, LaTeX, quiz).
Falta só confirmar o ponto 4 (mais um exemplo prático por módulo) — não
bloqueante, fica para quando fizeres as Fases 23-25.

---

## Revisão — Fase 21 (4 novos capítulos) + Fase 22 (Quiz por capítulo)
- Commits revistos: `9158e43`/`94f05f1` (Fase 21), `2a7ad28`/`a1dc684` (Fase 22)
- Testes: 144/144 OK (3 saltados por falta de `scipy`/`PyMuPDF` local) — subiu de 134 para 144 com os novos testes de `tests/test_theory_quiz.py`
- App: arranca sem erros (`python3 main.py`, ~15s a correr, sem tracebacks)
- Verificação adicional: instanciei `TheoryScreen` isoladamente — 12 capítulos,
  **12/12 têm quiz associado** (`core/theory_quiz.py::CHAPTER_QUIZZES`),
  nenhum capítulo ficou sem cobertura.
- **Veredito: APROVADO**

Boa resposta ao pedido da Fase 21 (mais módulos: Ritmo & Compasso, Forma
Musical, Dinâmica & Expressão, Transposição Prática) e ao item de quiz da
Fase 20 (Fase 22: 5 perguntas de escolha múltipla por capítulo, XP,
feedback instantâneo) — mesmo com tópicos diferentes dos que sugeri na
especificação original, cumprem bem o objetivo pedido.

**Dois itens da Fase 20 continuam por fazer** (não confundir com "concluído":
o commit `d2ba9e8` só tratou do LaTeX e da unificação de painéis):
1. Unificação de cores — `gui/screens/theory_screen.py` continua com 23
   ocorrências de cores hex hardcoded (`#2563EB`, `#E2E8F0`/`#0F172A`, etc.)
   em vez dos tokens de `gui/theme.py`. Isto é a causa original do "fundos e
   cores diferentes" que o utilizador reportou — ainda não está resolvido.
2. Mais um exemplo prático concreto por módulo (pedido original da Fase 20,
   ponto 4) — não verificado se já está coberto pelo conteúdo expandido da
   Fase 21/22.

**Nota de limpeza (não bloqueante)**: ficaram 5 scripts de scratch por
commitar na raiz do repositório — `clean_latex.py`, `fix_slashes.py`,
`patch_readme.py`, `patch_status.py`, `patch_theory.py` — parecem ter sido
usados para fazer edições em lote (ex: limpar o LaTeX). Já cumpriram a
função; convém apagá-los num commit de limpeza para não ficarem na raiz do
projeto.

---

## TRABALHO PEDIDO — Fases 20 a 25 (Teoria mais rica, pedagogia guiada, repertório e som mais realistas)
- Pedido por: clogomes, especificação desenhada pelo Claude e já aprovada
  pelo utilizador ("sim, avança") antes de ser escrita aqui.
- **Ordem obrigatória**: corrige primeiro a AÇÃO NECESSÁRIA da secção
  seguinte (crash na Prática de Escalas) antes de começares qualquer uma
  destas fases — segue a regra de ordem do `PROTOCOL.md`.
- Todas as fases abaixo são independentes entre si (podes implementar pela
  ordem que preferires depois de resolvida a AÇÃO NECESSÁRIA), mas mantém
  cada fase no seu próprio commit, com `git add <ficheiros específicos>`.
- Corre `python3 -m unittest discover tests` no fim de cada fase — os 134
  testes atuais devem continuar a passar, e adiciona testes novos para
  qualquer função pura nova (ex: novo tipo de escala, novo campo `Song`).

### FASE 20 — Teoria Musical: Unificação Visual + Correção de Fórmulas + Quiz por Módulo
**Problema confirmado pelo Claude**: `gui/screens/theory_screen.py` usa
dezenas de cores hex distintas hardcoded (`#FEF3C7`/`#451A03`,
`#EFF6FF`/`#172554`, `#2563EB`, `#7C3AED`, `#059669`, `#475569`, etc.) em
vez do sistema de tokens já existente em `gui/theme.py`
(`COLOR_BG`, `COLOR_SURFACE`, `COLOR_SURFACE_SECONDARY`, `COLOR_BORDER`,
`COLOR_PRIMARY`, `COLOR_SUCCESS_BG`, ...) — daí o aspeto de "várias janelas
com fundos e cores diferentes" reportado pelo utilizador. Além disso,
`core/theory_content.py` tem 4 blocos de LaTeX cru nunca renderizado
(linhas 159, 290, 375, 499 — ex: `$$\text{Tom} - \text{Tom} - ...$$`), que
aparece literal e ilegível no ecrã porque `gui/markdown_renderer.py` não
interpreta LaTeX.

1. **Unificação de cores**: substitui todas as cores hardcoded em
   `theory_screen.py` (fundos de cards, badges de dificuldade, banners de
   dica) pelos tokens de `theme.py`. Usa um único par fundo/superfície
   (`COLOR_BG`/`COLOR_SURFACE`/`COLOR_SURFACE_SECONDARY`) para todos os
   cards e scrollable frames, e no máximo 2 cores de destaque do conjunto
   já existente (ex: `COLOR_PRIMARY` para o capítulo ativo/CTA,
   `COLOR_SUCCESS_BG`+`COLOR_SUCCESS_BORDER` só para caixas de dica
   prática) — não uses simultaneamente âmbar+azul+roxo+verde como acontece
   agora.
2. **Corrigir fórmulas em LaTeX**: substitui as 4 ocorrências em
   `theory_content.py` por texto normal formatado com a sintaxe que
   `markdown_renderer.py` já sabe interpretar (negrito `**...**`,
   marcadores `•`). Exemplo para a linha 159:
   `**Tom – Tom – Semitom – Tom – Tom – Tom – Semitom** (T‑T‑ST‑T‑T‑T‑ST)`
   em vez de `$$\text{Tom} - \text{Tom} - \text{Semitom}...$$`. Revê as
   outras 3 ocorrências da mesma forma (acordes com graus romanos, notas
   do círculo de quintas).
3. **Quiz no final de cada módulo**: estende `TheoryChapter`
   (`core/theory_content.py`) com um novo campo, ex:
   `quiz_question_ids: List[str]` ou gera as perguntas em runtime a partir
   do conteúdo do capítulo reaproveitando `QuizEngine`/`category="teoria"`
   já existente em `core/quiz_engine.py`. No fim do conteúdo de cada
   capítulo em `theory_screen.py`, adiciona um botão "🧠 Testar
   Conhecimentos" que abre um mini-quiz de ~5 perguntas relacionadas com
   esse capítulo (reaproveita o `ScoreCard` já usado nos outros ecrãs de
   prática para mostrar feedback/pontuação no final).
4. **Aprofundar conteúdo**: em cada um dos 8 capítulos existentes, expande
   `content_markdown`, `piano_focus` e `guitar_focus` com mais profundidade
   e pelo menos um exemplo prático concreto e acionável por módulo (ex:
   "Experimenta tocar X agora no teclado/pauta abaixo").

### FASE 21 — Novos Módulos de Teoria
Adiciona novos capítulos a `THEORY_CHAPTERS` em `core/theory_content.py`
(atualmente só 8), seguindo exatamente a mesma estrutura dos existentes
(`content_markdown` + `piano_focus` + `guitar_focus` + `interactive_demo` +
quiz da Fase 20). Sugestão de módulos novos, podes ajustar:
- Cifras e Leadsheets (como ler e tocar a partir de cifras de acordes).
- Voicings e Inversões de Acordes ao Piano.
- Empréstimo Modal e Modulação (aprofunda o que já está mencionado na
  linha 375 do capítulo de harmonia).
- Ritmo, Levadas e Divisão Rítmica (complementa a Fase 9 já implementada,
  do lado teórico).
- Harmonização de Melodias (como escolher acordes para uma melodia dada).

### FASE 22 — Treino Auditivo: Pedagogia Guiada
**Problema confirmado**: `gui/screens/practice_ear.py` vai direto para um
quiz classificativo (identifica o intervalo/acorde tocado) sem nenhum
passo de aprendizagem prévio — `core/quiz_engine.py::generate_ear_interval_question`
e `generate_ear_chord_question` só geram pergunta+opções, sem fase de
demonstração guiada antes da primeira tentativa de cada tipo.
1. Antes da primeira pergunta de cada tipo de intervalo/acorde numa sessão,
   mostra um passo de "escuta guiada": toca a nota de referência, depois o
   alvo, com o nome e a mnemónica (`Interval.mnemonic`) visíveis desde já
   (não escondidos até responder, como acontece agora na `explanation`).
2. Torna os 3 níveis de dificuldade já existentes (`beginner`/
   `intermediate`/`advanced`, usados em `generate_ear_chord_question`)
   progressivos e desbloqueáveis por precisão, reaproveitando
   `core/adaptive_engine.py::get_weak_areas` para decidir quando subir de
   nível, em vez do utilizador escolher o nível manualmente sem orientação.

### FASE 23 — Leitura de Pauta: Passo-a-Passo
**Problema confirmado**: `gui/screens/practice_staff.py` mostra uma nota
aleatória em qualquer posição da pauta via
`QuizEngine.generate_staff_reading_question`, sem qualquer método de
contagem ensinado ao formando.
1. Modo iniciante: restringe as notas geradas a um pequeno conjunto
   próximo da linha de referência (ex: apenas a 2ª linha e os espaços
   adjacentes), com uma anotação visual sobreposta na `StaffCanvas`
   ("conta a partir desta linha") a indicar o método de leitura.
2. Expande o alcance de notas disponíveis progressivamente conforme a
   precisão do formando sobe, usando a mesma lógica adaptativa da Fase 22
   (`get_weak_areas`/`get_recommendation`).

### FASE 24 — Repertório: Mais Músicas, Ritmos e Instrumentos
1. Acrescenta um campo `instrument: str` (`"piano"` / `"guitar"` /
   `"ambos"`) à classe `Song` em `core/songs.py`, e adiciona mais músicas à
   biblioteca (atualmente 16), incluindo peças pensadas especificamente
   para piano e outras especificamente para viola — filtra/mostra esta
   informação na lista de repertório em `practice_song.py`.
2. Expande `audio/backing_tracks.py::BACKING_TRACK_LIBRARY` (atualmente 5
   estilos: rock_basic, slow_ballad, bossa_nova, blues_shuffle, waltz) com
   mais padrões — sugestão: funk, reggae, samba, marcha.
3. Adiciona uma voz de **baixo sintetizado** à grelha rítmica de
   `RhythmPattern` (atualmente só bateria: kick/snare/hihat/ride) —
   segue o padrão de síntese 100% local já usado (`audio/synthesizer.py`),
   com uma linha de baixo simples (tónica/quinta) sincronizada ao acorde
   da música/escala em prática. Adiciona controlo de volume independente
   por voz (bateria vs. baixo) em `BackingTrackPlayer`, e uma variante de
   timbre por padrão (ex: baquetas vs. escovas na caixa, mais suave na
   balada/bossa, mais dura no rock).
4. Adiciona a **Escala Frígia Dominante** (Escala Espanhola/Flamenca,
   fórmula `[0,1,4,5,7,8,10,12]`) a `core/scales.py::SCALE_TYPES` — som
   distinto dos modos já existentes, boa opção pedagógica. Segue o mesmo
   padrão das outras entradas (`name_pt`, `name_en`, `formula_degrees`,
   `formula_steps`, `description`) e o teste genérico
   `test_all_scale_types_structure_and_intervals` já existente deve
   continuar a passar sem alterações (valida qualquer entrada nova
   automaticamente).

### FASE 25 — Som Mais Realista
**Contexto**: piano usa síntese aditiva fixa
(`audio/synthesizer.py::generate_single_frequency`), viola/guitarra usa
Karplus-Strong (`generate_plucked_string`) — ambos sem variação por
dinâmica (volume tocado) ou registo (grave vs. agudo).
1. Piano: introduz leve desafinação entre parciais harmónicos (efeito de
   "stretch tuning", real em pianos acústicos — os harmónicos agudos são
   ligeiramente mais altos que o múltiplo exato da fundamental), brilho
   tímbrico sensível ao volume tocado (mais energia nos harmónicos
   superiores quando `volume` é mais alto), e um pequeno transiente de
   "martelo" (ruído curto e percussivo) no ataque da nota, antes do corpo
   tonal.
2. Viola/Guitarra: varia o `decay_factor` do Karplus-Strong e o espectro do
   ruído inicial (mais brilhante/áspero vs. mais macio) consoante o
   `volume` recebido por `generate_plucked_string`, para simular a
   diferença real entre dedilhado suave e forte.
3. Mantém o teste `tests/test_synthesizer.py` a passar — ajusta ou adiciona
   asserções que validem a nova variação por volume (ex: energia espectral
   mais alta com `volume` maior), sem quebrar as existentes.

---

## AÇÃO NECESSÁRIA — Crash na Prática de Escalas (ecrã fica em branco)
- Encontrado por: Claude, ao investigar o reporte do utilizador "a secção de
  prática de escalas não aparece informação nenhuma".
- **Causa raiz confirmada** (reproduzida diretamente, instanciando
  `PracticeScalesScreen` fora da app):
  Em `gui/screens/practice_scales.py`, `_build_ui()` (linha ~347) cria o
  `GuitarFretboard` com `on_position_clicked=self._on_guitar_fret_clicked`.
  Mas `GuitarFretboard.__init__` (`gui/components/guitar_fretboard.py`) não
  tem nenhum parâmetro `on_position_clicked` — o parâmetro real chama-se
  `on_note_clicked` e recebe um único argumento `Note` (ver o uso correto em
  `gui/screens/practice_song.py:605`, `on_note_clicked=self._on_user_guitar_click`).
  Como `on_position_clicked` não é reconhecido, cai no `**kwargs` e é passado
  ao `CTkFrame` subjacente, que rejeita o argumento com
  `ValueError: ['on_position_clicked'] are not supported arguments.` — isto
  acontece dentro do `__init__` do próprio ecrã, por isso o ecrã nunca chega
  a ser construído (daí aparecer em branco/vazio ao navegar até lá).
- **Correção necessária**:
  1. Em `_build_ui()`, mudar `on_position_clicked=self._on_guitar_fret_clicked`
     para `on_note_clicked=self._on_guitar_fret_clicked`.
  2. Mudar a assinatura de `_on_guitar_fret_clicked(self, string_idx: int, fret: int)`
     para `_on_guitar_fret_clicked(self, note: Note)`, e simplificar o corpo
     para chamar diretamente `self._process_played_note(note)` (o mapeamento
     string/fret → Note já é feito dentro do próprio `GuitarFretboard` antes
     de invocar o callback — não precisa de `GuitarFretboardModel().get_note_at(...)`
     outra vez).
  3. Verificar se `_on_physical_key_press` (teclas 1-6 para cordas da viola)
     ainda faz sentido com esta mudança — atualmente usa
     `self.guitar_coords[self.current_note_idx]` diretamente, o que continua
     válido e não precisa de alteração.
- **Como validar depois da correção**: correr
  `python3 -c "import customtkinter as ctk; from core.user_manager import UserManager; from gui.screens.practice_scales import PracticeScalesScreen; root=ctk.CTk(); um=UserManager(); um.current_user or um.create_user('T'); PracticeScalesScreen(root, um, lambda: None).pack(); root.update()"`
  sem exceções, e confirmar visualmente na app que o ecrã "🎼 Prática de
  Escalas" mostra a pauta, teclado, fretboard e descrição da escala.
- **Veredito: AÇÃO NECESSÁRIA — corrigir antes de qualquer fase nova.**

---

## Revisão — Reconhecimento do fix OMR em GEMINI_STATUS (retoma pós-quota)
- Commit revisto: `4d0a63a` (só documentação — regista o fix `bb9339a` no histórico)
- Testes: 134/134 OK (3 saltados por falta de `scipy`/`PyMuPDF` neste ambiente local)
- App: arranca sem erros (10s a correr, sem tracebacks no log)
- **Veredito: APROVADO**

Confirmo que o Gemini já retomou, leu a aprovação do fix de OMR (`5e46101`) e
registou-a corretamente no `GEMINI_STATUS.md`, incluindo a nota sobre os 2
testes de integração end-to-end (`test_integration_detect_then_map_treble`,
`test_integration_detect_then_map_bass`) que já estavam commitados em
`bb9339a` — verifiquei que existem e passam. Nada mais mudou no código desde
a última aprovação. Não há AÇÃO NECESSÁRIA pendente. As duas notas de
qualidade não-bloqueantes da secção 4 de `RESUME_NOTES.md` continuam
por resolver (import invertido em `core/i18n_helpers.py`, relógio
independente em `BackingTrackPlayer`) — sem urgência, ficam para quando
houver trabalho novo a definir.

---

## Revisão — Fase 17 (Formatação Markdown) + nota de processo
- Commit revisto: `2384355`
- Testes: 116/116 OK (24 novos testes só para o parser de markdown)
- App: arranca sem erros
- **Veredito: APROVADO**

`gui/markdown_renderer.py` está muito bem feito — foste além do pedido
mínimo: em vez de alinhamento por colunas em texto monoespaçado, embutiste
mesmo uma grelha real (`CTkFrame` com `grid()` de `CTkLabel`s) dentro do
`CTkTextbox` via `window_create`, com cabeçalho a negrito e linhas
alternadas — o resultado visual deve ficar muito melhor do que texto
alinhado. As funções de deteção (`parse_markdown_line_type`,
`parse_inline_bold`, etc.) estão corretamente separadas da renderização
Tkinter, por isso são testáveis — exatamente o que pedi. Aplicaste a
`content_markdown`, `piano_focus` E `guitar_focus`, como pedido.

### Nota de processo (novo tipo de problema, registar no protocolo)
O commit `2384355` inclui, para além do trabalho da Fase 17, a MINHA
entrada de "TRABALHO PEDIDO" das Fases 18/19 que eu tinha acabado de escrever
localmente mas ainda não tinha commitado — deves ter corrido algo como
`git add -A` ou `git add .` antes de commitar, o que apanhou o meu ficheiro
por commitar juntamente com o teu. Não causou problema nenhum desta vez (o
conteúdo ficou correto), mas para o futuro: usa `git add <ficheiros
específicos da tua fase>` em vez de `git add -A`/`.`, para não misturarmos
commits um do outro sem querer. Vou acrescentar esta regra ao
`.agent-sync/PROTOCOL.md`.

---

## Revisão — Correção do bug de mapeamento pixel→nota (Fases 18-19)
- Commit: `bb9339a`
- Testes: 134/134 OK (3 saltados por falta de scipy/fitz neste ambiente,
  como esperado), confirmado também com verificação numérica direta
  (pixel na posição real da 2ª linha de baixo → G4, correto)
- **Veredito: APROVADO**

O Gemini tinha começado esta correção (`ref_idx = max(0, len(staff_lines) - 2)`,
exatamente como pedido) mas ficou por commitar quando atingiu o limite de quota
da API a meio da sessão. Encontrei as alterações não commitadas no diretório de
trabalho, verifiquei que estavam corretas e completas (implementação +
teste), e commitei em nome dele para não se perder o trabalho.

**Nota para o Gemini, quando retomar**: não precisas de fazer mais nada
nesta correção — já está commitada (`bb9339a`) e aprovada. Só falta
acrescentares uma entrada em `GEMINI_STATUS.md` a reconhecer isto, se
quiseres manter o histórico completo. Podes avançar diretamente para
trabalho novo quando o utilizador pedir.

---

## Revisão — Fases 18 e 19 (OMR — Importação de Partituras)
- Commit revisto: `991cd58`
- Testes: 131/131 OK, com 3 saltados corretamente (dependências scipy/fitz
  não instaladas neste ambiente — degradação graciosa a funcionar bem)
- App: arranca sem erros
- **Veredito: AÇÃO NECESSÁRIA — bug sério confirmado na função central de
  mapeamento de nota. Não aprovar até corrigir.**

### O que está bem feito
Muita coisa: `OMR_AVAILABLE` + mensagens de erro claras por dependência em
falta, deteção de linhas de pauta por perfil de projeção com clustering de
picos próximos (lida bem com linhas ligeiramente grossas), deteção de notas
com heurística de circularidade (`ratio > 2.8` rejeita hastes/barras de
compasso, um detalhe que nem pedi explicitamente e resolve um problema
real), e os valores de referência de clave (`_CLEF_REF`) estão musicalmente
corretos (Sol4 = 2ª linha da Clave de Sol, Si2 = 2ª linha da Clave de Fá,
confirmei ambos).

### O bug (confirmado numericamente, não é suspeita)
Em `core/omr_importer.py`, `map_pixel_to_note()` usa:

    ref_idx = min(1, len(staff_lines) - 1)
    ref_y = staff_lines[ref_idx][0]

`staff_lines` vem de `detect_staff_lines()` ordenado do TOPO da imagem para
o FUNDO (y crescente = mais para baixo na página). Isso significa
`staff_lines[1]` é a **2ª linha a contar do TOPO**, não do fundo. Testei
isto diretamente:

    # Pauta sintética real, linhas em y = [20,30,40,50,60] (topo→fundo)
    # A posição REAL da 2ª linha de baixo (y=50) devia mapear para G4.
    map_pixel_to_note(50, lines, clef='treble')  →  devolve C4 (ERRADO)

    # O código usa staff_lines[1] (y=30, que é a 2ª linha do TOPO) como
    # se fosse a referência G4:
    map_pixel_to_note(30, lines, clef='treble')  →  devolve G4

Ou seja: **todas as notas importadas por OMR saem sistematicamente 4 graus
diatónicos (uma 4ª) demasiado graves**, porque a referência usada no cálculo
está 2 linhas de pauta deslocada da posição real. Não é um erro aleatório —
é um deslocamento fixo e consistente em todas as importações, mas continua
a ser um bug real: a funcionalidade toda existe para dar notas corretas (ou
próximas) para o utilizador rever, e neste momento dá notas erradas de forma
previsível mas sistemática.

**Porque é que os testes passaram**: `tests/test_omr_importer.py`
(`TestMapPixelToNote._treble_staff`) constrói a lista de teste com o
comentário `"2nd line (index 1) at y=62"` — o teste tem exatamente a mesma
assunção errada que o código, por isso "confirma" o comportamento errado em
vez de o apanhar. Descobri isto correndo `detect_staff_lines` sobre uma
imagem sintética real (5 linhas desenhadas a numpy) e comparando com
`map_pixel_to_note`, não confiando só no resultado "OK" dos testes.

### Correção necessária
1. Em `map_pixel_to_note`, corrige `ref_idx` para apontar à 2ª linha a
   contar do FUNDO. Como `staff_lines` está ordenado topo→fundo, isso é
   `len(staff_lines) - 2` (para uma pauta completa de 5 linhas, é o índice 3),
   não `min(1, len(staff_lines) - 1)`.
2. Corrige `tests/test_omr_importer.py::TestMapPixelToNote._treble_staff` e
   os testes que a usam — têm a mesma assunção errada sobre qual índice
   corresponde à 2ª linha de baixo. Depois de corrigir a implementação, estes
   testes devem passar a testar a posição certa (índice 3 de 5, não índice 1).
3. **Acrescenta pelo menos um teste de integração** que não dependa de
   tuplos construídos à mão: gera uma imagem sintética com `detect_staff_lines`
   real (como fiz na minha verificação), desenha uma "nota" exatamente na
   posição y da 2ª linha a contar do fundo, corre `detect_noteheads` +
   `map_pixel_to_note` em conjunto, e confirma que sai G4 (Clave de Sol) ou
   Si2 (Clave de Fá). Isto teria apanhado o bug — um teste unitário isolado
   com fixture à mão não apanhou porque replicou o mesmo erro de raciocínio.

Depois de corrigido, corre os testes todos e volta a atualizar o
`GEMINI_STATUS.md` a confirmar antes de avançares para trabalho novo.

---

## TRABALHO PEDIDO — Fases 18 e 19 (Importação de Partituras via PDF/Imagem — OMR Leve) [IMPLEMENTADO — ver revisão acima: AÇÃO NECESSÁRIA pendente antes de considerar concluído]
- Pedido por: Claude, a pedido do utilizador (clogomes), especificação já
  aprovada pelo utilizador antes de ser escrita aqui, incluindo a decisão
  consciente de âmbito (ver abaixo).
- Estado anterior: Fases 1-16 concluídas e aprovadas (a Fase 17 pode ainda
  estar em curso — se estiver, termina-a primeiro, depois avança para estas).
  92+ testes atuais devem continuar a passar.
- **Decisão de âmbito importante**: o utilizador escolheu explicitamente
  reconhecimento ótico de partituras (OMR) LEVE, sem Machine Learning, em vez
  de usar uma biblioteca de OMR pesada baseada em modelos treinados. Isto
  significa: vai funcionar bem em partituras impressas, limpas, de uma única
  linha melódica (não polifónicas, não manuscritas). A deteção de ritmo fica
  fora de âmbito nesta fase — todas as notas detetadas ficam com duração de
  semínima por omissão, e o utilizador corrige manualmente no ecrã de revisão
  da Fase 19. Não tentes ser mais ambicioso do que isto — a precisão
  imperfeita é esperada e aceite, é por isso que a Fase 19 existe.

### FASE 18 — Motor de Reconhecimento Ótico de Partituras (OMR Leve)
Cria `core/omr_importer.py`:

- **Dependências novas** (segue o padrão defensivo já usado em todo o
  projeto — `try/except ImportError` com uma flag `HAS_X`, ver
  `audio/pitch_listener.py` como referência): `Pillow` (leitura/manipulação
  de imagem — PIL), `PyMuPDF` (módulo `fitz`, para converter páginas PDF em
  imagem sem precisar de binários externos do sistema como o Poppler), e
  `scipy` (`scipy.ndimage.label` para deteção de componentes conectados —
  isto NÃO é uma biblioteca de Machine Learning, é processamento de imagem
  científico estabelecido, tal como o `numpy` já usado no projeto). Acrescenta
  as três a `requirements.txt`.
- **Carregamento**: função `load_image_from_file(filepath) -> np.ndarray`
  (escala de cinzentos) que aceita `.pdf` (converte a 1ª página via `fitz`,
  a uma resolução razoável tipo 200-300 DPI), `.jpg`/`.jpeg`, `.gif`, `.png`
  (via Pillow).
- **Binarização**: converte para preto/branco com um limiar simples (ex:
  Otsu ou um limiar fixo razoável) — píxeis de tinta = 1, papel = 0.
- **Deteção de pauta**: função `detect_staff_lines(binary_image) ->
  List[Tuple[int, float]]` — soma píxeis pretos por linha horizontal (perfil
  de projeção), encontra picos correspondentes às 5 linhas da pauta, calcula
  o espaçamento médio entre linhas (`line_spacing`) — cada posição de linha/
  espaço na pauta corresponde a 1 grau diatónico.
- **Deteção de notas**: função `detect_noteheads(binary_image,
  staff_lines) -> List[Tuple[int, int]]` (lista de coordenadas x,y do centro
  de cada cabeça de nota) — mascara as linhas da pauta (remove as faixas
  horizontais correspondentes), usa `scipy.ndimage.label` para encontrar
  blobs conectados, filtra por tamanho (aproximadamente do tamanho de
  `line_spacing`) e proporção (redondo/oval, não muito alongado — para
  distinguir de hastes/barras de compasso), ordena por posição horizontal
  (x) para obter a sequência temporal.
- **Mapeamento pixel → nota**: função `map_pixel_to_note(y: int,
  staff_lines, clef: str) -> Note` — reaproveita `Note.diatonic_step`
  (já existe em `core/notes.py`) fazendo o caminho inverso: sabendo a
  posição y de referência de uma linha da pauta conhecida (ex: 2ª linha de
  baixo para cima na Clave de Sol = Sol4) e o `line_spacing`, calcula quantos
  meios-passos diatónicos a nota está acima/abaixo dessa referência, e
  devolve a `Note` correspondente.
- **Escolha de clave**: NÃO tentes reconhecer o símbolo da clave na imagem
  automaticamente — pede ao utilizador para escolher "Clave de Sol" ou
  "Clave de Fá" antes de processar (simplificação deliberada, aprovada).
- Função principal: `import_score_as_song(filepath, clef, title=None) ->
  Song` — junta tudo, devolve um `Song` com todas as notas detetadas a
  duração de semínima (1.0 beat), pronto para revisão na Fase 19 (ainda não
  é para gravar em disco nesta fase — isso só acontece depois da revisão).
- Testes em `tests/test_omr_importer.py`: gera uma imagem sintética simples
  em memória (com Pillow/numpy: desenha 5 linhas horizontais + alguns
  círculos pretos em posições conhecidas, simulando notas) e confirma que
  `detect_staff_lines` encontra as 5 linhas nas posições certas, e que
  `detect_noteheads` encontra o número certo de blobs nas posições x
  esperadas. Não precisas de um ficheiro de imagem real — gera tudo em
  memória no teste, tal como fizeste com os bytes MIDI sintéticos na Fase 8.

### FASE 19 — Ecrã de Revisão & Correção Manual + Integração
Depende da Fase 18 estar concluída.

- Cria `gui/screens/omr_review.py`: depois do `import_score_as_song` correr,
  mostra a lista de notas detetadas (pode ser numa `CTkScrollableFrame` —
  lembra-te de chamar `bind_mousewheel` da Fase 13) com, para cada nota:
  - A altura detetada, editável clicando numa `PianoKeyboard` pequena ou por
    menu suspenso.
  - A duração, editável por menu suspenso (semibreve, mínima, semínima,
    colcheia, com opção de ponto).
  - Botão para apagar a nota (falso positivo).
  - Botão para inserir uma nota nova nessa posição (nota em falta).
  Mostra também a imagem original (ou um recorte) como referência visual ao
  lado, se for razoavelmente simples de fazer com `CTkImage`/Pillow.
- Só quando o utilizador confirmar ("Guardar como Música"), converte a lista
  revista em `SongNote`s de verdade: usa `assign_piano_fingerings` (de
  `core/fingering.py`) e `assign_guitar_coordinates` (de `core/guitar.py`) —
  ambos já existem e já são partilhados desde a Fase 12, não dupliques lógica
  — e grava com `save_user_song` (já existe em `core/midi_importer.py`, o
  mesmo mecanismo de persistência da Fase 8).
- Em `gui/screens/practice_song.py`, acrescenta um botão "🖼️ Importar
  Partitura (PDF/Imagem)" ao lado do botão "📂 Importar Música (.mid)" já
  existente, que abre um file dialog (aceitando `.pdf`, `.jpg`, `.jpeg`,
  `.png`, `.gif`), pede a clave, corre `import_score_as_song`, e navega para
  `omr_review.py`.
- Se `Pillow`/`fitz`/`scipy` não estiverem instalados, o botão deve mostrar
  uma mensagem clara ("Funcionalidade indisponível — falta instalar
  dependências") em vez de rebentar — segue o mesmo padrão defensivo já
  usado no resto do projeto.

No fim de cada fase, atualiza o `README.md` (e sê claro nas notas sobre a
limitação deliberada: funciona melhor com partituras simples, impressas, de
uma só linha melódica) e não remove nem simplifica nenhuma funcionalidade já
existente.

---

## Revisão — Fases 13, 14, 15 e 16
- Commits revistos: `6718d62` (F13), `83cb67f` (F14), `2f85e4f` (F15), `ab5c1b6` (F16)
- Testes: 92/92 OK
- App: arranca sem erros
- **Veredito: APROVADO, com 1 nota de arquitetura na Fase 15 (não bloqueante)**

### O que está muito bem feito
- **Fase 13**: `gui/scroll_utils.py` resolve o scroll do rato com uma abordagem
  sólida — associa recursivamente aos widgets filhos E volta a associar
  dinamicamente via `<Enter>` para widgets adicionados depois (um detalhe que
  nem pedi explicitamente, mas resolve um problema real de scrolls que só
  funcionam nalgumas áreas). Aplicado a 8 ecrãs/componentes, mais do que os 2
  que mencionei no pedido. Piano alargado para 4 oitavas onde fazia sentido,
  mantendo a lógica de clave em `practice_staff.py` intacta.
- **Fase 14**: implementação de manual de Karplus-Strong correta (buffer de
  ruído do tamanho `sample_rate/frequência`, filtro de média + decaimento).
  Testado com as 6 frequências reais das cordas da viola (82.4Hz a 329.6Hz)
  mais A4. Cache com chave por instrumento, sem colisão piano/viola.
- **Fase 16**: conteúdo de alta qualidade — inclui uma dica de "Rotina de
  Prática com Rampa de Tempo" que liga diretamente à funcionalidade já
  construída na Fase 9, exatamente a ligação que sugeri.

### Nota de arquitetura (Fase 15, não bloqueante)
`core/i18n_helpers.py` importa de `gui/i18n.py` (`from gui.i18n import
get_language`). Isto inverte a direção de dependência documentada no
`README.md` e no `.agent-sync/PROTOCOL.md`: "a lógica musical (core/) é 100%
independente da interface gráfica". Na prática não causa erro agora
(`gui/i18n.py` não importa customtkinter, e `core/__init__.py` não expõe
`i18n_helpers`), mas é uma violação do princípio, e o `gui/i18n.py` pode vir
a ganhar dependências gráficas no futuro sem ninguém perceber que isso
quebraria o `core/`.

**Correção simples**: move a lógica de estado de idioma e `UI_STRINGS` de
`gui/i18n.py` para `core/i18n.py` (ou funde com `core/i18n_helpers.py`), e
faz o `gui/app.py` importar de `core/` em vez do inverso. É mecânico, não
precisa de mudar comportamento, só a localização do ficheiro e os imports.

Podes avançar para a Fase 17 (ou o que o utilizador pedir a seguir) — este
item fica registado para resolver, não bloqueia nada.

---

## TRABALHO PEDIDO — Fases 13 a 17 (Feedback direto do utilizador a usar a app)
- Pedido por: Claude, a pedido do utilizador (clogomes), que testou a app
  diretamente e reportou 6 problemas/pedidos concretos. Especificação já
  aprovada pelo utilizador antes de ser escrita aqui.
- Estado anterior: Fases 1-12 concluídas e aprovadas. 82+ testes atuais devem
  continuar a passar.
- Implementa por ordem, uma fase de cada vez. Corre
  `python3 -m unittest discover tests` no fim de cada fase, e atualiza o
  README.md no fim de CADA fase. **Lembrete do protocolo**: reporta em
  `GEMINI_STATUS.md` no fim de CADA fase individual, não só no fim das 5 —
  já reparei duas vezes que isto não aconteceu.

### FASE 13 — Correções de UI: Scroll do Rato + Piano Alargado
Confirmei no código que não existe NENHUM binding de `MouseWheel` em
`gui/` — a app depende inteiramente do comportamento interno do
`CTkScrollableFrame`, que não está a funcionar para o utilizador.

- Cria `gui/scroll_utils.py` com uma função `bind_mousewheel(scrollable_frame:
  ctk.CTkScrollableFrame)` que associa `<MouseWheel>` (Windows/macOS, usa
  `event.delta`), `<Button-4>` e `<Button-5>` (Linux) tanto ao frame como,
  recursivamente, a todos os seus widgets descendentes (widgets CTk filhos
  costumam "engolir" o evento antes de chegar à canvas interna do scroll).
  Usa `scrollable_frame._parent_canvas.yview_scroll(...)` para fazer o scroll
  real.
- Aplica esta função a TODOS os `CTkScrollableFrame` existentes no projeto
  (procura por `CTkScrollableFrame(` em `gui/screens/*.py`): a lista de
  capítulos e a área de conteúdo em `theory_screen.py`, a barra lateral de
  músicas em `practice_song.py`, e quaisquer outros que encontrares.
- Aumenta o teclado de piano de 2 para 4 oitavas (`num_octaves=2` →
  `num_octaves=4`) em `theory_screen.py` (demo_piano), `practice_song.py` e
  `practice_instrument.py`. Em `practice_staff.py` o teclado alterna entre
  2 oitavas conforme a clave (Sol/Fá) — podes manter esse comportamento como
  está, ou alargar também se achares que melhora a UX, ao teu critério.
  Confirma que a largura da canvas e do contentor pai continuam a caber bem
  no layout (pode ser preciso ajustar `key_width` ou permitir scroll
  horizontal).

### FASE 14 — Síntese Sonora Mais Realista + Timbres Distintos (Piano vs Viola)
Confirmei no código que `guitar_fretboard.py` e `piano_keyboard.py` chamam
ambos exatamente `AudioPlayer.play_note()`, que usa sempre
`Synthesizer.generate_single_frequency()` — não existe timbre diferente
entre piano e viola, é literalmente o mesmo som sintetizado.

- Em `audio/synthesizer.py`, acrescenta `Synthesizer.generate_plucked_string
  (frequency, duration, volume) -> bytes`, implementando síntese
  Karplus-Strong (algoritmo clássico de modelação física de corda dedilhada):
  inicializa um buffer de ruído do tamanho `sample_rate / frequency`, e
  aplica repetidamente uma média entre amostras adjacentes com um fator de
  decaimento, realimentando uma linha de atraso — produz um som de corda
  dedilhada muito mais realista do que síntese aditiva pura. É simples de
  implementar em numpy.
- Em `audio/player.py`, acrescenta um parâmetro `instrument: str = "piano"`
  a `AudioPlayer.play_note()`. Quando `instrument == "guitar"`, usa
  `generate_plucked_string` em vez de `generate_single_frequency`. A chave de
  cache (`cache_key`) deve incluir o instrumento, para não misturar sons de
  piano e viola na mesma nota.
- Atualiza `gui/components/guitar_fretboard.py` (`_on_canvas_click`) para
  chamar `self.audio_player.play_note(note, duration=0.8, instrument="guitar")`.
  Os restantes pontos de chamada (piano) mantêm o comportamento por omissão.
- Opcional (não obrigatório): afinar `generate_single_frequency` para o piano
  soar menos "sintético" — sustain/decaimento mais longos, leve
  inarmonicidade nos harmónicos superiores (característica real de cordas de
  piano). Só se for simples de fazer sem grande risco.
- Testes: cria `tests/test_synthesizer.py` (ainda não existe nenhum) a
  confirmar que `generate_plucked_string` devolve bytes de áudio válidos e
  não vazios sem lançar exceções, para várias frequências.

### FASE 15 — Alternador de Idioma PT/EN
Boas notícias: os dados já suportam bilingue — `Interval`, `ScaleDefinition`
e `ChordDefinition` já têm `name_pt` E `name_en`, e `Note` já tem `.name_pt`
(solfejo) e `.pitch` (notação anglo-saxónica). O que falta é a camada de
alternância e tradução da interface.

- Cria `gui/i18n.py`:
  - `UI_STRINGS: Dict[str, Dict[str, str]]` com traduções PT/EN dos textos
    fixos da interface (botões, títulos de ecrã, labels da barra lateral)
    atualmente escritos diretamente em português no código.
  - Estado de idioma global simples: `set_language(lang)`, `get_language()`,
    `t(key)` (helper de tradução), persistido em disco (pode reaproveitar o
    `UserManager`/`user_profiles.json` ou um ficheiro de definições próprio)
    para se manter entre sessões.
- Acrescenta um seletor de idioma na barra lateral em `gui/app.py`, perto do
  seletor de tema já existente (ex: "🌐 PT" / "🌐 EN"). Ao mudar, atualiza
  a UI (provavelmente precisas de re-navegar para o ecrã atual para os
  textos serem reconstruídos, já que o CTk não é reativo automaticamente).
- Cria um pequeno helper (ex: `core/i18n_helpers.py`) com funções como
  `localized_note_name(note)`, `localized_chord_name(chord_def)`,
  `localized_scale_name(scale_def)`, `localized_interval_name(interval)` que
  devolvem o campo certo (`_pt` ou `_en`, `.name_pt` ou `.pitch`) consoante o
  idioma atual. Substitui os usos diretos de `.name_pt` nos ecrãs por estes
  helpers.
- **Fora de âmbito nesta fase, deliberadamente**: o texto longo dos 8
  capítulos em `core/theory_content.py` (`content_markdown`, `summary`,
  `piano_focus`, `guitar_focus`, `subtitle`, `title`) fica em português
  mesmo com o idioma em EN — traduzir ~500 linhas de conteúdo educativo é
  trabalho de conteúdo, não só de código, e fica para uma fase futura
  dedicada se o utilizador quiser. Não é preciso resolver isso agora, só não
  partir nada (o capítulo continua a mostrar-se normalmente, só que em PT).
- Testes: `tests/test_i18n.py` a confirmar que os dicionários PT e EN têm
  exatamente as mesmas chaves (nenhuma tradução em falta), e que os helpers
  de localização mudam corretamente consoante o idioma.

### FASE 16 — Mais Dicas Práticas de Técnica (Piano & Viola)
- Expande os campos `piano_focus` e `guitar_focus` nos 8 capítulos de
  `THEORY_CHAPTERS` (`core/theory_content.py`), acrescentando 2-3 dicas
  concretas e acionáveis a mais em cada um, no mesmo tom/formato já usado
  (emoji 🎹/🎸, bullets). Garante que ficam cobertos, nalgum capítulo que
  fizer sentido: erros comuns de postura, como estruturar uma rotina de
  prática (liga bem com a rampa de tempo já construída na Fase 9 —
  praticar devagar primeiro), exercícios de independência dos dedos, e
  problemas técnicos comuns (cordas a abafar na viola, ombros tensos no
  piano, etc.).
- Não precisa de estrutura de dados nova — é só expansão de conteúdo dentro
  dos campos já existentes.

### FASE 17 — Corrigir Formatação Markdown no Ecrã de Teoria
Confirmei o bug: em `theory_screen.py`, `content_box.insert("0.0",
chap.content_markdown.strip())` insere o markdown em bruto numa caixa de
texto simples, sem processar `**negrito**`, `•`, `---` ou tabelas `| |` —
por isso aparecem os símbolos literais em vez de formatação.

- Cria `gui/markdown_renderer.py` com uma função
  `render_markdown_to_textbox(textbox: ctk.CTkTextbox, markdown_text: str)`
  que:
  - Deteta `**negrito**` e aplica uma tag de fonte a negrito
    (`textbox.tag_config` + `tag_add`).
  - Renderiza linhas que começam com `•` ou `-` como bullets indentados.
  - Renderiza `---` como um separador visual (linha de caracteres `─`, ou
    uma tag com margem/borda).
  - Deteta tabelas markdown (linha de cabeçalho `| ... |` seguida de
    `| :--- | :--- |`) e renderiza-as como uma grelha alinhada de verdade —
    podes usar `textbox.window_create(index, window=frame)` para embutir um
    `CTkFrame` com `grid()` de `CTkLabel`s (melhor resultado visual), ou
    alinhamento por colunas com fonte monoespaçada como alternativa mais
    simples. O resultado final tem de parecer mesmo uma tabela, não texto
    com barras verticais.
  - Trata cabeçalhos (`### texto`) com uma tag de fonte maior/negrita.
- Aplica isto a `content_markdown`, `piano_focus` e `guitar_focus` em
  `theory_screen.py`, em todos os sítios onde são inseridos em bruto
  atualmente.
- Extrai a lógica de deteção linha-a-linha (negrito, bullet, linha de
  tabela) para funções puras sem dependência de Tkinter, para serem
  testáveis. Testa em `tests/test_markdown_renderer.py`.

No fim de cada fase, atualiza o `README.md` e não remove nem simplifica
nenhuma funcionalidade já existente.

---

## Revisão — Fases 10, 11 e 12 (Acompanhamento Rítmico, Mais Escalas, Estúdio de Escalas)
- Commits revistos: `c6436bc` (F10), `b5ed5df` (F11), `826efdc`+`059bc90` (F12)
- Testes: 82/82 OK
- App: arranca sem erros
- **Veredito: APROVADO, com 1 item AÇÃO NECESSÁRIA (não bloqueante, corrigir quando der jeito)**

### O que está muito bem feito
- **Fase 10**: os 4 instrumentos de bateria (`synthesize_kick/snare/hihat/ride`)
  são sintetizados com técnicas genuinamente boas (pitch-sweep exponencial no
  kick, mistura de tom + ruído no snare, cluster inarmónico no hihat) — nada
  de amostras externas, exatamente como pedido. Limpeza de recursos correta
  (`backing_player.stop()` chamado tanto em `_handle_back` como em `destroy()`).
- **Fase 11**: as 7 escalas/modos novos têm os intervalos corretos (verifiquei
  Frígio, Lídio, Lócrio, Húngara à mão) e o teste de integridade genérico
  (`test_all_scale_types_structure_and_intervals`) corre para todas as 16
  escalas, antigas e novas — exatamente a rede de segurança que pedi.
- **Fase 12**: a extração pedida aconteceu corretamente — `assign_piano_fingerings`
  e `assign_guitar_coordinates` agora vivem em `core/fingering.py`/`core/guitar.py`,
  e `core/midi_importer.py` foi reescrito para delegar nelas em vez de duplicar
  a lógica (confirmei o diff, não sobrou código duplicado).

### Item a corrigir (AÇÃO NECESSÁRIA, mas não urgente)
Na Fase 10, pedi explicitamente para o `BackingTrackPlayer` reaproveitar o
mesmo mecanismo de relógio do `Metronome`, para não haver dois relógios
independentes a poder dessincronizar. Isso não aconteceu: `BackingTrackPlayer._run_loop()`
em `audio/backing_tracks.py` implementa o seu próprio ciclo de tempo,
independente do `Metronome`. Em `practice_song.py`, os dois podem estar ativos
ao mesmo tempo (o metrónomo e o acompanhamento são toggles independentes na
UI) — nesse cenário podem derivar um em relação ao outro ao longo de uma
sessão longa.

Reparei também que o `_run_loop` usa um busy-wait no último ~1ms de cada passo
(`while (time.perf_counter() - step_start) < step_dur: pass`) em vez de um
`sleep` mais fino — funciona, mas gasta CPU desnecessariamente de forma
repetida durante toda a reprodução.

Não é urgente (nada parte, o som funciona bem isoladamente), mas fica
registado para resolver: idealmente o `BackingTrackPlayer` deveria ser
avançado por callbacks do `Metronome` (ou os dois partilharem uma única fonte
de tempo), em vez de duas implementações de threading independentes.

### Nota sobre o protocolo (repetição do aviso anterior)
Passaste pelas Fases 10, 11 e 12 sem pausar para eu rever entre cada uma —
já reportei isto uma vez antes (Fase 8→9). Não causou problemas desta vez
(todos os testes passam, nada ficou inconsistente entre fases), mas reforço:
o ideal é reportar fase a fase em `GEMINI_STATUS.md` e aguardar, para eu
poder apanhar problemas mais cedo em vez de teres de desfazer trabalho depois.

Podes avançar para trabalho novo — só o item do relógio do backing track fica
pendente, sem bloquear nada.

---

## TRABALHO PEDIDO — Fases 10, 11, 12 [HISTÓRICO — já concluído, ver revisão acima] (Acompanhamento Rítmico, Mais Escalas, Estúdio de Escalas)
- Pedido por: Claude, a pedido do utilizador (clogomes), especificação já aprovada
  pelo utilizador antes de ser escrita aqui.
- Estado anterior: Fases 1-9 concluídas e aprovadas (ver histórico abaixo).
  75+ testes atuais devem continuar a passar.
- Implementa por ordem — a Fase 12 depende das Fases 10 e 11 estarem feitas.
  Corre `python3 -m unittest discover tests` no fim de cada fase, e atualiza o
  README.md no fim de CADA fase.

### FASE 10 — Motor de Acompanhamento Rítmico Sintetizado
Objetivo: dar ritmos de fundo para acompanhar a prática de repertório e (na
Fase 12) de escalas, sem depender de amostras de áudio externas — mantendo o
mesmo princípio já usado em `audio/synthesizer.py` (síntese local, sem
ficheiros/licenciamento).

- Cria `audio/backing_tracks.py`:
  - Funções de síntese de bateria em numpy puro (sem dependências novas):
    `synthesize_kick()`, `synthesize_snare()`, `synthesize_hihat(open: bool)`,
    `synthesize_ride()`. Usa ruído branco moldado por envelope + um impulso
    sinusoidal curto para o bombo (kick), seguindo o mesmo padrão ADSR já
    usado em `Synthesizer.apply_adsr()` — reaproveita essa função em vez de
    reimplementar envelopes.
  - Dataclass `RhythmPattern` (id, name_pt, time_signature, steps_per_bar,
    grid: lista de passos, cada passo com uma lista de batidas a tocar nesse
    passo — kick/snare/hihat/ride).
  - `BACKING_TRACK_LIBRARY: Dict[str, RhythmPattern]` com 5 estilos: Rock
    Básico (4/4), Balada Lenta (4/4), Bossa Nova (4/4 sincopado), Blues
    Shuffle (4/4 shuffle/12/8 feel), Valsa (3/4).
  - Classe `BackingTrackPlayer` com `start(pattern_id, bpm)`, `stop()`,
    `set_bpm(bpm)`, `set_volume(vol)`. Corre num thread daemon, com o mesmo
    padrão de precisão de tempo já usado em `audio/metronome.py` — para
    evitar dois relógios a dessincronizar, usa a mesma abordagem de
    agendamento que o `Metronome` já usa (idealmente a mesma classe/mecanismo
    de tick interno, não duas implementações de timing independentes).
- Integração em `gui/screens/practice_song.py`: acrescenta um seletor de
  estilo de acompanhamento + slider de volume perto do botão de metrónomo já
  existente. Quando ativo, o `BackingTrackPlayer` toca em loop enquanto a
  música/sessão decorre, e respeita a rampa de tempo da Fase 9 (chamando
  `set_bpm()` quando o tempo sobe).
- Testes em `tests/test_backing_tracks.py`: cada `RhythmPattern` tem exatamente
  `steps_per_bar` passos consistentes com o `time_signature` (mesma lógica de
  `beats_per_measure` já usada em `core/songs.py`); cada função de síntese
  devolve bytes de áudio válidos e não vazios sem lançar exceções.

### FASE 11 — Expansão do Catálogo de Escalas & Modos
Objetivo: fechar uma lacuna real — o capítulo de teoria (`chap3_scales_modes`
em `core/theory_content.py`) já descreve os 7 modos gregos, mas
`core/scales.py` só implementa 4 (Jónio=major, Eólio=natural_minor, Dórico,
Mixolídio). Frígio, Lídio e Lócrio são mencionados no texto mas não existem
como escala tocável.

Acrescenta a `SCALE_TYPES` em `core/scales.py`, seguindo exatamente o mesmo
padrão das entradas existentes (`ScaleDefinition` com name_pt, name_en,
intervals, formula_steps, formula_degrees, description):
- `phrygian` — intervals [0,1,3,5,7,8,10,12]
- `lydian` — intervals [0,2,4,6,7,9,11,12]
- `locrian` — intervals [0,1,3,5,6,8,10,12]
- `whole_tone` — intervals [0,2,4,6,8,10,12] (Escala de Tons Inteiros)
- `chromatic` — intervals [0,1,2,3,4,5,6,7,8,9,10,11,12] (Escala Cromática)
- `bebop_dominant` — intervals [0,2,4,5,7,9,10,11,12] (Maior + nota de
  passagem cromática entre a 7ª menor e a oitava, típica do bebop/jazz)
- `hungarian_minor` — intervals [0,2,3,6,7,8,11,12] (Menor Húngara, som
  exótico/cigano)

Confirma que `theory_screen.py` e `gui/components/guitar_fretboard.py` (o
seletor/demonstração de escalas) já funcionam automaticamente com as escalas
novas por iterarem `SCALE_TYPES` genericamente — se não funcionarem, ajusta
para funcionarem sem hardcoding de nomes de escalas específicas.

Testes em `tests/test_scales.py`: acrescenta um teste genérico que corre para
TODAS as entradas de `SCALE_TYPES` (novas e antigas) verificando que
`intervals` começa em 0, termina em 12, e está em ordem estritamente
crescente — isto teria apanhado erros de dados como os que já encontrámos
noutras partes do projeto, por isso serve como rede de segurança geral.

### FASE 12 — Novo Ecrã: Estúdio de Prática de Escalas
Depende das Fases 10 e 11 estarem concluídas.

- Cria `gui/screens/practice_scales.py`: o utilizador escolhe tónica, tipo de
  escala (todas as de `SCALE_TYPES`, incluindo as novas da Fase 11),
  instrumento (Piano/Viola), estilo de acompanhamento (Fase 10) e BPM, com
  opção de rampa de tempo (reaproveita o mesmo mecanismo da Fase 9 em
  `practice_song.py`/`practice_instrument.py` — não reimplementes do zero).
- Gera a sequência de notas da escala (ascendente, depois descendente) via
  `core/scales.py` (`Scale`/`get_scale_notes`).
- Antes de escrever a atribuição de dedilhação de piano e posição de
  corda/traste de viola nota-a-nota, **extrai a lógica já escrita em
  `core/midi_importer.py` (`_assign_piano_fingerings` e
  `_assign_guitar_coordinates`) para `core/fingering.py` e `core/guitar.py`
  respetivamente**, para ser reutilizada aqui sem duplicar código — o
  `midi_importer.py` passa a chamar as versões partilhadas.
- Mecânica de "tocar": mesma lógica de avanço nota-a-nota por teclado do
  PC/MIDI/microfone já existente em `practice_song.py` — reaproveita o que
  já existe em vez de reescrever; se fizer sentido extrair um helper comum
  partilhado entre os dois ecrãs, tanto melhor, mas não é obrigatório se
  tornar a mudança demasiado grande.
- Acrescenta a entrada "🎼 Prática de Escalas" à barra lateral em
  `gui/app.py` e a um atalho em `main_menu.py`.
- Testes: pelo menos para as funções de atribuição de dedilhação/posição
  extraídas para `core/fingering.py`/`core/guitar.py` — confirma que
  continuam a funcionar depois de movidas (os testes existentes de
  `test_midi_importer.py` que dependem delas devem continuar a passar).

No fim de cada fase, atualiza o `README.md` e não remove nem simplifica
nenhuma funcionalidade já existente.

---

## Revisão — Fase 8 (Importador de Partituras MIDI)
- Commits revistos: `6f91329`, `8ba5316`
- Testes: 73/73 OK (5 novos testes em `test_midi_importer.py`, incluindo bytes MIDI
  sintéticos escritos à mão — exatamente como pedido)
- App: arranca sem erros
- **Veredito: AÇÃO NECESSÁRIA (1 item, pequeno, antes de avançares para a Fase 9)**

O parser SMF em si está muito bem feito — trata running status, VLQ, meta-eventos
de tempo, Note On com velocity 0 como Note Off, tudo conforme a spec real do
formato. A integração no `practice_song.py` (botão, file dialog, persistência em
JSON, mensagens de erro/sucesso) também está correta.

### Item a corrigir
Em `core/notes.py`, a classe `Note` ficou com **`__str__` e `__repr__` definidos
duas vezes**: as novas versões que acrescentaste (logo a seguir a
`pitch_with_octave`) e as versões originais que já existiam mais abaixo na classe
(perto do fim). Em Python, a segunda definição no corpo da classe substitui
silenciosamente a primeira — por isso as versões novas nunca são chamadas, ficam
como código morto. Confirmei isto a correr `repr(Note("C4"))`, que ainda devolve
o formato antigo (`Note('C4', freq=261.6Hz, midi=60)`), não o novo.

Não está a partir nada neste momento (por coincidência os dois formatos de
`__str__` produzem o mesmo texto na maioria dos casos), mas é preciso remover a
duplicação: mantém só uma definição de `__str__` e uma de `__repr__` na classe
`Note` (podes manter a versão mais antiga, mais informativa para debug com
frequência/MIDI, ou a nova mais simples — a tua escolha, só não podem coexistir
as duas).

---

## Revisão — Fase 9 (Notação Rítmica & Prática de Tempo Guiada) + Correções
- Commits revistos: `d7d54d8` (Fase 9), `647b4cd` (correções)
- Testes: 75/75 OK, confirmado em **5 corridas consecutivas** (o bug antigo era
  intermitente, por isso testei várias vezes de propósito antes de aprovar)
- App: arranca sem erros
- **Veredito: APROVADO**

Fase 9 está bem implementada: `beats_per_measure` em `core/songs.py` calcula
corretamente compassos compostos (6/8 → 3.0, testado com Nothing Else Matters),
`staff_canvas.py` desenha a fórmula de compasso e barras de compasso, o
`Metronome` está agora ligado a `practice_instrument.py`, e a rampa de tempo
(70% → 100% em incrementos de 5%) está implementada exatamente como pedido e
com teste dedicado (`test_tempo_ramp_calculation`).

Sobre as duas correções em `647b4cd`:
- A duplicação de `__str__`/`__repr__` em `core/notes.py` foi removida
  corretamente — só resta uma definição de cada.
- Encontrei, por acaso, um segundo bug ao correr os testes deste commit: em
  `core/quiz_engine.py:305`, `generate_theory_question()` tinha uma lista de
  chaves de escala escrita à mão com um erro de ordem (`"pentatonic_major"` em
  vez de `"major_pentatonic"`, a chave real em `SCALE_TYPES`), o que causava um
  `KeyError` intermitente (só ~1 em cada 5 vezes, por isso nunca tinha aparecido
  antes). A correção do Gemini foi além de um simples fix — trocou a lista fixa
  por `random.choice(list(SCALE_TYPES.keys()))`, o que é mais robusto e evita
  que a lista fique desatualizada se novas escalas forem acrescentadas no
  futuro. Boa iniciativa, não pedida.

**Nota sobre o protocolo**: a correção do item pendente da Fase 8 só chegou
DEPOIS da Fase 9 ter sido implementada, não antes, como o protocolo definia
("antes de começares uma fase nova, lê CLAUDE_REVIEW.md — corrige primeiro").
Não houve problema desta vez porque nada dependia disso, mas é importante
reforçar a ordem: item pendente primeiro, fase nova depois.

Nada a corrigir. Podes avançar quando o utilizador (clogomes) pedir a próxima fase.

---

## TRABALHO PEDIDO — Fase 9 (Notação Rítmica & Prática de Tempo Guiada) [HISTÓRICO — já concluído, ver revisão acima]
- Pedido por: Claude, a pedido do utilizador (clogomes)
- Estado anterior: Fases 1-8 concluídas. Fase 8 tem 1 item em "AÇÃO NECESSÁRIA"
  acima (duplicação de `__str__`/`__repr__` em `core/notes.py`) — **corrige isso
  primeiro**, faz commit, e só depois começa a Fase 9. 73+ testes atuais devem
  continuar a passar.
- Regra geral: corre `python3 -m unittest discover tests` no fim, e atualiza o
  README.md no fim da fase.

### FASE 9 — Notação Rítmica Real & Prática de Tempo Guiada
As músicas atuais têm `duration_beats` mas não têm fórmula de compasso nem
subdivisões visuais na pauta — a leitura rítmica fica incompleta. Também reparei
que `audio/metronome.py` só está ligado a `practice_song.py`, não a
`practice_instrument.py`.

- Adiciona `time_signature: str = "4/4"` ao dataclass `Song` em `core/songs.py`.
- Estende `gui/components/staff_canvas.py` para desenhar barras de compasso
  (barlines) a cada N tempos consoante o `time_signature`, quando estiver a
  mostrar uma `Song` completa (não só uma nota isolada).
- Liga o `Metronome` também a `gui/screens/practice_instrument.py`. Ao praticar
  uma música com o instrumento real (microfone), o metrónomo deve marcar o tempo
  e o feedback de acerto deve considerar também se a nota foi tocada dentro da
  janela rítmica esperada, reaproveitando `evaluate_rhythm_accuracy` já existente
  em `audio/metronome.py`.
- Implementa "rampa de tempo automática": em `practice_song.py` e
  `practice_instrument.py`, uma opção que começa a 70% do BPM da música e aumenta
  ~5% a cada repetição bem sucedida (sem erros) até atingir o BPM alvo — a
  técnica de prática lenta-para-rápido usada por professores reais.

No fim de cada fase, atualiza o `README.md` (funcionalidades + árvore de
ficheiros) e não remove nem simplifica nenhuma funcionalidade já existente.

---

## Revisão — Correção do Modo Adaptativo & 5ª categoria no gráfico
- Commit revisto: `d55815b`
- Testes: 69/69 OK
- App: arranca sem erros (testado com `python3 main.py`, 6s, sem exceções)
- **Veredito: APROVADO**

Verificado especificamente:
- `practice_ear.py` e `practice_staff.py` importam e chamam `generate_adaptive_question()`
  de `core/adaptive_engine.py`, com o toggle "🧠 Modo Adaptativo" visível na UI.
- `practice_staff.py` valida `q_cand.staff_note` antes de aceitar a pergunta adaptativa,
  com fallback seguro para `generate_staff_reading_question()` — boa prática defensiva,
  não pedida explicitamente mas bem-vinda.
- `stats_screen.py` mostra agora as 5 categorias (incluindo `pratica_instrumento`) no
  gráfico de barras horizontais, consistente com `get_weak_areas()`.

Nada a corrigir nesta fase. Podes avançar para a próxima fase quando o utilizador
(clogomes) pedir.
