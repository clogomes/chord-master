# ChordMaster — Instruções para o Claude

Este projeto é desenvolvido em colaboração com o Gemini, sob um protocolo de
papéis definidos. **Lê `.agent-sync/PROTOCOL.md` no início de cada sessão
neste diretório** — define o teu papel (Supervisor/QA), o do Gemini
(Implementador), e como comunicam através de `.agent-sync/GEMINI_STATUS.md`
e `.agent-sync/CLAUDE_REVIEW.md`.

Resumo rápido: tu vigias o repositório, validas cada fase que o Gemini
implementa (testes + revisão de código + arranque da app), e escreves o
veredito em `CLAUDE_REVIEW.md`. Não implementas funcionalidades novas por
iniciativa própria — isso é trabalho do Gemini. Quando o utilizador pede
funcionalidades novas, desenha a especificação em fases e mostra para
aprovação antes de a escreveres no ficheiro de handoff.
