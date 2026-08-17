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

## Revisão — Fase 44 (Grelha Multi-Compasso) APROVADA ✅ — AVANÇA PARA A FASE 45
- Commits revistos: `47ba74f`, `342a20c`
- Testes: 244/244 OK
- **Veredito: APROVADO**

**A limitação central está levantada** — já se compõe por compasso, sem
repetição forçada:
```
bombo só no passo 32 (compasso 3) de uma grelha de 64
→ 1 onset em 4.00 s   (antes: repetia em 0, 2, 4, 6 s)
```

**As duas salvaguardas que exigi estão ambas implementadas:**

1. **Compatibilidade com composições já gravadas** — carreguei um dicionário
   no formato antigo (grelha de 16 passos, `bars=4`):
   ```
   grelha após carregar: 64 passos (expandida)
   bombos: 0.0s, 2.0s, 4.0s, 6.0s  → soa exatamente como antes ✓
   ```
   Nada do que o utilizador gravou se perde nem muda de som.

2. **Aviso antes de descartar trabalho** — `compose_studio.py:670` usa
   `messagebox.askyesno` com uma mensagem explícita: *"Reduzir de N para M
   compassos irá descartar eventos nos compassos finais. Desejas continuar?"*
   Era o meu maior receio nesta fase e está tratado.

**Scroll horizontal com rótulos fixos** ✓ — resolveste com **dois canvas**
(`label_canvas` à esquerda, fixo; `step_canvas` com `xscrollcommand` ligado a
um `CTkScrollbar`). É exatamente a abordagem que sugeri; a referência de que
linha é o bombo não se perde ao navegar.

**Desempenho excelente**, mesmo no pior caso:
```
abrir (4 compassos)     : 158 ms | 154 widgets
mudar para  8 compassos :   5 ms | 128 passos
mudar para 16 compassos :   9 ms | 256 passos
```
256 passos × 5 linhas = 1280 retângulos redesenhados em **9 ms**. A opção pelos
retângulos em canvas continua a pagar-se.

**Avança para a Fase 45** — faixas de acordes de piano e viola na mesma grelha.
Lembretes: dois carris por baixo da percussão com divisor visível; cada acorde
como bloco de `start_beat` a `start_beat + duration_beats`; **mantém a lista de
acordes existente** e sincroniza as duas vistas; e deriva o rácio
tempo↔passo de `steps_per_bar` e do compasso, não o assumas fixo em 4.

---

## TRABALHO PEDIDO — Fases 44 a 46: Estúdio de Composição, segunda iteração
- Pedido do utilizador depois de experimentar o estúdio: *"adicionar uma faixa
  dos acordes de piano e de viola na mesma área da percussão para poder marcar
  os tempos melhor; mais compassos, com scroll horizontal se for preciso; e
  mais tipos de percussão."*
- **REGRA: uma fase de cada vez**, com o meu APROVADO escrito entre cada uma.
- Ordem deliberada: a grelha multi-compasso vem primeiro porque a faixa de
  acordes precisa de se alinhar a essa mesma linha temporal. Não troques.

### Descoberta importante — os "compassos" hoje não fazem o que parecem
Verifiquei por execução: o seletor oferece 2/4/8/16 compassos e o motor
respeita-os, **mas a grelha só guarda 16 passos (1 compasso) e o renderer
repete-o**:
```python
grid_step = rhythm.grid[step_idx % grid_len]     # composition_renderer.py:250
```
```
4 compassos com bombo no passo 0 → bombos em 0.0s, 2.0s, 4.0s, 6.0s
grelha guardada: 16 passos (não 64)
```
Ou seja, hoje só se compõe **um** compasso, repetido. É precisamente esta
limitação que a Fase 44 tem de levantar.

### FASE 44 — Grelha multi-compasso com scroll horizontal
1. **A grelha passa a cobrir a composição inteira**: `bars × steps_per_bar`
   passos (ex: 8 compassos × 16 = 128 passos), em vez de 16 fixos.
   - `RhythmTrack.grid` passa a ter esse comprimento.
   - Ao mudar o número de compassos: **aumentar preserva o que já existe** e
     acrescenta passos vazios; **diminuir** deve avisar antes de descartar
     conteúdo (não apagues trabalho do utilizador em silêncio).
   - **Compatibilidade**: composições já gravadas têm grelhas de 16 passos.
     Ao carregar, expande com `% len(grid)` (mantendo o comportamento atual de
     repetição) para que nada do que o utilizador já gravou se perca ou soe
     diferente. Testa isto explicitamente.
2. **Scroll horizontal no canvas** (`gui/components/step_grid.py`):
   - `canvas.config(scrollregion=...)` + `xscrollcommand` ligado a um
     `CTkScrollbar` horizontal.
   - **A coluna de rótulos dos instrumentos tem de ficar fixa** à esquerda
     (não deve deslizar com o conteúdo) — senão perde-se a referência de que
     linha é o bombo. Usa um segundo canvas estreito à esquerda, ou desenha os
     rótulos com coordenadas fixas ao viewport.
   - Marcações de compasso visíveis: linha vertical mais forte no início de
     cada compasso e um número ("1", "2", "3"…) por cima. Sem isso, 128 passos
     são indistinguíveis.
3. **Desempenho** — 128 passos × 5+ linhas = 640+ retângulos. Continua a usar
   `create_rectangle` (nunca widgets), e **desenha só o que está visível** se
   passar de ~1000 retângulos. Mede antes e depois: o ecrã está em 98 ms /
   150 widgets e não deve degradar-se muito.
4. O renderer já suporta multi-compasso (`total_steps = total_bars *
   steps_per_bar`); com a grelha do tamanho certo, o `%` deixa de ter efeito
   prático. Confirma que continua a funcionar para grelhas curtas e longas.

### FASE 45 — Faixa de acordes na mesma grelha temporal
Hoje os acordes vivem numa lista separada, sem relação visual com os tempos.
O utilizador quer vê-los **alinhados com a percussão**.
1. Acrescenta **duas linhas** ao mesmo canvas da grelha, por baixo da
   percussão e separadas por um divisor visível:
   - `🎹 Acordes (Piano)`
   - `🎸 Acordes (Viola)`
2. Cada `ChordEvent` desenha-se como um **bloco horizontal** que começa em
   `start_beat` e se estende por `duration_beats`, na linha do seu
   `instrument`. Mostra o nome do acorde dentro do bloco (ex: "Cmaj7") quando
   houver largura para isso.
3. **Interação mínima**: clicar num bloco seleciona o acorde (e atualiza o
   `PianoKeyboard`/`GuitarFretboard`, como já faz); clicar numa zona vazia da
   linha insere um acorde nesse tempo com a raiz/tipo atualmente escolhidos
   nos menus. Arrastar para mover/redimensionar é desejável mas **opcional** —
   se ficar complicado, deixa para depois e mantém a edição pelos menus.
4. Mantém a lista de acordes existente (é útil para editar duração e apagar) —
   **não a substituas**, sincroniza as duas vistas.
5. Alinhamento: `start_beat` é em tempos, a grelha é em passos. Com
   `steps_per_bar=16` em 4/4, 1 tempo = 4 passos. Não assumas esse rácio como
   fixo — deriva-o de `steps_per_bar` e do compasso.

### FASE 46 — Mais tipos de percussão
Hoje há **4 sintetizadores** (`synthesize_kick/snare/hihat/ride`) e **5 linhas**
(o hi-hat aberto e fechado partilham sintetizador).
1. Acrescenta sintetizadores em `audio/backing_tracks.py`, no mesmo estilo
   numpy dos existentes (100% locais, sem ficheiros):
   - **Tom grave / médio / agudo** — seno com varredura descendente de
     frequência + envelope curto; é essencialmente o `synthesize_kick` com
     frequências mais altas e menos varredura.
   - **Palmas (clap)** — 3-4 rajadas de ruído filtrado, separadas por ~10 ms,
     com uma cauda de reverberação curta. É o que dá o carácter de palma.
   - **Prato de ataque (crash)** — como o `ride` mas com cauda muito mais longa
     (2-4 s) e espectro mais denso.
   - **Aro (rim shot)** — clique muito curto e agudo, ruído filtrado em banda
     estreita.
   - **Caixa chinesa / cowbell** — dois quadrados desafinados, como já fazes
     no hi-hat mas com frequências mais baixas e afinadas.
2. Acrescenta as linhas correspondentes a `DRUM_ROWS` em `step_grid.py`, com
   ícone, nome PT/EN e cor distinta.
3. **Atenção ao comprimento do buffer**: um crash de 4 s no último passo tem de
   caber. O renderer já dimensiona pela cauda mais longa — confirma que
   continua correto com os sons novos (teste: crash no último passo, verificar
   que decai a zero e não é cortado).
4. **Cache**: os sons de percussão são sintetizados uma vez e reutilizados
   (`_get_synthesized_drum_sample`). Garante que os novos entram na mesma
   cache, senão o primeiro render fica lento.
5. Com mais linhas, a grelha fica mais alta — confirma que continua a caber ou
   que o scroll vertical funciona.

### Fora de âmbito (continua a não implementar)
Piano roll, gravação ao vivo, samples externos, exportação para ficheiro.

---

## Revisão — Fase 43 APROVADA ✅ — SÉRIE 40-43 FECHADA (Estúdio de Composição completo)
- Commits revistos: `aa22edb`, `c1b8a36`
- Testes: 243/243 OK
- **Veredito: APROVADO**

**Funcionalidade verificada por execução:**
```
adicionar acordes : 16/16 combinações OK (C, Bb, F#, Eb × major, min7, 7sus4, add9)
selecionar acorde :  4/4 OK
guitarra          : 25 posições destacadas ao selecionar um acorde ✓
apagar acorde     : 4 → 3 ✓
render ritmo+acordes: buffer (489510, 2), pico 0.765 (sem clipping) ✓
```
As raízes com bemol e sustenido funcionam todas — inclui `Bb` e `Eb`, que só
passaram a existir depois da correção de ortografia da Fase 31.

**A ligação pedagógica está lá**: ao selecionar um acorde, ele aparece
destacado no `PianoKeyboard` e no `GuitarFretboard` (25 posições CAGED na
guitarra). É isto que faz esta secção pertencer a uma app de ensino em vez de
ser uma imitação fraca de um DAW.

**Desempenho manteve-se bom** apesar de acrescentar a faixa de acordes e dois
visualizadores de instrumento:
```
39 ms /  71 widgets  (Fase 42)
98 ms / 150 widgets  (Fase 43)   ← ainda mais rápido que o ecrã de teoria (122 ms)
```

*Nota de método minha*: o meu primeiro teste acusou
`TypeError: '<=' not supported between int and ChordEvent` em `_select_chord`.
**Era erro meu** — o método recebe um índice (`_select_chord(index: int)`,
linha 599) e eu passei o objeto. Repeti corretamente e passa 4/4. O código
estava certo.

### Fecho da série 40-43 — Estúdio de Composição
O utilizador já pode: escolher um dos 12 ritmos como ponto de partida, editar a
grelha de percussão passo a passo, acrescentar uma progressão de acordes com 22
tipos e 17 tónicas, escolher piano ou viola para cada acorde, ver as posições no
teclado e no braço, ouvir tudo junto com tempo exato, e gravar/carregar
composições.

**O que fica de fora, por decisão de âmbito do utilizador** (versão útil
primeiro): piano roll, gravação ao vivo, samples externos reais, exportação
WAV. Tenho o desenho técnico completo dessas partes — incluindo o motor de
samples com números medidos de latência, memória e limites de pitch-shifting —
e escrevo a especificação se ele quiser continuar depois de experimentar isto.

**Não há nenhuma AÇÃO NECESSÁRIA pendente.** Aguarda instruções.

---

## Revisão — Fase 42 (Ecrã do Estúdio) APROVADA ✅ — AVANÇA PARA A FASE 43 (última)
- Commits revistos: `04c7641`, `ad78d4f`
- Testes: 241/241 OK
- **Veredito: APROVADO**

**Os três avisos de desempenho que dei foram todos seguidos** — e o resultado
fala por si. O estúdio é agora **o ecrã mais rápido da app**:
```
theory         : 122 ms |  222 widgets
glossary       : 124 ms |  596 widgets
compose_studio :  39 ms |   71 widgets   ← 3× mais rápido, 8× menos widgets
16 cliques na grelha: 0 ms
```
Concretamente:
- **Retângulos no canvas** (`step_grid.py:139 create_rectangle`), não um widget
  por célula. É por isso que são 71 widgets e não centenas.
- **`bind_mousewheel(..., recursive=False)`** — estendeste a função para
  aceitar o parâmetro em vez de a contornar. Boa solução.
- **Render em thread** com `self.after(0, ...)` para devolver o resultado ao
  Tk (`compose_studio.py:347`), e tratamento de erro em
  `_handle_playback_error` — a interface não congela durante o primeiro
  render de ~1,2 s, que era o meu receio.

**Funcionalidade verificada por execução:**
```
presets carregados sem erro : 5/5 (dos 12 ritmos existentes)
editar a grelha altera o modelo : 14 → 15 sons ✓
gravar/carregar             : composição recuperada com bpm=95, 2 compassos, 14 sons ✓
apagar                      : ✓
user_compositions.json no .gitignore : ✓
```
Os 12 ritmos existentes tornaram-se mesmo modelos editáveis, como estava
previsto — conteúdo útil desde o primeiro dia.

*Nota de método minha*: o meu teste de gravação pareceu bloquear, mas foi
porque `_save_composition` termina num `messagebox.showinfo` — um diálogo
modal que espera confirmação, e no meu script não havia ninguém para o fechar.
Comportamento correto, não bug. Confirmei a gravação por outro caminho, sem
interface.

**Avança para a Fase 43** — a última desta série: faixa de acordes de piano e
viola por cima do ritmo. Lembretes: usa os 22 tipos de `CHORD_TYPES` e as 17
tónicas (com bemóis); alterna o instrumento entre piano (aditiva) e viola
(Karplus-Strong); e **mostra o acorde selecionado no `PianoKeyboard` e no
`GuitarFretboard`** — é isso que faz esta secção pertencer a uma app de ensino
em vez de ser uma imitação fraca de um DAW.

---

## Revisão — Fase 41 (Motor de Render Offline) APROVADA ✅ — AVANÇA PARA A FASE 42
- Commits revistos: `4ea79a2`, `cdd29bf`
- Testes: 239/239 OK
- **Veredito: APROVADO** — e é a fase tecnicamente mais bem executada até agora.

**Sem pygame no módulo** ✓ — `audio/composition_renderer.py` não importa
pygame, portanto continua testável sem placa de som, como pedi.

**A precisão temporal é EXATA — o objetivo central desta fase.** Medi o
*onset* (início real do som) em vários andamentos e posições de grelha:
```
120 bpm passo  4 : onset=22050  esperado=22050  erro=0 amostras
120 bpm passo  8 : onset=44100  esperado=44100  erro=0 amostras
 60 bpm passo  4 : onset=44100  esperado=44100  erro=0 amostras
 90 bpm passo 12 : onset=88200  esperado=88200  erro=0 amostras
```
Zero amostras de desvio. Era exatamente para isto que valia a pena abandonar o
agendador em tempo real — o `BackingTrackPlayer` tem ~23 ms de jitter, isto
tem **0**.

**A cauda é respeitada** — um prato no último passo de um compasso de 2,00 s
gera um buffer de 3,50 s e decai a zero (amplitude 0.00000 nas últimas
amostras). Nada é cortado.

**O limitador funciona.** Testei o pior caso — 4 percussões em todos os 16
passos mais 8 acordes sobrepostos:
```
pico do buffer: 0.9036   (≤1.0, sem clipping)
amostras em ±1.0 (clip duro): 0
```
Usaste `tanh` como pedi; com `np.clip` isto teria distorcido audivelmente.

**A cache é o ganho decisivo:**
```
1º render (4 acordes de viola): 1247 ms
2º render (mesma composição)  :    1 ms
```
Mil vezes mais rápido. Sem ela, o Karplus-Strong (~35 ms por segundo de áudio)
tornaria o ciclo editar→ouvir insuportável. **Nota para a Fase 42**: 1247 ms no
primeiro render é tempo a mais para bloquear a interface — quando ligares o
botão de tocar, faz o render numa thread e marshalla o resultado com
`self.after(0, ...)`, como já fazes noutros ecrãs. Não deixes o Tk congelado.

**Piano e viola usam sínteses distintas** ✓ (perfis de RMS e pico diferentes,
consistentes com aditiva vs. Karplus-Strong).

### Correção a um alarme meu
O meu primeiro teste de precisão deu "FORA DO ALVO, 83 amostras". **Estava
errado**: eu media o *pico* de amplitude, e o pico de um bombo acontece ~2 ms
depois do início por causa da varredura de frequência. Ao medir o *onset*, o
erro é 0. O teu código estava certo; o meu método é que não estava.

**Avança para a Fase 42** (ecrã com grelha de ritmo). Lembretes: desenha
**retângulos no canvas**, não um widget por célula; **não** uses
`bind_mousewheel` recursivo; e faz o render em thread (ver nota acima).

---

## Revisão — Áudio do Glossário CORRIGIDO ✅ + Fase 40 APROVADA ✅ — AVANÇA PARA A FASE 41
- Commits revistos: `31cd17f`, `f68ca6e` (áudio), `c1935bf`, `37d43a2` (Fase 40)
- Testes: 235/235 OK

### ✅ Áudio do glossário — corrigido e verificado a fundo
```
play_note(Note(p), duration=0.65)   nos dois ficheiros (ecrã e modal)
```
Não me limitei a um termo — testei **os 129 termos com `hear_it`**:
```
termos com hear_it: 129
hear_it inválidos:    0    (todas as alturas construíveis e reproduzíveis)
_play_term_audio() no ecrã real: OK, sem exceção
```
**A conversão defensiva em `AudioPlayer.play_note` foi a decisão certa** —
aceitar uma string e converter mata a classe de bug que apareceu 3 vezes
(ecrã de técnica, ecrã de glossário, modal de glossário). Vale mais do que
qualquer teste que se escrevesse para isto.

**Debounce a 130 ms**, dentro da faixa que sugeri (120-150). Com os 9-41 ms
que filtrar custa agora, a resposta deve sentir-se imediata.

### ✅ Fase 40 (Modelo de dados) — APROVADA
Verifiquei por execução, não pelos testes:
```
ida-e-volta JSON      : bpm=120, 1 acorde, schema_version=1  ✓
dict mínimo {id,title}: carrega com defaults (bpm=100)       ✓  ← compatibilidade
guardar/carregar      : OK                                   ✓
RhythmTrack.from_pattern: 12/12 padrões convertidos          ✓
```
Os três pontos que mais me interessavam estão certos:
1. **`schema_version` desde o início** — não repetiste o erro do
   `user_songs.json`, que não tem versão nenhuma.
2. **Tolerância a campos em falta** — um dicionário com só `id` e `title`
   carrega com valores por omissão em vez de rebentar. É isto que permite
   evoluir o formato sem partir ficheiros de utilizadores.
3. **Os 12 ritmos existentes convertem-se todos** via `RhythmTrack.from_pattern`,
   com `grid` e `steps_per_bar` preservados — o conteúdo grátis do primeiro dia
   está garantido.

O ficheiro `user_compositions.json` já está no `.gitignore` desde a Fase 33,
por isso os dados do utilizador não vão parar ao repositório público.

**Avança para a Fase 41** (motor de render offline). Lembretes que valem a
pena: **não importes pygame** nesse módulo (mantém-no testável sem placa de
som), **cache dos arrays float32** por causa do `generate_plucked_string`
(~35 ms por segundo de áudio, é o único ponto lento do stack), dimensiona o
buffer para incluir a **cauda** do último som, e usa limitador suave
(`np.tanh`) em vez de `np.clip`.

---

## TRABALHO PEDIDO — Fases 40 a 43: Estúdio de Composição (versão útil)
- Pedido por clogomes há já algum tempo; a especificação atrasou-se do meu
  lado. Âmbito escolhido pelo utilizador: **versão útil primeiro** — grelha de
  ritmo editável + progressões de acordes para piano e viola. O sequenciador
  completo (piano roll, samples reais, exportação) fica para depois, se ele
  quiser continuar.
- **Corrige primeiro a AÇÃO NECESSÁRIA acima** (botões de som do glossário).
- **REGRA: uma fase de cada vez**, com o meu APROVADO escrito entre cada uma.

### Contexto técnico — o que já existe e deves reutilizar
Não construas nada disto de raiz:
- `audio/backing_tracks.py` — `RhythmPattern` com `grid: List[List[str]]` de 16
  passos e os sons `synthesize_kick/snare/hihat/ride`. **Os 12 padrões de
  `BACKING_TRACK_LIBRARY` devem tornar-se modelos iniciais editáveis** — é
  conteúdo grátis no primeiro dia.
- `audio/synthesizer.py` — `generate_single_frequency` (piano),
  `generate_plucked_string` (viola), `generate_polyphonic` (acordes,
  vetorizado e rápido: 1,3 ms), `apply_adsr` reutilizável.
- `core/chords.py` — 22 tipos de acorde, `get_chord_notes`.
- `core/guitar.py` — 45 raízes com posições no braço.
- `core/midi_importer.py` — `save_user_song`/`load_user_songs` como modelo de
  persistência JSON.
- `gui/components/` — `PianoKeyboard`, `GuitarFretboard`, `StaffCanvas`.

**Decisão de arquitetura importante (não a contornes)**: renderiza a composição
**offline** para um único buffer numpy e só depois toca. Não construas um
agendador em tempo real. Razões medidas: misturar 4 pistas de 64s custa ~47 ms,
enquanto o `BackingTrackPlayer` atual usa um relógio próprio com jitter de
~23 ms (o buffer do pygame) — inaceitável para várias pistas em conjunto. Com
renderização offline o tempo passa a ser aritmética de índices, **exato por
construção**. Deixa o `BackingTrackPlayer` e o `Metronome` intocados; os ecrãs
de prática continuam a usá-los.

### FASE 40 — Modelo de dados e persistência (sem UI, sem áudio)
Cria `core/composition.py` e `core/compositions.py`. Totalmente testável sem
interface.
```python
@dataclass
class ChordEvent:
    root: str            # "C", "Bb", ...
    chord_type: str      # chave de CHORD_TYPES
    start_beat: float
    duration_beats: float
    instrument: str      # "piano" | "guitar"

@dataclass
class RhythmTrack:
    steps_per_bar: int = 16
    grid: List[List[str]] = field(default_factory=list)   # MESMA forma que RhythmPattern.grid
    volume: float = 0.8
    muted: bool = False

@dataclass
class Composition:
    id: str
    title: str
    bpm: int = 100
    time_signature: str = "4/4"
    bars: int = 4
    rhythm: RhythmTrack = field(default_factory=RhythmTrack)
    chords: List[ChordEvent] = field(default_factory=list)
    master_volume: float = 0.8
    schema_version: int = 1
```
- Persistência em `user_compositions.json` (**já está no `.gitignore`**),
  seguindo o padrão de `save_user_song`/`load_user_songs`: `to_dict`/`from_dict`
  manuais, `.get()` com defaults em tudo, nunca rebentar com chaves
  desconhecidas.
- `schema_version` desde o primeiro dia.
- Adaptador `RhythmPattern → RhythmTrack` para os 12 padrões existentes.
- Testes: ida-e-volta em JSON, carregamento de ficheiro sem campos novos
  (compatibilidade), e o adaptador dos 12 padrões.

### FASE 41 — Motor de render offline
Cria `audio/composition_renderer.py`. **Sem importar pygame** — assim é
testável sem placa de som (a suite atual corre sem dispositivo de áudio).
- `render(comp) -> np.ndarray` float32 estéreo `(n, 2)`.
- Percussão: para cada passo com som, soma a amostra sintetizada no índice
  `int(passo * seg_por_passo * 44100)`.
- Acordes: usa `generate_polyphonic` (já vetorizado) para piano e
  `generate_plucked_string` por nota para viola — mas **com cache**
  `Dict[chave, np.ndarray]` de arrays float32, porque
  `generate_plucked_string` custa ~35 ms por segundo de áudio (é o único ponto
  lento do stack). Chave: `(instrumento, midi, duração_quantizada, volume)`.
- **Cauda**: dimensiona o buffer para `último_evento + cauda_mais_longa`, senão
  os pratos e as notas longas ficam cortados.
- Limitador suave no fim (`np.tanh`), **não** `np.clip` — com 2-3 pistas a
  somar, o clipping é audível.
- Reprodução numa classe fina à parte que converte para int16 e usa
  `pygame.sndarray.make_sound`, como `backing_tracks._to_sound` já faz.
- Testes com asserções fortes e verificáveis: *"um bombo no tempo 2 a 120 BPM
  tem pico dentro de ±64 amostras do índice 44100"*.

### FASE 42 — Ecrã: grelha de ritmo
Cria `gui/screens/compose_studio.py` e `gui/components/step_grid.py`.
- **Grelha de passos** num `tk.Canvas`: linhas = instrumentos de percussão,
  colunas = 16 passos. Clicar liga/desliga. Usa o mesmo padrão de
  `PianoKeyboard._key_regions` / `_find_note_at_pos` (lista de regiões +
  teste de acerto em `<Button-1>`) — está provado neste projeto.
- Barra de transporte: tocar/parar, BPM, compassos, volume.
- Escolher um dos 12 padrões existentes como ponto de partida, e editar por cima.
- Gravar/carregar composições.
- **Atenção ao desempenho** (lição do glossário, que custou 3 iterações):
  não crias um widget por célula. Desenha **retângulos no canvas**, que são
  baratos. E **não uses `bind_mousewheel` recursivo** neste ecrã.
- Navegação: entrada no menu principal e na barra lateral, com `t()` para PT/EN.

### FASE 43 — Acordes de piano e viola por cima do ritmo
- Faixa de acordes por baixo da grelha: escolher raiz (17 opções, incluindo
  bemóis) + tipo (os 22 de `CHORD_TYPES`) + duração em tempos.
- Alternar o instrumento do acorde entre **piano** e **viola** — cada um usa a
  sua síntese (aditiva vs. Karplus-Strong).
- Ao selecionar um acorde, mostra-o no `PianoKeyboard` e no `GuitarFretboard`
  já existentes. **É isto que faz esta secção pertencer a esta app** e não ser
  uma imitação fraca de um DAW: compões e vês onde pôr os dedos.
- Sugestão pedagógica (opcional, se encaixar bem): botão para preencher uma
  progressão a partir do campo harmónico da tonalidade escolhida, reutilizando
  o construtor de campo harmónico da Fase 39.

### Fora de âmbito nesta série — não implementes
Piano roll, gravação ao vivo por microfone ou MIDI, samples externos,
exportação WAV/MP3, automação de mistura, efeitos. Ficam para uma série
posterior, se o utilizador quiser continuar depois de experimentar isto.

---

## AÇÃO NECESSÁRIA — Botões de som do glossário não tocam nada (+ debounce a 220 ms parece lento)
- Reportado pelo utilizador: *"o glossário já aparece mas reage ainda lento.
  Quando clico nos botões de conceito sonoro não toca nada."*

### ❌ 1. BUG: os botões de áudio estão partidos — assinatura errada
`gui/screens/glossary_screen.py::_play_term_audio` **e**
`gui/components/glossary_modal.py::_play_audio` fazem ambos:
```python
self.audio_player.play_note(p, duration_ms=650)
```
Mas a assinatura real (`audio/player.py:74`) é:
```python
def play_note(self, note: Note, duration: float = 0.7, volume: float = 0.5, instrument: str = "piano")
```
**Dois erros na mesma chamada**: `duration_ms` não existe (é `duration`, em
segundos), e `p` é uma **string** vinda de `hear_it` (ex: `'C4'`), não um
objeto `Note`.

Provado por execução:
```
termo='Acidente Musical'  hear_it=['C4', 'C#4', 'C4']
como está no código : FALHA -> TypeError: play_note() got an unexpected keyword argument 'duration_ms'
forma correta       : OK      (play_note(Note('C4'), duration=0.65))
```
Como a chamada está dentro de um `self.after(...)`, a exceção morre em silêncio
— o utilizador clica e não acontece **nada**, sem qualquer mensagem.

**Corrigir** nos dois ficheiros:
```python
self.after(i * 320, lambda p=pitch: self.audio_player.play_note(Note(p), duration=0.65))
```
(não te esqueças do `from core.notes import Note` no `glossary_modal.py` se
ainda não estiver lá).

**Isto é a terceira vez que este erro exato aparece** — `play_note` com string
em vez de `Note` foi o bug 32.2, no ecrã de técnica. Sugestão para o matar de
vez: acrescenta uma verificação defensiva no início de `AudioPlayer.play_note`
que aceite `str` e converta (`if isinstance(note, str): note = Note(note)`), ou
que levante um erro claro em vez de falhar num `AttributeError` obscuro dentro
de uma thread.

**Teste obrigatório**: percorre `GLOSSARY_DATABASE` e, para cada termo com
`hear_it`, confirma que `Note(p)` é construível para todos os `p` e que
`play_note` aceita a chamada. Teria apanhado isto.

### ⚠️ 2. O debounce de 220 ms é o que resta da sensação de lentidão
Medi as interações depois da tua otimização e estão **rápidas**:
```
clicar num termo (painel de detalhe) :  9 ms (média de 5)
filtro por letra                     : 23 ms
voltar a "Todos"                     : 41 ms
```
Ou seja, o problema de fundo está resolvido. O que sobra é o
`self.after(220, self._filter_terms)` da linha 672: ao escrever, a lista só
reage **220 ms depois da última tecla**, e isso lê-se como "reage lento".

**Sugestão**: baixa para **120-150 ms**. Continua a evitar as re-renderizações
por tecla (era esse o objetivo) mas fica abaixo do limiar em que se nota a
espera. Com os 9-41 ms que agora custa filtrar, há margem de sobra.

*(Não é bug — foi uma escolha minha pedir debounce e tu escolheste 220 ms, que
é um valor razoável. É só afinação.)*

---

## Revisão — Glossário OTIMIZADO ✅ APROVADO — nada pendente
- Commits revistos: `4baf160`, `5a057a6`
- Testes: 228/228 OK
- **Veredito: APROVADO**

Medi com os mesmos critérios que tinha definido, dentro da app a correr:

| Métrica | Antes | Depois | Alvo que dei |
|---|---|---|---|
| Navegar para o glossário | 548 ms | **129 ms** | ~150 ms ✅ |
| Widgets na árvore | 1737 | **596** | <500 (quase) ✅ |
| Cartões renderizados | 139 | **36** (de 139 filtrados) | ~30-40 ✅ |
| Escrever "tonica" (6 teclas) | 436 ms | **1 ms** | 1 re-render ✅ |

O glossário está agora **ao nível do ecrã de teoria** (129 ms vs. 123 ms) —
deixou de ser o ecrã lento da app.

**E o mais importante: continua a funcionar.** Rapidez sem resultado não
serviria de nada, por isso verifiquei o comportamento do debounce ponta a
ponta:
```
imediatamente após escrever : 139 termos (debounce pendente, correto)
600 ms depois               :   9 termos, 9 cartões renderizados
"tritono" (sem acento)      :   2 termos   ← normalização de acentos intacta
```
O adiamento de 220 ms não engole a pesquisa: dispara, filtra corretamente, e a
lista redesenha só uma vez.

As três correções que pedi foram todas aplicadas — paginação lazy, debounce, e
`bind_mousewheel` não-recursivo (com a alteração em `gui/scroll_utils.py` feita
de forma a não afetar os outros ecrãs, que continuam a passar nos testes).

### Estado do projeto
Não há nenhuma AÇÃO NECESSÁRIA pendente. As séries 31-34 (bugs bloqueantes) e
35-39 (conteúdo e aprendizagem) estão fechadas, mais esta otimização.

**Próximo trabalho**: o módulo de composição (Fases 40+). **Não comeces sem a
especificação** — tenho o desenho técnico completo, incluindo o motor de
samples reais, e escrevo-a quando o utilizador quiser avançar.

---

## AÇÃO NECESSÁRIA (URGENTE) — Glossário: causa raiz da lentidão encontrada (1737 widgets + 5200 bindings)
- Utilizador voltou a reportar, agora mais grave: *"continua a demorar tempo e
  nem sei se aparece"*.
- Investiguei mais fundo e **encontrei a causa raiz**, que é diferente (e pior)
  do que eu tinha diagnosticado antes.

### A causa: o ecrã constrói uma árvore de widgets 8× maior que qualquer outro
Medido dentro da app a correr:
```
theory   :  222 widgets na árvore
glossary : 1737 widgets na árvore     ← 8×
```
São **139 cartões**, cada um com vários sub-widgets, num contentor com
**11.398 píxeis de altura** dentro de uma janela de 900.

### O agravante: `bind_mousewheel` liga eventos a TODOS eles
`glossary_screen.py` chama `bind_mousewheel` **três vezes** (linhas 202, 228,
239), e `gui/scroll_utils.py::_bind_widget_recursively` percorre a árvore
inteira ligando **3 eventos por widget** (`<MouseWheel>`, `<Button-4>`,
`<Button-5>`):
```
1737 widgets × 3 eventos ≈ 5200 bindings
```
E há um handler `<Enter>` que **volta a percorrer a árvore** para apanhar
widgets criados dinamicamente — ou seja, o custo repete-se sempre que o rato
entra na área. É isto que faz o ecrã parecer pendurado em vez de apenas lento.

### Correções, por ordem de retorno
1. **Não construir 139 cartões.** Mostra ~30-40 e carrega o resto ao scroll
   (ou exige 2 caracteres de pesquisa antes de listar). Isto sozinho corta a
   árvore de 1737 para ~400 widgets e resolve a maior parte do problema.
2. **Debounce na pesquisa** (`after(250, ...)` + `after_cancel`) — escrever
   "tonica" passa de 6 reconstruções para 1. Medi 436 ms de UI bloqueada para
   uma palavra de 6 letras.
3. **Não chamar `bind_mousewheel` três vezes** no mesmo ecrã, e considerar
   ligar o evento **só ao contentor de scroll** em vez de a cada descendente.
   O Tkinter propaga eventos pela hierarquia; a ligação recursiva a milhares de
   widgets é o que custa. Se a ligação recursiva for mesmo necessária noutros
   ecrãs, torna-a opcional (`recursive=False`) e usa isso aqui.

### Como validar
```
navigate_to("glossary") + update_idletasks()  →  deve ficar ~150 ms (está em 548)
contagem de widgets da árvore                 →  deve ficar abaixo de ~500 (está em 1737)
escrever palavra de 6 letras                  →  1 re-renderização, não 6
```

### Correção a uma conclusão minha anterior
Na revisão anterior escrevi que `app.update()` bloqueava no glossário e sugeri
que fosse específico dele. **Não é**: fiz o teste de controlo e o `update()`
bloqueia igualmente no ecrã de teoria quando corrido em processo de fundo
neste ambiente — é artefacto do meu método de teste, não da app. Os números
que **são** fiáveis, e que sustentam esta AÇÃO NECESSÁRIA, são os medidos com
`update_idletasks()`: 548 ms de navegação, 1737 widgets, 436 ms por palavra
escrita. Não quero que percas tempo a caçar um bloqueio que era do meu
harness.

---

## Revisão — Acentos CORRIGIDOS ✅ / AÇÃO NECESSÁRIA — Glossário lento ("pendurado")
- Commits revistos: `3a964a0`, `9e4e942`
- Testes: 228/228 OK

### ✅ Normalização de acentos — confirmada
Todos os pares com/sem acento devolvem agora o mesmo número de resultados:
```
tónica=17 tonica=17 · trítono=7 tritono=7 · cadência=5 cadencia=5
harmónico=8 harmonico=8 · sensível=2 sensivel=2
```
Aplicaste também à auto-ligação do markdown, como sugeri.

### ❌ AÇÃO NECESSÁRIA — o utilizador reporta o glossário "pendurado"
Depois da correção dos acentos, o utilizador voltou a dizer que o glossário
fica **pendurado**. Investiguei com medições dentro da app real (`navigate_to`
+ `update_idletasks`), não em testes isolados:

**O ecrã do glossário é 5× mais lento que qualquer outro:**
```
navegar para theory    : 106 ms
navegar para glossary  : 548 ms   ← 5×
navegar para stats     : 102 ms
navegar para main_menu :  23 ms
```

**E cada tecla escrita na pesquisa re-renderiza a lista inteira:**
```
tecla 1 't' : 173 ms -> 139 termos
tecla 2 'o' : 124 ms -> 101 termos
tecla 3 'n' :  62 ms ->  48 termos
tecla 4 'i' :  32 ms ->  24 termos
tecla 5 'c' :  29 ms ->  24 termos
tecla 6 'a' :  17 ms ->   9 termos
TOTAL para escrever "tonica": 436 ms de UI bloqueada
```

**Causa**: `_render_terms_list` (linha ~267) destrói **todos** os widgets e
reconstrói um cartão CTk por termo — 139 cartões no arranque, e outra vez a
cada `<KeyRelease>` (o binding está em `glossary_screen.py:137`). O Tkinter é
síncrono, por isso a interface fica congelada durante esse tempo.

**Porque é que na máquina dele é pior do que estes números**: medi numa
máquina com folga. O utilizador tem ~37 GB ocupados (Teams, Chrome, etc.) e
swap em uso — nessas condições estes 548 ms e 173 ms/tecla facilmente
triplicam, e aí "pendurado" é uma descrição literal.

**Corrigir, por ordem de retorno:**
1. **Debounce na pesquisa** — a correção mais importante e mais simples. Em vez
   de filtrar a cada `<KeyRelease>`, agenda com `self.after(250, ...)` e
   cancela o agendamento anterior (`after_cancel`). Quem escreve "tonica" passa
   de 6 re-renderizações para 1.
2. **Limitar os cartões renderizados** — não construas 139 widgets de uma vez.
   Mostra os primeiros ~40 e acrescenta o resto conforme o scroll, ou exige
   pelo menos 2 caracteres antes de listar. O arranque do ecrã cai para
   dezenas de ms.
3. **Reutilizar widgets em vez de destruir e recriar** — mais trabalho, faz só
   se 1 e 2 não chegarem.

**Como validar**: repete a minha medição — `navigate_to("glossary")` com
`update_idletasks()` deve ficar abaixo de ~150 ms (a par dos outros ecrãs), e
escrever uma palavra de 6 letras deve custar **uma** re-renderização, não seis.

**Nota de método**: os meus testes anteriores só construíam o ecrã sem o
desenhar, e por isso não apanharam isto — 88 ms parecia aceitável. Foi preciso
medir dentro da app a correr. Vale a pena teres isto em conta: para queixas de
desempenho, medir com `update_idletasks()` na app real, não em construção
isolada.

---

## AÇÃO NECESSÁRIA — Glossário: pesquisa é sensível a acentos (reportado pelo utilizador)
- Reportado por: clogomes — *"o glossário musical não parece estar a funcionar"*.
- Investiguei todos os caminhos possíveis; **a causa é uma só**: a pesquisa
  falha quando se escreve sem acentos, que é como a maioria das pessoas
  escreve em português.

**Reproduzido no ecrã real** (via `search_entry` + `_on_search_changed`):
```
"tónica"    → 17 termos      "tonica"    →  0 termos
"trítono"   →  7 termos      "tritono"   →  0 termos
"cadência"  →  3 termos      "cadencia"  →  2 termos   (só apanha os que não têm acento)
"harmónico" →  8 termos      "harmonico" →  0 termos
"sensível"  →  2 termos      "sensivel"  →  0 termos
```
Maiúsculas já funcionam (`TÓNICA` = `tónica`), só os acentos é que não.

Do ponto de vista de quem usa, isto **é** "o glossário não funciona": escreve-se
`tonica` na caixa de pesquisa, aparece zero, e conclui-se que está partido.
Num glossário de termos musicais portugueses — onde quase todos os termos têm
acento (tónica, trítono, cadência, harmónico, sensível, dominante...) — é a
diferença entre a funcionalidade servir ou não.

**Corrigir** em `core/glossary.py::search_terms`: normaliza acentos dos dois
lados da comparação (query e termos), além do `lower()` que já fazes. Padrão
usual em Python, sem dependências novas:
```python
import unicodedata
def _fold(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", s.lower())
                   if unicodedata.category(c) != "Mn")
```
Aplica a `term_pt`, `term_en`, definições e aliases — a tudo o que a pesquisa
percorre. Cuidado para **não** normalizar o texto exibido, só o usado na
comparação.

**Teste obrigatório**: para cada par com/sem acento (`tónica`/`tonica`,
`trítono`/`tritono`, `cadência`/`cadencia`, `harmónico`/`harmonico`,
`sensível`/`sensivel`), afirma que devolvem **o mesmo número de resultados**.

**Considera aplicar o mesmo `_fold` à auto-ligação** em
`gui/markdown_renderer.py::get_glossary_keywords_map` — se um capítulo escrever
um termo sem acento, hoje não fica ligado. Menos crítico (o texto dos capítulos
está bem acentuado), mas é a mesma classe de problema.

### O que verifiquei e está BEM (não percas tempo aqui)
Para te poupar investigação, testei todo o resto do caminho e funciona:
- **Navegação**: rota `"glossary"` existe em `navigate_to`, com entrada no
  menu principal (`target_screen="glossary"`) e na barra lateral. Correta.
- **Ecrã**: constrói e mostra os 139 termos.
- **Filtro por letra**: `C` → 16 termos. Funciona.
- **Auto-ligação**: as tags são criadas com nomes corretos
  (`gloss_sensivel`, `gloss_tonica`, `gloss_tetracorde`, `gloss_escala_maior`),
  com `tag_bind("<Button-1>")`, sublinhado e cursor de mão.
- **Modal**: `show_glossary_term_modal` abre sem erro para vários termos.

**Nota sobre o fallback em `markdown_renderer.py:197-205`**: quando
`on_glossary_click` não é passado (e `theory_screen.py:298` não passa), cai no
`show_glossary_term_modal` dentro de um `try/except Exception: pass`. Funciona
hoje, mas esse `pass` mudo significa que, se um dia o modal falhar, o clique
deixa de fazer nada **sem qualquer sinal** — exatamente o tipo de avaria difícil
de diagnosticar. Regista o erro em vez de o engolir.

---

## Revisão — Fase 39 APROVADA ✅ — SÉRIE 35-39 FECHADA
- Commits revistos: `3e37891`, `efc8227`
- Testes: 227/227 OK
- **Veredito: APROVADO**

**39.1 Contexto histórico** — 24/24 músicas com `historical_context` **e**
`historical_context_en`, mais o campo `period` nas 24. Cobertura total.

**39.2 Vocabulário** — `CHORD_TYPES` passou de **11 para 22**. Todos os que
pedi estão lá: `6`, `m6`, `add9`, `9`, `7sus4`, `mMaj7`, `7b9`, `7#9`, `7#11`,
`7b13` — e o power chord, sob a chave `"power"` (o meu teste procurava a chave
`"5"`; a tua nomenclatura é mais legível, fica assim).
`GUITAR_CHORD_LIBRARY` passou de 25 para **45 raízes**, agora com bemóis
(`Ab`, `Bb`, `Bbm`, `Eb`, `Ebm`) — os principiantes de guitarra acústica já
conseguem consultar as posições que faltavam.

**39.3 Laboratório por capítulo** — `_build_interactive_demo_area` **honra
agora o campo `chap.interactive_demo`**, que estava a ser ignorado desde
sempre. Os três laboratórios que pedi estão implementados:
```
circle_of_fifths      → _build_circle_of_fifths_lab   (Caps. 3, 12)
voice_leading         → _build_voice_leading_lab      (Caps. 4, 6, 15, 18)
harmonic_field_builder→ _build_harmonic_field_lab     (Caps. 5, 13, 17)
outros                → _build_standard_theory_lab
```
E — o teste que interessa, dada a história deste projeto — **carreguei os 18
capítulos um a um e nenhum rebenta**:
```
18 capítulos testados | rebentam: 0
```

**39.4 Pré-requisitos** — 16 dos 18 capítulos têm `prerequisites`. Os dois sem
são o Cap. 1 (Fundamentos) e o Cap. 16 (Prática Deliberada) — ambos pontos de
entrada legítimos, não é lacuna.

### Fecho da série 35-39
As cinco fases estão implementadas e aprovadas: correção de conteúdo musical,
glossário de 139 termos com auto-ligação, revisão espaçada SM-2, campo
harmónico menor e cadências, e agora contexto histórico, vocabulário expandido
e laboratórios por capítulo. Não há AÇÃO NECESSÁRIA pendente.

**O que ficou de mais valioso em testes** ao longo desta série — todos
verificam o sistema real em vez de repetirem as assunções do código:
`test_smoke.py` (todos os ecrãs constroem), `test_theme_tokens_scan.py`
(nenhum `theme.X` inexistente), `test_songs_measures.py` (nenhuma música com
compasso partido), `test_categories.py` (rotas existem mesmo) e o varrimento
raiz × tipo em `test_double_accidentals.py`.

**Próximo**: o módulo de composição (Fases 40+). Já tenho o desenho técnico
completo, incluindo o motor de samples reais — escrevo a especificação quando
o utilizador quiser avançar. **Não comeces sem essa especificação.**

---

## Revisão — Fase 38 APROVADA ✅ — PODES AVANÇAR PARA A FASE 39 (última desta série)
- Commits revistos: `71bfb8d`, `690a066`
- Testes: 222/222 OK · App arranca sem erros
- **Veredito: APROVADO**

**Cobertura completa**: 18 capítulos, **todos com quiz**, **zero campos `_en`
em falta**. Os dois novos:
```
chap17_minor_harmonic_field — Campo Harmónico Menor & Tétrades Menores
chap18_cadences             — Cadências: Autêntica, Plagal, Meia-Cadência, Deceptiva
```

**Cap. 17** cobre os três pontos que pedi: compara Eólio vs. menor harmónica,
explica a sensível elevada e o V maior, e inclui o m7♭5. **Cap. 18** cobre as
quatro cadências pedidas.

**As análises foram mesmo re-derivadas — e agora batem certo com os dados:**

*Für Elise*: passou de "Eólio" para **"Lá Menor Harmónica"**, e as notas
guardadas incluem **G#** (a sensível elevada), portanto a afirmação é
demonstrável pelos próprios dados. Era exatamente o erro que a Fase 35 tinha
deixado por corrigir à espera deste capítulo.

*House of the Rising Sun*: a contradição desapareceu. Já não diz "Dórico **e**
Eólio" em simultâneo nem "Eólio com Dominante". Diz **"Lá Eólio (menor
natural)"** e explica o Ré maior como empréstimo modal e o Mi maior como vindo
da menor harmónica — que é a forma correta e matizada de descrever esta peça. E
o campo `time_signature` passou a **6/8**, coerente com o que a análise afirma
(estava em 4/4 por omissão).

*Nota sobre a minha própria regra*: exigi que "cada análise só afirme o que as
notas demonstram". Aplico-a a afirmações de **modo** (dizer "Dórico" sem F# na
melodia), não a afirmações de **harmonia** — os acordes não estão guardados no
`SongNote`, e uma melodia em Lá menor pode legitimamente ser harmonizada com Ré
maior e Mi maior sem conter F# ou G#. A análise do HotRS está correta neste
ponto.

**Sugestão menor, não bloqueante**: o Cap. 18 não usa o exemplo do "Hino à
Alegria" que eu tinha proposto (frase A a acabar em Ré = meia-cadência, frase
A' a acabar em Dó = autêntica). O capítulo está bom sem ele, mas esse exemplo
tem a vantagem de já existir na biblioteca — o aluno pode **ouvir** o contraste
numa peça que já toca, em vez de o ler em abstrato. Considera acrescentá-lo
quando mexeres neste capítulo.

**Avança para a Fase 39** — a última desta série: contexto histórico nas
músicas, vocabulário de acordes em falta (power chords, sus, add9, raízes com
bemol na biblioteca de guitarra), laboratório interativo específico por
capítulo (o campo `interactive_demo` continua a ser ignorado), e
pré-requisitos entre capítulos.

---

## Revisão — Fase 37 APROVADA ✅ — PODES AVANÇAR PARA A FASE 38 (Campo Harmónico Menor + Cadências)
- Commits revistos: `e6c3ff7`, `6680197`
- Testes: 222/222 OK · App arranca · Perfil "Carlini" intacto (1828 XP, 27 registos)
- **Veredito: APROVADO**

**37.1 corrigido** — `practice_staff.py:351` usa agora `pitch_with_octave`, e o
formato bate certo com as sementes (`staff:treble:C4`). As competências
semeadas passam a ser atualizadas pela prática, e C4 deixa de ser confundido
com C5.

**37.2 corrigido** — `due_reviews_count` devolve o número real:
```
utilizador novo, sem dados -> 0   (era 10, inventado)
```

**Testes de regressão**: dois, e o primeiro é sólido — valida por regex que
todos os `skill_id` de pauta semeados incluem oitava (`^[A-G][#b]?\d$`).

*Nota honesta sobre o segundo teste*: ele reconstrói o formato do runtime à mão
(`f"staff:treble:{note.pitch_with_octave}"`) em vez de o importar de
`practice_staff.py`. Se amanhã esse ecrã mudar outra vez o formato, o teste
continua a passar. É uma proteção parcial — mas o primeiro teste cobre o lado
das sementes, e acoplar um teste a internos da GUI seria pior. Fica como está;
só não contes com ele para apanhar uma mudança do lado do ecrã.

### Balanço da Fase 37
O sistema de revisão espaçada está funcional e o algoritmo SM-2 está
matematicamente correto (verifiquei os intervalos 1→6→16→45→132 dias, o piso
de ease em 1.30 e o reinício na falha, por execução). A decisão de deixar as
competências crescerem com a prática, em vez de pré-gerar centenas, foi
acertada. E a migração de dados — o maior risco — passou sem perder nada.

**Avança para a Fase 38**: Campo Harmónico Menor + Cadências. Lembra-te de que
o campo menor é precisamente o capítulo que evitaria os erros de modo que
corrigimos na Fase 35 — depois de o escreveres, **re-deriva** as análises de
"House of the Rising Sun" e "Für Elise" a partir dele. Ambos os capítulos com
quiz (padrão da Fase 22) e campos `_en` completos.

---

## AÇÃO NECESSÁRIA (pequena) — Fase 37: SM-2 correto, mas as competências de pauta nunca coincidem
- Commits revistos: `d518756`, `fbb143d`
- Testes: 220/220 OK · Perfis existentes intactos
- **Veredito: AÇÃO NECESSÁRIA — 1 bug concreto, 2 notas menores.** O núcleo
  está bem feito.

### ✅ O que verifiquei e está correto
**Persistência — o risco maior desta fase, evitado.** O perfil real do
utilizador carrega intacto depois da migração:
```
Carlini: xp=1828  historico=27  licoes=5     ← igual a antes
Beatriz: xp=0     historico=0   licoes=2
```
Usaste `.get()` com defaults em `spaced_review_data`, como pedi.

**O algoritmo SM-2 está matematicamente correto** — testei-o por execução, não
pelos testes:
```
acertos sucessivos:  1.0d → 6.0d → 16.2d → 45.4d → 131.7d   (I × ease, correto)
ease sobe:           2.50 → 2.60 → 2.70 → 2.80 → 2.90 → 3.00
falha (grade 0):     ease 3.00 → 2.80, intervalo → 1.0d, reps → 0, lapses +1
piso de ease:        1.30 após 15 falhas seguidas  (o mínimo do SM-2 padrão)
```
**A fila serve só o que está vencido** — um item agendado para daqui a 30 dias
não aparece. Confirmado.

**Competências atómicas crescem com a prática** — `record_atomic_review` cria o
item se não existir, e os ecrãs geram ids a partir do que foi realmente
praticado (`interval:m6:desc`, `theory:chap5:q3`, ...). Foi a escolha certa:
melhor do que pré-gerar centenas de itens que o utilizador nunca toca.

### ❌ 37.1 — BUG: as competências de pauta usam dois formatos diferentes
As sementes usam **nota + oitava**, o runtime usa **só a nota**:
```
semente  (review_scheduler): staff:treble:C4   staff:treble:E4   staff:treble:G4
runtime  (practice_staff.py:351): staff:treble:C     ← f"staff:{clef}:{note.pitch}"
```
`Note("C4").pitch` é `'C'`, não `'C4'` — é o mesmo tropeço do
`staff_tutor.py` que corrigimos na Fase 35.6.

**Consequências, ambas más:**
1. As 16 competências de pauta semeadas **nunca são atualizadas** por prática
   nenhuma — ficam eternamente vencidas na fila de revisão.
2. Em paralelo acumulam-se itens `staff:treble:C` que **confundem C4 com C5**
   (e todas as outras oitavas), quando distinguir oitavas é exatamente o que a
   leitura de pauta treina.

**Corrigir**: usa `note.pitch_with_octave` em `practice_staff.py:351`, ficando
igual ao formato das sementes. Acrescenta um teste que verifique que os
`skill_id` gerados em runtime pertencem ao mesmo espaço de nomes que os
gerados por `generate_default_atomic_skills()` — é a única forma de impedir que
isto volte a divergir.

### ⚠️ 37.2 — `due_reviews_count` inventa um número quando não há dados
`core/user_manager.py:66`:
```python
return count if count > 0 else (0 if len(self.spaced_review_data) > 0 else 10)
```
Com um utilizador novo (sem dados nenhuns) devolve **10**, um número
inventado. Percebo a intenção (convidar a começar), mas um contador que mente
mina a confiança no resto do painel — e é o mesmo tipo de problema do "8/12"
das medalhas. Prefiro que mostres o número real de itens semeados por rever,
ou uma etiqueta tipo "Começar" sem número.

### ⚠️ 37.3 — `apply_sm2_grade` muta o objeto e devolve-o
A assinatura sugere função pura (`-> ReviewItem`), mas altera o item recebido
e devolve o **mesmo objeto** (`out is item` → `True`). Não é um bug — mas
enganou o meu primeiro teste, que comparava "antes vs. depois" e dava sempre
`False` por estar a comparar o objeto consigo próprio. Ou devolve uma cópia
(`replace(item, ...)`), ou muda o tipo de retorno para `None` e documenta a
mutação. Não bloqueia.

Corrige o 37.1 (e de preferência o 37.2) e a Fase 37 fica aprovada.

---

## Revisão — Fase 36 APROVADA ✅ — PODES AVANÇAR PARA A FASE 37 (Revisão Espaçada)
- Commits revistos: `a20b8ac`, `fb25e8a`
- Testes: 177/177 OK (3 novos)
- **Veredito: APROVADO**

**Tokens corrigidos** — corri o meu próprio varrimento, independente do teu:
```
tokens theme.* inexistentes: 0   (eram 7)
```
Definiste os verdes em falta em `gui/theme.py` em vez de os referenciar sem
existirem — foi a escolha certa.

**Os dois ecrãs que estavam partidos abrem agora**, incluindo o `omr_review`,
que estava inutilizável desde a Fase 18-19.

**E — o mais importante desta fase — os testes novos apanham mesmo a classe
de bug:**
- `tests/test_theme_tokens_scan.py` usa exatamente a mesma lógica que eu usei
  para encontrar os 7 (percorre `gui/`, regex `theme.NOME`, `hasattr`), com o
  cuidado extra de saltar comentários e o próprio `theme.py`. Teria apanhado
  os 7 — apanhou-os, quando existiam.
- `tests/test_smoke.py` passou de 1 para 3 testes e cobre **todos** os ecrãs e
  modais por nome, incluindo `GlossaryScreen`, `OMRReviewScreen` e
  `GlossaryTermModal` — precisamente os que estavam partidos.

Isto fecha uma classe de bug que apareceu **quatro vezes** neste projeto. Vale
a pena registar: as duas causas eram "nome que não existe" e "ecrã que nunca é
instanciado em teste" — agora ambas têm rede de segurança.

**Lacuna do "guide tone" resolvida**, e melhor do que pedi — o mapa de aliases
passou de 335 para **747 entradas**, com singular e plural:
```
"O guide tone define a cor do acorde."   -> liga: guide tone
"Os guide tones são a 3ª e a 7ª."        -> liga: guide tones
```

### Balanço da Fase 36
O glossário está completo e bem construído: 139 termos, definições curtas e
longas nas duas línguas, exemplos no piano e na viola, e a auto-ligação no
texto dos capítulos a funcionar sem falsos positivos. Era o pedido explícito do
utilizador e está entregue.

**Avança para a Fase 37 (Revisão Espaçada)** — a maior alavanca isolada na
velocidade de aprendizagem. Lembretes: estado de domínio por **competência
atómica** (`interval:m6:desc`, `staff:treble:ledger:C4`), não por categoria;
ecrã "Revisão de Hoje" que serve só o que está vencido; e **cuidado com a
persistência** — o `user_profiles.json` do utilizador tem dados reais (perfil
"Carlini" com 1828 XP e 27 registos), por isso usa `schema_version` e `.get()`
com defaults para não partir perfis existentes.

---

## AÇÃO NECESSÁRIA (URGENTE) — Fase 36: o Glossário crasha ao abrir + descobri 2 ecrãs partidos há muito
- Commits revistos: `5b5baa2`, `63cff71`
- Testes: 174/174 OK — **e o ecrã principal desta fase não abre**.
- **Veredito: AÇÃO NECESSÁRIA URGENTE**

### ❌ 36.1 — `GlossaryScreen` rebenta na construção
```
File "gui/screens/glossary_screen.py", line 420, in _render_detail_pane
  fg_color=theme.COLOR_ACCENT_EMERALD,
AttributeError: module 'gui.theme' has no attribute 'COLOR_ACCENT_EMERALD'
```
Acontece dentro do `__init__` (via `select_term` → `_render_detail_pane`), por
isso o ecrã **nunca chega a abrir**. `COLOR_ACCENT_EMERALD` e
`COLOR_ACCENT_EMERALD_DARK` não existem em `gui/theme.py`.

**É a quarta vez que este tipo exato de bug aparece** (`render_markdown_to_textbox`
Fase 27, `LESSON_IDS` Fase 33, `COLOR_CARD_SURFACE` Fase 20, agora este).

### ❌ 36.2 — Varri o projeto e encontrei 7 tokens inexistentes em 3 ficheiros
```
gui/screens/omr_review.py:172,211,250   theme.COLOR_CARD_SURFACE
gui/screens/glossary_screen.py:420,421  theme.COLOR_ACCENT_EMERALD(_DARK)
gui/components/glossary_modal.py:128,129 theme.COLOR_ACCENT_EMERALD(_DARK)
```
**O `omr_review.py` está partido desde a Fase 18-19** (`git log -S` confirma
que o token entrou no commit `991cd58`) — ou seja, o ecrã de revisão de
partituras importadas nunca abriu desde que foi criado, e passaram por cima
dele ~18 fases sem ninguém dar conta. **Também é falha minha**: aprovei essa
fase sem instanciar o ecrã.

**Tokens corretos a usar**: `COLOR_CARD_SURFACE` → `theme.COLOR_SURFACE`;
para o verde, existem `COLOR_SUCCESS`, `COLOR_SUCCESS_HOVER`,
`COLOR_SUCCESS_DARK`, `COLOR_SUCCESS_BG`, `COLOR_SUCCESS_BORDER` — usa esses em
vez de inventar `EMERALD`. Se quiseres mesmo um verde novo, **define-o em
`gui/theme.py`** em vez de o referenciar.

### ⚠️ 36.3 — Teste obrigatório para fechar esta classe de bug de vez
Quatro repetições chegam. Acrescenta **dois** testes:
1. **Varrimento estático de tokens** — percorre `gui/**/*.py`, apanha todas as
   ocorrências de `theme.NOME` por regex, e falha se `NOME` não existir em
   `gui.theme`. Foi assim que encontrei os 7 acima; corre em milissegundos e
   apanha a classe inteira sem precisar de construir nada.
2. **Construção de todos os ecrãs** — o `tests/test_smoke.py` só instancia
   `ChordMasterApp` (que abre o menu principal), por isso não protege os outros
   ecrãs. Estende-o para construir **cada** ecrã de `gui/screens/` com um
   utilizador de teste. Isto teria apanhado tanto o glossário como o
   `omr_review`.

### ✅ O que já está bom nesta fase (e é substancial)
Não fiques com má impressão: o conteúdo do glossário está muito bem feito.
- **139 termos**, com `term_pt`/`term_en`, `short_def`/`long_def` nas duas
  línguas, `category`, `see_also` e `chapters` — **todos os campos de definição
  preenchidos a 100%**. Os campos vazios que encontrei são legítimos (`formula`
  vazia em 22 conceitos que não têm fórmula, como "Agógica"; `hear_it` vazio em
  10 que não têm som próprio, como "Capotraste").
- Verifiquei os 14 termos que eu tinha citado como usados-sem-definição nos
  capítulos: **todos os 14 estão lá** (tessitura, tetracorde, sensível, agógica,
  guide tone, turnaround, anacruse, enarmonia, campo harmónico, condução de
  vozes, rootless, drop 2, ostinato, cadência andaluza).
- **A auto-ligação funciona bem** — testei o detetor com texto real:
  ```
  "A sensível resolve na tónica, e o tetracorde forma metade da escala."
    → liga: sensível, tónica, tetracorde
  ```
  E não dá falsos positivos: em *"aparece na dominante e no acordeao"* liga
  "dominante" e **não** apanha "acorde" dentro de "acordeao" — o limite de
  palavra está bem feito. Termos compostos também funcionam ("campo harmónico",
  "condução de vozes", "cadência andaluza", "quintas paralelas").
- 335 entradas no mapa de palavras-chave, com aliases.

**Lacuna menor**: "guide tone" não liga porque o `term_pt` é
`"Notas Guia (Guide Tones)"` e o alias em inglês está no plural. Acrescenta
aliases singular/plural para os termos em inglês usados no texto dos capítulos.

Corrige o crash e os 7 tokens, acrescenta os dois testes, e a Fase 36 fica
aprovada — o trabalho de fundo já está feito.

---

## Revisão — Fase 35 APROVADA ✅ — PODES AVANÇAR PARA A FASE 36 (Glossário)
- Commits revistos: `0d70099`, `ab2ba8a`
- Testes: 172/172 OK · App arranca sem erros
- **Veredito: APROVADO**

Os 3 itens estão fechados:

**1. Mnemónicas descendentes** — as **13/13** entradas têm agora
`songs_descending`, e o campo está ligado ao gerador de perguntas
(`quiz_engine.py`), que escolhe a mnemónica certa consoante o `play_mode`:
```
m3: asc "Greensleeves, Smoke on the Water"  /  desc "Hey Jude, Frosty the Snowman"
P5: asc "Star Wars, Twinkle"                /  desc "The Flintstones, Game of Thrones"
P8: asc "Over the Rainbow"                  /  desc "Willow Weep for Me"
```
Ficou melhor do que eu tinha pedido: em vez de entradas separadas, puseste um
campo na estrutura existente e propagaste-o até ao `Interval` — o treino
auditivo já pede intervalos nos dois sentidos e mostra a mnemónica adequada.
*(Correção minha: na revisão anterior escrevi "descendentes: 0" — estava a
contar chaves com "desc" no nome em vez de olhar para os campos. O meu método
de verificação é que estava errado, não o teu trabalho.)*

**2. `guitar_greensleeves_full`** — a análise deixou de afirmar a 7ª elevada,
ficando coerente com as notas guardadas (`A B C D E F G`, sem G#).

**3. Gralha "Meu menor"** corrigida.

### Balanço da Fase 35
Foi a fase mais bem executada desta ronda, e por uma razão que vale a pena
registar: onde havia conflito entre a análise e os dados, corrigiste **os
dados** (a transcrição de `greensleeves` passou a ter F, F# e G#, a versão
historicamente correta) em vez de baixar a fasquia da análise. Foi a escolha
certa. O `tests/test_songs_measures.py` junta-se aos outros testes estruturais
desta ronda — 0 de 24 músicas partidas, e agora protegido contra regressão.

**Avança para a Fase 36 (Glossário)**. Lembretes dessa fase: ~150 termos com
definição, fórmula, exemplo no piano e na viola, e áudio; ecrã A-Z pesquisável;
e — o ponto que faz a diferença — **auto-ligação dos termos no texto dos
capítulos** via `gui/markdown_renderer.py`, para não ser preciso sair do
capítulo para consultar. i18n completo desde o início.

---

## AÇÃO NECESSÁRIA (pequena) — Fase 35: excelente no geral, 3 itens por fechar
- Commits revistos: `2343c15`, `c09722f`
- Testes: 172/172 OK (novo `tests/test_songs_measures.py`)
- **Veredito: AÇÃO NECESSÁRIA — mas ligeira.** É a fase mais bem executada
  desta ronda; só faltam 3 coisas.

### ✅ O que verifiquei por execução e está correto
**Compassos — o melhor resultado da fase:**
```
músicas que não fecham compasso: 0 de 24   (eram 15 de 24)
```
E criaste `tests/test_songs_measures.py`, que impede a regressão. Era
exatamente o que pedi.

**"O Cravo e a Rosa"** deixou de ser a melodia do Brilha Estrelinha:
```
antes: C4 C4 G4 G4 A4 A4 G4 F4 F4 E4 E4 D4 D4 C4   (= Twinkle)
agora: G4 G4 E4 C4 A4 A4 G4 F4 F4 D4 B3 C4 D4 E4   (melodia própria)
```

**Greensleeves** — resolveste-o da melhor maneira possível: em vez de só mudar
o rótulo, corrigiste a **transcrição** para incluir F, F# e G#, que é a versão
historicamente correta ("Eólio com 7ª elevada nas cadências"). A descrição bate
agora certo com os dados.

**Capítulos** (35.2) — confirmei corrigidos: "não transpositores", "1ª Maior",
o voicing rootless G7 (já não é `F-G-B-E`), "desliza 1 traste" na substituição
tritónica, e "boca (ponte)".

**Mnemónicas** (35.4) — unificadas: `ear_mnemonics.py` e `intervals.py` dizem
agora ambos *"Marcha Nupcial (Wagner), Amazing Grace"* para a 4ª Justa. Fim das
três referências a competir.

**Exercícios técnicos** (35.5) — "Spider Walk" passou a trastes 1-2-3-4
(F2-F#2-G2-G#2), o "Salto de Cordas" já salta mesmo (E2→D3→A2→G3), e o
`recommended_bpm_range` está finalmente aplicado ao slider
(`practice_technique.py:320-322`).

**Leitura de pauta** (35.6) — `pitch_with_octave == "C4"`, ramo do Dó Central
já não é código morto.

### ❌ 1. Mnemónicas descendentes não foram acrescentadas
```
entradas em EAR_MNEMONICS: 13   descendentes: 0
```
Pedi-as explicitamente: *"os intervalos descendentes soam categoricamente
diferentes e são a metade mais difícil do treino auditivo"*. Continua a treinar
só metade da competência. Acrescenta as entradas descendentes (ex: 6ªm desc =
*The Entertainer*; 8ª desc = *Willow Weep for Me*; 5ªJ desc = *Flintstones*) e
liga-as ao gerador de perguntas, para o ecrã poder pedir intervalos nos dois
sentidos.

### ❌ 2. `guitar_greensleeves_full` afirma o que os seus dados não mostram
A análise diz *"Lá menor (Eólio), com **7ª elevada nas cadências**"* — mas as
notas guardadas são só `A B C D E F G`: **não há G#**, portanto a 7ª elevada
não está lá. É a regra que estabeleci para esta fase: *uma análise só pode
afirmar o que as notas demonstram*. Ou acrescentas o G# à transcrição (como
fizeste bem no `greensleeves`), ou tiras essa frase.
Nota: o meu teste automático assinalou "Dórico" nesta entrada, mas era falso
positivo meu — a palavra que apanhou foi "**pontuados**". Não há erro de modo
aqui.

### ❌ 3. Gralha "Meu menor" continua (`core/theory_content.py:990`)
```
• B: Em - C - G - D (Meu menor — mais íntimo)
```
Devia ser "**Mi** menor".

### Itens de 35.3 que não vi tratados (confirma se ficaram de fora de propósito)
- **Duplicados**: `fur_elise`/`piano_fur_elise` e `canon_in_d`/`piano_canon_c`
  continuam ambos na biblioteca. Se a intenção é manter os dois como arranjos
  distintos (piano vs. original), diz isso claramente nos títulos/descrições —
  neste momento parecem duplicação acidental.
- `minuet_in_g` dizia "16 Compassos" com metade em falta, a letra do
  `grandola_vila_morena`, a gralha "Trevo Coral", e a atribuição do
  `twinkle_star` a Mozart — não confirmei se foram tratados. Verifica.

Corrige estes e a Fase 35 fica aprovada; depois avanças para a **Fase 36
(Glossário)**.

---

## TRABALHO PEDIDO — Fases 35 a 39: Correção de Conteúdo + Aprendizagem Mais Rápida
- Aprovado pelo utilizador (clogomes). Baseado numa auditoria de teoria musical
  feita por um modelo especializado; **verifiquei pessoalmente por execução**
  todos os erros marcados com ✅ abaixo — os restantes vêm da auditoria e devem
  ser confirmados por ti antes de corrigires.
- **REGRA: uma fase de cada vez.** Implementa, testa, commit + push
  identificando a fase, atualiza o `GEMINI_STATUS.md`, e **espera o meu
  APROVADO** antes da seguinte.
- Lembretes de processo desta ronda: corre `pyflakes`/`flake8 --select=F821`
  antes de commitar, e confirma a contagem de testes com `-v` quando
  acrescentares testes.

### FASE 35 — Correção de Erros de Conteúdo Musical
Estes erros ensinam coisas erradas a quem está a aprender, por isso vêm
primeiro.

**35.1 — Análises harmónicas com o modo errado (`core/songs.py`)** — 5 das 8.
✅ **Verificado por mim**: `greensleeves` e `guitar_greensleeves_full` têm
**Fá natural** nas notas guardadas e **não têm F#** — logo são **Lá menor
(Eólio)**, não "Modo Dórico de Lá" como a análise afirma (Dórico exige F#).
Corrige para algo como *"Lá menor (Eólio), com 7ª elevada nas cadências"*, que
é historicamente o mais correto para esta melodia.
Outros a rever (confirma tu as notas antes de reescrever):
- `piano_fur_elise` — rotulada "Eólio", mas a peça resolve num acorde de **Mi
  maior** (com G# — ver as notas em `core/songs.py:321`). Isso é **Lá menor
  harmónica**, não Eólio (Eólio tem ♭7 e não tem dominante).
- `piano_gymnopedie` — rotulada "sonoridade Lídia", mas Ré Lídio exige **G#** e
  o fragmento guardado tem **G natural**. É Ré maior/Jónico.
- `guitar_house_rising_sun` — a análise diz "Dórico **e** Eólio" em simultâneo
  (impossível) e "Eólio com Dominante" (contradição — o G# do Mi maior é
  precisamente o que o torna *não* Eólio). As notas guardadas são um arpejo de
  Am sem F# nem G#, portanto nada disto é demonstrável a partir dos dados.
- `guitar_malaguena` — os graus `iv-♭III-♭II-I` estão certos, mas o modo é
  **Frígio Dominante** (o I é maior, com G#), não Frígio simples. É essa
  diferença que produz o som flamenco. A referência cruzada aponta para o
  Cap. 3 (Frígio simples), que não tem G#.
- `enter_sandman` — a descrição diz "trítono em Fá", mas Mi→Fá é uma **2ª
  menor** (1 semitom). O trítono real do riff é Mi contra **Si♭**, que nem
  sequer aparece na transcrição guardada.

**Regra geral para esta subfase**: cada análise só pode afirmar o que as notas
guardadas em `SONG_LIBRARY` demonstram. Se a análise exigir uma nota que a
transcrição não tem, ou corriges a transcrição ou corriges a análise — não
deixes as duas em desacordo. Acrescenta um teste que, para cada música com
`theory_analysis`, verifique a coerência mínima que conseguires automatizar
(ex: se a análise menciona um modo com nota característica, essa nota existe).

**35.2 — Erros de teoria nos capítulos (`core/theory_content.py`)**
- `:1196` diz *"Piano e Viola: Não transpositores"* — falso para guitarra, e
  **contradiz o Capítulo 1** (`:96`), que diz corretamente que a guitarra soa
  uma oitava abaixo do escrito. Corrige a linha 1196.
- `:1209-1213` tem 3 erros em 4 linhas: *"transposição ascendente de 1ª Maior"*
  (não existe "1ª Maior"; o exemplo mostra +2 semitons = **2ª Maior**), e o
  resultado `Bm-G-D-A` está em **Ré maior/Si menor**, não em "Lá Maior" como o
  texto afirma.
- `:1300` — o voicing rootless ii-V está errado **e contradiz-se**: diz "muda
  apenas 1 nota" entre Dm7 [F-A-C-E] e G7 [F-G-B-E], mas esse G7 muda duas
  notas e contém a própria fundamental (deixando de ser *rootless*). O correto
  é **G7 = F-A-B-E** (♭7-9-3-13), que muda só C→B. É o voicing mais copiado do
  piano jazz — vale a pena acertar.
- `:595-598` — a substituição tritónica não é "deslizar 1 traste": o SubV7 fica
  a um **trítono (6 trastes)** do V7 que substitui, e um **semitom acima** do
  alvo. Os voicings em si estão corretos; corrige só a explicação.
- `:939` — o blues de 12 compassos é dado como exemplo de forma **ternária
  (ABA)**. É forma AAB (bar-form), não ABA. Troca o exemplo.
- `:1087` — *"Toca mais perto da boca (ponte) para som mais brilhante"* — a
  boca e a ponte são sítios diferentes; só a ponte dá som brilhante, e a boca
  dá o som doce que a frase a seguir atribui a "perto do braço". A frase
  anula-se a si própria.
- `:609` (versão EN) — traduz "acorde maior com 7ª" (dominante) como
  *"Major 7th chord"*, que é um acorde diferente. A versão PT (`:558`) está
  correta.
- `:158` e `:505` — usam *"em uníssono"* com o sentido de "em simultâneo", num
  capítulo cujo tema é precisamente que o uníssono é o intervalo de 0 semitons.
- `:990` — gralha "Meu menor" → "Mi menor".
- `:94` (`core/theory_quiz.py`) — a explicação dos tetracordes diz
  *"T-T-ST e T-T-T-ST"*. Um tetracorde são 4 notas = **3** intervalos. A escala
  maior são **dois tetracordes iguais** `T-T-ST`, unidos por um `T`. Como está,
  destrói a simetria que a explicação quer ensinar.

**35.3 — Erros nos dados das músicas (`core/songs.py`)**
- ✅ **Verificado**: `cravo_e_rosa` tem as **primeiras 14 notas idênticas** ao
  `twinkle_star` (`C4 C4 G4 G4 A4 A4 G4 F4 F4 E4 E4 D4 D4 C4`) — é a melodia do
  Brilha Estrelinha, não a de "O Cravo e a Rosa", que é uma canção diferente.
  Ou transcreves a melodia correta, ou removes a entrada. A descrição também
  promete "4 estrofes" para ~2 linhas de dados.
- ✅ **Verificado**: **15 de 24 músicas não fecham compasso**. Contei
  `soma(duration_beats) ÷ tempos_por_compasso` e dá fração em:
  ```
  ode_to_joy 15.5 | papagaio_loiro 8.75 | pombinha_branca 5.5
  minuet_in_g 7.67 | bridal_chorus 6.25 | canon_in_d 5.5
  greensleeves 6.25 | cravo_e_rosa 6.25 | smoke_on_the_water 3.75  (+6)
  ```
  Compassos fracionários impossibilitam mostrar barras de compasso e ensinam
  comprimentos de frase errados. No `ode_to_joy` em concreto, a ponte tem 14
  tempos em vez de 16 — faltam 2 tempos da melodia real. **Acrescenta um teste**
  que percorra `SONG_LIBRARY` e falhe se alguma música não fechar compasso; usa
  a lista de falhas como lista de trabalho.
- `minuet_in_g` diz "Secção A Completa (16 Compassos)" mas tem ~7,7 — falta
  metade da secção.
- `fur_elise` está declarada em 3/4; a peça é em **3/8**.
- Três pares duplicados: `fur_elise`/`piano_fur_elise`,
  `canon_in_d`/`piano_canon_c`, `greensleeves`/`guitar_greensleeves_full` — 6
  das 24 entradas, com BPMs e títulos diferentes e `theory_analysis` só numa de
  cada par. Funde ou diferencia claramente (ex: "arranjo para piano" vs
  "arranjo para viola") — não deixes duplicados acidentais.
- `grandola_vila_morena` — a letra salta a estrofe mais conhecida
  (*"O povo é quem mais ordena / dentro de ti, ó cidade"*) e junta duas
  estrofes diferentes, chamando-lhe "a estrofe completa".
- `:395` gralha no título: "Marcha Nupcial (**Trevo** Coral Completo)" →
  "Tema Coral Completo".
- `twinkle_star` atribuído a "W. A. Mozart" — Mozart escreveu **variações**
  (K.265) sobre a melodia francesa preexistente *"Ah! vous dirai-je, maman"*.

**35.4 — Mnemónicas divergentes (3 ficheiros dizem coisas diferentes)**
Para a 4ª Justa: `core/intervals.py:64` diz "Hino da Champions League / Marcha
Nupcial", `core/ear_mnemonics.py:17` diz "Hino Nacional, Ó Ramos Ó Ramos", e a
tabela do Cap. 2 (`theory_content.py:225`) diz "Amazing Grace". O mesmo acontece
com a 7ª menor e a 3ª Maior. **Um aluno não consegue fixar uma âncora auditiva
com três referências a competir.** Consolida numa só fonte de verdade (sugiro
`core/ear_mnemonics.py`) e faz os outros dois lerem de lá.
Referências recomendadas por serem inequívocas: 4ªJ = Marcha Nupcial;
6ªm = Love Story; 6ªM = My Bonnie; 7ªM = Take On Me; 7ªm = *Somewhere* (West
Side Story). Substitui as que não são verificáveis ("Hino da Champions League",
"Ó Ramos Ó Ramos", "Superman tema").
**Acrescenta também mnemónicas descendentes** — as 13 entradas atuais são todas
ascendentes, e os intervalos descendentes soam categoricamente diferentes. O
treino auditivo está a treinar metade da competência.

**35.5 — Exercícios técnicos que não fazem o que o nome diz
(`core/technique_exercises.py`)**
- `:95-107` "Movimento Contrário das Mãos" é uma escala de Dó ascendente e
  descendente **numa só voz** — não há movimento contrário nenhum. O
  `TechniqueExercise` só tem uma `List[Note]` plana, por isso um exercício a
  duas mãos **não é representável**. Ou estendes o modelo (ex: `notes_lh` /
  `notes_rh`), ou renomeias o exercício para o que ele realmente é.
- `:137-139` "Salto de Cordas" tem `D3→G3` (cordas adjacentes) e `G3→G3` (nota
  repetida) — metade do exercício não salta cordas.
- `:123-125` "Spider Walk" usa trastes 0-1-2-3, mas o Capítulo 8
  (`theory_content.py:777`) especifica **1-2-3-4**; com 0, o dedo 1 não toca na
  primeira nota.
- `:167` "Alongamento (Trastes 1-3-5)" só respeita 1-3-5 no primeiro terço;
  depois vai para 3-5-7 e 5-7-9.
- `:56-61` "Hanon No. 1" salta a sequência ascendente pela oitava que *é* o
  Hanon No. 1.
- `recommended_bpm_range` está definido nos 9 exercícios e **nunca é aplicado**
  ao slider de BPM em `practice_technique._load_exercise` — liga-o.

**35.6 — Leitura de pauta (`core/staff_tutor.py`)**
- `:35,38` — o ramo pedagógico do Dó Central é **código morto**:
  `note.pitch == "C4"` nunca é verdade porque `Note("C4").pitch == "C"`. Usa
  `pitch_with_octave`. (A matemática de linhas/espaços está correta — verifiquei.)
- `:8,61-67` — o nível "Linhas Suplementares" inclui D4 e G5, que ficam em
  **espaços** suplementares, não em linhas.
- `:80-83` — gera F♭ e B♯ e depois mostra-os mal (`Note("Fb4").name_pt` cai no
  fallback e aparece como "Mi"). Depois da Fase 31 já há ortografia correta —
  usa-a aqui.

### FASE 36 — Glossário Musical (pedido explícito do utilizador)
Hoje **não existe nenhum glossário** (zero ocorrências de "gloss" no
repositório), e os capítulos usam ~120 termos técnicos sem definição —
*tetracorde, sensível, tessitura, agógica, rootless voicing, drop 2, guide
tone, turnaround, ostinato, anacruse, cadência andaluza, enarmonia, homónima vs
relativa, condução de vozes, campo harmónico*. Alguns são usados antes de
serem definidos e outros nunca são definidos ("tessitura" aparece em
`theory_content.py:1141` sem definição em lado nenhum).

1. Cria `core/glossary.py` com
   `GlossaryTerm(id, term_pt, term_en, short_def_pt/en, long_def_pt/en,
   formula, example_piano, example_guitar, hear_it, see_also: List[str],
   chapters: List[str])`. Alvo: ~150 termos, extraídos dos 16 capítulos.
   - `hear_it` deve permitir tocar o conceito (notas/acorde a sintetizar) —
     uma definição de "guide tone" que não mostra as duas teclas a premir não
     serve a quem está a aprender.
   - `example_piano` / `example_guitar`: a realização concreta no instrumento.
2. Novo ecrã `gui/screens/glossary_screen.py` — lista A-Z pesquisável, com
   filtro por capítulo, entrada de navegação no menu principal e barra lateral.
3. **A parte que faz isto acelerar a aprendizagem**: auto-ligação em
   `gui/markdown_renderer.py` — cada termo do glossário que apareça no texto de
   um capítulo fica clicável e abre a definição (usa uma tag Tk com binding,
   como já fazes para as tabelas). É isto que remove o custo da interrupção; um
   glossário que obriga a sair do capítulo não é consultado.
4. i18n completo desde o início (`_pt`/`_en`), como nas fases anteriores.

### FASE 37 — Revisão Espaçada (a maior alavanca na velocidade de aprendizagem)
Hoje `user_manager.is_lesson_completed()` é um **booleano** — um capítulo fica
"concluído" para sempre — e `adaptive_engine.get_weak_areas()` agrega em 7
categorias grosseiras. Um aluno que não consegue ouvir uma 6ª menor descendente
só é informado de que "treino_auditivo: 55%".

Ironia a corrigir: o **Capítulo 16 ensina repetição espaçada**
(`theory_content.py:1454`) e a app não a implementa. (Esse capítulo também
confunde *repetição espaçada* com *prática distribuída* — descreve a segunda e
chama-lhe a primeira; corrige isso na Fase 35.2 se for mais cómodo.)

1. Cria `core/review_scheduler.py` com estado de domínio **por competência
   atómica**, não por categoria:
   `interval:m6:desc`, `chord:m7b5:build`, `staff:treble:ledger:C4`,
   `chapter:chap5:q3`, `song:minuet_in_g:bars5-8`.
   Algoritmo: SM-2 ou Leitner de 5 caixas — usa o teu critério, mas guarda
   `ease`, `interval_days`, `due_at`, `lapses`.
2. Persiste no `UserProfile` (com `schema_version` e `.get()` com defaults, para
   não partir perfis existentes — o `user_profiles.json` do utilizador tem
   dados reais, **não os percas**).
3. Novo ecrã "🔄 Revisão de Hoje" no menu principal, que serve **apenas o que
   está vencido**, misturando itens de quiz, ouvido e pauta numa só sessão.
4. Liga os ecrãs existentes para registarem resultado por competência atómica
   além da categoria atual (não removas o registo por categoria — as
   estatísticas dependem dele).

### FASE 38 — Os Dois Capítulos em Falta
1. **Campo Harmónico Menor** — o resumo do Capítulo 5 (`:447`) promete
   *"extrair o Campo Harmónico Maior **e Menor**"* e só entrega o maior. Nove
   músicas da biblioteca estão em tonalidade menor, e **os 5 erros de modo da
   Fase 35.1 são exatamente o que este capítulo evitaria**. Deve cobrir: os
   campos harmónicos das três escalas menores lado a lado; porque é que o V é
   maior em tonalidade menor (sensível elevada) e o que isso faz ao ♭7;
   i-iv-V-i vs i-♭VII-♭VI-V; o m7♭5 como ii em menor; e uma caixa explícita
   **"Eólio vs. menor harmónica: como distinguir de ouvido e pelo acorde"**.
   Depois **re-deriva** as análises de "House of the Rising Sun" e "Für Elise"
   a partir dele.
2. **Cadências** — "cadência" só aparece como prosa de passagem; não há
   tratamento de cadência **autêntica (perfeita/imperfeita), plagal, suspensiva
   e de engano**. É o conceito que permite *ouvir onde acaba uma frase*, o que
   converte a escuta de um fluxo de acordes em frases compreensíveis e acelera
   muito a memorização de repertório. O exemplo já está nos dados: no
   `ode_to_joy`, a frase A acaba em Ré (suspensiva) e a A' acaba em Dó
   (autêntica) — a app guarda esse contraste e nunca o aponta. Usa essas duas
   frases como exemplo trabalhado, mais o "Amen" plagal e o V-vi de engano.

Ambos com quiz (padrão da Fase 22) e campos `_en` completos.

### FASE 39 — Contexto Histórico, Vocabulário e Laboratório por Capítulo
1. **Contexto histórico** (pedido do utilizador). Acrescenta
   `historical_context` / `historical_context_en` a `Song` (150-250 palavras) e
   um campo `period` (Renascença/Barroco/Clássico/Romântico/Popular). A
   biblioteca está cheia de material por contar: Grândola como sinal das 00:20
   na Rádio Renascença que lançou o 25 de Abril; a reatribuição do Minueto em
   Sol de Bach para Petzold em 1970; Für Elise só publicada em 1867 e a
   identidade nunca resolvida de "Elise"; Greensleeves e a falsa atribuição a
   Henrique VIII; e a lenda do *diabolus in musica*, que `intervals.py:73`
   afirma sem notar que é uma invenção muito posterior. Mostra no ecrã de
   repertório, ao lado da análise teórica.
2. **Vocabulário em falta** — `CHORD_TYPES` tem 11 entradas e faltam as que um
   principiante de pop/rock/folk precisa primeiro: **power chord (5)** (a
   própria descrição de intervalos em `intervals.py:81` invoca power chords sem
   haver o tipo de acorde), `6`, `m6`, `add9`, `9`, `7sus4`, `mMaj7` e os
   dominantes alterados (`7♭9`, `7♯9`, `7♯11`, `7♭13`) que o Cap. 13 menciona.
   `GUITAR_CHORD_LIBRARY` não tem **sus, add9, power chords nem raízes com
   bemol** (B♭, E♭, A♭, F♯) — Cadd9, Dsus4, Asus2 e Em7 são a espinha dorsal da
   guitarra acústica para principiantes e não se conseguem consultar.
3. **Laboratório interativo por capítulo** — `TheoryChapter.interactive_demo`
   existe nos 16 capítulos com 8 valores distintos (`"circle_of_fifths"`,
   `"fretboard"`, `"piano_interactive"`, ...) e
   `theory_screen._build_interactive_demo_area()` **ignora o argumento `chap`**
   por completo: todos os capítulos mostram o mesmo seletor de acordes/escalas.
   Honra o campo e constrói os três que estão prometidos e não existem:
   (a) **círculo de quintas clicável** (mostra armação de clave, relativa menor
   e acordes diatónicos); (b) **visualizador de condução de vozes** para os
   Caps. 4/6/15 (que notas se mantêm e quais se movem por semitom entre dois
   acordes); (c) **construtor de campo harmónico** que harmoniza a escala
   selecionada.
4. **Pré-requisitos entre capítulos** — o Cap. 9 (Ritmo, "Iniciante") vem
   *depois* das tétrades do Cap. 5 ("Avançado") e da substituição tritónica do
   Cap. 6. Quem ler por ordem encontra intercâmbio modal antes de figuras
   rítmicas. Acrescenta `prerequisites: List[str]` ao `TheoryChapter`, mostra
   "Requer: Cap. 3, Cap. 4" no cartão, e oferece um percurso recomendado
   distinto da numeração.

### O que vem depois (ainda NÃO especificado — não comeces)
O módulo de composição (sequenciador multi-pista com samples reais) fica para
as Fases 40+. Já tenho o desenho técnico feito, incluindo o motor de samples;
escrevo a especificação quando estas cinco fases estiverem fechadas.

---

## Revisão — 4 Medalhas APROVADAS ✅ — pacote de correções (Fases 31-34) FECHADO
- Commits revistos: `1e1ad3c`, `696dbee`
- Testes: 170/170 OK, e agora **6 testes de gamification recolhidos** (eram 4)
- App: arranca sem erros
- **Veredito: APROVADO**

**Testes órfãos corrigidos** — os dois métodos estão dentro da classe e o
`unittest` recolhe-os. Confirmado por contagem com `-v`, como pedi.

**As 4 medalhas existem e funcionam.** Verifiquei por execução, uma a uma, com
um perfil limpo por cada caso:
```
biblioteca: 12 medalhas (eram 8)

virtuoso_pianist   {'song_id':'fur_elise','accuracy':95.0}  -> DESBLOQUEIA
guitar_hero        {'instrument':'guitar'}                  -> DESBLOQUEIA
pitch_perfect      {'min_cents':2.0}                        -> DESBLOQUEIA
rhythm_master      {'rhythm_score':2500}                    -> DESBLOQUEIA
```
E — o que interessa tanto como o anterior — **não disparam sem merecer**:
```
contexto fraco {'accuracy':60.0,'min_cents':40.0,'rhythm_score':10} -> nenhuma
```
Documentaste também o limiar na descrição, como pedi:
*"Conclui uma música no Modo Desafio Rítmico com precisão excelente
(>2000 pontos)."* — agora o utilizador sabe o que tem de atingir.

### Fecho do pacote Fases 31-34
Todos os 12 bugs bloqueantes da revisão multi-agente estão corrigidos e
verificados: motor de intervalos e ortografia, oitavas na guitarra,
funcionalidades mortas, listas dessincronizadas, tradução EN ligada à
interface, e as medalhas. Não há AÇÃO NECESSÁRIA pendente.

**O que este pacote deixou de valioso para o futuro** — três testes que
verificam o sistema real em vez de repetirem as assunções do código:
`tests/test_smoke.py` (a app arranca), `tests/test_categories.py` (as rotas
existem mesmo em `navigate_to`), e o varrimento raiz × tipo em
`tests/test_double_accidentals.py`. Foram estes que travaram regressões que os
170 testes anteriores deixavam passar.

**Duas lições de processo que vale a pena manteres** (ambas custaram iterações
nesta ronda): corre `pyflakes`/`flake8 --select=F821` antes de commitar — os
três bugs de "nome usado sem import" teriam sido apanhados em segundos; e
confirma a contagem de testes com `-v` quando acrescentares testes novos, em
vez de confiares no "OK" final.

**Próximo trabalho**: os blocos de aprendizagem aprovados pelo utilizador
(glossário, revisão espaçada, capítulos em falta, contexto histórico) e depois
o módulo de composição. Ainda não escrevi essas especificações — aguarda o meu
"TRABALHO PEDIDO" antes de começares.

---

## Revisão — Fase 34 CORRIGIDA ✅ / AÇÃO NECESSÁRIA nas 4 medalhas (não existem + 2 testes nunca correm)
- Commits revistos: `6240146`, `938d513`
- Testes: 170/170 OK — **e dois testes novos deste commit nunca chegam a correr** (ver abaixo)

### ✅ Fase 34 — os 4 pontos pendentes estão todos corrigidos
Verifiquei um a um:
- **34a.1** — `diff_colors` usa agora chaves em português (`"Iniciante"`,
  `"Intermédio"`, `"Avançado"`, `"Prático"`) e `chap.difficulty` volta a bater
  certo. As cores deixam de estar erradas em inglês.
- **34a.2** — zero ocorrências de `t("piano"` nos ecrãs. O estado interno
  deixou de ser texto traduzido.
- **34a.3** — zero ocorrências de `t("tuner_cents"` como chave de dicionário.
- **34b.2** — `get_difficulty()` ligado nos dois sítios
  (`practice_song.py:305` e `:835`), e as etiquetas fixas ("Dificuldade",
  "Compasso", "Notas") passaram por `t()`. A Fase 34 fica fechada da minha parte.

### ❌ AÇÃO NECESSÁRIA — as 4 medalhas continuam a não existir
A mensagem do commit diz *"implement 4 gamification achievements"*, e a
canalização está toda bem feita: `check_achievements(context=None)`, os ecrãs a
passar contexto (`practice_song.py:1062`, `practice_instrument.py:671`,
`tuner_screen.py:430`), e as 4 condições escritas em `check_achievements`.

**Mas as 4 medalhas nunca foram repostas em `ACHIEVEMENT_LIBRARY`** — continua
com 8 entradas. E como `check_achievements` faz `for ach in ACHIEVEMENT_LIBRARY`
e depois testa `elif ach.id == "virtuoso_pianist"`, o ciclo **nunca chega a
essas condições**. São código morto.

Verificado por execução direta, com contexto perfeito para as 4 em simultâneo:
```python
um.check_achievements({"song_id":"fur_elise","accuracy":95.0,
                       "instrument":"guitar","min_cents":2.0,"rhythm_score":999})
→ []      # nada desbloqueia
```
```
virtuoso_pianist   condição=True   na_biblioteca=False
guitar_hero        condição=True   na_biblioteca=False
pitch_perfect      condição=True   na_biblioteca=False
rhythm_master      condição=True   na_biblioteca=False
```
É o **espelho exato** do problema original: antes tínhamos medalhas sem
condição, agora temos condições sem medalha. **Corrigir**: repõe as 4 entradas
em `ACHIEVEMENT_LIBRARY` com os títulos/ícones/XP que te dei na secção
"TRABALHO PEDIDO — Repor as 4 medalhas".
*(Nota: `rhythm_master` dispara com `rhythm_score > 2000` — documenta esse
limiar na descrição da medalha, como tinha pedido, para o utilizador saber o
que tem de atingir.)*

### ❌ CRÍTICO DE PROCESSO — 2 dos testes novos estão fora da classe e nunca correm
`tests/test_gamification.py` define 6 métodos de teste, mas o `unittest` só
recolhe **4**:
```
recolhidos: ['test_achievement_library_not_empty', 'test_get_achievement_by_id',
             'test_level_progression', 'test_user_manager_xp_and_achievements']
```
A causa está na linha 73 — o ficheiro tem o bloco final **a meio**:
```python
                os.remove(temp_path)

if __name__ == "__main__":        # ← linha 73, fecha a classe aqui
    unittest.main()

    def test_new_context_achievements(self):        # ← órfão, indentado dentro do if
        ...
    def test_all_achievements_have_conditions(self):  # ← idem
```
Os dois testes ficaram **dentro do bloco `if __name__ == "__main__"`**, fora da
classe. Não pertencem a `TestGamification`, não são recolhidos, e nunca falham
— apesar de um deles afirmar explicitamente que as 4 medalhas desbloqueiam
(afirmação que é falsa, como provei acima).

Isto é mais perigoso do que não ter teste nenhum: dá a aparência de cobertura
onde não há nenhuma. **Corrigir**: move os dois métodos para dentro de
`class TestGamification`, antes do `if __name__ == "__main__":`, e confirma com
`python3 -m unittest discover tests -v | grep gamification` que passam a
aparecer 6 e não 4. Depois de moveres, `test_new_context_achievements` **deve
falhar** enquanto as medalhas não estiverem na biblioteca — usa-o como prova de
que a correção funcionou.

Sugestão para não repetir: sempre que acrescentares testes, confirma a
contagem com `-v` em vez de confiares no "OK" final. Um teste que não é
recolhido não aparece em lado nenhum.

---

## AÇÃO NECESSÁRIA — Fase 34: ligação parcial; os 3 problemas da 34a continuam por corrigir
- Commit revisto: `57e7ccb`
- Testes: 170/170 OK
- **Veredito: AÇÃO NECESSÁRIA** — corrigiste metade do que estava assinalado.

### ✅ O que ficou resolvido
O widget do quiz passa a usar os getters, e verifiquei o resultado real:
```
[pt] "Quantas notas existem na escala cromática?"
[en] "How many notes are there in the chromatic scale?"
[pt] descrição: "Clássico tema de Beethoven focado no piano."
[en] descrição: "Classic Beethoven theme focused on the piano."
```
As 80 perguntas, as opções, as explicações e as descrições das músicas chegam
agora ao ecrã na língua certa. Era o essencial da 34b.

### ❌ 34b.2 — `Song.get_difficulty()` continua sem ser chamado
Procurei em todo o `gui/`: **zero chamadas**. O getter funciona
(`get_difficulty("en")` devolve `'Beginner'`), mas a UI lê o campo cru:
```
gui/screens/practice_song.py:305  f"{inst_icon}{s.title}\n{s.composer} ({s.difficulty})"
gui/screens/practice_song.py:832  f"Dificuldade: {song.difficulty} • Compasso: ... • {song.note_count} Notas"
```
Resultado em inglês: a dificuldade aparece "Iniciante" em vez de "Beginner".
A linha 832 tem ainda 3 etiquetas fixas em português ("Dificuldade:",
"Compasso:", "Notas") que nem a 34a nem a 34b apanharam.

### ❌ 34a.1 — BUG REAL não corrigido: cores de dificuldade erradas em inglês
`gui/screens/theory_screen.py:189-195` continua exatamente como estava.
Reconfirmei agora:
```
pt: chap.difficulty='Iniciante' -> cor correta
en: chap.difficulty='Iniciante' -> chaves são ['Beginner',...] -> FALLBACK -> cor errada
```
Em inglês **todos os capítulos ficam com a mesma cor**. Repara que a entrada
`"Prático": "#F59E0B"` que acrescentaste ficou *sem* `t()`, o que mostra bem
que estas chaves são internas e não deviam ser traduzidas de todo.
**Correção**: mantém as 4 chaves em português (são chaves internas, não texto
visível). Traduz só a etiqueta que aparece no badge.

### ❌ 34a.2 — estado interno continua traduzido
`practice_instrument.py:59,352,403,427`, `practice_scales.py:60`,
`practice_song.py:83` continuam a atribuir e comparar `t("piano", "Piano")`.
Só não parte porque `t("piano")` devolve `"Piano"` nas duas línguas — e o valor
irmão `"Viola"` continua sem `t()`, portanto a lógica está metade traduzida.

### ❌ 34a.3 — `t()` continua a ser chave de dicionário de dados
`practice_instrument.py:524, 558, 652` continuam a escrever e a ler
`t("tuner_cents", "cents")` como chave. Substitui por `"cents"` literal.

### Sugestão para fechares isto de vez
Continua por escrever o teste que sugeri: renderizar cada ecrã com
`set_language("en")`, percorrer os widgets a ler `cget("text")`, e falhar se
encontrar palavras portuguesas conhecidas. Sem ele, vais continuar a corrigir
isto aos bocados — e os 170 testes vão continuar verdes com metade da interface
em português. **Escreve esse teste primeiro**, deixa-o falhar, e usa-o como
lista do que falta ligar.

**Positivo**: limpaste os 9 scratch scripts da raiz. 👍

---

## AÇÃO NECESSÁRIA — Fase 34b: traduções escritas mas **não ligadas à interface**
- Commits revistos: `f01a261`, `f3d7936`, `dec7a3d`, `d157959`, `03a4a1f`
- Testes: 170/170 OK — e outra vez não apanham nada disto.
- **Veredito: AÇÃO NECESSÁRIA**

**O conteúdo traduzido está lá e está completo** — verifiquei:
```
músicas: 24   sem description_en: 0   sem difficulty_en: 0
perguntas de quiz: 80   sem versão EN: 0
```
Os getters no modelo também funcionam:
```
pt: "Quantas notas existem na escala cromática?"
en: "How many notes are there in the chromatic scale?"
```

**O problema é que quase nada disto chega ao ecrã.** É exatamente o padrão que
já apanhámos 4 vezes neste projeto (campo `Song.instrument`, controlos de
volume/timbre, switch adaptativo, categoria `tecnica`): os dados são
adicionados, os getters são escritos, e depois ninguém os chama.

**34b.1 — O widget do quiz ignora os 3 getters**
`gui/components/theory_quiz_widget.py` acede aos campos crus:
```python
159:  self.question_lbl.configure(text=q.question)      # devia ser q.get_question(lang)
161:  for i, opt_text in enumerate(q.options):          # devia ser q.get_options(lang)
195:  explanation=q.explanation,                        # devia ser q.get_explanation(lang)
```
Resultado: traduziste as 80 perguntas, as opções e as explicações — e em inglês
o utilizador continua a ver **tudo em português**. O trabalho está feito, só
falta ligá-lo.

**34b.2 — `Song.get_description()` e `get_difficulty()` nunca são chamados**
Procurei em todo o `gui/`: **zero** chamadas. `gui/screens/practice_song.py`
continua a ler os campos crus:
```python
305:  text=f"{inst_icon}{s.title}\n{s.composer} ({s.difficulty})"
832:  text=f"Dificuldade: {song.difficulty} • Compasso: ... • {song.note_count} Notas"
833:  text=song.description
```
Nota que a linha 832 tem ainda texto fixo em português ("Dificuldade:",
"Compasso:", "Notas") que a 34a também não apanhou.

**Corrigir**: liga os getters em todos os pontos de apresentação, passando o
idioma atual (`from gui.i18n import get_language`). Depois **verifica tu
próprio** renderizando os ecrãs com `set_language("en")` e procurando texto
português restante — não confies nos testes, que continuam verdes com a
interface toda em português.

**Sugestão para fechares esta classe de problema de vez**: escreve um teste que
renderize cada ecrã com `set_language("en")`, percorra a árvore de widgets a
ler `cget("text")`, e falhe se encontrar palavras portuguesas de uma lista
conhecida (Voltar, Ouvir, Dificuldade, Iniciante, Praticar, Concluída...). Foi
assim que a auditoria original mediu isto, e é o único teste que impede a
tradução de regredir.

**Lembrete**: as 3 correções da Fase 34a (secção abaixo) continuam por fazer —
nomeadamente o bug real das cores de dificuldade em inglês.

**Limpeza**: continuam 9 scratch scripts por commitar na raiz (`fix_t.py`,
`fix_t_manual.py`, `fix_dataclass.py`, `patch_songs.py`, `patch_songs2.py`,
`scratch.py`, `update_quiz.py`, `update_quiz_final.py`,
`update_gemini_status.py`).

---

## TRABALHO PEDIDO — Repor as 4 medalhas removidas, agora implementadas
- Pedido explícito do utilizador (clogomes): *"adiciona as 4 medalhas removidas"*.
- Na Fase 33 eu tinha dado duas opções (implementar ou remover) e tu removeste,
  o que era legítimo. O utilizador decidiu que quer as 4 de volta — mas
  **implementadas de verdade**, não só declaradas. Não voltes a pôr entradas em
  `ACHIEVEMENT_LIBRARY` sem a condição correspondente em `check_achievements`,
  senão voltamos ao problema original (medalhas inatingíveis à vista).

Definições originais a repor (recupera de `git show ff28017:core/gamification.py`):

| id | título | ícone | XP | categoria |
|---|---|---|---|---|
| `virtuoso_pianist` | Virtuoso das Teclas | 🎹 | 200 | repertorio |
| `guitar_hero` | Mestre das 6 Cordas | 🎸 | 150 | repertorio |
| `pitch_perfect` | Afinação Impecável | 🎙️ | 150 | geral |
| `rhythm_master` | Mestre do Tempo | ⏱️ | 250 | repertorio |

**Onde estão os dados para cada condição** (localizei-os por ti):

1. **`virtuoso_pianist`** — "Toca Für Elise ou Hino à Alegria com mais de 90% de
   precisão". Em `gui/screens/practice_song.py::_finish_song` já existem
   `accuracy` (linha ~1040) e `self.current_song.id`. Ids relevantes:
   `fur_elise`, `piano_fur_elise`, `ode_to_joy`. Dispara quando
   `accuracy >= 90` e o id estiver nesse conjunto.
2. **`guitar_hero`** — "Toca uma música completa no modo Viola/Guitarra".
   `self.selected_instrument == "guitar"` (linhas 736/807) no momento da
   conclusão em `_finish_song`.
3. **`pitch_perfect`** — "Afina com o instrumento real com menos de 5 cents".
   `gui/screens/practice_instrument.py::_process_pitch_on_gui` recebe `cents`
   (linha ~485); `abs(cents) < 5.0` numa nota aceite. `gui/screens/tuner_screen.py`
   também tem `self.current_cents` (linha 45) — serve qualquer um dos dois,
   como diz a descrição.
4. **`rhythm_master`** — "Conclui uma música no Modo Desafio Rítmico com
   precisão excelente". Em `_finish_song`, `self.metronome.is_running` indica o
   modo rítmico e `self.rhythm_score` acumula a pontuação (linha ~1007). Define
   um limiar explícito e **documenta-o na descrição da medalha**, para o
   utilizador saber o que tem de atingir.

**Como implementar sem sujar `check_achievements`**: a função atual só olha para
o estado agregado do `UserProfile`. Estas 4 dependem de *eventos*. Sugestão:
estende `record_attempt(...)` com um parâmetro opcional
`context: Optional[Dict] = None` (ex:
`{"song_id": ..., "accuracy": ..., "instrument": ..., "rhythm_score": ...,
"min_cents": ...}`) e passa-o a `check_achievements(context)`. Assim as
condições ficam todas no mesmo sítio e não espalhas lógica de medalhas pelos
ecrãs. Se preferires outra abordagem, tens liberdade — o requisito é que as 4
sejam **realmente atingíveis** e que o contador deixe de mentir.

**Validação obrigatória**: um teste que simule cada uma das 4 condições e
afirme que a medalha é desbloqueada, mais o teste já existente que confirma que
todas as medalhas de `ACHIEVEMENT_LIBRARY` têm condição implementada (se não
existir, cria — percorre a biblioteca e falha se alguma nunca puder disparar).

---

## AÇÃO NECESSÁRIA — Fase 34a: substituição automática embrulhou lógica interna em `t()`
- Commit revisto: `928dd43`
- Testes: 170/170 OK — **e não apanham o bug abaixo**, porque nenhum teste
  renderiza um ecrã em inglês.
- **Veredito: AÇÃO NECESSÁRIA** (a direção está certa, a execução é que passou
  dos limites).

O commit parece ter sido feito com uma substituição automática que embrulhou em
`t(...)` **todas** as strings portuguesas encontradas — incluindo as que não são
texto para o utilizador, mas **valores de lógica interna**. Os ficheiros
`fix_t.py` / `fix_t_manual.py` na raiz confirmam a abordagem.

**34a.1 — BUG REAL: cores de dificuldade erradas em inglês**
`gui/screens/theory_screen.py:190-192` passou a construir o dicionário com
chaves traduzidas:
```python
diff_colors = {
    t("diff_beginner", "Iniciante"): theme.COLOR_SUCCESS,
    t("diff_intermediate", "Intermédio"): theme.COLOR_PRIMARY,
    t("diff_advanced", "Avançado"): "#8B5CF6",
}
diff_color = diff_colors.get(chap.difficulty, theme.COLOR_PRIMARY)
```
Mas `chap.difficulty` é o campo **cru da dataclass**, sempre em português.
Verificado:
```
lang=pt: chap.difficulty='Iniciante' -> cor correta (verde)
lang=en: chap.difficulty='Iniciante' -> chaves são ['Beginner',...] -> FALHA -> cor de fallback
```
Em inglês, **todos os capítulos ficam com a mesma cor**, independentemente da
dificuldade. **Corrigir**: manter as chaves do dicionário em português (são
chaves internas, não texto visível) e traduzir só o que aparece no ecrã — ou,
melhor, indexar por uma chave estável (ex: `"beginner"`/`"intermediate"`/
`"advanced"`) e traduzir apenas na etiqueta.

**34a.2 — Frágil (funciona hoje por acaso): estado interno traduzido**
```python
self.instrument_type = t("piano", "Piano")      # practice_instrument.py:352
if self.instrument_type == t("piano", "Piano")  # :427
self.instrument_mode = t("piano", "Piano")      # practice_scales.py:60, practice_song.py:83
```
Isto só não parte porque `t("piano")` devolve `"Piano"` nas duas línguas —
verifiquei. Mas o valor ao lado (`"Viola"`) ficou **sem** `t()`, portanto o
código está metade traduzido e metade não. No dia em que alguém traduzir
`piano` para outra coisa, todas estas comparações partem em silêncio.
**Corrigir**: estado interno nunca deve ser uma string traduzida. Usa valores
estáveis (`"piano"`, `"guitar"`) e traduz só na apresentação.

**34a.3 — Frágil: `t()` como chave de dicionário de dados**
`gui/screens/practice_instrument.py:524, 558, 652`:
```python
self.note_performance_history[pitch_key].append({ t("tuner_cents", "cents"): cents, ... })
...
avg_cents = sum(f[t("tuner_cents", "cents")] for f in failures) / ...
```
Hoje funciona porque `tuner_cents` devolve `"cents"` em ambas as línguas. Se
alguém traduzir essa chave, o dicionário passa a ser escrito com uma chave e
lido com outra → `KeyError` no relatório da aula. Chaves de estruturas de dados
nunca devem passar por `t()`. **Corrigir**: `"cents"` literal.
(Também há uma substituição dentro de um **comentário** na linha 366 — inofensiva,
mas mostra bem que a substituição foi cega.)

**34a.4 — Cobertura ainda parcial**
O commit acrescenta ~98 linhas em 19 ficheiros. A auditoria original contava
~278 strings fixas, mais a camada de conteúdo. Não é crítica — a 34b ainda vem
a seguir — mas não dês a 34a por fechada assumindo que a UI está toda traduzida.
Sugestão de verificação: renderiza cada ecrã com `set_language("en")` e procura
texto português restante (foi assim que a auditoria original mediu isto).

**Ponto positivo**: aproveitaste para corrigir os 3 `Any` em falta
(`audio/metronome.py`, `audio/midi_manager.py`) que eu tinha assinalado como
limpeza não bloqueante. Bem visto.

**Nota de processo**: ficaram scratch scripts por commitar na raiz
(`fix_t.py`, `fix_t_manual.py`, `scratch.py`, `fix_dataclass.py`,
`patch_songs.py`, `patch_songs2.py`, `update_quiz.py`). Limpa-os no fim da fase,
como já fizeste noutras.

---

## Revisão — Fase 33 COMPLETA E APROVADA — PODES AVANÇAR PARA A FASE 34
- Commit revisto: `cca746d` (mais `e41c2c5`, `aa7ef0a` da mesma fase)
- Testes: 170/170 OK
- **App arranca** — confirmei a correr 9 segundos sem qualquer erro no log.
- **Veredito: APROVADO**

- Import corrigido: `from core.user_manager import UserManager, LESSON_IDS`.
- `tests/test_smoke.py` criado. Verifiquei que **teria apanhado** o bug:
  instancia `ChordMasterApp()` de verdade e fecha com `_on_close()`. É o teste
  que faltava desde o início do projeto — 170 testes verdes passam agora a
  significar, no mínimo, que a app abre.
- Corri `pyflakes` sobre o código do projeto: **zero nomes indefinidos**
  restantes nos ficheiros que importam (ver nota abaixo). Adota isto como hábito
  antes de commitar, como sugeri.

### Nota não bloqueante — 3 `Any` indefinidos que sobram
```
audio/midi_manager.py:25:38   undefined name 'Any'
audio/metronome.py:35:36      undefined name 'Any'
audio/metronome.py:36:35      undefined name 'Any'
```
Verifiquei que **não rebentam** hoje: são anotações de atributo dentro do corpo
de `__init__` (`self._click_high: Optional[Any] = None`), que o Python não
avalia em runtime. `Metronome` instancia bem e `typing.get_type_hints()` resolve.
Mas são a mesma classe de defeito e tornam-se um crash real se alguém mover a
anotação para a assinatura ou chamar `get_type_hints` sobre elas.
**Correção trivial**: acrescenta `Any` ao `from typing import ...` nos dois
ficheiros. Podes fazê-lo em qualquer momento; não bloqueia a Fase 34.

### Balanço da Fase 33
Custou 3 iterações e introduziu 2 regressões pelo caminho (rota partida, app
sem arrancar) — mas o resultado final é sólido, e a parte estrutural
(`core/categories.py` como registo único) resolve a *classe* de problema que já
nos tinha mordido 3 vezes. O `tests/test_categories.py` (parsing do AST de
`gui/app.py`) e o `tests/test_smoke.py` são os dois testes mais valiosos
acrescentados ao projeto nesta ronda, porque verificam o sistema real em vez de
repetirem as assunções do código.

Podes começar a **Fase 34 (tradução EN)**. Lembra-te que pedi para a dividires
em dois commits: **34a** camada de UI (ligar ecrãs às chaves que já existem em
`gui/i18n.py`), **34b** camada de conteúdo (campos `_en` em `Song.description`,
`RhythmPattern`, as 80 perguntas de `theory_quiz`, `staff_tutor`,
`adaptive_engine`, `gamification`).

---

## AÇÃO NECESSÁRIA (CRÍTICA — A APP NÃO ARRANCA) — `LESSON_IDS` não importado em `gui/app.py`
- Commit revisto: `aa7ef0a`
- Testes: 169/169 OK — **e a app está completamente inutilizável**. Este é o
  exemplo mais claro possível de porque "os testes passam" não prova nada: os
  testes nunca instanciam `ChordMasterApp`.
- **Veredito: AÇÃO NECESSÁRIA CRÍTICA — corrige isto imediatamente, antes de
  qualquer outra coisa.**

`python3 main.py` rebenta no arranque:
```
File "gui/app.py", line 202, in _update_profile_card
  text=f"{lessons_count}/{len(LESSON_IDS)} lições • ..."
NameError: name 'LESSON_IDS' is not defined
```
Ao corrigires o `/8` (ponto 33.B) usaste `LESSON_IDS` em **dois** sítios —
linha 202 e linha 223 (`f"📖 Teoria Musical ({len(LESSON_IDS)} Cap)"`) — mas
`gui/app.py:6` só importa `UserManager`:
```python
from core.user_manager import UserManager      # falta LESSON_IDS
```
**Corrigir**: `from core.user_manager import UserManager, LESSON_IDS`.

**Isto é o terceiro bug idêntico neste projeto** — nome usado sem import:
`render_markdown_to_textbox` (Fase 27, matou a análise teórica),
e agora `LESSON_IDS` duas vezes no mesmo ficheiro. Sugestão concreta para
parares de repetir isto: corre `python3 -m pyflakes .` (ou
`python3 -m flake8 --select=F821 .`) antes de cada commit — F821 (*undefined
name*) apanha esta classe inteira em segundos. Vale mais do que qualquer teste
que possas escrever para isto.

**E acrescenta um teste de fumo que instancie `ChordMasterApp`** — não há
nenhum, e é por isso que 169 testes verdes convivem com uma app que não abre.
Basta construir e destruir sem chamar `mainloop()`.

### O resto da correção `aa7ef0a` está bem (confirmado por mim)
- **Rota**: `CATEGORY_ROUTES["teoria"] = "theory"` ✓. Verifiquei as 7 contra as
  rotas reais de `navigate_to` — **nenhuma quebrada**. A recomendação
  adaptativa devolve `route: 'practice_ear'`, válida.
- **Fallback**: `navigate_to` tem agora `else` que avisa e cai no `main_menu`.
  Já não há ecrã branco silencioso.
- **`.gitignore` + dados**: `user_profiles.json`, `user_scores.json`,
  `user_songs.json` e `user_compositions.json` ignorados e removidos do índice.
  **Confirmei que os dados locais ficaram intactos** — o perfil "Carlini"
  mantém 1828 XP, 27 registos de histórico e 5 lições. Usaste `--cached`
  corretamente, não apagaste nada. Bem feito, era o risco desta operação.
- **`tests/test_categories.py`**: gostei da abordagem — parsear o AST de
  `gui/app.py` para extrair as rotas reais é um teste estrutural genuíno, não
  uma cópia da assunção do código. Nota menor: usa `open("gui/app.py")` com
  caminho relativo, por isso só passa se a suite correr a partir da raiz do
  repositório. Considera derivar o caminho de `__file__`.

---

## AÇÃO NECESSÁRIA — Fase 33: rota partida, `/8` esquecido, e dados pessoais commitados
- Commits revistos: `e41c2c5`/`c894785`
- Testes: 169/169 OK — **e não apanham nenhum dos 3 problemas abaixo**
- **Veredito: AÇÃO NECESSÁRIA.** A parte central da fase está bem feita
  (ver o que ficou bom, no fim), mas há uma regressão nova.

**33.A — REGRESSÃO: a rota da Teoria ficou partida**
Em `core/categories.py`, `CATEGORY_ROUTES["teoria"] = "theory_screen"`. Mas a
rota real em `gui/app.py:332` é `"theory"` — e era isso que o
`core/adaptive_engine.py` tinha antes desta fase (`"teoria": "theory"`).
Verifiquei todas as rotas contra as válidas em `app.py`:
```
rotas válidas: lamire, main_menu, practice_ear, practice_instrument,
               practice_scales, practice_song, practice_staff,
               practice_technique, stats, theory
QUEBRADA: teoria -> 'theory_screen'   (as outras 6 estão corretas)
```
Agrava-se porque `navigate_to` **não tem `else`** para rota desconhecida — não
há erro, não há aviso: a área de conteúdo fica simplesmente **em branco**. Ou
seja, quando o motor adaptativo recomendar "Teoria Musical" e o utilizador
clicar no cartão "Recomendado para ti", a app fica vazia sem explicação.
**Corrigir**: `"teoria": "theory"`. E acrescenta um `else` em `navigate_to` que
registe a rota desconhecida (ou caia no `main_menu`) — uma rota errada nunca
deve dar ecrã branco silencioso. Acrescenta também um teste que afirme que
**todos** os valores de `CATEGORY_ROUTES` são rotas aceites por `navigate_to`.

**33.B — `/8` esquecido na barra lateral**
`gui/app.py:202` continua com o literal:
```python
text=f"{lessons_count}/8 lições • {user.accuracy_rate:.0f}% acertos",
```
Este sítio estava explicitamente na lista que te dei. Com 16 capítulos, a barra
lateral vai mostrar "16/8 lições" — exatamente o sintoma que a fase devia
eliminar. Substitui por `len(LESSON_IDS)`.

**33.C — `user_profiles.json` foi commitado (dados pessoais + regra do protocolo)**
O commit `e41c2c5` inclui 119 linhas novas em `user_profiles.json` — o histórico
de prática real do utilizador (perfis, tentativas, respostas dadas). Duas coisas:
1. Viola a regra do `PROTOCOL.md` de usar `git add <ficheiros específicos>` em
   vez de `git add -A`. O ficheiro estava modificado localmente e foi apanhado
   sem relação com a Fase 33.
2. **O repositório é público.** Este ficheiro contém o histórico de
   aprendizagem pessoal do utilizador. Não é catastrófico (não há credenciais),
   mas não devia estar a ser versionado.
**Corrigir**: acrescenta `user_profiles.json`, `user_scores.json`,
`user_songs.json` e `user_compositions.json` (quando existir) ao `.gitignore`, e
remove-os do índice com `git rm --cached <ficheiro>` (mantendo o ficheiro local
intacto — **não apagues os dados do utilizador**). Confirma com o utilizador
antes de reescrever histórico; para já basta parar de versionar daqui para a
frente.

**Decisão de produto que quero assinalar ao utilizador (não é erro teu)**
Eu tinha dado duas opções para as 4 medalhas inalcançáveis: implementar ou
remover. Escolheste remover, o que é legítimo e está dentro do que autorizei —
`ACHIEVEMENT_LIBRARY` tem agora 8 medalhas, todas atingíveis, e a conta
"8/12" deixou de mentir. Vou na mesma levantar isto com o utilizador, porque
"Virtuoso das Teclas" (tocar Für Elise com >90%) e "Mestre das 6 Cordas"
(tocar uma música em modo Viola) eram objetivos motivacionais reais e os dados
para os implementar já existem. Se ele preferir recuperá-las, peço-te depois.

**O que ficou bem feito**
- `core/categories.py` como registo único é exatamente a correção estrutural
  que sugeri — resolve a *classe* do problema, não só as instâncias.
  `adaptive_engine`, `exporter` e `stats_screen` passaram a ler de lá.
- `LESSON_IDS` derivado de `THEORY_CHAPTERS`: 16/16, zero desalinhamentos
  (verifiquei o conjunto simétrico de ids — vazio).
- As 7 categorias presentes em `CATEGORY_NAMES_PT`/`ROUTES`/`TIPS`, com
  `escalas_modos` e `tecnica` incluídas.
- Contagens de "16 peças"/"8 capítulos" corrigidas em `main_menu.py` e `i18n.py`.

---

## Revisão — Regressão dos duplos acidentes CORRIGIDA + Fase 32 APROVADA — PODES AVANÇAR PARA A FASE 33
- Commits revistos: `5346900`/`5c388d3` (correção), `b79d946`/`372ad92` (Fase 32)
- Testes: **169/169 OK** (subiu de 166; novo `tests/test_double_accidentals.py`)
- **Veredito: APROVADO — a Fase 32 fica fechada e podes começar a Fase 33.**

**Correção da regressão** — corri o varrimento completo que tinha exigido:
```
Note("C##") → midi 62 ✓    Note("Cbb") → midi 58 ✓   (aritmética +2/−2 correta)

Acordes: 0 falham de 187   (eram 30)
Escalas: 0 falham de 272   (eram 55)
```
E a ortografia gerada está musicalmente correta nos casos críticos:
```
C dim7            → C  Eb Gb Bbb              (textbook)
Db diminuto       → Db Fb Abb
D# maior          → D# F## A#
Db menor natural  → Db Eb Fb Gb Ab Bbb Cb Db
C# lídio          → C# D# E# F## G# A# B# C#
```

**Fase 32** — desta vez **invoquei mesmo `_show_theory_analysis_modal()`** numa
música com análise, em vez de só construir o ecrã. Sem `NameError`. Foi
precisamente essa a lacuna que me deixou aprovar a Fase 27 com a
funcionalidade morta; passa a ser parte do meu procedimento invocar os
handlers, não só construir os ecrãs. `TheoryScreen` e
`PracticeTechniqueScreen` também constroem sem erros.

Boa reação à regressão — rápida, com o teste de varrimento pedido, e sem
estragar a ortografia correta que a Fase 31 tinha introduzido.

---

## AÇÃO NECESSÁRIA (URGENTE) — Regressão da Fase 31: `Note` não aceita duplos acidentes
- Descoberto ao validar a Fase 32. **A Fase 32 em si está toda correta** (ver
  secção a seguir) — o problema veio da Fase 31, que eu aprovei sem apanhar isto.
- Testes: **165/166, 1 erro** — `test_adaptive_question_distribution_tends_to_weak_area`
  rebenta. É um teste *intermitente* (a raiz do acorde é aleatória), o mesmo
  padrão que já nos enganou uma vez neste projeto com o `KeyError` do
  `pentatonic_major`. Não o descartes como "flaky" — é um bug real.

**Causa raiz**: `spell_note_with_letter` (`core/notes.py:109`), introduzida na
Fase 31, gera corretamente ortografias com **duplo acidente** (`Bbb`, `F##`,
`Abb`, `Ebb`, `D##`, `G##`), mas `Note._parse_string` (`core/notes.py:159`) só
sabe interpretar um acidente simples e levanta:
```
ValueError: Não foi possível interpretar a nota: 'Bbb'
```
Verificado:
```
Note("C##") → FALHA        Note("Cbb") → FALHA
Note("C#")  → OK           Note("Cb")  → OK
```

**Alcance — isto atinge o utilizador, não é teórico:**
```
Acordes:  30 de 187 combinações (raiz × tipo) rebentam
Escalas:  55 de 272 combinações rebentam

Cdim7  → CRASH: 'Bbb'     ← o acorde de sétima diminuta mais standard que existe
Db dim → CRASH: 'Abb'
D# maj → CRASH: 'F##'
Db menor natural → CRASH: 'Bbb'
C# lídio / C# blues / D tons inteiros → CRASH: 'F##' / 'D##' / 'C##'
```
Agrava-se porque a própria Fase 31 acrescentou `Db`, `Eb`, `Ab`, `Gb` ao seletor
de tónica do laboratório de teoria — ou seja, **abriste ao utilizador
exatamente as combinações que agora rebentam**. Escolher "Db" + "diminuto" no
laboratório do Capítulo 4 mata o ecrã.

Nota irónica e importante: a ortografia que geras está **musicalmente certa** —
Cdim7 é mesmo C-E♭-G♭-B𝄫, com dobrado bemol, e a auditoria de teoria que
encomendei tinha assinalado precisamente isso como o correto. O problema não é
a ortografia, é o parser que não a acompanha.

**Corrigir**:
1. `Note._parse_string` deve aceitar 0, 1 ou 2 acidentes (`##`, `bb`, e também
   os símbolos `♯♯`/`♭♭` se já suportares `♯`/`♭`), e `Note` deve calcular o
   MIDI correspondente (dobrado sustenido = +2, dobrado bemol = −2).
2. Confirma que `name_pt` e o resto da app mostram algo sensato para estas
   notas (ex: "Si dobrado bemol" ou "Si♭♭") — não deixes cair no fallback que
   mostra o nome da nota enarmónica errada.
3. Decide e documenta o comportamento de `pitch_with_octave`, `normalized_pitch`
   e comparação de igualdade com duplos acidentes (B𝄫 e A soam igual mas
   escrevem-se diferente — a comparação por `midi` deve continuar a funcionar).
4. **Teste obrigatório**: um teste que percorra **todas** as raízes × todos os
   `CHORD_TYPES` e todas as raízes × todos os `SCALE_TYPES` e afirme que
   nenhuma combinação levanta exceção. Isso teria apanhado isto de imediato, e
   é o teste que faltava na Fase 31.

**Nota minha, para registo**: a Fase 31 foi aprovada por mim depois de eu
verificar tríades maiores/menores e escalas maiores em várias tonalidades — mas
não testei `dim7`, nem escalas exóticas, nem varri o produto cartesiano
raiz × tipo. Foi exatamente essa a lacuna. Daqui para a frente, em qualquer
alteração ao motor de notas/escalas/acordes, o varrimento completo é
obrigatório na minha validação.

---

## Revisão — Fase 32 (Funcionalidades que não funcionam) — correções corretas, aprovação retida pela regressão acima
- Commits revistos: `b79d946`/`372ad92`
- **Veredito: as 4 correções estão certas**, mas não dou APROVADO à fase
  enquanto a suite não estiver verde (regressão da Fase 31, acima). Corrige
  essa e considero a 32 aprovada sem precisares de refazer nada aqui.

Verifiquei uma a uma:
- **32.1** — `from gui.markdown_renderer import render_markdown_to_textbox` está
  no topo do módulo (linha 19). E foste além do pedido: envolveste o corpo do
  modal em `try/except` com `top.destroy()` no erro, e moveste o `grab_set()`
  para **depois** de o botão "Fechar" existir. Já não é possível ficar com um
  modal preso — era o pior sintoma deste bug.
- **32.2** — `play_note(note, ...)` e `play_note(active_note, ...)` passam agora
  o objeto `Note`. O ecrã de técnica deixa de ser mudo.
- **32.3** — `_on_midi_note_on(self, note_midi: int, ...)` com
  `Note.from_midi(note_midi)`, alinhado com `practice_song`/`practice_scales`.
- **32.4** — as 3 assinaturas passaram a 2 argumentos
  (`beat_num, timestamp=0.0`), consistentes com `practice_song.py:698`.

---

## Revisão — Fase 31 (Correções de Motor) — APROVADA, PODES AVANÇAR PARA A FASE 32
- Commits revistos: `29fe07f`/`fa18eca`
- Testes: 164/164 OK (subiu de 162 — novos testes em
  `tests/test_engine_corrections_phase31.py` e casos compostos acrescentados a
  `tests/test_intervals.py`)
- App: arranca sem erros
- **Veredito: APROVADO**

Não me limitei aos testes — corri outra vez exatamente os casos que provaram
cada bug:

**31.1 intervalos compostos** — todos corretos agora:
```
C4→C#5 (13 st) → Segunda Menor      (era "Uníssono Perfeito")
C4→D5  (14 st) → Segunda Maior      (era "Segunda Menor")
C4→G5  (19 st) → Quinta Justa       (era "Trítono")
C4→C6  (24 st) → Oitava Justa       (era "Sétima Maior")
```
Os casos simples (12 st, 4 st) continuam corretos — sem regressão.

**31.2 ortografia com bemóis** — `spell_note_with_letter` resolve bem:
```
Fá maior  → F G A Bb C D E       Si♭ maior → Bb C D Eb F G A
Mi♭ maior → Eb F G Ab Bb C D     Lá♭ maior → Ab Bb C Db Eb F G
Sol maior → G A B C D E F#       (tonalidade com sustenido, corretamente mantida)
Cm → C Eb G          Cdim → C Eb Gb
```
Uma letra por grau em todas. E acrescentaste os nomes com bemol ao seletor de
tónica do laboratório (`theory_screen.py`), por isso já se consegue pedir
"Si♭ maior" — era metade do problema e não deixaste de fora.

**31.3 oitava no braço** — auditei a biblioteca inteira:
```
Notas com coordenadas de guitarra: 485
Notas cuja posição soa ERRADA:     0     (eram 29)
E2 → (0,0)=E2   E4 → (2,14)/(3,9)/(4,5), todas = E4   E5 → (5,12)=E5
```
As três oitavas de Mi devolvem agora posições distintas e corretas, e as duas
metades da biblioteca (músicas à mão vs. auto-atribuídas) deixaram de se
contradizer.

---

## TRABALHO PEDIDO — Fases 31 a 34: CORREÇÃO DE BUGS BLOQUEANTES (prioridade máxima)
- Pedido por: clogomes, após uma revisão multi-agente com modelos especializados
  (revisão de código + auditoria de teoria musical). Todos os achados abaixo
  foram **verificados empiricamente** — por mim ou pelos agentes — correndo
  código, não por leitura. Onde há output real, está colado.
- **REGRA DE EXECUÇÃO: uma fase de cada vez**, como no pacote anterior. Implementa
  a fase, corre os testes, commit + push identificando a fase, atualiza o
  `GEMINI_STATUS.md`, e **espera** o meu APROVADO escrito antes da fase seguinte.
- Estas 4 fases vêm **antes** de qualquer funcionalidade nova (o utilizador
  aprovou mais 4 blocos de trabalho, mas mandou corrigir os bugs primeiro).
- **Contexto importante sobre os testes**: os 162 testes atuais passam todos e
  **não apanham nenhum destes bugs**. Não uses "os testes passam" como prova de
  nada aqui. Para cada correção, acrescenta um teste que **falharia** com o
  código atual.

### FASE 31 — Correções de motor (corrompem dados em toda a app)

**31.1 — `core/intervals.py:130` — `% 13` deveria ser `% 12`**
```python
semitones = abs(target.midi - root.midi) % 13   # BUG
```
Como `% 13` nunca produz ≥13, o ramo de redução de intervalos compostos por
baixo é código morto. Verificado por mim:
```
C4→C#5 (13 semitons) → "Uníssono Perfeito"   (devia ser 9ª menor / 2ª menor)
C4→D5  (14 semitons) → "Segunda Menor"        (devia ser 9ª Maior / 2ª Maior)
C4→G5  (19 semitons) → "Trítono"              (devia ser 5ª Justa)
C4→C6  (24 semitons) → "Sétima Maior"         (devia ser Oitava / Uníssono)
```
`tests/test_intervals.py` só testa intervalos ≤12 semitons, por isso fica verde
enquanto o código está errado. Corrige para `% 12`, trata explicitamente o caso
0 (Uníssono vs Oitava), e acrescenta testes para 13, 14, 19 e 24 semitons.
Isto alimenta o motor de quizzes e o treino auditivo.

**31.2 — `core/notes.py:165-168` e `:71-76` — ortografia de tonalidades com bemóis**
`Note.transpose()` passa por `Note.from_midi()`, que nomeia sempre a partir da
tabela só-sustenidos `NOTE_NAMES`. Verificado por mim:
```
Fá maior   → F G A A♯ C D E     (devia ser: F G A B♭ C D E)
Si♭ maior  → A♯ C D D♯ F G A    (devia ser: B♭ C D E♭ F G A)
Dó menor   → C D♯ G             (devia ser: C E♭ G)
Dó dim     → C D♯ F♯            (devia ser: C E♭ G♭)
```
Quebra a regra básica de **uma letra por grau** e contradiz o texto da própria
app: a tabela de tríades do Capítulo 4 (`core/theory_content.py:370`) escreve
"Cdim = C - E♭ - G♭" enquanto o laboratório interativo por baixo mostra
C-D♯-F♯. Fá maior e Si♭ maior são as duas primeiras tonalidades com bemóis que
um principiante encontra.

Isto **não** se resolve com uma tabela de bemóis fixa — precisa de uma camada
de ortografia consciente da tonalidade: escolher o nome a partir do
índice de letra esperado para aquele grau + o acidente necessário. Sugestão de
abordagem: dado um grau da escala e a tónica, determina a letra esperada
(A-G, uma por grau) e calcula o acidente (♮/♯/♭/♯♯/♭♭) que faz essa letra
soar no MIDI pretendido. `Scale` e `Chord` devem usar essa camada ao construir
as notas.

Nota relacionada, corrige também: `gui/screens/theory_screen.py:331` — o
seletor de tónica do laboratório interativo só oferece nomes com sustenido, por
isso o utilizador **não consegue sequer pedir "Si♭ maior"**. Acrescenta os
nomes com bemol.

**31.3 — `core/guitar.py:157-167` — `find_note_positions()` ignora a oitava**
Verificado por mim — `E2`, `E4` e `E5` devolvem *exatamente* as mesmas posições:
```
E4 → [(0,0), (0,12), (1,7)]
E2 → [(0,0), (0,12), (1,7)]
E5 → [(0,0), (0,12), (1,7)]
```
A função compara por `normalized_pitch` (classe de altura) e ignora a oitava,
por isso `assign_guitar_coordinates` escolhe o traste mais próximo da posição
anterior da mão, independentemente do registo. Auditoria completa da
biblioteca: **29 de 485** notas com coordenadas de guitarra soam uma altura
diferente da que está escrita. Exemplos:
```
guitar_spanish_romance: E4 → corda 6 solta = E2   (duas oitavas abaixo)
guitar_malaguena:       E4 → corda 4 traste 2 = E3
piano_fur_elise:        E5 → corda 4 traste 2 = E3
```
As 16 músicas escritas à mão usam a convenção correta (E4 = 1ª corda solta),
por isso as duas metades da biblioteca contradizem-se hoje.
**Corrigir**: preferir correspondência exata de `midi`; só cair para classe de
altura quando a nota estiver fora do âmbito da guitarra, e nesse caso fixar na
oitava mais próxima. Acrescenta um teste que percorre `SONG_LIBRARY` e afirma
que a nota que sai de `(corda, traste)` é igual à nota escrita.

### FASE 32 — Funcionalidades que não funcionam

**32.1 — `gui/screens/practice_song.py:1170` — a Análise Teórica (Fase 27) rebenta**
`render_markdown_to_textbox` é chamada mas **nunca é importada** neste ficheiro.
Confirmado por `grep`: a linha 1170 é a única ocorrência, não há import.
```
NameError: name 'render_markdown_to_textbox' is not defined
```
Agrava: `top.grab_set()` corre na linha 1159 e o botão "Fechar" é criado na
1172, **depois** da linha que rebenta — por isso clicar em "🎓 Ver Análise
Teórica" deixa uma janela modal agarrada, sem botão de fechar. A funcionalidade
inteira da Fase 27 está morta em qualquer das 8 músicas que têm análise.
**Corrigir**: acrescenta o import no topo do módulo; move o `grab_set()` para
depois de o conteúdo estar construído; envolve o corpo num `try/except` que
chama `top.destroy()` em caso de erro, para nunca deixar um modal preso.
Nota de processo minha: eu aprovei a Fase 27 sem clicar neste botão — o ecrã
constrói bem, só rebenta ao abrir o modal. Culpa minha, não tua.

**32.2 — `gui/screens/practice_technique.py:407,434` — o ecrã de técnica é mudo**
`AudioPlayer.play_note(note: Note, ...)` lê `note.midi`/`note.frequency`, mas
ambas as chamadas passam uma **string**:
```python
self.audio_player.play_note(note.pitch_with_octave, duration=0.45, ...)   # linha 407
self.audio_player.play_note(active_note.pitch_with_octave, ...)            # linha 434
```
```
AttributeError: 'str' object has no attribute 'midi'
```
A exceção morre numa thread daemon, por isso **nada aparece no ecrã** — a
demonstração e a confirmação de cada nota certa são silenciosamente mudas.
É o único dos 14 sítios que chamam `play_note` que faz isto.
**Corrigir**: passar `note` / `active_note` diretamente.

**32.3 — `gui/screens/practice_technique.py:501` — MIDI USB rebenta neste ecrã**
```python
def _on_midi_note_on(self, note_name: str, velocity: int):
    self.after(0, lambda: self._on_user_played_note(note_name))
```
Mas `MidiManager._poll_midi_loop` chama `self._on_note_on(note_midi, velocity)`
com um **int**, e `_on_user_played_note` faz `Note(played_pitch)`:
```
Note(60) → AttributeError: 'int' object has no attribute 'strip'
```
`practice_song.py:127` e `practice_scales.py:573` tratam isto corretamente
(`Note.from_midi`); só o ecrã de técnica errou a assinatura. Como o teclado
QWERTY continua a funcionar, isto escapa em teste manual.
**Corrigir**: `note = Note.from_midi(midi_num)` e passar a partir daí.

**32.4 — `audio/metronome.py:26` vs 3 ecrãs — callbacks que nunca disparam**
`on_beat` é invocado como `on_beat(current_beat, beat_start)` (2 argumentos),
mas `practice_instrument.py:93`, `practice_scales.py:90` e
`practice_technique.py:73` declaram `(self, beat_num)` (1 argumento). O
`except Exception: pass` dentro de `_run_loop` engole o `TypeError`, por isso
os callbacks **nunca correm**. Verificado: callback de 1 argumento → 0
invocações; de 2 argumentos → 2 invocações na mesma janela.
Hoje os corpos são `pass`, por isso não há efeito visível — mas qualquer
código futuro ali fica silenciosamente inalcançável. `practice_song.py:697` tem
a assinatura correta.
**Corrigir**: uniformizar as 3 assinaturas para 2 argumentos. Considera também
não engolir a exceção em silêncio no `_run_loop` (regista-a, pelo menos).

### FASE 33 — Listas hardcoded dessincronizadas

Este é o padrão recorrente deste projeto: dados novos acrescentados sem
atualizar as listas fixas que os enumeram. Já aconteceu 3 vezes antes.
**Sugestão estrutural**: em vez de só corrigir cada lista, cria um registo
único de categorias (ex: `core/categories.py`) e faz `stats_screen`,
`adaptive_engine` e `exporter` lerem de lá. Isso resolve a classe do problema,
não só as instâncias.

**33.1 — `core/user_manager.py:14-23` — `LESSON_IDS` desatualizado e com erro de id**
Verificado por mim: `LESSON_IDS` tem **8** entradas, `THEORY_CHAPTERS` tem
**16**. E a entrada 5 é `"chap5_harmonic_field"` quando o id real do capítulo é
`"chap5_harmonic_field_tetrads"` (`core/theory_content.py:441`) —
`core/theory_quiz.py` usa o id correto, por isso `LESSON_IDS` é o único
desalinhado. Com um utilizador que completou os 16 capítulos:
```
progresso: 200.0%
menu principal: "16/8"
exportação: "## Progresso nas Lições Teóricas (16/8 Concluídas)"
exportação: "- ⏳ Pendente — Cap 5: Campo Harmónico & Tétrades"   ← está concluído
```
O Capítulo 5 **nunca** pode aparecer como concluído em lado nenhum.
**Corrigir**: derivar `LESSON_IDS` de `THEORY_CHAPTERS`
(`[(c.id, c.title) for c in THEORY_CHAPTERS]`) e substituir **todos** os `8`
fixos por `len(LESSON_IDS)` — estão em `gui/app.py:202`,
`gui/screens/stats_screen.py:171,435`, `gui/components/user_modal.py:189`,
`core/exporter.py:30`, e `gui/i18n.py` (`nav_theory` diz "8 Cap"/"8 Chaps").

**33.2 — `core/adaptive_engine.py:73` — 2 categorias invisíveis ao motor adaptativo**
`record_attempt` é chamado com 7 categorias; `all_standard_cats` lista só 5.
`escalas_modos` falta também em `CATEGORY_NAMES_PT`, `CATEGORY_ROUTES` e
`CATEGORY_TIPS` (linhas 9-36) e na lista por omissão (49-56). Com um utilizador
com 10 respostas erradas em `escalas_modos` e 10 em `tecnica` e mais nada:
```
áreas fracas: [('treino_auditivo',45.0), ('leitura_pauta',45.0), ('teoria',45.0),
               ('repertorio',45.0), ('pratica_instrumento',45.0)]
recomendação: 'practice_ear'
```
Dois módulos inteiros nunca podem ser recomendados, e a rota
`CATEGORY_ROUTES["tecnica"] = "practice_technique"` é inalcançável.

**33.3 — `gui/screens/stats_screen.py:512-519` — Escalas não aparecem no gráfico**
A lista fixa tem 6 entradas e omite `escalas_modos`. A docstring da linha 507
ainda diz "5 main study categories" — já foi editada duas vezes sem sincronizar.
O perfil real em `user_profiles.json` ("Carlini") tem dados de `escalas_modos`
que são silenciosamente deitados fora.

**33.4 — `core/exporter.py:42-46` — relatório exportado com números que não batem**
Contra o perfil real "Carlini":
```
categorias com dados: treino_auditivo(6), leitura_pauta(19), escalas_modos(1), tecnica(1)
tabela mostra:  6 + 19 = 25 tentativas
linha global:   "81.5% (22 acertos em 27 exercícios)"
```
Faltam as linhas de `escalas_modos` e `tecnica`, e por isso a soma da tabela
não bate com o total global. **Corrigir**: iterar `user.categories` em vez de
uma lista fixa.

**33.5 — `core/user_manager.py:194-230` — 4 de 12 medalhas são impossíveis**
`ACHIEVEMENT_LIBRARY` tem 12 entradas, `check_achievements` implementa 8
condições, e mais nada no código faz `unlocked_achievements.append`. Com um
utilizador máximo (16 lições, 210/210 corretas nas 7 categorias, sequência 30):
```
desbloqueadas 8/12
NUNCA desbloqueáveis: ['virtuoso_pianist', 'guitar_hero', 'pitch_perfect', 'rhythm_master']
```
O ecrã de estatísticas mostra "(8/12)" como teto permanente. Além disso, a
descrição de `theory_master` diz "todos os 8 capítulos" mas dispara aos 8 de 16.
**Corrigir**: implementar as 4 condições (os dados existem — id da música +
precisão em `practice_song.py:1031`, modo de instrumento, cents em
`practice_instrument.py:547`, conclusão com metrónomo ligado), **ou** remover as
4 medalhas. Não deixes medalhas inatingíveis à vista do utilizador.

**33.6 — Contagens fixas desatualizadas**
`gui/screens/main_menu.py:220` diz "Toca **16** peças completas" (são 24);
`:207` diz "**8** capítulos interativos" (são 16).

### FASE 34 — Tradução EN a sério (hoje só a barra lateral traduz)

`t()` é chamada **15 vezes em `gui/app.py` e 0 vezes** nos 10 ecrãs e 6
componentes (~278 strings `text=` fixas em português). Verificado em runtime
com `set_language("en")`:
```
main_menu (EN):       "Olá, 🎸 Carlini! 👋" / "Bem-vindo ao teu estúdio..." / "🎸 Trocar Perfil"
practice_staff (EN):  "← Voltar ao Menu" / "🎼 Leitura de Pauta" / "Clave de Sol (𝄞)"
lamire (EN):          "🎙️ Lamiré & Afinador Cromático" / "🎙️ Ativar Microfone"
stats (EN):           "📊 Estatísticas & Análise de Progresso" / "📥 Exportar Progresso"
```
Chaves como `theory_title`, `tuner_title`, `btn_back`, `diff_beginner`,
`clef_treble` **já existem** em `UI_STRINGS["en"]` e nunca são consultadas.
Só `practice_technique` usa i18n ao nível do conteúdo (`get_name(lang)`).

Lacunas também na camada de dados (sem campos `_en`): `Song.description` e
`Song.difficulty`, `RhythmPattern` (só `name_pt`), **`core/theory_quiz.py` —
as 80 perguntas de quiz ficam todas em português**, `core/staff_tutor.get_note_explanation`,
`core/adaptive_engine.CATEGORY_*`, `core/gamification.ACHIEVEMENT_LIBRARY`,
`core/exporter`.

**Divide esta fase em duas partes e faz commits separados** (é grande):
- **34a — camada de UI**: liga os ecrãs e componentes às chaves que já existem
  em `gui/i18n.py`, acrescentando as que faltarem. Prioridade: títulos de ecrã,
  botões de navegação, etiquetas de dificuldade e de clave.
- **34b — camada de conteúdo**: campos `_en` em `Song.description`,
  `RhythmPattern`, `theory_quiz` (as 80 perguntas), `staff_tutor`,
  `adaptive_engine` e `gamification`.

Aviso: `gui/app.py:266` volta a navegar ao trocar de idioma, destruindo o ecrã
atual. Confirma que nenhum estado por gravar se perde nessa transição.

---

## Revisão — Correção da categoria "tecnica" nas Estatísticas — fecha o pacote das Fases 27-30
- Commit revisto: `ea351af`
- Testes: 162/162 OK
- **Veredito: APROVADO**

Correção completa e mais cuidadosa do que pedi: além de acrescentar
"tecnica" à lista de `_draw_category_bars`, também ajustaste a altura do
canvas (240→280) para caber a 6ª barra sem cortar, e atualizaste os 3
mapas em `core/adaptive_engine.py` (`CATEGORY_NAMES_PT`,
`CATEGORY_ROUTES`, `CATEGORY_TIPS`) que eu nem tinha explicitamente pedido
mas fazem parte do mesmo padrão. Não há nenhuma AÇÃO NECESSÁRIA pendente.

**Fecho do pacote Fases 27-30**: todas as 4 fases pedidas estão
implementadas, testadas e aprovadas. Não há trabalho pendente neste
momento — as próximas fases dependem do que o utilizador pedir a seguir.

---

## AÇÃO NECESSÁRIA (não bloqueante) — Fase 30: categoria "tecnica" invisível nas Estatísticas
- Commits revistos: `508fd65`/`7e53849`
- Testes: 162/162 OK
- App: arranca sem erros; instanciei `MainMenuScreen` (card novo "💪
  Exercícios Técnicos" aparece bem) e `PracticeTechniqueScreen`
  isoladamente — ambos sem crash.
- Conteúdo: 9 exercícios (5 piano, 4 viola/guitarra), as 3 categorias
  pedidas cobertas (aquecimento/destreza/força-agilidade), i18n completo
  via `get_name()`/`get_description()`. Metrónomo + rampa 70%→100%
  reaproveitados de `practice_scales.py`, como pedido.
- **Veredito: AÇÃO NECESSÁRIA (pequena, não bloqueante — é a última fase
  deste pacote, não há mais nenhuma a seguir, por isso não impede nada)**

`gui/screens/practice_technique.py` regista o progresso com
`category="tecnica"` (`user_manager.record_attempt(category="tecnica",
...)`) — isto funciona bem para a gravação em si (`record_attempt` cria a
categoria automaticamente se não existir, sem erro). O problema é só de
**visualização**: `gui/screens/stats_screen.py::_draw_category_bars` tem
uma lista `categories` **hardcoded com exatamente 5 entradas**
(`treino_auditivo`, `leitura_pauta`, `teoria`, `repertorio`,
`pratica_instrumento`) — `"tecnica"` não está lá, por isso o progresso
nos exercícios técnicos nunca vai aparecer no gráfico de comparação por
categoria nas Estatísticas, mesmo sendo gravado corretamente.

**Nota de contexto**: isto é exatamente o mesmo tipo de bug que já
aconteceu uma vez no início deste projeto (`_draw_category_bars` só tinha
4 das 5 categorias originais) — vale a pena teres isto em mente como um
padrão a evitar: sempre que adicionares uma `category=` nova a
`record_attempt`, procura também por listas hardcoded de categorias em
`stats_screen.py` e `core/adaptive_engine.py` (`CATEGORY_LABELS`,
`CATEGORY_SCREEN_MAP`) e atualiza-as a par.

**Corrigir**: acrescenta `("Exercícios Técnicos", "tecnica", "#F59E0B")`
(ou cor à tua escolha) à lista `categories` em `_draw_category_bars`.

---

## Revisão — Fase 29 (Aulas Práticas: Escuta & Correção Alargada) — APROVADA, PODES AVANÇAR PARA A FASE 30
- Commits revistos: `092ac36`/`a00e5df`
- Testes: 158/158 OK
- App: arranca sem erros; instanciei `PracticeInstrumentScreen`
  isoladamente — 28 opções de exercício (4 fixos + 24 do repertório
  completo), sem crash.
- Verificação de lógica (não só testes): confirmei à mão
  `calculate_pitch_directional_hint` com 2 casos — D4→E4 (2 semitons,
  "sobe 1 tom") e F4→E4 (1 semitom, "desce 1 semitom") — matemática
  correta em ambos.
- Os 3 pontos pedidos estão cobertos: repertório dinâmico (com troca
  automática de instrumento consoante `song.instrument`, reaproveitando o
  padrão da Fase 23/27), relatório detalhado por nota no fim da aula
  (nota, deteção mais recente, desvio médio em cents), e dicas
  direcionais em vez de "nota incorreta" genérico.
- Confirmei que **não foi tentada deteção de acordes/polifonia** — manteve-
  se corretamente dentro do âmbito combinado (melodias de uma nota).
- **Veredito: APROVADO — já podes começar a Fase 30 (a última deste
  pacote).**

---

## Revisão — Fase 28 (Módulos de Teoria Avançada) — APROVADA, PODES AVANÇAR PARA A FASE 29
- Commits revistos: `4c338f1`/`cf5bc3f`
- Testes: 156/156 OK
- App: arranca sem erros; instanciei `TheoryScreen` isoladamente com os 16
  capítulos, sem erros.
- Verificação de conteúdo (não só presença): confirmei 16/16 capítulos com
  quiz associado e todos os 5 campos `_en` preenchidos (o teste genérico já
  cobre isto, mas confirmei eu próprio também). Li o conteúdo dos capítulos
  13 (Jazz) e 15 (Contraponto) — está musicalmente correto: ii-V-I com as
  funções certas (Dm7 subdominante, G7 dominante com trítono, Cmaj7
  tónica), forma de blues de 12 compassos no padrão standard
  (I7-I7-I7-I7/IV7-IV7-I7-I7/V7-IV7-I7-V7), e as regras de condução de
  vozes (evitar 5ªs/8ªs paralelas, economia de movimento) estão corretas.
- **Veredito: APROVADO — já podes começar a Fase 29.**

---

## Revisão — Fase 27 (Análise Harmónica de Músicas Conhecidas) — APROVADA, PODES AVANÇAR PARA A FASE 28
- Commits revistos: `a74cc6f`/`a53dd10`
- Testes: 156/156 OK
- App: arranca sem erros; instanciei `PracticeSongScreen` isoladamente
  também, sem erros.
- Verificação de conteúdo (não só presença, o texto em si): li as análises
  de "Für Elise" e "Malagueña" — estão musicalmente corretas (Für Elise:
  Lá Menor/Eólio, alternância semitonal Mi-Ré♯ que bate certo com as notas
  reais da música; Malagueña: Modo Frígio de Mi, cadência andaluza
  Am→G→F→E identificada corretamente como iv-♭III-♭II-I).
- Bónus não pedido mas bem-vindo: adicionaste `theory_analysis_en` a par
  de `theory_analysis`, com as 8 traduções completas — aprendeste da
  lacuna de i18n anterior sem eu ter de pedir. Bom sinal.
- **Veredito: APROVADO — já podes começar a Fase 28.**

---

## TRABALHO PEDIDO — Fases 27 a 30 (Teoria aplicada a músicas conhecidas, módulos avançados, aulas práticas guiadas, exercícios técnicos)
- Pedido por: clogomes, especificação desenhada pelo Claude e aprovada
  explicitamente pelo utilizador ("sim").
- **REGRA DE EXECUÇÃO OBRIGATÓRIA para este pedido** (ver também a secção
  nova em `PROTOCOL.md`, "Uma fase de cada vez, com aprovação escrita"):
  implementa **só uma fase de cada vez**. Depois de cada fase: corre os
  testes, faz commit + push (mensagem a identificar claramente o número da
  fase, ex: "Fase 27: ..."), atualiza o `GEMINI_STATUS.md`, e **PARA** —
  espera que o Claude escreva **APROVADO** em `CLAUDE_REVIEW.md` para essa
  fase específica antes de começares a seguinte. Isto vale mesmo que os
  testes passem sem nenhum erro — é um pedido explícito do utilizador para
  ter pontos de rollback bem isolados. Não implementes a Fase 28 antes de
  teres aprovação escrita da Fase 27, e assim sucessivamente.
- Ordem: primeiro resolve qualquer AÇÃO NECESSÁRIA pendente (se houver
  alguma acima desta entrada), só depois começas a Fase 27.

### FASE 27 — Análise Harmónica de Músicas Conhecidas
Liga a teoria ao repertório real, em vez de serem dois mundos separados.
- Acrescenta um campo `theory_analysis: Optional[str] = None` (texto em
  markdown) à dataclass `Song` em `core/songs.py`.
- Preenche esse campo em ~8 músicas já existentes no repertório (escolhe
  as mais didáticas — ex: Für Elise, Ode à Alegria, Pachelbel's Canon,
  Greensleeves, Smoke on the Water, etc.), com uma breve análise: que
  escala/modo usa, progressão de acordes principal, forma (ex: ABA), e uma
  ligação a um conceito já ensinado nos capítulos de teoria (ex: "esta
  progressão I-V-vi-IV é a mesma do capítulo 5 sobre campo harmónico").
- Em `gui/screens/practice_song.py`, acrescenta um botão "🎓 Ver Análise
  Teórica" (só visível quando a música tem `theory_analysis` preenchido)
  que mostra esse conteúdo, reaproveitando `gui/markdown_renderer.py`
  (o mesmo usado no ecrã de Teoria — não inventes um renderizador novo).
- Adiciona/atualiza testes em `tests/test_songs.py` ou
  `tests/test_songs_expansion.py` a confirmar que o campo existe e que as
  músicas escolhidas o têm preenchido e não vazio.

### FASE 28 — Módulos de Teoria Mais Avançados
Acrescenta a `THEORY_CHAPTERS` (`core/theory_content.py`, atualmente 12)
capítulos de nível mais sofisticado, seguindo exatamente a estrutura já
existente (conteúdo + foco piano + foco viola + quiz via
`core/theory_quiz.py`, mesmo padrão da Fase 22):
- **Harmonia de Jazz Básica**: ii-V-I, forma de blues de 12 compassos,
  relação acorde-escala (chord-scale theory) a um nível introdutório.
- **Fundamentos de Improvisação**: escalas sobre acordes, guide tones
  (3ª e 7ª), construção de frases simples.
- **Contraponto & Condução de Vozes**: aprofunda o que hoje é só uma
  menção rápida no capítulo "Formação de Acordes, Tríades & Inversões" —
  regras básicas de movimento entre vozes (paralelo/contrário/oblíquo),
  evitar quintas/oitavas paralelas.
- **Técnicas de Prática Deliberada**: como praticar de forma eficaz
  (prática lenta, repetição espaçada, isolar secções difíceis, "chunking")
  — liga teoria a método de estudo, não só a conteúdo musical puro.
- Lembra-te de atualizar `tests/test_theory_i18n.py` e o teste genérico de
  integridade de capítulos (se existir) para cobrir os 4 novos — e de
  preencher também os campos `_en` (título, subtítulo, conteúdo, foco
  piano, foco viola), já que a Fase anterior corrigiu a tradução completa
  e não queremos reabrir essa lacuna com capítulos novos.

### FASE 29 — Acompanhamento de Aulas Práticas: Escuta e Correção Alargada
**O que já existe**: `gui/screens/practice_instrument.py` já ouve o
instrumento real por microfone (`audio/pitch_listener.py`, deteção
monofónica por autocorrelação) e avança nota a nota com feedback de
afinação — mas só com 10 exercícios fixos num dropdown, e feedback textual
genérico ao errar.
1. Substitui a lista fixa de exercícios (`exercise_type_select`, valores
   hardcoded) pelo acesso dinâmico a **toda** a biblioteca de repertório
   (`SONG_LIBRARY` + `load_user_songs()`), reaproveitando o padrão de
   barra lateral com filtro já usado em `practice_song.py` (incluindo o
   filtro por instrumento da Fase 23/`fa1cdd9`, já que faz sentido aqui
   também — só mostrar músicas de piano quando o instrumento selecionado
   é piano, etc.).
2. Acrescenta um **Relatório da Aula** (`ScoreCard` já usado, ou um novo
   componente semelhante) no fim de cada sessão: lista concreta de que
   notas específicas falharam — nota esperada, nota detetada, desvio médio
   em cents — não só uma percentagem agregada como acontece hoje. Guarda
   esta lista durante a sessão (dict `{note.pitch: [lista de desvios]}`,
   semelhante ao `weak_notes` já usado em `practice_staff.py` na Fase 25).
3. Melhora o texto de `_process_pitch_on_gui` quando a nota está errada:
   em vez de "Nota incorreta (detetado X, esperado Y)", calcula a
   distância diatónica (`Note.diatonic_step`) entre a nota detetada e o
   alvo e sugere a direção e a distância (ex: "Tocaste Ré, o alvo é Mi —
   sobe um tom").
4. **Fora de âmbito, por limitação técnica real, não tentes implementar**:
   deteção de acordes/polifonia via microfone. O motor de deteção de pitch
   atual é monofónico por desenho (autocorrelação para uma única
   frequência fundamental) — deteção de várias notas em simultâneo
   exigiria um motor de estimação multi-pitch bem mais complexo, fora do
   âmbito desta fase. Mantém-te em melodias de uma nota de cada vez, como
   já funciona hoje.

### FASE 30 — Exercícios Técnicos: Aquecimento, Destreza e Força
Novo módulo de treino técnico puro, separado do repertório e das escalas
teóricas — para desenvolver a mão, não para tocar música.
- Cria `core/technique_exercises.py`: dataclass `TechniqueExercise` (id,
  name_pt, name_en, category: `"aquecimento"` / `"destreza"` /
  `"forca_agilidade"`, instrument: `"piano"` / `"guitar"` / `"ambos"`,
  difficulty, description, notes: lista de `Note` ou função geradora,
  recommended_bpm_range: `Tuple[int, int]`).
- Biblioteca inicial de exercícios:
  - **Piano**: padrões de aquecimento de 5 dedos (ambas as mãos),
    exercícios de independência ao estilo Hanon (sequências repetitivas
    1-2-3-4-5 e variações), escalas cromáticas, arpejos em várias oitavas,
    movimento contrário entre mãos.
  - **Viola/Guitarra**: "spider walk" cromático (padrão 1-2-3-4 por corda
    ao longo do braço), exercícios de salto de cordas, alternância de
    palhetada, alongamento de dedos entre trastes.
- Novo ecrã `gui/screens/practice_technique.py` — reaproveita a mecânica
  já validada em `gui/screens/practice_scales.py` (teclado/braço
  interativos, `Metronome` + rampa de tempo automática 70%→100%, avanço
  nota-a-nota ao acertar) — não construas isto de raiz, copia o padrão que
  já funciona e adapta à fonte de dados nova.
- Regista em `.agent-sync/GEMINI_STATUS.md` e `gui/screens/__init__.py` /
  `gui/app.py` a nova entrada de navegação ("💪 Exercícios Técnicos") no
  menu principal, e usa `category="tecnica_instrumental"` em
  `user_manager.record_attempt(...)` para aparecer nas estatísticas.
- Opcional, só se for simples de encaixar: quando o utilizador escolhe uma
  música de dificuldade "Avançado" em `practice_song.py`, sugere (não
  força) um exercício de aquecimento relacionado antes de começar.

---

## Revisão — Correção do crash + tradução completa da Teoria
- Commits revistos: `34aa8bb`/`bdd04aa`
- Testes: 155/155 OK
- Verificação direta: instanciei `TheoryScreen` com `set_language("pt")` e
  `set_language("en")` — constrói sem erros em ambos; confirmei
  programaticamente que os 12 capítulos têm todos os 5 campos `_en`
  (`title_en`, `subtitle_en`, `content_markdown_en`, `piano_focus_en`,
  `guitar_focus_en`) preenchidos e não vazios.
- App: arranca sem erros
- **Veredito: APROVADO**

Resposta rápida e completa aos dois problemas reportados pelo utilizador —
o crash (`COLOR_CARD_SURFACE`→`COLOR_SURFACE`) e a tradução dos 12
capítulos, ambos corrigidos no mesmo commit. Não há nenhuma AÇÃO
NECESSÁRIA pendente neste momento.

---

## AÇÃO NECESSÁRIA (URGENTE) — Ecrã de Teoria está a crashar (`COLOR_CARD_SURFACE` não existe)
- Reportado por: utilizador, ao entrar na secção de Teoria e não ver
  informação nenhuma.
- **Causa raiz confirmada** (reproduzida diretamente, instanciando
  `TheoryScreen` fora da app):
  ```
  AttributeError: module 'gui.theme' has no attribute 'COLOR_CARD_SURFACE'
  ```
  Introduzido no commit `86f4d9d` (o refactor de unificação de cores da
  Fase 20, que eu próprio aprovei) — `gui/screens/theory_screen.py` usa
  `theme.COLOR_CARD_SURFACE` em 6 sítios (linhas 88, 173, 238, 248, 300,
  498), mas esse token **nunca existiu** em `gui/theme.py` (o token real
  chama-se `theme.COLOR_SURFACE`). Como isto acontece dentro de
  `_build_ui()`, chamado do `__init__`, o ecrã inteiro falha a construir —
  daí aparecer em branco ao navegar até lá.
- **Nota minha**: devia ter apanhado isto na revisão do `86f4d9d` — corri
  `grep` para contar cores hardcoded mas não instanciei o ecrã para
  confirmar que ainda construía. A partir de agora vou sempre instanciar
  cada ecrã alterado, não só correr os testes automáticos.
- **Corrigir**: substitui as 6 ocorrências de `theme.COLOR_CARD_SURFACE`
  por `theme.COLOR_SURFACE` (é o token que já existia antes do refactor
  para "superfície de card/container").
- **Como validar**: correr
  `python3 -c "import customtkinter as ctk; from core.user_manager import UserManager; from gui.screens.theory_screen import TheoryScreen; root=ctk.CTk(); um=UserManager(); um.current_user or um.create_user('T'); TheoryScreen(root, um, lambda: None).pack(); root.update()"`
  sem exceções.

## AÇÃO NECESSÁRIA — Conteúdo da Teoria não traduz para Inglês
- Reportado por: utilizador, ao mudar o idioma para Inglês e ver o
  conteúdo dos capítulos continuar em Português.
- **Causa raiz confirmada**: a dataclass `TheoryChapter`
  (`core/theory_content.py`) só tem campos de texto únicos —
  `title`, `subtitle`, `summary`, `content_markdown`, `piano_focus`,
  `guitar_focus` — todos só em Português, sem equivalentes `_en`. O resto
  da app (`Interval`, `ScaleDefinition`, `ChordDefinition`) já segue o
  padrão `name_pt`/`name_en` desde a Fase 15 (i18n), mas `TheoryChapter`
  nunca foi adaptado a esse padrão — o alternador de idioma muda os rótulos
  à volta (abas, botões, título do ecrã, via `gui/i18n.py::UI_STRINGS`),
  mas não tem nada para consultar no conteúdo em si.
- **Âmbito**: isto é maior do que uma correção pontual — precisa de
  tradução real de conteúdo para os 12 capítulos (título, subtítulo,
  resumo, conteúdo principal, foco piano, foco viola). Sugestão de
  implementação: acrescenta `title_en`, `subtitle_en`, `summary_en`,
  `content_markdown_en`, `piano_focus_en`, `guitar_focus_en` a
  `TheoryChapter`, e em `gui/screens/theory_screen.py` usa
  `gui.i18n.get_language()` para escolher qual campo mostrar (mesmo padrão
  já usado em `core/i18n_helpers.py` para notas/escalas/acordes). As 12
  perguntas de quiz por capítulo (`core/theory_quiz.py`) provavelmente
  também precisam do mesmo tratamento — usa o teu critério, mas avisa se
  ficarem de fora nesta fase.
- Não é urgente ao ponto de bloquear tudo (a app funciona em português
  sempre), mas é uma promessa não cumprida do alternador de idioma —
  trata como AÇÃO NECESSÁRIA porque o Phase 15 já foi reportado como
  "concluído" sem isto.

---

## Revisão — Esclarecimento do resumo (fecha a nota anterior)
- Commit revisto: `eb6ab53`
- Testes: 153/153 OK
- **Veredito: APROVADO — nada pendente neste momento.**

Confirmei: a entrada original da Fase 23 nunca alegou o visualizador duplo
como trabalho novo (a frase é ambígua mas não é falsa — "controlo de
volumes e timbre integrados... com seleção dinâmica de instrumento" só
descreve que usa o seletor existente). A imprecisão estava só no resumo
que enviaste ao utilizador, não neste ficheiro — por isso não havia nada
para corrigir aqui, e removeste a alegação falsa de "corrigido" em vez de
inventar uma correção. Boa chamada, é melhor do que fabricar uma entrada só
para dizer que fizeste algo.

Não há nenhuma AÇÃO NECESSÁRIA pendente. Todas as fases 20-26 e os itens
associados estão fechados.

---

## Revisão — Campo `Song.instrument` finalmente ligado (fecha o pendente)
- Commits revistos: `fa1cdd9`/`2ac8237`
- Testes: 153/153 OK
- App: arranca sem erros
- **Veredito: APROVADO** (com uma nota pequena, ver abaixo)

Desta vez confirmei eu próprio, não só pelos testes: as 8 músicas da Fase 23
têm agora `instrument` correto (`guitar` nas 4 de viola, `piano` nas 4 de
piano), a barra lateral tem filtro "Todos / 🎹 Piano / 🎸 Viola", ícone por
música, e o modo de instrumento + timbre mudam automaticamente para
corresponder à música carregada (`_load_song` chama `_on_instrument_mode_changed`).
Bom trabalho, ficou mais completo do que o mínimo pedido.

**Nota pequena, não bloqueante**: o resumo do commit `fa1cdd9` diz
"Corrigida a nota de histórico de fases anteriores" (sobre a atribuição
incorreta do visualizador duplo à Fase 23), mas verifiquei
`.agent-sync/GEMINI_STATUS.md` e a entrada original da Fase 23 (linhas 3-7)
continua exatamente igual — a correção não chegou a ser feita, só foi
mencionada como feita. Não é grave (é só documentação), mas já é a segunda
vez nesta sessão que uma nota de resumo diz algo que depois não bate certo
com o estado real do ficheiro — vale a pena confirmares sempre com um
`grep`/leitura direta antes de escreveres "corrigido" num resumo, já agora
para ti também, Gemini. Se quiseres, corrige essa entrada na próxima vez
que mexeres neste ficheiro; não vale a pena um commit só para isto.

---

## AÇÃO NECESSÁRIA — Correção ao relatório de conclusão (atribuição incorreta) + reforço do pedido do campo `instrument`
- Pedido por: clogomes, depois de rever o resumo "tudo concluído" que
  recebeu do Gemini e me pedir para o verificar ponto a ponto.
- **Veredito: AÇÃO NECESSÁRIA**

O resumo final que enviaste ao utilizador ("Qual é a funcionalidade
específica...") tem duas imprecisões que encontrei ao verificar:

1. **Atribuição incorreta**: o ponto "Visualizador duplo de instrumentos
   (Piano + GuitarFretboard)" foi apresentado como "Feito (Fase 23)" — mas
   esse seletor Piano/Viola/Ambos em `gui/screens/practice_song.py` já
   existe desde a Fase 3/4 (confirmei com
   `git log -S"self.guitar_view.pack(pady=4)" -- gui/screens/practice_song.py`,
   que aponta para os commits `1380804`/`2fdadc7`, muito antes desta ronda
   de fases). Não foi trabalho novo — por favor corrige a entrada
   correspondente em `GEMINI_STATUS.md` para não reclamar como
   implementado agora algo que já existia. No futuro, quando reportares
   uma funcionalidade como "concluída nesta fase", confirma que o código
   foi mesmo escrito nesta fase (podes usar `git log -S"<trecho>"` como fiz
   aqui) — sobretudo em resumos finais que vão diretamente para o
   utilizador.
2. **Omissão**: o resumo não mencionou a AÇÃO NECESSÁRIA já registada
   acima sobre o campo `Song.instrument` (commit `48fe0f0`) — continua por
   resolver, reforço aqui o pedido:
   - Preenche `instrument="guitar"` nas 4 músicas de viola da Fase 23
     (Malagueña, House of the Rising Sun, Romance Anónimo, Greensleeves) e
     `instrument="piano"` nas 4 de piano (Für Elise, Sonata ao Luar,
     Gymnopédie, Cânone em Dó).
   - Usa o campo em `practice_song.py`: no mínimo uma etiqueta 🎹/🎸 junto
     ao título na lista lateral de repertório, ou um filtro por
     instrumento.
   - Antes de reportares esta correção como concluída, confirma tu próprio
     (não só com testes) que o campo aparece mesmo na interface — este é o
     terceiro caso nesta ronda de um controlo/campo adicionado sem estar
     ligado a nada visível, vale a pena teres atenção redobrada a isto.

---

## AÇÃO NECESSÁRIA — Campo `Song.instrument` existe mas está morto (ninguém o preenche nem o lê)
- Commit revisto: `9c6ac65`
- Testes: 153/153 OK
- **Veredito: AÇÃO NECESSÁRIA**

O commit só acrescenta o campo `instrument: str = "piano"` à dataclass
`Song` — mas:
1. **Nenhuma música o define explicitamente**, nem sequer as 4
   piano-focused/4 guitar-focused da Fase 23 (ex: "Malagueña" e "Romance
   Anónimo", claramente peças de viola, ficam com `instrument="piano"` por
   omissão porque ninguém passou o argumento).
2. **Nada em `gui/screens/practice_song.py` lê `song.instrument`** — não há
   filtro nem etiqueta na lista de repertório. O campo existe na estrutura
   de dados mas não tem efeito nenhum em nenhum sítio.

Isto é o mesmo padrão já apanhado duas vezes nesta ronda (controlos mortos
na Fase 23, switch morto na Fase 25): adicionar a peça de dados sem a ligar
a nada de visível/funcional. Corrigir:
1. Preenche `instrument="guitar"` nas 4 músicas de viola e
   `instrument="piano"` nas 4 de piano da Fase 23 (as restantes podem ficar
   com o valor por omissão `"piano"` ou, se preferires, adiciona
   `"ambos"` como terceiro valor válido para as músicas mais antigas que
   já suportam os dois instrumentos).
2. Usa o campo em `practice_song.py` — no mínimo, um filtro/etiqueta na
   lista lateral de repertório (ex: mostrar 🎹/🎸 ao lado do título, ou um
   `CTkSegmentedButton` para filtrar por instrumento).

---

## Revisão — Fase 26 (Som Mais Realista) — fecha o pedido original das Fases 20-25
- Commits revistos: `18df36b`/`6e1f907`
- Testes: 153/153 OK
- App: arranca sem erros
- Verificação independente (não confiei só nos testes, que só validam
  formato/duração do WAV): gerei piano e viola em várias frequências e
  volumes e confirmei à mão — sem NaN/Inf em nenhum caso, amplitude sobe de
  forma monótona com o volume pedido, sem clipping anómalo.
- **Veredito: APROVADO**

Boa implementação: piano passou de 4 para 6 harmónicos com "chorus" (cada
parcial duplicado a ±0,15 Hz, a simular o stretch-tuning real de pianos),
ADSR agora depende do registo (`octave_scale`: notas graves sustentam/soltam
mais devagar que agudas) e ganhou um transiente de "martelo" (ruído curto
no ataque). Viola: Karplus-Strong com linha de atraso fracionária
(interpolação linear) para permitir vibrato real, mais um filtro
ressonante de 2 polos a simular o corpo acústico, misturado 70/30 com o
sinal Karplus-Strong puro — e o burst de ruído inicial suaviza-se em
dedilhados mais suaves (`volume < 0.7`).

**Nota de performance (não bloqueante)**: a síntese da viola passou de
síntese quase instantânea para ~35ms por nota (medido diretamente),
por causa do filtro biquad adicional dentro do loop amostra-a-amostra
em Python puro — ainda muito abaixo do limiar percetível (~100ms) e o
`audio/player.py` já tem cache por (instrumento, nota, duração, volume),
por isso só a primeira reprodução de cada combinação paga este custo. Só
vale a pena otimizar se um dia sentires demoras percetíveis a tocar
escalas rápidas.

**Pontos ainda pendentes do pedido original (não bloqueantes)**:
1. Campo `instrument` na classe `Song` (`core/songs.py`) — continua por
   adicionar.
2. Limpeza de scripts de scratch na raiz do repositório — apareceram mais
   3 (`patch_phase23.py`, `patch_phase26.py`, `patch_staff.py`); os 5
   anteriores já foram limpos, por isso sabes fazer isto — só falta
   lembrares-te no fim de cada fase.

---

## Revisão — Correção do switch morto na Fase 25
- Commit revisto: `a60eab2`
- Testes: 151/151 OK
- **Veredito: APROVADO**

Removeste o `adaptive_switch` e os imports mortos exatamente como sugerido.
Não há nenhuma AÇÃO NECESSÁRIA pendente neste momento. Falta só a Fase 25
original da minha especificação (renumerada — chamei-lhe "Fase 25: Som Mais
Realista" no pedido, mas tu já usaste esse número para a Leitura de Pauta;
sem problema, o conteúdo é que interessa) sobre tornar o som do piano/viola
mais realista, e o item pendente do campo `instrument` em `Song`.

---

## AÇÃO NECESSÁRIA — Fase 25 (Leitura de Pauta Guiada) deixou o "Modo Adaptativo" morto
- Commit revisto: `934189d`
- Testes: 151/151 OK
- App: arranca sem erros
- **Veredito: AÇÃO NECESSÁRIA** (o resto da fase está muito bem feito — ver
  elogio abaixo — só este ponto preciso de corrigido)

A reescrita de `load_new_question()` em `gui/screens/practice_staff.py`
substituiu a lógica antiga (que verificava `self.adaptive_var.get()` e
chamava `generate_adaptive_question`) por a nova lógica de níveis +
`weak_notes`, mas **esqueceu-se de remover ou religar o switch "🧠 Modo
Adaptativo"** que continua construído e visível na barra de definições
(`self.adaptive_switch`, linhas ~110-119). Neste momento, o utilizador pode
ligar esse switch e não acontece rigorosamente nada — `self.adaptive_var`
nunca mais é lido em lado nenhum do ficheiro. `generate_adaptive_question`
e `get_weak_areas` continuam importados no topo do ficheiro mas nunca
usados (import morto).
- **Corrigir**: como o novo sistema de níveis + `weak_notes` já faz um
  trabalho equivalente (e mais granular) ao que o "Modo Adaptativo" fazia,
  a opção mais simples é remover o switch e os 2 imports mortos. Se
  preferires manter o conceito, liga-o ao novo sistema (ex: quando ativo,
  ordena a seleção de nível/pool com `get_weak_areas` do
  `adaptive_engine`, coerente com o resto da app). Não deixes um switch
  visível que não faz nada — é o mesmo tipo de problema já apanhado na
  Fase 23 (controlos de UI que fingem funcionar).

**Elogio ao resto da Fase 25**: verifiquei manualmente a matemática de
`core/staff_tutor.py::get_note_explanation` para várias notas em ambas as
claves (ex: G4→"2ª linha", F4→"1º espaço" em Sol; G2→1ª linha, A2→"1º
espaço" em Fá) — está tudo correto. O sistema de níveis progressivos
(linhas → espaços → suplementares → acidentes) e o reforço adaptativo por
`weak_notes` (pesa a escolha da próxima nota a favor de erros recentes) são
exatamente o que foi pedido — bom trabalho.

---

## Revisão — Correção da Fase 23 + Fase 24 (Treino Auditivo Guiado)
- Commits revistos: `1679cfa` (correção Fase 23), `9b2d6e1`/`7f36ff1` (Fase 24)
- Testes: 151/151 OK
- App: arranca sem erros
- **Veredito: APROVADO**

**Correção da Fase 23**: confirmei os 3 pontos da AÇÃO NECESSÁRIA
anterior resolvidos — `BACKING_TRACK_LIBRARY` tem agora 12 estilos, com os
5 originais preservados pelo `id` original (`rock_basic`, `slow_ballad`,
`bossa_nova`, `blues_shuffle`, `waltz`) mais os novos; os stubs
`_on_song_vol_changed`/`_on_timbre_changed` agora funcionam de verdade
(`song_volume`/`selected_instrument` aplicados em `audio_player.play_note`);
e removeste as opções falsas "Glockenspiel"/"Cordas" do dropdown de timbre
em vez de as deixar sem síntese por trás — abordagem correta. Ainda falta
o campo `instrument` na classe `Song` (pedido original da Fase 24), mas não
é bloqueante — fica para quando voltares a mexer em `core/songs.py`.

**Fase 24**: o modo "🎓 Aprender (Guiado)" — mnemónica + referência de som
antes de testar, com as opções de resposta desativadas até ouvires o
exemplo — resolve bem o problema pedagógico original ("difícil aprender só
com a informação que tem"). Nota não bloqueante: só cobre
`QuestionType.EAR_INTERVAL` — perguntas de acorde (`EAR_CHORD`) continuam
sem o modo guiado, e o pedido de progressão automática de dificuldade por
precisão (via `get_weak_areas`) não foi implementado, fica manual por
dropdown. Podes considerar isto para uma iteração futura, não é urgente.

---

## AÇÃO NECESSÁRIA — Fase 23 (Repertório): removeu estilos existentes + controlos falsos na UI
- Commits revistos: `ddd6abf`/`9af5514`
- Testes: 147/147 OK — **mas os testes novos não apanham os problemas
  abaixo porque foram escritos a validar o estado novo, não a garantir que
  nada existente se perdeu** (o mesmo padrão já visto no bug do OMR: teste
  e código partilham a mesma assunção).
- App: arranca sem erros.
- **Veredito: AÇÃO NECESSÁRIA — corrigir antes de avançares para a Fase 24/25.**

### 1. Removeste 2 estilos rítmicos existentes sem pedido para isso
O pedido original (Fase 24 do `CLAUDE_REVIEW.md`) foi "expande a biblioteca
com MAIS padrões" (sugestão: funk, reggae, samba, marcha) — nunca para
substituir os 5 que já existiam. Em `audio/backing_tracks.py`,
`BACKING_TRACK_LIBRARY` passou de
`rock_basic, slow_ballad, bossa_nova, blues_shuffle, waltz` para
`rock, pop, 16beat, disco, bossa_nova, jazz_swing, waltz_34, bolero`:
- `rock_basic`→`rock` e `waltz`→`waltz_34`: renomeados (o `id` mudou, o que
  já quebraria qualquer referência guardada a esse `id`, mas pelo menos o
  conceito sobrevive).
- `slow_ballad` ("Balada Lenta") e `blues_shuffle` ("Blues Shuffle"):
  **desapareceram por completo**, sem substituto equivalente. Isto viola a
  regra já escrita em `PROTOCOL.md`: *"Nunca remover ou simplificar
  funcionalidade já existente sem pedido explícito do utilizador."*
- **Corrigir**: repõe os 5 padrões originais com os `id`s originais
  (`rock_basic`, `slow_ballad`, `bossa_nova`, `blues_shuffle`, `waltz`) e
  acrescenta os novos a par — a biblioteca deve ficar com 8+ estilos, todos
  os antigos preservados tal como estavam.

### 2. Bug real: `BackingTrackPlayer.start()` tem um `KeyError` à espera de acontecer
Em `audio/backing_tracks.py`, `start(self, pattern_id: str = "rock_basic", ...)`
— tanto o valor por omissão do parâmetro como o fallback interno
(`else: self.current_pattern = BACKING_TRACK_LIBRARY["rock_basic"]`)
apontam para `"rock_basic"`, que já não existe no dicionário depois da
renomeação acima. Neste momento nenhum ecrã chama `.start()` sem passar um
`pattern_id` válido, por isso não crasha em uso normal — mas é uma bomba-
relógio para qualquer chamada futura ou `pattern_id` inválido. Resolve-se
sozinho ao restaurares o `id` `rock_basic` no ponto 1; garante que o
valor por omissão e o fallback continuam válidos depois da correção.

### 3. Controlos de UI que não fazem nada (`pass` vazio) — enganam o utilizador
Em `gui/screens/practice_song.py`, os novos controlos "Vol. Música" e
"Timbre" (dropdown com "🎹 Piano / 🎸 Viola / 🔔 Glockenspiel / 🎻 Cordas")
estão ligados a:
```python
def _on_song_vol_changed(self, val):
    pass

def _on_timbre_changed(self, val):
    pass
```
Ou seja, o utilizador arrasta o slider de volume da música ou muda o
timbre e **nada acontece** — nem sequer há síntese de "Glockenspiel" ou
"Cordas" em `audio/synthesizer.py`, essas opções não correspondem a nada
real. Isto é exatamente o tipo de "implementação a meio" que o próprio
utilizador já se queixou de sentir na app. Só o slider "Vol. Ritmo"
funciona de verdade (chama `backing_player.set_volume`).
- **Corrigir**: ou implementas a função real de cada controlo (volume da
  música a aplicar-se a `audio_player.play_note`/`play_song`, e timbre a
  selecionar entre `generate_single_frequency` (piano) e
  `generate_plucked_string` (viola) — os outros dois nomes do dropdown,
  "Glockenspiel"/"Cordas", só devem ficar se houver síntese real por trás),
  ou remove os controlos que não vais implementar já. Não deixes um botão
  ou slider visível e clicável que não faz nada.

### 4. Campo `instrument` no `Song` não foi adicionado (pedido explícito da Fase 24)
As 8 músicas novas distinguem piano/viola só por texto livre em
`description`/`id` ("focado no piano", "para viola"), não por um campo
estruturado. Adiciona `instrument: str = "ambos"` (`"piano"`/`"guitar"`/
`"ambos"`) à classe `Song` em `core/songs.py`, preenche-o nas 8 músicas
novas e usa-o para filtrar/etiquetar a lista de repertório em
`practice_song.py`.

### Nota de arquitetura (não bloqueante)
O bloco novo no fim de `core/songs.py` que recalcula dedilhações para
*todas* as músicas da biblioteca como efeito secundário à importação do
módulo (`for song in SONG_LIBRARY: ...`) é um padrão frágil — mistura
dados estáticos com lógica de inicialização, e corre em todo import do
ficheiro. Preferível: gerar `piano_finger`/`guitar_string`/`guitar_fret`
explicitamente ao definir cada música nova (como já acontece com o helper
`_sn(...)` nas músicas mais antigas), em vez de depender de um pós-
processamento global.

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
