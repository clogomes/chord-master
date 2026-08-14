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
