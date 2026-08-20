# Protocolo de Colaboração Supervisor ↔ Implementador — ChordMaster

Este projeto é desenvolvido por dois agentes de IA com papéis distintos e
complementares, coordenados pelo utilizador (clogomes). Este ficheiro é a
referência única do protocolo — `CLAUDE.md` (Supervisor) e `AGENTS.md`
(Implementador), na raiz do projeto, apontam para aqui.

## Nota sobre nomes (2026-08-17)

O protocolo é definido por **papéis**, não por ferramentas. O papel de
Implementador foi desempenhado pelo **Gemini/Antigravity** até à Fase 48 e
passou depois para o **opencode**. O papel de Supervisor é do **Claude**.

Por isso, alguns nomes são históricos e **mantêm-se de propósito**:
- `.agent-sync/GEMINI_STATUS.md` é o **ficheiro de estado do Implementador**,
  seja ele quem for. Não foi renomeado porque contém 400+ linhas de histórico
  e é referenciado centenas de vezes no `CLAUDE_REVIEW.md`.
- `GEMINI.md` na raiz é legado; o ponto de entrada atual do Implementador é
  **`AGENTS.md`**.
- Onde este documento e o `CLAUDE_REVIEW.md` dizem "Gemini", lê
  "**o Implementador**".

## Papéis

**Implementador** (atualmente opencode)
- Escreve o código de todas as funcionalidades do ChordMaster.
- Corre a suite de testes (`python3 -m unittest discover tests`) antes de
  considerar uma fase concluída.
- Corre `python3 -m pyflakes audio core gui tests main.py` antes de cada
  commit — nomes indefinidos causaram 6 bugs neste projeto, e há um teste
  (`tests/test_no_undefined_names.py`) que falha se houver algum.
- Atualiza o `README.md` (funcionalidades + árvore de ficheiros) no fim de
  CADA fase, não só no fim de tudo.
- Faz commit + push de cada fase concluída, e regista-a em
  `.agent-sync/GEMINI_STATUS.md`.

**Claude — Supervisor / QA**
- Não escreve funcionalidades novas por iniciativa própria no código do
  produto — a sua escrita de código limita-se a correções pontuais quando
  explicitamente pedidas pelo utilizador, e à manutenção deste protocolo.
- Vigia o repositório GitHub (via um monitor em segundo plano ligado a
  commits novos em `origin/main`).
- Quando deteta um commit novo: corre a suite de testes completa, revê o
  diff/código alterado, e arranca a aplicação (`python3 main.py`) para
  confirmar que não há erros de runtime.
- Regista o veredito em `.agent-sync/CLAUDE_REVIEW.md`.
- Quando o utilizador pede funcionalidades novas, Claude desenha a
  especificação em fases, **mostra ao utilizador para aprovação**, e só
  depois de aprovado escreve a especificação em `CLAUDE_REVIEW.md` como
  "TRABALHO PEDIDO" para o Implementador executar.

## Ficheiros do protocolo (`.agent-sync/`)

- **`GEMINI_STATUS.md`** — escrito só pelo **Implementador** (nome histórico,
  ver nota acima). Uma entrada no topo da secção "Histórico" por cada fase
  concluída (fase, estado, commit, resumo, ficheiros alterados).
- **`CLAUDE_REVIEW.md`** — escrito só pelo Claude. Cada entrada tem um
  veredito:
  - **APROVADO** — nada a fazer.
  - **AÇÃO NECESSÁRIA** — itens concretos a corrigir *antes* de qualquer
    fase nova (ver regra de ordem abaixo).
  - **TRABALHO PEDIDO** — especificação de funcionalidade nova, já aprovada
    pelo utilizador, pronta a implementar.

## Regra de ordem (importante)

Antes de começar uma fase nova, o Implementador deve ler `CLAUDE_REVIEW.md` e
resolver qualquer "AÇÃO NECESSÁRIA" pendente primeiro. Já aconteceu uma vez
neste projeto o Implementador avançar para a fase seguinte antes de corrigir um item
pendente — não é grave se nada depender disso, mas a ordem correta é sempre:
corrigir pendências → só depois trabalho novo.

## Uma fase de cada vez, com aprovação escrita (pedido explícito do utilizador)

Quando um pedido tiver várias fases numeradas (ex: "Fases 27 a 30"), o
Implementador faz **uma fase de cada vez**, por esta ordem obrigatória:
1. Implementa só a fase seguinte (não adianta trabalho de fases posteriores).
2. Corre a suite de testes completa.
3. Faz commit + push só dessa fase, com mensagem clara identificando o
   número da fase.
4. **Espera** que o Claude escreva um veredito **APROVADO** em
   `CLAUDE_REVIEW.md` para essa fase específica antes de começar a
   seguinte — mesmo que os testes passem sem erros. Se vier
   "AÇÃO NECESSÁRIA", corrige primeiro.

Isto é diferente da regra de ordem acima (que só bloqueia quando há um erro
pendente): esta regra pede uma pausa deliberada a cada fase, mesmo quando
está tudo bem, para que cada commit fique isolado e seja fácil fazer
rollback a uma versão específica se for preciso. Só se aplica quando o
utilizador pedir explicitamente sequenciamento fase-a-fase; caso contrário
mantém-se a cadência normal.

## Regras gerais para ambos

- Ao fazer commit, usa `git add <ficheiros específicos>` em vez de
  `git add -A`/`git add .`. Como os dois agentes trabalham no mesmo diretório
  local, um `git add -A` pode apanhar ficheiros que o outro agente ainda
  estava a escrever e não tinha commitado, misturando o trabalho dos dois
  num único commit sem intenção. Já aconteceu uma vez (Fase 17 apanhou o
  pedido de Fases 18/19 que o Claude ainda não tinha commitado).
- Nunca remover ou simplificar funcionalidade já existente sem pedido
  explícito do utilizador.
- **Áudio: regra revista em 2026-08-16 por decisão explícita do utilizador.**
  A regra anterior era "sintetizar sempre localmente, nunca usar ficheiros
  de áudio externos, por causa de licenciamento". O utilizador decidiu
  expressamente o contrário para o módulo de composição e para o realismo
  sonoro em geral: **podes usar samples reais / ficheiros de áudio
  externos, maximizando a qualidade e o realismo**. As questões de
  licenciamento ficam à responsabilidade do utilizador, para tratar mais
  tarde — não é motivo para não implementares, nem para escolheres uma
  solução pior só por prudência.
  - A síntese local existente (`audio/synthesizer.py`,
    `audio/backing_tracks.py`) **não deve ser removida** — continua a ser o
    caminho por omissão quando não houver sample disponível, e serve de
    fallback (regra "nunca remover funcionalidade existente" acima).
  - Segue o padrão defensivo do projeto: se um sample/pasta de samples não
    existir na máquina, a app tem de continuar a funcionar (cai no som
    sintetizado), nunca crashar.
  - Detalhe prático a respeitar: mantém os ficheiros de áudio **fora do
    que é commitado** (usa `.gitignore` para a pasta de samples) e faz o
    carregamento a partir de uma pasta local configurável. Isto não limita
    nada do realismo — o código suporta samples na mesma — e mantém a
    decisão de licenciamento em aberto e reversível para o utilizador,
    que é precisamente o que ele pediu ao adiá-la.
- Qualquer nova dependência em `requirements.txt` deve seguir o padrão
  defensivo já usado no projeto (`try/except ImportError` com uma flag
  `HAS_X`, ver `audio/pitch_listener.py` e `audio/player.py`) para a app
  continuar a funcionar em máquinas sem essa biblioteca instalada.
