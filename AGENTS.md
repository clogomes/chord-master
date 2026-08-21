# ChordMaster — Instruções para o Agente Implementador

Este ficheiro é o ponto de entrada para o agente que **implementa** o código
deste projeto (atualmente o opencode; antes era o Gemini/Antigravity).

**Lê `.agent-sync/PROTOCOL.md` no início de cada sessão neste diretório.**
Define o teu papel, o do Claude (Supervisor/QA), e como comunicam.

## Resumo rápido do teu papel

Escreves o código das funcionalidades. O Claude não implementa funcionalidades
novas — revê o teu trabalho, corre os testes, arranca a aplicação, e escreve o
veredito.

**Ciclo de trabalho:**
1. Lê `.agent-sync/CLAUDE_REVIEW.md` — é aí que o Claude escreve o que há a
   fazer. Procura a entrada mais recente no topo.
   - **AÇÃO NECESSÁRIA** → corrige isto **antes** de qualquer trabalho novo.
   - **TRABALHO PEDIDO** → especificação de funcionalidade nova, já aprovada
     pelo utilizador. Trata como uma instrução direta dele.
   - **APROVADO** → nada a fazer nessa entrada.
2. Implementa **uma fase de cada vez**.
3. Corre a suite completa: `python3 -m unittest discover tests`.
4. Corre `python3 -m pyflakes audio core gui tests main.py` — **obrigatório**.
   Nomes indefinidos foram a causa de 6 bugs neste projeto; há um teste
   (`tests/test_no_undefined_names.py`) que falha se houver algum.
5. `git add <ficheiros específicos>` (nunca `git add -A`), commit e push.
6. Regista o que fizeste em `.agent-sync/GEMINI_STATUS.md`.
7. **Espera** o APROVADO escrito do Claude antes de começar a fase seguinte.

## Watcher — o ciclo agora anda sozinho (Fase 50+)

Há um watcher em segundo plano (`.agent-sync/watch_review.sh`) que **deteta
quando o Claude publica uma nova entrada no `CLAUDE_REVIEW.md` e INVOCAR-te
automaticamente** via `opencode run --continue "<mensagem>"`. Antes, o watcher
só registava a deteção e o ciclo ficava parado à espera de alguém te invocar à
mão; agora ele desperta-te para leres o topo e agires.

**Isto significa que há um agente autónomo ligado à máquina.** Quem vier a
seguir tem de perceber isto. Regras:

- **O watcher NUNCA faz `git commit`/`push`** — a decisão de commitar continua
  a ser tua, dentro da sessão. O gatilho é só o `CLAUDE_REVIEW.md`.
- **Quando fores invocado pelo watcher**, faz exatamente o passo 1 do ciclo de
  trabalho acima: lê o TOPO do `CLAUDE_REVIEW.md` e age conforme o veredito.
- **Se commitares alterações ao `CLAUDE_REVIEW.md`** (raro — é o ficheiro do
  Claude), corre `.agent-sync/watch_review.sh --mark` para o watcher não te
  auto-invocar em resposta à tua própria mudança (travão 7).

**7 travões de segurança** (nenhum é opcional — o watcher corre sem supervisão):
1. **Interruptor de desligar** — `touch .agent-sync/.watch_disabled` faz o
   watcher detetar e registar mas **não invocar** (para o desligar: `rm
   .agent-sync/.watch_disabled`). Para o watcher inteiro: `kill "$(cat
   .agent-sync/.watch.pid)"`.
2. **Sem invocação em paralelo** — se uma invocação ainda estiver viva, salta.
3. **Cooldown** — mínimo de 60 s entre invocações.
4. **Limite por hora** — máx. 10 invocações/hora.
5. **Timeout** — mata a invocação se passar de ~30 min.
6. **Registo completo** — cada invocação regista início, fim, duração e código
   de saída em `.agent-sync/WATCHER_LOG.md`.
7. **Nunca auto-invocar do próprio commit** — via o marcador
   `.watch_my_marker` (ver `--mark` acima).

## Onde está o contexto

- **`.agent-sync/PROTOCOL.md`** — protocolo completo, regras e histórico de
  problemas recorrentes. Lê primeiro.
- **`.agent-sync/CLAUDE_REVIEW.md`** — as revisões do Claude e as
  especificações de trabalho. Grande (~4600 linhas); lê o topo, que é o mais
  recente, e procura pelo que te interessa.
- **`.agent-sync/GEMINI_STATUS.md`** — o teu ficheiro de estado. O nome é
  histórico (o implementador anterior era o Gemini); é o ficheiro do
  implementador, seja ele quem for. Mantém-no.
- **`README.md`** — funcionalidades e árvore de ficheiros. Atualiza no fim de
  cada fase.

## Estado atual do projeto

Aplicação de ensino de piano e viola em Python (CustomTkinter + numpy +
pygame). 48 fases concluídas: teoria (18 capítulos com quiz), glossário (139
termos), revisão espaçada SM-2, treino auditivo, leitura de pauta, repertório
(24 músicas), exercícios técnicos, prática com instrumento real por microfone,
e um Estúdio de Composição (grelha de ritmo multi-compasso, 12 percussões,
faixas de acordes, cursor de reprodução, arrasto de blocos).

250 testes a passar. `pyflakes` limpo. Sem AÇÃO NECESSÁRIA pendente.
