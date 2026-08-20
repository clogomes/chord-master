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
