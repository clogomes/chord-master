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

## TRABALHO PEDIDO — Fases 10, 11, 12 (Acompanhamento Rítmico, Mais Escalas, Estúdio de Escalas)
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
