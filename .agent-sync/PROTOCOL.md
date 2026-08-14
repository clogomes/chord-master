# Protocolo de Colaboração Claude ↔ Gemini — ChordMaster

Este projeto é desenvolvido por dois agentes de IA com papéis distintos e
complementares, coordenados pelo utilizador (clogomes). Este ficheiro é a
referência única do protocolo — `CLAUDE.md` e `GEMINI.md`, na raiz do projeto,
apontam para aqui.

## Papéis

**Gemini — Implementador**
- Escreve o código de todas as funcionalidades do ChordMaster.
- Corre a suite de testes (`python3 -m unittest discover tests`) antes de
  considerar uma fase concluída.
- Atualiza o `README.md` (funcionalidades + árvore de ficheiros) no fim de
  CADA fase, não só no fim de tudo.
- Faz commit + push de cada fase concluída.

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
  "TRABALHO PEDIDO" para o Gemini implementar.

## Ficheiros do protocolo (`.agent-sync/`)

- **`GEMINI_STATUS.md`** — escrito só pelo Gemini. Uma entrada no topo da
  secção "Histórico" por cada fase concluída (fase, estado, commit, resumo,
  ficheiros alterados).
- **`CLAUDE_REVIEW.md`** — escrito só pelo Claude. Cada entrada tem um
  veredito:
  - **APROVADO** — nada a fazer.
  - **AÇÃO NECESSÁRIA** — itens concretos a corrigir *antes* de qualquer
    fase nova (ver regra de ordem abaixo).
  - **TRABALHO PEDIDO** — especificação de funcionalidade nova, já aprovada
    pelo utilizador, pronta a implementar.

## Regra de ordem (importante)

Antes de começar uma fase nova, o Gemini deve ler `CLAUDE_REVIEW.md` e
resolver qualquer "AÇÃO NECESSÁRIA" pendente primeiro. Já aconteceu uma vez
neste projeto o Gemini avançar para a fase seguinte antes de corrigir um item
pendente — não é grave se nada depender disso, mas a ordem correta é sempre:
corrigir pendências → só depois trabalho novo.

## Regras gerais para ambos

- Ao fazer commit, usa `git add <ficheiros específicos>` em vez de
  `git add -A`/`git add .`. Como os dois agentes trabalham no mesmo diretório
  local, um `git add -A` pode apanhar ficheiros que o outro agente ainda
  estava a escrever e não tinha commitado, misturando o trabalho dos dois
  num único commit sem intenção. Já aconteceu uma vez (Fase 17 apanhou o
  pedido de Fases 18/19 que o Claude ainda não tinha commitado).
- Nunca remover ou simplificar funcionalidade já existente sem pedido
  explícito do utilizador.
- Preferir sintetizar áudio localmente (como já acontece em
  `audio/synthesizer.py`) em vez de depender de amostras/ficheiros externos
  com possíveis questões de licenciamento.
- Qualquer nova dependência em `requirements.txt` deve seguir o padrão
  defensivo já usado no projeto (`try/except ImportError` com uma flag
  `HAS_X`, ver `audio/pitch_listener.py` e `audio/player.py`) para a app
  continuar a funcionar em máquinas sem essa biblioteca instalada.
