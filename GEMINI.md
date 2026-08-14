# ChordMaster — Instruções para o Gemini

Este projeto é desenvolvido em colaboração com o Claude, sob um protocolo de
papéis definidos. **Lê `.agent-sync/PROTOCOL.md` no início de cada sessão
neste diretório** — define o teu papel (Implementador), o do Claude
(Supervisor/QA), e como comunicam através de `.agent-sync/GEMINI_STATUS.md`
e `.agent-sync/CLAUDE_REVIEW.md`.

Resumo rápido:
1. Antes de começares qualquer trabalho, lê `.agent-sync/CLAUDE_REVIEW.md`.
   Se a entrada mais recente tiver "AÇÃO NECESSÁRIA", corrige tudo o que lá
   está listado antes de avançares para trabalho novo.
2. Implementa a fase, corre `python3 -m unittest discover tests`, atualiza o
   `README.md`.
3. Faz commit + push.
4. Regista uma entrada no topo da secção "Histórico" de
   `.agent-sync/GEMINI_STATUS.md` com o formato já usado nas entradas
   anteriores (fase, estado, commit, resumo, ficheiros alterados).

Nunca escrevas em `.agent-sync/CLAUDE_REVIEW.md` — esse ficheiro é só lido
por ti, escrito pelo Claude.
