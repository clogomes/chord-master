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
